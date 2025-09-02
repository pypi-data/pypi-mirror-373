from collections import OrderedDict
import importlib.resources as resources
import json
import logging
import math
from typing import Any, Dict, Optional, Union

from transformers import PretrainedConfig

DEFAULT_KEY_FILTERS = [
    "auto_map",  # doesn't affect the model architecture
    "bos_token_id",  # doesn't affect the model architecture
    "eos_token_id",  # doesn't affect the model architecture
    "_name_or_path",  # doesn't affect the model architecture
    "head_dim",  # ignore because most models calculate it from hidden_size // num_attention_heads
    "n_layer",  # Compiler can handle different numbers of transformers blocks
    "num_layers",  # Compiler can handle different numbers of transformers blocks
    "num_hidden_layers",  # Compiler can handle different numbers of transformers blocks
    "max_window_layers",  # compared in _check_max_window_layers
    "max_position_embeddings",  # doesn't affect the model architecture
    "rms_norm_eps",  # doesn't affect the model architecture
    "rope_scaling",  # doesn't affect the model architecture,
    "rope_theta",  # doesn't affect the model architecture,
    "sliding_window",  # compared in _check_max_window_layers
    "use_cache",  # doesn't affect the model architecture
    "use_sliding_window",  # compared in _check_max_window_layers
    "torch_dtype",  # Check the allowance of compiler
    "transformers_version",  # doesn't affect the model architecture
    "vocab_size",  # It may be trivial. Remove this if it causes a problem.
]

# The difference of boolean flag existences would be Ok if the default value of
# the missing config is the same as that of the existences config.
BOOLEAN_FLAG_KEYS = [
    # some model configs of Qwen2.5 family include use_mrope, but the code does nothing with this config.
    ("use_mrope", False)
]

UNSUPPORTED_CONFIG_KEYS = [
    "compression_config",  # not supported now
]


def sort_config(d):
    """Recursively sort a dictionary by its keys."""
    if isinstance(d, dict):
        return OrderedDict(
            sorted(((k, sort_config(v)) for k, v in d.items()), key=lambda item: item[0])
        )
    if isinstance(d, list):
        return [sort_config(x) for x in d]
    return d


def filter_keys(d, keys_to_filter):
    """Recursively filter out specified keys from a dictionary."""
    if isinstance(d, dict):
        return OrderedDict(
            (k, filter_keys(v, keys_to_filter)) for k, v in d.items() if k not in keys_to_filter
        )
    if isinstance(d, list):
        return [filter_keys(x, keys_to_filter) for x in d]
    return d


def _compare_configs_recursively(
    base: Dict[str, Any], other: Dict[str, Any], path: str = ""
) -> bool:
    """
    Recursively compares two dictionaries based on the keys present in the base config.
    It checks if all keys and their corresponding values in `base` exist and are identical in `other`.
    Keys present in `other` but not in `base` are ignored.
    """
    for key, base_value in base.items():
        current_path = f"{path}.{key}" if path else key
        if key not in other:
            logging.debug(f"Key '{current_path}' from base config not found in the other config.")
            return False

        other_value = other[key]

        is_base_dict = isinstance(base_value, (dict, OrderedDict))
        is_other_dict = isinstance(other_value, (dict, OrderedDict))

        if is_base_dict and is_other_dict:
            if not _compare_configs_recursively(base_value, other_value, path=current_path):
                return False
        elif base_value != other_value:
            logging.debug(
                f"value mismatch for key '{current_path}': base is '{base_value}', other is '{other_value}'"
            )
            return False
    return True


def _check_dtype_compatibility(base: Dict[str, Any], other: Dict[str, Any]) -> bool:
    """
    Matches the torch_dtype in the base and other configurations.
    If torch_dtype is not present in either, it defaults to float32.
    """
    base_dtype = base.get("torch_dtype", "float32")
    other_dtype = other.get("torch_dtype", "float32")

    if base_dtype != other_dtype:
        # Even though the dtype is different, we still allow float32, bfloat16, and float16
        if other_dtype not in ("float32", "bfloat16", "float16"):
            logging.debug(f"Unsupported torch_dtype '{other_dtype}' in other config.")
            return False

    return True


def _check_sliding_window(base: Dict[str, Any], other: Dict[str, Any]) -> bool:
    base_use_sliding_window = base.get("use_sliding_window", False)
    other_use_sliding_window = other.get("use_sliding_window", False)
    base_max_window_layers = base.get("max_window_layers", 0)
    other_max_window_layers = other.get("max_window_layers", 0)
    base_sliding_window = base.get("sliding_window", 0)
    other_sliding_window = other.get("sliding_window", 0)

    if not base_use_sliding_window and not other_use_sliding_window:
        return True

    if base_use_sliding_window != other_use_sliding_window:
        # If one config has use_sliding_window enabled and the other does not, they are incompatible
        logging.debug(
            f"Mismatch in use_sliding_window: base is {base_use_sliding_window}, "
            f"other is {other_use_sliding_window}."
        )
        return False

    # we need to compare max_window_layers only if both configs have use_sliding_window enabled
    if base_use_sliding_window and other_use_sliding_window:
        if base_max_window_layers != other_max_window_layers:
            logging.debug(
                f"Mismatch in max_window_layers: base is {base_max_window_layers}, "
                f"other is {other_max_window_layers}."
            )
            return False

        if base_sliding_window != other_sliding_window:
            logging.debug(
                f"Mismatch in sliding_window: base is {base_sliding_window}, "
                f"other is {other_sliding_window}."
            )
            return False

    return True


