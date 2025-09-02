import dataclasses
import hashlib
import json
import logging
import os
import subprocess as sp
from time import time
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
)

import furiosa_llm_models  # type: ignore
import model_compressor_impl  # type: ignore
import torch
from torch._ops import OpOverload
from torch.fx import GraphModule, Node
from torch.fx.passes.shape_prop import TensorMetadata, _extract_tensor_metadata
from torch.utils._pytree import tree_flatten, tree_map_only
import transformers
from transformers import PretrainedConfig

from furiosa_llm.models.metadata import QuantizationConfig
from furiosa_llm.parallelize.utils import get_normalized_torch_op_node_args

logger = logging.getLogger(__file__)

MODEL_HASHER_VERSION: Final[str] = "0.3.4"


def get_env_independent_hash(val: Any) -> str:
    hasher = hashlib.sha256()
    if isinstance(val, (list, tuple)):
        for elem in val:
            hasher.update(get_env_independent_hash(elem).encode())
    else:
        if dataclasses.is_dataclass(val):
            assert not isinstance(
                val, type
            )  # is_dataclass narrows down to "DataclassInstance | type[DataclassInstance]"; we expect "DataclassInstance" only
            val = json.dumps(dataclasses.asdict(val), sort_keys=True, indent=2)
        hasher.update(str(val).encode())
    return hasher.hexdigest()


def hash_model(
    original_model_type: Type,
    model_config: PretrainedConfig,
    quantization_config: Optional[QuantizationConfig],
    qformat_qparam_path: Optional[Tuple[os.PathLike, os.PathLike]],
    weight_hash: str,
    seed: Optional[int],
    is_random_weight_model: bool,
    allow_bfloat16_cast_with_mcp: bool,
    extra_args: Mapping[str, str] = {},
) -> str:
    if is_random_weight_model and seed is None:
        raise ValueError(
            "When `is_random_weight_model` is True, `seed` should not be None to determine weight value is same."
        )

    weight_hash = str(seed) if is_random_weight_model else weight_hash

    to_be_hashed = [
        MODEL_HASHER_VERSION,
        str(original_model_type),
        model_config.to_json_string(),
        weight_hash,
    ]

    # Add version info of the model
    if original_model_type.__module__.startswith("furiosa_llm_models"):
        to_be_hashed.append(furiosa_llm_models.__version__)
    elif original_model_type.__module__.startswith("transformers"):
        to_be_hashed.append(transformers.__version__)
    elif original_model_type.__module__.startswith("furiosa_models.architecture.models"):
        import furiosa_models

        to_be_hashed.append(furiosa_models.__version__)
    else:
        raise NotImplementedError(f"unhashable model class module: {original_model_type}")

    # Add quantization info if quantized
    if qformat_qparam_path is not None:
        mcp_version = model_compressor_impl.__version__  # e.g., '0.3.1 (rev: eb19f39d)'

        # Hash qformat, qparam files.
        start = time()
        qfile_hashes = (
            hashlib.md5(open(filename, "rb").read()).hexdigest() for filename in qformat_qparam_path
        )
        logger.info(f"Quantization artifacts hashing takes {time() - start:.2f} seconds.")

        to_be_hashed.append(mcp_version)
        to_be_hashed.extend(qfile_hashes)
        to_be_hashed.append(str(quantization_config))

    if allow_bfloat16_cast_with_mcp:
        to_be_hashed.append("allow_bfloat16_cast_with_mcp")
    if extra_args:
        to_be_hashed.append(json.dumps(extra_args, sort_keys=True))

    return get_env_independent_hash(to_be_hashed)


def hash_tensor(tensor: torch.Tensor, deterministic_across_processes: bool = False) -> str:
    """Hash tensor. Same hash if and only if tensors have same values, shapes, and dtypes."""
    key = (tuple(tensor.flatten().tolist()), tensor.shape, tensor.dtype, tensor.stride())
    if deterministic_across_processes:
        hasher = hashlib.sha256()
        for elem in key:
            hasher.update(str(elem).encode())
        return hasher.hexdigest()
    else:
        return str(hash(key))


T = TypeVar("T")


def map_only(ty: Type[T], func: Callable[[T], Any], obj, leaf_types: Sequence[Type] = ()):
    if isinstance(obj, ty):
        return func(obj)
    elif isinstance(obj, (tuple, list)):
        return type(obj)(map_only(ty, func, el, leaf_types=leaf_types) for el in obj)
    elif isinstance(obj, dict):
        return {k: map_only(ty, func, v, leaf_types=leaf_types) for k, v in obj.items()}
    elif isinstance(obj, tuple(leaf_types)):
        return obj
    else:
        raise ValueError(f"Unsupported object {obj} for type {ty}")


