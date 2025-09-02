from functools import reduce
import operator
from typing import Sequence

import torch
import torch.lib


@torch.library.custom_op("furiosa::sparse_select", mutates_args=())
def sparse_select(
    x: torch.Tensor, indices: Sequence[torch.Tensor], dummy_index: int, index_group_size: int
) -> torch.Tensor:
    """Custom ``aten.index.Tensor`` operator optimized for Furiosa compiler stack.

    When run on torch, this operator is equivalent to ``torch.ops.aten.index.Tensor`` except for some constraints on inputs.
    For more details, refer to https://www.notion.so/furiosa/model-rewriter-custom-op-3921611bb063482592518f419056cff8?pvs=4.
    """
    if len(indices) > 1:
        raise NotImplementedError("We don't support multi-dim indexing yet")
    assert len(indices[0].size()) == 1
    assert reduce(operator.mul, indices[0].shape) % index_group_size == 0
    return torch.ops.aten.index.Tensor(x, indices)


@torch.library.register_fake("furiosa::sparse_select")
def _sparse_select_fake(x, indices, dummy_index, index_group_size):
    assert len(indices[0].size()) == 1
    if len(indices) > 1:
        raise NotImplementedError("We don't support multi-dim indexing yet")
    return torch.ops.aten.index.Tensor(x, indices)


@torch.library.custom_op("furiosa::sparse_select_v1_5", mutates_args=())
def sparse_select_v1_5(
    x: torch.Tensor,
    indices: Sequence[torch.Tensor],
    dummy_index: int,
    index_group_size: int,
    valid_count_tile_size: int,  # beam search width
) -> torch.Tensor:
    """Custom ``aten.index.Tensor`` operator optimized for Furiosa compiler stack.

    When run on torch, this operator is equivalent to ``torch.ops.aten.index.Tensor`` except for some constraints on inputs.
    For more details, refer to https://www.notion.so/furiosa/model-rewriter-custom-op-3921611bb063482592518f419056cff8?pvs=4.
    """
    return sparse_select(x, indices, dummy_index, index_group_size)


@torch.library.register_fake("furiosa::sparse_select_v1_5")
def _sparse_select_v1_5_fake(
    x: torch.Tensor,
    indices: Sequence[torch.Tensor],
    dummy_index: int,
    index_group_size: int,
    valid_count_tile_size: int,  # beam search width
) -> torch.Tensor:
    """Custom ``aten.index.Tensor`` operator optimized for Furiosa compiler stack.

    When run on torch, this operator is equivalent to ``torch.ops.aten.index.Tensor`` except for some constraints on inputs.
    For more details, refer to https://www.notion.so/furiosa/model-rewriter-custom-op-3921611bb063482592518f419056cff8?pvs=4.
    """
    return _sparse_select_fake(x, indices, dummy_index, index_group_size)


@torch.library.custom_op("furiosa::gather_i32", mutates_args=())
def gather_i32(x: torch.Tensor, dim: int, index: torch.Tensor, sparse_grad: bool) -> torch.Tensor:
    """torch.ops.aten.gather.default that receives i32 index tensor."""
    assert index.dtype == torch.int32
    return torch.ops.aten.gather.default(x, dim, index.to(torch.int64), sparse_grad=sparse_grad)


@torch.library.register_fake("furiosa::gather_i32")
def _gather_i32_fake(
    x: torch.Tensor, dim: int, index: torch.Tensor, sparse_grad: bool
) -> torch.Tensor:
    return torch.ops.aten.gather.default(x, dim, index.to(torch.int64), sparse_grad=sparse_grad)


@torch.library.custom_op("furiosa::module_marker", mutates_args=())
def module_marker(
    x: torch.Tensor,
    kind: str,  # "input", "output"
    module_path: str,
    module_class: str,
    arg_name: str,
) -> torch.Tensor:
    return x.clone()


@torch.library.register_fake(
    "furiosa::module_marker",
)
def module_marker_fake(
    x: torch.Tensor,
    kind: str,
    module_path: str,
    module_class: str,
    arg_name: str,
) -> torch.Tensor:
    return x
