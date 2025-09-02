from abc import ABC, abstractmethod
import copy
from dataclasses import dataclass
import functools
import operator
from typing import List, Optional, Sequence, Tuple

from pydantic import BaseModel
from typing_extensions import Self

from furiosa_llm.models.config_types import (
    Bucket,
    BucketConfig,
    BucketWithOutputLogitsSize,
    ManualBucketConfig,
    MinimalBucketConfig,
)


class ArtifactBase(BaseModel, ABC):
    """Abstract class for old version artifacts."""

    @classmethod
    @abstractmethod
    def from_previous_version(cls, previous_version_artifact) -> Self: ...


# NOTE: The following version identification is specific to `Artifact`.
# The version must be updated appropriately whenever any change,
# occurs in the format of `Artifact` or its related types.
# Version follows the format `X.Y` (where each X,Y represents major, minor versions)

# FIXME: A tentative policy is that each major version change should result in the creation
# of a new `ArtifactBase` class.


@functools.total_ordering
class SchemaVersion(BaseModel):
    major: int
    minor: int

    def __eq__(self, other):
        if not isinstance(other, SchemaVersion):
            return False
        return (self.major, self.minor) == (
            other.major,
            other.minor,
        )

    def __lt__(self, other):
        if not isinstance(other, SchemaVersion):
            return False
        return (self.major, self.minor) < (other.major, other.minor)


