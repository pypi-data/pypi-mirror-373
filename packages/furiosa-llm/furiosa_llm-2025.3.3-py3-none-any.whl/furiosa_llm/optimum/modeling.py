import contextlib
from contextlib import AbstractContextManager, ExitStack, contextmanager
import copy
import functools
import logging
import os
from pathlib import Path
from typing import (
    Any,
    ContextManager,
    Dict,
    Final,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)
from unittest.mock import patch
import warnings

import accelerate
import furiosa_llm_models as flm
from furiosa_llm_models.generators.v3.base.generator import GeneratorForDecoderOnlyModels
from furiosa_llm_models.llama3.symbolic.utils import LlamaBasedModelConverter
import furiosa_models
from furiosa_models.architecture.models.serve import (
    CausalModelServer,
)
from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE
from optimum.modeling_base import OptimizedModel
import torch
from torch._dynamo.utils import deepcopy_to_fake_tensor
from torch._subclasses.fake_tensor import FakeTensorMode
from torch.fx import GraphModule
import transformers
from transformers import LlamaConfig, PretrainedConfig, PreTrainedModel

from furiosa_llm.models.config_types import Bucket
from furiosa_llm.models.quant import (
    QuantCausalLM,
    _get_input_names_and_concrete_args_for_symbolic_trace,
    fx_symbolic_trace_model,
)
from furiosa_llm.models.utils import generate_input_sample
from furiosa_llm.optimum.model_configs import find_canonical_model_id
from furiosa_llm.optimum.transformers import _AutoModelFinder
from furiosa_llm.optimum.types import (
    AttentionType,
    FuriosaConfig,
    OptimizationConfig,
    QuantizationConfig,
)

_WARNINGS_TO_IGNORE = [
    ".*copying from a non-meta parameter in the checkpoint to a meta parameter in the current model, which is a no-op..*",
]

FURIOSA_CONFIG_JSON = "furiosa_config.json"
_QFORMAT_YAML = "qformat.yaml"
_QPARAM_NPY = "qparam.npy"
_EXPORTED_MODEL_QCKPT = "exported_model.qckpt"


# Pretrained model IDs
FURIOSA_EXAONE3_7D8B_INSTRUCT_PRETRAINED_ID: Final[str] = (
    "furiosa-ai/EXAONE-3.0-7.8B-Instruct-converted"
)
EXAONE3_7D8B_INSTRUCT_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-3.0-7.8B-Instruct"
EXAONE3_5_2D4B_INSTRUCT_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
EXAONE3_5_7D8B_INSTRUCT_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
EXAONE3_5_32B_INSTRUCT_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-3.5-32B-Instruct"
EXAONE_DEEP_2_4B_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-Deep-2.4B"
EXAONE_DEEP_7_8B_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-Deep-7.8B"
EXAONE_DEEP_32B_PRETRAINED_ID: Final[str] = "LGAI-EXAONE/EXAONE-Deep-32B"

GPT_2_PRETRAINED_ID: Final[str] = "gpt2"
GPT_NEO_PRETRAINED_ID: Final[str] = "EleutherAI/gpt-neo-125m"
GPT_J_PRETRAINED_ID: Final[str] = "EleutherAI/gpt-j-6B"

MLPERF_BERT_LARGE_PRETRAINED_ID: Final[str] = "furiosa-ai/mlperf-bert-large"
MLPERF_GPTJ_PRETRAINED_ID: Final[str] = "furiosa-ai/mlperf-gpt-j-6b"

CODE_LLAMA_7B_PRETRAINED_ID: Final[str] = "meta-llama/CodeLlama-7b-hf"
CODE_LLAMA_7B_INSTRUCT_PRETRAINED_ID: Final[str] = "meta-llama/CodeLlama-7b-Instruct-hf"
CODE_LLAMA_13B_PRETRAINED_ID: Final[str] = "meta-llama/CodeLlama-13b-hf"
CODE_LLAMA_13B_INSTRUCT_PRETRAINED_ID: Final[str] = "meta-llama/CodeLlama-13b-Instruct-hf"
LLAMA_7B_PRETRAINED_ID: Final[str] = "huggyllama/llama-7b"
LLAMA2_70B_CHAT_PRETRAINED_ID: Final[str] = "meta-llama/Llama-2-70b-chat-hf"
LLAMA3_1_8B_PRETRAINED_ID: Final[str] = "meta-llama/Llama-3.1-8B"
LLAMA3_1_70B_PRETRAINED_ID: Final[str] = "meta-llama/Llama-3.1-70B"
LLAMA3_1_8B_INSTRUCT_PRETRAINED_ID: Final[str] = "meta-llama/Llama-3.1-8B-Instruct"
LLAMA3_1_70B_INSTRUCT_PRETRAINED_ID: Final[str] = "meta-llama/Llama-3.1-70B-Instruct"
LLAMA3_3_70B_INSTRUCT_PRETRAINED_ID: Final[str] = "meta-llama/Llama-3.3-70B-Instruct"

LLAMA3_1_8B_ELICEAI_HELPY_EDU_B_PRETRAINED_ID: Final[str] = "eliceai/helpy-edu-b-llama3.1"

SOLAR_10D7B_INSTRUCT_PRETRAINED_ID: Final[str] = "upstage/SOLAR-10.7B-Instruct-v1.0"
SOLAR_ENKOJA_10D7B_32K_1_3_PRETRAINED_ID: Final[str] = (
    "UpstageShareFuriosaAI/solar-lnc-enkoja-10.7b-32k-1.3.0-chat.2"
)

DEEPSEEK_R1_DISTILL_LLAMA_8B_PRETRAINED_ID: Final[str] = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
DEEPSEEK_R1_DISTILL_LLAMA_70B_PRETRAINED_ID: Final[str] = (
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
)
DEEPSEEK_R1_DISTILL_QWEN_7B_PRETRAINED_ID: Final[str] = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
DEEPSEEK_R1_DISTILL_QWEN_14B_PRETRAINED_ID: Final[str] = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
DEEPSEEK_R1_DISTILL_QWEN_32B_PRETRAINED_ID: Final[str] = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

