from abc import ABC, abstractmethod
import copy
import os
from typing import Any, Mapping, Optional, Sequence, Union

import torch
from torch.fx import GraphModule
from transformers import PretrainedConfig

from furiosa_llm.parallelize.block_slicer import (
    ModuleMarkConfig,
    get_block_slicing_edges,
    get_blockwise_sliced_color_map,
    is_marker_op,
    remove_marker_nodes,
)
from furiosa_llm.parallelize.model_creation_info import ModelCreationInfo
from furiosa_llm.parallelize.mppp.config import (
    Device,
    DeviceId,
    DeviceMesh,
    DynamicTensorSpec,
    MpppConfig,
    Replicate,
    ShardSpec,
)
from furiosa_llm.parallelize.trace import get_aten_graph_with_metadata
from furiosa_llm.parallelize.utils import (
    gen_mppp_config_with_no_parallelism,
    get_original_model_type,
)


class Mppp(ABC):

    @abstractmethod
    def gen_config(
        self,
        model: Union[torch.nn.Module, ModelCreationInfo],
        # TODO: remove model_config parameter
        model_config: PretrainedConfig,
        devices: Sequence[Device],
        example_args: Sequence[Any],
        example_kwargs: Mapping[str, Any],
        graph_module: Optional[GraphModule] = None,
        other_configs: Mapping[str, Any] = {},
    ) -> MpppConfig:
        raise NotImplementedError("Mppp Should implement gen_config method")


class DefaultMppp(Mppp):
    def __init__(self) -> None: ...

    def gen_config(
        self,
        model: Union[torch.nn.Module, ModelCreationInfo],
        # TODO: remove model_config parameter
        model_config: PretrainedConfig,
        devices: Sequence[Device],
        example_args: Sequence[Any],
        example_kwargs: Mapping[str, Any],
        graph_module: Optional[GraphModule] = None,
        other_configs: Mapping[str, Any] = {},
    ) -> MpppConfig:
        # FIXME: remove monkey patch and replace this with general strategy finding logic.
        raise NotImplementedError(f"Mppp doesn't support {model.__class__} model yet")


