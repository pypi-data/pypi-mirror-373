from collections import defaultdict
from functools import reduce
import operator
from typing import (
    Any,
    DefaultDict,
    Dict,
    List,
    MutableMapping,
    NamedTuple,
    Optional,
    Sequence,
    cast,
)

import furiosa_torch_ext.torch_ext as torch_ext
from furiosa_torch_ext.torch_ext import STD_DECOMPOSITIONS, do_make_fx
import torch
from torch._dynamo.utils import deepcopy_to_fake_tensor
from torch._guards import detect_fake_mode
from torch.fx import Graph, GraphModule, Node
from torch.fx.passes.shape_prop import TensorMetadata, _extract_tensor_metadata
from torch.fx.passes.split_module import split_module
from torch.utils._pytree import tree_flatten, tree_map_only

from furiosa_llm.parallelize.model_rewriter.mppp_config import DeviceId
from furiosa_llm.parallelize.model_rewriter.ops.utils import is_single_dev_comm_op
from furiosa_llm.parallelize.node_meta import (
    add_tensor_meta,
    get_color,
    get_device_id,
    get_original_name,
    has_original_name,
    set_color,
    set_original_name,
)
from furiosa_llm.parallelize.utils import is_kvcache


# revert shape of parameters to its original shape in fx graph before make_fx.
# NOTE: parameters in GraphModule are transposed in make_fx when it's used by aten.mm.default node.
# I'm not sure this covers all the cases and same problem occurs in other torch versions.
def revert_parameter_shapes_to_before_makefx(gm_after_makefx: GraphModule):
    for node in gm_after_makefx.graph.nodes:
        if node.op != "get_attr":
            continue
        need_transpose = any(str(user.target) == "aten.mm.default" for user in node.users.keys())

        if need_transpose:
            original_constant = getattr(gm_after_makefx, node.name)
            # NOTE: we only consider param with 2 dims
            assert len(original_constant.shape) == 2
            setattr(gm_after_makefx, node.name, original_constant.t())

            with gm_after_makefx.graph.inserting_after(node):
                new_node = gm_after_makefx.graph.create_node(
                    "call_function", torch.ops.aten.transpose.int, (node, 0, 1)
                )

            node.replace_all_uses_with(
                new_node, delete_user_cb=lambda x: x != new_node, propagate_meta=True
            )

    gm_after_makefx.recompile()


def _get_first_call_function_node(graph: Graph) -> Optional[Node]:
    for node in graph.nodes:
        if node.op == "call_function":
            return node
    return None


# is node a submodule that just contains single collective communication?
def _is_replaced_cc(gm: GraphModule, node: Node, submod_prefix: str) -> bool:
    return (
        node.op == "call_module"
        and node.name.startswith(submod_prefix)
        and any(
            is_single_dev_comm_op(node)
            for node in tuple(getattr(gm, cast(str, node.target)).graph.nodes)
        )
    )


def _correct_node_color_info_from_dev_id(gm: GraphModule) -> None:
    colors_per_dev_id = defaultdict(set)

    # Find actually assigned colors per device ids.
    for node in gm.graph.nodes:
        if is_single_dev_comm_op(node) or node.op == "output":
            continue
        colors = get_color(node)
        assert isinstance(colors, Sequence)
        if len(colors) == 1:
            dev_id = get_device_id(node)
            assert isinstance(dev_id, DeviceId)
            colors_per_dev_id[dev_id].add(colors[0])

    # Filter out colors that are not assigned to corresponding node's assigned device.
    # This is needed because in the node replication stage, each node's color metadata
    # was copied to the replicated ones.
    for node in gm.graph.nodes:
        if is_single_dev_comm_op(node) or node.op == "output":
            continue
        colors = get_color(node)
        assert isinstance(colors, Sequence)
        dev_id = get_device_id(node)
        assert isinstance(dev_id, DeviceId)

        colors = tuple(color for color in colors if color in colors_per_dev_id[dev_id])
        set_color(node, colors)


