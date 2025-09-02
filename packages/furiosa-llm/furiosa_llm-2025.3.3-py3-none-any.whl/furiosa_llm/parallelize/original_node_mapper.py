from itertools import chain
import logging
import operator
from typing import Dict, Optional, Sequence, Tuple

import torch
from torch._dynamo.source import AttrSource, GetItemSource, GlobalSource, LocalSource
from torch._guards import Source
from torch.fx import GraphModule, Node

from furiosa_llm.parallelize.node_meta import (
    ConstantKind,
    QParamKind,
    has_original_name,
    set_constant_kind,
    set_original_name,
    set_qparam_kind,
)
from furiosa_llm.parallelize.utils import recursive_getattr

# attribute names of the  that contain qparams.
_QPARAM_SCALE_ATTRS = ["scale", "weight_scale", "input1_scale"]
_QPARAM_ZEROPOINT_ATTRS = ["zero_point"]

KWARGS_NAME = "kwargs"
ARGS_NAME = "args"


def _get_input_name_from_dynamo_source(source: Source) -> str:
    if isinstance(source, GetItemSource):
        prefix = _get_input_name_from_dynamo_source(source.base)
        return source.index if prefix == "" else f"{prefix}_{source.index}"
    elif isinstance(source, LocalSource):
        # We don't want to include "kwargs" in tensor name. If certain argument is a value in kwargs,
        # its key becomes name.
        # TODO: find more robust way. This can be broken easily.
        return "" if source.local_name == KWARGS_NAME else f"{source.local_name}"
    elif isinstance(source, AttrSource):
        base = _get_input_name_from_dynamo_source(source.base)
        return f"{base}_{source.member}"
    elif isinstance(source, GlobalSource):
        return source.name()
    else:
        raise NotImplementedError(f"Unsupported source type: {source}")


def _add_input_original_name_info_from_original_gm(
    original_gm: GraphModule, transformed_gm: GraphModule
):
    original_placeholder_names = tuple(
        _get_input_name_from_dynamo_source(node._dynamo_source)
        for node in original_gm.graph.nodes
        if node.op == "placeholder"
    )
    new_placeholders = tuple(
        node for node in transformed_gm.graph.nodes if node.op == "placeholder"
    )
    assert len(original_placeholder_names) == len(new_placeholders)

    # save info
    for original_name, new_node in zip(original_placeholder_names, new_placeholders):
        set_original_name(new_node, original_name)


def _add_output_original_name_info_from_original_gm(
    original_gm: GraphModule, transformed_gm: GraphModule
):
    def _get_output_node(graph):
        output_node = tuple(graph.nodes)[-1]
        assert output_node.op == "output"

        return output_node

    original_output_node = _get_output_node(original_gm.graph)
    new_output_node = _get_output_node(transformed_gm.graph)

    original_output_node_args = original_output_node.args[0]
    new_output_node_args = new_output_node.args[0]

    assert len(original_output_node_args) == len(new_output_node_args)
    assert all(
        isinstance(output, Node)
        for output in chain(original_output_node_args, new_output_node_args)
    )

    # match output nodes
    set_original_name(new_output_node, tuple(node.name for node in original_output_node_args))


def _is_zero_point_for_dpe(node: Node):
    # TODO: This method might not be robust when failed to get original name for model's original parameter. Find a better way.
    return (
        not has_original_name(node)
        and len(node.users) == 1
        and tuple(node.users.keys())[0].op == "call_function"
        and tuple(node.users.keys())[0].target == torch.ops.furiosa.type_emulation_in.default
    )


def add_qparam_info(original_model: torch.nn.Module, transformed_gm: GraphModule):
    """Add qparam-related information for get_attr which are qparam tensors in ``transformed_gm``."""
    # Store original name info for qparams.
    qparam_mapping = {}

    try:
        for name, module in original_model.named_modules():
            for attr in _QPARAM_SCALE_ATTRS:
                if hasattr(module, attr):
                    qparam_mapping[getattr(module, attr)] = (f"{name}_{attr}", False)
            for attr in _QPARAM_ZEROPOINT_ATTRS:
                if hasattr(module, attr):
                    qparam_mapping[getattr(module, attr)] = (f"{name}_{attr}", True)
    except Exception:
        pass

    # NOTE (IMPORTANT): With this kind of matching based on tensor's, We cannot find mapping for scalar tensors.
    # Buf this is sufficient now because scalar tensor constant nodes will always be embedded in GraphModule as constants.
    for node in transformed_gm.graph.nodes:
        if node.op != "get_attr":
            continue
        actual_tensor = recursive_getattr(transformed_gm, node.target)
        qparam_name, is_zero_point = qparam_mapping.get(actual_tensor, (None, None))
        if qparam_name is None:
            continue

        # Order matters. Qparam kind must be determined before setting original name.
        if is_zero_point:
            if _is_zero_point_for_dpe(node):
                qparam_kind = QParamKind.ZERO_POINT_FOR_DPE
            else:
                qparam_kind = QParamKind.ZERO_POINT
        else:
            qparam_kind = QParamKind.SCALE

        set_original_name(node, qparam_name)

        set_qparam_kind(node, qparam_kind)


