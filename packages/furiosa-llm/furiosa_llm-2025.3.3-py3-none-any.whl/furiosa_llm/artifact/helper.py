from collections import Counter, deque
import copy
from itertools import chain, islice
import logging
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, Type, Union

import torch
from torch._subclasses import FakeTensorMode
from torch.overrides import TorchFunctionMode
from transformers import PreTrainedModel

from furiosa_llm.parallelize.export.tensor import ParamFileMetadata
from furiosa_llm.parallelize.mppp.config import DeviceId
from furiosa_llm.parallelize.pipeline.builder.arg_types import (
    LogitsSliceConfig,
    NonSharedPipelineBuildConfig,
)
from furiosa_llm.parallelize.pipeline.types import (
    CommSuperTask,
    CompSuperTask,
    Device,
    InOutputSuperTask,
    MetaData,
    MetadataTensorSlice,
    MetadataTensorSlices,
    NameAfterMakeFx,
    ParamInfo,
    SuperTask,
    SuperTaskId,
    SuperTaskKind,
)
from furiosa_llm.utils import (
    get_list_with_no_dup_with_order_preserved,
    maybe_register_config_serialize_by_value,
    zip_equal,
)

from ..models import ModelMetadata
from ..models.config_types import (
    Bucket,
    BucketConfig,
    BucketWithOutputLogitsSize,
    KvCacheSharingAcrossBeamsConfig,
    ManualBucketConfig,
    MinimalBucketConfig,
    PagedAttentionConfig,
    PipelineMetadata,
    PipelineWithMetadata,
)
from ..models.utils import generate_input_sample
from ..parallelize.compiler_config import CompilerConfigContext, PipelineMode
from ..parallelize.model_creation_info import ModelCreationInfo
from ..parallelize.mppp.api import Mppp
from ..parallelize.pipeline import Pipeline
from ..parallelize.pipeline.builder import PipelineBuilder
from ..parallelize.pipeline.types import ParamFileId, TensorGenInfo, TensorInfo

logger = logging.getLogger(__name__)

# TODO: do we need to relax this assumption?
_CHUNKED_PREFILL_BUCKETS_BATCH_SIZE = 1
_FAKE_TENSOR_MODE = FakeTensorMode(allow_non_fake_inputs=True)


class TensorToTensorGenInfoMode(TorchFunctionMode):
    """Converts Tensor to TensorGenInfo when clone or deepcopy is called on a tensor."""

    def __init__(self):
        super().__init__()

    def __torch_function__(self, func, types, args=(), kwargs=None):
        kwargs = kwargs if kwargs else {}

        if func == torch._C._TensorBase.clone:
            tensor = args[0]
            tensor_info = extract_tensor_info(tensor)
            return tensor_info
        elif func == torch.Tensor.__deepcopy__:
            assert len(args) == 2 and len(kwargs) == 0
            tensor, memo = args

            if id(tensor) in memo:
                return memo[id(tensor)]

            tensor_info = extract_tensor_info(tensor)
            memo[id(tensor)] = tensor_info
            return tensor_info
        else:
            raise ValueError(f"Not clone or deepcopy op: {func}")


def extract_tensor_info(tensor: torch.Tensor) -> TensorGenInfo:
    return TensorGenInfo(shape=tensor.shape, dtype=tensor.dtype)