QWQ_32B_PRETRAINED_ID: Final[str] = "Qwen/QwQ-32B"
QWEN_2_5_3B_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-3B"
QWEN_2_5_7B_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-7B"
QWEN_2_5_14B_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-14B"
QWEN_2_5_32B_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-32B"
QWEN_2_5_3B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-3B-Instruct"
QWEN_2_5_7B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-7B-Instruct"
QWEN_2_5_14B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-14B-Instruct"
QWEN_2_5_32B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-32B-Instruct"
QWEN_2_5_CODER_7B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-Coder-7B-Instruct"
QWEN_2_5_CODER_14B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-Coder-14B-Instruct"
QWEN_2_5_CODER_32B_INSTRUCT_PRETRAINED_ID: Final[str] = "Qwen/Qwen2.5-Coder-32B-Instruct"

# The LLAMA3_BASED_* constants below are used to identify whether a model is Llama3-based. A model
# is considered Llama3-based if (1) its type is in LLAMA3_BASED_MODEL_TYPES, (2) its config type is
# in LLAMA3_BASED_MODEL_CONFIG_TYPES, or (3) its model ID is in LLAMA3_BASED_MODEL_IDS. For more
# details, refer to the implementation of the is_llama3_based function.
#
# Why do these three constants exist? Some models have unique model types or config types that
# clearly categorize them as Llama3-based, which is handled by LLAMA3_BASED_MODEL_TYPES and
# LLAMA3_BASED_MODEL_CONFIG_TYPES. However, other models use LlamaForCausalLM and LlamaConfig, which
# are shared by both Llama2- and Llama3-based models. In these cases, we rely on the model's ID to
# determine if it is Llama3-based, which is handled by LLAMA3_BASED_MODEL_IDS.
LLAMA3_BASED_MODEL_TYPES: Final[Set[str]] = {
    "ExaoneForCausalLM",
}
LLAMA3_BASED_MODEL_CONFIG_TYPES: Final[Set[str]] = {"ExaoneConfig"}
LLAMA3_BASED_MODEL_IDS: Final[Set[str]] = {
    LLAMA3_1_8B_INSTRUCT_PRETRAINED_ID,
    LLAMA3_1_70B_INSTRUCT_PRETRAINED_ID,
    LLAMA3_3_70B_INSTRUCT_PRETRAINED_ID,
    LLAMA3_1_8B_PRETRAINED_ID,
    LLAMA3_1_70B_PRETRAINED_ID,
    LLAMA3_1_8B_ELICEAI_HELPY_EDU_B_PRETRAINED_ID,
    FURIOSA_EXAONE3_7D8B_INSTRUCT_PRETRAINED_ID,
    DEEPSEEK_R1_DISTILL_LLAMA_8B_PRETRAINED_ID,
    DEEPSEEK_R1_DISTILL_LLAMA_70B_PRETRAINED_ID,
    SOLAR_ENKOJA_10D7B_32K_1_3_PRETRAINED_ID,
}

"""List of canonical model IDs which the minimum unique set of supported models"""
# Keep the minimum set of base model IDs in alphabetical order.
CANONICAL_MODEL_IDS: Final[List[str]] = [
    CODE_LLAMA_7B_PRETRAINED_ID,
    EXAONE3_5_2D4B_INSTRUCT_PRETRAINED_ID,
    EXAONE3_5_7D8B_INSTRUCT_PRETRAINED_ID,
    EXAONE3_5_32B_INSTRUCT_PRETRAINED_ID,
    # EXAONE4_0_32B_PRETRAINED_ID,
    LLAMA2_70B_CHAT_PRETRAINED_ID,
    LLAMA3_1_8B_PRETRAINED_ID,
    LLAMA3_1_70B_PRETRAINED_ID,
    MLPERF_BERT_LARGE_PRETRAINED_ID,
    MLPERF_GPTJ_PRETRAINED_ID,
    SOLAR_10D7B_INSTRUCT_PRETRAINED_ID,
    SOLAR_ENKOJA_10D7B_32K_1_3_PRETRAINED_ID,
    QWEN_2_5_3B_PRETRAINED_ID,
    QWEN_2_5_7B_PRETRAINED_ID,
    QWEN_2_5_14B_PRETRAINED_ID,
    QWEN_2_5_32B_PRETRAINED_ID,
]


# FIXME: there exists a gptj_rope_packed_rngd_gelu model and it differs from mlperf_submission
MODEL_CLS_TO_MLPERF_OPT_CONFIGS = {
    transformers.GPTJForCausalLM: OptimizationConfig(
        attention_type=AttentionType.PAGED_ATTENTION,
        optimize_rope=True,
        optimize_packed=True,
        use_rngd_gelu=True,
        kv_cache_sharing_across_beams=True,
        causal_mask_free_decoding=True,
        inbound_beamsearch_softmax=True,
    ),
    transformers.LlamaForCausalLM: OptimizationConfig(
        attention_type=AttentionType.PAGED_ATTENTION,
        optimize_rope=True,
        optimize_packed=True,
        causal_mask_free_decoding=True,
    ),
    transformers.Qwen2ForCausalLM: OptimizationConfig(
        attention_type=AttentionType.PAGED_ATTENTION,
        optimize_rope=True,
        optimize_packed=True,
        causal_mask_free_decoding=True,
        optimized_for_speculative_decoding=True,
    ),
    transformers.BertForQuestionAnswering: OptimizationConfig(
        use_unsplit_packed=True,
        use_rngd_gelu=True,
    ),
}

OPTIMIZATION_CONFIG_MAPPER = {
    "use_only_beam_search": "kv_cache_sharing_across_beams",
}


# borrowed and modified from https://github.com/furiosa-ai/model-compressor-release-test/blob/9cb475d8c6120c00edba12ff455913187aafd7d0/tests/utils/helper_functions.py#L582.
MODEL_CLS_TO_GENERATOR_CLS: Final[
    Dict[Type[PreTrainedModel], Type[GeneratorForDecoderOnlyModels]]
] = {
    flm.llama3.symbolic.mlperf_submission.LlamaForCausalLM: flm.generators.v3.paged_attention.Generator,
    flm.llama.symbolic.mlperf_submission.LlamaForCausalLM: flm.generators.v3.paged_attention.Generator,
    flm.gptj.symbolic.tta_submission.GPTJForCausalLM: flm.generators.v3.paged_attention.Generator,
    flm.gptj.symbolic.mlperf_submission.GPTJForCausalLM: flm.generators.v3.paged_attention.MLPerfSubmissionGenerator,
    # flm.bert.symbolic.mlperf_submission.BertForQuestionAnswering: flm.encoders.bert_encoder.BertUnsplitPackedEncoder,
}


