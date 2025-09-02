import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Iterable, List, Optional, TypeVar

if sys.version_info >= (3, 10):
    def zip_equal(*iterables):  # fmt: skip
        return zip(*iterables, strict=True)
else:
    from more_itertools import zip_equal  # noqa


_modified_handlers = set()


def get_logger_with_tz(logger: logging.Logger) -> logging.Logger:
    """
    This function is used to add timezone info to logging.Logger's formatter.
    Mind that this function updates in-place, and the ancestor handlers of the logger as well.
    So if called to some logger, it may update the root logger as well.
    """
    global _modified_handlers
    current_logger: Optional[logging.Logger] = logger
    # Traverse up the logger hierarchy to modify all relevant handlers
    while current_logger:
        for handler in current_logger.handlers:
            if handler in _modified_handlers:
                continue
            _modified_handlers.add(handler)
            if handler.formatter:
                if handler.formatter.datefmt:
                    handler.formatter.datefmt += "%z"
                else:
                    handler.formatter.datefmt = logging.Formatter.default_time_format + "%z"
            else:
                handler.setFormatter(
                    logging.Formatter(datefmt=logging.Formatter.default_time_format + "%z")
                )
        if not current_logger.propagate:
            break
        current_logger = current_logger.parent

    return logger


T = TypeVar("T")


def get_list_with_no_dup_with_order_preserved(obj: Iterable[T]) -> List[T]:
    return list(dict.fromkeys(obj).keys())


# Borrowed from https://github.com/vllm-project/vllm/blob/6e1fc61f0fb90c37f0d4a1a8f76235a6e4e1103c/vllm/transformers_utils/config.py#L464,
# with some modifications (modifying vllm-specific parts and removing code for multiprocessing).
def maybe_register_config_serialize_by_value() -> None:
    """Try to register HF model configuration class to serialize by value

    If trust_remote_code is set, and the model's config file specifies an
    `AutoConfig` class, then the config class is typically an instance of
    a custom class imported from the HF modules cache.

    Examples:

    >>> from transformers import AutoConfig
    >>> klass = AutoConfig.from_pretrained('meta-llama/Llama-3.1-8B', trust_remote_code=True)
    >>> klass.__class__ # transformers.models.llama.configuration_llama.LlamaConfig
    >>> import transformers_modules # error, not initialized
    >>> klass = AutoConfig.from_pretrained('deepseek-ai/DeepSeek-V2.5', trust_remote_code=True)
    >>> import transformers_modules # success, initialized
    >>> klass.__class__ # transformers_modules.deepseek-ai.DeepSeek-V2.5.98b11844770b2c3ffc18b175c758a803640f4e77.configuration_deepseek.DeepseekV2Config

    In the DeepSeek example, the config class is an instance of a custom
    class that is not serializable by default. This class will not be
    importable in spawned workers, and won't exist at all on
    other nodes, which breaks serialization of the config.

    In this function we tell the cloudpickle serialization library to pass
    instances of these generated classes by value instead of by reference,
    i.e. the class definition is serialized along with its data so that the
    class module does not need to be importable on the receiving end.

    See: https://github.com/cloudpipe/cloudpickle?tab=readme-ov-file#overriding-pickles-serialization-mechanism-for-importable-constructs
    """  # noqa
    try:
        import transformers_modules  # type: ignore [import-not-found]
    except ImportError:
        # the config does not need trust_remote_code
        return

    try:
        # We don't need this.
        # cloudpickle.register_pickle_by_value(transformers_modules)

        # ray vendors its own version of cloudpickle
        import ray

        ray.cloudpickle.register_pickle_by_value(transformers_modules)
    except Exception as e:
        logging.warning(
            "Unable to register remote classes used by"
            " trust_remote_code with by-value serialization. This may"
            " lead to a later error.",
            exc_info=e,
        )


CACHE_DIR = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "furiosa" / "llm"
HOT_CACHE_DIR = os.environ.get("HOT_CACHE_DIR")


def get_path_via_hot_cache(origin_path: str) -> str:
    if not os.path.isfile(origin_path):
        return origin_path

    if not HOT_CACHE_DIR:
        return origin_path

    if not os.path.exists(HOT_CACHE_DIR):
        os.makedirs(HOT_CACHE_DIR, exist_ok=True)

    if not os.path.isdir(HOT_CACHE_DIR):
        return origin_path

    origin_path = os.path.abspath(origin_path)
    try:
        relative = Path(origin_path).relative_to(CACHE_DIR)
    except Exception:
        relative = Path(origin_path[1:])
    hot_cached_path = os.path.join(HOT_CACHE_DIR, relative)

    if not os.path.exists(hot_cached_path):
        du = shutil.disk_usage(HOT_CACHE_DIR)
        if du.free / du.total < 0.1:
            return origin_path

        with tempfile.NamedTemporaryFile(dir=HOT_CACHE_DIR, delete=False) as tmp_file:
            temp_path = tmp_file.name

        try:
            shutil.copyfile(origin_path, temp_path)
            os.makedirs(os.path.dirname(hot_cached_path), exist_ok=True)
            shutil.move(temp_path, hot_cached_path)
        except Exception as e:
            print(f"Exception in get_path_via_hot_cache: {e}", flush=True)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return hot_cached_path if os.path.exists(hot_cached_path) else origin_path