def _flatten_example_inputs_into_json_serializable(obj: Any):
    if dataclasses.is_dataclass(obj):
        assert not isinstance(obj, type)
        return {
            field.name: _flatten_example_inputs_into_json_serializable(getattr(obj, field.name))
            for field in dataclasses.fields(obj)
        }
    elif isinstance(obj, (tuple, list)):
        return type(obj)(_flatten_example_inputs_into_json_serializable(el) for el in obj)
    elif isinstance(obj, dict):
        return {k: _flatten_example_inputs_into_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (int, float, bool, str)) or obj is None:
        return obj
    elif isinstance(obj, torch.Tensor):
        return (obj.shape, str(obj.dtype), obj.stride(), str(obj.device))
    else:
        raise ValueError(f"Unsupported object {obj} for type {type(obj)}")


def hash_example_inputs(
    example_args: Sequence,
    example_kwargs: Mapping,
) -> str:
    return get_env_independent_hash(
        json.dumps(
            _flatten_example_inputs_into_json_serializable((example_args, example_kwargs)),
            sort_keys=True,
            indent=2,
        ),
    )


def _get_only_needed_tensor_meta_for_hashing(
    node: Node, gm: GraphModule, include_tensor_stride: bool
) -> Tuple:
    example_val = node.meta.get("val")
    tensor_meta = node.meta.get("tensor_meta")
    if example_val is not None:
        tensor_meta = _extract_tensor_metadata(example_val)
    elif tensor_meta is not None:
        pass
    elif node.op == "get_attr":
        assert isinstance(node.target, str)
        example_val = getattr(gm, node.target)
        tensor_meta = _extract_tensor_metadata(example_val)
    elif node.op == "placeholder" and not node.users:
        # Dead placeholder node. We don't need to hash it.
        return ()
    else:
        raise ValueError(
            "There's no way to get tensor meta from node. Fill 'val' or 'tensor_meta'."
        )

    # We don't care about other information such as memory_format, requires_grad, and quantization metadata.
    def extract_func(tensor_meta: TensorMetadata) -> Tuple:
        if include_tensor_stride:
            return (tensor_meta.shape, tensor_meta.dtype, tensor_meta.stride)
        else:
            return (tensor_meta.shape, tensor_meta.dtype)

    return map_only(TensorMetadata, extract_func, tensor_meta)


# Are 10 iterations sufficient?
_WL_ITERATION = 10
_INFO_ATTR = "label"
_SPECIAL_MARKER_FOR_NODE = "special_marker_for_node_@#$$!##"


def _get_nodes_and_edges_with_metadata(
    gm: GraphModule,
    include_tensor_stride_info: bool,
    exclude_constant_values: bool,
) -> Tuple[Dict[str, Any], List[Tuple[str, str, Any],]]:
    """Returns: Tuple of {node name: node metadata}, [(src, dst, edge_metadata)]"""
    placeholder_cnt = 0

    node_attrs = {}
    type_emulation_in_out: Set
    try:
        type_emulation_in_out = {
            torch.ops.furiosa.type_emulation_in.default,
            torch.ops.furiosa.type_emulation_out.default,
        }
    except AttributeError:
        type_emulation_in_out = set()

    edges = []
    for node in gm.graph.nodes:
        attrs: Dict[str, Any] = {"op": node.op}

        if node.op == "placeholder":
            attrs["idx"] = placeholder_cnt
            attrs["tensor_meta"] = _get_only_needed_tensor_meta_for_hashing(
                node, gm, include_tensor_stride_info
            )
            placeholder_cnt += 1
        elif node.op == "get_attr":
            attrs["tensor_meta"] = _get_only_needed_tensor_meta_for_hashing(
                node, gm, include_tensor_stride_info
            )
            if not exclude_constant_values:
                attrs["tensor_hash"] = hash_tensor(
                    getattr(gm, node.target), deterministic_across_processes=True
                )
        elif node.op == "call_function":
            attrs["target"] = str(node.target)

            node_args = tuple(node.args)
            node_kwargs = dict(node.kwargs)

            if isinstance(node.target, OpOverload):
                node_args, node_kwargs = get_normalized_torch_op_node_args(node)

            # We don't consider Node in kwargs now. It's very rare case.
            flattened_kwargs, _ = tree_flatten(node_kwargs)
            assert all(not isinstance(x, Node) for x in flattened_kwargs)

            # type_emulation_in/out op's third argument is node's name, we don't want it to be used for hashing.
            if node.target in type_emulation_in_out:
                node_args = node_args[:2] + node_args[3:]

            node_replaced_args = tree_map_only(Node, lambda x: _SPECIAL_MARKER_FOR_NODE, node_args)
            node_replaced_kwargs = tree_map_only(
                Node, lambda x: _SPECIAL_MARKER_FOR_NODE, node_kwargs
            )

            attrs["args"] = node_replaced_args
            attrs["kwargs"] = node_replaced_kwargs

            # We don't consider Node in kwargs now. It's very rare case.
            flattened_kwargs, _ = tree_flatten(node_replaced_kwargs)
            assert all(not isinstance(x, Node) for x in flattened_kwargs)

            flattened_args, _ = tree_flatten(node_args)
            for i, arg in enumerate(flattened_args):
                if not isinstance(arg, Node):
                    continue
                edges.append((arg.name, node.name, i))
        elif node.op == "call_module":
            # We only consider fx graph with no call_module node now (e.g., aten-level fx graph).
            raise NotImplementedError("Fx graph containing call module node is not supported yet.")
        elif node.op == "output":
            assert len(node.kwargs) == 0
            node_replaced_args = tree_map_only(Node, lambda x: _SPECIAL_MARKER_FOR_NODE, node.args)
            attrs["args"] = node_replaced_args

            flattened_args, _ = tree_flatten(node.args)
            for i, arg in enumerate(flattened_args):
                if not isinstance(arg, Node):
                    continue
                edges.append((arg.name, node.name, i))
        else:
            raise NotImplementedError(node)

        node_attrs[node.name] = attrs

    return node_attrs, edges


