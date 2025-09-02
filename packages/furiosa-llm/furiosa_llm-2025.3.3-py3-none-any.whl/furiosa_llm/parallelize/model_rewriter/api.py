from collections import defaultdict
from itertools import chain
from typing import Dict, Sequence, Set

from furiosa_torch_ext.torch_ext import eliminate_dead_code
import torch
from torch.fx import Graph, GraphModule
from torch.fx.passes.fake_tensor_prop import FakeTensorProp
from torch.fx.passes.shape_prop import ShapeProp

import furiosa_llm.parallelize.mppp.config as mpc
from furiosa_llm.parallelize.node_meta import get_spec
from furiosa_llm.parallelize.utils import get_fake_mode
from furiosa_llm.parallelize.visualize import draw_graph

from .cc_calculator import CCCalculator
from .cc_inserter import insert_cc_at
from .mppp_config import DeviceId, MpppConfig, ShardSpec
from .ops.utils import is_multi_dev_comm_op
from .replicator import replicate_nodes
from .sharding_prop import ShardingPropagator


def _merge_comm_nodes(graph: Graph) -> None:
    """Merge communication nodes that have the same parent, group and op kind."""
    node_to_idx = {node: i for i, node in enumerate(graph.nodes)}

    for node in graph.nodes:
        comm_op_per_group = defaultdict(list)
        for user in sorted(node.users, key=lambda x: node_to_idx[x]):
            if not is_multi_dev_comm_op(user):
                continue
            comm_op_per_group[(tuple(user.target.group.to_list()), user.__class__.__name__)].append(
                user
            )

        for _, comm_ops in comm_op_per_group.items():
            if len(comm_ops) < 2:
                continue
            # merge communication ops.
            # only retain first one and replace others with first one.
            for comm_op in comm_ops[1:]:
                comm_op.replace_all_uses_with(comm_ops[0])
                graph.erase_node(comm_op)
    graph.lint()


# Globally one FxGraphParallelizer across devices.
class ModelRewriter:
    model: GraphModule
    mppp_config: MpppConfig
    cc_calculator: CCCalculator

    def __init__(self, model: GraphModule, mppp_config: mpc.MpppConfig):
        self.model = model
        self.mppp_config = MpppConfig.from_exportable_type(mppp_config)

        ModelRewriter.__check_mppp_config(model, self.mppp_config)

        self.cc_calculator = CCCalculator(self.mppp_config.devices)

    @staticmethod
    def __check_mppp_config(gm: GraphModule, mppp_config: MpppConfig):
        # check all node names in ``mppp_config`` actually exist in ``gm``.
        nodes_in_fx_graph = set(node.name for node in gm.graph.nodes)
        all_nodes_in_mppp_config: Set[str] = set(
            (
                *mppp_config.static_tensors.keys(),
                *chain(*map(lambda spec: (spec.src, spec.dst), mppp_config.dynamic_tensors)),
            )
        )
        if not all_nodes_in_mppp_config.issubset(nodes_in_fx_graph):
            raise ValueError(
                "Nodes in mppp_config are not subset of nodes in the given graph:"
                f"{all_nodes_in_mppp_config - nodes_in_fx_graph}"
            )

    def get_device_id_map(self) -> Dict[DeviceId, mpc.DeviceId]:
        return self.mppp_config.device_id_map

    def rewrite(self, example_inputs: Sequence) -> GraphModule:
        """
        Rewrite the given model to be parallelized across the devices.
        """
        graph: Graph = self.model.graph

        # Stage 0: Generate tensor_meta info for nodes in the graph if not exist. This is needed for sharding propagation.
        if any("tensor_meta" not in node.meta for node in graph.nodes if node.op != "output"):
            # Stage 0: Prepare tensor_meta info for the Sharding Propagater.
            fake_mode = get_fake_mode(chain(self.model.parameters(), self.model.buffers()))
            fake_mode.allow_non_fake_inputs = True
            fake_example_inputs = [
                fake_mode.from_tensor(t) if isinstance(t, torch.Tensor) else t
                for t in example_inputs
            ]
            ShapeProp(self.model).propagate(*fake_example_inputs)
            FakeTensorProp(self.model, mode=fake_mode).propagate(*fake_example_inputs)
        draw_graph(self.model, "stage0")

        # Stage 1: Propagate tensor sharding & mesh information
        ShardingPropagator(self.model, self.mppp_config).propagate()
        draw_graph(self.model, "stage1")

        # Stage 2: Replicate nodes and get needed cc graphs per edges
        node_name_to_node = {node.name: node for node in graph.nodes}
        cc_graphs_per_edge = {}

        # replicate nodes
        replicated_gm, original_node_to_replicates = replicate_nodes(
            self.model,
            tuple((dspec.src, dspec.dst) for dspec in self.mppp_config.dynamic_tensors),
            self.mppp_config.devices,
        )

        # get needed cc graphs per edges
        for from_node, to_node, dst_spec in self.mppp_config.dynamic_tensors:
            from_spec = get_spec(node_name_to_node[from_node])
            assert isinstance(from_spec, ShardSpec)
            assert isinstance(dst_spec, ShardSpec)
            cc_graphs_per_edge[(from_node, to_node)] = self.cc_calculator.get_needed_cc_graph(
                from_spec, dst_spec
            )

        draw_graph(replicated_gm, "stage2")

        # Stage 3: Insert cc operations to replicated gm
        for (src, dst), cc_graphs in cc_graphs_per_edge.items():
            input_nodes, cc_output_placeholder_node = original_node_to_replicates[
                node_name_to_node[src]
            ]
            output_nodes, _ = original_node_to_replicates[node_name_to_node[dst]]

            insert_cc_at(
                replicated_gm.graph,
                cc_graphs,
                input_nodes,
                output_nodes,
                cc_output_placeholder_node,
            )
        _merge_comm_nodes(replicated_gm.graph)

        eliminate_dead_code(replicated_gm.graph)
        replicated_gm.recompile()

        draw_graph(replicated_gm, "stage3")

        return replicated_gm
