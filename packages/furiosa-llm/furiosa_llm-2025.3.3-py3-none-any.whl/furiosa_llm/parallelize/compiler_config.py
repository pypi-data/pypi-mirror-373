import dataclasses
from dataclasses import dataclass
from enum import Enum
import functools
import logging
import os
import typing
from typing import Any, List, Mapping, Optional, Sequence, Tuple, TypeVar, Union

import furiosa_llm_models
from pydantic import BaseModel, model_serializer, model_validator
from typing_extensions import Self
import yaml

# For using some features without installing furiosa-native-compiler.
if typing.TYPE_CHECKING:
    from furiosa.native_compiler import LayerType

from furiosa_llm.models import ModelMetadata
from furiosa_llm.models.config_types import Bucket
from furiosa_llm.parallelize.utils import get_list_with_no_dup_with_order_preserved
from furiosa_llm.utils import get_logger_with_tz

logger = get_logger_with_tz(logging.getLogger(__name__))


class PipelineMode(Enum):
    UNKNOWN = "unknown"
    LLM_PREFILL = "prefill"
    LLM_DECODE = "decode"

    def __str__(self):
        return self.value

    @classmethod
    def _missing_(cls, value):
        if value is None:
            return cls.UNKNOWN


class BlockType(str, Enum):
    FIRST = "first"
    MID = "mid"
    LAST = "last"
    WHOLE = "all_merged"

    def __str__(self):
        return self.value


# FIXME: CompilerConfigContext must provide more generic way to match between target node and compiler config.
# the following implementation is MLPerf-specific (mostly targets gptj and bert) and should be fixed in the future.
@dataclass
class CompilerConfigContext:
    model_metadata: ModelMetadata
    num_pe_per_chip: Optional[int] = None
    num_chip: Optional[int] = None
    block_type: Optional[BlockType] = None
    num_blocks_per_graph: Union[int, Sequence[int]] = 1
    embedding_as_single_block: bool = False
    bucket: Optional[Bucket] = None
    phase: Optional[PipelineMode] = None
    beam_size: Optional[int] = None
    compiler_config_overrides: Optional[Mapping] = None
    enable_bf16_partial_sum_for_split: bool = False

    def load_config(self) -> Mapping:
        from furiosa.native_compiler import (
            LayerType,
            create_default_compiler_config,
            create_llm_compiler_config,
        )

        logger.info(f"Loading compiler config for {self}")
        config: Optional[Mapping] = None

        consisting_layers = self.get_consisting_layers()

        if self.bucket:
            num_chip = self.num_chip or 1
            num_pe = self.num_pe_per_chip or 8

            is_quantized = (
                not self.model_metadata.quantization_config.is_bf16
                if self.model_metadata.quantization_config
                else False
            )

            config_yaml = create_llm_compiler_config(
                self.model_metadata.pretrained_id,
                num_chip,
                num_pe,
                self.bucket.batch_size,
                self.bucket.attention_size,
                self.bucket.input_ids_size,
                consisting_layers,
                is_quantized,
                self.enable_bf16_partial_sum_for_split,
                # TODO: put True if valid length tensor is used.
                False,
            )
            logger.debug(f"Generated compiler config yaml: {config_yaml}")
            if config_yaml:
                config = yaml.safe_load(config_yaml)

        if config is None:
            logger.info("Failed to create compiler config; using default compiler config")
            config_yaml = create_default_compiler_config()
            config = yaml.safe_load(config_yaml)

        # TODO: move to compiler-config-generator
        config = {
            **config,
            "insert_wait_by_estimation": False,
            "profile_sync": False,
            "enable_tuc_profile": False,
        }

        # TODO: remove this when compiler config generater is updated to apply use_block_compile option.
        # Block compile config is used if graph consisting of multiple mid blocks in decode is compiled.
        if (
            consisting_layers
            and len(consisting_layers) == 1
            and consisting_layers[0][0] == LayerType.TRANSFORMER_BLOCK
            and consisting_layers[0][1] > 1
            and self.bucket
            and self.bucket.is_decode
            and self.bucket.input_ids_size == 1
            and self.model_metadata.get_optimized_cls()
            in (
                furiosa_llm_models.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
                furiosa_llm_models.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
            )
        ):
            logger.info(
                "Decode multi-mid-block compile detected. Add `use_block_compile` to compiler config."
            )
            config["use_block_compile"] = True

        if self.compiler_config_overrides is not None:
            config = {**config, **self.compiler_config_overrides}

        return config

    @functools.lru_cache
    def get_consisting_layers(self) -> Optional[List[Tuple["LayerType", int]]]:
        return generate_layers_from_compiler_config_context(
            self.model_metadata,
            self.num_blocks_per_graph,
            self.embedding_as_single_block,
            self.block_type,
        )

    def __hash__(self):
        return hash((getattr(self, field.name) for field in dataclasses.fields(self)))