def generate_non_shared_pipeline_build_config(
    model_metadata: ModelMetadata,
    bucket: Bucket,
    kv_cache_dtype: Optional[torch.dtype],
    paged_attention_config: Optional[PagedAttentionConfig],
    kv_cache_sharing_across_beams_config: Optional[KvCacheSharingAcrossBeamsConfig],
    is_packed_optimized: bool,
    compact_causal_mask_for_bert: bool,
    use_causal_mask_for_prefill: bool,
    need_args_for_speculative_decoding: bool,
    use_2d_attn_masks: bool,
    is_quantized: bool,
    go_through_mcp: bool,
    is_sliced_model: bool,
    prefill_pipeline_mode: PipelineMode,
    decode_pipeline_mode: PipelineMode,
    original_model_type: Type,
    num_blocks_per_supertask: Union[int, Sequence[int]],
    compiler_config_context: CompilerConfigContext,
    target_output_logits_size: Optional[int],
    output_logits_slice_direction: Optional[str] = "left",
) -> NonSharedPipelineBuildConfig:

    # https://furiosa-ai.slack.com/archives/C04HK6EK8RL/p1747286933388599?thread_ts=1747212852.183939&cid=C04HK6EK8RL
    # This value has effect on compilation result.
    paged_attention_num_blocks = bucket.batch_size * bucket.attention_size + 100

    with _FAKE_TENSOR_MODE:
        input_sample_data = generate_input_sample(
            model_metadata.get_optimized_cls(),
            model_metadata.config,
            bucket,
            kv_cache_dtype,
            paged_attention_num_blocks if paged_attention_config else None,
            paged_attention_config.block_size if paged_attention_config else None,
            kv_cache_sharing_across_beams_config,
            is_packed_optimized,
            compact_causal_mask_for_bert,
            use_causal_mask_for_prefill,
            need_args_for_speculative_decoding,
            go_through_mcp,
            is_sliced_model,
            use_2d_masks=use_2d_attn_masks,
            merged_kv_indices=model_metadata.optimize_options.merged_kv_indices,
        )
        with TensorToTensorGenInfoMode():
            input_sample_data = copy.deepcopy(input_sample_data)
        model_name = (
            f"Quantized_{original_model_type.__module__}.{original_model_type.__name__}"
            if is_quantized
            else f"{original_model_type.__module__}.{original_model_type.__name__}"
        )
        # Please reflect the implementation of PipelineName in furiosa-llm-tests/src/e2e_base.rs
        # TODO: save needed information in Pipeline's metadata, instead of saving it in pipeline name.
        pipeline_name = f"{model_name}-kv{bucket.kv_cache_size}-b{bucket.batch_size}-attn{bucket.attention_size}"
        compiler_config_context = copy.deepcopy(compiler_config_context)

        if bucket.is_prefill:
            compiler_config_context.phase = prefill_pipeline_mode
        elif bucket.is_decode:
            compiler_config_context.phase = decode_pipeline_mode
        else:
            # FIXME: change this to proper phase config
            compiler_config_context.phase = PipelineMode.UNKNOWN
        compiler_config_context.bucket = bucket

        logits_slice_config = None
        if target_output_logits_size is not None:
            original_output_logits_size = model_metadata.get_output_logits_size(bucket)
            if original_output_logits_size is None:
                raise ValueError("Failed to get expected output logit size of the model.")
            if original_output_logits_size != target_output_logits_size:
                if target_output_logits_size == 0:
                    output_logits_slice_direction = None
                logits_slice_config = LogitsSliceConfig(
                    output_logits_slice_direction, target_output_logits_size
                )

        return NonSharedPipelineBuildConfig(
            args_data=(),  # assumed LLM models have kwargs only
            kwargs_data=input_sample_data,
            pipeline_name=pipeline_name,
            compile_config=compiler_config_context,
            logits_slice_config=logits_slice_config,
            num_blocks_per_supertask=num_blocks_per_supertask,
        )


