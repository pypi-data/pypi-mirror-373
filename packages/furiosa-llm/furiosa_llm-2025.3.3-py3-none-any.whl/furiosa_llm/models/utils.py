from functools import reduce
import operator
from typing import Any, Callable, Dict, Optional, Tuple, Type

from furiosa_models.architecture.models.serve import (
    CausalModelServer,
)
import torch
from transformers import PretrainedConfig

from .config_types import Bucket, KvCacheSharingAcrossBeamsConfig


def _generate_input_sample_for_bert_qa(
    model_config: PretrainedConfig,
    bucket: "Bucket",
    compact_causal_mask: bool,
    tensor_generator: Callable[..., torch.Tensor],
) -> Dict[str, Any]:
    attention_mask_shape: Tuple[int, ...]
    if compact_causal_mask:
        attention_mask_shape = (bucket.batch_size, bucket.attention_size)
        attention_mask_dtype = torch.uint8
    else:
        attention_mask_shape = (bucket.batch_size, bucket.attention_size, bucket.attention_size)
        attention_mask_dtype = torch.bool

    return {
        "input_ids": tensor_generator(
            bucket.batch_size,
            bucket.attention_size,
            dtype=torch.int32,
            high=model_config.vocab_size,
        ),
        "token_type_ids": tensor_generator(
            bucket.batch_size,
            bucket.attention_size,
            dtype=torch.int32,
            high=model_config.type_vocab_size,
        ),
        "attention_mask": tensor_generator(*attention_mask_shape, dtype=attention_mask_dtype),
        "position_ids": tensor_generator(
            bucket.batch_size,
            bucket.attention_size,
            dtype=torch.int32,
            high=model_config.max_position_embeddings,
        ),
    }


def _range_and_reshape(*args, dtype: torch.dtype, start=0) -> torch.Tensor:
    return torch.arange(start, start + reduce(operator.mul, args, 1), dtype=dtype).reshape(*args)