class DramShapeKind(Enum):
    FREE = "Free"
    BROADCAST = "Broadcast"
    FIXED = "Fixed"


class AxisTagLabel(BaseModel):
    inner: str


class LabelStride(BaseModel):
    label: AxisTagLabel
    stride: int


# Type to represent field in `AxisTag` enum. Only needed types are defined now.
class AxisTagKind(Enum):
    LabelStride = "LabelStride"
    Broadcast = "Broadcast"


class AxisTag(BaseModel):
    kind: AxisTagKind
    label_stride: Optional[LabelStride] = None

    @model_serializer
    def serialize_model(self):
        # Workaround to make serialization result (yaml) same as counterpart in npu-tools.
        if self.kind is AxisTagKind.Broadcast:
            assert self.label_stride is None
            return "Broadcast"
        elif self.kind is AxisTagKind.LabelStride:
            assert self.label_stride
            return {"LabelStride": self.label_stride.model_dump()}
        else:
            raise ValueError(f"Unknown AxisTag kind: {self.kind}")

    @model_validator(mode="before")
    @classmethod
    def validate_model_before(cls, data: Any):
        if isinstance(data, dict) and "LabelStride" in data:
            data = {"kind": AxisTagKind.LabelStride, "label_stride": data["LabelStride"]}
        elif isinstance(data, str) and data == AxisTagKind.Broadcast.value:
            data = {"kind": AxisTagKind.Broadcast}
        return data

    @model_validator(mode="after")
    def validate_model_after(self) -> Self:
        if self.kind is AxisTagKind.Broadcast:
            if self.label_stride:
                raise ValueError("`label_stride` should not be set for Broadcast kind")
        elif self.kind is AxisTagKind.LabelStride:
            if not self.label_stride:
                raise ValueError("`label_stride` should be set for LabelStride kind")
        else:
            raise ValueError(f"Unknown AxisTag kind: {self.kind}")
        return self

    @classmethod
    def broadcast(cls) -> Self:
        return cls(kind=AxisTagKind.Broadcast)


class GenericAxisTagSize(BaseModel):
    tag: AxisTag
    size: int


class TaggedShape(BaseModel):
    inner: List[GenericAxisTagSize]


class AxisTagSizeStride(BaseModel):
    tag: AxisTag
    size: int
    stride: int


class StridedShape(BaseModel):
    axes: List[AxisTagSizeStride]
    offset: int = 0


class DramShapeGuide(BaseModel):
    kind: DramShapeKind
    inter_chip_axes: Optional[TaggedShape] = None
    intra_chip_axes: Optional[StridedShape] = None

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: Any):
        # Workaround to make serialization result (yaml) same as counterpart in npu-tools.
        if isinstance(data, str) and data in (e.value for e in DramShapeKind):
            return {"kind": DramShapeKind(data)}
        elif isinstance(data, dict) and DramShapeKind.FIXED.value in data:
            assert len(data) == 1
            kind = next(iter(data.keys()))
            return {"kind": kind, **data[kind]}
        else:
            return data

    @model_serializer
    def serialize_model(self):
        # For consistency with `DramShapeGuide` in npu-tools, which is an enum with fields.
        if self.kind is DramShapeKind.FIXED:
            assert self.inter_chip_axes and self.intra_chip_axes
            return {
                self.kind.value: {
                    "inter_chip_axes": self.inter_chip_axes.model_dump(),
                    "intra_chip_axes": self.intra_chip_axes.model_dump(),
                }
            }
        else:
            return self.kind.value

    @classmethod
    def free(cls) -> Self:
        return cls(kind=DramShapeKind.FREE)

    @classmethod
    def broadcast(cls) -> Self:
        return cls(kind=DramShapeKind.BROADCAST)


class SparseRatio(BaseModel):
    mean: float
    sigma: float
    sorted: bool


class ValidLengthInfo(BaseModel):
    target: int
    valid_length: int
    valid_length_axis: int
    sparse_key_axis: int
    sparse_ratio: SparseRatio


# NOTE: This is ported version of `GraphMetadata` in npu-tools.
# But only fields and types that are actually used are ported.
# Keep this same with one in npu-tools.
class GraphMetadata(BaseModel):
    valid_length: Optional[ValidLengthInfo]
    input_dram_shape_guide: List[DramShapeGuide]
    output_dram_shape_guide: List[DramShapeGuide]

    def to_yaml(self) -> str:
        return yaml.dump(self.model_dump(), sort_keys=False)

    def dump_yaml(self, path: Union[str, os.PathLike]) -> None:
        with open(path, "w") as f:
            f.write(self.to_yaml())

    @classmethod
    def from_yaml(cls, data: str) -> Self:
        return cls.model_validate(yaml.safe_load(data))

    @classmethod
    def load_yaml(cls, path: Union[str, os.PathLike]) -> Self:
        with open(path, "r") as f:
            data = f.read()
        return cls.from_yaml(data)


