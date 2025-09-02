import logging
from pathlib import Path
from typing import List, Optional, Union

from torch import nn
from torch._dynamo import OptimizedModule
from transformers import (
    AutoTokenizer,
    BatchEncoding,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

from furiosa_llm.utils import get_logger_with_tz

logger = get_logger_with_tz(logging.getLogger(__name__))

# A fast LLaMA tokenizer with the pre-processed `tokenizer.json` file.
_FAST_LLAMA_TOKENIZER = "hf-internal-testing/llama-tokenizer"


def encode_auto(
    tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
    prompts: Union[str, List[str]],
    add_special_tokens: bool = False,
    **kwargs,
) -> BatchEncoding:
    # choose "longest" padding policy if prompts is batched.
    padding = "longest" if isinstance(prompts, (list, tuple)) else False
    return tokenizer(prompts, padding=padding, add_special_tokens=add_special_tokens, **kwargs)


def get_tokenizer(
    model_name_or_path: Union[str, Path, nn.Module, PreTrainedModel, OptimizedModule],
    tokenizer: Optional[Union[str, PreTrainedTokenizer, PreTrainedTokenizerFast]] = None,
    tokenizer_mode: str = "auto",
    trust_remote_code: Optional[bool] = None,
    revision: Optional[str] = None,
    **kwargs,
) -> Union[PreTrainedTokenizer, PreTrainedTokenizerFast]:
    """Gets a tokenizer for the given model name via Huggingface."""

    if tokenizer and isinstance(tokenizer, (PreTrainedTokenizer, PreTrainedTokenizerFast)):
        return tokenizer
    elif isinstance(tokenizer, str):
        tokenizer_id = tokenizer
    elif isinstance(model_name_or_path, str):
        tokenizer_id = model_name_or_path
    elif isinstance(model_name_or_path, Path):
        tokenizer_id = str(model_name_or_path)
    elif isinstance(model_name_or_path, (PreTrainedModel, OptimizedModule)):
        try:
            tokenizer_id = model_name_or_path.name_or_path
        except AttributeError:
            raise ValueError(
                "Tokenizer must be specified if model is not originated from Huggingface."
            )
    else:
        raise ValueError("tokenizer must be specified if model is nn.Module")

    if tokenizer_mode == "slow":
        if kwargs.get("use_fast", False):
            raise ValueError("Cannot use the fast tokenizer in slow tokenizer mode.")
        kwargs["use_fast"] = False
    if (
        "llama" in tokenizer_id.lower()
        and kwargs.get("use_fast", True)
        and tokenizer_id != _FAST_LLAMA_TOKENIZER
    ):
        logger.info(
            "For some LLaMA V1 models, initializing the fast tokenizer may "
            "take a long time. To reduce the initialization time, consider "
            f"using '{_FAST_LLAMA_TOKENIZER}' instead of the original "
            "tokenizer."
        )

    try:
        # WARN: We cannot make sure about side effect of padding_side="left" and setting up pad_token
        # for single batch encode/decode. Please confirm whether they have side effect or not later.
        tokenizer_ = AutoTokenizer.from_pretrained(
            tokenizer_id,
            padding_side="left",
            trust_remote_code=trust_remote_code,
            revision=revision,
            **kwargs,
        )
        if (
            tokenizer_.eos_token is not None
        ):  # To avoid setting NONE to pad_token in some models like bert
            tokenizer_.pad_token = tokenizer_.eos_token

    except TypeError as e:
        # The LLaMA tokenizer causes a protobuf error in some environments.
        err_msg = (
            "Failed to load the tokenizer. If you are using a LLaMA V1 model "
            f"consider using '{_FAST_LLAMA_TOKENIZER}' instead of the "
            "original tokenizer."
        )
        raise RuntimeError(err_msg) from e
    except ValueError as e:
        # If the error pertains to the tokenizer class not existing or not
        # currently being imported, suggest using the --trust-remote-code flag.
        if not trust_remote_code and (
            "does not exist or is not currently imported." in str(e)
            or "requires you to execute the tokenizer file" in str(e)
        ):
            err_msg = (
                "Failed to load the tokenizer. If the tokenizer is a custom "
                "tokenizer not yet available in the HuggingFace transformers "
                "library, consider setting `trust_remote_code=True` in LLM "
                "or using the `--trust-remote-code` flag in the CLI."
            )
            raise RuntimeError(err_msg) from e
        else:
            raise e

    if not isinstance(tokenizer_, PreTrainedTokenizerFast):
        logger.warning(
            "Using a slow tokenizer. This might cause a significant "
            "slowdown. Consider using a fast tokenizer instead."
        )

    tokenizer_.encode_auto = lambda prompt, **_kwargs: encode_auto(tokenizer_, prompt, **_kwargs)
    return tokenizer_