def is_mlperf_optimized(model_cls: Type, optimization_config: OptimizationConfig) -> bool:
    if mlperf_option := MODEL_CLS_TO_MLPERF_OPT_CONFIGS.get(model_cls):
        return optimization_config == mlperf_option
    return False


def contains_mlperf_opts(model_cls: Type, optimization_config: OptimizationConfig) -> bool:
    if mlperf_option := MODEL_CLS_TO_MLPERF_OPT_CONFIGS.get(model_cls):
        return (
            optimization_config.get_enabled_opts().issuperset(mlperf_option.get_enabled_opts())
            and optimization_config.attention_type == mlperf_option.attention_type
        )
    return False


def is_mlperf_optimized_with(
    model_cls: Type, optimization_config: OptimizationConfig, **kwargs
) -> bool:
    if mlperf_option := MODEL_CLS_TO_MLPERF_OPT_CONFIGS.get(model_cls):
        copied = copy.deepcopy(mlperf_option)
        for k, v in kwargs.items():
            setattr(copied, k, v)
        return optimization_config == copied
    return False


def is_llama3_based(
    pretrained_id: str, model_or_config_cls: Union[Type[PreTrainedModel], Type[PretrainedConfig]]
) -> bool:
    if pretrained_id in LLAMA3_BASED_MODEL_IDS:
        return True
    if issubclass(model_or_config_cls, PreTrainedModel):
        return model_or_config_cls.__qualname__ in LLAMA3_BASED_MODEL_TYPES
    if issubclass(model_or_config_cls, PretrainedConfig):
        return model_or_config_cls.__qualname__ in LLAMA3_BASED_MODEL_CONFIG_TYPES
    return False


def is_generative_model(model_cls: Type[PreTrainedModel]) -> bool:
    return model_cls in transformers.MODEL_FOR_CAUSAL_LM_MAPPING.values()


def update_config_inplace(
    pretrained_id: str, config: PretrainedConfig, optimization_config: OptimizationConfig
) -> None:
    """Update PretrainedConfig inplace for an optimized class"""
    # NOTE: this function might be called multiple times for one model's config.
    # Make sure config is in intended state after arbitrary number of updates.

    # Apply this update to only models that use LlamaConfig.
    # Models that use its own config type (e.g., Exaone) will go through this conversion inside `from_huggingface` method.
    if (
        is_llama3_based(pretrained_id, type(config))
        and type(config) is transformers.LlamaConfig
        and getattr(config, "rope_scaling", None)
        and not getattr(config, "inv_freq_config", None)
    ):
        # FIXME: This is needed because furiosa-llm-models llama3 model cannot accept
        # the config as it is.
        config.inv_freq_config = config.rope_scaling
        config.rope_scaling = None

    # This is a workaround to make model with decomposed layernorm distinguishable after instantiation.
    if optimization_config.decompose_layernorm:
        config.decompose_layernorm = True


class DecomposedLayerNorm(torch.nn.Module):
    def __init__(self, hidden_size, eps=1e-5):
        """
        Decomposed torch.nn.LayerNorm for efficient chip2chip communication by decomposing in more smaller units.
        This is only available for inference.
        """
        super().__init__()
        self.weight = torch.nn.Parameter(torch.ones(hidden_size))
        self.bias = torch.nn.Parameter(torch.zeros(hidden_size))
        self.variance_epsilon = eps
        self.hidden_size = hidden_size

    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        mean = hidden_states.mean(-1, keepdim=True)
        pow_mean = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = (
            self.weight
            * (hidden_states - mean)
            * torch.rsqrt(pow_mean - mean.pow(2) + self.variance_epsilon)
            + self.bias
        )

        return hidden_states.to(input_dtype)


@contextmanager
def replace_layernorm(temp_layernorm):
    original_layernorm = torch.nn.LayerNorm
    torch.nn.LayerNorm = temp_layernorm  # type: ignore
    try:
        yield
    finally:
        torch.nn.LayerNorm = original_layernorm  # type: ignore


# To suppress verbose but not important warnings
class MCPLogFilter(logging.Filter):
    def filter(self, record):
        return (
            "torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction is enabled. \
                This optimization may affect performance."
            not in record.msg
        )


_cqm_logger = logging.getLogger("create_quantsim_model")
_cqm_logger.addFilter(MCPLogFilter())


logger = logging.getLogger(__name__)


def apply_warning_filters():
    warnings.simplefilter(action='ignore', category=FutureWarning)
    for warning_to_ignore in _WARNINGS_TO_IGNORE:
        warnings.filterwarnings(action="ignore", message=warning_to_ignore, append=True)


def get_mapped_class_for_optimization(
    original: Type[PreTrainedModel], canonical_model_id: str
) -> Type[PreTrainedModel]:
    """Some models share other model's optimized class in furiosa-llm-models
    because their architectures are essentially same.
    """
    if original.__qualname__ == "ExaoneForCausalLM":
        return transformers.LlamaForCausalLM

    return original


def _get_default_optimization_config(
    model_cls: Type[PreTrainedModel], pretrained_id: str
) -> OptimizationConfig:
    model_cls = get_mapped_class_for_optimization(model_cls, pretrained_id)

    if optim_options := MODEL_CLS_TO_MLPERF_OPT_CONFIGS.get(model_cls):
        return optim_options
    else:
        return OptimizationConfig()


def _get_optimization_config(
    model_cls: Type[PreTrainedModel], pretrained_id: str, **kwargs
) -> OptimizationConfig:
    optimization_config = _get_default_optimization_config(model_cls, pretrained_id)

    overridden_config: Dict[str, Any] = {}
    for k in OPTIMIZATION_CONFIG_MAPPER.keys():
        if k in kwargs:
            v = OPTIMIZATION_CONFIG_MAPPER[k]
            overridden_config[v] = kwargs.pop(k)

    return optimization_config.with_optimizations(overridden_config)


