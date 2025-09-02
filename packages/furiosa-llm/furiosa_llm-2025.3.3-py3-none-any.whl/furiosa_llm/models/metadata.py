from contextlib import ExitStack
import copy
from copy import deepcopy
import functools
import json
import logging
import os
from pathlib import Path
import sys
import typing
from typing import Any, Dict, Final, Iterable, Mapping, Optional, Sequence, Tuple, Type, Union

import cachetools
from cachetools.keys import hashkey
import furiosa_llm_models
from furiosa_models.architecture.models.serve import (
    CausalModelServer,
)
from pydantic import BaseModel, Field, PrivateAttr, model_validator
import torch
import transformers
from transformers import PretrainedConfig, PreTrainedModel, set_seed
from typing_extensions import Self

from furiosa_llm.models.config_types import Bucket
from furiosa_llm.optimum import AttentionType, OptimizationConfig, QDtype, QuantizationConfig
import furiosa_llm.optimum.modeling
from furiosa_llm.optimum.modeling import (
    LLAMA3_1_8B_ELICEAI_HELPY_EDU_B_PRETRAINED_ID,
    MODEL_CLS_TO_MLPERF_OPT_CONFIGS,
    SOLAR_10D7B_INSTRUCT_PRETRAINED_ID,
    AutoModel,
    AutoModelForCausalLM,
    AutoModelForQuestionAnswering,
    DecomposedLayerNorm,
    _FuriosaBaseAutoModelClass,
    _get_quant_causal_lm,
    convert_config_for_optimized_cls,
    get_mapped_class_for_optimization,
    get_optimized_cls,
    is_generative_model,
    is_llama3_based,
    is_mlperf_optimized,
    is_mlperf_optimized_with,
    is_model_path,
    is_supported_by_mcp,
    replace_layernorm,
    requires_parameter_names_conversion,
    set_default_torch_dtype,
    update_config_inplace,
)
from furiosa_llm.optimum.types import LLMConfig

if typing.TYPE_CHECKING:
    from furiosa_llm.parallelize.pipeline.types import Pipeline

from ..utils import get_logger_with_tz, zip_equal
from .config_types import GeneratorConfig, KvCacheSharingAcrossBeamsConfig, PipelineMetadata
from .utils import generate_input_sample

DEFAULT_SEED_VALUE: Final = 42

# The maximum number of `Model.pretrained_models` kept.
# A custom pytest hook is used to group parametrized tests to work around this limit.
# Note that this should be at least 2 because quantized models recursively load base models!
PRETRAINED_MODEL_CACHE_SIZE: Final = 2
FURIOSA_LLM_PACKAGE_PATH: Final = Path(__file__).parent.parent
TINY_GPTJ_CONFIG: Final[Dict[str, Any]] = {
    "n_embd": 32,
    "rotary_dim": 2,
    "n_inner": 1,
}

MODEL_CONFIG_ROOT_DIR = Path(__file__).parent.with_name("model_configs")

with open(MODEL_CONFIG_ROOT_DIR / "LLaMA3.1-8B.json") as f:
    LLAMA3_1_8B_CONFIG = json.load(f)

with open(MODEL_CONFIG_ROOT_DIR / "LLaMA3.1-70B.json") as f:
    LLAMA3_1_70B_CONFIG = json.load(f)


logger = get_logger_with_tz(logging.getLogger(__name__))

TASK_TYPE_TO_AUTO_MODEL_CLASS: Final[Dict[str, Type[PreTrainedModel]]] = {
    "text-generation": AutoModelForCausalLM,
    "question-answering": AutoModelForQuestionAnswering,
}


# Cache based on `pretrained_id` and `revision` only.
@cachetools.cached(
    cache=cachetools.LRUCache(128),
    key=lambda pretrained_id, trust_remote_code, revision: hashkey(pretrained_id, revision),
)
def get_config_from_pretrained_id(
    pretrained_id: Union[str, Path],
    trust_remote_code: Optional[bool],
    revision: Optional[str],
) -> PretrainedConfig:
    return transformers.AutoConfig.from_pretrained(
        pretrained_id, trust_remote_code=trust_remote_code, revision=revision
    )


class DummyModel(torch.nn.Module):
    def __init__(self, batch_size: int = 1):
        super(DummyModel, self).__init__()
        self.linear1 = torch.nn.Linear(16, batch_size)

    def forward(self, x):
        return self.linear1(x)


def get_model_cls_from_pretrained_id(
    pretrained_id: Union[str, Path],
    trust_remote_code: Optional[bool],
    revision: Optional[str] = None,
    task_type: Optional[str] = None,
) -> Type[PreTrainedModel]:
    model_config = get_config_from_pretrained_id(pretrained_id, trust_remote_code, revision)
    supported_architectures = getattr(model_config, "architectures", [])

    if task_type:
        if auto_model_cls := TASK_TYPE_TO_AUTO_MODEL_CLASS.get(task_type):
            return auto_model_cls.find_model_class(
                pretrained_id,
                model_config,
                trust_remote_code=trust_remote_code,
            )
        else:
            raise NotImplementedError(f"Unsupported task_type: {task_type}")
    else:
        if len(supported_architectures) != 1:
            raise ValueError(
                f"Task type not given, but multiple architectures found: {supported_architectures}"
            )

        if model_cls := getattr(transformers, supported_architectures[0], None):
            return model_cls

        # Model should be loaded with remote code.
        if not hasattr(model_config, "auto_map"):
            raise ValueError(
                f"Model {pretrained_id} is not a local model, but does not have an auto map in config."
            )
        auto_class_names = [
            auto_class_name
            for auto_class_name, class_ref in model_config.auto_map.items()
            if class_ref.rsplit('.', maxsplit=1)[-1] == supported_architectures[0]
        ]
        assert len(auto_class_names) == 1
        auto_class_name = auto_class_names[0]
        if not (module_finder := getattr(furiosa_llm.optimum.modeling, auto_class_name)):
            raise ValueError(f"Unsupported auto model class type: {auto_class_name}")
        assert issubclass(module_finder, _FuriosaBaseAutoModelClass)
        return module_finder.find_model_class(
            pretrained_id,
            model_config,
            trust_remote_code=trust_remote_code,
        )


