from functools import reduce
from typing import Iterator, Mapping, Sequence, Tuple, Union, cast

import torch
from torch.fx.passes.shape_prop import TensorMetadata

from furiosa_llm.parallelize.model_rewriter.mppp_config import Device, DeviceId, RedOpType, ReduceOp
from furiosa_llm.parallelize.model_rewriter.ops.single_device_comm import (
    AllGatherSingle,
    AllReduceSingle,
    AllToAllSingle,
    BroadcastSingle,
    GatherSingle,
    Recv,
    ReduceScatterSingle,
    ReduceSingle,
    Send,
)
from furiosa_llm.parallelize.model_rewriter.ops.types import (
    CommGroup,
    CommOpWithSameInOutDevice,
    MultiDeviceCommOp,
    SingleDeviceCommOp,
)

__all__ = [
    "Reduce",
    "AllReduce",
    "Gather",
    "AllGather",
    "ReduceScatter",
    "AllToAll",
    "Broadcast",
    "SendRecv",
]


def _maybe_change_cpu_dev(dev: torch.device) -> torch.device:
    if dev.type == "cpu":
        return torch.device("cpu")
    else:
        return dev


def _check_same_dev(args: Sequence[torch.Tensor], devices: Iterator[Device]) -> bool:
    return tuple(dev.to_torch_device() for dev in devices) == tuple(
        _maybe_change_cpu_dev(arg.device) for arg in args
    )


def _move_args(
    args: Union[torch.Tensor, Sequence[torch.Tensor]], dst_dev: Device
) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
    if isinstance(args, (list, tuple)):
        return tuple(cast(torch.Tensor, _move_args(arg, dst_dev)) for arg in args)
    else:
        assert isinstance(args, torch.Tensor)
        torch_dev = dst_dev.to_torch_device()
        return args.to(torch_dev) if torch_dev != args.device else args


class Reduce(MultiDeviceCommOp):
    def __init__(
        self,
        reduce_op: RedOpType,
        dst: DeviceId,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ):
        # Do we need to relax this assumption? maybe not..
        if reduce_op != ReduceOp.SUM:
            raise NotImplementedError("Reduce op {reduce_op} is not implemented yet")

        super().__init__(group, device_id_to_device)
        self.reduce_op = reduce_op
        self.dst = dst
        self.dst_torch_device = self.to_device(self.dst)

    def __call__(self, *args, check=False) -> torch.Tensor:
        if check:
            assert _check_same_dev(args, map(self.to_device, self.group))

        moved_args = _move_args(args, self.dst_torch_device)
        if self.reduce_op == ReduceOp.SUM:
            return reduce(torch.add, moved_args)
        else:
            raise NotImplementedError(f"Reduce op {self.reduce_op} is not implemented yet")

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        return ReduceSingle(self.reduce_op, self.dst, device_id, self.group)

    def input_devices(self) -> Tuple[DeviceId, ...]:
        return self.group.group

    def output_devices(self) -> Tuple[DeviceId, ...]:
        return (self.dst,)


class AllReduce(CommOpWithSameInOutDevice):
    reduce_op: RedOpType

    def __init__(
        self,
        reduce_op: RedOpType,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ):
        # Do we need to relax this assumption? maybe not..
        if reduce_op != ReduceOp.SUM:
            raise NotImplementedError("Reduce op {reduce_op} is not implemented yet")

        super().__init__(group, device_id_to_device)
        self.reduce_op = reduce_op
        self.reduce: Reduce = Reduce(
            self.reduce_op, self.group[0], self.group, self.device_id_to_device
        )

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        return AllReduceSingle(device_id, self.reduce_op, self.group)

    def __call__(self, *args, check=False) -> Tuple[torch.Tensor, ...]:
        if check:
            assert _check_same_dev(args, map(self.to_device, self.group))

        res = self.reduce(*args)
        return (res,) + tuple(res.to(arg.device) for arg in args[1:])


class Gather(MultiDeviceCommOp):
    reduce_op: str

    def __init__(
        self,
        dim: int,
        dst: DeviceId,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ):
        super().__init__(group, device_id_to_device)
        self.dst = dst
        self.dim = dim
        self.dst_torch_device = self.to_device(self.dst).to_torch_device()

    def __call__(self, *args, check=False) -> torch.Tensor:
        if check:
            assert _check_same_dev(args, map(self.to_device, self.group))

        moved_args = [
            (arg.to(self.dst_torch_device) if arg.device != self.dst_torch_device else arg)
            for arg in args
        ]
        return torch.cat(moved_args, self.dim)

    def input_devices(self) -> Tuple[DeviceId, ...]:
        return self.group.group

    def output_devices(self) -> Tuple[DeviceId, ...]:
        return (self.dst,)

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        return GatherSingle(self.dst, self.dim, device_id, self.group)