def is_model_path(model_id: Union[str, os.PathLike]) -> bool:
    return (
        isinstance(model_id, os.PathLike)
        or model_id.startswith("/")
        or model_id.startswith(".")
        or Path(model_id).exists()
    )


def is_quantized_model_path(model_id: Union[str, Path]) -> bool:
    return is_model_path(model_id) and (Path(model_id) / FURIOSA_CONFIG_JSON).exists()


def get_optimized_cls(
    canonical_model_id: str,
    model_cls: Type[PreTrainedModel],
    optimization_config: OptimizationConfig,
) -> Type[torch.nn.Module]:

    import furiosa_llm_models as flm

    # If no optimization is enabled, return the original model class.
    if not optimization_config.get_enabled_opts():
        return model_cls

    is_llama3_based_model = is_llama3_based(canonical_model_id, model_cls)

    model_cls = get_mapped_class_for_optimization(model_cls, canonical_model_id)

    if model_cls is transformers.BertForQuestionAnswering:
        if is_mlperf_optimized(model_cls, optimization_config):
            return flm.bert.symbolic.mlperf_submission.BertForQuestionAnswering
        elif optimization_config.compact_causal_mask:
            return (
                flm.bert.symbolic.experimental.huggingface_unsplit_packed.BertForQuestionAnswering
            )
        elif optimization_config.optimize_furiosa:
            return flm.bert.symbolic.huggingface.BertForQuestionAnswering
        else:
            raise ValueError(
                f"Unsupported bert model: pretrained_id={canonical_model_id}, model_cls={model_cls}, optimization_config={optimization_config}"
            )
    elif model_cls is transformers.LlamaForCausalLM:
        if is_mlperf_optimized(model_cls, optimization_config):
            if is_llama3_based_model:
                return flm.llama3.symbolic.mlperf_submission.LlamaForCausalLM
            else:
                return flm.llama.symbolic.mlperf_submission.LlamaForCausalLM
        elif is_mlperf_optimized_with(
            model_cls, optimization_config, calculate_logit_only_for_last_token=True
        ):
            if is_llama3_based_model:
                return flm.llama3.symbolic.mlperf_submission_slice.LlamaForCausalLM
            else:
                return flm.llama.symbolic.mlperf_submission_slice.LlamaForCausalLM
        elif (
            is_mlperf_optimized_with(
                model_cls,
                optimization_config,
                optimized_for_speculative_decoding=True,
            )
            and is_llama3_based_model
        ):
            return flm.llama3.symbolic.aramco_specdec.LlamaForCausalLM
        elif (
            is_mlperf_optimized_with(
                model_cls,
                optimization_config,
                calculate_logit_only_for_last_token=True,
                optimized_for_speculative_decoding=True,
            )
            and is_llama3_based_model
        ):
            return flm.llama3.symbolic.aramco_specdec_slice_integrated.LlamaForCausalLM
        elif (
            is_mlperf_optimized_with(
                model_cls,
                optimization_config,
                optimized_for_speculative_decoding=True,
                use_2d_masks=True,
            )
            and is_llama3_based_model
        ):
            return flm.llama3.symbolic.llama3.LlamaForCausalLM
        elif is_mlperf_optimized_with(
            model_cls,
            optimization_config,
            optimized_for_speculative_decoding=True,
            merged_kv_indices=True,
        ):
            return flm.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM
        elif is_mlperf_optimized_with(
            model_cls,
            optimization_config,
            optimized_for_speculative_decoding=True,
            use_2d_masks=True,
            merged_kv_indices=True,
        ):
            return flm.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM
        else:
            raise ValueError(
                f"Unsupported llama model: pretrained_id={canonical_model_id}, model_cls={model_cls}, optimization_config={optimization_config}"
            )
    elif model_cls is transformers.GPTJForCausalLM:
        optim_options = optimization_config
        assert not optim_options.use_unsplit_packed, "Unsplit packed is not supported for GPT-J"
        if is_mlperf_optimized(model_cls, optimization_config):
            return flm.gptj.symbolic.mlperf_submission.GPTJForCausalLM
        elif is_mlperf_optimized_with(
            model_cls, optimization_config, calculate_logit_only_for_last_token=True
        ):
            return flm.gptj.symbolic.mlperf_submission_slice.GPTJForCausalLM
        elif is_mlperf_optimized_with(
            model_cls, optimization_config, kv_cache_sharing_across_beams=False
        ):
            return flm.gptj.symbolic.tta_submission.GPTJForCausalLM

        # fmt: off
        self_to_cls: Dict[Tuple[AttentionType,FrozenSet[str]],Type[PreTrainedModel]] = {
            (AttentionType.VANILLA, frozenset(("optimize_furiosa",))): flm.gptj.symbolic.huggingface.GPTJForCausalLM,
            (AttentionType.VANILLA, frozenset(("decompose_layernorm",))): transformers.GPTJForCausalLM,
            (AttentionType.VANILLA, frozenset()): transformers.GPTJForCausalLM,
            (AttentionType.VANILLA, frozenset(("optimize_rope",))): flm.gptj.symbolic.huggingface_rope.GPTJForCausalLM,
            (AttentionType.VANILLA, frozenset(("optimize_rope", "use_rngd_gelu"))): flm.gptj.symbolic.huggingface_rope_rngd_gelu.GPTJForCausalLM,
            (AttentionType.PREALLOCATION_CONCAT, frozenset()): flm.gptj.symbolic.preallocated_concat.GPTJForCausalLM,
            (AttentionType.PREALLOCATION_CONCAT, frozenset(("optimize_rope",))): flm.gptj.symbolic.preallocated_concat_rope.GPTJForCausalLM,
            (AttentionType.PAGED_ATTENTION, frozenset(("optimize_rope",))): flm.gptj.symbolic.paged_attention_rope.GPTJForCausalLM,
            (AttentionType.PAGED_ATTENTION, frozenset(("optimize_rope", "optimize_packed", "causal_mask_free_decoding"))): flm.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM,
        }
        # fmt: on
        assert set(key for keys in self_to_cls.keys() for key in keys[1]).issubset(
            OptimizationConfig().model_dump().keys()
        )

        if cls_ := self_to_cls.get(
            (optim_options.attention_type, optimization_config.get_activated_options())
        ):
            return cls_
        else:
            raise ValueError(
                f"Unsupported model: pretrained_id={canonical_model_id}, model_cls={model_cls}, optimization_config={optimization_config}"
            )
    elif model_cls is transformers.Qwen2ForCausalLM:
        if is_mlperf_optimized(model_cls, optimization_config):
            return furiosa_models.Qwen2ForCausalLM
        else:
            raise ValueError(
                f"Unsupported model: pretrained_id={canonical_model_id}, model_cls={model_cls}, optimization_config={optimization_config}"
            )

    return model_cls


