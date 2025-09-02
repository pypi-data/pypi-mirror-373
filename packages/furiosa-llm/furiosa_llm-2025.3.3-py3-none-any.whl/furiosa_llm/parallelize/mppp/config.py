from abc import ABC
from collections import defaultdict
import dataclasses
from dataclasses import dataclass
from enum import Enum
import functools
from functools import cached_property
import json
import os
import re
import typing
from typing import Dict, List, Optional, Sequence

import torch
from typing_extensions import Self, TypeAlias


class ReduceOp(Enum):
    SUM = "sum"
    AVG = "avg"
    MAX = "max"
    MIN = "min"

    def __repr__(self) -> str:
        return self.value


class Placement(ABC): ...


@dataclass(frozen=True)
class Partial(Placement):
    reduce_op: ReduceOp
    type: str = "partial"

    def __post_init__(self):
        assert self.type == "partial"


@dataclass(frozen=True)
class Shard(Placement):
    dim: int
    type: str = "shard"

    def __post_init__(self):
        assert self.type == "shard"


@dataclass(frozen=True)
class Replicate(Placement):
    type: str = "replicate"

    def __post_init__(self):
        assert self.type == "replicate"


NodeId: TypeAlias = str


class DeviceMesh(List):
    def __post_init__(self):
        try:
            torch.tensor(self, dtype=torch.int)
        except Exception:
            raise ValueError(
                "DeviceMesh must be a n-dimensional int type array with fixed dimension sizes"
            )


@dataclass
class ShardSpec:
    placements: List[Placement]
    mesh: DeviceMesh

    def _to_brief_str(self) -> str:
        return f"({self.placements}, {self.mesh})"


class TensorId(NodeId): ...


NPU_PE_RANGE_IDX_RE = re.compile(r"(\d)-(\d)")
POSSIBLE_FUSION_GRANULARITY = {1, 2, 4, 8}


def _verify_device(device: str) -> None:
    kind, *rest = device.split(":")
    if kind == "cpu":
        if rest and (len(rest) != 1 or not rest[0].isdigit()):
            raise ValueError(f"Invalid device string: {device}")
    elif kind == "rngd":
        # furiosa-torch representation with device index
        if len(rest) != 2 or not rest[0].isdigit() or not rest[1].isdigit():
            raise ValueError(f"Invalid device string: {device}")
        if int(rest[1]) not in POSSIBLE_FUSION_GRANULARITY:
            raise ValueError(f"Invalid num pe: {rest[1]}")
    elif kind == "npu":
        # Example of allowed formats: "npu:0:0", "npu:1:*", "npu:1:0-3", "npu:2".
        if not rest[0].isdigit():
            raise ValueError(f"Invalid npu index: {rest[0]}")

        if len(rest) == 1:
            # npu:1
            return

        if len(rest) != 2:
            raise ValueError(f"Invalid device string: {device}")

        if rest[1].isdigit():
            if int(rest[1]) > 7:
                raise ValueError(f"Invalid pe index: {rest[1]}")
        elif NPU_PE_RANGE_IDX_RE.match(rest[1]):
            start_, end_ = rest[1].split("-")
            start, end = int(start_), int(end_) + 1  # Make end inclusive
            core_range = end - start
            if core_range in POSSIBLE_FUSION_GRANULARITY and end % core_range == 0:
                pass
            else:
                raise ValueError(f"Invalid pe index range: {rest[1]}")
        elif rest[1] == "*":
            pass
        else:
            raise ValueError(f"Invalid device string: {device}")
    else:
        raise ValueError(f"Invalid device string: {device}")


