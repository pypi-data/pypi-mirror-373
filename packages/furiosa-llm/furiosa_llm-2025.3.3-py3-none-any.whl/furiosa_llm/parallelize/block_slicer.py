from collections import OrderedDict, defaultdict
from contextlib import contextmanager
import copy
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
from itertools import chain
import logging
import re
from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    Final,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    cast,
)

import torch
from torch._subclasses.fake_tensor import FakeCopyMode, FakeTensorMode
from torch.fx import GraphModule, Node
from torch.fx.passes.split_module import split_module
from torch.utils._pytree import tree_flatten, tree_unflatten

from furiosa_llm.parallelize.node_meta import get_original_name, set_color
from furiosa_llm.parallelize.utils import is_typecast_node
from furiosa_llm.parallelize.visualize import draw_graph

# TODO - Find a better way to adopt the block slicer to various models.
# 1st layernorm weight name of GPT-J transformer blocks.
GPTJ_FIRST_LAYERNORM_WEIGHT_PATTERN = r"transformer\.h\.\d+\.ln_1(\.org_target)?\.weight"
# Embedding weight name of GPT-J.
GPTJ_EMBEDDING_WEIGHT_PATTERN = r"transformer\.wte(\.org_target)?\.weight"


# Layernorm biases' names in BERT's embedding or attention output layers.
BERT_EMBEDDING_OR_ATTENTION_OUTPUT_LAYERNORM_BIAS_PATTERN = r"(bert\.encoder\.layer\.\d+\.output\.LayerNorm(\.org_target)?\.bias)|(bert\.embeddings\.LayerNorm(\.org_target)?\.bias)"
# Word embedding weight name of Bert.
BERT_FIRST_EMBEDDING_WEIGHT_PATTERN = r"bert\.embeddings\.word_embeddings(\.org_target)?\.weight"


# Layernorm biases' names in RoBerta's embedding or attention output layers.
ROBERTA_EMBEDDING_OR_ATTENTION_OUTPUT_LAYERNORM_BIAS_PATTERN = r"(roberta\.embeddings\.LayerNorm(\.org_target)?\.bias)|(roberta\.encoder\.layer\.\d+\.output\.LayerNorm(\.org_target)?\.bias)"
# Word embedding weight name of RoBerta.
ROBERTA_FIRST_EMBEDDING_WEIGHT_PATTERN = (
    r"roberta\.embeddings\.word_embeddings(\.org_target)?\.weight"
)


# 1st rms norm weight name of Llama blocks.
# Second pattern is for matching weights in torch ir level graph generated from torchdynamo tracing.
LLAMA_FIRST_RMS_NORM_WEIGHT_PATTERN = r"(model\.layers\.\d+\.input_layernorm(\.org_target)?\.weight)|(L__self___model_layers(_slice_None__\d+__None__)?_(_modules__)?\d+\_(__)?input_layernorm_weight)|(L__self___model_layers_\d+_input_layernorm__forward_method___self___weight)"
# Embedding weight name of Llama.
LLAMA_EMBEDDING_WEIGHT_PATTERN = (
    r"(L__self___model_embed_tokens(\.org_target)?\.weight)|(model\.embed_tokens\.weight)"
)


aten = torch.ops.aten


def _is_mcp_type_emulation(node: Node) -> bool:
    try:
        mcp_emulation_op_types = (
            torch.ops.furiosa.type_emulation_in.default,
            torch.ops.furiosa.type_emulation_out.default,
        )
    except AttributeError:
        logging.warning("torch.ops.furiosa has not been found, check mcp has been loaded")
        return False
    return node.target in mcp_emulation_op_types


def _get_children(
    node: Node,
    skip_type_emulation_nodes: bool = True,
    skip_typecast_nodes: bool = True,
    excludes: AbstractSet[Node] = frozenset(),
) -> List[Node]:
    maybe_children = [node for node in node.users if node not in excludes]

    children = []

    while maybe_children:
        candidate = maybe_children.pop()
        if (skip_type_emulation_nodes and _is_mcp_type_emulation(candidate)) or (
            skip_typecast_nodes and is_typecast_node(candidate)
        ):
            maybe_children.extend(candidate.users)
        else:
            children.append(candidate)
    return children


def _get_children_if_type_emulation(node: Node) -> Node:
    """Return child if child node is type emulation node. Otherwise return `node`."""
    if len(node.users) == 1 and _is_mcp_type_emulation(next(iter(node.users))):
        return next(iter(node.users))
    else:
        assert all(not _is_mcp_type_emulation(child) for child in node.users)
        return node


