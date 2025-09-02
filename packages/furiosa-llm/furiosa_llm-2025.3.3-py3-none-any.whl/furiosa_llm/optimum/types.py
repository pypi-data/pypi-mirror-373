from enum import Enum
import functools
import importlib
import json
import logging
import os
import re
from typing import Any, Dict, Final, FrozenSet, List, Optional, Set, Type, Union

from pydantic import BaseModel, Field, RootModel, field_serializer, field_validator, model_validator
import torch
from typing_extensions import Self

logger = logging.getLogger(__name__)


FURIOSA_CONFIG_VERSION = "1.0.0"

WEIGHT_QDTYPE_FIELD_NAME_IN_QFORMAT: Final[str] = "weight_dtype"
ACTIVATION_QDTYPE_FIELD_NAME_IN_QFORMAT: Final[str] = "act_dtype"
KVCACHE_QDTYPE_FIELD_NAME_IN_QFORMAT: Final[str] = "kv_dtype"


@functools.total_ordering
class AttentionType(str, Enum):
    VANILLA = "VANILLA"
    PAGED_ATTENTION = "PAGED_ATTENTION"
    # preallocate memory space for kv cache, return in-place updated kv cache (concat)
    PREALLOCATION_CONCAT = "PREALLOCATION_CONCAT"

    def __lt__(self, other):
        if not isinstance(other, AttentionType):
            return NotImplemented
        return self.value < other.value


@functools.total_ordering
class OptimizationConfig(BaseModel):
    attention_type: AttentionType = AttentionType.VANILLA
    optimize_rope: bool = False
    optimize_packed: bool = False
    decompose_layernorm: bool = False
    optimize_furiosa: bool = False
    use_unsplit_packed: bool = False
    compact_causal_mask: bool = False
    use_rngd_gelu: bool = False
    causal_mask_free_decoding: bool = False
    kv_cache_sharing_across_beams: bool = False
    inbound_beamsearch_softmax: bool = False
    # https://furiosa-ai.slack.com/archives/C06R68UU9DJ/p1720453142548739
    calculate_logit_only_for_last_token: bool = False
    optimized_for_speculative_decoding: bool = False
    use_2d_masks: bool = False
    merged_kv_indices: bool = False

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other):
        return repr(self) < repr(other)

    def get_activated_options(self) -> FrozenSet[str]:
        return frozenset(
            key
            for key, value in self.model_dump().items()
            if value and key not in {"attention_type"}
        )

    def get_all_flags(self) -> FrozenSet[str]:
        return frozenset(key for key in self.model_dump() if key != "attention_type")

    def contains(self, other: "OptimizationConfig") -> bool:
        return self.get_enabled_opts().issuperset(other.get_enabled_opts())

    def get_enabled_opts(self) -> Set[str]:
        return {
            k
            for k, v in self.model_dump().items()
            if (k == "attention_type" and v != AttentionType.VANILLA)
            or (k != "attention_type" and v)
        }

    def with_optimizations(self, opts: Dict[str, Any]) -> "OptimizationConfig":
        new_dict = self.model_dump()
        new_dict.update(opts)
        return OptimizationConfig(**new_dict)