def replicate_nodes_with_multiple_colors(gm: GraphModule) -> None:
    to_be_erased = []

    # We need to replicate nodes colored with more than one colors.
    node_to_replicated_node: MutableMapping[Node, Dict[int, Node]] = defaultdict(dict)
    for node in gm.graph.nodes:
        if is_single_dev_comm_op(node) or node.op == "output":
            continue
        colors = get_color(node)
        assert isinstance(colors, Sequence)

        # Don't care about nodes with one color.
        if len(colors) == 1:
            continue

        # Don't need to placeholder, get_attr nodes. These nodes can be shared across partitions.
        if node.op in ("placeholder", "get_attr"):
            for color in colors:
                node_to_replicated_node[node][color] = node
            continue

        # Create replica node of the node for each color. Each replica should be connected to the parent node's replica with same color.
        # ASSUMPTION: the node with multiple colors' all parent nodes are all have same colors.
        for color in colors:
            with gm.graph.inserting_before(node):
                new_args = tree_map_only(
                    Node, lambda x: node_to_replicated_node[x][color], node.args
                )
                new_kwargs = tree_map_only(
                    Node, lambda x: node_to_replicated_node[x][color], node.kwargs
                )
                new_node = gm.graph.create_node(node.op, node.target, new_args, new_kwargs)
                new_node.meta = node.meta.copy()
                set_color(new_node, [color])

                node_to_replicated_node[node][color] = new_node

        # Change children (users) with one color to point to the proper replica node with same color.
        for user in tuple(node.users.keys()):
            user_colors = get_color(user)
            assert isinstance(user_colors, Sequence)
            if len(user_colors) != 1:
                continue
            user_color = user_colors[0]
            user.args = tree_map_only(
                Node,
                lambda x: node_to_replicated_node[x][user_color] if x == node else x,
                user.args,
            )
            user.kwargs = tree_map_only(
                Node,
                lambda x: node_to_replicated_node[x][user_color] if x == node else x,
                user.kwargs,
            )
        to_be_erased.append(node)

    # Erase original node.
    for node in reversed(to_be_erased):
        gm.graph.erase_node(node)