def get_default_task_type_from_pretrained_id(
    pretrained_id: str, trust_remote_code: Optional[bool], revision: Optional[str] = None
) -> str:
    model_cls = get_model_cls_from_pretrained_id(pretrained_id, trust_remote_code, revision)
    if model_cls in transformers.MODEL_FOR_CAUSAL_LM_MAPPING.values():
        return "text-generation"
    elif model_cls in transformers.MODEL_FOR_QUESTION_ANSWERING_MAPPING.values():
        return "question-answering"
    else:
        raise ValueError(f"cannot set task_type automatically for {model_cls}")


def download_model_and_get_hash(model_id: str, revision: str) -> str:
    """
    Extract the commit SHA from the huggingface_hub snapshot directory path.
    For example: .../snapshots/11c5a3d5811f50298f278a704980280950aedb10/config.json
    """
    from huggingface_hub import snapshot_download

    from furiosa_llm.optimum.modeling import is_model_path

    assert not is_model_path(model_id), "must be called when the model id is given"
    path = snapshot_download(repo_id=model_id, repo_type="model", revision=revision)

    p = Path(path)
    parts = p.parts
    if "snapshots" in parts:
        i = parts.index("snapshots")
        if i + 1 < len(parts):
            return parts[i + 1]

    raise ValueError("Could not find commit hash in snapshot path.")


