import operator
from typing import Dict, List, Mapping, Sequence, Tuple, cast

import torch
from torch.fx import Graph, Node

import furiosa_llm.parallelize.model_rewriter.mppp_config as mrw
from furiosa_llm.parallelize.model_rewriter.mppp_config import (
    Device,
    DeviceId,
    Partial,
    Placement,
    RedOpType,
    ReduceOp,
    Replicate,
    Shard,
)
from furiosa_llm.parallelize.model_rewriter.ops.comp import Split
from furiosa_llm.parallelize.model_rewriter.ops.multi_device_comm import (
    AllGather,
    AllReduce,
    AllToAll,
    CommGroup,
    Gather,
    Reduce,
    ReduceScatter,
    SendRecv,
)
from furiosa_llm.parallelize.model_rewriter.ops.types import Op
from furiosa_llm.parallelize.node_meta import set_device_id


# NOTE: copy of torch.distributed._tensor.redistribute._replicate_then_shard
def _replicate_then_shard(val: Tuple[int, Tuple[Placement, Placement]]) -> int:
    """
    Replicate from inner to outer dimension.
    Shard from outer to inner dimension.
    The order is important when multiple dimensions of device meshes are
    sharded in same dimension.
    """
    i, (current, target) = val
    if (target.is_replicate() or target.is_partial()) and current.is_shard():
        return -i
    elif (current.is_replicate() or current.is_partial()) and target.is_shard():
        return i
    else:
        return 0


def _str_to_reduce_op_type(reduce_op: str) -> RedOpType:
    if reduce_op == "sum":
        return ReduceOp.SUM
    elif reduce_op == "min":
        return ReduceOp.MIN
    elif reduce_op == "max":
        return ReduceOp.MAX
    else:
        raise ValueError(f"Unsupported reduce op type {reduce_op}")


