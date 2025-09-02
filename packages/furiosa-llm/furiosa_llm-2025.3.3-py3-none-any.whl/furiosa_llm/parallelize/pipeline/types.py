from collections import Counter, defaultdict, deque
from contextlib import contextmanager
import copy
import dataclasses
from dataclasses import InitVar, dataclass, fields
from enum import Enum
from functools import cached_property
import itertools
from itertools import chain
import json
import os
from pathlib import PosixPath
import typing
from typing import (
    Any,
    DefaultDict,
    Deque,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

from furiosa_torch_ext.torch_ext import preprocess
from safetensors import safe_open
import torch
from torch._subclasses import FakeTensor, FakeTensorMode
from torch.fx import GraphModule, Node
from torch.fx.passes.shape_prop import ShapeProp

from furiosa_llm.parallelize.compiler_config import BlockType
from furiosa_llm.parallelize.export.graphmodule import deserialize_gm
from furiosa_llm.parallelize.export.tensor import ParamfileFormat, ParamFileInfo
import furiosa_llm.parallelize.model_rewriter.mppp_config as mrw
from furiosa_llm.parallelize.mppp.config import Device, DeviceId
from furiosa_llm.parallelize.node_meta import get_spec
from furiosa_llm.parallelize.utils import zip_equal

SCHEMA_VERSION = "0.1.0"


class DataBlobId(str): ...


class ParamFileId(str): ...


class Placements(List[Tuple[int, int]]):
    @staticmethod
    def from_spec(
        spec: mrw.ShardSpec, device_id: mrw.DeviceId, unsharded_tensor_shape: Sequence[int]
    ) -> "Placements":
        device_mesh = spec.mesh
        indexes = device_mesh.get_coordinate(device_id)
        _range: List[Tuple[int, int]] = [(0, s) for s in unsharded_tensor_shape]

        cur_device_group = device_mesh.to_torch_tensor()

        assert len(indexes) == len(spec.placements)
        for index, placement in zip(indexes, spec.placements):
            # we assume there is no tensor with partial placement among input, output and weight tensors.
            assert not placement.is_partial()
            if placement.is_shard():
                shard = cast(mrw.Shard, placement)
                group_size = len(cur_device_group)
                # assume there's at most one sharding for each dimension
                assert _range[shard.dim][0] == 0
                length = _range[shard.dim][1] - _range[shard.dim][0]
                chunk_size = length // group_size

                _range[shard.dim] = (
                    chunk_size * index,
                    chunk_size * (index + 1),
                )
                # don't consider uneven sharding now.
                assert length % group_size == 0, "We only consider even partitioning"
            cur_device_group = cur_device_group[index]
        return Placements(_range)

    @staticmethod
    def from_node(node: Node) -> "Placements":
        spec = get_spec(node)
        assert isinstance(spec, mrw.ShardSpec), spec
        device_id = node.meta["device_id"]

        unsharded_shape = list(node.meta["tensor_meta"].shape)
        for placement, group_size in zip(spec.placements, spec.mesh.to_torch_tensor().shape):
            if not placement.is_shard():
                continue
            shard = cast(mrw.Shard, placement)
            unsharded_shape[shard.dim] *= group_size

        return Placements.from_spec(spec, device_id, unsharded_shape)


@dataclass
class ParamValue:
    param_file: ParamFileId
    name: str
    name_in_graph: str  # name in graph/dfg
    placements: Placements

    def eq_except_name_in_graph(self, other):
        if not isinstance(other, ParamValue):
            return False
        return (
            self.param_file == other.param_file
            and self.name == other.name
            and self.placements == other.placements
        )


def get_pipeline_dtype(torch_dtype: torch.dtype) -> str:
    converter = {
        "int8": "i8",
        "uint8": "u8",
        "float16": "f16",
        "float32": "f32",
        "float64": "f64",
        "int64": "i64",
        "int32": "i32",
        "bfloat16": "bf16",
        "bool": "bool",
    }

    original_name = str(torch_dtype)
    assert original_name.startswith("torch."), original_name
    name = original_name[6:]
    assert name in converter, f"not supported dtype: {torch_dtype}"

    return converter[name]


class Dtype(str):
    def __new__(cls, dtype: Union[str, torch.dtype]):
        if isinstance(dtype, str):
            return super().__new__(cls, dtype)
        elif isinstance(dtype, torch.dtype):
            return super().__new__(cls, get_pipeline_dtype(dtype))
        else:
            raise ValueError(f"Invalid dtype: {dtype}")

    def to_torch_dtype(self) -> torch.dtype:
        if self == "f32":
            return torch.float32
        elif self == "f64":
            return torch.float64
        elif self == "i64":
            return torch.int64
        elif self == "i32":
            return torch.int32
        elif self == "bf16":
            return torch.bfloat16
        elif self == "bool":
            return torch.bool
        elif self == "i8":
            return torch.int8
        elif self == "u8":
            return torch.uint8
        else:
            raise NotImplementedError(f"Not supported dtype: {self}")


@dataclass
class ParamInfo:
    shape: List[int]
    dtype: Dtype
    value: ParamValue


@dataclass
class TensorInfo:
    shape: List[int]
    dtype: Dtype

    @classmethod
    def from_node_tensor_meta_data(
        cls, t: torch.fx.passes.shape_prop.TensorMetadata
    ) -> "TensorInfo":
        return cls(shape=list(t.shape), dtype=Dtype(t.dtype))

    @classmethod
    def from_node(cls, node: torch.fx.Node) -> "TensorInfo":
        return cls.from_node_tensor_meta_data(node.meta["tensor_meta"])

    def __eq__(self, other):
        if not isinstance(other, TensorInfo):
            return False
        return self.shape == other.shape and self.dtype == other.dtype

    def __hash__(self):
        return hash((tuple(self.shape), self.dtype))


@dataclass
class TensorInfoWithPlacement(TensorInfo):
    placements: Placements

    @classmethod
    def from_tensor_info(
        cls, tensor_info: TensorInfo, placements: Placements
    ) -> "TensorInfoWithPlacement":
        return cls(shape=tensor_info.shape, dtype=tensor_info.dtype, placements=placements)

    @classmethod
    def from_node(cls, node: Node) -> "TensorInfoWithPlacement":
        placements = Placements.from_node(node)
        return cls.from_tensor_info(TensorInfo.from_node(node), placements)


class SuperTaskKind(str, Enum):
    # computation supertask kind
    DFG = "dfg"
    FX = "fx"
    EDF = "edf"

    # source, sink supertasks
    INPUT = "input"
    OUTPUT = "output"

    # comm ops
    SEND = "send"
    RECV = "recv"
    REDUCE = "reduce"
    ALL_REDUCE = "all_reduce"
    GATHER = "gather"
    ALL_GATHER = "all_gather"
    REDUCE_SCATTER = "reduce_scatter"
    ALLTOALL = "all_to_all"
    BROADCAST = "broadcast"

    @staticmethod
    def from_str(val: str) -> "SuperTaskKind":
        return SuperTaskKind(val)

    def to_ir_kind(self) -> str:
        ret = _SUPERTASK_KIND_TO_IR_KIND.get(self, None)
        if ret is None:
            raise ValueError(f"{self} cannot be converted to target ir")
        return ret


_SUPERTASK_KIND_TO_IR_KIND = {
    SuperTaskKind.DFG: "dfg",
    SuperTaskKind.EDF: "edf",
}


class NameAfterMakeFx(str): ...


class NameBeforeTransform(str): ...


@dataclass
class SuperTask:
    kind: SuperTaskKind
    inputs: List[NameAfterMakeFx]
    outputs: List[NameAfterMakeFx]

    def is_input(self) -> bool:
        return self.kind is SuperTaskKind.INPUT

    def is_output(self) -> bool:
        return self.kind is SuperTaskKind.OUTPUT

    def shallow_copy_with_replaced_inputs(self, new_inputs: List[NameAfterMakeFx]):
        copied = copy.copy(self)
        copied.inputs = new_inputs
        return copied

    def shallow_copy_with_replaced_outputs(self, new_outputs: List[NameAfterMakeFx]):
        copied = copy.copy(self)
        copied.outputs = new_outputs
        return copied

    def _eq_except_for_inoutputs_and_groups(self, other: "SuperTask") -> bool:
        # this function is not for general use; only for equality checks
        # between overriding pipeline (by calling `LLM.from_artifacts`) and directly-generated (by calling `LLM.__init__`) pipeline.
        if type(self) is not type(other):
            return False

        other_shallow_copy = copy.copy(other)
        other_shallow_copy.inputs = self.inputs
        other_shallow_copy.outputs = self.outputs

        if isinstance(other_shallow_copy, CommSuperTask):  # FIXME : recheck if it is safe choice
            assert isinstance(self, CommSuperTask)
            other_shallow_copy.group = self.group

        return other_shallow_copy == self


@dataclass
class InOutputSuperTask(SuperTask): ...


@dataclass
class SuperTaskWithDevice(SuperTask):
    device: DeviceId


@dataclass
class TensorGenInfo:
    # this is our adoption of class `TensorMetadata` from torch.fx.passes.shape_prop
    shape: torch.Size
    dtype: torch.dtype

    @classmethod
    def deepcopy_to_fake_tensor_mode(cls, fake_mode: FakeTensorMode):

        @contextmanager
        def helper():
            assert not hasattr(cls, "__deepcopy__")
            cls.__deepcopy__ = lambda self, memo: self.to_fake_tensor(fake_mode)
            try:
                yield
            finally:
                delattr(cls, "__deepcopy__")

        return helper()

    def to_fake_tensor(self, fake_mode: FakeTensorMode) -> FakeTensor:
        with fake_mode:
            return torch.zeros(self.shape, dtype=self.dtype)  # type: ignore [return-value]


@dataclass
class CompSuperTask(SuperTaskWithDevice):
    data: Optional[str] = None  # serialized data
    data_blob: Optional[DataBlobId] = None  # id for data blob

    def __post_init__(self):
        if self.data is None and self.data_blob is None:
            raise ValueError("Either data or data_blob should not be None")

    def shallow_copy_with_replaced_device(self, device_id: DeviceId) -> "CompSuperTask":
        copied = copy.copy(self)
        copied.device = device_id
        return copied


CommMetaVal = Union[int, str]


@dataclass
class CommSuperTask(SuperTaskWithDevice):
    group: Optional[str]
    device_idx: int
    metadata: Dict[str, CommMetaVal]


@dataclass
class MetadataTensor(TensorInfo):
    idx: int

    def __eq__(self, other):
        if not isinstance(other, MetadataTensor):
            return False
        return super().__eq__(other) and self.idx == other.idx


@dataclass
class MetadataTensorSlice:
    placements: Placements
    origin: str
    dtype: Dtype
    device: DeviceId

    def shallow_copy_with_replaced_device(self, new_device: DeviceId) -> "MetadataTensorSlice":
        copied = copy.copy(self)
        copied.device = new_device
        return copied


@dataclass
class MetadataTensors:
    inputs: Dict[NameBeforeTransform, MetadataTensor]
    outputs: Dict[NameBeforeTransform, MetadataTensor]


@dataclass
class MetadataTensorSlices:
    inputs: Dict[NameAfterMakeFx, MetadataTensorSlice]
    outputs: Dict[NameAfterMakeFx, MetadataTensorSlice]


@dataclass()
class MetaData:
    tensors: MetadataTensors
    tensor_slices: MetadataTensorSlices

    def validate(
        self,
        tensors: Optional[Dict[NameAfterMakeFx, Union[TensorInfo, ParamInfo]]] = None,
        devices: Optional[Dict[DeviceId, Device]] = None,
        supertasks: Optional[
            Dict["SuperTaskId", Union[InOutputSuperTask, CompSuperTask, CommSuperTask]]
        ] = None,
    ):
        if tensors:
            # every check item of `validate_tensors_metadata_consistency` depends on `tensors`
            self.validate_tensors_metadata_consistency(tensors)
        self.validate_metadata_attributes(devices, supertasks)

    def validate_metadata_attributes(
        self,
        devices: Optional[Dict[DeviceId, Device]] = None,
        supertasks: Optional[
            Dict["SuperTaskId", Union[InOutputSuperTask, CompSuperTask, CommSuperTask]]
        ] = None,
    ):
        """Validates `Pipeline.metadata`.
        Specifically, following properties of `Pipeline.metadata` will be checked :
            a. Collection of `MetadataTensorSlice.device` from `Pipeline.metadata.tensor_slices.{inputs|outputs}`
                must be a subset of `Pipeline.devices`. If `devices` is None, this check will be skipped.
            b. The collection of `MetadataTensorSlice.origin` from `Pipeline.metadata.tensor_slices.{inputs|outputs}`
                must be equal to the keys of `Pipeline.metadata.tensors`.
            c. For each `MetadataTensorSlice` from `Pipeline.metadata.tensor_slices.inputs(outputs)`,
                there is a corresponding `MetadataTensors` from `Pipeline.metadata.tensors.inputs(outputs)` satisfying:
                - `MetadataTensorSlice.origin` is key for  the `MetadataTensors` within `Pipeline.metadata.tensors`
                - `MetadataTensorSlice.dtype` is equal to `MetadataTensors.dtype`
                - `MetadataTensorSlice.shape` is a subplacement of `MetadataTensors.shape`.
                    That is, `MetadataTensorSlice.shape` smaller then `MetadataTensors.shape` in tuple order.
            d. For `SuperTaskWithDevice` type supertasks (currently, either `Comp` or `Comm` supertasks),
                and for each tensor slice in the supertask's input or output,
                the corresponding `MetadataTensorSlice.device` must match the supertask's `SuperTaskWithDevice.device`.
                If `supertasks` is None, this check will be skipped.
            e. For Input(Output) supertask, its outputs(inputs) must be equal to keys of .metadata.tensor_slices.inputs(outputs).
                If `supertasks` is None, this check will be skipped.
        """
        if devices is not None:
            devices_in_metadata: Set[DeviceId] = set(
                metadata_ts.device
                for metadata_ts in chain(
                    self.tensor_slices.inputs.values(), self.tensor_slices.outputs.values()
                )
            )
            # validate check item a.
            if not devices_in_metadata.issubset(devices.keys()):
                raise (
                    ValueError(
                        f"Collection of devices from `.metadata` which is {devices_in_metadata} "
                        f"must be equal keys of `Pipeline.devices` {devices.keys()}."
                    )
                )

        def is_valid_placement(placements: Sequence[Tuple[int, int]], shape: Sequence[int]) -> bool:
            return all(
                (placement[0] >= 0 and placement[1] <= dim_size)
                for placement, dim_size in zip(placements, shape)
            ) and len(placements) == len(shape)

        def is_corresponding_metadatatensor(
            metadata_ts: MetadataTensorSlice, metadata_tensor: MetadataTensor
        ) -> bool:
            return metadata_ts.dtype == metadata_tensor.dtype and is_valid_placement(
                metadata_ts.placements, metadata_tensor.shape
            )

        # validate check item b,c.
        for attr in ["inputs", "outputs"]:
            origins_from_metadata_ts = {
                ts.origin for ts in getattr(self.tensor_slices, attr).values()
            }
            keys_of_metadata_tensors = set(getattr(self.tensors, attr).keys())
            if origins_from_metadata_ts != keys_of_metadata_tensors:
                raise (
                    ValueError(
                        f"Collection of `MetadataTensorSlice.origin` from `Pipeline.metadata.tensor_slices.{attr}` "
                        f"must be equal to keys of `Pipeline.metadata.tensors.{attr}`. "
                        f"However, they were {origins_from_metadata_ts} and {keys_of_metadata_tensors} respectively."
                    )
                )
            unmatched_ts_and_tensor = [
                (ts, getattr(self.tensors, attr)[ts.origin])
                for ts in getattr(self.tensor_slices, attr).values()
                if not is_corresponding_metadatatensor(ts, getattr(self.tensors, attr)[ts.origin])
            ]

            if unmatched_ts_and_tensor:
                raise ValueError(
                    f"There was no corresponding `MetadataTensors` for following "
                    f"`MetadataTensorSlice`s : {unmatched_ts_and_tensor}, "
                    f"from  `Pipeline.metadata.tensor_slices.{attr}."
                )

        if supertasks is None:
            return
        # validate check item d.
        metadata_ts_devices: Dict[NameAfterMakeFx, DeviceId] = {
            ts: metadata_ts.device
            for ts, metadata_ts in (self.tensor_slices.inputs | self.tensor_slices.outputs).items()
        }
        input_supertask = next(spt for spt in supertasks.values() if spt.is_input())
        output_supertask = next(spt for spt in supertasks.values() if spt.is_output())

        ts_device_info_from_spt: Dict[NameAfterMakeFx, DeviceId] = {
            tensor: spt.device
            for spt in supertasks.values()
            if isinstance(spt, SuperTaskWithDevice)
            for tensor in (spt.inputs + spt.outputs)
            if tensor in input_supertask.outputs + output_supertask.inputs
        }

        diffs_in_device = set(metadata_ts_devices.items()) - set(ts_device_info_from_spt.items())
        # FIXME(ileixe): https://furiosa-ai.slack.com/archives/C07RVETN63D/p1741272146009429?thread_ts=1740708131.511209&cid=C07RVETN63D
        if diffs_in_device:
            raise ValueError(
                "The device info of following tensor slices are not aligned with device info "
                f"within the supertasks : {diffs_in_device}."
            )

        # validate check item e.
        inoutput_spt = dict()
        inoutput_spt["input"] = next(spt for spt in supertasks.values() if spt.is_input())
        inoutput_spt["output"] = next(spt for spt in supertasks.values() if spt.is_output())
        for spt_type in ["input", "output"]:
            target_spt_field = "outputs" if spt_type == "input" else "inputs"
            field_to_check = set(getattr(inoutput_spt[spt_type], target_spt_field))
            corr_ts_set = set(getattr(self.tensor_slices, spt_type + "s").keys())
            if field_to_check != corr_ts_set:
                raise ValueError(
                    (
                        f"{target_spt_field} of {spt_type.capitalize()} SuperTask must be "
                        f"equal to Pipeline.metadata.tensor_slices.{spt_type}s, "
                        + f"however we got {field_to_check} and {corr_ts_set}."
                    )
                )

    def validate_tensors_metadata_consistency(
        self, tensors: Dict[NameAfterMakeFx, Union[TensorInfo, ParamInfo]]
    ) -> None:
        """Validates consistency between `Pipeline.metadata` and `Pipeline.tensors`
        Specifically, following properties will be checked :
            a. Each key in `Pipeline.metadata.tensor_slices.inputs(outputs)` must exist in `Pipeline.tensors`.
            b. For each tensor name in `Pipeline.metadata.tensor_slices.inputs(outputs)`
                must exist in `Pipeline.tensors` with a matching tensor name (as ensured by the above check),
                and the value satisfies the followings:
                - the value is of type `TensorInfo`
                For `MetadataTensorSlice` in `Pipeline.metadata.tensor_slices.inputs(outputs)` with matched tensor name
                - `MetadataTensorSlice.dtype` and `TensorInfo.dtype` must be equal
                - `MetadataTensorSlice.placements` must be consistent to `TensorInfo.shape`, which means :
                    let int tuple `(start,end)` and `dim_size` be the i-th element of MetadataTensorSlice.placements
                    and `TensorInfo.shape`, respectively. Then, must be (end-start) == dim_size.
        """

        metadata_ts_tensor_info_pair: Dict[
            NameAfterMakeFx, Tuple[MetadataTensorSlice, Union[TensorInfo, ParamInfo]]
        ] = dict()
        # validate check item a.
        for attr in ["inputs", "outputs"]:
            for ts_name in getattr(self.tensor_slices, attr).keys():
                try:
                    corr_tensor_info = tensors[ts_name]
                    # it is guaranteed that getattr(self.tensor_slices,attr)[ts_name] exist
                    metadata_ts_tensor_info_pair[ts_name] = (
                        getattr(self.tensor_slices, attr)[ts_name],
                        corr_tensor_info,
                    )
                except KeyError:
                    # KeyError for corr_tensor_info = tensors[ts_name]
                    raise ValueError(
                        f"Tensor slice {ts_name} is not defined in Pipeline.tensors : {tensors}"
                    )

        def is_corresponding_tensor_info(
            metadata_ts: MetadataTensorSlice, tensor_info: Union[TensorInfo, ParamInfo]
        ) -> bool:
            if isinstance(tensor_info, ParamInfo):
                return False
            return (
                metadata_ts.dtype == tensor_info.dtype
                and len(metadata_ts.placements) == len(tensor_info.shape)
                and all(
                    place[1] - place[0] == dim_size
                    for place, dim_size in zip(metadata_ts.placements, tensor_info.shape)
                )
            )

        # validate check item b.
        tensor_slices_with_no_matched_tensor_info = [
            ts_name
            for ts_name, (metadata_ts, tensor_info) in metadata_ts_tensor_info_pair.items()
            if not is_corresponding_tensor_info(metadata_ts, tensor_info)
        ]
        if tensor_slices_with_no_matched_tensor_info:
            raise (
                ValueError(
                    f"There is no matching `TensorInfo` "
                    f"for tensor slices {tensor_slices_with_no_matched_tensor_info}"
                    "in `metadata.tensor_slices`."
                )
            )


class SuperTaskId(str): ...


class SerializationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, PosixPath):
            return str(obj.absolute())
        return super().default(obj)


