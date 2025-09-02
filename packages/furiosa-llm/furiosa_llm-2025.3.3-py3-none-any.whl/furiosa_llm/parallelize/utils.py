import contextlib
from functools import partial
import os
from pathlib import Path
import re
import sys
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import furiosa_llm_models as flm
from furiosa_models.architecture.models.serve import (
    CausalModelServer,
)
import torch
from torch._dynamo.source import AttrSource, GetItemSource, LocalSource
from torch._guards import Source, detect_fake_mode
from torch._ops import OpOverload
from torch._subclasses.fake_tensor import FakeTensor, FakeTensorMode
from torch.distributed._tensor import DTensor
from torch.fx import GraphModule, Node
from torch.fx.passes.shape_prop import ShapeProp, TensorMetadata, _extract_tensor_metadata
from torch.utils._pytree import tree_flatten, tree_map_only
import transformers
from transformers import MODEL_FOR_CAUSAL_LM_MAPPING

from furiosa_llm.models import ModelMetadata
from furiosa_llm.models.quant import QuantCausalLM
from furiosa_llm.parallelize.mppp.config import (
    Device,
    DeviceId,
    DeviceMesh,
    MpppConfig,
    Replicate,
    ShardSpec,
)

KWARGS_NAME = "kwargs"
ARGS_NAME = "args"
aten = torch.ops.aten


def nested_to_dtensor(
    device_mesh,
    placement,
    target,
):
    if isinstance(target, DTensor):
        return target
    elif isinstance(target, torch.Tensor):
        return DTensor.from_local(target, device_mesh, placement)
    elif isinstance(target, List):
        return list(map(partial(nested_to_dtensor, device_mesh, placement), target))
    elif isinstance(target, Tuple):
        return tuple(map(partial(nested_to_dtensor, device_mesh, placement), target))
    else:
        return target


def nested_to_local(target):
    if isinstance(target, DTensor):
        return target.to_local()
    elif isinstance(target, torch.Tensor):
        return target
    elif isinstance(target, List):
        return list(map(nested_to_local, target))
    elif isinstance(target, Tuple):
        return tuple(map(nested_to_local, target))
    else:
        return target


# follow given node's child and return the first DTensor node found.
def get_first_dtensor_descendant(node: Node, allow_multiple_children=False) -> Node:
    while not isinstance(node.meta["example_value"], DTensor):
        assert allow_multiple_children or len(node.users) == 1
        child = tuple(node.users.keys())[0]
        node = child
    return node


# follow given node's child and return the first DTensor node found.
def get_first_dtensor_ancestor(node: Node) -> Node:
    while not isinstance(node.meta["example_value"], DTensor):
        assert len(node.all_input_nodes) == 1 and node.target == "to_local"
        node = node.all_input_nodes[0]
    return node


def _get_original_name(source: Source) -> str:
    if isinstance(source, GetItemSource):
        return _get_original_name(source.base)
    elif isinstance(source, LocalSource):
        return source.local_name
    elif isinstance(source, AttrSource):
        return f"{_get_original_name(source.base)}.{source.member}"
    else:
        raise ValueError(f"Unknown source type: {source}")


def _get_tensor(source: Source, local_variables: Mapping[str, Any]):
    if isinstance(source, GetItemSource):
        return _get_tensor(source.base, local_variables)[source.index]
    elif isinstance(source, LocalSource):
        return local_variables[source.local_name]
    elif isinstance(source, AttrSource):
        return getattr(_get_tensor(source.base, local_variables), source.member)
    else:
        raise NotImplementedError(f"Unsupported source: {source}")


def flatten_input_tensors(
    torch_ir_gm: GraphModule,
    original_args: Sequence,
    original_kwargs: Mapping,
) -> Tuple:
    placeholder_nodes = torch_ir_gm.graph.find_nodes(op="placeholder")

    local_vars = {KWARGS_NAME: original_kwargs, ARGS_NAME: original_args}
    for k, v in original_kwargs.items():
        assert k not in local_vars
        local_vars[k] = v

    args_in_order = tuple(
        _get_tensor(node._dynamo_source, local_vars) for node in placeholder_nodes
    )
    return args_in_order


def get_torch_major_version() -> str:
    # e.g., "2.1"
    return ".".join(torch.__version__.split(".", 2)[0:2])


