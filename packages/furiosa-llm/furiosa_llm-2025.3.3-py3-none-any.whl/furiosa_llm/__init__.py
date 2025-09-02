""" "Furiosa LLM"""

# Importing absolute path in order to avoid cyclic imports
import logging

from furiosa_llm.version import FURIOSA_LLM_VERSION

from . import models as models
from . import parallelize as parallelize
from .api import LLM, Bucket, GeneratorConfig, LLMBackend, RequestOutput

try:
    from .llm_engine import AsyncEngineArgs, AsyncLLMEngine, EngineArgs, LLMEngine
except ImportError as e:
    logging.warning(f"Failed to import LLMEngine with error: {e}")
from .sampling_params import GuidedDecodingParams, SamplingParams

__version__ = FURIOSA_LLM_VERSION


def full_version() -> str:
    """Returns a full version from furiosa-llm version"""
    try:
        import furiosa.native_runtime as rt

        return "Furiosa LLM {} (furiosa-rt {} {} {})".format(
            __version__,
            rt.__version__,
            rt.__git_short_hash__,
            rt.__build_timestamp__,
        )
    except ImportError:
        return f"Furiosa LLM {__version__} (w/o furiosa-rt)"


__full_version__ = full_version()

__all__ = [
    "__version__",
    "__full_version__",
    "AsyncEngineArgs",
    "AsyncLLMEngine",
    "Bucket",
    "EngineArgs",
    "GeneratorConfig",
    "GuidedDecodingParams",
    "LLM",
    "LLMEngine",
    "LLMBackend",
    "parallelize",
    "RequestOutput",
    "SamplingParams",
]
