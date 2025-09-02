from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple, Union

from furiosa_llm.parallelize.compiler_config import CompilerConfigContext
from furiosa_llm.parallelize.pipeline.types import TensorGenInfo


@dataclass
class LogitsSliceConfig:
    slice_direction: Optional[str]  # "left" or "right"
    slice_size: int

    def __init__(self, slice_direction: Optional[str], slice_size: int):
        if slice_direction not in [None, "left", "right"]:
            raise ValueError(
                f"`slice_direction` must be either 'left' or 'right'. Got: {slice_direction}"
            )
        if slice_size < 0:
            raise ValueError(f"`slice_size` must be greater than or equal to 0. Got: {slice_size}")
        if slice_size > 0 and slice_direction is None:
            raise ValueError(
                "`slice_direction` must be given explicitly when `slice_size` is positive number."
            )
        self.slice_direction = slice_direction
        self.slice_size = slice_size


# TODO: better name?
@dataclass
class NonSharedPipelineBuildConfig:
    args_data: Tuple
    kwargs_data: Dict[str, Union[TensorGenInfo, Any]]
    pipeline_name: str
    compile_config: "CompilerConfigContext"
    logits_slice_config: Optional[LogitsSliceConfig]
    num_blocks_per_supertask: Union[int, Sequence[int]]