# TODO: refactor this.
def partition_gm(
    gm: GraphModule,
    submod_prefix: str,
    one_supertask_per_device: bool = False,
    use_color_for_partitioning: bool = False,
) -> GraphModule:
    """Transform FX graph into one that is composed of submodules.

    Each submodule is either a collection of computations on same single device or a single collective communication.
    In FX graph, collection of computations are "call_module" node for submodule and collective communication nodes remain same.
    """
    _node_to_partition: DefaultDict[str, Any] = defaultdict(lambda: 1)
    node_to_children: DefaultDict[str, List[str]] = defaultdict(list)
    comm_ops = set()
    partition_cnt = 0
    node_name_to_node = {node.name: node for node in gm.graph.nodes}

    if one_supertask_per_device:
        if use_color_for_partitioning:
            _correct_node_color_info_from_dev_id(gm)
            replicate_nodes_with_multiple_colors(gm)

        def splitter(node):
            if is_single_dev_comm_op(node):
                return node.name
            else:
                color = get_color(node)
                if use_color_for_partitioning:
                    assert isinstance(color, Sequence) and len(color) == 1
                    return f"d{get_device_id(node)}-c{color[0]}"
                else:
                    return f"d{get_device_id(node)}"

        splitted = split_module(gm, gm, splitter)
    else:
        if use_color_for_partitioning:
            # TODO
            raise NotImplementedError(
                "Colorwise partitioning without one_supertask_per_device option is not supported yet."
            )
        # calculate node -> its children mapping
        for node in gm.graph.nodes:
            for parent in node.all_input_nodes:
                node_to_children[parent.name].append(node.name)

        to_search = []

        for node in gm.graph.nodes:
            if node.op in ("placeholder", "get_attr", "output"):
                continue
            if node.op == "call_function":
                if not is_single_dev_comm_op(node):
                    continue
                comm_ops.add(node.name)
                _node_to_partition[node.name] = 1 << partition_cnt
                partition_cnt += 1
                for child in node_to_children[node.name]:
                    to_search.append((child, 1 << partition_cnt))

        descendants: Dict[str, List[str]] = {}

        def descendants_of_node(node: str) -> List[str]:
            if node in descendants:
                return descendants[node]
            ret: List[str] = list(
                set(
                    reduce(
                        operator.add,
                        map(lambda n: descendants_of_node(n) + [n], node_to_children[node]),
                        [],
                    )
                )
            )
            descendants[node] = ret
            return ret

        # to prevent reaching recursion limit
        for node in reversed(gm.graph.nodes):
            descendants_of_node(node.name)

        # color each node.
        for node, partition_color in to_search:
            _node_to_partition[node] |= partition_color

            for desc in descendants_of_node(node):
                _node_to_partition[desc] |= partition_color

        for node in gm.graph.nodes:
            if node.name not in _node_to_partition:
                _node_to_partition[node.name] = 0

        for comm_op in comm_ops:
            del _node_to_partition[comm_op]

        for node_name in tuple(_node_to_partition.keys()):
            node = node_name_to_node[node_name]
            if node.op == "output":
                del _node_to_partition[node_name]
                continue
            device_id = get_device_id(node)

            new_partition = (device_id, _node_to_partition[node_name])
            _node_to_partition[node_name] = new_partition

        # normalize partition numbers
        partition_num_normalizer = dict(
            (v, i) for i, v in enumerate(tuple(set(_node_to_partition.values())))
        )

        node_to_partition = dict(
            map(
                lambda kv: (kv[0], partition_num_normalizer[kv[1]]),
                _node_to_partition.items(),
            )
        )

        # maintain name of comm ops
        for i, comm_op in enumerate(comm_ops):
            node_to_partition[comm_op] = comm_op

        for node in gm.graph.nodes:
            if node.op == "get_attr":
                if len(node_to_children[node.name]) == 0:
                    continue
                children_partitions = map(
                    lambda x: node_to_partition[x], node_to_children[node.name]
                )
                node_to_partition[node.name] = next(children_partitions)

        partition_to_node = defaultdict(list)

        for k, v in node_to_partition.items():
            partition_to_node[v].append(k)

        def splitter(node):
            assert node.name in node_to_partition
            return node_to_partition[node.name]

        splitted = split_module(gm, gm, splitter)

    output_node_meta = tuple(gm.graph.nodes)[-1].meta.copy()

    for node in tuple(splitted.graph.nodes):
        if _is_replaced_cc(splitted, node, submod_prefix):
            # Replace wrapped cc node which is a call_module node that calls cc inside with call_function node.
            actual_op_node = _get_first_call_function_node(getattr(splitted, node.name).graph)
            assert actual_op_node is not None
            assert is_single_dev_comm_op(actual_op_node)

            with splitted.graph.inserting_after(node):
                new_node = splitted.graph.call_function(actual_op_node.target)

            new_node.meta = actual_op_node.meta.copy()
            new_node.args = node.args
            node.replace_all_uses_with(new_node)
            splitted.graph.erase_node(node)

    for node in splitted.graph.nodes:
        # If tensor_meta doesn't exist, add it.
        if "tensor_meta" not in node.meta and node.op != "output":
            add_tensor_meta(node, gm=splitted)

    splitted.recompile()

    # restore output node metadata
    tuple(splitted.graph.nodes)[-1].meta = output_node_meta

    # comm ops
    for comm_op in comm_ops:
        assert getattr(splitted, f"{submod_prefix}_{comm_op}") is not None

    return splitted


def convert_to_fake_gm(gm: GraphModule, inputs, fake_mode=None) -> GraphModule:
    """Convert a GraphModule to a GraphModule with fake tensors"""

    if fake_mode is None:
        fake_mode_set = set(map(lambda x: x.fake_mode, inputs))

        assert (
            len(fake_mode_set) == 1
        ), "All the parameters and buffers must have the same FakeTensorMode"

        fake_mode = fake_mode_set.pop() or detect_fake_mode(inputs)

    fake_gm = deepcopy_to_fake_tensor(gm, fake_mode)

    fake_inputs = [fake_mode.from_tensor(t, static_shapes=True) for t in inputs]

    # trace module with fake module
    with fake_mode:
        gm = do_make_fx(fake_gm, fake_inputs, decomposition_table=STD_DECOMPOSITIONS)

    return gm


