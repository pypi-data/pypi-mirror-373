# Most of code is copied from npu-tools/crates/npu-torch-models/pymodels/model_quantize/transformers_llm.py
# https://github.com/furiosa-ai/npu-tools/blob/daaed216eb409bc1e84afe0a582b9e417f1d7876/crates/npu-torch-models/pymodels/model_quantize/transformers_llm.py
from itertools import chain
import logging
import os
from pathlib import Path
import tempfile
from time import time
from typing import AbstractSet, Any, Dict, Mapping, Optional, Sequence, Set, Tuple, Union

import furiosa_llm_models
from furiosa_llm_models.symbolic.helper import CustomHFTracer
import model_compressor as mcp  # type: ignore
import torch
from torch.fx import GraphModule
from torch.overrides import TorchFunctionMode
from transformers import PreTrainedModel
from transformers.modeling_outputs import CausalLMOutputWithPast  # type: ignore

from furiosa_llm.optimum.types import QuantizationConfig

from .config_types import (
    Bucket,
    KvCacheSharingAcrossBeamsConfig,
    PagedAttentionConfig,
)

SAMPLE_PREFILL_BUCKET = Bucket.prefill(4, 128)
SAMPLE_DECODE_BUCKET = Bucket.decode(4, 256)
SAMPLE_PAGED_ATTENTION_CONFIG = PagedAttentionConfig(4096, 1)
SAMPLE_KVCACHE_SHARING_ACROSS_BEAMS_CONFIG = KvCacheSharingAcrossBeamsConfig(4, 128)

logger = logging.getLogger(__file__)


def fx_symbolic_trace_model(
    model: torch.nn.Module,
    input_names: AbstractSet[str],
    custom_concrete_args: Optional[Mapping[str, Any]] = None,
) -> torch.fx.GraphModule:
    from transformers.utils.fx import get_concrete_args  # type: ignore

    concrete_args = get_concrete_args(model, list(input_names))
    if custom_concrete_args is not None:
        concrete_args.update(custom_concrete_args)

    tracer = CustomHFTracer()
    traced_graph = tracer.trace(model, concrete_args=concrete_args)
    traced = torch.fx.GraphModule(model, traced_graph)

    traced.config = model.config
    # The model class must be stored as an attribute to allow model deserialization, which uses trace, and thus
    # _generate_dummy_input, where the model class is needed.
    traced.class_for_deserialization = model.__class__  # type: ignore [assignment]
    traced.device = model.device
    traced.module_name = f"{model.__class__.__module__}.{model.__class__.__name__}"  # type: ignore [assignment]

    return traced


def torchdynamo_trace_model(
    model: torch.nn.Module,
    example_kwargs: Mapping[str, Any],
) -> torch.fx.GraphModule:
    return torch._dynamo.export(model, tracing_mode="symbolic", aten_graph=False)(**example_kwargs)[
        0
    ]


def torch_gather_i32(
    x: torch.Tensor, dim: int, index: torch.Tensor, *, sparse_grad: bool = False
) -> torch.Tensor:
    return torch.ops.furiosa.gather_i32.default(x, dim, index, sparse_grad)


def _replace_gathers_with_gather_i32(model, prefill_model, decode_model) -> None:
    """Replace gathers with gather_i32 for gptj_mlperf_* models."""

    # FIXME: move this to PipelineBuilder
    def _replace_torch_gather_with_gather_i32(
        gm: torch.fx.GraphModule,
    ) -> None:
        for node in gm.graph.nodes:
            if node.target != torch.gather:
                continue
            if len(node.args) == 3 and isinstance(node.args[1], int):
                node.target = torch_gather_i32
            else:
                raise NotImplementedError("We don't support this form of torch.gather op yet.")
        gm.recompile()

    replace_gathers_with_gather_i32 = isinstance(
        model,
        (
            furiosa_llm_models.gptj.symbolic.mlperf_submission.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.mlperf_submission_slice.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.paged_attention_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.paged_attention.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.tta_submission.GPTJForCausalLM,
        ),
    )

    if replace_gathers_with_gather_i32:
        # FIXME: do this in PipelineBuilder at aten level and make logic more general.
        # Replace torch.gather ops to make position_ids's dtype i32.
        _replace_torch_gather_with_gather_i32(prefill_model)

        if decode_model:
            _replace_torch_gather_with_gather_i32(decode_model)