def gen_pp_mpc(
    model: Union[torch.nn.Module, ModelCreationInfo],
    devices: Sequence[Device],
    args: Sequence[Any],
    kwargs: Mapping[str, Any],
    graph_module: Optional[GraphModule] = None,
    num_blocks_per_devices: Optional[Sequence[int]] = None,
    use_marker_based_block_slicer: bool = False,
    cache_dir: Optional[os.PathLike] = None,
) -> MpppConfig:
    """Generate Pipeline Parallelism Mppp Config for ``model``, running with ``devices``."""
    if graph_module is None:
        if use_marker_based_block_slicer:
            module_mark_config = ModuleMarkConfig(include_submodules_in_modulelists=True)
        else:
            module_mark_config = None
        gm, _ = get_aten_graph_with_metadata(
            model, args, kwargs, cache_dir=cache_dir, module_mark_config=module_mark_config
        )
    else:
        if use_marker_based_block_slicer and not any(
            is_marker_op(node) for node in graph_module.graph.nodes
        ):
            raise ValueError(
                "To use marker based block slicer, `graph_module` should have marker nodes."
            )
        gm = GraphModule(graph_module, copy.deepcopy(graph_module.graph))

    if isinstance(model, torch.nn.Module):
        original_model_type = get_original_model_type(model)
    else:
        original_model_type = model.metadata.get_optimized_cls()

    if len(devices) == 1:
        # No parallelism
        return gen_mppp_config_with_no_parallelism(f"{original_model_type}-no-pp", gm, devices[0])

    n_layer = model.metadata.config.num_hidden_layers

    if use_marker_based_block_slicer:
        block_idx_map, _ = get_blockwise_sliced_color_map(
            gm, method="marker", mark_color_to_meta=False
        )

        # To create mppp config based on graph without marker nodes.
        remove_marker_nodes(gm)
    else:
        # When applying PP, we want to see (embedding + first transformer block) as a single block.
        split_edges = get_block_slicing_edges(gm, original_model_type, False)

        assert len(split_edges) == n_layer

        block_idx_map, _ = get_blockwise_sliced_color_map(
            gm, method="split_by_edges", split_edges=split_edges, mark_color_to_meta=False
        )
    block_idx_to_pp_stage_idx = {}

    if num_blocks_per_devices is None:
        # Distribute transformer(bert) blocks to stages equally.
        pp_level = len(devices)

        if n_layer % pp_level != 0:
            raise NotImplementedError(
                "Mppp Config cannot be generated for the case when number of transformer blocks is not a multiple of pipeline parallelism level."
            )
        n_block_per_pp_stage = n_layer // pp_level

        for block_idx in range(n_layer):
            block_idx_to_pp_stage_idx[block_idx] = block_idx // n_block_per_pp_stage
    else:
        # Distribute transformer(bert) blocks according to `num_blocks_per_devices`.
        if sum(num_blocks_per_devices) != n_layer:
            raise ValueError(
                "Sum of elements in `num_blocks_per_devices` is not same as number of layers of the model."
            )

        cur_block_idx = 0
        for stage_idx, num_blocks in enumerate(num_blocks_per_devices):
            for _ in range(num_blocks):
                block_idx_to_pp_stage_idx[cur_block_idx] = stage_idx
                cur_block_idx += 1

    # Node name to belonging pp stages.
    pp_stage_map = {
        node_name: set(block_idx_to_pp_stage_idx[block_idx] for block_idx in block_indices)
        for node_name, block_indices in block_idx_map.items()
    }

    dynamic_tensors = []
    static_tensors = {}
    mppp_devices = {DeviceId(str(i)): device for i, device in enumerate(devices)}

    for node in gm.graph.nodes:
        if node.op == "output" or node.all_input_nodes:
            continue
        device_ids = [DeviceId(str(stage_num)) for stage_num in pp_stage_map[node.name]]
        static_tensors[node.name] = ShardSpec([Replicate()], DeviceMesh(device_ids))

    for node in gm.graph.nodes:
        if node.op == "output":
            continue
        parent_stages = pp_stage_map[node.name]
        for user in node.users:
            if user.op == "output":
                continue
            child_stages = pp_stage_map[user.name]
            # If stages are different, need repartitioning.
            if child_stages != parent_stages:
                # color is different. need repartitioning
                child_device_mesh = DeviceMesh(
                    [DeviceId(str(stage_num)) for stage_num in child_stages]
                )
                dynamic_tensors.append(
                    DynamicTensorSpec(
                        src=node.name,
                        dst=user.name,
                        spec=ShardSpec([Replicate()], child_device_mesh),
                    )
                )
    mppp_config = MpppConfig(
        f"{original_model_type}-pp{len(devices)}",
        devices=mppp_devices,
        static_tensors=static_tensors,
        dynamic_tensors=dynamic_tensors,
    )
    return mppp_config


class PipelineParallelismMppp(Mppp):
    def __init__(
        self,
        num_blocks_per_devices: Optional[Sequence[int]] = None,
    ) -> None:
        self.num_blocks_per_devices = num_blocks_per_devices

    def gen_config(
        self,
        model: Union[torch.nn.Module, ModelCreationInfo],
        _model_config: PretrainedConfig,
        devices: Sequence[Device],
        example_args: Sequence[Any],
        example_kwargs: Mapping[str, Any],
        graph_module: Optional[GraphModule] = None,
        other_configs: Mapping[str, Any] = {},
    ) -> MpppConfig:
        use_marker_based_block_slicer = other_configs.get("use_marker_based_block_slicer", False)

        return gen_pp_mpc(
            model,
            devices,
            example_args,
            example_kwargs,
            graph_module=graph_module,
            num_blocks_per_devices=self.num_blocks_per_devices,
            use_marker_based_block_slicer=use_marker_based_block_slicer,
        )
