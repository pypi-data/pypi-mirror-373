from dataclasses import dataclass
import os
from typing import Optional, Tuple

from transformers import PreTrainedModel

from furiosa_llm.models import ModelMetadata


@dataclass(frozen=True)
class ModelCreationInfo:
    metadata: ModelMetadata
    random_weight_model: bool
    seed: Optional[int] = None
    qformat_path: Optional[os.PathLike] = None
    qparam_path: Optional[os.PathLike] = None
    quant_ckpt_file_path: Optional[os.PathLike] = None

    def __post_init__(self):
        if self.metadata.need_quant_artifacts and not (self.qformat_path and self.qparam_path):
            raise ValueError("Qformat and qparam path should be given.")

    def instantiate_model(self) -> PreTrainedModel:
        if self.random_weight_model:
            return self.metadata.random_weight_model(
                qformat_path=self.qformat_path, qparam_path=self.qparam_path
            )
        else:
            return self.metadata.pretrained_model(
                qformat_path=self.qformat_path,
                qparam_path=self.qparam_path,
                quant_ckpt_file_path=self.quant_ckpt_file_path,
            )

    def get_qparam_qformat_path(self) -> Optional[Tuple[os.PathLike, os.PathLike]]:
        if not self.metadata.need_quant_artifacts:
            return None
        if self.qformat_path:
            # This was already checked in __post_init__.
            assert self.qformat_path and self.qparam_path
            return (self.qformat_path, self.qparam_path)
        else:
            return None

    def is_hashable(self) -> bool:
        return not self.random_weight_model or self.seed is not None