class MetaCopyMode(TorchFunctionMode):
    def __init__(self):
        pass

    def _handle_tensor(self, input_tensor: torch.Tensor) -> torch.Tensor:
        return torch.zeros(
            input_tensor.shape, dtype=input_tensor.dtype, layout=input_tensor.layout, device="meta"
        )

    def __torch_function__(self, func, types, args=(), kwargs=None):
        kwargs = kwargs if kwargs else {}

        # clone will get called in Parameter deepcopy
        if func == torch._C._TensorBase.clone:
            to_be_cloned = args[0]
            new_tensor = self._handle_tensor(to_be_cloned)
            return new_tensor
        elif func == torch.Tensor.__deepcopy__:
            assert len(args) == 2 and len(kwargs) == 0
            tensor, memo = args

            if id(tensor) in memo:
                return memo[id(tensor)]

            out = self._handle_tensor(tensor)
            memo[id(tensor)] = out
            return out
        else:
            with torch._C.DisableTorchFunctionSubclass():
                return func(*args, **kwargs)


def _load_params_from_bin_file(
    quantized_model: GraphModule,
    quant_ckpt_file_path: Union[str, os.PathLike],
) -> None:
    mcp.load_qckpt(
        quantized_model, os.fspath(quant_ckpt_file_path), map_location=torch.device("cpu")
    )


def _get_bf16_casted_graph(
    graph: GraphModule,
    quant_config: QuantizationConfig,
) -> GraphModule:
    with tempfile.TemporaryDirectory() as tmp_dir:
        kv_dtype = None
        if quant_config.kv_cache is not None:
            kv_dtype = quant_config.kv_cache.to_qformat()

        quantsim_model = mcp.create_quantsim_model(
            graph,
            dataloader=None,
            output_path=tmp_dir,
            weight_calib_method="AMAX_SYM",
            weight_dtype=quant_config.weight.to_qformat(),
            weight_granularity="channel",
            act_calib_method="AMAX_SYM",
            act_dtype=quant_config.activation.to_qformat(),
            act_granularity="tensor",
            kv_dtype=kv_dtype,
            disable_inout=(True, True),
            weighted_op_emul_dtype="fp64",
        )
        mcp.save_qformat_qparam(quantsim_model, artifacts_out_dir=tmp_dir)
        return mcp.export(quantsim_model, artifacts_dir_path=tmp_dir, save_qckpt=False)