def _get_child_if_typecast_to_lower_precision(node: Node) -> Node:
    """Return child if child node is typecast node to lower precision. Otherwise return `node`."""
    if len(node.users) != 1:
        return node
    child = next(iter(node.users))

    # TODO: add other typecast ops
    if child.target == torch.ops.aten.to.dtype:
        dst_dtype = child.args[1]
    elif child.target == torch.ops.aten._to_copy.default:
        if "dtype" in child.kwargs:
            dst_dtype = child.kwargs["dtype"]
        else:
            return node
    else:
        return node

    cur_dtype = node.meta["tensor_meta"].dtype
    assert isinstance(dst_dtype, torch.dtype)

    # Return child only if child is typecast node to lower-precision dtype.
    if torch.finfo(cur_dtype).bits > torch.finfo(dst_dtype).bits:
        return child
    else:
        return node


def _get_parent_with_index(
    node: Node,
    arg_index: int,
    skip_type_emulation_nodes: bool = True,
    skip_typecast_nodes: bool = True,
) -> Node:
    parent = node.args[arg_index]
    if not isinstance(parent, Node):
        raise ValueError("`node`'s specified parent is not a Node")

    while True:
        if (skip_type_emulation_nodes and _is_mcp_type_emulation(parent)) or (
            skip_typecast_nodes and is_typecast_node(parent)
        ):
            # Because we only consider ops with only one parent.
            assert len(parent.all_input_nodes) == 1
            parent = parent.all_input_nodes[0]
        else:
            break

    return parent


def _get_parents(
    node: Node,
    skip_type_emulation_nodes: bool = True,
    skip_typecast_nodes: bool = True,
    excludes: AbstractSet[Node] = frozenset(),
    exclude_get_attr_nodes: bool = False,
) -> List[Node]:
    maybe_parents = [node for node in node.all_input_nodes if node not in excludes]

    parents = []

    while maybe_parents:
        candidate = maybe_parents.pop()
        if exclude_get_attr_nodes and candidate.op == "get_attr":
            continue
        if (skip_type_emulation_nodes and _is_mcp_type_emulation(candidate)) or (
            skip_typecast_nodes and is_typecast_node(candidate)
        ):
            maybe_parents.extend(candidate.all_input_nodes)
        else:
            parents.append(candidate)

    return parents


def is_power_of_two(num: int) -> bool:
    return num > 0 and num & (num - 1) == 0


def log_2(num: int) -> int:
    return len(bin(num)) - 3


def _get_only_live_child(node: Node) -> Node:
    live_children = [child for child in node.users if child.users]
    if len(live_children) > 1:
        raise ValueError("Node has more than one live child")
    return live_children[0]


def get_attention_output_layernorm_edge_names(
    gm: torch.fx.GraphModule,
    layernorm_bias_patterns: str,
) -> List[List[Tuple[str, str]]]:
    """Get outgoing edges from layernorm layers with ``layernorm_bias_patterns``."""
    param_constants = (
        n for n in gm.graph.nodes if n.op == 'get_attr' and n.name.startswith("_param")
    )
    layernorm_biases = [
        n for n in param_constants if re.search(layernorm_bias_patterns, get_original_name(n))
    ]
    # Remove the last layernorm bias node because layernorm exists at the end of each block
    # and we will find the boundary by going down from the layernorm node.
    if layernorm_biases:
        layernorm_biases.pop()
    if not layernorm_biases:
        raise ValueError("Layernorm bias not found")
    num_blocks = len(layernorm_biases)
    adds_or_layernorms = [x for y in layernorm_biases for x in _get_children(y)]

    # For this case, logic for finding target node is same regardless of whether layernorm was decomposed or not.
    # Always layernorm_bias's child node is the final node of the layernorm operation.
    _check_nodes_with_expected_ops(
        adds_or_layernorms,
        {
            torch.ops.aten.add.Tensor,
            torch.ops.aten.layer_norm.default,
            torch.ops.aten.native_layer_norm.default,
        },
    )

    # torch.ops.aten.native_layer_norm.default produces multiple tensors and we expect only one child is live.
    if adds_or_layernorms[0].target == torch.ops.aten.native_layer_norm.default:
        xs = [_get_only_live_child(x) for x in adds_or_layernorms]
    else:
        xs = adds_or_layernorms

    xs = [_get_child_if_typecast_to_lower_precision(_get_children_if_type_emulation(x)) for x in xs]

    if len(xs) != num_blocks:
        raise ValueError("Failed to get same number of nodes as blocks")

    x_out_edges = [[(x.name, dst.name) for dst in x.users.keys()] for x in xs]

    return x_out_edges


def _get_nodes_not_with_expected_op(
    nodes: Sequence[Node], expected_ops: AbstractSet[Callable]
) -> Tuple[Node, ...]:
    return tuple(node for node in nodes if node.target not in expected_ops)