def _get_index_batch_size_for_beam_search_kv_cache_sharing_model(
    index_op_node: Node, input_ids_batch_size: int
) -> int:
    assert index_op_node.target == torch.ops.aten.index.Tensor

    # Find first concatenation which concats past k/v cache with newly generated k/v.
    cur = index_op_node
    while True:
        if len(cur.users) != 1:
            raise ValueError(
                "Unexpected pattern. We expect concatenated k/v to be 4-dimensional tensor."
            )
        child = next(iter(cur.users))
        if child.target == torch.ops.aten.cat.default:
            break
        cur = child

    concatenated_shape = child.meta["tensor_meta"].shape
    if len(concatenated_shape) != 4:
        raise ValueError(
            "Unexpected pattern. We expect concatenated k/v to be 4-dimensional tensor."
        )

    # Assume sequence length doesn't change from index to concat.
    k_or_v_cache_shape_before_concat = cur.meta["tensor_meta"].shape
    mul_of_batch_size_and_seq_length_before_concat = (
        k_or_v_cache_shape_before_concat[0] * k_or_v_cache_shape_before_concat[1]
    )
    if mul_of_batch_size_and_seq_length_before_concat % input_ids_batch_size != 0:
        raise ValueError(
            "Unexpected pattern. We expect batch size and sequence length to be first two dimensions of k/v cache (Order doesn't matter)."
        )

    seq_length = mul_of_batch_size_and_seq_length_before_concat // input_ids_batch_size

    index_output_shape = index_op_node.meta["tensor_meta"].shape
    mul_of_batch_size_and_seq_length_after_index = index_output_shape[0] * index_output_shape[1]

    if mul_of_batch_size_and_seq_length_after_index % seq_length != 0:
        raise ValueError(
            "Unexpected pattern. We expect multiplication of index output tensor's first two dimensions equals to multiplication of batch size and sequence length."
        )
    return mul_of_batch_size_and_seq_length_after_index // seq_length


def _get_input_ids_batch_size(graph: Graph) -> int:
    input_ids_node = tuple(
        node
        for node in graph.nodes
        if node.op == "placeholder"
        and has_original_name(node)
        and get_original_name(node) == "input_ids"
    )
    if len(input_ids_node) != 1:
        raise ValueError("Multiple input id nodes exist. This is different from expected.")
    input_ids_shape = input_ids_node[0].meta["tensor_meta"].shape
    if len(input_ids_shape) != 2:
        raise ValueError("Input ids shape is different from expected.")
    return input_ids_shape[0]