def is_aten_op(func: Callable) -> bool:
    return isinstance(func, OpOverload) and func._schema.name.startswith("aten")


def is_custom_op(func: Callable) -> bool:
    return isinstance(func, OpOverload) and func._schema.name.startswith("furiosa::")


def gen_mppp_config_with_no_parallelism(
    name: str, model: GraphModule, device: Device
) -> MpppConfig:
    device_id = DeviceId("0")
    static_tensors = {
        node.name: ShardSpec([Replicate()], DeviceMesh([device_id]))
        for node in model.graph.nodes
        if not node.all_input_nodes
    }

    return MpppConfig(
        name=name,
        devices={device_id: device},
        static_tensors=static_tensors,
        dynamic_tensors=[],
    )


def get_output_names(model: Union[ModelMetadata, torch.nn.Module]) -> List[str]:
    if isinstance(model, ModelMetadata):
        model_class = model.get_optimized_cls()
    else:
        assert isinstance(model, torch.nn.Module)
        model_class = get_original_model_type(model)

    if model_class == MODEL_FOR_CAUSAL_LM_MAPPING[model.config.__class__] or model_class in (
        flm.gptj.symbolic.huggingface.GPTJForCausalLM,
        flm.gptj.symbolic.huggingface_rope.GPTJForCausalLM,
        flm.gptj.symbolic.huggingface_rope_rngd_gelu.GPTJForCausalLM,
    ):
        # original huggingface PretrainedModel.
        output_names = ["logits"]
        for layer_idx in range(model.config.num_hidden_layers):
            for kv_idx in range(2):
                output_names.append(f"past_key_values_{layer_idx}_{kv_idx}")
        return output_names
    elif model_class in (
        transformers.BertForQuestionAnswering,
        transformers.RobertaForQuestionAnswering,
    ):
        return ["start_logits", "end_logits"]
    elif model_class in (
        flm.gptj.symbolic.preallocated_concat.GPTJForCausalLM,
        flm.gptj.symbolic.preallocated_concat_rope.GPTJForCausalLM,
    ):
        output_names = ["logits"]
        for kv_idx in range(2):
            for layer_idx in range(model.config.num_hidden_layers):
                output_names.append(f"past_key_values_{layer_idx}_{kv_idx}")
        return output_names
    elif model_class in (
        flm.gptj.symbolic.paged_attention_optimized_packed_rope.GPTJForCausalLM,
        flm.gptj.symbolic.mlperf_submission_slice.GPTJForCausalLM,
        flm.gptj.symbolic.mlperf_submission.GPTJForCausalLM,
        flm.gptj.symbolic.paged_attention_rope.GPTJForCausalLM,
        flm.bert.symbolic.mlperf_submission.BertForQuestionAnswering,
        flm.bert.symbolic.experimental.huggingface_unsplit_packed.BertForQuestionAnswering,
        flm.llama.symbolic.mlperf_submission.LlamaForCausalLM,
        flm.llama.symbolic.mlperf_submission_slice.LlamaForCausalLM,
        flm.llama3.symbolic.mlperf_submission.LlamaForCausalLM,
        flm.llama3.symbolic.mlperf_submission_slice.LlamaForCausalLM,
        flm.llama3.symbolic.aramco_specdec.LlamaForCausalLM,
        flm.llama3.symbolic.aramco_specdec_slice_integrated.LlamaForCausalLM,
    ) or issubclass(model_class, CausalModelServer):
        return ["logits"]
    else:
        raise NotImplementedError(f"Cannot get output names for model {model_class}")


def get_normalized_torch_op_node_args(node) -> Tuple[Tuple, Dict]:
    if node.op != "call_function" or not isinstance(node.target, OpOverload):
        raise ValueError("torch op call function node can only be normalized.")
    node_args = list(node.args)
    node_kwargs = dict(node.kwargs)
    for idx, arg in enumerate(node.target._schema.arguments):
        if arg.name not in node_kwargs:
            continue
        if arg.kwarg_only:
            # Remove kwarg whose value is its default value.
            if arg.has_default_value() and arg.default_value == node_kwargs[arg.name]:
                del node_kwargs[arg.name]
                continue
        else:
            # Convert non-kwarg-only kwarg into positional arguments.
            assert idx == len(node_args)
            node_args.append(node_kwargs.pop(arg.name))

    # Remove positional arguments whose value is its default value.
    for i in range(len(node_args) - 1, -1, -1):
        arg_info = node.target._schema.arguments[i]
        if arg_info.has_default_value() and arg_info.default_value == node_args[i]:
            node_args.pop()
        else:
            break

    return tuple(node_args), node_kwargs