# Borrowed from https://github.com/furiosa-ai/npu-tools/blob/daaed216eb409bc1e84afe0a582b9e417f1d7876/crates/npu-torch-models/pymodels/model_quantize/quant_causal.py
class QuantCausalLM(PreTrainedModel):
    """This is a wrapper class around quantized models to mimic behavior of original model."""

    def __init__(
        self,
        model: PreTrainedModel,
        prefill_graph: GraphModule,
        decode_graph: Optional[GraphModule],
    ):
        # order matters
        _replace_gathers_with_gather_i32(model, prefill_graph, decode_graph)
        self.original_type = type(model)
        super().__init__(model.config)
        self.prefill_model = prefill_graph
        self.decode_model = decode_graph
        self._merge_duplicate_parameters()

    @classmethod
    def from_quant_ckpt(
        cls,
        model: PreTrainedModel,
        prefill_graph: GraphModule,
        decode_graph: Optional[GraphModule],
        qparam_path: Union[str, os.PathLike],
        qformat_path: Union[str, os.PathLike],
        quant_ckpt_file_path: Optional[Union[str, os.PathLike]],
    ):
        # order matters
        original_type = type(model)
        qparam_path = qparam_path
        qformat_path = qformat_path

        need_parameter_load = any(
            t.device == torch.device("meta") for t in chain(model.parameters(), model.buffers())
        )

        logger.info(
            f"Quantizing model: {original_type}, qparam: {qparam_path}, qformat: {qformat_path}"
        )
        start = time()

        with tempfile.TemporaryDirectory() as tmp_dir:
            if decode_graph:
                quantsim_model = mcp.FXGraphCausalLM(original_type, prefill_graph, decode_graph)
            else:
                quantsim_model = prefill_graph

            try:
                qlv2_model = mcp.create_quantsim_model(
                    quantsim_model,
                    qformat_path=os.fspath(qformat_path),
                    qparam_path=os.fspath(qparam_path),
                    qlevel=2,
                    target_machine='RGDA0',
                    decode_phase=False,
                    output_path=tmp_dir,
                )
            except (KeyError, TypeError):
                # Retry with `disable_auto_node_mapping=True`. With this option, model is splitted into layers with model class-specific rules,
                # instead of using general transformer block pattern matching algorithm.
                # This general pattern matching algorithm might doesn't work for the following cases. Auto node mapping should be disabled for them:
                # - model's number of layers (transformer / bert blocks) is smaller than 3.
                # - quantization artifacts for model with larger number of layers is used.
                logger.info(
                    "Failed to quantize with `disable_auto_node_mapping=False`, retry with `disable_auto_node_mapping=True`."
                )
                qlv2_model = mcp.create_quantsim_model(
                    quantsim_model,
                    qformat_path=os.fspath(qformat_path),
                    qparam_path=os.fspath(qparam_path),
                    qlevel=2,
                    target_machine='RGDA0',
                    decode_phase=False,
                    output_path=tmp_dir,
                    disable_auto_node_mapping=True,
                )

            quantized_model = mcp.export(
                qlv2_model,
                artifacts_dir_path=Path(qformat_path).parent,
                save_qckpt=False,
            )

            if decode_graph:
                prefill_model = quantized_model.prefill_model
                decode_model = quantized_model.decode_model
            else:
                prefill_model = quantized_model
                decode_model = None

        if need_parameter_load:
            if quant_ckpt_file_path is None:
                raise ValueError(
                    "`quant_ckpt_file_path` is required when quantization is done by loading quantized parameter directly."
                )
            _load_params_from_bin_file(quantized_model, quant_ckpt_file_path)

        logger.info(f"Quantization done, elapsed: {time() - start:.2f}s")

        return cls(model, prefill_model, decode_model)

    @classmethod
    def get_bf16_casted(
        cls,
        model: PreTrainedModel,
        prefill_graph: GraphModule,
        decode_graph: Optional[GraphModule],
        quant_config: QuantizationConfig,
    ):
        logger.info(f"Quantizing model: {type(model)} for {quant_config}")
        start = time()

        prefill_model = _get_bf16_casted_graph(
            prefill_graph,
            quant_config,
        )
        decode_model = None
        if decode_graph:
            decode_model = _get_bf16_casted_graph(
                decode_graph,
                quant_config,
            )

        logger.info(f"Quantization done, elapsed: {time() - start:.2f}s")

        return cls(model, prefill_model, decode_model)

    def _merge_duplicate_parameters(self) -> None:
        if self.decode_model is None or self.prefill_model is self.decode_model:
            return

        # merge duplicated parameters.
        decode_model_param_and_buffers = dict(
            chain(self.decode_model.named_parameters(), self.decode_model.named_buffers())
        )
        for name, param_in_prefill in tuple(
            chain(self.prefill_model.named_parameters(), self.prefill_model.named_buffers())
        ):
            param_in_decode = decode_model_param_and_buffers.get(name)
            if param_in_decode is None or not param_in_decode.equal(param_in_prefill):
                continue

            # Two param or buffer types should be same.
            assert type(param_in_prefill) is type(param_in_decode)
            splitted = name.rsplit(".", maxsplit=1)
            if len(splitted) == 1:
                submodule = self.decode_model
                final_attr_name = splitted[0]
            else:
                submodule_name, final_attr_name = splitted
                submodule = self.decode_model.get_submodule(submodule_name)  # type: ignore

            # To ensure memory deallocation.
            delattr(submodule, final_attr_name)
            setattr(submodule, final_attr_name, param_in_prefill)

    def _is_prefill(self, kwargs: Mapping[str, Any]) -> bool:
        if self.original_type in (
            furiosa_llm_models.gptj.symbolic.huggingface.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.huggingface_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.preallocated.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.preallocated_concat.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.preallocated_concat_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.huggingface_rope_rngd_gelu.GPTJForCausalLM,
        ):
            return kwargs.get("past_key_values", None) is None
        elif (
            self.original_type
            == furiosa_llm_models.gptj.symbolic.paged_attention_rope.GPTJForCausalLM
        ):
            # paged_attention_rope model has same model for prefill/decode.
            return True
        elif self.original_type in (
            furiosa_llm_models.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.tta_submission.GPTJForCausalLM,
            furiosa_llm_models.llama.symbolic.mlperf_submission.LlamaForCausalLM,
            furiosa_llm_models.llama.symbolic.mlperf_submission_slice.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.mlperf_submission_slice.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.aramco_specdec_slice_integrated.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.llama3.LlamaForCausalLM,
        ):
            # For paged_attention_optimized_packed_rope model, prefill / decode cannot be distinguished with the presence of past_key_values.
            # Instead, past_valid_key_indices can be used.
            return kwargs.get("past_valid_key_indices", None) is None
        elif self.original_type in (
            furiosa_llm_models.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM,
        ):
            return kwargs.get("past_valid_kv_indices", None) is None
        elif self.original_type in (
            furiosa_llm_models.gptj.symbolic.mlperf_submission.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.mlperf_submission_slice.GPTJForCausalLM,
        ):
            return kwargs.get("past_valid_key_prompt_indices", None) is None
        elif self.original_type in (
            furiosa_llm_models.bert.symbolic.mlperf_submission.BertForQuestionAnswering,
            furiosa_llm_models.bert.symbolic.experimental.huggingface_unsplit_packed.BertForQuestionAnswering,
        ):
            return True
        else:
            raise ValueError(f"Invalid model: {self}")

    # Doesn't use kwargs for maintain same signature as original Model. This information will be used for input matching in PipelineBuilder.
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ):
        if self._is_prefill(kwargs):
            output = self.prefill_model(input_ids=input_ids, position_ids=position_ids, **kwargs)
        else:
            output = self.decode_model(input_ids=input_ids, position_ids=position_ids, **kwargs)  # type: ignore
        if return_dict:
            # we assume that this option is only used by huggingface generator and `labels` should be None.
            # output `loss` is None if `labels` is None.
            assert kwargs.get("labels", None) is None
            # First element of `CausalLMOutputWithPast` is loss.
            assert isinstance(output, Sequence)
            return CausalLMOutputWithPast(None, *output)
        else:
            return output

    # Without ``attention_mask=None``, error occurs from ``GenerationMixin``'s unused argument check.
    # https://github.com/huggingface/transformers/blob/d502bd64756535ff6af43cbc5a15aa5da7f52483/src/transformers/generation/utils.py#L1155
    def prepare_inputs_for_generation(self, input_ids, attention_mask=None, **model_kwargs):
        return self.original_type.prepare_inputs_for_generation(
            self, input_ids, attention_mask=attention_mask, **model_kwargs
        )

    def _reorder_cache(
        self, past_key_values: Tuple[Tuple[torch.Tensor]], beam_idx: torch.Tensor
    ) -> Tuple[Tuple[torch.Tensor]]:
        """
        This function is used to re-order the `past_key_values` cache if [`~PretrainedModel.beam_search`] or
        [`~PretrainedModel.beam_sample`] is called. This is required to match `past_key_values` with the correct
        beam_idx at every generation step.
        """
        assert issubclass(self.original_type, PreTrainedModel)
        return self.original_type._reorder_cache(self, past_key_values, beam_idx)

    def can_generate(self):
        return self.original_type.can_generate()


