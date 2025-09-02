from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Tuple, Union, cast, overload

import torch
import torch.distributed._tensor as dt
from torch.distributed._tensor.placement_types import DTensorSpec as PTDTensorSpec
from torch.distributed._tensor.placement_types import Partial, Placement, Replicate, Shard
import torch.distributed.distributed_c10d as c10d

import furiosa_llm.parallelize.mppp.config as mpc
from furiosa_llm.parallelize.mppp.config import Device, NodeId, TensorId

RedOpType = c10d.ReduceOp.RedOpType
ReduceOp = c10d.ReduceOp


class DeviceId(int): ...


def _map_nested_sequence(target, func: Callable):
    if isinstance(target, (list, tuple)):
        return type(target)(_map_nested_sequence(x, func) for x in target)
    else:
        return func(target)


@dataclass
class DeviceMesh:
    """
    This class mocks the `torch.distributed._tensor.device_mesh.DeviceMesh` class.
    Torch's DeviceMesh requires distribute backend and process group to be initialized.
    See https://pytorch.org/docs/stable/distributed.html for more details.
    This class is used to represent the device mesh without doing any distributed operations.

    c.f. torch.distributed._tensor.device_mesh.DeviceMesh
    class DeviceMesh:
        device_type: str
        mesh: torch.Tensor
        mesh_dim_names: Optional[Tuple[str, ...]]
    """

    mesh: torch.Tensor  # int64 dtype tensor whose element is device id.
    device_type: Optional[str] = None
    mesh_dim_names: Optional[Tuple[str, ...]] = None

    def __post_init__(self):
        self.current_rank = int(self.mesh.view(-1)[0])

    def __repr__(self) -> str:
        return f"DeviceMesh({self.mesh.tolist()})"

    def __hash__(self):
        return hash((self.mesh, id(self)))

    def __eq__(self, other: object) -> bool:
        if id(self) == id(other):
            return True
        if not isinstance(other, (dt.DeviceMesh, DeviceMesh)):
            return False
        else:
            return self.mesh.equal(other.mesh)

    @property
    def ndim(self) -> int:
        return self.mesh.ndim

    def get_coordinate(self, rank: Optional[int] = None) -> List[int]:
        rank = rank or self.current_rank
        return torch.tensor((self.mesh == rank).nonzero(as_tuple=True)).tolist()

    @overload
    def size(self, dim: int) -> int: ...

    @overload
    def size(self) -> Tuple[int, ...]: ...

    def size(self, dim: Optional[int] = None) -> Union[Tuple[int, ...], int]:
        if dim is None:
            return tuple(self.mesh.size())
        return self.mesh.size(dim)

    def get_groups(self, dim: int) -> Tuple[Tuple[DeviceId, ...], ...]:
        """Get communication groups of devices for specified mesh dim"""
        groups = self.mesh.swapdims(-1, dim).reshape(-1, self.mesh.size(dim))

        return tuple(tuple(map(DeviceId, group.tolist())) for group in groups)

    def get_all_devices(self) -> Tuple[DeviceId, ...]:
        return tuple(map(DeviceId, self.mesh.reshape(-1).tolist()))

    def to_torch_tensor(self) -> torch.Tensor:
        return self.mesh.detach().clone()

    def get_all_ranks(self) -> List[int]:
        return self.mesh.reshape(-1).tolist()

    def get_rank(self) -> int:
        return self.current_rank

    @staticmethod
    def from_exportable_type(
        device_mesh: mpc.DeviceMesh, device_id_map: Mapping[mpc.DeviceId, DeviceId]
    ) -> "DeviceMesh":
        nested_int_list = _map_nested_sequence(device_mesh, lambda x: device_id_map[x])
        return DeviceMesh(torch.tensor(nested_int_list, dtype=torch.int))

    def to_exportable_type(self, device_map: Mapping[DeviceId, mpc.DeviceId]) -> mpc.DeviceMesh:
        return mpc.DeviceMesh(_map_nested_sequence(self.mesh.tolist(), lambda x: device_map[x]))


def to_exportable_reduce_op_type(reduce_op: str) -> mpc.ReduceOp:
    if reduce_op == "sum":
        return mpc.ReduceOp.SUM
    elif reduce_op == "avg":
        return mpc.ReduceOp.AVG
    elif reduce_op == "max":
        return mpc.ReduceOp.MAX
    elif reduce_op == "min":
        return mpc.ReduceOp.MIN
    else:
        raise ValueError(f"Unsupported reduce op: {reduce_op}")


def to_exportable_placement_type(placement: Placement) -> mpc.Placement:
    if placement.is_shard():
        shard = cast(Shard, placement)
        return mpc.Shard(shard.dim)
    elif placement.is_partial():
        partial = cast(Partial, placement)
        return mpc.Partial(to_exportable_reduce_op_type(partial.reduce_op))
    elif placement.is_replicate():
        return mpc.Replicate()
    else:
        raise ValueError(f"Invalid placement: {placement}")