def get_original_model_type(model: torch.nn.Module) -> Type:
    if isinstance(model, QuantCausalLM):
        return model.original_type
    else:
        return model.__class__


# Pattern for models in transformers and furiosa-llm-models.
_KV_CACHE_PATTERN = r"past_key_values_[0-9]+_[0-9]+"
# Pattern for model in furiosa-models-lang.
_MODELS_LANG_KV_CACHE_PATTERN = r"kv_caches_[0-9]+_[0-9]+"


def is_kvcache(name: str) -> bool:
    return bool(
        re.compile(_KV_CACHE_PATTERN).match(name)
        or re.compile(_MODELS_LANG_KV_CACHE_PATTERN).match(name)
    )


def check_gms_strict_equal(gm1: GraphModule, gm2: GraphModule) -> bool:
    """Check two gms are strictly equal, including node order, names, and actual tensor constant values."""
    if len(gm1.graph.nodes) != len(gm2.graph.nodes):
        return False

    node1_node_to_idx = {node.name: i for i, node in enumerate(gm1.graph.nodes)}
    node2_node_to_idx = {node.name: i for i, node in enumerate(gm2.graph.nodes)}

    for node1, node2 in zip(gm1.graph.nodes, gm2.graph.nodes):
        if node1.op != node2.op or node1.target != node2.target:
            return False
        if node1.op == "get_attr":
            if not getattr(gm1, node1.target).equal(getattr(gm2, node2.target)):
                return False
        for attr_name in ("args", "kwargs"):
            node1_list, node1_spec = tree_flatten(getattr(node1, attr_name))
            node2_list, node2_spec = tree_flatten(getattr(node2, attr_name))
            if len(node1_list) != len(node2_list):
                return False
            if node1_spec != node2_spec:
                return False
            for arg1, arg2 in zip(node1_list, node2_list):
                if isinstance(arg1, Node):
                    if not isinstance(arg2, Node):
                        return False
                    if node1_node_to_idx[arg1.name] != node2_node_to_idx[arg2.name]:
                        return False
                if isinstance(arg1, torch.Tensor):
                    if not isinstance(arg2, torch.Tensor):
                        return False
                    if not arg1.equal(arg2):
                        return False
                else:
                    if arg1 != arg2:
                        return False
    return True


def is_typecast_node(node: Node) -> bool:
    # TODO: add more ops
    if node.op == "call_function":
        if node.target == aten.to.dtype:
            return True
        elif node.target == aten._to_copy.default:
            assert isinstance(node.target, OpOverload)
            mutable_kwargs_copy = dict(node.kwargs)
            for arg in node.target._schema.arguments:
                if not arg.has_default_value():
                    continue
                # Delete default kwargs.
                # Default value can be None or False.
                if arg.name in node.kwargs and arg.default_value == node.kwargs[arg.name]:
                    del mutable_kwargs_copy[arg.name]
            return tuple(mutable_kwargs_copy) == ("dtype",)
        else:
            return False
    return False


def _recursive_getattr(obj, attr_path):
    for attr in attr_path:
        if not hasattr(obj, attr):
            return None
        obj = getattr(obj, attr)

    return obj


def recursive_getattr(obj, target: str):
    attr_path = target.split(".")
    return _recursive_getattr(obj, attr_path)


def get_cache_path_if_exists(
    hash_val: str,
    file_extension: str,
    cache_dir: Union[str, os.PathLike],
    *,
    allow_dir: bool = False,
) -> Optional[Path]:

    def fname_matches(fname: str) -> bool:
        return fname.rsplit("-", 1)[-1].split(".", 1) == [
            hash_val,
            file_extension,
        ]

    try:
        cached = next(
            f
            for f in os.listdir(cache_dir)
            if fname_matches(f)
            and (
                os.path.isfile(os.path.join(cache_dir, f))
                or (allow_dir and os.path.isdir(os.path.join(cache_dir, f)))
            )
        )
    except StopIteration:
        # No cache found
        return None
    else:
        return Path(cache_dir) / cached