class QDtype(str, Enum):
    INT4 = "int4"
    INT8 = "int8"
    FP8 = "fp8"
    BF16 = "bf16"
    FP32 = "fp32"

    @classmethod
    def from_qformat_dtype(cls, dtype: str) -> "QDtype":
        if dtype == "int8":
            return QDtype.INT8
        elif dtype == "fp8-E4M3":
            return QDtype.FP8
        elif dtype == "bf16":
            return QDtype.BF16
        else:
            raise ValueError(f"Unsupported qformat dtype string: {dtype}")

    def to_qformat(self) -> str:
        if self == QDtype.INT4:
            return "int4"
        elif self == QDtype.INT8:
            return "int8"
        elif self == QDtype.FP8:
            return "fp8-E4M3"
        elif self == QDtype.BF16:
            return "bf16"
        else:
            raise ValueError(f"{self}.to_qformat_dtype() is not supported")

    def bits(self) -> int:
        if self == QDtype.INT4:
            return 4
        elif self in (QDtype.INT8, QDtype.FP8):
            return 8
        elif self == QDtype.BF16:
            return 16
        else:
            raise ValueError(f"{self}.bits() is not supported")

    def to_torch_dtype(self) -> torch.dtype:
        if self is QDtype.INT4:
            # NOTE: There's no int4 type in torch. int8 is used instead.
            return torch.int8
        elif self is QDtype.INT8:
            return torch.int8
        elif self is QDtype.FP8:
            # NOTE: We decided to use torch.int8 to represent fp8 in compression stack.
            return torch.int8
        elif self is QDtype.BF16:
            return torch.bfloat16
        elif self is QDtype.FP32:
            return torch.float32
        else:
            raise ValueError(f"{self} has no corresponding torch dtype")

    def suffix(self):
        return QDTYPE_TO_SUFFIX_MAPPING[self]

    @classmethod
    def from_suffix(cls, val: str) -> "QDtype":
        return SUFFIX_TO_QDTYPE_MAPPING[val]


SUFFIX_TO_QDTYPE_MAPPING = {
    "4": QDtype.INT4,
    "8": QDtype.INT8,
    "8f": QDtype.FP8,
    "16": QDtype.BF16,
}

QDTYPE_TO_SUFFIX_MAPPING = {v: k for k, v in SUFFIX_TO_QDTYPE_MAPPING.items()}


def get_field_dtype_from_qformat(field_name: str, qformat_path: Union[os.PathLike, str]) -> QDtype:
    with open(qformat_path, "r") as f:
        metadata_line = f.readline()
    matched = re.search(rf"--{field_name} \S+\b", metadata_line)
    if not matched:
        raise ValueError(f"Cannot find kv_cache_dtype from '{metadata_line}'")
    dtype = matched.group().split()[-1]

    try:
        return QDtype.from_qformat_dtype(dtype)
    except Exception:
        raise RuntimeError(f"Failed to parse dtype information for {field_name} in qformat file.")


def get_kv_cache_dtype_from_qformat(qformat_path: Union[os.PathLike, str]) -> QDtype:
    return get_field_dtype_from_qformat(KVCACHE_QDTYPE_FIELD_NAME_IN_QFORMAT, qformat_path)


