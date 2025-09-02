from collections import defaultdict
from functools import reduce
import operator
from typing import Any, Dict, Mapping, Sequence, Tuple, cast

import torch
from torch.fx import Graph, GraphModule, Node, map_arg
from torch.fx.node import Argument
from torch.utils._pytree import tree_all

import furiosa_llm.parallelize.model_rewriter.mppp_config as mrw
from furiosa_llm.parallelize.model_rewriter.mppp_config import (
    Device,
    DeviceId,
    NodeId,
    Shard,
    ShardSpec,
)
from furiosa_llm.parallelize.node_meta import get_device_id, get_spec, set_device_id
from furiosa_llm.parallelize.utils import recursive_getattr


class CCOutputPlaceholderNode(Node):
    """Special node for marking blank points that should be replaced with Communication op nodes."""

    ...


def _get_sliced_tensor(
    original: torch.Tensor, spec: ShardSpec, device_id: DeviceId
) -> torch.Tensor:
    """Get sliced tensor on specified rank according to spec and rank"""
    coord = spec.mesh.get_coordinate(device_id)

    sliced = original
    assert len(coord) == len(spec.placements)
    for placement, idx, group_size in zip(spec.placements, coord, spec.mesh.size()):
        if placement.is_replicate():
            continue
        elif placement.is_shard():
            shard = cast(Shard, placement)
            sliced = torch.chunk(sliced, chunks=group_size, dim=shard.dim)[idx]
        else:
            raise ValueError(f"Slicing for {placement} is not supported now")
    return sliced


def _create_cc_output_placeholder_node(original_name: str) -> CCOutputPlaceholderNode:
    # node for marking blank point that should be filled with replicated nodes.
    return CCOutputPlaceholderNode(Graph(), f"blank_{original_name}", "get_attr", "blank", (), {})


def _get_new_target_shape_for_view_ops(
    op: torch._ops._Ops,
    node: Node,
    device_mesh: mrw.DeviceMesh,
    spec: ShardSpec,
) -> Tuple[int, ...]:

    # These operator's shape args must be changed accordingly.
    original_shape = node.meta["tensor_meta"].shape

    original_target_shape = original_shape
    assert isinstance(original_target_shape, (tuple, list))

    divisor_per_dim = [1 for _ in original_target_shape]
    cur_submesh = device_mesh.to_torch_tensor()

    if op in (
        torch.ops.aten._unsafe_view.default,
        torch.ops.aten.view.default,
    ):

        # calculate divisor for each target dim.
        for placement in spec.placements:
            if not placement.is_shard():
                continue

            shard = cast(Shard, placement)

            original_stride = reduce(operator.mul, original_shape[shard.dim + 1 :])

            after_view_stride = 1

            idx = len(original_target_shape) - 1

            while idx >= 0:
                dim_shape = original_target_shape[idx]
                after_view_stride *= dim_shape

                idx -= 1
                if after_view_stride >= original_stride and not (
                    idx >= 0 and original_target_shape[idx] == 1
                ):
                    break

            ## For view operation, sharded dim's stride and width must be kept same after view op.
            assert (
                after_view_stride
                == original_stride
                # and original_target_shape[idx] == original_shape[shard.dim]
            ), "Original stride must be kept same for view operation for DTensor to be propagated"

            divisor_per_dim[idx] *= len(cur_submesh)

            cur_submesh = cur_submesh[0]

        assert all(
            length % divisor == 0 for length, divisor in zip(original_shape, divisor_per_dim)
        )
        new_target_shape = tuple(
            length // divisor for length, divisor in zip(original_shape, divisor_per_dim)
        )
        return new_target_shape
    elif op == torch.ops.aten.expand.default:
        for placement in spec.placements:
            if not placement.is_shard():
                continue

            sharded_dim = cast(Shard, placement).dim
            divisor_per_dim[sharded_dim] *= len(cur_submesh)
            cur_submesh = cur_submesh[0]
        new_target_shape = tuple(
            length // divisor for length, divisor in zip(original_target_shape, divisor_per_dim)
        )
        return new_target_shape
    else:
        raise NotImplementedError(f"{op} cannot be replicated now")


