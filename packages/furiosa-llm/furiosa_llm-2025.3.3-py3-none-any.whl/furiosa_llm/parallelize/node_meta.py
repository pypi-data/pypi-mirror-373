import enum
from enum import auto
from functools import partial
import typing
from typing import Any, Dict, Optional, Sequence, Tuple, Union

from pydantic import BaseModel
import torch
from torch._subclasses import FakeTensorMode
from torch.fx import GraphModule, Node
from torch.fx.passes.shape_prop import TensorMetadata, _extract_tensor_metadata
from torch.utils._pytree import tree_map_only

from furiosa_llm.parallelize.utils import (
    _is_parent_of_lift_fresh_copy,
    get_real_tensor_from_fake_tensor,
    get_tensor_from_node,
)

if typing.TYPE_CHECKING:
    from furiosa_llm.parallelize.model_rewriter.mppp_config import DeviceId, ShardSpec

from furiosa_llm.parallelize.utils import recursive_getattr

_ORIGINAL_NAME_KEY = "original_name"
_UNSHARDED_TENSOR_META_KEY = "unsharded_shape"
_CONSTANT_EMBEDDING_POLICY_KEY = "constant_embedding_policy"
_QPARAM_KIND_KEY = "qparam_kind"
_COLOR_KEY = "color"
_GM_HASH_KEY = "gm_hash"
_CONSTANT_KIND_KEY = "constant_kind"
_DEVICE_ID_KEY = "device_id"
_SPEC_KEY = "spec"

_INPUT_KIND_KEY = "input_kind"


class ConstantEmbeddingPolicy(enum.Enum):
    SHOULD_BE_EMBEDDED = enum.auto()
    SHOULD_BE_INPUT = enum.auto()


def set_original_name(node: Node, original_name: Union[str, Tuple[str, ...]]):
    node.meta[_ORIGINAL_NAME_KEY] = original_name


def get_original_name(node: Node):
    return node.meta[_ORIGINAL_NAME_KEY]


def has_original_name(node: Node) -> bool:
    return _ORIGINAL_NAME_KEY in node.meta


def get_unsharded_tensor_meta(node: Node) -> Union[TensorMetadata, Sequence[TensorMetadata]]:
    return node.meta[_UNSHARDED_TENSOR_META_KEY]


def set_unsharded_tensor_meta(
    node: Node, tensor_meta: Union[TensorMetadata, Sequence[TensorMetadata]]
) -> None:
    node.meta[_UNSHARDED_TENSOR_META_KEY] = tensor_meta


def set_to_be_embedded(node: Node):
    if node.op != "get_attr":
        raise ValueError("Only get_attr nodes can have constant embedding metadata.")
    node.meta[_CONSTANT_EMBEDDING_POLICY_KEY] = ConstantEmbeddingPolicy.SHOULD_BE_EMBEDDED


def set_to_be_input(node: Node):
    if node.op != "get_attr":
        raise ValueError("Only get_attr nodes can have constant embedding metadata.")
    node.meta[_CONSTANT_EMBEDDING_POLICY_KEY] = ConstantEmbeddingPolicy.SHOULD_BE_INPUT


def should_be_embedded(node: Node) -> bool:
    if node.op != "get_attr":
        raise ValueError("Only get_attr nodes can have constant embedding metadata.")
    return (
        node.meta.get(_CONSTANT_EMBEDDING_POLICY_KEY, None)
        == ConstantEmbeddingPolicy.SHOULD_BE_EMBEDDED
    )


def should_be_input(node: Node) -> bool:
    if node.op != "get_attr":
        raise ValueError("Only get_attr nodes can have constant embedding metadata.")
    return (
        node.meta.get(_CONSTANT_EMBEDDING_POLICY_KEY, None)
        == ConstantEmbeddingPolicy.SHOULD_BE_INPUT
    )


def get_color(node: Node) -> Optional[Tuple[int, ...]]:
    return node.meta.get(_COLOR_KEY, None)


def set_color(node: Node, color: Sequence[int]) -> None:
    node.meta[_COLOR_KEY] = tuple(color)


class QParamKind(str, enum.Enum):
    SCALE = enum.auto()
    ZERO_POINT = enum.auto()
    # zero-points for operations running on DPE. These qparams must go through emulation_in operator before being used for any other operations.
    ZERO_POINT_FOR_DPE = enum.auto()


def set_qparam_kind(node, qparam_kind: QParamKind):
    node.meta[_QPARAM_KIND_KEY] = qparam_kind


def get_qparam_kind(node) -> Optional[QParamKind]:
    return node.meta.get(_QPARAM_KIND_KEY, None)


def is_qparam(node: Node) -> bool:
    return _QPARAM_KIND_KEY in node.meta


def set_gm_hash(node: Node, hash: str) -> None:
    node.meta[_GM_HASH_KEY] = hash


def get_gm_hash(node: Node) -> Optional[str]:
    return node.meta.get(_GM_HASH_KEY)


class ConstantKind(str, enum.Enum):
    WEIGHT = enum.auto()
    BUFFER = enum.auto()
    OTHERS = enum.auto()


def set_constant_kind(node: Node, kind: ConstantKind) -> None:
    if node.op != "get_attr":
        raise ValueError("Node with constant kind should be get_attr node.")
    node.meta[_CONSTANT_KIND_KEY] = kind