def get_generator_cls(model_cls: Type[PreTrainedModel]) -> Type[GeneratorForDecoderOnlyModels]:
    if generator_cls := MODEL_CLS_TO_GENERATOR_CLS.get(model_cls):
        return generator_cls
    raise ValueError(f"Failed to find generator class for model class: {model_cls}")


def _load_quantized_model_meta(
    path: Path,
) -> Tuple[FuriosaConfig, Path, Path, Path]:
    furiosa_config_file = path / FURIOSA_CONFIG_JSON
    qformat_path = path / _QFORMAT_YAML
    qparam_path = path / _QPARAM_NPY
    quant_ckpt_file_path = path / _EXPORTED_MODEL_QCKPT

    furiosa_config: FuriosaConfig = FuriosaConfig.load(furiosa_config_file)

    return (
        furiosa_config,
        qformat_path,
        qparam_path,
        quant_ckpt_file_path,
    )


def requires_parameter_names_conversion(model_cls: Type[PreTrainedModel]) -> bool:
    return model_cls.__qualname__ == "ExaoneForCausalLM"


def convert_exaone_config_to_llama_config(original_config: PretrainedConfig) -> LlamaConfig:
    if type(original_config).__qualname__ != "ExaoneConfig":
        raise ValueError("`original_config` is not an exaone config.")
    # borrowed from `furiosa_llm_models.llama3.symbolic.mlperf_submission.LlamaForCausalLM.from_huggingface`
    # https://github.com/furiosa-ai/furiosa-llm-models/blob/702cc4ba4209f02a452e49cef5afdf89d7d8af34/furiosa_llm_models/llama3/symbolic/mlperf_submission.py#L823
    # TODO: make this conversion as an independent method in furiosa-llm-models and use it.
    new_exaone_config = LlamaConfig(
        vocab_size=original_config.vocab_size,
        hidden_size=original_config.hidden_size,
        intermediate_size=original_config.intermediate_size,
        num_hidden_layers=original_config.num_layers,
        num_attention_heads=original_config.num_attention_heads,
        max_position_embeddings=original_config.max_position_embeddings,
        rms_norm_eps=original_config.layer_norm_epsilon,
        num_key_value_heads=original_config.num_key_value_heads,
        rope_theta=original_config.rope_theta,
        bos_token_id=original_config.bos_token_id,
        eos_token_id=original_config.eos_token_id,
        pad_token_id=original_config.pad_token_id,
        attention_bias=False,
    )
    new_exaone_config.architectures = ["LlamaForCausalLM"]
    new_exaone_config.torch_dtype = original_config.torch_dtype

    # Furiosa specific: we currently utilize inv_freq_config for rope scaling
    if new_exaone_config.rope_scaling is not None:
        new_exaone_config.inv_freq_config = new_exaone_config.rope_scaling
        new_exaone_config.rope_scaling = None

    return new_exaone_config


def convert_config_for_optimized_cls(
    original_config: PretrainedConfig, optimized_cls: Type[PreTrainedModel]
) -> PretrainedConfig:
    if (
        type(original_config).__qualname__ == "ExaoneConfig"
        and optimized_cls.__qualname__ == "LlamaForCausalLM"
    ):
        return convert_exaone_config_to_llama_config(original_config)
    raise ValueError(f"Cannot convert config of type {original_config} for {type(optimized_cls)}")


@contextmanager
def set_default_torch_dtype(
    dtype: torch.dtype,
):
    original_dtype = PreTrainedModel._set_default_torch_dtype(dtype)
    try:
        yield
    finally:
        PreTrainedModel._set_default_torch_dtype(original_dtype)


def _load_from_pretrained(
    model_id_or_path: Union[str, os.PathLike],
    optimized_cls: Type[torch.nn.Module],
    config: PretrainedConfig,
    need_param_name_conversion: bool,
    torch_dtype: Optional[Union[str, torch.dtype]] = None,
    **kwargs,
) -> Tuple[torch.nn.Module, Optional[Dict[str, str]]]:
    if issubclass(optimized_cls, PreTrainedModel):
        optimized_cls = cast(Type[PreTrainedModel], optimized_cls)
        # Model is from transformers or furiosa-llm-models.
        if torch_dtype:
            torch_dtype = (
                getattr(torch, torch_dtype) if isinstance(torch_dtype, str) else torch_dtype
            )
            assert isinstance(torch_dtype, torch.dtype)
            default_dtype_context: AbstractContextManager = set_default_torch_dtype(torch_dtype)
        else:
            default_dtype_context = contextlib.nullcontext()

        with default_dtype_context:
            if need_param_name_conversion:
                if kwargs.pop("low_cpu_mem_usage", None):
                    logger.warning(
                        "`low_cpu_mem_usage` option cannot be used for models that need parameter name conversion. It's ignored."
                    )

                assert issubclass(optimized_cls, LlamaBasedModelConverter)
                optimized_cls = cast(Type[LlamaBasedModelConverter], optimized_cls)

                return optimized_cls.from_huggingface(
                    model_id_or_path,
                    config=config,
                    **kwargs,
                )
            else:
                low_cpu_mem_usage = kwargs.pop("low_cpu_mem_usage", True)
                return (
                    optimized_cls.from_pretrained(
                        model_id_or_path,
                        config=config,
                        low_cpu_mem_usage=low_cpu_mem_usage,
                        **kwargs,
                    ),
                    None,
                )
    elif issubclass(optimized_cls, CausalModelServer):
        # For furiosa-models models, parameter name conversion is not needed.
        if need_param_name_conversion:
            raise ValueError(
                "Parameter name conversion is not supported for furiosa-models-lang models."
            )

        model_lang_kwargs: Dict[Any, Any] = {}
        if torch_dtype:
            torch_dtype = (
                getattr(torch, torch_dtype) if isinstance(torch_dtype, str) else torch_dtype
            )
            assert isinstance(torch_dtype, torch.dtype)
            dtype_str = str(torch_dtype).split(".")[-1]
            model_lang_kwargs["model_dtype"] = dtype_str

        model = optimized_cls.create(
            config,
            **model_lang_kwargs,
        )

        kwargs.pop("low_cpu_mem_usage", None)

        # FIXME: this will not work for models with remote code. Find more robust method.
        original_hf_model = getattr(transformers, model.__class__.__name__).from_pretrained(
            model_id_or_path,
            config=config,
            low_cpu_mem_usage=True,
            **kwargs,
        )
        assert isinstance(original_hf_model, PreTrainedModel)

        model.load_weights(
            original_hf_model.state_dict().items(),
        )

        return (
            model,
            None,
        )
    else:
        raise ValueError(f"Invalid model of type {optimized_cls}")


