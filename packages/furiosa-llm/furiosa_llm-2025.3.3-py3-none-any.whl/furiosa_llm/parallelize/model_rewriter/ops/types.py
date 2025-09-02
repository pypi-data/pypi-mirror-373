from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Mapping, Tuple

import torch
from torch.fx.passes.shape_prop import TensorMetadata

from furiosa_llm.parallelize.model_rewriter.mppp_config import Device, DeviceId
from furiosa_llm.parallelize.pipeline.types import CommMetaVal, SuperTaskKind


class Op(ABC, torch.nn.Module):
    def __init__(self):
        super().__init__()
        # This is needed for ops to be used as FX graph call function node.
        # For more details, refer to ``torch.fx.graph.Graph.create_node``.
        self.__name__ = self.name()

    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def __call__(self, *args): ...

    def forward(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)


@dataclass
class CommGroup:
    id: int
    group: Tuple[DeviceId, ...]  # sequence of ranks

    def __iter__(self):
        return iter(self.group)

    def __len__(self):
        return len(self.group)

    def __getitem__(self, idx: int) -> DeviceId:
        return self.group[idx]

    def index(self, elem: DeviceId) -> int:
        return self.group.index(elem)

    def __contains__(self, dev_id: DeviceId) -> bool:
        return dev_id in self.group

    def to_list(self) -> List[DeviceId]:
        return list(self.group)


class SingleDeviceCommOp(Op, ABC):
    """Abstract class for mimicking communication operations running on single device,
    exactly corresponding to single communication supertask in ``Pipeline``.

    SingleDeviceCommOp can take and return tensors on same single device. When it's called,
    it just returns tensor of same shape as if corresponding single device communication operation is run.
    No actual communication happens. This is for maintaining FX graph containing `SingleDeviceCommOp`s still executable,
    which is needed for Shape Propagation and useful for testing.
    """

    def __init__(self, group: CommGroup, device_id: DeviceId):
        super().__init__()
        self.group = group
        self.device_id = device_id

    @abstractmethod
    def metadata(self) -> Dict[str, CommMetaVal]: ...

    @abstractmethod
    def kind(self) -> SuperTaskKind: ...


class MultiDeviceCommOp(Op, ABC):
    """Abstract class for communication operations running on multiple devices.

    MultiDeviceCommOp can take and return tensors on multiple devices,
    and actually perform corresponding communication and computation when it's called.
    """

    def __init__(
        self,
        group: CommGroup,
        device_id_to_device: Mapping[DeviceId, Device],
    ) -> None:
        super().__init__()
        self.group = group
        self.device_id_to_device = device_id_to_device

    @abstractmethod
    def input_devices(self) -> Tuple[DeviceId, ...]: ...

    @abstractmethod
    def output_devices(self) -> Tuple[DeviceId, ...]: ...

    def to_device(self, device_id: DeviceId) -> Device:
        return self.device_id_to_device[device_id]

    @abstractmethod
    def get_single_dev_op(
        self, device_id: DeviceId, tensor_meta: TensorMetadata
    ) -> SingleDeviceCommOp:
        """Convert ``MultiDeviceCommOp`` to ``SingleDeviceCommOp`` for given ``device_id`` and ``tensor_meta``."""
        ...


class CommOpWithSameInOutDevice(MultiDeviceCommOp):
    def input_devices(self) -> Tuple[DeviceId, ...]:
        return self.group.group

    def output_devices(self) -> Tuple[DeviceId, ...]:
        return self.group.group