def build_pipelines(
    model: ModelCreationInfo,
    buckets_with_output_size: Sequence[BucketWithOutputLogitsSize],
    devices: Sequence[Device],
    param_file_metadata: ParamFileMetadata,
    cache_dir: Optional[Path],
    mppp: Mppp,
    comp_supertask_kind: SuperTaskKind,
    one_supertask_per_device: bool,
    use_blockwise_compile: bool,
    embedding_layer_as_single_block: bool,
    do_decompositions_for_model_rewrite: bool,
    kv_cache_dtype: Optional[torch.dtype],
    paged_attention_config: Optional[PagedAttentionConfig],
    sparse_select_version: str,
    kv_cache_sharing_across_beams_config: Optional[KvCacheSharingAcrossBeamsConfig],
    tmp_dir: os.PathLike,
    model_metadata: ModelMetadata,
    # current context: model_qname, beam_size
    compiler_config_context: CompilerConfigContext,
    num_pipeline_builder_workers: int,
    num_compile_workers: int,
    embed_all_constants_into_graph: bool,
    num_blocks_per_supertask: Union[
        int, Sequence[int], Callable[[Bucket], Union[int, Sequence[int]]]
    ],
    is_generative_model: bool,
    param_saved_format: str = "safetensors",
    **kwargs,
) -> List[PipelineWithMetadata]:

    if paged_attention_config and paged_attention_config.block_size != 1:
        raise NotImplementedError(
            "Currently, only paged attention with block_size=1 is supported. "
            f"However {paged_attention_config.block_size} is given."
        )

    prefill_pipeline_mode = (
        PipelineMode.LLM_PREFILL if is_generative_model else PipelineMode.UNKNOWN
    )
    decode_pipeline_mode = PipelineMode.LLM_DECODE if is_generative_model else PipelineMode.UNKNOWN

    # do pre-compile first, and generate a pipelines with fx.graph supertask
    is_beam_search_kv_cache_sharing_model = model_metadata.is_beam_search_kv_cache_sharing_model

    pipeline_builder = PipelineBuilder(
        model,
        model.metadata.config,
        tmp_dir,
        is_beam_search_kv_cache_sharing_model=is_beam_search_kv_cache_sharing_model,
    )
    is_packed_optimized = model_metadata.optimize_options.optimize_packed
    compact_causal_mask_for_bert = model_metadata.is_compact_causal_mask_for_bert()
    use_causal_mask_for_prefill = model_metadata.optimize_options.causal_mask_free_decoding
    need_args_for_speculative_decoding = model_metadata.supports_speculative_decoding
    is_quantized = model_metadata.is_quantized

    if isinstance(model, PreTrainedModel):
        original_model_type = model.original_type
    else:
        assert isinstance(model, ModelCreationInfo)
        original_model_type = model.metadata.get_optimized_cls()

    num_blocks_per_supertasks_per_pipeline = [
        (
            num_blocks_per_supertask(bucket_with_output_size.bucket)
            if callable(num_blocks_per_supertask)
            else num_blocks_per_supertask
        )
        for bucket_with_output_size in buckets_with_output_size
    ]

    non_shared_pipe_build_configs = [
        generate_non_shared_pipeline_build_config(
            model_metadata=model_metadata,
            bucket=bucket_with_output_size.bucket,
            kv_cache_dtype=kv_cache_dtype,
            paged_attention_config=paged_attention_config,
            kv_cache_sharing_across_beams_config=kv_cache_sharing_across_beams_config,
            is_packed_optimized=is_packed_optimized,
            compact_causal_mask_for_bert=compact_causal_mask_for_bert,
            use_causal_mask_for_prefill=use_causal_mask_for_prefill,
            need_args_for_speculative_decoding=need_args_for_speculative_decoding,
            use_2d_attn_masks=model_metadata.optimize_options.use_2d_masks,
            is_quantized=is_quantized,
            go_through_mcp=model.metadata.need_quant_artifacts,
            is_sliced_model=model.metadata.optimize_options.calculate_logit_only_for_last_token,
            prefill_pipeline_mode=prefill_pipeline_mode,
            decode_pipeline_mode=decode_pipeline_mode,
            original_model_type=original_model_type,
            num_blocks_per_supertask=num_blocks_per_supertask_,
            compiler_config_context=compiler_config_context,
            target_output_logits_size=bucket_with_output_size.output_logits_size,
        )
        for bucket_with_output_size, num_blocks_per_supertask_ in zip_equal(
            buckets_with_output_size, num_blocks_per_supertasks_per_pipeline
        )
    ]

    pipelines = pipeline_builder.build_pipelines(
        devices=devices,
        mppp=mppp,
        non_shared_configs=non_shared_pipe_build_configs,
        param_file_metadata=param_file_metadata,
        comp_supertask_kind=comp_supertask_kind,
        cache_dir=cache_dir,
        one_supertask_per_device=one_supertask_per_device,
        use_blockwise_compile=use_blockwise_compile,
        embedding_layer_as_single_block=embedding_layer_as_single_block,
        do_decompositions_for_model_rewrite=do_decompositions_for_model_rewrite,
        sparse_select_version=sparse_select_version,
        embed_all_constants_into_graph=embed_all_constants_into_graph,
        padding_block_idx=(
            paged_attention_config.padding_block_idx if paged_attention_config else None
        ),
        param_saved_format=param_saved_format,
        num_pipeline_builder_workers=num_pipeline_builder_workers,
        num_compile_workers=num_compile_workers,
    )

    pipelines_with_metadata = [
        PipelineWithMetadata(
            pipeline=pipeline,
            metadata=PipelineMetadata(
                output_logits_size=bucket_with_output_size.output_logits_size,
                num_blocks_per_supertask=num_blocks_per_supertask_,
            ),
        )
        for pipeline, bucket_with_output_size, num_blocks_per_supertask_ in zip_equal(
            pipelines, buckets_with_output_size, num_blocks_per_supertasks_per_pipeline
        )
    ]

    return pipelines_with_metadata


def _get_buckets_for_chunked_prefill(
    max_prompt_len: int,
    chunk_size: int,
) -> List[Bucket]:
    assert chunk_size <= max_prompt_len

    share, remainder = divmod(max_prompt_len, chunk_size)
    buckets = []

    # XXX: We only consider buckets with batch 1 if chunked prefill is used.
    for i in range(1, share + 1):
        buckets.append(
            Bucket(
                _CHUNKED_PREFILL_BUCKETS_BATCH_SIZE,
                i * chunk_size,
                (i - 1) * chunk_size,
            )
        )
    if remainder:
        buckets.append(
            Bucket(
                _CHUNKED_PREFILL_BUCKETS_BATCH_SIZE,
                max_prompt_len,
                share * chunk_size,
            )
        )
    return buckets