BUCKET_SIZE_ARG_NAME = "bucket_size"


def _get_input_names_and_concrete_args_for_symbolic_trace(
    model: PreTrainedModel,
):
    prefill_concrete_args: Dict[str, Any] = {}
    decode_input_names: Optional[Set[str]] = None
    decode_concrete_args = None

    if isinstance(
        model,
        (
            furiosa_llm_models.gptj.symbolic.huggingface.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.preallocated_concat_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.huggingface_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.huggingface_rope_rngd_gelu.GPTJForCausalLM,
        ),
    ):
        prefill_concrete_args = decode_concrete_args = {
            'return_dict': False,
            'use_cache': True,
            'output_attentions': False,
            'output_hidden_states': False,
        }
        prefill_input_names = {'input_ids', 'attention_mask', 'position_ids'}
        decode_input_names = {*prefill_input_names, 'past_key_values'}
    elif isinstance(model, furiosa_llm_models.gptj.symbolic.paged_attention_rope.GPTJForCausalLM):
        prefill_input_names = {
            'input_ids',
            'past_key_values',
            'position_ids',
            'attention_mask',
            "input_metadata",
        }
        prefill_concrete_args = {
            'use_cache': False,
            'return_dict': False,
            'output_attentions': False,
            'output_hidden_states': False,
        }
    elif isinstance(model, furiosa_llm_models.llama.symbolic.huggingface.LlamaForCausalLM):
        prefill_input_names = {"input_ids"}
        decode_input_names = {*prefill_input_names, "past_key_values"}

        prefill_concrete_args = decode_concrete_args = {
            "return_dict": True,
            "use_cache": True,
            "output_attentions": False,
            "output_hidden_states": False,
        }

    elif isinstance(
        model,
        (
            furiosa_llm_models.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.tta_submission.GPTJForCausalLM,
        ),
    ):
        # `furiosa_llm_models.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM`
        # model has different concrete_args for tracing for prefill and decode mode.
        prefill_input_names_, prefill_concrete_args = model.get_input_names_and_concrete_args(model)
        decode_input_names_, decode_concrete_args = model.get_input_names_and_concrete_args(
            model, prefill_phase=False
        )

        assert isinstance(decode_concrete_args, dict)

        # We want to concretize bucket size after quantization.
        prefill_input_names = set(prefill_input_names_)
        # bucket_size arg is not used when it's prefill phase.
        try:
            prefill_input_names.remove(BUCKET_SIZE_ARG_NAME)
            # This value has no effect.
            prefill_concrete_args[BUCKET_SIZE_ARG_NAME] = 39482
        except KeyError:
            pass

        decode_input_names = set(decode_input_names_)
        decode_input_names.add(BUCKET_SIZE_ARG_NAME)
        decode_concrete_args.pop(BUCKET_SIZE_ARG_NAME, None)
    elif isinstance(
        model,
        (
            furiosa_llm_models.gptj.symbolic.mlperf_submission.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.mlperf_submission_slice.GPTJForCausalLM,
        ),
    ):
        prefill_input_names_, prefill_concrete_args = model.get_input_names_and_concrete_args(model)
        decode_input_names_, decode_concrete_args = model.get_input_names_and_concrete_args(
            model, prefill_phase=False
        )
        prefill_input_names = set(prefill_input_names_)
        decode_input_names = set(decode_input_names_)

        # bucket_size arg is not used when it's prefill phase.
        try:
            prefill_input_names.remove(BUCKET_SIZE_ARG_NAME)
            # This value has no effect.
            prefill_concrete_args[BUCKET_SIZE_ARG_NAME] = 39482
        except KeyError:
            pass

        # due to mypy
        assert isinstance(decode_concrete_args, dict)

        # We want to concretize these arguments after quantization.
        for name in ("num_beam", "max_new_tokens", "num_real_batch", "bucket_size"):
            decode_input_names.add(name)
            decode_concrete_args.pop(name, None)
    elif isinstance(
        model,
        (
            furiosa_llm_models.bert.symbolic.mlperf_submission.BertForQuestionAnswering,
            furiosa_llm_models.bert.symbolic.experimental.huggingface_unsplit_packed.BertForQuestionAnswering,
        ),
    ):
        prefill_input_names = {
            "input_ids",
            "token_type_ids",
            "attention_mask",
            "position_ids",
        }
    elif isinstance(
        model,
        (
            furiosa_llm_models.llama.symbolic.mlperf_submission.LlamaForCausalLM,
            furiosa_llm_models.llama.symbolic.mlperf_submission_slice.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.mlperf_submission_slice.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.aramco_specdec_slice_integrated.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.llama3.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM,
            furiosa_llm_models.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM,
        ),
    ):
        prefill_input_names_, prefill_concrete_args = model.get_input_names_and_concrete_args(model)
        decode_input_names_, decode_concrete_args = model.get_input_names_and_concrete_args(
            model, prefill_phase=False
        )

        # due to mypy
        assert isinstance(decode_concrete_args, dict)
        prefill_input_names = set(prefill_input_names_)
        decode_input_names = set(decode_input_names_)

        # bucket_size arg is not used when it's prefill phase.
        try:
            prefill_input_names.remove(BUCKET_SIZE_ARG_NAME)
            # This value has no effect.
            prefill_concrete_args[BUCKET_SIZE_ARG_NAME] = 39482
        except KeyError:
            pass

        decode_input_names.add(BUCKET_SIZE_ARG_NAME)
        decode_concrete_args.pop(BUCKET_SIZE_ARG_NAME, None)
    else:
        raise ValueError(f"Quantization for {type(model)} model is not supported.")

    return prefill_input_names, prefill_concrete_args, decode_input_names, decode_concrete_args
