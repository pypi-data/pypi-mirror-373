from typing import Dict, Optional

import torch
from torch.fx.passes.shape_prop import TensorMetadata

from furiosa_llm.parallelize.model_rewriter.mppp_config import DeviceId, RedOpType, ReduceOp
from furiosa_llm.parallelize.model_rewriter.ops.types import CommGroup, SingleDeviceCommOp
from furiosa_llm.parallelize.pipeline.types import CommMetaVal, SuperTaskKind

__ALL__ = [
    "ReduceSingle",
    "AllReduceSingle",
    "GatherSingle",
    "AllGatherSingle",
    "ReduceScatterSingle",
    "AllToAllSingle",
    "BroadcastSingle",
    "Send",
    "Recv",
]


class GatherSingle(SingleDeviceCommOp):
    def __init__(
        self,
        dst: DeviceId,
        dim: int,
        device_id: DeviceId,
        group: CommGroup,
    ):
        super().__init__(group, device_id)
        self.device_id = device_id
        self.dst = dst
        self.dim = dim

    def __call__(self, *args, check=False) -> Optional[torch.Tensor]:
        assert len(args) == 1
        if self.dst == self.device_id:
            repeat_size = [1 if i != self.dim else len(self.group) for i in range(args[0].dim())]
            return args[0].repeat(repeat_size)
        else:
            return None

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "dim": self.dim,
            "dst": self.dst,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.GATHER


class ReduceSingle(SingleDeviceCommOp):
    def __init__(
        self,
        reduce_op: RedOpType,
        dst: DeviceId,
        device_id: DeviceId,
        group: CommGroup,
    ):
        # Do we need to relax this assumption? maybe not..
        assert reduce_op == ReduceOp.SUM

        super().__init__(group, device_id)
        self.reduce_op = reduce_op
        self.device_id = device_id
        self.dst = dst

    def __call__(self, *args, check=False) -> Optional[torch.Tensor]:
        if self.device_id == self.dst:
            return args[0]
        else:
            return None

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "reduce_op": self.reduce_op.value,
            "dst": self.dst,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.REDUCE


class AllReduceSingle(SingleDeviceCommOp):
    def __init__(
        self,
        device_id: DeviceId,
        reduce_op: RedOpType,
        group: CommGroup,
    ):
        # Do we need to relax this assumption? maybe not..
        assert reduce_op == ReduceOp.SUM

        super().__init__(group, device_id)
        self.reduce_op = reduce_op
        self.device_id = device_id

    def __call__(self, *args, check=False) -> torch.Tensor:
        return args[0]

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "reduce_op": self.reduce_op.value,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.ALL_REDUCE


class AllGatherSingle(SingleDeviceCommOp):
    def __init__(
        self,
        device_id: DeviceId,
        dim: int,
        group: CommGroup,
    ):
        super().__init__(group, device_id)
        self.device_id = device_id
        self.dim = dim

    def __call__(self, *args, check=False) -> torch.Tensor:
        assert len(args) == 1
        repeat_size = [1 if i != self.dim else len(self.group) for i in range(args[0].dim())]
        return args[0].repeat(repeat_size)

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "dim": self.dim,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.ALL_GATHER


class Send(SingleDeviceCommOp):
    def __init__(self, src: DeviceId, dst: DeviceId, group: CommGroup):
        super().__init__(group, src)
        self.dst = dst
        self.src = src
        self.group = group

    def __call__(self, *args):
        pass

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {}

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.SEND


class Recv(SingleDeviceCommOp):
    def __init__(
        self,
        src: DeviceId,
        dst: DeviceId,
        group: CommGroup,
        torch_device: torch.device,
        tensor_meta: TensorMetadata,
    ):
        super().__init__(group, dst)
        self.dst = dst
        self.src = src
        self.group = group
        self.tensor_meta = tensor_meta
        self.device = torch_device

    def __call__(self, *args):
        return torch.zeros(self.tensor_meta.shape, dtype=self.tensor_meta.dtype, device=self.device)

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {}

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.RECV


class ReduceScatterSingle(SingleDeviceCommOp):
    dim: int

    def __init__(
        self,
        device_id: DeviceId,
        reduce_op: RedOpType,
        dim: int,
        group: CommGroup,
    ):
        # Do we need to relax this assumption? maybe not..
        assert reduce_op == ReduceOp.SUM

        super().__init__(group, device_id)
        self.reduce_op = reduce_op
        self.device_id = device_id
        self.dim = dim

    def __call__(self, *args) -> torch.Tensor:
        return torch.chunk(args[0], len(self.group), self.dim)[0]

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "reduce_op": str(self.reduce_op),
            "dim": self.dim,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.REDUCE_SCATTER


class AllToAllSingle(SingleDeviceCommOp):
    def __init__(
        self,
        src_dim: int,
        dst_dim: int,
        device_id: DeviceId,
        group: CommGroup,
    ):
        super().__init__(group, device_id)
        self.device_id = device_id
        self.src_dim = src_dim
        self.dst_dim = dst_dim

    def __call__(self, *args) -> torch.Tensor:
        assert len(args) == 1
        sliced = torch.chunk(args[0], len(self.group), dim=self.src_dim)[0]
        repeat_size = [1 if i != self.dst_dim else len(self.group) for i in range(args[0].dim())]

        return sliced.repeat(repeat_size)

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "src_dim": self.src_dim,
            "dst_dim": self.dst_dim,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.ALLTOALL


class BroadcastSingle(SingleDeviceCommOp):
    def __init__(
        self,
        src: DeviceId,
        tensor_meta: TensorMetadata,
        torch_device: torch.device,
        device_id: DeviceId,
        group: CommGroup,
    ):
        super().__init__(group, device_id)
        self.device_id = device_id
        self.src = src
        self.tensor_meta = tensor_meta
        self.torch_device = torch_device

    def __call__(self, *args) -> torch.Tensor:
        if self.device_id == self.src:
            assert len(args) == 1
            return args[0]
        else:
            assert len(args) == 0
            return torch.zeros(
                self.tensor_meta.shape, dtype=self.tensor_meta.dtype, device=self.torch_device
            )

    def metadata(self) -> Dict[str, CommMetaVal]:
        return {
            "src": self.src,
        }

    def kind(self) -> SuperTaskKind:
        return SuperTaskKind.BROADCAST
