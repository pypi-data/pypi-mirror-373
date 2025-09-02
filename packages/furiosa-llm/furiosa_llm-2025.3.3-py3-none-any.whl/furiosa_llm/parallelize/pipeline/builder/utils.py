import functools
from itertools import chain
import operator
from typing import Any, Dict, List, Optional, Sequence, Tuple

import torch
from torch.distributed import get_rank
from torch.fx import GraphModule, Node

from furiosa_llm.parallelize.node_meta import get_original_name, has_original_name
from furiosa_llm.parallelize.pipeline.types import DeviceId


def get_indexes_in_nested_tuple(haystack: Sequence[Any], needle: Any) -> Optional[Tuple[int, ...]]:
    if not isinstance(haystack, (tuple, list)):
        return None
    try:
        return (haystack.index(needle),)
    except ValueError:
        for i, item in enumerate(haystack):
            indexes = get_indexes_in_nested_tuple(item, needle)
            if indexes:
                return (i,) + indexes
        return None


def new_name_with_device_id(original_name: str, device_id: DeviceId) -> str:
    return f"d{device_id}-{original_name}"


def nested_equal(a, b) -> bool:
    if isinstance(a, (list, tuple)):
        if not isinstance(b, (list, tuple)):
            return False
        return all(map(lambda e1, e2: nested_equal(e1, e2), a, b))
    elif a is None:
        return b is None
    else:
        return a.equal(b)


def log(msg: str):
    if get_rank() == 0:
        print(msg)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


def get_params_and_buffers_from_call_module_node(
    gm: GraphModule, node: Node
) -> List[Tuple[str, torch.Tensor]]:
    """Get parameter and buffer tensors inside call_module node.

    Args:
        gm (GraphModule): GraphModule containing `node`.
        node (Node): Target call_module node.

    Returns:
        List[Tuple[str, torch.Tensor]]: Each element is a pair of {node_name}_{parameter or buffer name} and actual tensor.
    """

    if node.op != "call_module":
        return []
    assert isinstance(node.target, str)
    module = getattr(gm, node.target)
    return list(
        map(
            lambda kv: (f"{node.target}_{kv[0]}", kv[1]),
            chain(module.named_parameters(), module.named_buffers()),
        )
    )


def is_getitem(node: Node) -> bool:
    return node.op == "call_function" and node.target == operator.getitem


def get_tensor_name_with_idx(parent_name: str, idx: int) -> str:
    return f"{parent_name}:{idx}"


def get_tensor_name(node: Node, idx: Optional[int] = None) -> str:
    if node.op == "placeholder":
        node_name = node.name
    elif node.op == "call_module":
        node_name = node.name
    elif node.op == "get_attr":
        node_name = node.name
    elif is_getitem(node):
        # getitem node does not exist in Pipeline format.
        assert len(node.args) == 2
        parent, output_idx = node.args
        assert isinstance(parent, Node) and isinstance(output_idx, int)
        assert not is_getitem(parent)
        return get_tensor_name_with_idx(get_tensor_name(parent), output_idx)
    elif node.op == "call_function":
        return node.name
    else:
        raise NotImplementedError(f"node {node.name} cannot be converted to tensor name")

    if idx is not None:
        node_name = get_tensor_name_with_idx(node_name, idx)
    return node_name


# Get names of parameters saved in the param file
def get_constant_tensors_with_original_name(
    model: GraphModule,
) -> Dict[str, torch.Tensor]:
    """Get tensor constants in ``model`` that has original name and its original name is not in ``excludes``."""

    # Get param tensors that has original name but not in ``excludes``.
    return {
        get_original_name(node): getattr(model, node.target)
        for node in model.graph.nodes
        if node.op == "get_attr" and has_original_name(node)
    }