@dataclass
class ArtifacPipelineFilter:
    allowed_prefill_buckets: Optional[List[Tuple[int, int]]] = None
    allowed_decode_buckets: Optional[List[Tuple[int, int]]] = None
    max_prompt_len: Optional[int] = None
    max_seq_len: Optional[int] = None
    max_batch_size: Optional[int] = None
    min_batch_size: Optional[int] = None

    def apply_on_bucket_config(self, bucket_config: BucketConfig) -> BucketConfig:
        bucket_config = copy.deepcopy(bucket_config)
        if self.max_prompt_len is None and self.max_seq_len is not None:
            self.max_prompt_len = self.max_seq_len
        elif self.max_prompt_len is not None and self.max_seq_len is not None:
            self.max_prompt_len = min(self.max_prompt_len, self.max_seq_len)
        if isinstance(bucket_config, ManualBucketConfig):
            prefill_buckets = bucket_config.prefill_buckets
            if self.max_prompt_len is not None:
                prefill_buckets = [
                    (bs, sl) for bs, sl in prefill_buckets if sl <= self.max_prompt_len
                ]
            if self.allowed_prefill_buckets is not None:
                prefill_buckets = [
                    (bs, sl)
                    for bs, sl in prefill_buckets
                    if (bs, sl) in self.allowed_prefill_buckets
                ]
            if self.max_batch_size is not None:
                prefill_buckets = [
                    (bs, sl) for bs, sl in prefill_buckets if bs <= self.max_batch_size
                ]
            if self.min_batch_size is not None:
                prefill_buckets = [
                    (bs, sl) for bs, sl in prefill_buckets if bs >= self.min_batch_size
                ]
            bucket_config.prefill_buckets = prefill_buckets

            if bucket_config.decode_buckets is not None:
                decode_buckets = bucket_config.decode_buckets
                if self.max_seq_len is not None:
                    decode_buckets = [
                        (bs, sl) for bs, sl in decode_buckets if sl <= self.max_seq_len
                    ]
                if self.allowed_decode_buckets is not None:
                    decode_buckets = [
                        (bs, sl)
                        for bs, sl in decode_buckets
                        if (bs, sl) in self.allowed_decode_buckets
                    ]
                if self.max_batch_size is not None:
                    decode_buckets = [
                        (bs, sl) for bs, sl in decode_buckets if bs <= self.max_batch_size
                    ]
                if self.min_batch_size is not None:
                    decode_buckets = [
                        (bs, sl) for bs, sl in decode_buckets if bs >= self.min_batch_size
                    ]
                bucket_config.decode_buckets = decode_buckets

            return bucket_config

        elif isinstance(bucket_config, MinimalBucketConfig):
            if self.max_seq_len is not None:
                bucket_config.max_seq_len = min(bucket_config.max_seq_len, self.max_seq_len)
            return bucket_config

        raise ValueError("Unsupported bucket configuration type: {}".format(type(bucket_config)))

    def apply(
        self,
        buckets_with_output_logits_size: Sequence[BucketWithOutputLogitsSize],
        # TODO : having `bucket_config` as a input argument seems a bit odd and unnecessary,
        # resolve this argument later.
        bucket_config: ManualBucketConfig,
    ) -> List[BucketWithOutputLogitsSize]:
        # NOTE: Currently, pipeline selection for plain buckets (i.e., pipelines generated from a standard bucket set,
        # excluding advanced features such as speculative decoding or chunked prefill) is only supported by
        # `_derive_manual_config_buckets_with_output_logits_size`.
        # More finer pipeline selection logic should be implemented in the future.

        # TODO: Implement the filtering logic in a way of `apply_on_bucket_config`,
        # so that pipelines are filtered according to each field of `ArtifacPipelineFilter`.

        if self.is_no_op():
            return list(buckets_with_output_logits_size)

        filtered_bucket_config = self.apply_on_bucket_config(bucket_config)
        assert isinstance(filtered_bucket_config, ManualBucketConfig)
        return self._derive_manual_config_buckets_with_output_logits_size(
            buckets_with_output_logits_size,
            filtered_bucket_config,
        )

    def _derive_manual_config_buckets_with_output_logits_size(
        self,
        pipeline_buckets_with_output_logits_size: Sequence[BucketWithOutputLogitsSize],
        target_bucket_config: ManualBucketConfig,
    ) -> List[BucketWithOutputLogitsSize]:

        assert pipeline_buckets_with_output_logits_size

        def get_prefill_bucket_with_output_logits_size(
            bucket: Tuple[int, int],
        ) -> BucketWithOutputLogitsSize:
            # For prefill buckets, possible output_logits_size values are:
            # - 1 (if logit shape optimization is applied and model is generative)
            # - None (for non-generative models without logit shape optimization)
            # - input_ids_size (for generative models without logit shape optimization)
            # we prioritize bucket with output_logits_size=1
            # even though user might have built the artifact with logit shape optimization
            prefill_bucket = Bucket.prefill(*bucket)
            bucket_matches = [
                bucket_with_output_size
                for bucket_with_output_size in pipeline_buckets_with_output_logits_size
                if bucket_with_output_size.bucket == prefill_bucket
            ]

            if not bucket_matches:
                raise ValueError(
                    f"No matching pipeline found for the prefill bucket: {prefill_bucket}"
                )

            # must be unique set - not allowing pipelines of duplicated bucket with output_logits_size
            assert len(bucket_matches) == len(set(bucket_matches))
            if None in [bucket.output_logits_size for bucket in bucket_matches]:
                if len(bucket_matches) > 1:
                    raise ValueError(
                        "Invalid artifact: A pipeline with output_logit_size 'None' was found, indicating the model is non-generative. "
                        "However, other pipelines with same bucket have non-None output logit sizes, which is inconsistent"
                    )
                # bucket_matches contains exactly one element,
                # and its output_logits_size must be None.
                return bucket_matches[0]
            nonzero_output_buckets = [
                bucket
                for bucket in bucket_matches
                if bucket.output_logits_size is not None and bucket.output_logits_size >= 1
            ]
            if not nonzero_output_buckets:
                raise ValueError(
                    "No valid BucketWithOutputLogitsSize with output_logits_size >= 1 was found."
                )
            return min(
                nonzero_output_buckets,
                key=operator.attrgetter("output_logits_size"),  # type: ignore[return-value, arg-type]
            )

        prefill_buckets_with_output_logits_size = [
            get_prefill_bucket_with_output_logits_size(bucket)
            for bucket in target_bucket_config.prefill_buckets
        ]

        decode_buckets_with_output_logits_size = [
            BucketWithOutputLogitsSize(Bucket.decode(*bucket), 1)
            for bucket in (target_bucket_config.decode_buckets or [])
        ]

        for mode, derived in zip(
            ["prefill", "decode"],
            [prefill_buckets_with_output_logits_size, decode_buckets_with_output_logits_size],
        ):
            if not set(derived) <= set(pipeline_buckets_with_output_logits_size):
                raise ValueError(
                    f"Required {mode} buckets not in artifact. "
                    f"Artifact: {pipeline_buckets_with_output_logits_size}, Required: {derived}"
                )

        return prefill_buckets_with_output_logits_size + decode_buckets_with_output_logits_size

    def is_no_op(self) -> bool:
        return (
            not self.allowed_prefill_buckets
            and not self.allowed_decode_buckets
            and self.max_prompt_len is None
            and self.max_seq_len is None
            and self.max_batch_size is None
            and self.min_batch_size is None
        )