def from_exportable_placement_type(self: mpc.Placement) -> Placement:
    if isinstance(self, mpc.Shard):
        return Shard(self.dim)
    elif isinstance(self, mpc.Partial):
        return Partial(self.reduce_op.value)
    elif isinstance(self, mpc.Replicate):
        return Replicate()
    else:
        raise ValueError(f"Invalid placement: {self}")


def from_exportable_reduce_op_type(reduce_op: mpc.ReduceOp) -> RedOpType:
    if reduce_op == mpc.ReduceOp.SUM:
        return c10d.ReduceOp.SUM
    elif reduce_op == mpc.ReduceOp.AVG:
        return c10d.ReduceOp.AVG
    elif reduce_op == mpc.ReduceOp.MAX:
        return c10d.ReduceOp.MAX
    elif reduce_op == mpc.ReduceOp.MIN:
        return c10d.ReduceOp.MIN
    else:
        raise ValueError(f"Unsupported reduce op: {reduce_op}")


class ShardSpec(PTDTensorSpec):
    """
    This class wraps the `torch.distributed._tensor.placement_types.ShardSpec` class.
    The original `ShardSpec` class' mesh attribute is `DeviceMesh` type, which requires
    process group. So this class uses `mrw.DeviceMesh` instead of torch's `DeviceMesh` which
    does not require process group.
    """

    mesh: DeviceMesh  # type: ignore [assignment]

    def __str__(self) -> str:
        return f"ShardSpec(mesh={self.mesh}, placements={self.placements})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Union['ShardSpec', PTDTensorSpec]) -> bool:  # type: ignore [override]
        if not isinstance(other, (ShardSpec, PTDTensorSpec)):
            return False
        return self.placements == other.placements and self.mesh == other.mesh

    @staticmethod
    def from_exportable_type(
        dtensor_spec: mpc.ShardSpec, device_id_map: Mapping[mpc.DeviceId, DeviceId]
    ) -> "ShardSpec":
        return ShardSpec(
            placements=tuple(
                from_exportable_placement_type(placement) for placement in dtensor_spec.placements
            ),
            mesh=DeviceMesh.from_exportable_type(dtensor_spec.mesh, device_id_map),  # type: ignore
        )

    def to_exportable_type(self, device_map: Mapping[DeviceId, mpc.DeviceId]) -> mpc.ShardSpec:
        return mpc.ShardSpec(
            placements=[to_exportable_placement_type(placement) for placement in self.placements],
            mesh=self.mesh.to_exportable_type(device_map),
        )


@dataclass
class DynamicTensorSpec:
    src: NodeId
    dst: NodeId
    spec: ShardSpec

    def __iter__(self):
        yield self.src
        yield self.dst
        yield self.spec

    @staticmethod
    def from_exportable_type(
        dynamic_tensor_spec: mpc.DynamicTensorSpec, device_id_map: Mapping[mpc.DeviceId, DeviceId]
    ) -> "DynamicTensorSpec":
        return DynamicTensorSpec(
            dynamic_tensor_spec.src,
            dynamic_tensor_spec.dst,
            ShardSpec.from_exportable_type(dynamic_tensor_spec.spec, device_id_map),
        )

    def to_exportable_type(
        self, device_map: Mapping[DeviceId, mpc.DeviceId]
    ) -> mpc.DynamicTensorSpec:
        return mpc.DynamicTensorSpec(self.src, self.dst, self.spec.to_exportable_type(device_map))


@dataclass
class MpppConfig:
    name: str
    devices: Dict[DeviceId, Device]
    static_tensors: Dict[TensorId, ShardSpec]
    dynamic_tensors: List[DynamicTensorSpec]
    device_id_map: Dict[DeviceId, mpc.DeviceId]

    def to_json(self) -> str:
        return self.to_exportable_type().to_json()

    @staticmethod
    def from_exportable_type(mppp_config: mpc.MpppConfig) -> "MpppConfig":
        new_to_original = {
            DeviceId(idx): dev_id for idx, dev_id in enumerate(mppp_config.devices.keys())
        }
        original_to_new = {v: k for k, v in new_to_original.items()}

        return MpppConfig(
            name=mppp_config.name,
            devices={
                new_dev: mppp_config.devices[original_dev]
                for new_dev, original_dev in new_to_original.items()
            },
            static_tensors={
                k: ShardSpec.from_exportable_type(v, original_to_new)
                for k, v in mppp_config.static_tensors.items()
            },
            dynamic_tensors=[
                DynamicTensorSpec.from_exportable_type(dynamic_tensor, original_to_new)
                for dynamic_tensor in mppp_config.dynamic_tensors
            ],
            device_id_map=new_to_original,
        )

    def to_exportable_type(self) -> mpc.MpppConfig:
        return mpc.MpppConfig(
            name=self.name,
            devices={self.device_id_map[dev_id]: device for dev_id, device in self.devices.items()},
            static_tensors={
                k: v.to_exportable_type(self.device_id_map) for k, v in self.static_tensors.items()
            },
            dynamic_tensors=[
                dynamic_tensor.to_exportable_type(self.device_id_map)
                for dynamic_tensor in self.dynamic_tensors
            ],
        )