def get_first_layernorm_edge_names(
    gm: torch.fx.GraphModule,
    first_layernorm_weight_pattern: str,
) -> List[List[Tuple[str, str]]]:
    """Get the first layernorm's input's output edges' names for each layer.

        +------------------+     +-----+
        | layernorm_weight | --> | mul | <----+
        +------------------+     +-----+      |
                                              |
    +-----+     +-------+     +------+     +-----+
    | pow | <-- |   x   | --> | mean | --> | sub |
    +-----+     +-------+     +------+     +-----+
                  |   |                       ^
    next layer <--+   +-----------------------+

    Starts from layernorm_weight and returns x's 4 out edges for each layer
    """
    param_constants = [
        n for n in gm.graph.nodes if n.op == 'get_attr' and n.name.startswith("_param")
    ]
    first_layernorm_weights = [
        n
        for n in param_constants
        if re.search(first_layernorm_weight_pattern, get_original_name(n))
    ]
    num_blocks = len(first_layernorm_weights)

    if not first_layernorm_weights:
        raise ValueError("First layernorm weights not found")
    muls_or_layernorms = [x for y in first_layernorm_weights for x in _get_children(y)]

    if all(x.target == torch.ops.aten.mul.Tensor for x in muls_or_layernorms):
        # Layernorm has been decomposed
        subs = [
            parent
            for parents in map(_get_parents, muls_or_layernorms)
            for parent in parents
            if parent not in first_layernorm_weights
        ]
        _check_nodes_with_expected_ops(
            subs,
            {
                torch.ops.aten.sub.Tensor,
            },
        )
        xs = [_get_parent_with_index(n, 0) for n in subs]
    elif all(
        x.target in (torch.ops.aten.layer_norm.default, torch.ops.aten.native_layer_norm.default)
        for x in muls_or_layernorms
    ):
        # Layernorm was not decomposed
        # Get "input" parents for layernorm, which is first arg,
        xs = [_get_parent_with_index(layernorm, 0) for layernorm in muls_or_layernorms]
    else:
        not_mul_or_layernorm_ops = _get_nodes_not_with_expected_op(
            muls_or_layernorms,
            {
                torch.ops.aten.mul.Tensor,
                torch.ops.aten.layer_norm.default,
                torch.ops.aten.native_layer_norm.default,
            },
        )
        raise ValueError(
            "Unexpected node type. expected: mul or layernorm, got: {}".format(
                not_mul_or_layernorm_ops[0].target
            )
        )

    if len(xs) != num_blocks:
        raise ValueError("Failed to get same number of nodes as blocks")
    xs = [_get_child_if_typecast_to_lower_precision(x) for x in xs]
    x_out_edges = [[(x.name, dst.name) for dst in x.users.keys()] for x in xs]

    return x_out_edges


def _check_nodes_with_expected_ops(
    nodes: Sequence[Node], expected_ops: AbstractSet[Callable]
) -> None:
    unexpected_nodes = _get_nodes_not_with_expected_op(nodes, expected_ops)
    if unexpected_nodes:
        unexpected_ops = set(node.target for node in unexpected_nodes)
        raise ValueError(f"Unexpected node type. expected: {expected_ops}, got: {unexpected_ops}")


def get_first_rms_norm_edge_names(
    gm: torch.fx.GraphModule,
    first_rms_norm_weight_pattern: str,
) -> List[List[Tuple[str, str]]]:
    param_constants = (
        n for n in gm.graph.nodes if n.op == 'get_attr' and n.name.startswith("_param")
    )

    first_rms_norm_weights = tuple(
        n for n in param_constants if re.search(first_rms_norm_weight_pattern, get_original_name(n))
    )
    num_blocks = len(first_rms_norm_weights)
    if not first_rms_norm_weight_pattern:
        raise ValueError("First rms norm weights not found")

    muls = tuple(x for y in first_rms_norm_weights for x in _get_children(y))
    _check_nodes_with_expected_ops(
        muls,
        {
            torch.ops.aten.mul.Tensor,
        },
    )

    muls_2 = tuple(_get_parents(x, exclude_get_attr_nodes=True)[0] for x in muls)
    _check_nodes_with_expected_ops(
        muls_2,
        {
            torch.ops.aten.mul.Tensor,
        },
    )

    add_or_embeddings = tuple(
        _get_parents(mul, excludes={cast(Node, mul.args[1])})[0] for mul in muls_2
    )
    _check_nodes_with_expected_ops(
        add_or_embeddings, {torch.ops.aten.add.Tensor, torch.ops.aten.embedding.default}
    )

    if len(add_or_embeddings) != num_blocks:
        raise ValueError("Failed to get same number of nodes as blocks")

    xs = [_get_child_if_typecast_to_lower_precision(x) for x in add_or_embeddings]
    add_out_edges = [[(add.name, dst.name) for dst in add.users] for add in xs]

    return add_out_edges