def _get_optimized_buckets_with_output_logits_size(
    bucket_config: BucketConfig,
    is_generative_model: bool,
    max_prompt_len: int,
    max_seq_len_to_capture: int,
    num_speculative_tokens: Optional[int],
    prefill_chunk_size: Optional[int],
    allow_buckets_with_no_output: bool = False,
) -> Tuple[
    List[BucketWithOutputLogitsSize],
    List[BucketWithOutputLogitsSize],
    List[BucketWithOutputLogitsSize],
]:
    if isinstance(bucket_config, MinimalBucketConfig):
        assert bucket_config.max_seq_len == max_seq_len_to_capture
        if prefill_chunk_size:
            # If chunked prefill is used, original prefill buckets are not used.
            prefill_buckets = []
        else:
            prefill_buckets = [Bucket.prefill(1, max_prompt_len)]
        decode_buckets = [Bucket.decode(1, max_seq_len_to_capture)] if is_generative_model else []
    elif isinstance(bucket_config, ManualBucketConfig):
        duplicate_prefill_buckets = [
            bucket for bucket, cnt in Counter(bucket_config.prefill_buckets).items() if cnt > 1
        ]
        if duplicate_prefill_buckets:
            logger.warning(f"Duplicate prefill buckets are found: {duplicate_prefill_buckets}. ")

        if bucket_config.decode_buckets:
            duplicate_decode_buckets = [
                bucket for bucket, cnt in Counter(bucket_config.decode_buckets).items() if cnt > 1
            ]
            if duplicate_decode_buckets:
                logger.warning(f"Duplicate decode buckets are found: {duplicate_decode_buckets}. ")

        prefill_buckets = [Bucket.prefill(*bucket) for bucket in bucket_config.prefill_buckets]
        if is_generative_model:
            # FIXME: This is a temporary workaround to support empty decode bucket case,
            # just for getting fx graphs using `LLM.get_splitted_gms` without creating `NativeLLMEngine`.
            if bucket_config.decode_buckets is None:
                raise ValueError("decode_buckets must be given for generative models.")
            decode_buckets = [Bucket.decode(*bucket) for bucket in bucket_config.decode_buckets]
        else:
            if bucket_config.decode_buckets:
                logger.warning(
                    "decode_buckets will be ignored because the model is not a generative model."
                )
            decode_buckets = []
    else:
        raise ValueError(f"Invalid bucket config: {bucket_config}")

    if is_generative_model:
        prefill_output_logits_size = 1
    else:
        prefill_output_logits_size = None

    prefill_buckets_with_output_size = [
        BucketWithOutputLogitsSize(bucket=bucket, output_logits_size=prefill_output_logits_size)
        for bucket in prefill_buckets
    ]
    assert all(bucket.input_ids_size == 1 for bucket in decode_buckets)
    decode_buckets_with_output_size = [
        BucketWithOutputLogitsSize(bucket, output_logits_size=1) for bucket in decode_buckets
    ]

    other_buckets_with_output_size: List[BucketWithOutputLogitsSize] = []

    # Generate buckets for speculative decoding if needed.
    if num_speculative_tokens is not None:
        if num_speculative_tokens == 0:
            raise ValueError("`num_speculative_tokens` must be larger than 0.")
        for bucket_with_output_size in decode_buckets_with_output_size:
            bucket = bucket_with_output_size.bucket
            new_bucket = Bucket(
                bucket.batch_size,
                bucket.attention_size,
                # NOTE: Why input_ids length become (num_speculative_tokens + 1) instead of num_speculative_tokens?
                # Whenever target model verifies draft model's suggested tokens, it generates exactly one bonus token regardless
                # of how many suggestion tokens are actually accepted. And at the time of next verification, this bonus token
                # (from previous verification) should be given as an input_ids (not kv cache!) because there is no kv cache for this bonus token.
                # So input_ids length for each verification should be num_speculative_tokens + 1 (for bonus token).
                bucket.attention_size - (num_speculative_tokens + 1),
            )
            other_buckets_with_output_size.append(
                BucketWithOutputLogitsSize(new_bucket, output_logits_size=new_bucket.input_ids_size)
            )

    if prefill_chunk_size:
        # Add buckets for chunked prefill.
        if prefill_chunk_size > max_prompt_len:
            raise ValueError("`prefill_chunk_size` should be smaller than `max_prompt_len`.")
        buckets_for_chunked_prefill = _get_buckets_for_chunked_prefill(
            max_prompt_len, prefill_chunk_size
        )
        for bucket in buckets_for_chunked_prefill:
            # Always need output from chunked prefill bucket graph with `max_prompt_len` attention size.
            generate_no_output_graph = bucket.attention_size != max_prompt_len
            if generate_no_output_graph and allow_buckets_with_no_output:
                output_logits_sizes: Tuple[int, ...] = (0, 1)
            else:
                output_logits_sizes = (1,)

            for output_logits_size in output_logits_sizes:
                if bucket.is_prefill:
                    prefill_buckets_with_output_size.append(
                        BucketWithOutputLogitsSize(bucket, output_logits_size)
                    )
                else:
                    other_buckets_with_output_size.append(
                        BucketWithOutputLogitsSize(bucket, output_logits_size)
                    )

    return (
        prefill_buckets_with_output_size,
        decode_buckets_with_output_size,
        other_buckets_with_output_size,
    )