def calculate_dir_hashsum(path: os.PathLike) -> str:
    import time

    import blake3

    BLOCK_SIZE: int = 8192
    start_ts = time.perf_counter()
    hasher = blake3.blake3()
    path = Path(path)
    if not path.is_dir():
        raise ValueError(f"{path} is not a directory")

    # Collect all files recursively, sort for determinism
    files = sorted([p for p in path.rglob("*") if p.is_file()])
    total_files = len(files)
    total_bytes = 0

    # Calculate the hashsum of all found files
    for file in files:
        # Update with relative path for uniqueness
        rel_path = str(file.relative_to(path)).encode()
        hasher.update(rel_path)
        # Update with file content
        with open(file, "rb") as f:
            while True:
                chunk = f.read(BLOCK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
                total_bytes += len(chunk)

    digest = hasher.hexdigest()
    elapsed = time.perf_counter() - start_ts
    mb = total_bytes / (1024 * 1024)
    mbps = (mb / elapsed) if elapsed > 0 else 0.0

    logger.info(
        "Calculated the hashsum in %.3fs for '%s' (files=%d, size=%.2f MB, throughput=%.2f MB/s)",
        elapsed,
        str(path),
        total_files,
        mb,
        mbps,
    )
    return digest


@functools.total_ordering
class ModelMetadata(BaseModel):
    # TODO - Rename pretrained_id to distinguish two roles: a model_id to choose the LLM
    # optimization and a Hub repo ID for model weights
    pretrained_id: str  # Canonical model ID
    task_type: Optional[str] = None
    llm_config: LLMConfig = Field(default_factory=LLMConfig)
    hf_configs: Dict[str, Any] = Field(default_factory=dict)
    # path to load pre-trained model weights (optional)
    model_weight_path: Optional[os.PathLike] = None
    trust_remote_code: Optional[bool] = None
    allow_bfloat16_cast_with_mcp: bool = True

    # This field exists only for artifact backward compatibility.
    auto_bfloat16_cast: Optional[bool] = True

    # Below fields are not serialized in artifact.json.
    # So, they exist only in Python part and Rust part shouldn't rely on them.
    _model_id_or_path: Union[str, Path] = PrivateAttr(default=None)
    _revision: Optional[str] = PrivateAttr(default=None)
    # Hash sum via blake3, use huggingface git commit, or pretrained_id (only for tests)
    _weights_hash: Optional[str] = PrivateAttr(default=None)

    @model_validator(mode='after')
    def validate_model_metadata(self):
        if self.task_type is None:
            # Here, we cannot use _model_id_or_path and _revision because PrivateAttr
            # must be set after __init__. But, it's ok now because we just get a task type here.
            # TODO: For more precise behavior, we need to use both _model_id_or_path and _revision.
            #  Fine-tuned models may be able to support different tasks.
            self.task_type = get_default_task_type_from_pretrained_id(
                self.pretrained_id, self.trust_remote_code
            )
        assert self.task_type in transformers.pipelines.SUPPORTED_TASKS, "unsupported task_type"
        return self

    @property
    @functools.lru_cache
    def model_cls(self) -> Type[PreTrainedModel]:
        return get_model_cls_from_pretrained_id(
            self._model_id_or_path, self.trust_remote_code, self._revision, self.task_type
        )

    @property
    def _is_tiny_gptj(self) -> bool:
        config_without_num_hidden_layers = {
            k: v for k, v in self.hf_configs.items() if k != "num_hidden_layers"
        }

        return (
            self.model_cls == transformers.GPTJForCausalLM
            and config_without_num_hidden_layers == TINY_GPTJ_CONFIG
        )

    @property
    def num_hidden_layers(self) -> int:
        return (
            self.config_dict.get("num_hidden_layers")
            or self.config_dict.get("num_layers")
            or self.config_dict["n_layer"]
        )

    @property
    def attention_type(self) -> AttentionType:
        return self.llm_config.optimization_config.attention_type

    @property
    def optimize_options(self) -> OptimizationConfig:
        return self.llm_config.optimization_config

    @property
    def quantization_config(self) -> Optional[QuantizationConfig]:
        return self.llm_config.quantization_config

    def __init__(
        self,
        pretrained_id: str,
        task_type: Optional[str] = None,
        llm_config: LLMConfig = LLMConfig(),
        hf_configs: Dict = {},
        model_weight_path: Optional[os.PathLike] = None,
        trust_remote_code: Optional[bool] = None,
        allow_bfloat16_cast_with_mcp: bool = True,
        # This arg exists for artifact backward compatibility.
        auto_bfloat16_cast: Optional[bool] = None,
        # model id or path for weights
        model_id_or_path: Optional[Union[str, Path]] = None,
        revision: Optional[str] = None,
    ):
        super(ModelMetadata, self).__init__(
            pretrained_id=pretrained_id,
            task_type=task_type,
            llm_config=llm_config,
            hf_configs=hf_configs,
            model_weight_path=model_weight_path,
            trust_remote_code=trust_remote_code,
            allow_bfloat16_cast_with_mcp=allow_bfloat16_cast_with_mcp,
            auto_bfloat16_cast=auto_bfloat16_cast,
        )
        # pretrained_id is allowed only for tests
        self._model_id_or_path = model_id_or_path or pretrained_id
        self._revision = revision

        # If the model is not quantized and can be casted to bfloat16, enable auto bf16 cast.
        if not self.quantization_config and (
            (self.config_dict.get("torch_dtype") == "bfloat16" and allow_bfloat16_cast_with_mcp)
            or auto_bfloat16_cast
        ):
            self._enable_auto_bfloat16_cast()

    @classmethod
    def init_with_mlperf_optim_options(
        cls,
        pretrained_id: str,
        quantization_config: Optional[QuantizationConfig] = None,
        hf_configs: Dict = {},
        model_weight_path: Optional[os.PathLike] = None,
        trust_remote_code: Optional[bool] = None,
        allow_bfloat16_cast_with_mcp: bool = True,
        model_id_or_path: Optional[Union[str, Path]] = None,
        revision: Optional[str] = None,
    ) -> Self:
        # pretrained_id is allowed only for tests
        model_id_or_path = model_id_or_path or pretrained_id
        return cls(
            pretrained_id=pretrained_id,
            llm_config=LLMConfig(
                optimization_config=ModelMetadata.get_mlperf_options(
                    get_model_cls_from_pretrained_id(model_id_or_path, trust_remote_code, revision),
                    pretrained_id,
                ),
                quantization_config=quantization_config,
            ),
            hf_configs=hf_configs,
            model_weight_path=model_weight_path,
            trust_remote_code=trust_remote_code,
            allow_bfloat16_cast_with_mcp=allow_bfloat16_cast_with_mcp,
            model_id_or_path=model_id_or_path,
            revision=revision,
        )

    def with_num_layers(self, num_hidden_layers: int) -> Self:
        return self.model_copy(
            update={
                "hf_configs": {**self.hf_configs, "num_hidden_layers": num_hidden_layers},
            },
            deep=True,
        )

    def with_hf_configs(self, hf_configs: Mapping[str, Any]) -> Self:
        new_hf_configs = deepcopy(self.hf_configs)
        new_hf_configs.update(hf_configs)
        return self.model_copy(
            update={
                "hf_configs": new_hf_configs,
            },
            deep=True,
        )

    def with_quantization_config(self, quantization_config: QuantizationConfig) -> Self:
        return self.model_copy(
            update={
                "llm_config": self.llm_config.with_quantization_config(quantization_config),
            },
            deep=True,
        )

    def with_optimizations(self, opts: Union[Dict[str, Any], str]) -> Self:
        if isinstance(opts, str):
            opts = {opts: True}
        return self.model_copy(
            update={
                "llm_config": self.llm_config.with_optimizations(opts),
            },
            deep=True,
        )

    @property
    def is_beam_search_kv_cache_sharing_model(self) -> bool:
        return (
            self.model_cls is transformers.GPTJForCausalLM
            and self.optimize_options.kv_cache_sharing_across_beams
        )

    def is_compact_causal_mask_for_bert(self) -> bool:
        return (
            self.model_cls is transformers.BertForQuestionAnswering
            and self.optimize_options.compact_causal_mask
        )

    @staticmethod
    def get_mlperf_options(
        model_cls: Type[PreTrainedModel], canonical_model_id: str
    ) -> OptimizationConfig:
        model_cls = get_mapped_class_for_optimization(model_cls, canonical_model_id)

        if optim_options := MODEL_CLS_TO_MLPERF_OPT_CONFIGS.get(model_cls):
            return optim_options
        raise NotImplementedError(f"Unsupported mlperf model variant: {model_cls}")

    @staticmethod
    def mlperf_option_exists(model_cls: Type[PreTrainedModel]) -> bool:
        return model_cls in MODEL_CLS_TO_MLPERF_OPT_CONFIGS

    @property
    def contains_mlperf_opts(self) -> bool:
        model_cls = get_mapped_class_for_optimization(self.model_cls, self.pretrained_id)

        return ModelMetadata.mlperf_option_exists(  # fmt: off
            model_cls
        ) and self.optimize_options.contains(self.get_mlperf_options(model_cls, self.pretrained_id))

    @property
    def use_paged_attention(self) -> bool:
        return self.attention_type == AttentionType.PAGED_ATTENTION

    def __str__(self):
        name = str(self._model_id_or_path).rsplit("/", maxsplit=1)[-1]

        return "{}{}_{}L{}{}".format(
            "TINY_" if self._is_tiny_gptj else "",
            name,
            self.get_num_hidden_layers(),
            f"_{self.get_optimized_cls().__module__}",
            f"_{self.quantization_config}" if self.is_quantized else "",
        )

    @property
    def name(self):
        return self.__str__()

    @property
    def __hash_key(self):
        """A hashable key to uniquely identify the model metadata."""

        # Convert the nested values to hashable types in a recursively way
        def hashable_dict(d):
            return frozenset(
                (
                    k,
                    (
                        hashable_dict(v)
                        if isinstance(v, dict)
                        else tuple(v) if isinstance(v, list) else v
                    ),
                )
                for k, v in d.items()
            )

        hashable_hf_configs = {
            k: (hashable_dict(v) if isinstance(v, dict) else tuple(v) if isinstance(v, list) else v)
            for k, v in self.hf_configs.items()
        }

        return (
            self._model_id_or_path,
            self.task_type,
            not self.optimize_options.optimize_furiosa,
            self.hf_configs.get("num_hidden_layers"),
            self.attention_type,
            self.optimize_options,
            self.quantization_config,
            frozenset(hashable_hf_configs.items()),
        )

    def __eq__(self, other):
        if not isinstance(other, ModelMetadata):
            return False
        return self.__hash_key == other.__hash_key

    def __lt__(self, other):
        if not isinstance(other, ModelMetadata):
            return NotImplemented
        return self.__hash_key < other.__hash_key

    def __hash__(self):
        return hash(self.__hash_key)

    def get_num_hidden_layers(self) -> int:
        """Retrieve the number of hidden layers in the model.

        If the number of hidden layers was specified during initialization, it returns that value.
        Otherwise, it returns the total number of layers in the model variant.

        Returns:
            int: The number of hidden layers.

        Raises:
            ValueError: If the number of layers in the model variant is unknown.
        """
        return self.hf_configs.get("num_hidden_layers", self.full_layer_count)

    @property
    def pretrained_name(self) -> str:
        return str(self._model_id_or_path)

    @property
    def is_generative_model(self) -> bool:
        return self.task_type == "text-generation" or is_generative_model(self.model_cls)

    @property
    def kv_cache_torch_dtype(self) -> Optional[torch.dtype]:
        return self.kv_cache_dtype.to_torch_dtype() if self.kv_cache_dtype else None

    @property
    def kv_cache_dtype(self) -> Optional[QDtype]:
        if not self.is_generative_model:
            return None
        if self.quantization_config:
            return self.quantization_config.kv_cache
        return QDtype.FP32

    @property
    def is_quantized(self) -> bool:
        return self.quantization_config is not None

    @property
    def need_quant_artifacts(self) -> bool:
        # BF16 model doesn't need qparam, qformat files.
        return (
            self.quantization_config is not None
            and self.quantization_config.use_mcp
            and not (self.allow_bfloat16_cast_with_mcp and self.quantization_config.is_bf16)
        )

    def with_allowing_bf16_cast_with_mcp(self) -> Self:
        return self.model_copy(
            update={
                "allow_bfloat16_cast_with_mcp": True,
            },
            deep=True,
        )

    def with_auto_bfloat16_cast(self) -> Self:
        copied = copy.deepcopy(self)
        copied._enable_auto_bfloat16_cast()
        return copied

    def _enable_auto_bfloat16_cast(self) -> None:
        if self.is_generative_model:
            quant_config = QuantizationConfig.w_16_a_16_kv_16()
        else:
            quant_config = QuantizationConfig.w_16_a_16()
        use_mcp = is_supported_by_mcp(self.get_optimized_cls())
        quant_config = quant_config.model_copy(update={"use_mcp": use_mcp})
        self.llm_config = self.llm_config.with_quantization_config(quant_config)
        self.allow_bfloat16_cast_with_mcp = True

    @property
    def full_layer_count(self) -> int:
        config = get_config_from_pretrained_id(
            self._model_id_or_path, self.trust_remote_code, self._revision
        )

        if full_layer_cnt := getattr(
            config, "num_hidden_layers", getattr(config, "n_layers", None)
        ):
            return full_layer_cnt
        raise ValueError(f"Unknown number of hidden layers for {self}")

    @property
    def config(self) -> PretrainedConfig:
        config_original: PretrainedConfig = get_config_from_pretrained_id(
            self._model_id_or_path, self.trust_remote_code, self._revision
        )
        config = copy.deepcopy(config_original)

        # Some `PretrainedConfig` types may have non-standard attribute names,
        # so we use the config's `attribute_map` to validate key names.
        attribute_map_of_config = getattr(config, "attribute_map", {})
        valid_config_attributes = {*config.__dict__.keys(), *attribute_map_of_config.keys()}
        for key, val in self.hf_configs.items():
            if key not in valid_config_attributes:
                logger.warning(
                    f"{key} in hf_configs is not valid attribute of {type(config_original)}, and it will be ignored."
                )
            setattr(config, key, val)

        update_config_inplace(self.pretrained_id, config, self.optimize_options)
        return config

    @property
    def config_dict(self) -> Dict[str, Any]:
        return self.config.to_dict()

    @property
    def is_mlperf_optimized(self) -> bool:
        return is_mlperf_optimized(self.model_cls, self.optimize_options)

    def is_mlperf_optimized_with(self, **kwargs) -> bool:
        return is_mlperf_optimized_with(self.model_cls, self.optimize_options)

    def get_optimized_cls(self) -> Type[PreTrainedModel]:
        return get_optimized_cls(self.pretrained_id, self.model_cls, self.optimize_options)

    @property
    def model_qname(self) -> str:
        cls_type = self.get_optimized_cls()
        return f"{cls_type.__module__}.{cls_type.__name__}"

    @property
    def _is_bf16_model_without_mcp(self) -> bool:
        return bool(
            self.quantization_config
            and not self.quantization_config.use_mcp
            and self.quantization_config
            not in (QuantizationConfig.w_16_a_16_kv_16(), QuantizationConfig.w_16_a_16())
        )

    def ensure_model_and_update_weight_hash(self):
        if is_model_path(self._model_id_or_path):
            if self._revision is not None:
                logging.warning("Ignoring Huggingface model revision because the model is local.")
            self._revision = None
            self._weights_hash = calculate_dir_hashsum(self._model_id_or_path)
        else:
            self._revision = download_model_and_get_hash(self._model_id_or_path, self._revision)
            self._weights_hash = self._revision

    @functools.lru_cache(maxsize=1)
    def _random_weight_model(
        self,
        seed: int,
        qformat_path: Optional[os.PathLike],
        qparam_path: Optional[os.PathLike],
        run_gc: bool,
    ) -> PreTrainedModel:
        # FIXME: This is a workaround to reduce memory usage
        self._pretrained_model.cache_clear()
        if run_gc:
            import gc

            gc.collect()
        set_seed(seed)
        print(f"\x1b[1;36m(Creating {self} with random weights)\x1b[0m", end="", file=sys.stderr)
        sys.stderr.flush()

        contexts = []
        if self.optimize_options.decompose_layernorm:
            contexts.append(replace_layernorm(DecomposedLayerNorm))
        if self._is_bf16_model_without_mcp:
            contexts.append(set_default_torch_dtype(torch.bfloat16))
        with ExitStack() as stack:
            for ctx in contexts:
                stack.enter_context(ctx)
            if requires_parameter_names_conversion(self.model_cls):
                config = convert_config_for_optimized_cls(self.config, self.get_optimized_cls())
            else:
                config = self.config
            optimized_cls = self.get_optimized_cls()
            if issubclass(optimized_cls, PreTrainedModel):
                model = optimized_cls(config=config)
            elif issubclass(optimized_cls, CausalModelServer):
                assert (
                    not self.quantization_config or not self.quantization_config.use_mcp
                ), "furiosa-models-lang model cannot be used with MCP."
                if not self.quantization_config:
                    model_dtype = "float32"
                    kv_cache_dtype = model_dtype if self.is_generative_model else None
                else:
                    model_dtype = _qdtype_to_model_lang_dtype(self.quantization_config.weight)
                    kv_cache_dtype = (
                        _qdtype_to_model_lang_dtype(self.quantization_config.kv_cache)
                        if self.quantization_config.kv_cache
                        else None
                    )

                model = optimized_cls.create(
                    config,
                    model_dtype=model_dtype,
                    kv_cache_dtype=kv_cache_dtype,
                )
            else:
                raise ValueError(
                    f"Unsupported model class: {optimized_cls.__module__}.{optimized_cls.__name__}"
                )

        model.eval()
        model.requires_grad_(False)

        if self.optimize_options.decompose_layernorm:
            model.config.decompose_layernorm = True

        if self.is_quantized and self.need_quant_artifacts:
            if not (qformat_path and qparam_path):
                raise ValueError(
                    "Both `qparam_path` and `qformat_path` should be given for quantization."
                )
            return _get_quant_causal_lm(
                model,
                self.optimize_options,
                qformat_path=qformat_path,
                qparam_path=qparam_path,
            )
        else:
            return model

    # FIXME: This wraps internal function to properly cache the model(because of default args)
    def random_weight_model(
        self,
        seed: int = DEFAULT_SEED_VALUE,
        qformat_path: Optional[os.PathLike] = None,
        qparam_path: Optional[os.PathLike] = None,
        run_gc: bool = True,
    ) -> PreTrainedModel:
        return self._random_weight_model(seed, qformat_path, qparam_path, run_gc)  # type: ignore[arg-type]

    @functools.lru_cache(maxsize=PRETRAINED_MODEL_CACHE_SIZE)
    def _pretrained_model(
        self,
        qformat_path: Optional[os.PathLike] = None,
        qparam_path: Optional[os.PathLike] = None,
        quant_ckpt_file_path: Optional[os.PathLike] = None,
        run_gc: bool = True,
    ) -> PreTrainedModel:
        # FIXME: This is a workaround to reduce memory usage
        self._random_weight_model.cache_clear()
        if run_gc:
            import gc

            gc.collect()
        print(f"\x1b[1;36m(Loading {self})\x1b[0m", end="", file=sys.stderr)
        sys.stderr.flush()

        # Make sure qformat_path and qparam_path are given together or not given at all.
        if qformat_path and os.path.isfile(qformat_path):
            assert qparam_path and os.path.isfile(qparam_path), "qparam_path should be given."
        if qparam_path and os.path.isfile(qparam_path):
            assert qformat_path and os.path.isfile(qformat_path), "qformat_path should be given."

        # Make sure qparam_path, qformat_path, and quant_ckpt_file_path (optional) are
        # under the same directory and set quantization_checkpt_path to the directory.
        # It's necessary because AutoModel.from_pretrained uses a specific directory
        # to load quantization artifacts (qparam.npy, qformat.yaml, and exported_model.qckpt).
        quantization_checkpt_path = None
        if qparam_path and qformat_path:
            # Make sure qparam_path and qformat_path are belong to the same parent directory
            assert os.path.dirname(qparam_path) == os.path.dirname(
                qformat_path
            ), "qparam_path and qformat_path should be in the same directory."
            if (
                quant_ckpt_file_path
            ):  # if quant_ckpt_file_path is given, make sure it is in the same directory
                assert os.path.dirname(quant_ckpt_file_path) == os.path.dirname(
                    qparam_path
                ), "quant_ckpt_file_path should be in the same directory."

            # Set quantization_checkpt_path to the parent directory of qformat.yaml, qparam.npy,
            #   and exported_model.qckpt (optional)
            quantization_checkpt_path = os.path.dirname(qformat_path)

        auto_model_cls: Optional[Type[_FuriosaBaseAutoModelClass]]
        if self.task_type is None:
            auto_model_cls = AutoModel
        else:
            auto_model_cls = TASK_TYPE_TO_AUTO_MODEL_CLASS.get(self.task_type)
            if auto_model_cls is None:
                raise ValueError(f"Unsupported task_type: {self.task_type}")

        if self.quantization_config and not self.quantization_config.use_mcp:
            quant_types = {self.quantization_config.weight, self.quantization_config.activation}
            if self.quantization_config.kv_cache:
                quant_types.add(self.quantization_config.kv_cache)
            if len(quant_types) > 1:
                raise ValueError(
                    f"Quantization for {self.quantization_config} without MCP is not supported. "
                )
            torch_dtype = quant_types.pop().to_torch_dtype()
        else:
            torch_dtype = None

        return auto_model_cls.from_pretrained(
            model_id=self._model_id_or_path,
            config=self.config,
            optimization_config=self.optimize_options,
            quantization_checkpt_path=quantization_checkpt_path,
            trust_remote_code=self.trust_remote_code,
            revision=self._revision,
            auto_bfloat16_cast=self.quantization_config
            and self.quantization_config.is_bf16
            and self.quantization_config.use_mcp,
            _disable_implicit_typecast=True,
            torch_dtype=torch_dtype,
        )

    # FIXME: This wraps internal function to properly cache the model
    def pretrained_model(
        self,
        qformat_path: Optional[os.PathLike] = None,
        qparam_path: Optional[os.PathLike] = None,
        quant_ckpt_file_path: Optional[os.PathLike] = None,
        run_gc: bool = True,
    ) -> PreTrainedModel:
        return self._pretrained_model(qformat_path, qparam_path, quant_ckpt_file_path, run_gc)  # type: ignore[arg-type]

    def has_side_effect(self) -> bool:
        return self.attention_type == AttentionType.PAGED_ATTENTION

    def is_available(self) -> bool:
        if not self.is_quantized:
            return True

        if self.get_optimized_cls() in (
            furiosa_llm_models.gptj.symbolic.huggingface.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.preallocated_concat_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.huggingface_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM,
            furiosa_llm_models.gptj.symbolic.paged_attention_rope.GPTJForCausalLM,
            furiosa_llm_models.bert.symbolic.experimental.huggingface_unsplit_packed.BertForQuestionAnswering,
        ):
            return False

        # These models are temporarily available.
        UNAVAILABLE_PAIRS = {
            (SOLAR_10D7B_INSTRUCT_PRETRAINED_ID, QuantizationConfig.w_16_a_16_kv_16()),
            (
                LLAMA3_1_8B_ELICEAI_HELPY_EDU_B_PRETRAINED_ID,
                QuantizationConfig.w_f8_a_f8_kv_f8(),
            ),
            (
                LLAMA3_1_8B_ELICEAI_HELPY_EDU_B_PRETRAINED_ID,
                QuantizationConfig.w_16_a_16_kv_16(),
            ),
            (
                SOLAR_10D7B_INSTRUCT_PRETRAINED_ID,
                QuantizationConfig.w_f8_a_f8_kv_f8(),
            ),
        }
        if (self.pretrained_id, self.quantization_config) in UNAVAILABLE_PAIRS:
            return False

        # All w4a16 models are temporarily unavailable.
        if self.quantization_config in (QuantizationConfig.w_4_a_16_kv_f8(),):
            return False

        return True

    def uses_models(self) -> Iterable[str]:
        return [self.name]

    # FIXME: make this robust
    def is_random_weight_only_model(self) -> bool:
        return "n_embd" in self.hf_configs

    def is_llama3_based(self) -> bool:
        return is_llama3_based(self.pretrained_id, type(self.config))

    @property
    def supports_speculative_decoding(self) -> bool:
        return self.optimize_options.optimized_for_speculative_decoding

    @property
    def seq_dim_in_logits(self) -> int:
        """Returns which dimension is sequence dimension in output logits tensor."""
        # This function is used for prefill last block slicing.
        if get_mapped_class_for_optimization(self.model_cls, self.pretrained_id) in {
            transformers.GPTJForCausalLM,
            transformers.BertForQuestionAnswering,
            transformers.LlamaForCausalLM,
            transformers.Qwen2ForCausalLM,
        }:
            return 1
        else:
            raise NotImplementedError(f"Sequence dimension in logits for model {self} is unknown")

    @property
    def head_dim_in_kv_cache(self) -> int:
        if self.contains_mlperf_opts and get_mapped_class_for_optimization(
            self.model_cls, self.pretrained_id
        ) in {
            transformers.GPTJForCausalLM,
            transformers.LlamaForCausalLM,
        }:
            return 2
        else:
            raise NotImplementedError(f"Head dimension in kv cache for model {self} is unknown")

    @property
    def batch_dim_in_mask(self) -> int:
        if self.task_type == "text-generation":
            return 0
        else:
            raise ValueError(f"Batch dimension in mask for model {self} is unknown")

    # TODO: add support for furiosa-models-lang models.
    def attn_dim_in_mask(self, phase: str) -> int:
        if self.contains_mlperf_opts and get_mapped_class_for_optimization(
            self.model_cls, self.pretrained_id
        ) in {
            transformers.GPTJForCausalLM,
            transformers.LlamaForCausalLM,
        }:
            if phase == "prefill":
                # expect 3d mask (b, s, s)
                return 2
            elif phase == "decode":
                if self.optimize_options.optimized_for_speculative_decoding:
                    # expect 3d mask (b, s, s)
                    return 2
                else:
                    # expect 2d mask (b, s)
                    return 1
            else:
                raise ValueError(f"Invalid phase: {phase}")
        else:
            raise ValueError(f"Attention dimension in mask for model {self} is unknown")

    @property
    def hidden_size(self) -> int:
        return self.config_dict.get("hidden_size") or self.config_dict["n_embd"]

    def get_output_logits_size(self, bucket: Bucket) -> Optional[int]:
        if not self.is_generative_model:
            return None
        if self.optimize_options.calculate_logit_only_for_last_token and bucket.is_prefill:
            return 1
        return bucket.input_ids_size

    def get_example_input(
        self,
        bucket: Bucket,
        paged_attention_num_blocks: Optional[int] = None,
        paged_attention_block_size: Optional[int] = None,
        kv_cache_sharing_across_beams_config: Optional[KvCacheSharingAcrossBeamsConfig] = None,
        random_value: bool = False,
    ) -> Tuple[Tuple, Dict]:
        if self.attention_type is AttentionType.PAGED_ATTENTION:
            if not paged_attention_num_blocks:
                raise ValueError(
                    "`paged_attention_num_blocks` should be given for paged attention models."
                )
            if not paged_attention_block_size:
                raise ValueError(
                    "`paged_attention_block_size` should be given for paged attention models."
                )
        else:
            if paged_attention_num_blocks is not None:
                raise ValueError(
                    "`paged_attention_num_blocks` should be given if and only if the model is paged attention model."
                )
            if paged_attention_block_size is not None:
                raise ValueError(
                    "`paged_attention_block_size` should be given if and only if the model is paged attention model."
                )

        if self.is_beam_search_kv_cache_sharing_model:
            if not kv_cache_sharing_across_beams_config:
                raise ValueError(
                    "`kv_cache_sharing_across_beams_config` should be given if the model is optimized for kv cache sharing across beams."
                )
        else:
            if kv_cache_sharing_across_beams_config is not None:
                raise ValueError(
                    "`kv_cache_sharing_across_beams_config` should be given if and only if the model is optimized for kv cache sharing across beams."
                )

        if not self.is_generative_model and not bucket.is_prefill:
            raise ValueError("encoder-only model supports prefill mode only")

        use_causal_mask = self.optimize_options.causal_mask_free_decoding

        return (), generate_input_sample(
            self.get_optimized_cls(),
            self.config,
            bucket,
            self.kv_cache_torch_dtype,
            paged_attention_num_blocks,
            paged_attention_block_size,
            kv_cache_sharing_across_beams_config,
            self.optimize_options.optimize_packed,
            self.is_compact_causal_mask_for_bert(),
            use_causal_mask,
            self.supports_speculative_decoding,
            self.need_quant_artifacts,
            self.optimize_options.calculate_logit_only_for_last_token,
            self.optimize_options.use_2d_masks,
            self.optimize_options.merged_kv_indices,
            random_value=random_value,
        )


# NOTE: make sure to sync the logic with the rust-side implementation in `furiosa-llm-common/src/config.rs`
class GeneratorModelMetadata(BaseModel):
    pretrained_id: str
    hf_config: Dict[str, Any] = Field(default_factory=dict)
    eos_token_ids: list[int]
    kv_cache_dtype: Optional[QDtype]
    task_type: Optional[str]
    separate_shared_prompt_kv_indices_nbeam: Optional[int]
    from_furiosa_llm_models: bool

    @staticmethod
    def from_model_metadata(
        generator_config: GeneratorConfig,
        hf_config: Dict[str, Any],
        metadata: ModelMetadata,
    ) -> "GeneratorModelMetadata":
        # field type: `List[int] | int | None`
        eos_token_id_val = hf_config['eos_token_id']
        if isinstance(eos_token_id_val, list):
            eos_token_ids = eos_token_id_val
        elif isinstance(eos_token_id_val, int):
            eos_token_ids = [eos_token_id_val]
        else:
            assert eos_token_id_val is None
            eos_token_ids = []

        beam_config = generator_config.kv_cache_sharing_across_beams_config
        from_furiosa_llm_models = generator_config.model_qname.startswith("furiosa_llm_models.")
        kv_cache_dtype = (
            metadata.llm_config.quantization_config.kv_cache
            if metadata.llm_config.quantization_config
            else QDtype.FP32
        )

        return GeneratorModelMetadata(
            pretrained_id=metadata.pretrained_id,
            hf_config=hf_config,
            eos_token_ids=eos_token_ids,
            kv_cache_dtype=kv_cache_dtype,
            task_type=metadata.task_type,
            separate_shared_prompt_kv_indices_nbeam=(
                beam_config.beam_width if beam_config is not None else None
            ),
            from_furiosa_llm_models=from_furiosa_llm_models,
        )


def _get_bucket_from_pipeline_name(pipeline_name: str) -> Bucket:
    # Returns: tuple of (is_prefill, bucket)
    # Possible pipeline name formats:
    # * f"{model_name}-{mode}-b{bucket.batch_size}-attn{bucket.attention_size} (will be deprecated)
    # * f"{model_name}-kv{bucket.kv_cache_size}-b{bucket.batch_size}-attn{bucket.attention_size}
    _, mode_or_kv_cache_size, b_batch_size, attn_attn_size = pipeline_name.split("-")

    batch_size = int(b_batch_size[1:])
    attn_size = int(attn_attn_size[4:])

    if mode_or_kv_cache_size == "prefill":
        kv_size = 0
    elif mode_or_kv_cache_size == "decode":
        kv_size = attn_size - 1
    else:
        assert mode_or_kv_cache_size.startswith("kv")
        kv_size = int(mode_or_kv_cache_size[2:])

    return Bucket(batch_size, attn_size, kv_size)


# NOTE: make sure to sync the logic with the rust-side implementation in `furiosa-llm-common/src/config.rs`
class GeneratorPipelineMetadata(BaseModel):
    batch_size: int
    attention_size: int
    kv_cache_size: int
    output_logits_size: Optional[int]
    include_softmax_in_graph: bool
    mask_dim: int

    @staticmethod
    def from_pipeline_metadata(
        generator_config: GeneratorConfig,
        pipelines: Sequence["Pipeline"],
        pipeline_metadata: Sequence[PipelineMetadata],
    ) -> list["GeneratorPipelineMetadata"]:
        # TODO: use actual model info, not match over qname
        model_qname = generator_config.model_qname

        if model_qname in [
            "furiosa_llm_models.gptj.symbolic.mlperf_submission.GPTJForCausalLM",
            "furiosa_llm_models.gptj.symbolic.mlperf_submission_slice.GPTJForCausalLM",
        ]:
            include_softmax_in_graph = True
            prefill_mask_dim = 3
            decode_mask_dim = 2
        elif model_qname in [
            "furiosa_llm_models.bert.symbolic.mlperf_submission.BertForQuestionAnswering",
            "furiosa_llm_models.llama3.symbolic.llama3.LlamaForCausalLM",
            "furiosa_llm_models.llama3.symbolic.llama3_merged_kv_idx.LlamaForCausalLM",
            "transformers.models.gptj.modeling_gptj.GPTJForCausalLM",
        ]:
            include_softmax_in_graph = False
            prefill_mask_dim = 2
            decode_mask_dim = 2
        elif model_qname in [
            "furiosa_llm_models.llama.symbolic.mlperf_submission.LlamaForCausalLM",
            "furiosa_llm_models.llama3.symbolic.mlperf_submission.LlamaForCausalLM",
            "furiosa_llm_models.llama.symbolic.mlperf_submission_slice.LlamaForCausalLM",
            "furiosa_llm_models.llama3.symbolic.mlperf_submission_slice.LlamaForCausalLM",
        ]:
            include_softmax_in_graph = False
            prefill_mask_dim = 3
            decode_mask_dim = 2
        elif model_qname in [
            "furiosa_llm_models.llama3.symbolic.aramco_specdec.LlamaForCausalLM",
            "furiosa_llm_models.llama3.symbolic.aramco_specdec_slice_integrated.LlamaForCausalLM",
            "furiosa_llm_models.llama3.symbolic.aramco_specdec_merged_kv_idx.LlamaForCausalLM",
            "furiosa_models.architecture.models.qwen2.Qwen2ForCausalLM",
        ]:
            include_softmax_in_graph = False
            prefill_mask_dim = 3
            decode_mask_dim = 3
        else:
            raise ValueError(f"unknown model qname: {model_qname}")

        # TODO: avoid getting bucket from pipeline name and directly include it in
        # pipeline metadata.
        buckets = [_get_bucket_from_pipeline_name(pipeline.name) for pipeline in pipelines]

        return [
            GeneratorPipelineMetadata(
                batch_size=bucket.batch_size,
                attention_size=bucket.attention_size,
                kv_cache_size=bucket.kv_cache_size,
                output_logits_size=pipeline.output_logits_size,
                include_softmax_in_graph=include_softmax_in_graph,
                # TODO: specify fine-grained per-pipeline mask dimension
                mask_dim=prefill_mask_dim if bucket.is_prefill else decode_mask_dim,
            )
            for bucket, pipeline in zip_equal(buckets, pipeline_metadata)
        ]


class GeneratorMetadata(BaseModel):
    model_metadata: GeneratorModelMetadata
    pipeline_metadata: list[GeneratorPipelineMetadata]


def dump_generator_metadata_json(
    generator_config: GeneratorConfig,
    model_config: Dict[str, Any],
    model_metadata: ModelMetadata,
    pipelines: Sequence["Pipeline"],
    pipeline_metadata: Sequence[PipelineMetadata],
) -> str:
    generator_metadata = GeneratorMetadata(
        model_metadata=GeneratorModelMetadata.from_model_metadata(
            generator_config,
            model_config,
            model_metadata,
        ),
        pipeline_metadata=GeneratorPipelineMetadata.from_pipeline_metadata(
            generator_config, pipelines, pipeline_metadata
        ),
    )

    return generator_metadata.model_dump_json()


def _qdtype_to_model_lang_dtype(qdtype: QDtype) -> str:
    if qdtype is QDtype.FP32:
        return "float32"
    elif qdtype is QDtype.BF16:
        return "bfloat16"
    else:
        raise ValueError(f"Unsupported qdtype: {qdtype}")