def instantiate_model(
    model_id_or_path: Union[str, os.PathLike],  # for model weights
    optimized_cls: Type[PreTrainedModel],
    config: PretrainedConfig,
    optimization_config: OptimizationConfig,
    need_param_name_conversion: bool,
    empty_weight: bool = False,
    torch_dtype: Optional[Union[str, torch.dtype]] = None,
    **kwargs,
) -> Tuple[PreTrainedModel, Optional[Dict[str, str]]]:
    canonical_model_id = find_canonical_model_id(config)
    # TODO: Check if we need to allow this exceptional case.
    # `tests/test_api.py::test_get_splitted_gms[gpt-j-layer4]` invokes LLM.__init__()
    # directly with pretrained_id.
    if canonical_model_id is None and not is_model_path(model_id_or_path):
        canonical_model_id = str(model_id_or_path)
    # canonical_model_id must be available at this point
    assert canonical_model_id, "Failed to find canonical model ID"

    config = copy.deepcopy(config)
    update_config_inplace(canonical_model_id, config, optimization_config)

    ctx_mgrs: List[Union[AbstractContextManager[Any], ContextManager[Any]]] = []
    if empty_weight:
        ctx_mgrs.append(accelerate.init_empty_weights())
    if optimization_config.decompose_layernorm:
        ctx_mgrs.append(replace_layernorm(DecomposedLayerNorm))

    with ExitStack() as stack:
        for ctx_mgr in ctx_mgrs:
            stack.enter_context(ctx_mgr)

        # Suppress too verbose warnings
        with warnings.catch_warnings(record=True):
            apply_warning_filters()

            if empty_weight:
                if type(config).__name__ == "ExaoneConfig":
                    # Exaone model config needs conversion to llama config.
                    # If `from_huggingface` is used, this conversion is done by the method internally,
                    # But for empty weight loading without model hub download, we should do this manually,
                    config = convert_config_for_optimized_cls(config, optimized_cls)

                # Loading the random weights
                model = optimized_cls(config=config)
                parameter_conversion_map = None
            else:
                # Load pretrained weights.
                try:
                    with patch(
                        "torch.load",
                        new=functools.partial(torch.load, mmap=True, weights_only=True),
                    ):
                        model, parameter_conversion_map = _load_from_pretrained(
                            model_id_or_path,
                            optimized_cls,
                            config,
                            need_param_name_conversion,
                            torch_dtype=torch_dtype,
                            **kwargs,
                        )
                except OSError:
                    # Error occurs if the model was not saved with `_use_new_zipfile_serialization` option.
                    # Try again without mmap option.
                    model, parameter_conversion_map = _load_from_pretrained(
                        model_id_or_path,
                        optimized_cls,
                        config,
                        need_param_name_conversion,
                        torch_dtype=torch_dtype,
                        **kwargs,
                    )
    model.eval()
    model.requires_grad_(False)
    return model, parameter_conversion_map


def get_fx_graphs_for_quant(
    model: PreTrainedModel,
) -> tuple[GraphModule, Optional[GraphModule]]:
    prefill_input_names, prefill_concrete_args, decode_input_names, decode_concrete_args = (
        _get_input_names_and_concrete_args_for_symbolic_trace(model)
    )
    if type(model) in (
        flm.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
        flm.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
        flm.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM,
        flm.llama3.symbolic.llama3.LlamaForCausalLM,
        flm.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM,
        flm.llama.symbolic.mlperf_submission.LlamaForCausalLM,
        flm.gptj.symbolic.tta_submission.GPTJForCausalLM,
    ):
        if type(model) in (
            flm.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
            flm.llama.symbolic.mlperf_submission.LlamaForCausalLM,
            flm.gptj.symbolic.tta_submission.GPTJForCausalLM,
        ):
            example_inputs = [
                generate_input_sample(
                    type(model),
                    model.config,
                    bucket,
                    kv_cache_dtype=model.dtype,
                    paged_attention_num_blocks=64,
                    paged_attention_block_size=1,
                    kv_cache_sharing_across_beams_config=None,
                    is_packed_optimized=True,
                    compact_causal_mask_for_bert=False,
                    use_causal_mask_for_generative_model=True,
                    need_args_for_speculative_decoding=False,
                    go_through_mcp=False,
                    is_sliced_model=False,
                    use_2d_masks=False,
                    merged_kv_indices=False,
                )
                for bucket in (Bucket.prefill(4, 2), Bucket.decode(4, 6))
            ]
        elif type(model) in (
            flm.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
            flm.llama3.symbolic.llama3.LlamaForCausalLM,
            flm.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM,
            flm.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM,
        ):
            use_2d_masks = type(model) in (
                flm.llama3.symbolic.llama3.LlamaForCausalLM,
                flm.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM,
            )
            merged_kv_indices = "new_kv_location" in prefill_input_names
            example_inputs = [
                generate_input_sample(
                    type(model),
                    model.config,
                    bucket,
                    kv_cache_dtype=model.dtype,
                    paged_attention_num_blocks=64,
                    paged_attention_block_size=1,
                    kv_cache_sharing_across_beams_config=None,
                    is_packed_optimized=True,
                    compact_causal_mask_for_bert=False,
                    use_causal_mask_for_generative_model=True,
                    need_args_for_speculative_decoding=True,
                    go_through_mcp=False,
                    is_sliced_model=False,
                    use_2d_masks=use_2d_masks,
                    merged_kv_indices=merged_kv_indices,
                )
                for bucket in (Bucket.prefill(4, 2), Bucket(4, 6, 3))
            ]
        else:
            raise ValueError(f"Unsupported model type: {type(model)}")

        empty_init = model.device == torch.device("meta")

        # Model on meta device cannot be traced properly with torchdynamo.
        # So convert model parameters to fake tensor on cpu.
        if empty_init:
            model = deepcopy_to_fake_tensor(model, FakeTensorMode(allow_non_fake_inputs=True)).to(
                "cpu"
            )

        torch._dynamo.reset()
        exported = torch._dynamo.export(
            model,
        )
        prefill_graph, decode_graph = (
            exported(**example_input)[0] for example_input in example_inputs
        )

        # If empty_init, revert model to be on meta device.
        if empty_init:
            prefill_graph = prefill_graph.to("meta")
            decode_graph = decode_graph.to("meta")

        prefill_graph.captured_input, decode_graph.captured_input = example_inputs  # type: ignore [assignment]
        prefill_graph.device = model.device
        decode_graph.device = model.device

        assert isinstance(prefill_graph, GraphModule)
        assert isinstance(decode_graph, GraphModule)
    else:
        logger.info("use fx symbolic tracing for quantization.")
        # use torch.fx.symbolic_trace for tracing.
        prefill_graph = fx_symbolic_trace_model(model, prefill_input_names, prefill_concrete_args)
        if decode_input_names is not None:
            # Generative model
            decode_graph = fx_symbolic_trace_model(model, decode_input_names, decode_concrete_args)
        else:
            decode_graph = None

    # Set information for MCP.
    prefill_graph.input_names = prefill_input_names  # type: ignore [union-attr]
    prefill_graph.concrete_args = prefill_concrete_args  # type: ignore [union-attr]
    if decode_input_names is not None:
        decode_graph.input_names = decode_input_names  # type: ignore [union-attr]
        decode_graph.concrete_args = decode_concrete_args  # type: ignore [union-attr]
        decode_graph.config = model.config  # type: ignore [union-attr]
    prefill_graph.config = model.config  # type: ignore [union-attr]

    return prefill_graph, decode_graph