def get_buckets_with_output_logits_size(
    model_metadata: ModelMetadata,
    bucket_config: BucketConfig,
    max_prompt_len: int,
    max_seq_len_to_capture: int,
    num_speculative_tokens: Optional[int],
    prefill_chunk_size: Optional[int],
    optimize_bucket_output_logits_size: bool,
) -> Tuple[
    List[BucketWithOutputLogitsSize],
    List[BucketWithOutputLogitsSize],
    List[BucketWithOutputLogitsSize],
]:
    (
        prefill_buckets_with_output_size,
        decode_buckets_with_output_size,
        other_buckets_with_output_size,
    ) = _get_optimized_buckets_with_output_logits_size(
        bucket_config,
        model_metadata.is_generative_model,
        max_prompt_len,
        max_seq_len_to_capture,
        num_speculative_tokens,
        prefill_chunk_size,
    )

    if not optimize_bucket_output_logits_size:
        # If bucket output logit optimization is disabled, change each bucket's output logit size to original model's expected one.
        for bucket_with_output_size in chain(
            prefill_buckets_with_output_size,
            decode_buckets_with_output_size,
            other_buckets_with_output_size,
        ):
            bucket_with_output_size.output_logits_size = model_metadata.get_output_logits_size(
                bucket_with_output_size.bucket
            )

    # Remove duplication
    prefill, decode, others = (
        get_list_with_no_dup_with_order_preserved(buckets_with_output_size)
        for buckets_with_output_size in (
            prefill_buckets_with_output_size,
            decode_buckets_with_output_size,
            other_buckets_with_output_size,
        )
    )

    return prefill, decode, others


def _is_match_in_inoutputs(
    sp_task: Union[CommSuperTask, CompSuperTask],
    succ_sp_task: Union[CommSuperTask, CompSuperTask],
) -> bool:
    """
    Determine whether two supertasks will execute sequentially by verifying if the outputs of `sp_task` are passed as inputs to `succ_sp_task`.
    If so, we record outputs of `sp_task` to mark them as inter-supertask input arg for `succ_sp_task`.
    """
    if isinstance(sp_task, CompSuperTask) and isinstance(succ_sp_task, CompSuperTask):
        return (
            set(sp_task.outputs).issubset(set(succ_sp_task.inputs))
            and sp_task != succ_sp_task
            and bool(sp_task.outputs)
        )
    elif isinstance(sp_task, CompSuperTask) and isinstance(succ_sp_task, CommSuperTask):
        return sp_task.outputs == succ_sp_task.inputs and succ_sp_task.kind is SuperTaskKind.SEND
    elif isinstance(sp_task, CommSuperTask):
        if sp_task.kind is SuperTaskKind.RECV:
            return isinstance(succ_sp_task, CompSuperTask) and set(sp_task.outputs).issubset(
                set(succ_sp_task.inputs)
            )
        elif sp_task.kind is SuperTaskKind.SEND:
            return (
                isinstance(succ_sp_task, CommSuperTask)
                and succ_sp_task.kind is SuperTaskKind.RECV
                and succ_sp_task.group == sp_task.group
            )
        else:
            raise ValueError(f"Invalid CommSuperTask {sp_task} is encountered.")
    else:
        raise ValueError(f"Unexpected Supertask {sp_task} and {succ_sp_task}")


def _get_ordered_supertasks(
    pipeline: Pipeline,
) -> List[Tuple[Union[CompSuperTask, CommSuperTask], Set[NameAfterMakeFx]]]:
    """
    Returns an ordered sequence of Comp/Comm Supertasks in execution order using a topological-sort style algorithm.
    Dependencies between two supertasks are determined by matching output and input args between tasks.
    """
    ordered_super_tasks = list()
    inter_supertask_args = set(
        x
        for supertask in pipeline.supertasks.values()
        for x in supertask.outputs
        if not isinstance(supertask, InOutputSuperTask)
    )

    # Derive a starting CompSuperTask
    # Starting CompSuperTask <> inputs are consisted of arguments excluding inter-supertask args(e.g., `recv`, `submod_d0_c1`) or param/tensor constants
    starting_comp_super_tasks: Sequence[
        Tuple[Union[CommSuperTask, CompSuperTask], Set[NameAfterMakeFx]]
    ] = [
        (sp_task, set())
        for sp_task in pipeline.supertasks.values()
        if isinstance(sp_task, CompSuperTask)
        and not set(sp_task.inputs).intersection(inter_supertask_args)
    ]

    # following must be guaranteed if input `pipeline` is well-formed
    assert starting_comp_super_tasks

    queue_nodes = deque(starting_comp_super_tasks)

    while queue_nodes:
        visited = queue_nodes.popleft()
        ordered_super_tasks.append(visited)
        for sp_task in pipeline.supertasks.values():
            if not isinstance(sp_task, (CompSuperTask, CommSuperTask)):
                continue
            is_matched = _is_match_in_inoutputs(visited[0], sp_task)
            if is_matched:
                queue_nodes.append((sp_task, set(visited[0].outputs)))
    assert len(ordered_super_tasks) == len(
        [
            supertask
            for supertask in pipeline.supertasks.values()
            if not isinstance(supertask, InOutputSuperTask)
        ]
    )
    return ordered_super_tasks


