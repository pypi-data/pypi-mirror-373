import logging
from pathlib import Path
import tempfile
from typing import Optional, Type, Union

from furiosa_llm_models.generators.v3.base.generator import GeneratorForDecoderOnlyModels
import model_compressor
from optimum.quantization_base import OptimumQuantizer
from torch.utils.data import DataLoader
import transformers
from transformers import (
    AutoConfig,
    AutoTokenizer,
    PretrainedConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
)

from furiosa_llm.optimum.model_configs import find_canonical_model_id
from furiosa_llm.optimum.modeling import (
    FURIOSA_CONFIG_JSON,
    _get_optimization_config,
    get_fx_graphs_for_quant,
    get_generator_cls,
    get_optimized_cls,
    instantiate_model,
    requires_parameter_names_conversion,
)
from furiosa_llm.optimum.transformers import _AutoModelFinder
from furiosa_llm.optimum.types import (
    FuriosaConfig,
    LLMConfig,
    ModelClass,
    ModelKind,
    OptimizationConfig,
    QuantizationConfig,
)

logger = logging.getLogger(__name__)


def trace_hf_rope_llama(model, prefill_input_names=None, decode_input_names=None):
    (
        traced_prefill_model,
        prefill_input_names,
        prefill_concrete_args,
    ) = model_compressor.helper.llama_custom_symbolic_trace(
        model,
        input_names=(
            prefill_input_names
            if prefill_input_names is not None
            else ["input_ids", "attention_mask", "position_ids"]
        ),
        disable_check=True,
    )
    traced_prefill_model.input_names = prefill_input_names
    traced_prefill_model.concrete_args = prefill_concrete_args
    (
        traced_decode_model,
        decode_input_names,
        decode_concrete_args,
    ) = model_compressor.helper.llama_custom_symbolic_trace(
        model,
        input_names=(
            decode_input_names
            if decode_input_names is not None
            else ["input_ids", "past_key_values", "attention_mask", "position_ids"]
        ),
        disable_check=True,
    )
    traced_decode_model.input_names = decode_input_names
    traced_decode_model.concrete_args = decode_concrete_args
    return traced_prefill_model, traced_decode_model