class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (torch.dtype, torch.device)):
            return str(obj)
        elif isinstance(obj, (torch.memory_format, torch.layout)):
            return ""
        else:
            return super().default(obj)


# This function is only for debugging purpose.
def stringify_nodes_metadata(gm: GraphModule, include_tensor_stride_info: bool) -> str:
    nodes_metadata, _ = _get_nodes_and_edges_with_metadata(gm, include_tensor_stride_info, True)
    return json.dumps(nodes_metadata, indent=2, sort_keys=True, cls=_Encoder)


def hash_fx_graph(
    gm: GraphModule,
    include_tensor_stride_info: bool = True,
    nodes_to_exclude: Sequence[str] = [],
    exclude_constant_values: bool = False,
) -> str:
    import networkx as nx  # type: ignore[import-untyped]

    g = nx.DiGraph()

    nodes_metadata, edges = _get_nodes_and_edges_with_metadata(
        gm, include_tensor_stride_info, exclude_constant_values
    )
    for node_to_exclude in nodes_to_exclude:
        nodes_metadata[node_to_exclude] = {}
    for node, metadata in nodes_metadata.items():
        metadata = json.dumps(metadata, indent=2, sort_keys=True, cls=_Encoder)
        g.add_node(node, **{_INFO_ATTR: metadata})

    for src, dst, metadata in edges:
        g.add_edge(src, dst, **{_INFO_ATTR: metadata})

    return nx.weisfeiler_lehman_graph_hash(
        g, node_attr=_INFO_ATTR, edge_attr=_INFO_ATTR, iterations=_WL_ITERATION
    )


def hash_fx_graph_excluding_num_paged_attention_blocks(
    gm: GraphModule, include_tensor_stride_info: bool = True, exclude_constant_values=False
) -> str:
    past_key_value_total_spaces = []

    for node in gm.graph.nodes:
        if node.target not in (torch.ops.aten.index_put.default, torch.ops.aten.index_put_.default):
            continue
        indexee = node.args[0]
        assert isinstance(indexee, Node)
        if indexee.op != "placeholder":
            raise ValueError("Unexpected pattern.")
        past_key_value_total_spaces.append(indexee.name)
    return hash_fx_graph(
        gm,
        include_tensor_stride_info,
        past_key_value_total_spaces,
        exclude_constant_values=exclude_constant_values,
    )


# TODO: Move the following function under `furiosa-compiler-python`
# as it is only used by `compiler.rs`.
def hash_compilation(
    gm: GraphModule,
    example_input_args: Sequence,
    example_input_kwargs: Mapping[str, Any],
    target_npu: str,
    target_ir: str,
    compiler_config: Optional[Mapping],
    experimental_lower_only_einsum_by_dpe: Optional[int],
    graph_metadata: Optional[str],
    extra_args_for_hash: Optional[Mapping],
    only_cpu_tasks=False,
) -> str:
    compiler_version = sp.run(
        ["furiosa-compiler-bridge", "--version"],
        stdout=sp.PIPE,
        stderr=sp.STDOUT,
        text=True,
    ).stdout
    to_be_hashed = [
        hash_fx_graph(gm),
        hash_example_inputs(example_input_args, example_input_kwargs),
        target_npu,
        target_ir,
        json.dumps(compiler_config, sort_keys=True),
        experimental_lower_only_einsum_by_dpe,
        extra_args_for_hash,
        compiler_version,
        only_cpu_tasks,
    ]
    if graph_metadata is not None:
        to_be_hashed.append(graph_metadata)

    return get_env_independent_hash(to_be_hashed)