def mark_color_to_node_meta(
    node_to_color: Mapping[Node, Sequence[int]],
) -> None:
    """Assigns colors to the meta attribute of nodes in-place.

    `node_to_color` is a mapping of node names to colors, and `node_name_to_node` is a mapping of
    node names to Node objects. This function modifies the Node objects by reference, meaning the
    original objects are changed. You can create node_name_to_node by
    `{node.name: node for node in gm.graph.nodes}`

    Args:
        node_to_color (Mapping[Node, int]): A mapping of node to colors.
    """
    for node, color in node_to_color.items():
        set_color(node, color)


def bitmap_to_binary_digits(bitmap: int) -> Tuple[int, ...]:
    """Converts a bitmap to a tuple of integers (binary digits).

    Args:
        bitmap (int): The input bitmap.

    Returns:
        Tuple[int]: A tuple of integers (binary digits).
    """
    return tuple(i for i, bit in enumerate(reversed(f"{bitmap:b}")) if bit == '1')


def _propagate_colors(
    gm: torch.fx.GraphModule,
    node_to_bitmap: Mapping[str, int],
) -> Dict[str, int]:
    node_to_bitmap = dict(node_to_bitmap)
    nodes_to_be_colored = {
        node.name for node in gm.graph.nodes if node_to_bitmap.setdefault(node.name, 0) == 0
    }

    # loop until all nodes are colored.
    while nodes_to_be_colored:
        num_nodes_to_color_before_iter = len(nodes_to_be_colored)
        # propagate color to blank ancestors
        need_coloring = set()
        for node in reversed(gm.graph.nodes):
            for x in node.all_input_nodes:
                if node_to_bitmap[x.name] == 0:
                    need_coloring.add(x.name)
                if x.name in need_coloring:
                    node_to_bitmap[x.name] |= node_to_bitmap[node.name]
                    if node_to_bitmap[x.name] != 0:
                        nodes_to_be_colored.discard(x.name)

        # Color dead nodes that are not colored.
        for node in gm.graph.nodes:
            if node_to_bitmap[node.name] == 0:
                if node.users and any(node_to_bitmap[user.name] != 0 for user in node.users):
                    raise ValueError(f"Node {node.name} is not dead node but not colored")
                parent_colors = set(node_to_bitmap[parent.name] for parent in node.all_input_nodes)
                parent_colors.discard(0)
                if len(parent_colors) == 0:
                    continue
                color = reduce(lambda a, b: a & b, parent_colors)
                node_to_bitmap[node.name] = color
                nodes_to_be_colored.discard(node.name)
        if num_nodes_to_color_before_iter == len(nodes_to_be_colored):
            break

    for node in gm.graph.nodes:
        if node_to_bitmap[node.name] == 0:
            if node.op == "output":
                # Output node's color doesn't matter
                node_to_bitmap[node.name] = 1
                continue
            if not node.users and not node.all_input_nodes:
                logging.warning(f"Dead node {node} found. Color it with 1.")
                node_to_bitmap[node.name] = 1
                continue
            raise ValueError(f"node {node.name} is not colored")

    return node_to_bitmap


def _get_blockwise_sliced_color_bitmap_with_split_edges(
    gm: torch.fx.GraphModule,
    split_edges: Sequence[Sequence[Tuple[str, str]]],
) -> Dict[str, int]:
    node_name_to_node = {node.name: node for node in gm.graph.nodes}
    node_to_bitmap: MutableMapping[str, int] = defaultdict(int)
    num_colors = len(split_edges)

    # visit from the last layer (we stop propagating if node is already colored)
    for i, stage_split_points in enumerate(reversed(split_edges)):
        current_color = 1 << (num_colors - i - 1)
        # Mypy differs chain type from iterator type :<
        to_visits = chain(iter(dst for _, dst in stage_split_points))
        while True:
            # explore new node by calling next, break if to_visits is empty
            if (node_name := next(to_visits, None)) is None:
                break
            if node_to_bitmap[node_name]:
                continue
            node_to_bitmap[node_name] |= current_color
            # no more memory required cause we're using dict's iterator
            to_visits = chain(
                to_visits, iter(x.name for x in iter(node_name_to_node[node_name].users))
            )
    return _propagate_colors(gm, node_to_bitmap)


def is_marker_op(node: Node) -> bool:
    return node.op == "call_function" and node.target == torch.ops.furiosa.module_marker.default