T = TypeVar("T")


def group_consecutive_names(names: Sequence[T]) -> List[Tuple[T, int]]:
    """
    Group consecutive identical names and count their occurrences.

    Takes a sequence of names and returns a list of tuples where each tuple
    contains a unique name and the number of consecutive times it appears.

    Args:
        names: A sequence of string names to be grouped

    Returns:
        A list of tuples, each containing (name, consecutive_count)

    Example:
        >>> group_consecutive_names(['a', 'a', 'b', 'b', 'b', 'a'])
        [('a', 2), ('b', 3), ('a', 1)]
    """
    cur_name = None
    cur_cnt = 0

    if not names:
        return []

    grouped = []
    for name in names:
        if name == cur_name or cur_name is None:
            cur_cnt += 1
        else:
            grouped.append((cur_name, cur_cnt))
            cur_cnt = 1
        cur_name = name

    assert cur_name is not None
    grouped.append((cur_name, cur_cnt))

    return grouped


def generate_layers_from_compiler_config_context(
    model_metadata: ModelMetadata,
    num_blocks_per_graph: Union[int, Sequence[int]],
    embedding_as_single_block: bool,
    block_type: Optional[BlockType],
) -> Optional[List[Tuple["LayerType", int]]]:
    from furiosa.native_compiler import (
        LayerType,
    )

    total_num_layers = model_metadata.num_hidden_layers
    num_layers_per_graph = num_blocks_per_graph

    if block_type in (None, BlockType.WHOLE):
        return None

    if type(num_layers_per_graph) is int:
        if total_num_layers % num_layers_per_graph != 0:
            raise ValueError(
                f"Total number of layers ({total_num_layers}) is not divisible by num_blocks_per_graph ({num_layers_per_graph})."
            )

        # This assumes that embedding layer is not compiled as a single block.
        # TODO: add support for embedding layer as a single block case.
        if block_type is BlockType.FIRST:
            if embedding_as_single_block:
                layers = [
                    (LayerType.EMBEDDING, 1),
                ]
            else:
                layers = [
                    (LayerType.EMBEDDING, 1),
                    (LayerType.TRANSFORMER_BLOCK, num_layers_per_graph),
                ]
        elif block_type is BlockType.MID:
            layers = [(LayerType.TRANSFORMER_BLOCK, num_layers_per_graph)]
        elif block_type is BlockType.LAST:
            layers = [
                (LayerType.TRANSFORMER_BLOCK, num_layers_per_graph),
                (LayerType.OUTPUT_HEAD_AND_POST_PROCESS, 1),
            ]
        else:
            raise ValueError(f"Unknown block type: {block_type}")
    else:
        assert isinstance(num_layers_per_graph, Sequence)
        layers_per_block: List[Sequence[LayerType]] = []
        if total_num_layers == 1:
            total_layers: List[Tuple[LayerType, ...]] = [
                (
                    LayerType.EMBEDDING,
                    LayerType.TRANSFORMER_BLOCK,
                    LayerType.OUTPUT_HEAD_AND_POST_PROCESS,
                )
            ]
        else:
            first_layer = (
                (LayerType.EMBEDDING,)
                if embedding_as_single_block
                else (LayerType.EMBEDDING, LayerType.TRANSFORMER_BLOCK)
            )
            total_layers = [
                first_layer,
                *((LayerType.TRANSFORMER_BLOCK,) for _ in range(total_num_layers - 2)),
                (LayerType.TRANSFORMER_BLOCK, LayerType.OUTPUT_HEAD_AND_POST_PROCESS),
            ]

        cur_start = 0
        for num_layers in num_layers_per_graph:
            layers_per_block.append(sum(total_layers[cur_start : cur_start + num_layers], ()))
            cur_start += num_layers
        if cur_start != len(total_layers):
            raise ValueError(
                f"Total number of layers ({len(total_layers)}) is not equal to the sum of num_layers_per_graph ({sum(num_layers_per_graph)})."
            )
        layers_per_block = get_list_with_no_dup_with_order_preserved(layers_per_block)

        if len(layers_per_block) != 3:
            raise ValueError(f"There's more than 3 kind of blocks: {layers_per_block}.")

        layers_per_block_with_cnt = [group_consecutive_names(layers) for layers in layers_per_block]
        blocktype_to_idx = {
            BlockType.FIRST: 0,
            BlockType.MID: 1,
            BlockType.LAST: 2,
        }
        assert block_type
        layers = layers_per_block_with_cnt[blocktype_to_idx[block_type]]
    return layers