def override_pp_size_on_pipeline(
    old_pipeline: Pipeline,
    devices: Sequence[Sequence[Device]],
    pipeline_parallel_size: Union[int, None],
    num_blocks_per_pp_stage: Union[Sequence[int], None],
) -> Pipeline:
    """
    Returns a new Pipeline that satisfies the pipeline parallelism specified by either pipeline_parallel_size or num_blocks_per_pp_stage,
    by overriding `old_pipeline`. While the generated pipeline is guaranteed to be semantically equivalent to old_pipeline, the input and output argument names may differ.
    """
    assert not (pipeline_parallel_size and num_blocks_per_pp_stage)
    num_of_comp_supertask = len(
        [
            supertask
            for supertask in old_pipeline.supertasks.values()
            if isinstance(supertask, CompSuperTask)
        ]
    )
    if num_blocks_per_pp_stage and sum(num_blocks_per_pp_stage) != num_of_comp_supertask:
        raise ValueError(
            "Sum of `num_blocks_per_pp_stage` must be equal to number of CompSuperTasks within the pipeline."
        )

    # If only `pipeline_parallel_size` is provided, do pp-overriding in even distribution of transformer blocks
    if pipeline_parallel_size and (not num_blocks_per_pp_stage):
        if num_of_comp_supertask % pipeline_parallel_size != 0:
            raise ValueError(
                "For even distribution of transformer blocks over pipeline stages,"
                + "the number of CompSuperTasks within the pipeline must be divisible by `pipeline_parallel_size`."
            )
        num_blocks_per_pp_stage = [
            num_of_comp_supertask // pipeline_parallel_size
        ] * pipeline_parallel_size

    assert num_blocks_per_pp_stage

    if len(devices) != len(num_blocks_per_pp_stage):
        raise ValueError(
            f"Number of devices must be equal to pipeline parallelism size {len(num_blocks_per_pp_stage)}"
        )

    # Returns an overriding pipeline that aligns with the pipeline parallelism specified by num_blocks_per_pp_stage.
    ordered_super_tasks = _get_ordered_supertasks(old_pipeline)

    # Types are specified in `List` type due to later usage of .append()
    ordered_comp_supertasks: List[Tuple[CompSuperTask, Set[NameAfterMakeFx]]] = list()
    for idx, spt in enumerate(ordered_super_tasks):
        if isinstance(spt[0], CompSuperTask):
            if idx != (len(ordered_super_tasks) - 1) and len(spt[0].outputs) > 1:
                raise NotImplementedError(
                    "Currently, pp overriding only supports pipelines of intermediate CompSuperTasks with single output."
                )
            ordered_comp_supertasks.append(spt)  # type: ignore[arg-type]

    assert ordered_comp_supertasks

    def get_device_id_by_device_val(d: Dict[DeviceId, Device], value: Device):
        for k, v in d.items():
            if v == value:
                return k
        raise KeyError(f"Value {value} not found in device dict {d}.")

    new_devices: Dict[DeviceId, Device] = dict()
    alinged_device_ids_in_order: List[DeviceId] = list()
    device_id_cnt = 0
    for device_id, device in enumerate(devices):
        if len(device) != 1:
            raise NotImplementedError(
                "Currently, we do not support pipeline parallelism overriding over artifacts with inter-chip tensor parallelism."
            )
        if device[0] not in new_devices.values():
            new_devices[DeviceId(str(device_id_cnt))] = device[0]
            device_id_cnt += 1
        alinged_device_ids_in_order.append(get_device_id_by_device_val(new_devices, device[0]))

    old_input_tensor_slices: Dict[NameAfterMakeFx, MetadataTensorSlice] = (
        old_pipeline.metadata.tensor_slices.inputs
    )

    old_pipeline_constant_args: Dict[NameAfterMakeFx, ParamInfo] = {
        name: info for name, info in old_pipeline.tensors.items() if isinstance(info, ParamInfo)
    }

    updated_constant_args: Dict[Tuple[DeviceId, ParamFileId, str], NameAfterMakeFx] = {}

    updated_pipeline_tensors: Dict[NameAfterMakeFx, Union[ParamInfo, TensorInfo]] = {}
    updated_pipeline_meta_tensorslices_input: Dict[NameAfterMakeFx, MetadataTensorSlice] = dict()
    in_iter = iter(ordered_comp_supertasks)
    slices_of_comps_per_device = [list(islice(in_iter, 0, i)) for i in num_blocks_per_pp_stage]

    updated_non_inoutput_spt = list()

    # Typed as `List` for the consistency with the field type defined in `SuperTask`
    outputs_of_non_inoutput_spt_lastly_added: List[NameAfterMakeFx] = list()
    group_id_cnt = 0

    def get_metadata_tensorslice_by_origin(
        origin: str, metadata_tensorslices: Sequence[MetadataTensorSlice]
    ) -> MetadataTensorSlice:
        for metadata_tensorslice in metadata_tensorslices:
            if metadata_tensorslice.origin == origin:
                return metadata_tensorslice
        raise ValueError(f"Invalid origin {origin} is encountered")

    old_pipeline_input_meta_ts = list(old_pipeline.metadata.tensor_slices.inputs.values())
    for device_execution_order, device_and_comp_spts in enumerate(
        zip_equal(alinged_device_ids_in_order, slices_of_comps_per_device)
    ):
        device_idx, comps_on_device = device_and_comp_spts
        assert isinstance(device_idx, DeviceId)
        # A map from origins (in str) to ts names in overriding supertask, previously added
        prev_loaded_tensor_slice_within_device: Dict[str, NameAfterMakeFx] = dict()
        for comp, input_from_pred_supertask in comps_on_device:
            # Updates argument for each CompSuperTask.
            # We need to consider the followings:
            # 1. Parameters and Tensor constants: can be preserved while overriding.
            # 2. Tensor slices: require assigning new tensor slices args, as newly derived partition (through CommSuperTask) of CompSuperTasks can split the application of existing tensor slices.
            #   e.g, if the new pipeline parallelism configuration decides to split the execution of CompSuperTasks A and B, common tensor slice arg over A and B should be split into different device.
            # 3. Inter-supertask arguments: restored from the `outputs_of_non_inoutput_spt_lastly_added` in the previous iteration.
            updated_input_names = list()
            # input_from_pred_supertask is `set` instance
            for curr_comp_input_name in comp.inputs:
                if curr_comp_input_name in input_from_pred_supertask:
                    updated_input_names += outputs_of_non_inoutput_spt_lastly_added
                elif curr_comp_input_name in old_pipeline_constant_args:
                    old_param_info = old_pipeline_constant_args[curr_comp_input_name]
                    param_tensor_matching_key = (
                        device_idx,
                        old_param_info.value.param_file,
                        old_param_info.value.name,
                    )
                    if param_tensor_matching_key not in updated_constant_args:
                        new_name = NameAfterMakeFx(f"{curr_comp_input_name}_r{device_idx}")
                        updated_constant_args[param_tensor_matching_key] = new_name
                        assert new_name not in updated_pipeline_tensors
                        updated_pipeline_tensors[new_name] = old_param_info

                    updated_input_names.append(updated_constant_args[param_tensor_matching_key])
                else:
                    origin_of_curr_comp_input = old_input_tensor_slices[curr_comp_input_name].origin
                    if prev_loaded_ts_name_of_same_origin := prev_loaded_tensor_slice_within_device.get(
                        origin_of_curr_comp_input
                    ):
                        ts_name_to_append = prev_loaded_ts_name_of_same_origin
                    else:
                        # Then, it is a tensor slice of unique origin, at least within current device context
                        ts_name_to_append = NameAfterMakeFx(
                            f"d{device_idx}_override_ts_{curr_comp_input_name}"
                        )
                        prev_loaded_tensor_slice_within_device[origin_of_curr_comp_input] = (
                            ts_name_to_append
                        )
                    updated_pipeline_tensors[ts_name_to_append] = old_pipeline.tensors[
                        curr_comp_input_name
                    ]
                    updated_input_names.append(ts_name_to_append)
            updated_pipeline_tensors.update({x: old_pipeline.tensors[x] for x in comp.outputs})
            # since we are assuming sequential structure, just append all the output from previous `outputs_of_lastly_added`
            updated_supertask = comp.shallow_copy_with_replaced_device(
                device_idx
            ).shallow_copy_with_replaced_inputs(updated_input_names)
            updated_non_inoutput_spt.append(updated_supertask)
            outputs_of_non_inoutput_spt_lastly_added = updated_supertask.outputs
        updated_pipeline_meta_tensorslices_input.update(
            {
                overridden_name: get_metadata_tensorslice_by_origin(
                    origin, old_pipeline_input_meta_ts
                ).shallow_copy_with_replaced_device(device_idx)
                for origin, overridden_name in prev_loaded_tensor_slice_within_device.items()
            }
        )

        if device_execution_order != len(slices_of_comps_per_device) - 1:
            # if it is not the final executed CompSuperTask within the device, add two new CommSuperTask instances: SEND and RECV.
            send_comm_supertask = CommSuperTask(
                kind=SuperTaskKind.SEND,
                inputs=outputs_of_non_inoutput_spt_lastly_added,
                outputs=[],
                device=device_idx,
                device_idx=0,
                metadata={},
                group=str(group_id_cnt),
            )
            updated_non_inoutput_spt.append(send_comm_supertask)
            output_name_for_new_comm_recv = NameAfterMakeFx(f"overriding_recv_{group_id_cnt}")

            # overriding Pipeline.tensors
            assert len(outputs_of_non_inoutput_spt_lastly_added) == 1
            updated_pipeline_tensors[output_name_for_new_comm_recv] = old_pipeline.tensors[
                outputs_of_non_inoutput_spt_lastly_added[0]
            ]
            recv_comm_supertask = CommSuperTask(
                kind=SuperTaskKind.RECV,
                inputs=[],
                outputs=[output_name_for_new_comm_recv],
                device=alinged_device_ids_in_order[device_execution_order + 1],
                device_idx=1,
                metadata={},
                group=str(group_id_cnt),
            )
            updated_non_inoutput_spt.append(recv_comm_supertask)
            group_id_cnt += 1
            outputs_of_non_inoutput_spt_lastly_added = recv_comm_supertask.outputs

    # Generating new InOutputSupertasks for the overriding pipeline
    input_super_tasks = [x for x in old_pipeline.supertasks.values() if SuperTask.is_input(x)]
    assert len(input_super_tasks) == 1
    output_super_tasks = [x for x in old_pipeline.supertasks.values() if SuperTask.is_output(x)]
    assert len(output_super_tasks) == 1
    updated_input_supertask = input_super_tasks[0].shallow_copy_with_replaced_outputs(
        list(updated_pipeline_meta_tensorslices_input.keys())
    )
    updated_output_supertask = output_super_tasks[0].shallow_copy_with_replaced_inputs(
        updated_non_inoutput_spt[-1].outputs
    )

    updated_inoutput_supertasks = [updated_input_supertask, updated_output_supertask]
    updated_supertasks = updated_inoutput_supertasks + updated_non_inoutput_spt

    updated_supertasks_with_id = {
        SuperTaskId(i): supertask for i, supertask in enumerate(updated_supertasks)
    }

    # overriding pipeline metadata
    updated_metadata = MetaData(
        tensors=old_pipeline.metadata.tensors,
        tensor_slices=MetadataTensorSlices(
            inputs=updated_pipeline_meta_tensorslices_input,
            outputs={
                output_name: meta_ts.shallow_copy_with_replaced_device(
                    DeviceId(len(num_blocks_per_pp_stage) - 1)
                )
                for output_name, meta_ts in old_pipeline.metadata.tensor_slices.outputs.items()
            },
        ),
    )
    return (
        old_pipeline.shallow_copy_with_new_devices_and_supertasks(
            new_devices, updated_supertasks_with_id
        )
        .shallow_copy_with_replaced_tensors(updated_pipeline_tensors)
        .shallow_copy_with_replaced_metadata(updated_metadata)
    )