def get_blockwise_sliced_color_map(
    gm: torch.fx.GraphModule,
    method: str = "split_by_edges",
    split_edges: Optional[Sequence[Sequence[Tuple[str, str]]]] = None,
    mark_common_ancestor_as_first_layer: bool = False,
    mark_color_to_meta: bool = True,
) -> Tuple[Dict[str, Tuple[int, ...]], Optional[Dict[int, Any]]]:
    """Assigns a unique color to each node in the graph based on the specified split edges.


    If `mark_common_ancestor_as_first_layer` is True, the common ancestor of all nodes is marked as
    the first layer (i.e., color 1). If `mark_color_to_meta` is True, the color is assigned to the
    meta attribute of the nodes.

    Args:
        gm: The input graph module.
        method: The method to use for block slicing. It can be either "marker" or "split_by_edges".
            Defaults to "split_by_edges".
        split_edges: A Sequence of sequences where each inner list represents a stage boundaries,
            and each tuple within the inner list represents an edge between two node names (source,
            destination) indicating the split points for that stage.
        mark_common_ancestor_as_first_layer: If True, the common ancestor of all nodes is marked as
            the first layer (i.e., color 1).
        mark_color_to_meta: If True, the color is assigned to the meta attribute of the nodes.

    Returns:
        Tuple[Dict[str, int], Optional[Dict[str, Any]]]: Tuple of dictionary mapping each node name to its assigned color
            and optional dictionary mapping each color to its metadata generated during block slicing.
    """

    if method == "marker":
        node_to_bitmap, color_to_metadata = get_blockwise_sliced_color_bitmap_with_marker(gm)
    elif method == "split_by_edges":
        if split_edges is None:
            raise ValueError("split_edges must be provided when `method`==\"split_edges\".")
        node_to_bitmap = _get_blockwise_sliced_color_bitmap_with_split_edges(gm, split_edges)
        color_to_metadata = None
    else:
        raise ValueError(f"Invalid block slicing method: {method}")

    node_to_color: Dict[str, Tuple[int, ...]] = {}
    for node in gm.graph.nodes:
        if is_marker_op(node):
            continue
        color_bitmap = node_to_bitmap[node.name]
        assert color_bitmap > 0, f"Node {node.name} is not colored"
        node_to_color[node.name] = bitmap_to_binary_digits(color_bitmap)

    # Mark common ancestor with first child block. Note that first child block might
    # not be the first block.
    if mark_common_ancestor_as_first_layer:
        for node in gm.graph.nodes:
            if is_marker_op(node):
                continue
            block_indices = node_to_color[node.name]
            if len(block_indices) > 1:
                node_to_color[node.name] = (min(block_indices),)

    if mark_color_to_meta:
        node_name_to_node = {node.name: node for node in gm.graph.nodes}
        mark_color_to_node_meta(
            {node_name_to_node[node_name]: color for node_name, color in node_to_color.items()}
        )

    return node_to_color, color_to_metadata


def get_first_embedding_edge_names(
    gm: GraphModule,
    embedding_weight_pattern: str,
) -> List[List[Tuple[str, str]]]:
    param_constants = (
        n for n in gm.graph.nodes if n.op == 'get_attr' and n.name.startswith("_param")
    )
    embedding_weights = [
        n for n in param_constants if re.search(embedding_weight_pattern, get_original_name(n))
    ]

    assert len(embedding_weights) == 1
    embedding_weight = embedding_weights[0]

    assert len(embedding_weight.users) == 1
    return [[(embedding_weight.name, next(iter(embedding_weight.users)).name)]]


MODEL_ARCH_TO_BLOCK_SPLITTER_AND_WEIGHT_NODE_PATTERN: Final[
    Dict[str, List[Tuple[Callable[[GraphModule, str], List[List[Tuple[str, str]]]], str]]]
] = {
    "GPTJForCausalLM": [
        (get_first_embedding_edge_names, GPTJ_EMBEDDING_WEIGHT_PATTERN),
        (get_first_layernorm_edge_names, GPTJ_FIRST_LAYERNORM_WEIGHT_PATTERN),
    ],
    "BertForQuestionAnswering": [
        (get_first_embedding_edge_names, BERT_FIRST_EMBEDDING_WEIGHT_PATTERN),
        (
            get_attention_output_layernorm_edge_names,
            BERT_EMBEDDING_OR_ATTENTION_OUTPUT_LAYERNORM_BIAS_PATTERN,
        ),
    ],
    "RobertaForQuestionAnswering": [
        (get_first_embedding_edge_names, BERT_FIRST_EMBEDDING_WEIGHT_PATTERN),
        (
            get_attention_output_layernorm_edge_names,
            ROBERTA_EMBEDDING_OR_ATTENTION_OUTPUT_LAYERNORM_BIAS_PATTERN,
        ),
    ],
    "LlamaForCausalLM": [
        (get_first_embedding_edge_names, LLAMA_EMBEDDING_WEIGHT_PATTERN),
        (get_first_rms_norm_edge_names, LLAMA_FIRST_RMS_NORM_WEIGHT_PATTERN),
    ],
}