def replace_paged_attention_index_ops_with_furiosa_sparse_index(
    graph: Graph,
    dummy_index: int,
    model_use_beam_search_kv_cache_sharing: bool,
    sparse_select_version: str,
) -> None:
    input_ids_batch_size = _get_input_ids_batch_size(graph)

    index_op_nodes = [node for node in graph.nodes if node.target == torch.ops.aten.index.Tensor]

    if model_use_beam_search_kv_cache_sharing:
        # To ensure `past_valid_key_prompt_indices` indexing nodes goes before `past_valid_key_decode_indices` indexing nodes.
        index_op_nodes.sort(
            key=lambda node: _get_index_batch_size_for_beam_search_kv_cache_sharing_model(
                node, input_ids_batch_size
            )
        )

    prompt_batch_size = None

    for node in index_op_nodes:
        input_tensor = node.args[0]

        found = False
        queue = [input_tensor]

        # Check index op node is one for kv cache indexing.
        while queue:
            next_ = queue.pop()
            if next_.op == "placeholder" and is_kvcache(get_original_name(next_)):
                # Assume dimension of total kv cache space is 4
                if len(next_.meta["tensor_meta"].shape) != 4:
                    raise ValueError(
                        "Unexpected pattern: input kv cache tensor should be 4-dimensional."
                    )
                # If kv cache total space is its ancestor, we consider this index op as one for paged attention indexing.
                found = True
                break
            args, _ = tree_flatten((next_.args, next_.kwargs))
            for arg in args:
                if not isinstance(arg, Node):
                    continue
                queue.append(arg)

        if found:
            indices = node.args[1]
            if len(indices) != 1:
                raise NotImplementedError("We only consider index ops with single index tensor.")
            index_tensor_node = indices[0]
            index_tensor_shape = index_tensor_node.meta["tensor_meta"].shape

            if model_use_beam_search_kv_cache_sharing:
                batch_size = _get_index_batch_size_for_beam_search_kv_cache_sharing_model(
                    node, input_ids_batch_size
                )
                if input_ids_batch_size == batch_size:
                    # indexing for "past_valid_{key|value}_decode"s
                    assert prompt_batch_size is not None
                    beam_width = batch_size // prompt_batch_size
                else:
                    # indexing for "past_valid_{key|value}_prompt"s
                    if prompt_batch_size is None:
                        prompt_batch_size = batch_size
                    else:
                        if prompt_batch_size != batch_size:
                            raise ValueError(
                                "Unexpected pattern: batch sizes of all past_valid_{key|value}_prompt tensors should be same."
                            )
                    beam_width = 1
            else:
                batch_size = input_ids_batch_size
                beam_width = 1

            if len(index_tensor_shape) == 1:
                # Index tensor is in shape (batch_size * kv_cache_length_per_batch).
                assert index_tensor_shape[0] % batch_size == 0
                kv_cache_length_per_batch = index_tensor_shape[0] // batch_size
            elif len(index_tensor_shape) == 2:
                # In this case, index tensor is in shape (batch_size, kv_cache_length_per_batch)
                kv_cache_length_per_batch = index_tensor_shape[1]

                # Sparse select cannot handle 2d index tensor. So insert reshape nodes before and after the sparse index node.
                with graph.inserting_after(index_tensor_node):
                    before_reshape_node = graph.call_function(
                        torch.ops.aten.reshape.default,
                        args=(
                            index_tensor_node,
                            (-1,),
                        ),
                    )

                # Update node metadata
                val = index_tensor_node.meta["val"].reshape(-1)
                before_reshape_node.meta["val"] = val
                before_reshape_node.meta["tensor_meta"] = _extract_tensor_metadata(val)

                # Update index node's args.
                node.args = (node.args[0], [before_reshape_node], *node.args[2:])

                target_shape = tuple(node.meta["tensor_meta"].shape)
                with graph.inserting_after(node):
                    after_reshape_node = graph.call_function(
                        torch.ops.aten.reshape.default,
                        args=(node, target_shape),
                    )
                node.replace_all_uses_with(after_reshape_node, propagate_meta=True)
                # Update arg again because first arg (`node`) was also replaced.
                after_reshape_node.args = (node, *after_reshape_node.args[1:])

                # update index node's metadata
                node.meta["val"] = node.meta["val"].reshape(target_shape)
                node.meta["tensor_meta"] = _extract_tensor_metadata(node.meta["val"])
            else:
                raise ValueError(
                    f"Index tensor should be 1d or 2d, but its {len(index_tensor_shape)}d."
                )

            # change node target and args to furiosa.sparse_select
            assert len(node.args) == 2
            if sparse_select_version == "v1.0":
                node.target = torch.ops.furiosa.sparse_select.default
                node.args = (*node.args, dummy_index, kv_cache_length_per_batch)
            elif sparse_select_version == "v1.5":
                node.target = torch.ops.furiosa.sparse_select_v1_5.default
                node.args = (
                    *node.args,
                    dummy_index,
                    kv_cache_length_per_batch,
                    beam_width,
                )
            else:
                raise ValueError(f"Invalid sparse_select_version: {sparse_select_version}")


class OpInfo(NamedTuple):
    target: torch._ops.OpOverload
    args: Sequence


def append_op_to_the_graph(graph: Graph, op_info: OpInfo, target_node: Node) -> None:
    with graph.inserting_after(target_node):
        new_node = graph.call_function(op_info.target, (target_node, *op_info.args))

    original_output_tensor_meta = target_node.meta["tensor_meta"]
    assert isinstance(original_output_tensor_meta, TensorMetadata)

    res = op_info.target(target_node.meta["val"], *op_info.args)
    tensor_meta = _extract_tensor_metadata(res)

    new_node.meta["tensor_meta"] = tensor_meta
    new_node.meta["val"] = res

    target_node.replace_all_uses_with(new_node)

    # `replace_all_uses_with` also replace target_node in new_node's args. So revert it.
    new_node.args = (target_node, *op_info.args)


def remove_output(graph: Graph, eliminate_dead_code: bool = False) -> None:
    output_node = next(iter(reversed(graph.nodes)))
    assert output_node.op == "output"
    # It's convention to make output_node.args tuple containing single tuple containing nodes to be output.
    output_node.args = ((),)
    assert not output_node.kwargs

    if has_original_name(output_node):
        set_original_name(output_node, ())

    if eliminate_dead_code:
        torch_ext.eliminate_dead_code(graph)
