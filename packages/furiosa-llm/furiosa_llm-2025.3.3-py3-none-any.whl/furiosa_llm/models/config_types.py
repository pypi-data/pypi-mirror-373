import abc
from enum import Enum
import json
import os
import typing
from typing import List, Literal, NamedTuple, Optional, Tuple, Union

from pydantic import BaseModel, RootModel
from pydantic.dataclasses import dataclass

if typing.TYPE_CHECKING:
    from furiosa_llm.parallelize.pipeline.types import Pipeline


class LLMBackend(Enum):
    """The backend implementation to run forward() of a model for the LLM."""

    # FIXME: In order to increase the code consistency, use the capital letter for the enum value
    TORCH_PIPELINE_RUNNER = "torch_pipeline_runner"
    FURIOSA_RT_NPU = "furiosa_rt_npu"
    FURIOSA_RT_V2 = "furiosa_rt_v2"
    MOCK_BACKEND_V2 = "mock_backend_v2"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            return cls[value.upper()]


@dataclass
class SchedulerConfig:
    """
    * version: Version of the `SchedulerConfig`.
    * scheduler_kind: Select named scheduler implementation with specialized strategy when provided.
                      Use default scheduler when omitted, which handles generic cases well.
    * npu_queue_limit: Maximum number of tasks that can be queued in the hardware
    * max_processing_samples: Maximum number of samples that can be processed by the scheduler
    * spare_blocks_ratio: Ratio of spare blocks that are reserved by scheduler. Smaller value will force the scheduler to use dram aggressively
    * is_offline: If True, use strategies optimized for offline scenario
    * prefill_chunk_size: Chunk size used for chunked prefill. If the value is `None`, chunked prefill is not used.
    * estimation_time_limit_ms: Amount of time scheduler will use to make scheduling decision.
    * enable_prefix_caching: If True, enable prefix caching in the scheduler (default: False). Prefix caching can improve performance by reusing prefix tokens in decoding.
    """

    scheduler_kind: Optional[str] = None
    npu_queue_limit: int = 2
    max_processing_samples: int = 65536
    spare_blocks_ratio: float = 0.0
    # TODO: migrate to `scheduler_kind='offline'`
    is_offline: bool = False
    # TODO: move this field to GeneratorConfig.
    prefill_chunk_size: Optional[int] = None
    estimation_time_limit_ms: Optional[int] = None
    enable_prefix_caching: bool = False

    def __post_init__(self):
        if self.is_offline:
            self.scheduler_kind = "offline"

    # custom comparator to handle float comparison
    def __eq__(self, other):
        return (
            self.scheduler_kind == other.scheduler_kind
            and self.npu_queue_limit == other.npu_queue_limit
            and self.max_processing_samples == other.max_processing_samples
            and abs(self.spare_blocks_ratio - other.spare_blocks_ratio) < 1e-6
        )

    def export(self, path: Union[str, os.PathLike]):
        with open(path, "w") as f:
            f.write(RootModel[SchedulerConfig](self).model_dump_json(indent=4))

    @classmethod
    def load(cls, path: Union[str, os.PathLike]) -> "SchedulerConfig":
        with open(path) as f:
            o = json.load(f)
            return SchedulerConfig(**o)


class Bucket(BaseModel):
    batch_size: int  # batch size, batch size must be a multiple of 2 now.
    attention_size: int
    kv_cache_size: int

    @property
    def input_ids_size(self) -> int:
        return self.attention_size - self.kv_cache_size

    def __init__(self, batch_size: int, attention_size: int, kv_cache_size: int):
        super(Bucket, self).__init__(
            batch_size=batch_size, attention_size=attention_size, kv_cache_size=kv_cache_size
        )

    @classmethod
    def prefill(cls, batch_size: int, attention_size: int) -> "Bucket":
        return cls(batch_size, attention_size, 0)

    @classmethod
    def decode(cls, batch_size: int, attention_size: int) -> "Bucket":
        return cls(batch_size, attention_size, attention_size - 1)

    @property
    def is_prefill(self) -> bool:
        return self.kv_cache_size == 0

    @property
    def is_decode(self) -> bool:
        return self.kv_cache_size > 0

    def __hash__(self) -> int:
        return hash((str(self.__class__), self.batch_size, self.attention_size))


class BucketConfig(abc.ABC): ...


@dataclass
class ManualBucketConfig(BucketConfig):
    prefill_buckets: List[Tuple[int, int]]
    decode_buckets: Optional[List[Tuple[int, int]]] = None


@dataclass
class MinimalBucketConfig(BucketConfig):
    max_seq_len: int


class PagedAttentionConfig(BaseModel):
    """Paged attention configuration.

    Attributes:
        block_size (int): The maximum number of tokens that can be stored in a single paged attention block
        padding_block_idx (int|None): Padding block's index. This will be used for optimization.
    """

    block_size: int

    # Padding block's index. This will be used for optimization.
    padding_block_idx: Optional[int] = None

    def __init__(self, block_size: int, padding_block_idx: Optional[int] = None):
        assert block_size > 0
        super(PagedAttentionConfig, self).__init__(
            block_size=block_size, padding_block_idx=padding_block_idx
        )


class KvCacheSharingAcrossBeamsConfig(BaseModel):
    beam_width: int
    max_new_tokens: int

    def __init__(self, beam_width: int, max_new_tokens: int):
        assert beam_width > 0
        assert max_new_tokens > 0
        super(KvCacheSharingAcrossBeamsConfig, self).__init__(
            beam_width=beam_width, max_new_tokens=max_new_tokens
        )


@dataclass
class GeneratorConfig:
    position_id_pad: int
    buckets: List[Bucket]
    model_qname: str  # qualified name of the model (module + class)
    paged_attention_config: Optional[PagedAttentionConfig]
    packing_type: Literal["IDENTITY"]
    kv_cache_sharing_across_beams_config: Optional[KvCacheSharingAcrossBeamsConfig]
    num_speculative_tokens: Optional[int]
    unpadded_vocab_size: Optional[int]

    def export(self, path: Union[str, os.PathLike]):
        with open(path, "w") as f:
            f.write(RootModel[GeneratorConfig](self).model_dump_json(indent=4))

    @classmethod
    def load(cls, path: Union[str, os.PathLike]) -> "GeneratorConfig":
        with open(path) as f:
            o = json.load(f)
            return GeneratorConfig(**o)


class ModelRewritingConfig(BaseModel):
    do_decompositions_for_model_rewrite: bool
    use_blockwise_compile: bool
    embedding_layer_as_single_block: bool
    embed_all_constants_into_graph: bool
    optimize_logit_shape: bool


class ParallelConfig(BaseModel):
    tensor_parallel_size: int
    pipeline_parallel_size: int


class PipelineMetadata(BaseModel, frozen=True):
    output_logits_size: Optional[int]
    num_blocks_per_supertask: Union[int, List[int]] = 1


class PipelineWithMetadata(NamedTuple):
    pipeline: "Pipeline"
    metadata: PipelineMetadata


@dataclass
class BucketWithOutputLogitsSize:
    bucket: Bucket
    output_logits_size: Optional[int] = None

    def __hash__(self):
        return hash((str(self.__class__), self.bucket, self.output_logits_size))