def _get_edges_from_slicing_info(gm, info):
    block_slicing_function, *args = info
    return block_slicing_function(gm, *args)


def get_block_slicing_edges(
    gm: GraphModule,
    original_model_type: Type[torch.nn.Module],
    embedding_layer_as_single_block: bool,
) -> List[List[Tuple[str, str]]]:
    original_model_type_name = original_model_type.__name__

    if block_slicing_info := MODEL_ARCH_TO_BLOCK_SPLITTER_AND_WEIGHT_NODE_PATTERN.get(
        original_model_type_name
    ):
        if embedding_layer_as_single_block:
            return sum([_get_edges_from_slicing_info(gm, info) for info in block_slicing_info], [])
        else:
            # In this case, first block should be integrated with second block.
            return sum([_get_edges_from_slicing_info(gm, info) for info in block_slicing_info], [])[
                1:
            ]
    else:
        raise NotImplementedError(f"Block slicing for {original_model_type_name} is not supported.")


def get_blockwise_sliced_gms(
    original_gm: torch.fx.GraphModule,
    node_to_color: Mapping[str, Sequence[int]],
    common_ancestor_as_first_layer: bool = False,
    keep_original_order: bool = False,
) -> List[Tuple[int, torch.fx.GraphModule]]:
    """Slices the input graph module into multiple graph modules based on the assigned colors.

    Args:
        original_gm: The input graph module.
        node_to_color: A dictionary mapping each node name to its assigned color.
        common_ancestor_as_first_layer: If True, assumes the common ancestor of all nodes is marked
            as the first layer (i.e., color 1).
        keep_original_order: If True, the original order of the graph modules is preserved.

    Returns:
        List[Tuple[int, torch.fx.GraphModule]]: A list of tuples where each tuple contains the
            color and the corresponding sliced graph module.
    """
    colors = set(node_to_color.values())
    gms = []

    for color in colors:
        if common_ancestor_as_first_layer:

            def key(x):
                assert len(node_to_color[x.name]) == 1
                return node_to_color[x.name][0]

        else:
            if len(color) != 1:
                continue

            # if common part, return current `color` else return node's annotated color
            def key(x):
                node_color = node_to_color[x.name]
                if len(node_color) != 1:
                    return color[0]
                return node_color[0]

        with FakeTensorMode(allow_non_fake_inputs=True) as mode:
            with FakeCopyMode(mode):
                gm = deepcopy(original_gm)
        # To avoid the circular dependency error, delete [common] -> [rest color] edges
        for n in gm.graph.nodes:
            if node_to_color[n.name] != color:
                # if [x] -> [n] is [common] -> [rest color] edge, replace x with dummy node
                raw_args, specs = tree_flatten((n.args, n.kwargs))
                for i, x in enumerate(raw_args):
                    if (
                        isinstance(x, torch.fx.Node)
                        and node_to_color[x.name] != node_to_color[n.name]
                        and len(node_to_color[x.name]) > 1
                    ):
                        raw_args[i] = None
                n.args, n.kwargs = tree_unflatten(raw_args, specs)
        gm.recompile()

        # FIXME: there's a bug (KeyError raised) if `keep_original_order=True`
        sliced = split_module(gm, gm, key, keep_original_order=keep_original_order)

        gms.append((color[0], deepcopy(getattr(sliced, f"submod_{color[0]}"))))
        # hopefully release memory
        del sliced, gm

    return gms


def is_input_marker(node) -> bool:
    return is_marker_op(node) and node.args[1] == "input"


def is_output_marker(node) -> bool:
    return is_marker_op(node) and node.args[1] == "output"


def get_module_path_for_marker_node(node: Node) -> str:
    assert is_marker_op(node)
    assert isinstance(node.args[2], str)
    return node.args[2]