def _get_quant_causal_lm(
    model: PreTrainedModel,
    optimization_config: OptimizationConfig,
    qformat_path: Union[str, os.PathLike],
    qparam_path: Union[str, os.PathLike],
    quant_ckpt_file_path: Optional[Union[str, os.PathLike]] = None,
) -> QuantCausalLM:
    prefill_graph, decode_graph = get_fx_graphs_for_quant(
        model,
    )
    assert isinstance(prefill_graph, GraphModule)

    # Load the quantized model directly from the checkpoint
    quant_model = QuantCausalLM.from_quant_ckpt(
        model,
        prefill_graph,
        decode_graph,
        qparam_path=qparam_path,
        qformat_path=qformat_path,
        quant_ckpt_file_path=quant_ckpt_file_path,
    )

    # Set configs to be compatible with PretrainedModel and LLM
    quant_model.config = model.config
    quant_model.optimization_config = optimization_config
    quant_model.quantization_config = QuantizationConfig.from_qformat(qformat_path)
    return quant_model


def _get_bf16_casted_causal_lm(
    model: PreTrainedModel,
    optimization_config: OptimizationConfig,
    quantization_config: QuantizationConfig,
):
    prefill_graph, decode_graph = get_fx_graphs_for_quant(
        model,
    )
    assert isinstance(prefill_graph, GraphModule)

    quant_model = QuantCausalLM.get_bf16_casted(
        model, prefill_graph, decode_graph, quantization_config
    )

    # Set configs to be compatible with PretrainedModel and LLM
    quant_model.config = model.config
    quant_model.optimization_config = optimization_config
    quant_model.quantization_config = quantization_config
    return quant_model


def _is_bf16_castable_dtype(torch_dtype: Union[str, torch.dtype]) -> bool:
    """Return True if the dtype is quantizable with naive quantization."""
    return torch_dtype in ("float32", "float16", "bfloat16") or torch_dtype in (
        torch.float32,
        torch.float16,
        torch.bfloat16,
    )