def _dict_to_dataclass(cls, data):
    if isinstance(cls, str):
        assert isinstance(data, str)
        return cls(data)
    elif typing.get_origin(cls) == typing.Union and type(None) in typing.get_args(cls):
        if data is None:
            return None
        ty_args = typing.get_args(cls)
        assert len(ty_args) == 2
        return _dict_to_dataclass(ty_args[0], data)
    elif dataclasses.is_dataclass(cls):
        cls_fields = fields(cls)
        if len(cls_fields) < len(data):
            raise Exception(
                f"Number of data may not exceed the number of fields in the dataclass {cls}"
            )
        assert type(data) is dict
        cls_fields_name = set(field.name for field in cls_fields)
        if data.keys() - cls_fields_name:
            raise Exception(
                f"The provided data {data.keys()} contains a field "
                f"not present in the fields of {cls} which are {cls_fields_name}"
            )
        data_in_obj = dict()
        type_hints = typing.get_type_hints(cls)
        for f in dataclasses.fields(cls):
            name = f.name
            data_in_obj[name] = _dict_to_dataclass(type_hints[name], data[name])
        obj = cls(**(data_in_obj))
        return obj
    elif isinstance(data, list):
        origin_cls = typing.get_origin(cls)

        if origin_cls in (list, tuple):
            if len(data) == 0:
                return origin_cls(data)
            d_type = typing.get_args(cls)[0]
            return origin_cls(_dict_to_dataclass(d_type, d) for d in data)
        else:
            assert origin_cls is None
            if cls == Placements:
                data = [tuple(d) for d in data]
            return cls(data)
    elif len(typing.get_args(cls)) == 0:
        assert not isinstance(data, dict)
        return cls(data)
    elif typing.get_origin(cls) == typing.Union:
        if cls == CommMetaVal:
            # NOTE: to prevent union subtype reordering when calling typing.get_args.
            cls = CommMetaVal
        d_types = typing.get_args(cls)
        for d_type in d_types:
            try:
                return _dict_to_dataclass(d_type, data)
            except Exception:
                pass
        raise SerializationError(f"Cannot deserialize {data} to {cls}")
    elif isinstance(data, dict):
        k_type, v_type = typing.get_args(cls)
        return {
            _dict_to_dataclass(k_type, k): _dict_to_dataclass(v_type, v) for k, v in data.items()
        }
    return data