def get_blockwise_sliced_color_bitmap_with_marker(
    gm_with_module_markers: GraphModule,
) -> Tuple[Dict[str, int], Dict[int, Any]]:
    module_name_to_containing_nodes: OrderedDict[Optional[str], List[Node]] = OrderedDict()
    node_to_belonging_module: Dict[Node, Optional[str]] = {}

    # We don't want to affect original gm but share parameter/buffers without physical copy.
    gm_with_module_markers = GraphModule(
        gm_with_module_markers, copy.deepcopy(gm_with_module_markers.graph)
    )

    # Replicate get_attr nodes with more than one users to make coloring process easier.
    original_node_to_replicas = {}
    for node in gm_with_module_markers.graph.nodes:
        if node.op == "get_attr" and len(node.users) > 1:
            replicas = [node.name]
            for user in tuple(node.users)[1:]:
                with gm_with_module_markers.graph.inserting_after(node):
                    new_node = gm_with_module_markers.graph.get_attr(node.target)
                    new_node.meta = node.meta.copy()
                    user.replace_input_with(node, new_node)
                    replicas.append(new_node.name)
            original_node_to_replicas[node.name] = replicas

    # Manipulate graph so that any two submodule areas (surrounded by input / output marker nodes) in graph
    # are not overlapped. This occurs even though two submodules are actually not in the parent-child relationship
    # in the original model.
    for node in gm_with_module_markers.graph.nodes:
        if not is_input_marker(node):
            continue
        assert len(node.all_input_nodes) == 1
        assert all(not is_input_marker(parent) for parent in node.all_input_nodes)

        parent_node = node.all_input_nodes[0]
        module_path = get_module_path_for_marker_node(node)

        assert isinstance(node.args[0], Node)
        for child in tuple(node.users.keys()):
            if not is_input_marker(child):
                continue
            child_module_path = get_module_path_for_marker_node(child)
            if child_module_path.startswith(module_path):
                raise ValueError(
                    f"Marked module {module_path} contains another marked module {child_module_path}. \
                    To use auto block slicer, any two marked submodules should not be overlapped."
                )
            child.replace_input_with(node, parent_node)

    draw_graph(gm_with_module_markers, "gm_with_module_markers")

    # Add container module info for all nodes except output.
    # Visit nodes in topological order. Belonging modules will be added to `module_name_to_containing_nodes` in topological order.
    for node in gm_with_module_markers.graph.nodes:
        if node.op == "output":
            continue
        parent_belonging_modules = set(
            node_to_belonging_module[parent] for parent in node.all_input_nodes
        )
        parent_belonging_modules.discard(None)
        if len(parent_belonging_modules) > 1:
            raise ValueError(
                f"Node {node} has multiple parents with different belonging modules: {parent_belonging_modules}"
            )
        belonging_module = next(iter(parent_belonging_modules), None)
        if is_marker_op(node):
            if is_input_marker(node):
                # Update belonging module
                assert isinstance(node.args[2], str)
                belonging_module = node.args[2]
            else:
                # output marker
                assert is_output_marker(node)
                assert belonging_module is not None
                belonging_module = None
        node_to_belonging_module[node] = belonging_module
        module_name_to_containing_nodes.setdefault(belonging_module, []).append(node)

    # Remove marker nodes.
    for node in gm_with_module_markers.graph.nodes:
        if is_marker_op(node):
            node.replace_all_uses_with(node.args[0])
            gm_with_module_markers.graph.erase_node(node)

    # Pop nodes with no container module.
    module_name_to_containing_nodes.pop(None, None)

    node_to_bitmap = {}
    partition_idx_to_module_name = {}
    for partition_idx, (module_name, nodes) in enumerate(module_name_to_containing_nodes.items()):
        for node in nodes:
            node_to_bitmap[node.name] = 1 << partition_idx
        partition_idx_to_module_name[partition_idx] = module_name

    node_to_bitmap = _propagate_colors(gm_with_module_markers, node_to_bitmap)

    # Gather colors from replicas and merge into original node.
    for original_node, replicas in original_node_to_replicas.items():
        new_color = 1
        for replica in replicas:
            new_color |= node_to_bitmap.pop(replica)
        node_to_bitmap[original_node] = new_color

    return node_to_bitmap, partition_idx_to_module_name