class _FuriosaBaseQuantizer(_AutoModelFinder, OptimumQuantizer):
    def __init__(
        self,
        canonical_model_id: str,
        model: PreTrainedModel,
        config: PretrainedConfig,
        original_model_cls: Type[PreTrainedModel],
        optimized_model_cls: Type[PreTrainedModel],
        generator_cls: Type[GeneratorForDecoderOnlyModels],
        optimization_config: OptimizationConfig,
        tokenizer: PreTrainedTokenizer,
        parameter_conversion_map: Optional[dict] = None,
    ):
        self.canonical_model_id = canonical_model_id
        self.model = model
        self.config = config
        self.original_model_cls = original_model_cls
        self.optimized_model_cls = optimized_model_cls
        self.generator_cls = generator_cls
        self.tokenizer = tokenizer
        self.optimization_config = optimization_config
        self.parameter_conversion_map = parameter_conversion_map

    @classmethod
    def from_pretrained(
        cls,
        model_name_or_path: Union[str, Path],
        config: Optional[PretrainedConfig] = None,
        *,
        use_only_beam_search: bool = False,
        **kwargs,
    ):
        """
        Instantiate a quantizer from a pre-trained model.

        Args:
            model_name_or_path: The model id or path to the pre-trained model.
            config: The configuration of the model.
            use_only_beam_search: If True, the quantizer will apply an optimization for only beam search
                to the model. It forces to allow only beam search rather than using both beam search and
                top-k sampling.
            compute_logit_for_last_token: If True, the model will compute only the logits for the last token.
                It's effective when the model is chosen for generative tasks.
            **kwargs: Additional keyword arguments.
        """
        if config is None:
            config = AutoConfig.from_pretrained(
                model_name_or_path,
                **kwargs,
            )
        tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            **kwargs,
        )

        canonical_model_id = find_canonical_model_id(config)
        if canonical_model_id is None:
            raise ValueError(f"FuriosaQuantizer doesn't support {type(config)} for quantization")

        try:
            model_cls = cls.find_model_class(model_name_or_path, config, **kwargs)
        except ValueError:
            raise ValueError(f"FuriosaQuantizer doesn't support {type(config)} for quantization")

        # OptimizationConfig is only for internal use. We expect OptimizationConfig to be passed
        # from furiosa-llm, and we don't expect users to pass it.
        optimization_config = kwargs.pop("optimization_config", None)
        if optimization_config is None:
            optimization_config = _get_optimization_config(
                model_cls,
                canonical_model_id,
                use_only_beam_search=use_only_beam_search,
            )

        optimized_model_cls = get_optimized_cls(
            canonical_model_id,
            model_cls,
            optimization_config,
        )

        assert isinstance(config, PretrainedConfig)

        need_param_name_conversion = requires_parameter_names_conversion(model_cls)
        model, parameter_name_conversion_map = instantiate_model(
            model_name_or_path,
            optimized_model_cls,
            config,
            optimization_config,
            need_param_name_conversion,
            **kwargs,
        )

        generator_cls = get_generator_cls(optimized_model_cls)

        return cls(
            canonical_model_id,
            model,
            config,
            model_cls,
            optimized_model_cls,
            generator_cls,
            optimization_config,
            tokenizer,
            parameter_name_conversion_map,
        )

    def quantize(
        self,
        save_dir: Union[str, Path],
        dataloader: DataLoader,
        quantization_config: QuantizationConfig,
        file_prefix: Optional[str] = None,
        **kwargs,
    ):
        """
        Quantizes the model and saves the quantized model, qformat, qparam, config.json, vocab.json, and tokenizer.json.

        Args:
            save_dir: The directory to save the quantized model.
            dataloader: The dataloader for calibration.
            quantization_config: The quantization configuration.
            file_prefix: The prefix for the saved files.
            **kwargs: Additional keyword arguments.
        """

        temp_dir = kwargs.pop("temp_dir", None)
        if temp_dir is None:
            _tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
            temp_dir = _tempdir.name

        prefill_graph, decode_graph = get_fx_graphs_for_quant(
            self.model,
        )

        logger.info("Tracing done.")

        hf_model_trace = model_compressor.FXGraphCausalLM(
            type(self.model), prefill_graph, decode_graph, self.generator_cls, used_dynamo=True
        )

        disable_inout = (True, True)
        weight_calib_method = "AMAX_SYM"
        weight_dtype = quantization_config.weight.to_qformat()
        weight_granularity = "channel"
        act_dtype = quantization_config.activation.to_qformat()
        act_calib_method = "AMAX_SYM"
        act_granularity = "channel"
        kv_dtype = None
        if quantization_config.kv_cache is not None:
            kv_dtype = quantization_config.kv_cache.to_qformat()
        weighted_op_emul_dtype = "fp64"
        model_specific_kwargs = {"set_pow_dtype_to_bf16": False}

        quantsim_model = model_compressor.create_quantsim_model(
            hf_model_trace,
            dataloader=dataloader,
            output_path=save_dir,
            weight_calib_method=weight_calib_method,
            weight_dtype=weight_dtype,
            weight_granularity=weight_granularity,
            act_calib_method=act_calib_method,
            act_dtype=act_dtype,
            act_granularity=act_granularity,
            kv_dtype=kv_dtype,
            disable_inout=disable_inout,
            weighted_op_emul_dtype=weighted_op_emul_dtype,
            **model_specific_kwargs,
        )

        logger.info("Quantsim model creation done.")

        quantsim_model = model_compressor.calibrate(
            quantsim_model,
            model_type=type(self.model),
            enable_multi_gpu=False,
            ckpt_folder_path=save_dir,
            ckpt_to_state_key_map=self.parameter_conversion_map,
            use_dynamo_export=True,
        )

        logger.info("Calibration done.")

        # Saves the quantized parameters
        model_compressor.export(quantsim_model, artifacts_dir_path=save_dir, save_qckpt=True)

        # Save config.json, vocab.json, and tokenizer.json
        self.config.save_pretrained(save_dir)
        self.tokenizer.save_pretrained(save_dir)

        furiosa_config = FuriosaConfig(
            model_id=self.canonical_model_id,
            model_kinds=[ModelKind.QUANTIZED_MODEL],
            model_class=ModelClass.from_class(self.optimized_model_cls),
            llm_config=LLMConfig(self.optimization_config, quantization_config),
        )

        furiosa_config_json_path = Path(save_dir) / FURIOSA_CONFIG_JSON
        furiosa_config.export(furiosa_config_json_path)


class QuantizerForCausalLM(_FuriosaBaseQuantizer):
    _model_mapping = transformers.MODEL_FOR_CAUSAL_LM_MAPPING
    _auto_model_cls = transformers.AutoModelForCausalLM


class QuantizerForQuestionAnswering(_FuriosaBaseQuantizer):
    _model_mapping = transformers.MODEL_FOR_QUESTION_ANSWERING_MAPPING
    _auto_model_cls = transformers.AutoModelForQuestionAnswering