# TODO: move this to furiosa-llm/device.py
class UnitDevice(str):
    """Type for representing single chip device."""

    def __init__(self, val: str):
        _verify_device(val)

    @cached_property
    def kind(self) -> str:
        return self.split(":", maxsplit=1)[0]

    @cached_property
    def is_npu(self) -> bool:
        return self.kind in ("npu", "rngd")

    @cached_property
    def idx(self) -> Optional[int]:
        splitted = self.split(":")
        if len(splitted) == 1:
            return None
        elif len(splitted) >= 2:
            return int(splitted[1])
        else:
            raise ValueError(f"Invalid device string: {self}")

    @cached_property
    def pe_idx(self) -> str:
        """Returns pe index of the device.
        Returns one of the two forms: "4-7" (for fusioned one), "2" (for single pe)."""
        kind, *rest = self.split(":")

        if kind != "npu":
            raise ValueError("Only npu devices have pe indexes.")

        if len(rest) == 1 or rest[1] == "*":
            return "0-7"
        elif len(rest) == 2:
            return rest[1]
        else:
            raise ValueError(f"Invalid npu device string: {self}")

    def split_into_single_pes(self) -> List[Self]:
        if self.kind != "npu":
            raise ValueError("Only npu devices can be split into pes.")
        splitted_pe_idx = self.pe_idx.split("-")
        if len(splitted_pe_idx) == 1:
            return [self]
        elif len(splitted_pe_idx) == 2:
            start, end = splitted_pe_idx
            return [type(self)(f"npu:{self.idx}:{i}") for i in range(int(start), int(end) + 1)]
        else:
            raise ValueError(f"Invalid npu device string: {self}")

    def to_torch_device_with_cpu_idx(self) -> torch.device:
        # npu:x:y representation cannot be converted to torch device. So consider it as CPU for now.
        # TODO: fix this to cover all kind of representations for NPU once it's established.
        if self.kind == "npu":
            return torch.device("cpu")
        elif self.kind == "rngd":
            # "rngd:x:y" representation is only for furiosa-torch.
            # When it's converted to torch device, only its first index is used.
            # Fusion information will be passed with environment variable.
            return torch.device(f"rngd:{self.idx}")
        elif self.idx is not None:
            return torch.device(self.kind, self.idx)
        else:
            return torch.device(self.kind)

    def to_torch_device(self) -> torch.device:
        # Ignore device index if kind is "cpu".
        if self.kind == "cpu":
            return torch.device("cpu")
        else:
            return self.to_torch_device_with_cpu_idx()

    @property
    def num_pe(self) -> int:
        if self.kind == "rngd":
            # FIXME: "rngd:x:y" representation is only for furiosa-torch.
            # Two indices (x, y) mean device index and number of fusioned pes respectively.
            return int(self.rsplit(":", maxsplit=1)[-1])
        elif self.kind == "npu":
            return len(self.split_into_single_pes())
        else:
            raise ValueError("num_pe should not be called for non-npu devices.")


# TODO : core logic of `fusion_pes_for_unit_device` is duplication to `fusion_pes` in device.py.
# resolve the duplication later
def fusion_pes_for_unit_device(devices: Sequence[UnitDevice]) -> UnitDevice:
    """Given a list of single pe devices, fuse them into a single fused pe device."""
    assert all(len(dev.split_into_single_pes()) == 1 for dev in devices)

    num_pes = len(devices)
    if num_pes not in POSSIBLE_FUSION_GRANULARITY:
        raise ValueError("Only 1, 2, 4, 8 PEs can be fused.")

    if num_pes == 1:
        return devices[0]
    devices = sorted(devices)

    # All devices must be single pe (in the form of "npu:\d:\d")
    dev_idx = devices[0].idx

    start_pe_idx = int(devices[0].pe_idx)

    if start_pe_idx % num_pes != 0:
        raise ValueError(f"Invalid start pe index for fusion: {start_pe_idx}")

    for device, expected_pe_idx in zip(devices, range(start_pe_idx, start_pe_idx + num_pes)):
        if int(UnitDevice(device).pe_idx) != expected_pe_idx:
            raise ValueError(
                "Unexpected pe index. Expected: {expected_pe_idx}, actual: {device.idx}"
            )

    return UnitDevice(f"npu:{dev_idx}:{start_pe_idx}-{start_pe_idx + num_pes - 1}")