def add_marker_op_hooks(
    model: torch.nn.Module,
    module_selector: Callable[[str, torch.nn.Module], bool],
    allow_overlapping_submodule_selection: bool = True,
) -> Callable[[], None]:
    """
    Mark all the modules in the model with a module marker.
    Returns a hook that can be used to remove the markers.
    """
    hooks = []
    module_marker = torch.ops.furiosa.module_marker
    assert callable(module_marker)

    if not allow_overlapping_submodule_selection:
        module_selector = SubmoduleSelector(module_selector)

    def tree_map_tensors(
        obj, arg_name: str, tensor_map_func: Callable[[torch.Tensor, str], torch.Tensor]
    ):
        if isinstance(obj, torch.Tensor):
            return tensor_map_func(obj, arg_name)
        elif isinstance(obj, (list, tuple)):
            return type(obj)(
                tree_map_tensors(el, f"{arg_name}_{idx}", tensor_map_func)
                for idx, el in enumerate(obj)
            )
        elif isinstance(obj, dict):
            return {
                key: tree_map_tensors(value, f"{arg_name}_{key}", tensor_map_func)
                for key, value in obj.items()
            }
        else:
            return obj

    try:
        for module_name, sub_module in model.named_modules():
            if not module_selector(module_name, sub_module):
                continue

            def marker_pre_hook(module, input_, kwargs, name=module_name):
                input_ = list(input_)
                for idx, v in enumerate(input_):
                    input_[idx] = tree_map_tensors(
                        v,
                        str(idx),
                        lambda t, arg_name: module_marker(
                            t,
                            "input",
                            name,
                            f"{module.__class__.__module__}.{module.__class__.__name__}",
                            arg_name,
                        ),
                    )

                for k, v in kwargs.items():
                    kwargs[k] = tree_map_tensors(
                        v,
                        k,
                        lambda t, arg_name: module_marker(
                            t,
                            "input",
                            name,
                            f"{module.__class__.__module__}.{module.__class__.__name__}",
                            arg_name,
                        ),
                    )

                return (tuple(input_), kwargs)

            def marker_post_hook(module, args, kwargs, output, name=module_name):
                return tree_map_tensors(
                    output,
                    "",
                    lambda t, arg_name: module_marker(
                        t,
                        "output",
                        name,
                        f"{module.__class__.__module__}.{module.__class__.__name__}",
                        arg_name,
                    ),
                )

            hooks.append(sub_module.register_forward_pre_hook(marker_pre_hook, with_kwargs=True))
            hooks.append(sub_module.register_forward_hook(marker_post_hook, with_kwargs=True))
    except:
        for hook in hooks:
            hook.remove()
        raise

    def remove_hooks():
        for hook in hooks:
            hook.remove()

    return remove_hooks


@dataclass
class ModuleMarkConfig:
    class_pattern: Optional[str] = None
    module_path_pattern: Optional[str] = None
    include_submodules_in_modulelists: bool = False


def get_submodule_paths_in_modulelists(model: torch.nn.Module) -> Tuple[str, ...]:
    module_lists = [m for m in model.named_modules() if isinstance(m[1], torch.nn.ModuleList)]
    return tuple(
        f"{parent_module_path}.{child_module_path}"
        for parent_module_path, module_list in module_lists
        for child_module_path, _ in module_list.named_children()
    )


_PRESENT_KEY = ".#_present_#."


class SubmoduleSelector:
    def __init__(self, selector: Callable[[str, torch.nn.Module], bool]):
        self.selector = selector
        self.selected_submodule_tree: Dict[str, Any] = {}

    def __call__(self, submodule_path: str, submodule: torch.nn.Module) -> bool:
        selected = self.selector(submodule_path, submodule)

        if selected:
            cur_node = self.selected_submodule_tree
            splitted = submodule_path.split(".")
            for i, cur_dir in enumerate(splitted):
                if _PRESENT_KEY in cur_node:
                    # Ancestor of this submodule was already selected.
                    raise ValueError(
                        f"Overlapping submodules are selected: {submodule_path} and {'.'.join(splitted[:i + 1])}."
                    )
                cur_node = cur_node.setdefault(cur_dir, {})

            cur_node[_PRESENT_KEY] = True
            if len(cur_node) > 1:
                # Descendant of this submodule was already selected.
                first_key = next(k for k in cur_node.keys() if k != _PRESENT_KEY)
                cur = cur_node[first_key]
                descendant_path = f"{submodule_path}.{first_key}"
                while _PRESENT_KEY not in cur:
                    next_key, cur = next(iter(cur_node.items()))
                    descendant_path += f".{next_key}"
                raise ValueError(
                    f"Overlapping submodules are selected: {descendant_path} and {submodule_path}."
                )

        return selected


@contextmanager
def enable_marker_op(
    model: torch.nn.Module,
    module_mark_config: ModuleMarkConfig,
    allow_overlapping_submodule_selection: bool = True,
):
    if module_mark_config.include_submodules_in_modulelists:
        submodule_paths = get_submodule_paths_in_modulelists(model)

    def module_selector(module_path: str, module: torch.nn.Module) -> bool:
        return bool(
            (
                module_mark_config.class_pattern
                and re.match(
                    module_mark_config.class_pattern,
                    f"{module.__class__.__module__}.{module.__class__.__name__}",
                )
            )
            or (
                module_mark_config.module_path_pattern
                and re.match(module_mark_config.module_path_pattern, module_path)
            )
            or (module_path in submodule_paths)
        )

    hook_remover = add_marker_op_hooks(
        model,
        module_selector,
        allow_overlapping_submodule_selection=allow_overlapping_submodule_selection,
    )
    try:
        yield
    finally:
        hook_remover()


def remove_marker_nodes(gm: GraphModule) -> None:
    for node in gm.graph.nodes:
        if is_marker_op(node):
            node.replace_all_uses_with(node.args[0])
            gm.graph.erase_node(node)
    gm.recompile()
