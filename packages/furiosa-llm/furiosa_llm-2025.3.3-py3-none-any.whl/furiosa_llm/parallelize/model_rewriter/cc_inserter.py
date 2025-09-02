from typing import Sequence

from torch.fx import Node
from torch.fx.graph import Graph

from furiosa_llm.parallelize.model_rewriter.replicator import CCOutputPlaceholderNode


def insert_cc_at(
    global_graph: Graph,
    cc_subgraph: Graph,
    input_nodes: Sequence[Node],
    output_nodes: Sequence[Node],
    cc_output_placeholder_node: CCOutputPlaceholderNode,
):
    """Insert ``cc_subgraph`` between ``input_nodes`` and ``output_nodes`` in ``global_graph``.

    Inserted cc_subgraph will have ``input_nodes` as inputs and ``output_nodes`` as outputs.

    Args:
        global_graph: The graph to insert ``cc_subgraph`` into.
        cc_subgraph: The graph to insert into ``global_graph``.
        input_nodes: The nodes that will be parent (input) of inserted ``cc_subgraph``.
        output_nodes: The nodes that will be child (receiving output) of inserted ``cc_subgraph``
        cc_output_placeholder_node: The node to mark position in output nodes' args that should be replaced with inserted cc_subgraph's output.
    """
    # Find the first appearing output node in FX graph, so that all `cc_subgraph` nodes can be placed before that.
    output_node_set = set(output_nodes)
    first_output_node = None
    for node in global_graph.nodes:
        if node in output_node_set:
            first_output_node = node
            break
    else:
        assert False, "global_graph doesn't contain any output_nodes"
    subg_placeholders = tuple(node for node in cc_subgraph.nodes if node.op == "placeholder")

    assert len(subg_placeholders) == len(input_nodes)

    # Prepare replace map for ``Graph.graph_copy``, which maps ``input_nodes`` to placeholder nodes in cc_subgraph.
    replace_map = {
        subg_placeholder: input_node
        for subg_placeholder, input_node in zip(subg_placeholders, input_nodes)
    }

    # insert cc_subgraph into global graph, before first_output_node to maintain topological order.
    with global_graph.inserting_before(first_output_node):
        # Insert cc_subgraph to global graph and get output nodes of inserted cc_subgraph.
        # Now ``cc_subgraph`` is inserted into global graph and it's connected to `input_nodes`.
        # NOTE: returned ``cc_output_nodes`` are output nodes of inserted ``cc_subgraph``.
        # For more details, refer to ``torch.fx.Graph.graph_copy``.
        cc_output_nodes = global_graph.graph_copy(cc_subgraph, replace_map)
        assert isinstance(cc_output_nodes, tuple)

        assert (
            len(cc_output_nodes) == len(output_nodes) or output_nodes[0].op == "output"
        ), f"num output args from cc subgraph: {len(cc_output_nodes)}, num_output_nodes expected: {len(output_nodes)}"

        # Connect inserted ``cc_subgraph`` to `output_nodes`.
        if first_output_node.op == "output":
            # Inserted ``cc_subgraph`` should have output op node as its child.
            # Output op node is special because there should be only one output op node in FX graph.
            # So, all cc_subgraph's output nodes should be connected to single output op node.

            # Replicated output arguments should be consecutive, and replicas' order should be same as mesh.get_all_devices().
            # Find the first and last replicated argument and replace them.
            cur_output_args = first_output_node.args[0]
            assert isinstance(cur_output_args, tuple)
            assert len(output_nodes) == 1

            start_idx = None
            end_idx = None
            for i, arg in enumerate(cur_output_args):
                assert isinstance(arg, Node)
                if arg == input_nodes[0]:
                    assert (
                        start_idx is None
                    ), "Output's args does not starts with first replicated input node."
                    start_idx = i
                    # Fall through, as start_idx and end_idx may coincide
                if arg == input_nodes[-1]:
                    assert (
                        start_idx is not None
                    ), "Output's args does not ends with last replicated input node."
                    end_idx = i
                    break
            assert (
                start_idx is not None and end_idx is not None
            ), "Failed to match replicated nodes in CC insertion."
            assert end_idx - start_idx == len(input_nodes) - 1

            first_output_node.args = (
                (cur_output_args[:start_idx] + cc_output_nodes + cur_output_args[end_idx + 1 :]),
            )
        else:
            # If first_output_node is not an output op node, all ``output_node``s should not be an output op, because all `output_node`s are replica of same node.
            # Each pair of ``output_node`` and ``cc_output_node`` should be allocated to same device, and all we should do is just to connect each pair in global graph.
            assert len(output_nodes) == len(cc_output_nodes)

            # ASSUME: all placeholder args to be replaced with ``cc_output_nodes`` are represented as ``CCOutputPlaceholderNode``.
            for output_node, output_arg in zip(output_nodes, cc_output_nodes):
                # replace all ``cc_output_placeholder_node`` with ``output_arg``
                # in ``output_node``'s args.
                output_node.replace_input_with(cc_output_placeholder_node, output_arg)