@functools.total_ordering
class QuantizationConfig(BaseModel):
    weight: QDtype
    activation: QDtype
    kv_cache: Optional[QDtype]
    use_mcp: bool = True

    @model_validator(mode="after")
    def validate_quantization_config(self):
        if not self.use_mcp and not self != QuantizationConfig.w_16_a_16_kv_16():
            raise ValueError(f"{self} type needs mcp.")
        return self

    @classmethod
    def from_qformat(cls, qformat_path: Union[os.PathLike, str]) -> Self:
        weight_type = get_field_dtype_from_qformat(
            WEIGHT_QDTYPE_FIELD_NAME_IN_QFORMAT, qformat_path
        )
        act_dtype = get_field_dtype_from_qformat(
            ACTIVATION_QDTYPE_FIELD_NAME_IN_QFORMAT, qformat_path
        )
        try:
            kv_dtype = get_kv_cache_dtype_from_qformat(qformat_path)
        except ValueError:
            kv_dtype = None
        return cls(
            weight=weight_type,
            activation=act_dtype,
            kv_cache=kv_dtype,
            use_mcp=True,
        )

    def __hash__(self) -> int:
        return hash(repr(self))

    @classmethod
    def w_i8_a_i8_kv_i8(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.INT8, activation=QDtype.INT8, kv_cache=QDtype.INT8)

    @classmethod
    def w_i8_a_i8(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.INT8, activation=QDtype.INT8, kv_cache=None)

    @classmethod
    def w_f8_a_f8_kv_f8(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.FP8, activation=QDtype.FP8, kv_cache=QDtype.FP8)

    @classmethod
    def w_f8_a_f8(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.FP8, activation=QDtype.FP8, kv_cache=None)

    @classmethod
    def w_4_a_16_kv_f8(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.INT4, activation=QDtype.BF16, kv_cache=QDtype.FP8)

    @classmethod
    def w_16_a_16_kv_16(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.BF16, activation=QDtype.BF16, kv_cache=QDtype.BF16)

    @classmethod
    def w_16_a_16(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.BF16, activation=QDtype.BF16, kv_cache=None)

    @classmethod
    def w_16_a_16_kv_16_no_mcp(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.BF16, activation=QDtype.BF16, kv_cache=QDtype.BF16, use_mcp=False)

    @classmethod
    def w_8_a_16_kv_16(cls) -> "QuantizationConfig":
        return cls(weight=QDtype.INT8, activation=QDtype.BF16, kv_cache=QDtype.BF16)

    @property
    def is_bf16(self) -> bool:
        return (
            self.weight is QDtype.BF16
            and self.activation is QDtype.BF16
            and self.kv_cache in (None, QDtype.BF16)
        )

    @field_serializer('weight', 'activation', 'kv_cache')
    def serialize(self, dtype: Optional[QDtype]) -> Optional[str]:
        return dtype.value if dtype else None

    @field_validator('weight', 'activation', 'kv_cache', mode="before")
    @classmethod
    def deserialize(cls, dtype: Union[None, str, QDtype]) -> Optional[QDtype]:
        if dtype is None:
            return None
        if isinstance(dtype, QDtype):
            return dtype
        elif isinstance(dtype, str):
            return QDtype(dtype)
        raise ValueError(f"Invalid dtype: {dtype!r}")

    # NOTE: This method should be synced with from_str.
    def __str__(self) -> str:
        return "W{}A{}{}{}".format(
            self.weight.suffix(),
            self.activation.suffix(),
            f"KV{self.kv_cache.suffix()}" if self.kv_cache else "",
            "_NO_MCP" if not self.use_mcp else "",
        )

    @classmethod
    # NOTE: This method should be synced with __str__.
    def from_str(cls, val: str) -> Self:
        pattern = re.compile(
            r"W(?P<weight>[a-z0-9]+)A(?P<activation>[a-z0-9]+)(KV(?P<kv_cache>[a-zA-Z0-9]+))?(?P<no_mcp>_NO_MCP)?"
        )
        match = pattern.match(val)
        if not match:
            raise ValueError(f"Invalid string format: {val}")

        weight_dtype = QDtype.from_suffix(match.group("weight"))
        activation_dtype = QDtype.from_suffix(match.group("activation"))
        kv_cache_dtype = (
            QDtype.from_suffix(match.group("kv_cache")) if match.group("kv_cache") else None
        )
        use_mcp = match.group("no_mcp") is None

        return cls(
            weight=weight_dtype,
            activation=activation_dtype,
            kv_cache=kv_cache_dtype,
            use_mcp=use_mcp,
        )

    def to_compiler_notation(self) -> str:
        """Convert into notation that can be converted into `QType` in dram shape guide generator."""
        if not self.kv_cache:
            raise ValueError(
                "Quantization config without kv cache dtype cannot be converted into compiler qtype notation."
            )
        if self.weight == self.activation == self.kv_cache:
            return f"w{self.weight.suffix()}a{self.activation.suffix()}"
        return f"w{self.weight.suffix()}a{self.activation.suffix()}kv{self.kv_cache.suffix()}"

    def __lt__(self, other):
        return str(self) < str(other)


class ModelClass(BaseModel, frozen=True):
    module: str
    name: str

    @classmethod
    def from_class(cls, clazz: Type) -> "ModelClass":
        return cls(module=clazz.__module__, name=clazz.__name__)


class ModelKind(Enum):
    QUANTIZED_MODEL = "QUANTIZED_MODEL"
    ARTIFACT = "ARTIFACT"