def add_param_buffer_original_name_info(
    original_model: torch.nn.Module, transformed_gm: GraphModule
):
    """Add original name information for parameter/buffer nodes in ``transformed_gm`` that corresponds to parameter/buffer in ``original_model.state_dict()``.

    Original name information will be in node.meta["original_name"].
    """

    # To ensure duplicates are eliminated in deterministic way.
    original_model_constants = list(
        chain(
            original_model.named_buffers(remove_duplicate=False),
            original_model.named_parameters(remove_duplicate=False),
        )
    )
    original_model_constants.sort(
        key=operator.itemgetter(0),
    )

    # make mapping FakeTensor to buffer name
    # we only cares about tensors in ``original_model.buffers() or parameters()``.
    reversed_origin_state_dict = {tensor: key for key, tensor in original_model_constants}

    # parameter/buffer in transformed gm  -> (original name in original model's state_dict, whether it's weight parameter)
    name_mappings: Dict[str, Tuple[str, bool]] = {}

    for key, fake_t in chain(transformed_gm.named_parameters(), transformed_gm.named_buffers()):
        if fake_t not in reversed_origin_state_dict:
            continue
        original_param_name = reversed_origin_state_dict[fake_t]
        name_mappings[key] = (original_param_name, isinstance(fake_t, torch.nn.Parameter))
        del reversed_origin_state_dict[fake_t]

    unmapped_non_scalar_constants = tuple(
        name for tensor, name in reversed_origin_state_dict.items() if len(tensor.size()) > 0
    )

    if len(unmapped_non_scalar_constants) > 0:
        logging.warning(
            f"{len(unmapped_non_scalar_constants)} non-scalar constants in parameter saved file are not mapped: {unmapped_non_scalar_constants}"
        )

    # Store original name info in nodes.
    for node in transformed_gm.graph.nodes:
        if node.op != "get_attr":
            continue
        if original_info := name_mappings.get(node.target):
            original_name, is_weight = original_info
            if is_weight:
                set_constant_kind(node, ConstantKind.WEIGHT)
            else:
                set_constant_kind(node, ConstantKind.BUFFER)
            set_original_name(node, original_name)
        else:
            set_constant_kind(node, ConstantKind.OTHERS)


def set_original_name_info_for_inputs(
    gm: GraphModule,
    input_names: Sequence[str],
) -> None:
    """Set original name information for placeholder nodes in ``gm``."""

    placeholder_nodes = tuple(node for node in gm.graph.nodes if node.op == "placeholder")
    if len(input_names) != len(placeholder_nodes):
        raise ValueError(
            "Given number of input names does not match with number of placeholders in FX graph."
        )

    for node, name in zip(placeholder_nodes, input_names):
        set_original_name(node, name)


def set_original_name_info_for_outputs(
    gm: GraphModule,
    output_names: Sequence[str],
) -> None:
    """Set original name information for output node in ``gm``."""

    output_node = tuple(gm.graph.nodes)[-1]
    if len(output_node.args[0]) != len(output_names):
        raise ValueError(
            "Given number of output names does not match with number of outputs in FX graph."
        )
    set_original_name(output_node, tuple(output_names))


def add_original_name_info(
    original_model: torch.nn.Module,
    original_gm: GraphModule,
    transformed_gm: GraphModule,
    input_names: Optional[Sequence[str]] = None,
    output_names: Optional[Sequence[str]] = None,
):
    """Add original name information for all placeholder, output nodes and some of get_attr nodes in ``transformed_gm``.

    Original names for parameters/buffers will be obtained from ``original_model`` and input/output's original names
    will be obtained from ``original_gm``.
    """
    if input_names:
        set_original_name_info_for_inputs(transformed_gm, input_names)
    else:
        _add_input_original_name_info_from_original_gm(original_gm, transformed_gm)

    add_param_buffer_original_name_info(original_model, transformed_gm)
    if output_names:
        set_original_name_info_for_outputs(transformed_gm, output_names)
    else:
        _add_output_original_name_info_from_original_gm(original_gm, transformed_gm)