def get_constant_kind(node: Node) -> Optional[ConstantKind]:
    return node.meta.get(_CONSTANT_KIND_KEY, None)


def is_weight_or_buffer(node: Node) -> bool:
    return node.meta.get(_CONSTANT_KIND_KEY, False) in (
        ConstantKind.WEIGHT,
        ConstantKind.BUFFER,
    )


class SerializableMetadata(BaseModel):
    original_name: Optional[Union[str, Tuple[str, ...]]] = None
    qparam_kind: Optional[QParamKind] = None
    constant_kind: Optional[ConstantKind] = None
    stack_trace: Optional[str] = None

    @classmethod
    def from_node(cls, node: Node):
        return cls(
            original_name=get_original_name(node) if has_original_name(node) else None,
            qparam_kind=get_qparam_kind(node),
            constant_kind=get_constant_kind(node),
            stack_trace=node.meta.get("stack_trace"),
        )


def serialize_metadata(node: Node) -> str:
    metadata = SerializableMetadata.from_node(node)
    return metadata.model_dump_json(exclude_none=True)


def deserialize_metadata(value: str) -> Dict[str, Any]:
    metadata = SerializableMetadata.model_validate_json(value)
    return metadata.model_dump(exclude_none=True)


def fill_tensor_meta_from_val_meta(gm: GraphModule) -> None:
    # Generate "tensor_meta" metadata from "val" metadata which contains example value for corresponding node.
    # The result is same as calling ShapeProp, but more efficient.
    for node in gm.graph.nodes:
        if node.op == "get_attr":
            node.meta["tensor_meta"] = _extract_tensor_metadata(recursive_getattr(gm, node.target))
        elif node.op == "output":
            continue
        else:
            example_val = node.meta.get("val")
            if example_val is None and node.users:
                raise ValueError("Missing \"val\" metadata for node with child.")

            # Make data type tuple for consistency.
            if isinstance(example_val, list):
                example_val = tuple(example_val)
            node.meta["tensor_meta"] = tree_map_only(
                torch.Tensor, _extract_tensor_metadata, example_val
            )


def get_device_id(
    node: Node,
) -> Union["DeviceId", Tuple["DeviceId", ...]]:
    return node.meta[_DEVICE_ID_KEY]


def set_device_id(
    node: Node,
    device_id: Union["DeviceId", Tuple["DeviceId", ...]],
):
    node.meta[_DEVICE_ID_KEY] = device_id


def has_device_id(node) -> bool:
    return _DEVICE_ID_KEY in node.meta


def get_spec(node: Node) -> Union["ShardSpec", Tuple["ShardSpec", ...]]:
    return node.meta[_SPEC_KEY]


def set_spec(node: Node, spec: Union["ShardSpec", Tuple["ShardSpec", ...]]):
    node.meta[_SPEC_KEY] = spec


def has_spec(node: Node) -> bool:
    return _SPEC_KEY in node.meta


class InputKind(enum.Enum):
    CONSTANT_TENSOR = auto()
    USER_INPUT = auto()
    INTERMEDIATE_TENSOR = auto()


def set_input_kind(node: Node, kind: InputKind) -> None:
    node.meta[_INPUT_KIND_KEY] = kind


def get_input_kind(node: Node) -> Optional[InputKind]:
    return node.meta.get(_INPUT_KIND_KEY)


def add_tensor_meta(node: Node, gm: Optional[GraphModule] = None) -> None:
    assert node.op in ("call_function", "call_module")

    fake_mode = FakeTensorMode(allow_non_fake_inputs=True)
    fake_args = tree_map_only(Node, partial(get_tensor_from_node, fake_mode=fake_mode), node.args)
    fake_kwargs = tree_map_only(
        Node, partial(get_tensor_from_node, fake_mode=fake_mode), node.kwargs
    )

    if node.op == "call_function":
        target = node.target
        assert callable(target)
    elif node.op == "call_module":
        if gm is None:
            raise ValueError("GraphModule must be provided for call_module node.")
        assert isinstance(node.target, str)
        # Get actual module that is callable.
        target = getattr(gm, node.target)

        if isinstance(target, GraphModule):
            # If module is GraphModule, there might be placeholder nodes that is given as the input to `torch.ops.aten.lift_fresh_copy.default` op node,
            # which doesn't allow fake tensor to be an its input. So we need to convert corresponding input tensors that will used as an
            # `torch.ops.aten.lift_fresh_copy.default` op's input back to real tensors.
            placeholder_nodes = tuple(
                node for node in target.graph.nodes if node.op == "placeholder"
            )

            assert len(placeholder_nodes) == len(fake_args)
            fake_args = tuple(
                (
                    get_real_tensor_from_fake_tensor(arg)
                    if _is_parent_of_lift_fresh_copy(placeholder_nodes[i])
                    else arg
                )
                for i, arg in enumerate(fake_args)
            )

            assert len(fake_kwargs) == 0
    else:
        raise ValueError(f"{node.op} node's tensor metadata cannot be derived from other nodes.")

    # Get fake tensor result
    assert callable(target)
    res = target(*fake_args, **fake_kwargs)

    del fake_args, fake_kwargs
    tensor_meta = tree_map_only(torch.Tensor, _extract_tensor_metadata, res)
    node.meta["tensor_meta"] = tensor_meta
    node.meta["val"] = res