def _generate_input_sample_for_causal_lm(
    model_config: PretrainedConfig,
    bucket: "Bucket",
    kv_cache_dtype: torch.dtype,
    paged_attention_num_blocks: Optional[int],
    paged_attention_block_size: Optional[int],
    kv_cache_sharing_across_beams_config: Optional["KvCacheSharingAcrossBeamsConfig"],
    is_packed_optimized: bool,
    use_causal_mask: bool,
    need_args_for_speculative_decoding: bool,
    go_through_mcp: bool,
    is_sliced_model: bool,
    use_2d_masks: bool,
    merged_kv_indices: bool,
    tensor_generator: Callable[..., torch.Tensor],
) -> Dict[str, Any]:
    num_kv_heads = getattr(
        model_config, "num_key_value_heads", getattr(model_config, "num_attention_heads", None)
    )
    if num_kv_heads is None:
        raise ValueError(
            f"Failed to get number of key value heads for {type(model_config)} model config."
        )

    if (paged_attention_num_blocks is None) != (paged_attention_block_size is None):
        raise ValueError(
            "Both `paged_attention_num_blocks` and `paged_attention_block_size` must be "
            "provided together or both must be None. Only one of them cannot be set."
        )
    num_attention_heads = model_config.num_attention_heads
    hidden_size = model_config.hidden_size
    kv_head_dim = getattr(model_config, "head_dim", hidden_size // num_attention_heads)

    num_hidden_layers = model_config.num_hidden_layers

    if model_config.architectures[0] in (
        "LlamaForCausalLM",
        "ExaoneForCausalLM",
        "MistralForCausalLM",
    ):
        assert len(model_config.architectures) == 1
        position_ids_dtype = torch.int32
    else:
        position_ids_dtype = (
            torch.int32
            if go_through_mcp
            and paged_attention_num_blocks is not None
            and model_config.architectures[0] == "GPTJForCausalLM"
            else torch.int64
        )

    sample: Dict[str, Any] = {
        "input_ids": tensor_generator(
            bucket.batch_size,
            bucket.input_ids_size,
            dtype=torch.int32,
            high=model_config.vocab_size,
        ),
        "attention_mask": torch.ones(bucket.batch_size, bucket.attention_size, dtype=torch.bool),
        "position_ids": torch.arange(
            bucket.attention_size,
            bucket.attention_size + bucket.input_ids_size,
            dtype=position_ids_dtype,
        ).expand(bucket.batch_size, -1),
    }

    if paged_attention_num_blocks is not None and paged_attention_block_size is not None:
        # paged attention model

        # total block space
        sample["past_key_values"] = [
            [
                tensor_generator(
                    paged_attention_num_blocks,
                    1,
                    num_kv_heads,
                    kv_head_dim,
                    dtype=kv_cache_dtype,
                )
                for _ in range(2)
            ]
            for _ in range(model_config.num_hidden_layers)
        ]

        if is_packed_optimized:
            # paged attention model with packed attention optimization.
            sample["new_key_location"] = _range_and_reshape(
                bucket.batch_size, bucket.input_ids_size, dtype=torch.int32
            )
            sample["new_value_location"] = _range_and_reshape(
                bucket.batch_size, bucket.input_ids_size, dtype=torch.int32
            )
            sample["bucket_size"] = bucket.attention_size
            sample["use_cache"] = False

            sample["is_prefill"] = bucket.is_prefill

            if kv_cache_sharing_across_beams_config is not None and not (
                bucket.is_prefill and go_through_mcp
            ):
                # Size of the real batch that current batch originates from in beam search.
                real_batch_size = (
                    bucket.batch_size // kv_cache_sharing_across_beams_config.beam_width
                )
                sample["num_beam"] = kv_cache_sharing_across_beams_config.beam_width
                sample["num_real_batch"] = real_batch_size
                sample["max_new_tokens"] = kv_cache_sharing_across_beams_config.max_new_tokens

            if bucket.is_prefill:
                if use_causal_mask:
                    # attention_mask is not used in prefill phase
                    del sample["attention_mask"]
                    if use_2d_masks:
                        causal_mask = torch.ones(
                            (bucket.batch_size, bucket.attention_size),
                            dtype=torch.bool,
                        )
                    else:
                        causal_mask = torch.ones(
                            (bucket.batch_size, bucket.attention_size, bucket.attention_size),
                            dtype=torch.bool,
                        )
                    sample["causal_mask"] = causal_mask
            else:
                if kv_cache_sharing_across_beams_config is None:
                    sample["past_valid_key_indices"] = torch.arange(
                        bucket.batch_size * bucket.input_ids_size,
                        bucket.batch_size * bucket.attention_size,
                        dtype=torch.int32,
                    )
                    sample["past_valid_value_indices"] = torch.arange(
                        bucket.batch_size * bucket.input_ids_size,
                        bucket.batch_size * bucket.attention_size,
                        dtype=torch.int32,
                    )
                else:
                    if bucket.batch_size % kv_cache_sharing_across_beams_config.beam_width != 0:
                        raise ValueError(
                            "Invalid input sample generation config: Bucket's batch size is not divisible by num beams."
                        )
                    max_prompt_len = (
                        bucket.attention_size - kv_cache_sharing_across_beams_config.max_new_tokens
                    )
                    sample["past_valid_key_prompt_indices"] = tensor_generator(
                        real_batch_size * max_prompt_len, dtype=torch.int32
                    )
                    sample["past_valid_value_prompt_indices"] = tensor_generator(
                        real_batch_size * max_prompt_len, dtype=torch.int32
                    )
                    sample["past_valid_key_decode_indices"] = tensor_generator(
                        bucket.batch_size
                        * ((bucket.attention_size - bucket.input_ids_size) - max_prompt_len),
                        dtype=torch.int32,
                    )
                    sample["past_valid_value_decode_indices"] = tensor_generator(
                        bucket.batch_size
                        * ((bucket.attention_size - bucket.input_ids_size) - max_prompt_len),
                        dtype=torch.int32,
                    )

        else:
            attention_length = bucket.attention_size
            sample["input_metadata"] = [
                torch.IntTensor(
                    [
                        tuple(
                            range(
                                b * attention_length,
                                b * attention_length + bucket.input_ids_size,
                            )
                        )
                        for b in range(bucket.batch_size)
                    ]
                ).reshape(
                    bucket.batch_size, bucket.input_ids_size
                ),  # new_key_location
                torch.IntTensor(
                    [
                        tuple(
                            range(
                                b * attention_length,
                                b * attention_length + bucket.input_ids_size,
                            )
                        )
                        for b in range(bucket.batch_size)
                    ]
                ).reshape(
                    bucket.batch_size, bucket.input_ids_size
                ),  # new_value_location
                attention_length * paged_attention_block_size,  # bucket_size
                torch.IntTensor(
                    [
                        tuple(range(b * attention_length, (b + 1) * attention_length))
                        for b in range(bucket.batch_size)
                    ]
                ).reshape(
                    -1
                ),  # valid_key_indices
                torch.IntTensor(
                    [
                        tuple(range(b * attention_length, (b + 1) * attention_length))
                        for b in range(bucket.batch_size)
                    ]
                ).reshape(
                    -1
                ),  # valid_value_indices
            ]
    else:
        if not bucket.is_prefill:
            kv_cache = [
                [
                    tensor_generator(
                        bucket.batch_size,
                        num_kv_heads,
                        bucket.kv_cache_size,
                        kv_head_dim,
                        dtype=kv_cache_dtype,
                    )
                    for _ in range(2)
                ]
                for _ in range(num_hidden_layers)
            ]
            sample["past_key_values"] = kv_cache

    if need_args_for_speculative_decoding and bucket.kv_cache_size > 0:
        # FIXME: remove this branching and `is_slice_model` arg after unifying `llama3.symbolic.aramco_specdec.LlamaForCausalLM`'s args
        # with `llama3.symbolic.aramco_specdec_slice_integrated.LlamaForCausalLM`.
        if use_2d_masks:
            sample["attention_mask"] = torch.ones(
                bucket.batch_size, bucket.attention_size, dtype=torch.bool
            )
        else:
            if is_sliced_model:
                sample["sp_len"] = bucket.input_ids_size - 1
            else:
                sample["sp_len"] = bucket.input_ids_size
            sample["attention_mask"] = torch.ones(
                bucket.batch_size, bucket.input_ids_size, bucket.attention_size, dtype=torch.bool
            )

    if merged_kv_indices:
        # Model has merged kv indices tensors.
        del sample["new_key_location"]
        del sample["new_value_location"]
        sample["new_kv_location"] = tensor_generator(
            bucket.batch_size, bucket.input_ids_size, dtype=torch.int32
        )
        if bucket.is_decode:
            del sample["past_valid_key_indices"]
            del sample["past_valid_value_indices"]
            sample["past_valid_kv_indices"] = tensor_generator(
                bucket.batch_size * bucket.kv_cache_size, dtype=torch.int32
            )

    return sample


def _torch_zeros(*args, **kwargs) -> torch.Tensor:
    kwargs.pop("low", None)
    kwargs.pop("high", None)

    return torch.zeros(*args, **kwargs)


def gen_random_tensor(*args, dtype=torch.float32, low=0, high=100) -> torch.Tensor:
    if dtype in (torch.float16, torch.float32, torch.float64):
        return torch.rand(*args, dtype=dtype)
    elif dtype in (torch.int8, torch.uint8, torch.int16, torch.int32, torch.int64, torch.bool):
        if dtype == torch.bool:
            low, high = 0, 2
        return torch.randint(low, high, args, dtype=dtype)
    else:
        raise NotImplementedError(f"Unsupported dtype: {dtype}")


def generate_input_sample(
    model_cls: Type[torch.nn.Module],
    model_config: PretrainedConfig,
    bucket: "Bucket",
    kv_cache_dtype: Optional[torch.dtype],
    paged_attention_num_blocks: Optional[int],
    paged_attention_block_size: Optional[int],
    kv_cache_sharing_across_beams_config: Optional["KvCacheSharingAcrossBeamsConfig"],
    is_packed_optimized: bool,
    compact_causal_mask_for_bert: bool,
    use_causal_mask_for_generative_model: bool,
    need_args_for_speculative_decoding: bool,
    go_through_mcp: bool,
    is_sliced_model: bool,
    use_2d_masks: bool,
    merged_kv_indices: bool,
    random_value: bool = False,
) -> Dict[str, Any]:
    """Generate input samples of nn.Module, which are used to traces through Torch Dynamo

    :param model_cls: Class of the model.
    :param model_config: Hf config of the model.
    :param bucket: Bucket used to generate input sample.
    :param kv_cache_dtype: Dtype of kv cache.
    :param paged_attention_num_blocks: Number of paged attenetion blocks for model trace.
    :param paged_attention_block_size: The maximum number of tokens that can be stored in a single paged attention block.
    :param is_packed_optimized: Whether it's input for packed optimized model.
    :param random_value: Whether to generate input tensors filled with random values.
    :param is_quantized: Whether it's input for quantized model.
    :param compact_causal_mask_for_bert: Whether its input for Bert model with compact causal mask optimization.
        This option has effect only when the model's architecture is ``BertForQuestionAnswering``.
    :param use_causal_mask_for_generative_model: Whether to use causal mask instead of attention mask for generative model in prefill phase.
    :param go_through_mcp: Whether the model is quantized via MCP.
    :param is_sliced_model: Whether the model's last block is sliced in prefill phase.
    :param use_2d_masks: Whether the model uses 2D attention masks instead of 3D masks.
    :param merged_kv_indices: Whether the model's kv cache indices tensors are merged into one single input tensor.
    :return: Input sample of type Dict. Model can be run with ``model(**sample)``.
    """
    if len(model_config.architectures) != 1:
        raise NotImplementedError("Currently, only single architecture model is supported.")

    tensor_generator: Callable = gen_random_tensor if random_value else _torch_zeros  # type: ignore

    arch = model_config.architectures[0]

    if issubclass(model_cls, CausalModelServer):
        # furiosa-models-lang models. Use its own input sample generation API.
        if not paged_attention_num_blocks or not paged_attention_block_size:
            raise ValueError(
                "Both `paged_attention_num_blocks` and `paged_attention_block_size` should be "
                "given and not be zero for furiosa-models-lang models."
            )
        if not kv_cache_dtype:
            raise ValueError("kv_cache_dtype must be provided for furiosa-models-lang models.")

        if merged_kv_indices:
            raise ValueError(
                "Model with merged kv indices are not supported for furiosa-models-lang models."
            )
        if use_2d_masks:
            raise ValueError("2D masks are not supported for furiosa-models-lang models.")

        return model_cls.make_example_inputs(
            model_config,
            batch_size=bucket.batch_size,
            attention_size=bucket.attention_size,
            kv_cache_size=bucket.kv_cache_size,
            paged_attention_block_size=paged_attention_block_size,
            paged_attention_num_blocks=paged_attention_num_blocks,
            kv_cache_dtype=kv_cache_dtype,
        )
    elif arch in (
        "GPTJForCausalLM",
        "LlamaForCausalLM",
        "OPTForCausalLM",
        "GPT2LMHeadModel",
        "ExaoneForCausalLM",
        "MistralForCausalLM",
    ):
        if kv_cache_dtype is None:
            raise ValueError("kv_cache_dtype must be provided for CausalLM models.")
        return _generate_input_sample_for_causal_lm(
            model_config,
            bucket,
            kv_cache_dtype,
            paged_attention_num_blocks,
            paged_attention_block_size,
            kv_cache_sharing_across_beams_config,
            is_packed_optimized,
            use_causal_mask_for_generative_model,
            need_args_for_speculative_decoding,
            go_through_mcp,
            is_sliced_model,
            use_2d_masks,
            merged_kv_indices,
            tensor_generator,
        )
    elif arch in ("BertForQuestionAnswering", "RobertaForQuestionAnswering"):
        return _generate_input_sample_for_bert_qa(
            model_config, bucket, compact_causal_mask_for_bert, tensor_generator
        )
    else:
        raise NotImplementedError(f"Unsupported model architecture: {arch}")