# n-dimensional array whose all leaf elements are ``DeviceId``s.
@dataclass
class TopologyDeviceConstraint(List): ...


@dataclass
class DeviceConstraint:
    kind: str
    devices: TopologyDeviceConstraint


def load_partial_param(
    param_file_path: Union[os.PathLike, str],
    tensor_name: str,
    placements: Placements,
    format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
    *,
    cache: Dict[Any, Any],
    device: str = "cpu",
) -> torch.Tensor:
    if format == format.__class__.SAFETENSORS:
        try:
            f = cache[param_file_path, device]
        except KeyError:
            f = cache[param_file_path, device] = safe_open(
                param_file_path, framework="pt", device=device
            )
        # If tensor is a shared tensor and not stored, get stored one.
        if metadata := f.metadata():
            tensor_name = metadata.get(tensor_name, tensor_name)
        if not placements:
            # if tensor is scalar value with 0 dim.
            tensor = f.get_tensor(tensor_name)
            if tensor.dim() > 0:
                raise ValueError(
                    f"tensor {tensor_name} is not scalar even if its placements is empty"
                )
            return tensor
        tensor_slice = f.get_slice(tensor_name)
        return tensor_slice[[slice(*p) for p in placements]]
    else:
        raise NotImplementedError(f"param save format {format} is not supported yet")


