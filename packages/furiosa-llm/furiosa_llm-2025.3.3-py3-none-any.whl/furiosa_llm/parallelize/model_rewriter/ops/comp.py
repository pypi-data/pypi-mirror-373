# Split local tensor into `world_size` chunks in `dim` and only return `rank`th piece.
from typing import Optional, Tuple, Union

import torch

from furiosa_llm.parallelize.model_rewriter.ops.types import Op


class Split(Op):
    world_size: int
    dim: int
    rank: int

    def __init__(self, dim: int, num_chunks: int, idx: Optional[int] = None) -> None:
        super().__init__()
        self.dim = dim
        self.num_chunks = num_chunks
        self.idx = idx

    def __call__(self, tensor: torch.Tensor) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        if tensor.size(self.dim) % self.num_chunks != 0:
            raise NotImplementedError("Uneven sharding is not supported now")

        chunks = torch.chunk(tensor, self.num_chunks, self.dim)
        if self.idx is not None:
            return chunks[self.idx]
        else:
            return tuple(chunks)