def _move_to(
    t: torch.Tensor,
    device: Device,
) -> torch.Tensor:
    device_ = device.to_torch_device_with_cpu_idx()

    return t.to(device_)


def replicate_nodes(
    gm: GraphModule,
    comm_points: Sequence[Tuple[NodeId, NodeId]],
    devices: Mapping[DeviceId, Device],
) -> Tuple[GraphModule, Dict[Node, Tuple[Tuple[Node, ...], CCOutputPlaceholderNode]]]:
    """Replicate nodes in FX graph according to device mesh, one replicated node per each device, and
    returns new ``GraphModule` with replicated nodes.

    For example, if certain node has ShardSpec with device mesh consisting of 4 devices, there will
    be same number of replicated nodes (one per each device) in replicated ``GraphModule``. Also, each
    replicated node will be a child of replicates of original node's parents on same device. If there's
    no replicated parents on same device, this would be marked with ``BlankNode``, which is a special node.

    Args:
        gm (GraphModule): GraphModule to replicate.
        comm_points: Contains edges, specified by source and destination node, that communication operations will inserted at
            For src and dst node in ``comm_points``, their replicas will not be connected.
            Instead, there will be ``CCOutputPlaceholderNode`` corresponding to src node
            in the dst node's argument position that src node originally exist in. This is for
            helping CCInserter to connect communication op subgraph with output nodes.
    Returns:
        Tuple[GraphModule, Dict[Node, Sequence[Node]]]: tuple of replicated
            GraphModule and mapping from original node to replicated nodes and ``CCOutputPlaceholderNode``s.
            When parent's device mesh is different from the child node's, some replicated nodes
            does not have replicated parent on the same device. In this case, cc_output_placeholder_node is used
            as if it's parent of the replicated node. In the later stage, all ``CCOutputPlaceholderNode``s will be
            replaced with communication ops by ``CCInserter``.
    """

    new_graph = Graph()
    node_mapping: Dict[Node, Dict[DeviceId, Node]] = defaultdict(dict)
    constants = {}

    cc_points_ = set(comm_points)

    def replace_arg_with_replicated(arg: Argument, cur_node: Node, device_id: DeviceId) -> Argument:
        # if there's replicated input_node for the device, return it.
        # otherwise, just return cc_output_placeholder_node.
        return map_arg(
            arg,
            lambda node: (
                cc_output_placeholder_nodes[node]
                if (node.name, cur_node.name) in cc_points_
                else node_mapping[node][device_id]
            ),
        )

    cc_output_placeholder_nodes: Dict[Node, CCOutputPlaceholderNode] = {
        node: _create_cc_output_placeholder_node(node.name) for node in gm.graph.nodes
    }

    for node in gm.graph.nodes:
        specs = get_spec(node)

        if node.op == "output":
            # Assume output node's args are in the form of ((arg0, arg1, .. ), ).
            # When the output node is created with Graph.output() method, node's args follow this form.
            assert len(node.args) == 1 and isinstance(node.args[0], (list, tuple))

            def get_all_replicated_nodes(node: Node) -> Sequence[Node]:
                specs = get_spec(node)
                assert isinstance(specs, ShardSpec)
                devices = specs.mesh.get_all_devices()

                return tuple(node_mapping[node][device_id] for device_id in devices)

            # Don't replicate output node. Just create one global output node and
            # connect each device's replicated output generating nodes to it.
            # original output node args: (a, b, c) -> new output node args: (a_d0, a_d1, a_d2, b_d0, b_d1, c_d0)
            new_args: Tuple[Any, ...] = (
                reduce(
                    operator.add,
                    (get_all_replicated_nodes(arg) for arg in node.args[0]),
                    (),
                ),
            )
            new_node = new_graph.create_node(op="output", target="output", args=new_args)

            # copy original metadata and set device id info for output node.
            new_node.meta = node.meta.copy()

            assert all(isinstance(get_device_id(node), DeviceId) for node in new_args[0])
            set_device_id(
                new_node, tuple(cast(DeviceId, get_device_id(node)) for node in new_args[0])
            )

            output_node = node
            replicated_output_node = new_node
        else:
            if isinstance(specs, (list, tuple)):
                dev_mesh = specs[0].mesh
                assert all(spec.mesh == dev_mesh for spec in specs)
            else:
                dev_mesh = specs.mesh

            # Create new node per each device in device mesh.
            for device_id in dev_mesh.get_all_devices():
                # Handle 'call_function', 'get_attr', 'call_module', 'placeholder' nodes.
                # Assume that other type of nodes doesn't exist in the graph. This assumption
                # is valid because we only care about aten level FX graph.
                if node.op == "placeholder":
                    # add prefix to target name to avoid duplicate target name
                    new_node = new_graph.placeholder(
                        f"d{device_id}_{node.target}",
                    )
                elif node.op == "get_attr":
                    # parameter/buffer node
                    actual_tensor = recursive_getattr(gm, node.target)
                    assert isinstance(specs, ShardSpec)
                    spec = specs

                    # Add sliced param to constants.
                    new_attr_name = f"{node.target}-r{device_id}"
                    sliced_param = _move_to(
                        _get_sliced_tensor(actual_tensor, spec, device_id), devices[device_id]
                    )
                    constants[new_attr_name] = sliced_param

                    # create get_attr node
                    new_node = new_graph.get_attr(new_attr_name)
                elif node.op == "call_function":
                    # TODO: any other operator that should be handled specially?
                    if node.target in (
                        torch.ops.aten._unsafe_view.default,
                        torch.ops.aten.view.default,
                        torch.ops.aten.expand.default,
                    ):
                        # view ops must be handled specially because it's shape arg
                        # must be changed according to ShardSpec when it's replicated.
                        assert isinstance(
                            specs, ShardSpec
                        ), "view ops must have output consist of single tensor"
                        new_target_shape = _get_new_target_shape_for_view_ops(
                            node.target, node, dev_mesh, specs
                        )
                        assert len(node.args) == 2, "view op must have 2 args"
                        new_args = (
                            replace_arg_with_replicated(node.args[0], node, device_id),
                            new_target_shape,
                        )
                        new_kwargs = node.kwargs
                    elif node.target == torch.ops.furiosa.sparse_select:
                        if not tree_all(
                            lambda x: not isinstance(x, Node)
                            or all(
                                p.is_replicate() for p in cast(ShardSpec, get_spec(x)).placements
                            ),
                            node.args,
                        ):
                            # TODO:
                            raise NotImplementedError(
                                "sparse_select node with non-replicate placements cannot be replicated now"
                            )
                        new_args = cast(
                            Tuple, replace_arg_with_replicated(node.args, node, device_id)
                        )
                        new_kwargs = {
                            k: replace_arg_with_replicated(v, node, device_id)
                            for k, v in node.kwargs.items()
                        }
                    else:
                        new_args = cast(
                            Tuple, replace_arg_with_replicated(node.args, node, device_id)
                        )
                        new_kwargs = {
                            k: replace_arg_with_replicated(v, node, device_id)
                            for k, v in node.kwargs.items()
                        }
                    new_node = new_graph.call_function(
                        node.target,
                        args=new_args,
                        kwargs=new_kwargs,
                    )

                else:
                    raise NotImplementedError(f"{node.op} node cannot be replicated now")

                # copy metadata from original node
                new_node.meta = node.meta.copy()
                # add device id info to node.
                set_device_id(new_node, device_id)

                assert device_id not in node_mapping[node]
                node_mapping[node][device_id] = new_node
                # add_spec_info(new_node, specs)

    # These metadatas are not valid after node replication. Remove them to avoid confusion.
    for node in new_graph.nodes:
        node.meta.pop("tensor_meta", None)
        node.meta.pop("val", None)

    # convert node mapping to Dict[Node, Tuple[Node, ...]].
    # NOTE: As of Python 3.6, for the CPython implementation of Python,
    # dictionaries remember the order of items inserted.
    flattened_node_mapping_with_cc_output_placeholder_node = {
        node: (tuple(new_nodes.values()), cc_output_placeholder_nodes[node])
        for node, new_nodes in node_mapping.items()
    }

    flattened_node_mapping_with_cc_output_placeholder_node[output_node] = (
        (replicated_output_node,),
        _create_cc_output_placeholder_node(output_node.name),
    )

    return (
        GraphModule(constants, new_graph),
        flattened_node_mapping_with_cc_output_placeholder_node,
    )