if sys.version_info >= (3, 10):
    def zip_equal(*iterables):  # fmt: skip
        return zip(*iterables, strict=True)
else:
    from more_itertools import zip_equal  # noqa


def _is_parent_of_lift_fresh_copy(node: Node) -> bool:
    if any(child.target == torch.ops.aten.lift_fresh_copy.default for child in node.users):
        assert len(node.users) == 1
        return True
    return False


def get_real_tensor_from_fake_tensor(fake_tensor: FakeTensor) -> torch.Tensor:
    return torch.zeros(
        fake_tensor.shape,
        dtype=fake_tensor.dtype,
        layout=fake_tensor.layout,
        device=fake_tensor.device,
        requires_grad=fake_tensor.requires_grad,
    )


def get_fake_mode(tensors: Iterable[torch.Tensor]) -> FakeTensorMode:
    # Get fake mode from ``tensors`` if exist.
    # Otherwise, get currently active one or create new one if there's no currently active one.
    fake_mode_set = set(tensor.fake_mode for tensor in tensors if isinstance(tensor, FakeTensor))
    if len(fake_mode_set) > 1:
        raise ValueError(
            "There must be at most one FakeTensorMode for all parameters, buffers and inputs"
        )
    return (
        fake_mode_set.pop()
        if len(fake_mode_set) == 1
        else detect_fake_mode() or FakeTensorMode(allow_non_fake_inputs=True)
    )


def propagate_shape_info_without_real_computation(
    gm: GraphModule, example_args: Sequence[torch.Tensor]
) -> None:
    assert all(isinstance(arg, FakeTensor) for arg in example_args)

    fake_mode = get_fake_mode(example_args)
    fake_example_args = tuple(fake_mode.from_tensor(arg) for arg in example_args)

    original_tensor_constants = {}

    # Replace all tensor constants with fake ones to avoid real computation.
    for node in gm.graph.nodes:
        if (
            node.op != "get_attr"
            or _is_parent_of_lift_fresh_copy(node)
            or node.target in original_tensor_constants
        ):
            continue
        original_tensor_constants[node.target] = getattr(gm, node.target)
        setattr(
            gm,
            node.target,
            fake_mode.from_tensor(original_tensor_constants[node.target], static_shapes=True),
        )

    ShapeProp(gm).propagate(*fake_example_args)

    # Restore original tensor constants.
    for attr_name, tensor in original_tensor_constants.items():
        setattr(gm, attr_name, tensor)
    del original_tensor_constants


def get_tensor_from_node(
    node: Node, fake_mode: Optional[FakeTensorMode] = None, gm: Optional[GraphModule] = None
) -> torch.Tensor:
    example_val = node.meta.get("val", None)
    if example_val is not None:
        if fake_mode is not None:
            example_val = tree_map_only(torch.Tensor, fake_mode.from_tensor, example_val)
        return example_val

    tensor_meta = node.meta.get("tensor_meta", None)
    if tensor_meta is None:
        if node.op == "get_attr":
            if gm is None:
                raise ValueError(
                    "GraphModule must be provided for get_attr_node with no tensor_meta."
                )
            assert isinstance(node.target, str)
            tensor_meta = _extract_tensor_metadata(getattr(gm, node.target))
        else:
            raise ValueError("`tensor_meta` must be set for the node to get tensor.")
    elif not isinstance(tensor_meta, TensorMetadata):
        raise NotImplementedError("We don't support nested form of tensor_meta now.")
    else:
        pass

    context = fake_mode or contextlib.nullcontext()

    with context:
        # TODO: Is this okay?
        ret = torch.empty(
            tensor_meta.shape,
            dtype=tensor_meta.dtype,
            requires_grad=tensor_meta.requires_grad,
            memory_format=tensor_meta.memory_format,
        ).as_strided(tensor_meta.shape, tensor_meta.stride)
    return ret


T = TypeVar("T")


def get_list_with_no_dup_with_order_preserved(obj: Iterable[T]) -> List[T]:
    return list(dict.fromkeys(obj).keys())