class Device(str):
    """
    Device in MpppConfig. Multiple chips can be represented in a single `Device` if they are
        grouped together for interchip tensor parallelism.
    """

    def __init__(self, val: str) -> None:
        unit_devs = tuple(map(UnitDevice, map(str.strip, val.split(","))))

        dev_kinds = set(d.kind for d in unit_devs)
        if len(dev_kinds) > 1:
            raise ValueError(
                f"All unit devices must be in same kind. But multiple kinds found: {dev_kinds}"
            )

        if unit_devs[0].kind == "npu":
            unit_devs_by_chip_idx: Dict[int, List] = defaultdict(list)
            for unit_dev in unit_devs:
                assert unit_dev.idx is not None
                unit_devs_by_chip_idx[unit_dev.idx] += unit_dev.split_into_single_pes()

            # unit devs fused
            unit_devs = tuple(
                fusion_pes_for_unit_device(val) for val in unit_devs_by_chip_idx.values()
            )

        if len(unit_devs) != len(set(unit_dev.idx for unit_dev in unit_devs)):
            raise ValueError(
                f"All unit devices must have unique index. But found duplicates: {unit_devs}"
            )

        self.unit_devices = unit_devs
        self.num_chip = len(unit_devs)
        self.kind = unit_devs[0].kind

    @cached_property
    def is_npu(self) -> bool:
        return self.get_unit_devices()[0].is_npu

    @cached_property
    def idx(self) -> Optional[int]:
        unit_devs = self.get_unit_devices()
        if len(unit_devs) != 1:
            raise ValueError(f"Cannot get index if more than one unit device exist: {unit_devs}")
        return unit_devs[0].idx

    @functools.lru_cache
    def get_unit_devices(self) -> List[UnitDevice]:
        return list(map(UnitDevice, map(str.strip, self.split(","))))

    @cached_property
    def num_pe_per_chip(self) -> int:
        if not self.is_npu:
            raise ValueError("num_pe_per_dev should not be called for non-npu devices.")
        num_pes = set(unit_dev.num_pe for unit_dev in self.unit_devices)
        if len(num_pes) > 1:
            raise ValueError(
                f"Unit devices with different number of pes found: {self.unit_devices}"
            )
        return num_pes.pop()

    def split_into_single_pes(self) -> List[Self]:
        if self.kind != "npu":
            raise ValueError("Only npu devices can be split into pes.")
        return list(
            map(
                self.__class__,
                sum(map(UnitDevice.split_into_single_pes, self.get_unit_devices()), []),
            )
        )

    @cached_property
    def is_single_pe(self) -> bool:
        if not self.is_npu:
            return False
        unit_devs = self.get_unit_devices()
        return len(unit_devs) == 1 and unit_devs[0].num_pe == 1

    def to_torch_device_with_cpu_idx(self) -> torch.device:
        if self.kind == "npu":
            return torch.device("cpu")
        else:
            devs = self.get_unit_devices()

            if len(devs) == 1:
                return devs[0].to_torch_device_with_cpu_idx()
            raise ValueError("Only npu devices can be converted to torch device with cpu index.")

    def to_torch_device(self) -> torch.device:
        device = self.to_torch_device_with_cpu_idx()
        if device.type == "cpu":
            return torch.device("cpu")
        else:
            return device


@dataclass
class DynamicTensorSpec:
    src: NodeId
    dst: NodeId
    spec: ShardSpec

    def __iter__(self):
        yield self.src
        yield self.dst
        yield self.spec


class MpppConfigEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, torch.Tensor):
            return obj.tolist()
        elif isinstance(obj, ReduceOp):
            return obj.value
        return super().default(obj)


class SerializationError(Exception):
    def __init__(self, message):
        super().__init__(message)


def _dict_to_dataclass(cls, data):
    if isinstance(data, (str, int)):
        return cls(data)
    elif dataclasses.is_dataclass(cls):
        obj = cls(**data)  # type: ignore[assignment]
        type_hints = typing.get_type_hints(cls)
        for f in dataclasses.fields(cls):
            name = f.name
            new_field_obj = _dict_to_dataclass(type_hints[name], getattr(obj, name))
            setattr(obj, name, new_field_obj)
        return obj
    elif isinstance(data, list) and typing.get_origin(cls) is list:
        d_type = typing.get_args(cls)[0]
        return [_dict_to_dataclass(d_type, d) for d in data]
    elif isinstance(data, dict) and typing.get_origin(cls) is dict:
        k_type, v_type = typing.get_args(cls)
        return {
            _dict_to_dataclass(k_type, k): _dict_to_dataclass(v_type, v) for k, v in data.items()
        }
    else:
        try:
            if isinstance(data, dict):
                obj = cls(**data)
            else:
                obj = cls(data)
        except TypeError:
            for subclass in cls.__subclasses__():
                try:
                    obj = subclass(**data)
                    return obj
                except TypeError:
                    pass
            raise SerializationError(f"Cannot deserialize {data} to {cls}")
    return data


class DeviceId(str): ...


@dataclass
class MpppConfig:
    name: str
    devices: Dict[DeviceId, Device]
    static_tensors: Dict[TensorId, ShardSpec]
    dynamic_tensors: List[DynamicTensorSpec]

    @classmethod
    def from_str(cls, val: str) -> "MpppConfig":
        return _dict_to_dataclass(cls, json.loads(val))

    @classmethod
    def load(cls, path: os.PathLike) -> "MpppConfig":
        with open(path, "r") as f:
            return cls.from_str(f.read())

    def to_json(self) -> str:
        return json.dumps(
            dataclasses.asdict(self),
            cls=MpppConfigEncoder,
            indent=4,
            allow_nan=False,
            sort_keys=True,
        )

    def export(self, path: os.PathLike):
        with open(path, "w") as f:
            f.write(self.to_json())