class _FuriosaBaseAutoModelClass(_AutoModelFinder):
    @classmethod
    def _from_quantized_model(cls, path: Path, config: PretrainedConfig) -> "OptimizedModel":
        furiosa_config, qformat_path, qparam_path, quant_ckpt_file_path = (
            _load_quantized_model_meta(path)
        )
        model_id = furiosa_config.model_id
        optimized_cls = furiosa_config.import_model_class()
        optimization_config = furiosa_config.llm_config.optimization_config

        model, _ = instantiate_model(
            model_id,
            optimized_cls,
            config,
            optimization_config,
            False,
            empty_weight=True,
        )

        return _get_quant_causal_lm(
            model,
            optimization_config,
            qformat_path,
            qparam_path,
            quant_ckpt_file_path,
        )

    @classmethod
    def _from_pretrained(
        cls,
        model_id: Union[str, Path],
        config: PretrainedConfig,
        use_auth_token: Optional[Union[bool, str]] = None,
        token: Optional[Union[bool, str]] = None,
        revision: Optional[str] = None,
        force_download: bool = False,
        cache_dir: str = HUGGINGFACE_HUB_CACHE,
        subfolder: str = "",
        local_files_only: bool = False,
        *,
        use_only_beam_search: bool = False,
        compute_logit_for_last_token: bool = False,
        auto_bfloat16_cast: bool = False,
        torch_dtype: Optional[Union[str, torch.dtype]] = None,
        _disable_implicit_typecast: bool = False,
        **kwargs,
    ) -> "OptimizedModel":
        # *Design Note*
        #
        # This method basically keeps the same behavior as the original `AutoModel._from_pretrained` method
        # and its variations (e.g., AutoModelForCausalLM._from_pretrained) in transformers library.
        #
        # It additionally supports the quantized model loading and naive quantization.
        # They are provided by additional arguments, `quantization_checkpt_path` and `torch_dtype`.
        # The native quantization is enabled when `torch_dtype` is 'auto' or 'bfloat16'.

        ctx_mgrs: List[Union[AbstractContextManager[Any], ContextManager[Any]]] = []
        model_cls = cls.find_model_class(model_id, config, **kwargs)
        exported_model_qckpt_path: Optional[Path] = None

        # If the model is quantized by FuriosaQuantizer (a conditional branch for production)
        if is_quantized_model_path(model_id):
            model_path = Path(model_id) if not isinstance(model_id, Path) else model_id
            return cls._from_quantized_model(model_path, config)
        else:
            # If the model is not quantized but a model id with qparam, qformat are specified,
            # this code path will be invoked.
            # TODO - we can remove this branch if we improve LLM class and e2e_pipe.py
            #   to pass the directory path of furiosa-llm-models-artifacts instead of individual files.

            # TODO - Remove this assertion after the dependency of model_id is removed.
            #  It should be able to run with the model directory. See update_config_inplace() and
            #  get_optimized_cls(). They depend on a model_id string.
            assert isinstance(
                model_id, str
            ), "model_id must be a string rather than Path if it is not a quantized model"

            # OptimizationConfig is only for internal use. We expect OptimizationConfig to be passed
            # from furiosa-llm, and we don't expect users to pass it.
            optimization_config = kwargs.pop("optimization_config", None)
            # This is a hidden feature for the furiosa-llm team to pass the quantization config.
            quantization_checkpt_path = kwargs.pop("quantization_checkpt_path", None)

            if optimization_config is None:
                optimization_config = _get_optimization_config(
                    model_cls,
                    model_id,
                    use_only_beam_search=use_only_beam_search,
                    compute_logit_for_last_token=compute_logit_for_last_token,
                )

            canonical_model_id = find_canonical_model_id(config)
            if canonical_model_id is None:
                raise ValueError(
                    f"furiosa_llm.optimum.AutoModel doesn't support the model config {type(config)}"
                )

            optimized_cls = get_optimized_cls(canonical_model_id, model_cls, optimization_config)

            config = copy.deepcopy(config)
            need_param_name_conversion = requires_parameter_names_conversion(model_cls)

            pretrained_weight_load_options = {
                "use_auth_token": use_auth_token,
                "token": token,
                "revision": revision,
                "force_download": force_download,
                "cache_dir": cache_dir,
                "subfolder": subfolder,
                "local_files_only": local_files_only,
            }

            # Fill qformat, qparam, exported_models.qckpt if they exist
            if quantization_checkpt_path:
                if not isinstance(quantization_checkpt_path, Path):
                    quantization_checkpt_path = Path(quantization_checkpt_path)

                qformat_path = quantization_checkpt_path / _QFORMAT_YAML
                qparam_path = quantization_checkpt_path / _QPARAM_NPY
                exported_model_qckpt_path = quantization_checkpt_path / _EXPORTED_MODEL_QCKPT

                if not qformat_path.exists() or not qparam_path.exists():
                    raise ValueError(
                        f"qformat.yaml or qparam.npy checkpoint files are not found in {quantization_checkpt_path}"
                    )

                if exported_model_qckpt_path and exported_model_qckpt_path.exists():
                    ctx_mgrs.append(accelerate.init_empty_weights())
                else:
                    exported_model_qckpt_path = None

            cast_to_bf16 = (
                auto_bfloat16_cast
                or (config.torch_dtype == torch.bfloat16 and not _disable_implicit_typecast)
                and not torch_dtype
            )
            supported_by_mcp = is_supported_by_mcp(optimized_cls)

            if not supported_by_mcp and cast_to_bf16:
                # To cast model to bf16 without MCP, we need to set torch_dtype.
                torch_dtype = torch.bfloat16

            model, _ = instantiate_model(
                model_id,
                optimized_cls,
                config,
                optimization_config,
                need_param_name_conversion,
                empty_weight=bool(exported_model_qckpt_path),
                torch_dtype=torch_dtype,
                **pretrained_weight_load_options,
                **kwargs,
            )

            # Quantize model weights with qparam/format or loading a quantized model directly
            if quantization_checkpt_path:
                assert supported_by_mcp
                return _get_quant_causal_lm(
                    model,
                    optimization_config,
                    qformat_path,
                    qparam_path,
                    exported_model_qckpt_path,
                )
            elif supported_by_mcp and cast_to_bf16:
                # The model trained with bfloat16 can run by default, or auto_bfloat16_cast=True is required.
                return _get_bf16_casted_causal_lm(
                    model, optimization_config, QuantizationConfig.w_16_a_16_kv_16()
                )
            elif cast_to_bf16:
                # Cast to bf16 without using MCP.
                return model
            else:
                logger.warning(
                    "The model is neither quantized nor trained with bfloat16. This model won't be loaded to RNGD."
                )
                if _is_bf16_castable_dtype(config.torch_dtype):
                    logger.warning(
                        f"The model has torch_dtype={config.torch_dtype} which can be casted to bfloat16. "
                        "If you want to use this model with bfloat16, please set auto_bfloat16_cast=True."
                    )
                return model


class AutoModel(_FuriosaBaseAutoModelClass, OptimizedModel):
    _model_mapping = transformers.MODEL_MAPPING
    _auto_model_cls = transformers.AutoModel


class AutoModelForCausalLM(_FuriosaBaseAutoModelClass, OptimizedModel):
    _model_mapping = transformers.MODEL_FOR_CAUSAL_LM_MAPPING
    _auto_model_cls = transformers.AutoModelForCausalLM


class AutoModelForQuestionAnswering(_FuriosaBaseAutoModelClass, OptimizedModel):
    _model_mapping = transformers.MODEL_FOR_QUESTION_ANSWERING_MAPPING
    _auto_model_cls = transformers.AutoModelForQuestionAnswering


def is_supported_by_mcp(
    optimized_cls: Type[torch.nn.Module],
) -> bool:
    """
    Check if the model class is supported by Model Compressor.
    """

    return optimized_cls in (
        flm.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
        flm.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
        flm.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM,
        flm.llama3.symbolic.llama3.LlamaForCausalLM,
        flm.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM,
        flm.llama.symbolic.mlperf_submission.LlamaForCausalLM,
        flm.gptj.symbolic.mlperf_submission.GPTJForCausalLM,
        flm.gptj.symbolic.tta_submission.GPTJForCausalLM,
        flm.bert.symbolic.mlperf_submission.BertForQuestionAnswering,
    )
