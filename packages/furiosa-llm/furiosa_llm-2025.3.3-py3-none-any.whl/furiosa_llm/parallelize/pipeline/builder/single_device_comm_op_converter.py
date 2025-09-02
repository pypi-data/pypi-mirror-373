from collections import defaultdict
import operator
from typing import Dict, List, Set

from torch.fx import Graph, GraphModule, Node

from furiosa_llm.parallelize.model_rewriter.mppp_config import DeviceId
from furiosa_llm.parallelize.model_rewriter.ops.utils import (
    is_multi_dev_comm_op,
    is_single_dev_comm_op,
)
from furiosa_llm.parallelize.node_meta import add_tensor_meta, set_device_id


def _eliminate_dead_nodes(graph: Graph, target_ops: Set[Node]):
    # Slightly modified version of ``torch.fx.Graph.eliminate_dead_code``.

    # Lint the graph first to make sure its topologically sorted, otherwise
    # DCE below will not behave as expected.
    graph.lint()

    # Reverse iterate so that when we remove a node, any nodes used as an
    # input to that node have an updated user count that no longer reflects
    # the removed node.
    for node in reversed(graph.nodes):
        # Don't remove inserted `SingleDeviceCommOp`nodes.
        # Some `SingleDeviceCommOp`s like `Send` node has no user (child in FX graph),
        # so it will be removed if it's not excluded.
        if is_single_dev_comm_op(node):
            continue
        if not node.is_impure() and len(node.users) == 0:
            graph.erase_node(node)


def convert_to_single_device_comm_ops(gm: GraphModule):
    """convert given gm to new gm that consists of only single-device communication ops"""
    to_be_erased = set()
    graph = gm.graph

    for node in tuple(graph.nodes):
        if not is_multi_dev_comm_op(node):
            # Skip pure computation nodes.
            continue

        to_be_erased.add(node)

        # Convert comm op nodes to single-device nodes.
        input_devices = node.target.input_devices()
        output_devices = node.target.output_devices()

        assert len(input_devices) == len(node.args)

        # Nodes that actually corresponds to comm op output tensor on each device.
        # Mapping of device id to "node to be replaced with per-device comm op".
        original_comm_op_node_per_device: Dict[DeviceId, List[Node]] = defaultdict(list)

        # match node users and output devices.
        for user in node.users:
            if user.op == "call_function" and user.target == operator.getitem:
                dev_id = output_devices[user.args[1]]
                # This comm op node produces multiple output tensors across devices.
                # And that's the reason why there's getitem node.
                # So each getitem node should be replaced with corresponding per-device comm op.
                original_comm_op_node_per_device[dev_id].append(user)
            else:
                # This comm op node produces single output tensor on single device.
                # Do we need to relax this assumption?
                assert len(output_devices) == 1
                dev_id = output_devices[0]
                original_comm_op_node_per_device[dev_id].append(node)

        # new single-device op per device.
        new_nodes: Dict[DeviceId, Node] = {}

        # create per-device comm op nodes for each input tensor's device.
        for dev_id, input_node in zip(input_devices, node.args):
            with graph.inserting_after(node):
                single_dev_op = node.target.get_single_dev_op(dev_id, node.meta["tensor_meta"])
                new_node = graph.call_function(single_dev_op, args=(input_node,))
                new_nodes[dev_id] = new_node
            # Add "tensor_meta" metadata to newly created node.
            add_tensor_meta(new_node)

            set_device_id(new_node, dev_id)

        # Create single-device comm op nodes.
        for dev_id, original_comm_ops in original_comm_op_node_per_device.items():
            if dev_id in new_nodes:
                # Both input and output tensors for this comm op includes tensor on this device.
                # We've already created single-device comm op node for this device.
                new_node = new_nodes[dev_id]
            else:
                # Just output tensors for this comm op includes tensor on this device.
                # Single-device comm op node on this device was not created yet, so create it.
                with graph.inserting_after(original_comm_ops[0]):
                    single_dev_op = node.target.get_single_dev_op(dev_id, node.meta["tensor_meta"])
                    new_node = graph.call_function(single_dev_op, args=())
                # Add "tensor_meta" metadata to newly created node.
                add_tensor_meta(new_node)

                set_device_id(new_node, dev_id)

            # Replace all uses of ``original_comm_op`` with ``new_node``
            # in ``to_be_replaced.users`` to connect newly created single-device comm op node
            # to ``original_comm_op``'s users.
            for original_comm_op in original_comm_ops:
                original_comm_op.replace_all_uses_with(
                    new_node, lambda node: node in original_comm_op.users
                )

    # Remove multi-device comm ops not needed anymore.
    _eliminate_dead_nodes(graph, to_be_erased)
    gm.recompile()