class AllGather(CommOpWithSameInOutDevice):
    dim: int

    def __init__(self, dim, group, device_id_to_device: Mapping[DeviceId, Device]):
        super().__init__(group, device_id_to_device)

        self.dim = dim
        self.group = group
        self.gather = Gather(self.dim, self.group[0], self.group, self.device_id_to_device)

    def __call__(self, *args, check=False) -> Tuple[torch.Tensor, ...]:
        if check:
            assert _check_same_dev(args, map(self.to_device, self.group))

        res = self.gather(*args)
        return (res,) + tuple(res.to(arg.device) for arg in args[1:])

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        return AllGatherSingle(device_id, self.dim, self.group)


class SendRecv(MultiDeviceCommOp):
    def __init__(
        self,
        src: DeviceId,
        dst: DeviceId,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ) -> None:
        super().__init__(group, device_id_to_device)
        self.src = src
        self.dst = dst
        assert len(group) == 2
        assert src in group and dst in group
        self.src_torch_device = self.to_device(src).to_torch_device()
        self.dst_torch_device = self.to_device(dst).to_torch_device()

    def __call__(self, t: torch.Tensor, check=False) -> torch.Tensor:
        if check:
            assert t.device == self.src_torch_device
        return t.to(self.dst_torch_device)

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        if device_id == self.src:
            return Send(self.src, self.dst, self.group)
        else:
            assert device_id == self.dst
            return Recv(self.src, self.dst, self.group, self.dst_torch_device, tensor_meta)

    def input_devices(self) -> Tuple[DeviceId, ...]:
        return (self.src,)

    def output_devices(self) -> Tuple[DeviceId, ...]:
        return (self.dst,)


class ReduceScatter(CommOpWithSameInOutDevice):
    reduce_op: RedOpType
    dim: int

    def __init__(
        self,
        reduce_op: RedOpType,
        dim: int,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ):
        # Do we need to relax this assumption? maybe not..
        super().__init__(group, device_id_to_device)
        if reduce_op != ReduceOp.SUM:
            raise NotImplementedError("Reduce op {reduce_op} is not implemented yet")

        self.reduce_op = reduce_op
        self.dim = dim
        self.torch_devices = tuple(self.to_device(dev).to_torch_device() for dev in group)
        self.reduce = Reduce(self.reduce_op, self.group[0], self.group, self.device_id_to_device)

    def __call__(self, *args, check=False) -> Tuple[torch.Tensor, ...]:
        if check:
            assert _check_same_dev(args, map(self.to_device, self.group))

        res = self.reduce(*args)
        chunks = res.chunk(chunks=len(self.group), dim=self.dim)

        return tuple(chunk.to(device) for chunk, device in zip(chunks, self.torch_devices))

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        return ReduceScatterSingle(device_id, self.reduce_op, self.dim, self.group)


class Broadcast(MultiDeviceCommOp):
    src: DeviceId

    def __init__(
        self,
        src: DeviceId,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ):
        super().__init__(group, device_id_to_device)
        self.src = src
        self.torch_devices = tuple(self.to_device(dev).to_torch_device() for dev in group)
        self.src_torch_device = self.to_device(src).to_torch_device()

    def __call__(self, t: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        assert t.device == self.src_torch_device
        return tuple(t.to(dev) for dev in self.torch_devices)

    def input_devices(self) -> Tuple[DeviceId, ...]:
        return (self.src,)

    def output_devices(self) -> Tuple[DeviceId, ...]:
        return self.group.group

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        torch_device = self.device_id_to_device[device_id].to_torch_device()
        return BroadcastSingle(self.src, tensor_meta, torch_device, device_id, self.group)


# split into src dim and concat with dst dim
# Shard(dst_dim) -> Shard(src_dim)
class AllToAll(CommOpWithSameInOutDevice):
    src_dim: int
    dst_dim: int

    def __init__(
        self,
        src_dim: int,
        dst_dim: int,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ) -> None:
        super().__init__(group, device_id_to_device)
        self.src_dim = src_dim
        self.dst_dim = dst_dim
        self.group_torch_devices = tuple(
            self.to_device(dev_id).to_torch_device() for dev_id in group
        )

    def __call__(self, *args, check=False) -> Tuple[torch.Tensor, ...]:
        if check:
            assert _check_same_dev(args, map(self.to_device, self.group))

        # g * g nested tuple
        _chunks = (arg.chunk(len(self.group), dim=self.src_dim) for arg in args)

        # transpose it
        chunks = tuple(zip(*_chunks))

        return tuple(
            torch.cat(tuple(chunk.to(self.group_torch_devices[i]) for chunk in chunks[i]))
            for i in range(len(self.group))
        )

    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        return AllToAllSingle(self.src_dim, self.dst_dim, device_id, self.group)