class CCCalculator:
    cur_node_per_dev: Dict[DeviceId, Node]

    def __init__(self, device_id_to_device: Mapping[DeviceId, Device]):
        self.device_id_to_device = device_id_to_device
        self.next_group_id = 0

        self.cur_node_per_dev = {}

    def _to_device(self, device_id: DeviceId) -> Device:
        return self.device_id_to_device[device_id]

    def _get_next_group_id(self) -> int:
        self.next_group_id += 1
        return self.next_group_id - 1

    def _gather_results(
        self,
        idxes: Tuple[int, ...],
        mesh: torch.Tensor,
        src_spec: mrw.ShardSpec,
        dst: DeviceId,
        subgraph: Graph,
    ) -> DeviceId:
        """Insert ops for gathering results over multiple devices into one gathered result on single device"""
        if len(idxes) == len(mesh.size()):
            for idx in idxes:
                mesh = mesh[idx]
            return DeviceId(int(mesh))
        else:
            # gather subroot's results into single root and return it.
            # TODO: add logic for calculating most efficient gathering logic.
            subroots = tuple(
                self._gather_results(idxes + (i,), mesh, src_spec, dst, subgraph)
                for i in range(mesh.size()[len(idxes)])
            )

            if dst in subroots:
                root = dst
            else:
                root = subroots[0]

            cur_placement = src_spec.placements[len(idxes)]

            comm_group = CommGroup(self._get_next_group_id(), subroots)

            if cur_placement.is_replicate():
                pass
            elif cur_placement.is_shard():
                shard = cast(Shard, cur_placement)
                self._insert_new_op(
                    subgraph,
                    subroots,
                    (root,),
                    Gather(
                        shard.dim,
                        root,
                        comm_group,
                        self.device_id_to_device,
                    ),
                )
            elif cur_placement.is_partial():
                partial = cast(Partial, cur_placement)
                self._insert_new_op(
                    subgraph,
                    subroots,
                    (root,),
                    Reduce(
                        _str_to_reduce_op_type(partial.reduce_op),
                        root,
                        comm_group,
                        self.device_id_to_device,
                    ),
                )
            else:
                raise NotImplementedError("Not Implemented yet")

            return root

    def _scatter_results(
        self,
        idxes: Tuple[int, ...],
        mesh: torch.Tensor,
        src: DeviceId,
        dst: mrw.ShardSpec,
        cur_node: Node,
        subgraph: Graph,
    ):
        cur_submesh = mesh
        src_dev = self.device_id_to_device[src]

        for idx in idxes:
            cur_submesh = cur_submesh[idx]

        if len(idxes) == len(mesh.size()):
            # leaf device in mesh
            dst_devid = DeviceId(int(cur_submesh))
            dst_dev = self.device_id_to_device[dst_devid]

            if dst_dev != src_dev:
                new_node = subgraph.create_node(
                    "call_function",
                    SendRecv(
                        src,
                        dst_devid,
                        CommGroup(
                            self._get_next_group_id(),
                            (src, dst_devid),
                        ),
                        self.device_id_to_device,
                    ),
                    args=(cur_node,),
                )
            else:
                new_node = cur_node
            self.cur_node_per_dev[dst_devid] = new_node
        else:
            dst_placement = dst.placements[len(idxes)]

            subgroup_size = mesh.size()[len(idxes)]
            if dst_placement.is_replicate():
                subroot_nodes = (cur_node,) * subgroup_size
            elif dst_placement.is_shard():
                shard = cast(Shard, dst_placement)
                chunks = subgraph.create_node(
                    "call_function",
                    Split(shard.dim, subgroup_size),
                    args=(cur_node,),
                )
                set_device_id(chunks, src)
                subroot_nodes = tuple(
                    subgraph.create_node("call_function", operator.getitem, args=(chunks, i))
                    for i in range(subgroup_size)
                )
                for subroot_node in subroot_nodes:
                    set_device_id(subroot_node, src)

            elif dst_placement.is_partial():
                raise ValueError("Replicate to Partial is not supported")
            else:
                raise NotImplementedError("Not Implemented yet")

            for i, subroot in enumerate(subroot_nodes):
                self._scatter_results(idxes + (i,), mesh, src, dst, subroot, subgraph)

    def _replicate_into_single_device(
        self,
        subgraph: Graph,
        src: mrw.ShardSpec,
        dst: DeviceId,
    ):
        """Make DTensor with spec ``src`` into replicate on single device ``dst``"""

        # TODO: improve this logic to insert set of communication ops that are most efficient.
        root = self._gather_results((), src.mesh.to_torch_tensor(), src, dst, subgraph)

        if root != dst:
            self._insert_new_op(
                subgraph,
                (root,),
                (dst,),
                SendRecv(
                    root,
                    dst,
                    CommGroup(self._get_next_group_id(), (root, dst)),
                    self.device_id_to_device,
                ),
            )

    def _insert_new_op(
        self,
        subgraph: Graph,
        input_group: Sequence[DeviceId],
        output_group: Sequence[DeviceId],
        op: Op,
    ) -> List[Node]:
        """Insert ``op`` to ``subgraph`` and return created nodes."""
        args = tuple(self.cur_node_per_dev[dev_id] for dev_id in input_group)

        new_op_node = subgraph.create_node(
            "call_function",
            op,
            args=args,
        )

        ret = []

        # TODO: add check for input/output num for op
        if len(output_group) > 1:
            # add getitem nodes to make each node as a single tensor.
            for i, dev_id in enumerate(output_group):
                getitem_node = subgraph.create_node(
                    "call_function",
                    operator.getitem,
                    args=(new_op_node, i),
                )
                set_device_id(getitem_node, dev_id)
                self.cur_node_per_dev[output_group[i]] = getitem_node
                ret.append(getitem_node)
        else:
            self.cur_node_per_dev[output_group[0]] = new_op_node
            ret.append(new_op_node)
        return ret

    def _same_mesh_partial_to_replicate(
        self,
        current: Partial,
        target: Replicate,
        comm_group: CommGroup,
        group: Tuple[DeviceId, ...],
        subgraph: Graph,
    ):
        self._insert_new_op(
            subgraph,
            group,
            group,
            AllReduce(
                _str_to_reduce_op_type(current.reduce_op), comm_group, self.device_id_to_device
            ),
        )

    def _same_mesh_shard_to_replicate(
        self,
        current: Shard,
        target: Replicate,
        comm_group: CommGroup,
        group: Tuple[DeviceId, ...],
        subgraph: Graph,
    ):
        self._insert_new_op(
            subgraph,
            group,
            group,
            AllGather(current.dim, comm_group, self.device_id_to_device),
        )

    def _same_mesh_partial_to_shard(
        self,
        current: Partial,
        target: Shard,
        comm_group: CommGroup,
        group: Tuple[DeviceId, ...],
        subgraph: Graph,
    ):
        self._insert_new_op(
            subgraph,
            group,
            group,
            ReduceScatter(
                _str_to_reduce_op_type(current.reduce_op),
                target.dim,
                comm_group,
                self.device_id_to_device,
            ),
        )

    def _same_mesh_replicate_to_shard(
        self,
        current: Replicate,
        target: Shard,
        comm_group: CommGroup,
        group: Tuple[DeviceId, ...],
        subgraph: Graph,
    ):
        target_dim = target.dim
        for idx, dev_id in enumerate(group):
            new_node = subgraph.create_node(
                "call_function",
                Split(target_dim, len(group), idx),
                args=(self.cur_node_per_dev[dev_id],),
            )
            set_device_id(new_node, dev_id)
            self.cur_node_per_dev[dev_id] = new_node

    def _same_mesh_shard_to_shard(
        self,
        current: Shard,
        target: Shard,
        comm_group: CommGroup,
        group: Tuple[DeviceId, ...],
        subgraph: Graph,
    ):
        cur_dim = current.dim
        target_dim = target.dim

        if cur_dim == target_dim:
            return

        self._insert_new_op(
            subgraph,
            group,
            group,
            AllToAll(
                target_dim,
                cur_dim,
                comm_group,
                self.device_id_to_device,
            ),
        )

    def get_needed_cc_graph(
        self,
        src: mrw.ShardSpec,
        dst: mrw.ShardSpec,
    ) -> Graph:
        """Get needed operations between ``src`` and ``dst`` in the form of Graph.

        Args:
            src (mrw.ShardSpec)
            dst (mrw.ShardSpec)

        Returns:
            Graph: FX Graph containing needed operations. It has input nodes for each device in ``dst`` and output nodes for each device in ``dst``.
        """
        self.cur_node_per_dev.clear()

        current_placements = src.placements
        target_placements = dst.placements

        sorted_placements = list(enumerate(zip(current_placements, target_placements)))
        sorted_placements.sort(key=_replicate_then_shard)

        src_torch_devices = tuple(map(DeviceId, src.mesh.to_torch_tensor().reshape(-1).tolist()))
        dst_torch_devices = tuple(map(DeviceId, dst.mesh.to_torch_tensor().reshape(-1).tolist()))

        subgraph = Graph()

        # Currently last node that is used as a input node of the next node per device.
        # Assume there's only one input node per device.
        self.cur_node_per_dev = {
            dev_id: subgraph.placeholder(f"d{dev_id}-arg") for dev_id in src_torch_devices
        }

        # TODO: avoid monkey patch and implement general logic.
        if src.mesh == dst.mesh:
            # Devices that original tensor is distributed over remain same,
            # but only their placements might be changed. This case includes
            # weight-gathered, tensor, and data parallelism.
            for i, (current, target) in sorted_placements:
                if current == target:
                    continue

                def get_placement_class_name(obj):
                    ret = type(obj).__name__.lower()
                    if ret.startswith("_"):
                        ret = ret[1:]
                    return ret

                groups = src.mesh.get_groups(i)
                try:
                    per_group = getattr(
                        self,
                        f"_same_mesh_{get_placement_class_name(current)}_to_{get_placement_class_name(target)}",
                    )
                except AttributeError:
                    raise RuntimeError(
                        f"redistribution from {current} to {target} with same mesh not supported yet"
                    )

                # cal needed cc ops per each group.
                for group in groups:
                    comm_group = CommGroup(self._get_next_group_id(), tuple(group))
                    per_group(current, target, comm_group, group, subgraph)
        elif src.placements == dst.placements and src.mesh.size() == dst.mesh.size():
            # Simple pipeline parallelism
            # Each device just sends tensor that it contains to other device or
            # do nothing if destination device is same as it.
            for src_dev_id, dst_dev_id in zip(
                src.mesh.get_all_devices(), dst.mesh.get_all_devices()
            ):
                if src_dev_id == dst_dev_id:
                    continue
                op = SendRecv(
                    src_dev_id,
                    dst_dev_id,
                    CommGroup(self._get_next_group_id(), (src_dev_id, dst_dev_id)),
                    self.device_id_to_device,
                )
                self._insert_new_op(subgraph, (src_dev_id,), (dst_dev_id,), op)
        elif all(plac.is_replicate() for plac in dst.placements):
            # Gather distributed tensors into ``Replicate``d ones on destination devices
            for dst_dev_id in dst.mesh.get_all_devices():
                self._replicate_into_single_device(subgraph, src, dst_dev_id)
        elif len(src.mesh.get_all_devices()) == 1:
            # Distribute ``Replicate``d original tensor on single device to tensors on multiple devices.
            assert all(
                placement.is_replicate() for placement in src.placements
            ), "When there's only single device in devicemesh, placement must be ``Replicate``"

            src_devid = src.mesh.get_all_devices()[0]
            self._scatter_results(
                (),
                dst.mesh.to_torch_tensor(),
                src_devid,
                dst,
                self.cur_node_per_dev[src_devid],
                subgraph,
            )
        else:
            raise NotImplementedError(
                f"Conversion from TensorSpec {src} to TensorSpec {dst} is not supported yet"
            )

        subgraph.output(tuple(self.cur_node_per_dev[dev_id] for dev_id in dst_torch_devices))

        return subgraph