def _check_config_compatibility(other: Dict[str, Any]) -> bool:
    for key in UNSUPPORTED_CONFIG_KEYS:
        if key in other:
            logging.warning(f"Unsupported config key '{key}' found in the other config.")
            return False

    return True


def _check_vocab_size(base: Dict[str, Any], other: Dict[str, Any]) -> bool:
    """Allow vocab_size difference within 4% of the base model's vocab_size.

    A tolerance proportional to the base vocab size is often needed because
    models can be extended with a small number of new tokens (e.g., added
    special tokens or fine‑tuning artifacts). Using a percentage keeps the
    rule flexible across small and large vocabularies.
    """
    max_tolerance_factor = 0.04
    base_vocab_size = base.get("vocab_size")
    other_vocab_size = other.get("vocab_size")

    if base_vocab_size is None:
        raise ValueError("vocab_size in base model is missing")
    if other_vocab_size is None:
        raise ValueError("vocab_size in other model is missing")

    try:
        base_vocab_size = int(base_vocab_size)
        other_vocab_size = int(other_vocab_size)
    except (TypeError, ValueError):
        raise ValueError(
            f"Non-integer vocab_size encountered (base={base_vocab_size}, other={other_vocab_size})."
        )

    if base_vocab_size < 0 or other_vocab_size < 0:
        logging.debug(
            f"Negative vocab_size encountered (base={base_vocab_size}, other={other_vocab_size})."
        )
        return False

    diff = abs(base_vocab_size - other_vocab_size)
    # Allowed tolerance: floor of max_tolerance_factor (so diff must be <= tolerance).
    # For small vocabs this may be 0. It should be Ok.
    tolerance = math.ceil(base_vocab_size * max_tolerance_factor)

    if diff > tolerance:
        logging.debug(
            "Mismatch in vocab_size: base is %s, other is %s (diff=%d > max_tolerance=%d%% tolerance=%d).",
            base_vocab_size,
            other_vocab_size,
            diff,
            max_tolerance_factor * 100,
            tolerance,
        )
        return False

    return True


def _check_boolean_flags(base: Dict[str, Any], other: Dict[str, Any]) -> bool:
    for key, default in BOOLEAN_FLAG_KEYS:
        base_value = base.pop(key, default)
        other_value = other.pop(key, default)
        if base_value != other_value:
            logging.debug(
                f"Mismatch in boolean flag '{key}': base is {base_value}, other is {other_value}."
            )
            return False
    return True


def default_matcher(base: Dict[str, Any], other: Dict[str, Any]) -> bool:
    # Precondition check: this assumes that both base and other have the same model_type.
    assert base['model_type'] == other['model_type'], "Model types do not match"

    # If _name_or_path is the same, we can consider them compatible
    if base.get("_name_or_path") == other.get("_name_or_path"):
        return True

    # If other includes unsupported keys
    if not _check_config_compatibility(other):
        return False

    # Check if quantization_config exists in both configs or not.
    # If both have it, we can compare it in _compare_configs_recursively
    if ('quantization_config' in base) != ('quantization_config' in other):
        logging.debug("Mismatch: `quantization_config` must be in both or neither")
        return False

    if not _check_dtype_compatibility(base, other):
        logging.debug("Mismatch: `torch_dtype` does not match")
        return False

    if not _check_sliding_window(base, other):
        logging.debug("Mismatch: `max_window_layers` does not match")
        return False

    if not _check_vocab_size(base, other):
        logging.debug("Mismatch: `vocab_size` differs beyond tolerance")
        return False

    if not _check_boolean_flags(base, other):
        return False

    # Sort and filter the dictionaries
    base = sort_config(filter_keys(base, DEFAULT_KEY_FILTERS))
    other = sort_config(filter_keys(other, DEFAULT_KEY_FILTERS))

    return _compare_configs_recursively(base, other)


# Invariant: Configs of the same model type must be distinguishable from one another.
def find_canonical_model_id(config: Union[Dict[str, Any], PretrainedConfig]) -> Optional[str]:
    """
    Finds a canonical model ID for a given Hugging Face model configuration.

    The candidate model ID is used to determine a Compiler Config and
    how a given model is optimized with specific options.

    Args:
        config: The Hugging Face model configuration.

    Returns:
        The canonical model ID of the matching configuration.
    """
    if isinstance(config, PretrainedConfig):
        config = config.to_dict()

    model_type = config['model_type']
    local_configs = {}

    try:
        # Use importlib.resources to list files in the directory
        package = f"furiosa_llm.optimum.configs.{model_type}"
        files = resources.files(package)
        for item in files.iterdir():
            if item.is_file() and item.name.endswith(".json"):
                # Restore model_id from filename (e.g., "org_model-name.json" -> "org/model-name")
                model_id = item.name[:-5].replace("_", "/", 1)
                config_text = item.read_text(encoding="utf-8")
                local_configs[model_id] = json.loads(config_text)
    except ModuleNotFoundError:
        raise ValueError(f"No local configurations found for model type '{model_type}'")

    # Find a config with the same architectures
    for model_id, local_config in local_configs.items():
        logging.debug(f"Comparing {model_id} with {config['_name_or_path']}")
        if default_matcher(local_config, config):
            return model_id

    logging.warning(
        f"Could not find a matching config for model_type='{model_type}' and "
        f"architectures='{config['architectures']}'. "
        f"Available configs for this model type: {list(local_configs.keys())}"
    )
    return None