class VersionInfo(BaseModel):
    version: str
    git_hash: Optional[str]
    build_time: Optional[str]

    def __init__(
        self, version: str, git_hash: Optional[str] = None, build_time: Optional[str] = None
    ):
        super(VersionInfo, self).__init__(
            version=version,
            git_hash=git_hash,
            build_time=build_time,
        )


class ComponentVersions(BaseModel, frozen=True):
    furiosa_llm: VersionInfo
    furiosa_ir: VersionInfo
    furiosa_runtime: VersionInfo
    furiosa_model_compressor: VersionInfo

    @classmethod
    def default(cls) -> "ComponentVersions":
        import model_compressor as mcp

        import furiosa.native_runtime
        from furiosa_llm.version import FURIOSA_LLM_VERSION

        return ComponentVersions(
            furiosa_llm=VersionInfo(
                FURIOSA_LLM_VERSION.version + "-" + FURIOSA_LLM_VERSION.stage,
                FURIOSA_LLM_VERSION.hash,
            ),
            furiosa_runtime=VersionInfo(
                furiosa.native_runtime.__version__,
                furiosa.native_runtime.__git_short_hash__,
                furiosa.native_runtime.__build_timestamp__,
            ),
            furiosa_ir=VersionInfo(
                furiosa.native_runtime.__ir_version__,  # type: ignore
                furiosa.native_runtime.__ir_git_short_hash__,  # type: ignore
                furiosa.native_runtime.__ir_build_timestamp__,  # type: ignore
            ),
            furiosa_model_compressor=VersionInfo(version=mcp.__version__),
        )


class LLMConfig(BaseModel, frozen=True):
    optimization_config: OptimizationConfig = OptimizationConfig()
    quantization_config: Optional[QuantizationConfig] = None

    def __init__(
        self,
        optimization_config: OptimizationConfig = OptimizationConfig(),
        quantization_config: Optional[QuantizationConfig] = None,
    ):
        super(LLMConfig, self).__init__(
            optimization_config=optimization_config, quantization_config=quantization_config
        )

    def with_quantization_config(self, quantization_config: QuantizationConfig) -> "LLMConfig":
        return self.model_copy(
            update={
                "quantization_config": quantization_config,
            },
            deep=True,
        )

    def with_optimizations(self, opts: Dict[str, Any]) -> "LLMConfig":
        return self.model_copy(
            update={
                "optimization_config": self.optimization_config.with_optimizations(opts),
            },
            deep=True,
        )


class FuriosaConfig(BaseModel, frozen=True):
    config_version: str
    model_id: str
    model_kinds: List[ModelKind]
    model_class: ModelClass  # model class to compile (i.e. *_mlperf_submission)
    llm_config: LLMConfig = Field(default_factory=LLMConfig)
    components_versions: ComponentVersions

    def __init__(
        self,
        model_id: str,
        model_kinds: List[ModelKind],
        model_class: ModelClass,
        llm_config: LLMConfig,
        components_versions: ComponentVersions = ComponentVersions.default(),
        config_version: str = FURIOSA_CONFIG_VERSION,
    ):
        super(FuriosaConfig, self).__init__(
            config_version=config_version,
            model_id=model_id,
            model_kinds=model_kinds,
            model_class=model_class,
            llm_config=llm_config,
            components_versions=components_versions,
        )

    def import_model_class(self) -> Type:
        """
        Returns the model class.
        """
        module = importlib.import_module(self.model_class.module)
        return getattr(module, self.model_class.name)

    def export(self, path: Union[str, os.PathLike]):
        with open(path, "w") as f:
            f.write(RootModel[FuriosaConfig](self).model_dump_json(indent=2))

    @classmethod
    def load(cls, path: Union[str, os.PathLike]) -> "FuriosaConfig":
        try:
            with open(path) as f:
                o = json.load(f)
                return FuriosaConfig(**o)
        except Exception as e:
            logger.error(e)
            raise ValueError("FuriosaConfig schema mismatched.")
