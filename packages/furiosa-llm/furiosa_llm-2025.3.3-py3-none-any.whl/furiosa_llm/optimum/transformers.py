import os
from pathlib import Path
from typing import Any, Dict, Union
import warnings

from transformers import PretrainedConfig
from transformers.dynamic_module_utils import (
    get_class_from_dynamic_module,
    resolve_trust_remote_code,
)

HUB_KWARGS_NAMES = [
    "cache_dir",
    "code_revision",
    "force_download",
    "local_files_only",
    "proxies",
    "resume_download",
    "revision",
    "subfolder",
    "use_auth_token",
    "token",
]


# Borrowed from https://github.com/huggingface/transformers/blob/c41291965f078070c5c832412f5d4a5f633fcdc4/src/transformers/models/auto/auto_factory.py#L443
def extract_hub_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    hub_kwargs = {name: kwargs.pop(name) for name in HUB_KWARGS_NAMES if name in kwargs}

    token = hub_kwargs.pop("token", None)
    use_auth_token = hub_kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn(
            "The `use_auth_token` argument is deprecated and will be removed in v5 of Transformers.",
            FutureWarning,
        )
        if token is not None:
            raise ValueError(
                "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
            )
        token = use_auth_token

    if token is not None:
        hub_kwargs["token"] = token

    return hub_kwargs


# Borrowed from auto_factory.py
# https://github.com/huggingface/transformers/blob/9613933b022ddbf085e2c593ed4ceea4c734179a/src/transformers/models/auto/auto_factory.py#L387
def _get_model_class(config, model_mapping):
    supported_models = model_mapping[type(config)]
    if not isinstance(supported_models, (list, tuple)):
        return supported_models

    name_to_model = {model.__name__: model for model in supported_models}
    architectures = getattr(config, "architectures", [])
    for arch in architectures:
        if arch in name_to_model:
            return name_to_model[arch]
        elif f"TF{arch}" in name_to_model:
            return name_to_model[f"TF{arch}"]
        elif f"Flax{arch}" in name_to_model:
            return name_to_model[f"Flax{arch}"]

    # If not architecture is set in the config or match the supported models, the first element of the tuple is the
    # defaults.
    return supported_models[0]


# Borrowed from _BaseAutoModelClass
# https://github.com/huggingface/transformers/blob/9613933b022ddbf085e2c593ed4ceea4c734179a/src/transformers/models/auto/auto_factory.py#L407
class _AutoModelFinder:
    # Base class for auto models.
    _model_mapping = None
    _auto_model_cls = None

    @classmethod
    def find_model_class(
        cls, model_id_or_path: Union[str, Path], config: PretrainedConfig, **kwargs
    ):
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        kwargs["_from_auto"] = True
        hub_kwargs = extract_hub_kwargs(kwargs)

        assert cls._auto_model_cls
        auto_model_cls_name = cls._auto_model_cls.__name__
        has_remote_code = hasattr(config, "auto_map") and auto_model_cls_name in config.auto_map
        has_local_code = type(config) in cls._model_mapping.keys()  # type: ignore
        trust_remote_code = resolve_trust_remote_code(
            trust_remote_code, model_id_or_path, has_local_code, has_remote_code
        )
        if has_remote_code and trust_remote_code:
            class_ref = config.auto_map[auto_model_cls_name]
            model_class = get_class_from_dynamic_module(
                class_ref, model_id_or_path, **hub_kwargs, **kwargs
            )
            _ = hub_kwargs.pop("code_revision", None)
            if os.path.isdir(model_id_or_path):
                model_class.register_for_auto_class(auto_model_cls_name)
            else:
                cls.register(config.__class__, model_class, exist_ok=True)
            return model_class

        elif type(config) in cls._model_mapping.keys():  # type: ignore
            return _get_model_class(config, cls._model_mapping)

        raise ValueError(
            f"Unrecognized configuration class {config.__class__} for this kind of AutoModel: {cls.__name__}.\n"
            f"Model type should be one of {', '.join(c.__name__ for c in cls._model_mapping.keys())}."  # type: ignore
        )

    @classmethod
    def register(cls, config_class, model_class, exist_ok=False):
        """
        Register a new model for this class.

        Args:
            config_class ([`PretrainedConfig`]):
                The configuration corresponding to the model to register.
            model_class ([`PreTrainedModel`]):
                The model to register.
        """
        if hasattr(model_class, "config_class") and model_class.config_class != config_class:
            raise ValueError(
                "The model class you are passing has a `config_class` attribute that is not consistent with the "
                f"config class you passed (model has {model_class.config_class} and you passed {config_class}. Fix "
                "one of those so they match!"
            )
        cls._model_mapping.register(config_class, model_class, exist_ok=exist_ok)