@dataclass
class Pipeline:
    name: str
    devices: Dict[DeviceId, Device]
    tensors: Dict[NameAfterMakeFx, Union[TensorInfo, ParamInfo]]
    supertasks: Dict[SuperTaskId, Union[InOutputSuperTask, CompSuperTask, CommSuperTask]]
    metadata: MetaData
    blobs: Dict[DataBlobId, str]
    param_files: Dict[ParamFileId, ParamFileInfo]
    device_constraints: List[DeviceConstraint]
    version: str = SCHEMA_VERSION

    skip_validation: InitVar[bool] = False
    skip_dead_supertask_check: InitVar[bool] = False
    # FIXME : Following `skip_param_file_eq_check` needs to be set False by default,
    # later after some modification in PipelineBuilder
    skip_param_file_eq_check: InitVar[bool] = True
    skip_inter_supertask_operand_check: InitVar[bool] = False

    def __post_init__(
        self,
        skip_validation: bool,
        skip_dead_supertask_check: bool,
        skip_param_file_eq_check: bool,
        skip_inter_supertask_operand_check: bool,
    ):
        if skip_validation:
            return

        self.validate(
            skip_dead_supertask_check,
            skip_param_file_eq_check,
            skip_inter_supertask_operand_check,
        )

    @cached_property
    def input_supertask(self) -> InOutputSuperTask:
        input_supertask = next(spt for spt in self.supertasks.values() if spt.is_input())
        assert isinstance(input_supertask, InOutputSuperTask)
        return input_supertask

    @cached_property
    def output_supertask(self) -> InOutputSuperTask:
        output_supertask = next(spt for spt in self.supertasks.values() if spt.is_output())
        assert isinstance(output_supertask, InOutputSuperTask)
        return output_supertask

    def validate(
        self,
        skip_dead_supertask_check: bool = False,
        skip_param_file_eq_check: bool = False,
        skip_inter_supertask_operand_check: bool = False,
    ):

        # check .tensors and .metadata
        self.validate_tensors_attributes(skip_param_file_eq_check)
        self.metadata.validate(self.tensors, self.devices, self.supertasks)
        # check .supertasks
        self.validate_tensor_classification(skip_inter_supertask_operand_check)
        self.validate_complete_devices()
        self.validate_inoutput_supertasks()
        self.validate_supertask_dataflow(skip_dead_supertask_check)
        self.validate_comm_supertasks()

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), cls=EnumEncoder, indent=4, allow_nan=False)

    @classmethod
    def from_dict(cls, val: Dict[str, Any]) -> "Pipeline":
        return _dict_to_dataclass(cls, val)

    def export(self, path: Union[str, os.PathLike]):
        with open(path, "w+") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, path: Union[str, os.PathLike]):
        with open(path) as f:
            pipeline_dict = json.load(f)
            return cls.from_dict(pipeline_dict)

    def get_blob_kind(self) -> Dict[DataBlobId, SuperTaskKind]:
        return {
            task.data_blob: task.kind
            for _, task in self.supertasks.items()
            if isinstance(task, CompSuperTask) and task.data_blob
        }

    # FIXME: This method is highly coupled to MLPerf context.
    def get_block_type_from_supertask_id(self, task_id: SuperTaskId) -> BlockType:
        supertask = self.supertasks[task_id]
        if not isinstance(supertask, CompSuperTask):
            raise ValueError("Only comp supertasks have block type info.")

        comp_supertasks = [
            spt for spt in self.supertasks.values() if isinstance(spt, CompSuperTask)
        ]
        if len(comp_supertasks) == 1:
            # Blockwise compile has not been used.
            return BlockType.WHOLE

        # Assume blockwise compile is used.
        comp_supertask_ids_in_order = [
            sid
            for sid, supertask in self.get_supertasks_in_topo_order()
            if isinstance(supertask, CompSuperTask)
        ]

        if task_id == comp_supertask_ids_in_order[0]:
            return BlockType.FIRST
        elif task_id == comp_supertask_ids_in_order[-1]:
            return BlockType.LAST
        else:
            return BlockType.MID

    def shallow_copy_with_replaced_devices(self, old_to_new: Dict[Device, Device]) -> "Pipeline":
        if set(old_to_new.keys()) != set(self.devices.values()):
            raise ValueError("`old_to_new` should have mappings for all original devices")

        new_devices = {dev_id: old_to_new[old_dev] for dev_id, old_dev in self.devices.items()}

        copied = copy.copy(self)
        copied.devices = new_devices
        return copied

    def shallow_copy_with_new_devices_and_supertasks(
        self,
        devices: Dict[DeviceId, Device],
        supertasks: Dict[SuperTaskId, Union[InOutputSuperTask, CompSuperTask, CommSuperTask]],
    ) -> "Pipeline":
        copied = copy.copy(self)
        copied.devices = devices
        copied.supertasks = supertasks
        return copied

    def shallow_copy_with_replaced_tensors(
        self, tensors: Dict[NameAfterMakeFx, Union[TensorInfo, ParamInfo]]
    ) -> "Pipeline":
        copied = copy.copy(self)
        copied.tensors = tensors
        return copied

    def shallow_copy_with_replaced_metadata(self, metadata: MetaData) -> "Pipeline":
        copied = copy.copy(self)
        copied.metadata = metadata
        return copied

    def eq_except_for_param_files(self, other: "Pipeline") -> bool:
        other_shallow_copy = copy.copy(other)
        other_shallow_copy.param_files = self.param_files
        return other_shallow_copy == self

    def get_gms(
        self,
        get_input_constants: bool = False,
        skip_preprocess: bool = False,
    ) -> Union[
        Tuple[GraphModule, ...], Tuple[Tuple[GraphModule, Tuple[Optional[torch.Tensor], ...]], ...]
    ]:
        """Get sub GraphModules in the pipeline."""

        ret: List = []
        gm_cache: Dict[Optional[DataBlobId], GraphModule] = {}

        # Sort supertasks by id to guarantee consistent order.
        sorted_supertasks = (
            supertask for _, supertask in sorted(self.supertasks.items(), key=lambda x: int(x[0]))
        )

        for supertask in sorted_supertasks:
            if not isinstance(supertask, CompSuperTask):
                continue

            if supertask.kind != SuperTaskKind.FX:
                raise ValueError("Supertask is not FX graph supertask.")

            param_load_cache: Dict[Any, Any] = {}

            fake_mode = FakeTensorMode(allow_non_fake_inputs=True)

            with fake_mode:
                fake_example_inputs = tuple(
                    torch.zeros(
                        self.tensors[input_].shape,
                        dtype=self.tensors[input_].dtype.to_torch_dtype(),
                    )
                    for input_ in supertask.inputs
                )

            gm = gm_cache.get(supertask.data_blob, None)
            if gm is None:
                if supertask.data is not None:
                    data = supertask.data
                else:
                    assert supertask.data_blob is not None
                    data = self.blobs[supertask.data_blob]

                gm = deserialize_gm(data)
                # NOTE: This Shape propagation is required because tensor meta information is lost during serialization. We need to regenerate this.
                ShapeProp(gm).propagate(*fake_example_inputs)
                # preprocess gms for it to be compiled immediately
                if not skip_preprocess:
                    processed = preprocess(gm, fake_example_inputs)
                    # Copy metadata for placeholder nodes.
                    for ph1, ph2 in zip_equal(
                        processed.graph.find_nodes(op="placeholder"),
                        gm.graph.find_nodes(op="placeholder"),
                    ):
                        ph1.meta.update(ph2.meta)
                    gm = processed

                if supertask.data_blob is not None:
                    gm_cache[supertask.data_blob] = cast(GraphModule, gm)

            if get_input_constants:
                # TODO: change this to share same tensor among slices.
                def load_tensor(tensor_name) -> Optional[torch.Tensor]:
                    tensor_info = self.tensors[tensor_name]
                    if isinstance(tensor_info, TensorInfo):
                        # If it's not an input constant tensor (i.e., input tensor not originated from constant tensor),
                        # just return None.
                        return None
                    else:
                        assert isinstance(tensor_info, ParamInfo)
                        param_value = tensor_info.value
                        param_file_info = self.param_files[param_value.param_file]

                        return load_partial_param(
                            param_file_info.path,
                            param_value.name,
                            param_value.placements,
                            param_file_info.format,
                            cache=param_load_cache,
                        ).contiguous()

                example_input = tuple(load_tensor(input_name) for input_name in supertask.inputs)
                ret.append((gm, example_input))
            else:
                ret.append(gm)

        return tuple(ret)

    def get_supertasks_in_topo_order(
        self,
    ) -> List[Tuple[SuperTaskId, SuperTask]]:
        """
        Returns an ordered sequence of Supertasks in execution order using a topological-sort style algorithm.
        Note that input supertask and output supertask always come first and last respectively.
        Dependencies between two supertasks are determined by matching output and input args between them.
        """

        ret: List[Tuple[SuperTaskId, SuperTask]] = []
        to_visit: Deque[Tuple[SuperTaskId, SuperTask]] = deque(
            (sid, supertask) for sid, supertask in self.supertasks.items() if supertask.is_input()
        )
        sid_to_supertask: Dict[SuperTaskId, SuperTask] = {
            sid: supertask for sid, supertask in self.supertasks.items()
        }
        tensor_to_consumers: DefaultDict[NameAfterMakeFx, List[SuperTaskId]] = defaultdict(list)

        group_to_recv_task_id: Dict[str, SuperTaskId] = {}
        remaining_pred_comm_cnt_per_spt: typing.Counter[SuperTaskId] = Counter({})

        for sid, supertask in self.supertasks.items():
            if supertask.kind != SuperTaskKind.RECV:
                continue
            assert isinstance(supertask, CommSuperTask) and supertask.group
            group_to_recv_task_id[supertask.group] = sid
            remaining_pred_comm_cnt_per_spt[sid] = 1

        def get_non_constant_inputs(supertask: SuperTask) -> List[NameAfterMakeFx]:
            return [
                input_
                for input_ in supertask.inputs
                if not isinstance(self.tensors[input_], ParamInfo)
            ]

        remaining_input_tensor_cnt_per_spt = Counter(
            {
                sid: len(get_non_constant_inputs(supertask))
                for sid, supertask in self.supertasks.items()
            }
        )
        remaining_dep_cnt_per_spt = (
            remaining_input_tensor_cnt_per_spt + remaining_pred_comm_cnt_per_spt
        )

        def is_ready(sid: SuperTaskId) -> bool:
            return remaining_dep_cnt_per_spt[sid] == 0

        for sid, supertask in self.supertasks.items():
            non_constant_inputs = get_non_constant_inputs(supertask)

            for input_tensor in non_constant_inputs:
                tensor_to_consumers[input_tensor].append(sid)

            if isinstance(supertask, InOutputSuperTask):
                # Input supertask has already been added.
                # Output supertask should come last, so will be handled specially.
                continue

            if is_ready(sid):
                to_visit.append((sid, supertask))

        while to_visit:
            sid, supertask = to_visit.popleft()  # type: ignore [assignment]

            # We don't visit output supertask to force it to come last.
            if supertask.is_output():
                continue

            ret.append((sid, supertask))

            candidates = set()

            if supertask.kind is SuperTaskKind.SEND:
                assert isinstance(supertask, CommSuperTask) and supertask.group
                recv_task_id = group_to_recv_task_id[supertask.group]
                remaining_dep_cnt_per_spt[recv_task_id] -= 1
                candidates.add(recv_task_id)

            for output_tensor in supertask.outputs:
                for consumer in tensor_to_consumers.pop(output_tensor, ()):
                    remaining_dep_cnt_per_spt[consumer] -= 1
                    assert remaining_dep_cnt_per_spt[consumer] >= 0
                    candidates.add(consumer)

            for cand_id in candidates:
                if is_ready(cand_id):
                    to_visit.append((cand_id, sid_to_supertask[cand_id]))

        output_sid_with_spt = next(
            sid_with_spt for sid_with_spt in self.supertasks.items() if sid_with_spt[1].is_output()
        )

        # All output tensors should be ready.
        assert remaining_dep_cnt_per_spt[output_sid_with_spt[0]] == 0

        ret.append(output_sid_with_spt)

        assert len(ret) == len(sid_to_supertask)

        return ret

    def validate_tensors_attributes(self, skip_param_file_eq_check: bool = False) -> None:
        """Validates Pipeline.tensors
        Specifically, following properties of `Pipeline.tensors` will be checked :
            a. Collection of tensor names in each supertasks's in/outputs must be equal to `Pipeline.tensors.keys()`
            b. Check parameter files :
                - Collection of `ParamInfo.value.param_file` from `Pipeline.tensors`
                    must subset of `Pipeline.param_files.keys()`.
                - [Optional] and more strictly, they should be equal
                    - this check will be skipped if `skip_param_file_eq_check=True`
        """
        tensors_from_spt = set(
            itertools.chain.from_iterable(
                spt.inputs + spt.outputs for spt in self.supertasks.values()
            )
        )
        # validate check item a.
        if tensors_from_spt != set(self.tensors.keys()):
            raise (
                ValueError(
                    "The collection of input and output tensors from supertasks must be "
                    "equal to key collections from `Pipeline.tensors`, "
                    f"but we got {tensors_from_spt} and {set(self.tensors.keys())}, respectively."
                )
            )

        param_files_from_tensors: Set[ParamFileId] = set(
            info.value.param_file for info in self.tensors.values() if isinstance(info, ParamInfo)
        )
        param_files_from_pipeline = set(self.param_files.keys())
        # validate check item b.
        if not (param_files_from_tensors <= param_files_from_pipeline):
            raise ValueError(
                "Parameter file from each tensor in `Pipeline.tensors` must be "
                "one of parameter files defined in the `Pipeline`."
            )
        if (not skip_param_file_eq_check) and param_files_from_tensors != param_files_from_pipeline:
            raise (
                ValueError(
                    "The collection of parameter files in `Pipeline.tensors` must be equal to `Pipeline.param_files`, "
                    f"but got {param_files_from_tensors} and {param_files_from_pipeline}, respectively."
                )
            )

    def validate_complete_devices(self) -> None:
        """Validates if device set from `Pipeline.devices` is equal to set of devices from `Pipeline.supertasks`."""
        device_set_from_spt = set(
            spt.device for spt in self.supertasks.values() if isinstance(spt, SuperTaskWithDevice)
        )
        device_set_from_pipeline = set(self.devices.keys())
        if device_set_from_pipeline != device_set_from_spt:
            raise ValueError(
                f"Set of devices occupied by Supertasks {device_set_from_spt} must be "
                f"equal to devices defined in the `Pipeline` {device_set_from_pipeline}."
            )

    def validate_inoutput_supertasks(self) -> None:
        """Validates whether the pipeline contains exactly one Input and one Output supertask each
        and if `.inputs` of Input supertask and `outputs` Output supertask are empty."""
        inoutput_spt = dict()
        inoutput_spt["input"] = [spt for spt in self.supertasks.values() if spt.is_input()]
        inoutput_spt["output"] = [spt for spt in self.supertasks.values() if spt.is_output()]

        for spt_type in ["input", "output"]:
            if len(inoutput_spt[spt_type]) != 1:
                raise ValueError(
                    f"There must be only one {spt_type.capitalize()} supertask. "
                    f"However we got {inoutput_spt[spt_type]}."
                )
            targ_spt = inoutput_spt[spt_type].pop()

            if getattr(targ_spt, spt_type + "s"):
                raise ValueError(
                    f" `.{spt_type}s` of {spt_type.capitalize()} supertask must be empty."
                )

    def validate_tensor_classification(
        self, skip_inter_supertask_operand_check: bool = False
    ) -> None:
        """Validates each tensors in `Pipeline.tensors.keys()` to be one of following type :
        - constant tensor/parameter : the corresponding value in `Pipeline.tensors` is of type `ParamInfo`
        - pipeline input : the corresponding value in `Pipeline.tensors` is of type `TensorInfo`
            and exist in `.outputs` field of Input Supertask (which must uniquely exist in the `Pipeline`)
        - pipeline output : the corresponding value in `Pipeline.tensors` is of type `TensorInfo`
            and exist in `.inputs` field of Output Supertask (which must uniquely exist in the `Pipeline`)
        - inter-supertask args : the corresponding value in `Pipeline.tensors` is of type `TensorInfo`
            and satisfies followings :
            * there exist unique supertasks whose `.outputs` includes the given tensor
            * [Optional] (if the tensor is not the output of CommSuperTask `RECV`) there exist a supertasks whose
                `.inputs` includes the tensor
                - this check will be skipped if `skip_inter_supertask_operand_check=True`
        """
        # assume in/output supertask exist uniquely, which will be checked by `validate_inoutput_supertasks`.
        input_supertask = next(spt for spt in self.supertasks.values() if spt.is_input())
        output_supertask = next(spt for spt in self.supertasks.values() if spt.is_output())

        input_spt_outputs = set(input_supertask.outputs)
        output_spt_inputs = set(output_supertask.inputs)

        def is_constant_tensor_or_param(tensor_name) -> bool:
            return isinstance(self.tensors[tensor_name], ParamInfo)

        def is_pipeline_input(tensor_name: NameAfterMakeFx) -> bool:
            return (
                isinstance(self.tensors[tensor_name], TensorInfo)
                and tensor_name in input_spt_outputs
            )

        def is_pipeline_output(tensor_name: NameAfterMakeFx) -> bool:
            return (
                isinstance(self.tensors[tensor_name], TensorInfo)
                and tensor_name in output_spt_inputs
            )

        def is_intersupertask_arg(tensor_name: NameAfterMakeFx) -> bool:
            is_input_of_some_spt = (
                skip_inter_supertask_operand_check or self.tensor_consumer_supertasks[tensor_name]
            )
            is_output_of_some_spt = self.tensor_producer_supertasks[tensor_name]

            return bool(is_input_of_some_spt and is_output_of_some_spt)

        tensor_classifiers = [
            is_constant_tensor_or_param,
            is_pipeline_input,
            is_pipeline_output,
            is_intersupertask_arg,
        ]
        tensor_type_name = [
            "constant",
            "pipeline input",
            "pipeline output",
            "inter-supertask arg",
        ]

        for tensor_name in self.tensors:
            check_results = [condition(tensor_name) for condition in tensor_classifiers]
            if not any(check_results):
                raise ValueError(
                    f"Invalid tensor {tensor_name} : the tensor satisfies none of conditions "
                    "for being constant, pipeline in/output, and intersupertask args. "
                    "See `help(furiosa_llm.parallelize.pipeline.types.validate_tensor_attributes)` "
                    "for definition of each class."
                )
            elif sum(check_results) != 1:
                raise ValueError(
                    f"Invalid tensor {tensor_name} in : the tensor needs to be "
                    "only one of constant, pipeline in/output, and intersupertask args. "
                    f"However, it satisfied conditions "
                    f"{[tensor_type_name[idx] for idx, res in enumerate(check_results) if res]}. "
                    "See `help(furiosa_llm.parallelize.pipeline.types.validate_tensor_attributes)` "
                    "for the details of each class."
                )

    def validate_supertask_dataflow(self, skip_dead_supertask_check: bool = False) -> None:
        """Validates data flow relations between supertasks within the `Pipeline`.
        The dataflow relation is defined as follows :

        for two different supertask S, S', a data flow relation `~>` is as `S ~> S' if outputs of S overlaps with S'.

        Under the defined data flow relation, following items are checked :
            a. For two supertask S, S' with `S~>S`, if the two $S,S'$ are not `InoutputSupertask`,
                then the S,S' must be loaded in same device (i.e, field value `.device` must be the same).
            b. [Optional] Collection of supertasks S, S' such that S ~> S
                must be equal to collection of all supertasks within the `Pipeline` (i.e, no dead supertasks).
                - this check will be skipped if `skip_dead_supertask_check=True`
        """
        spts_from_rel: Set[SuperTaskId] = set()
        for tensor in self.tensors:
            consumer = self.tensor_consumer_supertasks[tensor]
            producer = self.tensor_producer_supertasks[tensor]
            if len({self.supertasks[spt_id].device for spt_id in (consumer | producer)}) > 1:  # type: ignore[union-attr]
                raise ValueError(
                    f"For tensor {tensor}, its consumer supertasks {consumer} "
                    f"and producing supertask {producer} must be loaded in same device"
                )

            if consumer & producer:
                raise ValueError(
                    f"Tensor {tensor} is a cycle by "
                    f"consumer supertasks(id) {consumer} and producer supertasks(id) {producer}"
                )

            if (not skip_dead_supertask_check) and consumer and producer:
                spts_from_rel.update(consumer | producer)

        # validate check item b.
        if not skip_dead_supertask_check:
            spts_from_pipeline = {
                spt_id
                for spt_id, spt in self.supertasks.items()
                if isinstance(spt, SuperTaskWithDevice)
            }
            # if len(spts_from_pipeline) == 1, then only one Comp or Comm Supertask Exist,
            # which is always free from the dead-supertask condition
            if spts_from_pipeline != spts_from_rel and len(spts_from_pipeline) != 1:
                raise ValueError(
                    f"Following supertasks are never related by other supertasks in data-flow "
                    f"(i.e, they are dead supertasks): {spts_from_pipeline-spts_from_rel}."
                )

    def validate_comm_supertasks(self) -> None:
        """Validates if the comm supertasks are well related with other comm supertasks within the `Pipeline`.
        For each CommSuperTask S, let G be the collection of CommSuperTasks of specific group.
        If G_S is of type..
        - `SEND`, `RECV` pair :
            * `.outputs` of the SEND must be empty and `.inputs` of the RECV must be empty
            * `SEND` and `RECV` must have different device field
            * number of tensors in `.inputs` of the `SEND` and `.outputs` of the `RECV` must be 1
            * and the each tensor of each `SEND` and `RECV` must be same in shape and dtype
        - For other types, it is yet to be implemented.
        """

        supertasks_by_group: Dict[str, List[SuperTaskId]] = defaultdict(list)
        for id, supertask in self.supertasks.items():
            if isinstance(supertask, CommSuperTask):
                assert supertask.group
                supertasks_by_group[supertask.group].append(id)

        for group_id, grouped_supertasks in supertasks_by_group.items():
            if {self.supertasks[spt].kind for spt in grouped_supertasks} == {
                SuperTaskKind.SEND,
                SuperTaskKind.RECV,
            } and len(grouped_supertasks) == 2:
                send_spt, recv_spt = [
                    self.supertasks[spt_id]
                    for spt_id in (
                        grouped_supertasks
                        if self.supertasks[grouped_supertasks[0]].kind is SuperTaskKind.SEND
                        else reversed(grouped_supertasks)
                    )
                ]

                assert isinstance(send_spt, CommSuperTask)
                assert isinstance(recv_spt, CommSuperTask)

                if send_spt.device == recv_spt.device:
                    raise ValueError(
                        f"{send_spt} and {recv_spt} must be loaded on different devices "
                        f"but were both loaded on {send_spt.device}."
                    )
                if not (len(send_spt.inputs) == len(recv_spt.outputs) == 1):
                    raise ValueError(
                        f"Number of `SEND` inputs and `RECV` outputs  must be exactly one, "
                        f"but got {send_spt.inputs} and {recv_spt.outputs}."
                    )

                if not (
                    self.tensors[send_spt.inputs[0]].shape
                    == self.tensors[recv_spt.outputs[0]].shape
                    and self.tensors[send_spt.inputs[0]].dtype
                    == self.tensors[recv_spt.outputs[0]].dtype
                ):
                    raise ValueError(
                        "Tensors in `SEND` and `RECV` must have same shape and dtype, "
                        f"however got { self.tensors[send_spt.inputs[0]] } "
                        f"and {self.tensors[recv_spt.outputs[0]]} respectively."
                    )

            else:
                raise ValueError(
                    f"Invalid CommSuperTask group : {grouped_supertasks} of id {group_id}"
                )

    @cached_property
    def tensor_consumer_supertasks(self) -> DefaultDict[NameAfterMakeFx, Set[SuperTaskId]]:
        tensor_consumer_spt_dict: DefaultDict[NameAfterMakeFx, Set[SuperTaskId]] = defaultdict(set)
        for spt_id, spt in self.supertasks.items():
            if not isinstance(spt, SuperTaskWithDevice):
                continue
            for tensor in spt.inputs:
                if isinstance(self.tensors[tensor], TensorInfo):
                    tensor_consumer_spt_dict[tensor].add(spt_id)
        return tensor_consumer_spt_dict

    @cached_property
    def tensor_producer_supertasks(self) -> DefaultDict[NameAfterMakeFx, Set[SuperTaskId]]:
        tensor_producer_spt_dict: DefaultDict[NameAfterMakeFx, Set[SuperTaskId]] = defaultdict(set)
        for spt_id, spt in self.supertasks.items():
            if not isinstance(spt, SuperTaskWithDevice):
                continue
            for tensor in spt.outputs:
                tensor_producer_spt_dict[tensor].add(spt_id)
        return tensor_producer_spt_dict