def get_default_pipeline_metadata(
    model_metadata: ModelMetadata, bucket: Bucket
) -> PipelineMetadata:
    output_logits_size = model_metadata.get_output_logits_size(bucket)
    return PipelineMetadata(
        output_logits_size=output_logits_size,
        num_blocks_per_supertask=1,
    )


def prestep_for_remote_code_model(
    model_metadata: ModelMetadata,
    num_pipeline_builder_workers: int,
):
    # If `trust_remote_code` and parallel pipeline building is used,
    # serialization logic for remote model config should be registered. Otherwise,
    # it fails to send model metadata to remote ray tasks.
    if num_pipeline_builder_workers > 1:
        # Ensure remote model config is registered in transformers by calling `ModelMetadata.config`.
        model_metadata.config
        maybe_register_config_serialize_by_value()


def verify_device_mesh(device_mesh: Sequence[Sequence[Sequence[str]]]) -> None:
    """
    Verify the device mesh is valid.
    """
    if not device_mesh:
        raise ValueError("Device mesh is empty.")
    pp_group_size = set(len(pp_group) for pp_group in device_mesh)
    if len(pp_group_size) > 1:
        raise ValueError(
            f"Various size of pp groups are detected in given device mesh {device_mesh}. All pp groups must have same number of stages."
        )
    if len(device_mesh) > 1:
        raise NotImplementedError("Using device mesh with data parallelism is not supported yet.")
