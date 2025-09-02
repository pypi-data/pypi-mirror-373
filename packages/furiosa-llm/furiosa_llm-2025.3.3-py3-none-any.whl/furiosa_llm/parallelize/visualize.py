import os
from typing import Dict, Iterable, Optional

import torch
import torch.fx
from torch.fx.node import _format_arg
from torch.fx.passes.graph_drawer import FxGraphDrawer
from torch.fx.passes.shape_prop import TensorMetadata

import furiosa_llm.parallelize.model_rewriter.mppp_config as mrw
from furiosa_llm.parallelize.model_rewriter.ops.types import SingleDeviceCommOp
from furiosa_llm.parallelize.model_rewriter.ops.utils import (
    is_multi_dev_comm_op,
    is_single_dev_comm_op,
)
from furiosa_llm.parallelize.mppp.config import MpppConfig
from furiosa_llm.parallelize.node_meta import get_color

COLORS_PER_DEV_ID = ["#E84D8A", "#7F58AF", "#64C5EB", "#FEB326"]
COMM_OP_COLOR = "#FCA311"


def escape_curly_braces(text):
    if not text:
        return ''
    result = ''
    escaped = False
    for char in text:
        if char == '\\':
            result += '\\'
            escaped = not escaped
        elif char == '{' or char == '}':
            if not escaped:
                result += '\\' + char
            else:
                result += char
        else:
            result += char
        if char != '\\':
            escaped = False
    return result


class FuriosaFXGDrawer(FxGraphDrawer):
    def _get_node_label(
        self,
        module: torch.fx.GraphModule,
        node: torch.fx.Node,
        skip_node_names_in_args: bool,
        # For torch 2.2.+ compatibility
        parse_stack_trace: Optional[bool] = None,
    ) -> str:
        def _get_str_for_args_kwargs(arg):
            if isinstance(arg, tuple):
                prefix, suffix = r"|args=(\l", r",\n)\l"
                arg_strs_list = [_format_arg(a, max_list_len=8) for a in arg]
            elif isinstance(arg, dict):
                prefix, suffix = r"|kwargs={\l", r",\n}\l"
                arg_strs_list = [f"{k}: {_format_arg(v, max_list_len=8)}" for k, v in arg.items()]
            else:  # Fall back to nothing in unexpected case.
                return ""

            # Strip out node names if requested.
            if skip_node_names_in_args:
                arg_strs_list = [a for a in arg_strs_list if "%" not in a]
            if len(arg_strs_list) == 0:
                return ""
            arg_strs = prefix + r",\n".join(arg_strs_list) + suffix
            if len(arg_strs_list) == 1:
                arg_strs = arg_strs.replace(r"\l", "").replace(r"\n", "").replace("->", "-\\>")
            return escape_curly_braces(arg_strs)

        label = "{" + f"name=%{node.name}|op_code={node.op}\n"

        if original_name := node.meta.get("original_name"):
            label += f"|original_name={original_name}\n"

        if p := node.meta.get("spec"):
            if not isinstance(p, Iterable):
                p = (p,)
            for id, pp in enumerate(p):
                if not isinstance(pp, mrw.ShardSpec):
                    raw_spec_str = escape_curly_braces(str(pp))
                    label += f"|spec_raw_{id}={raw_spec_str}\n"
                else:
                    label += f"|placements_{id}={pp.placements}\n"
                    label += f"|mesh_{id}={pp.mesh}\n"

        if node.op == "call_module":
            leaf_module = self._get_leaf_node(module, node)
            label += r"\n" + self._typename(leaf_module) + r"\n|"
            extra = ""
            if hasattr(leaf_module, "__constants__"):
                extra = r"\n".join(
                    [f"{c}: {getattr(leaf_module, c)}" for c in leaf_module.__constants__]  # type: ignore[union-attr]
                )
            label += extra + r"\n"
        else:
            label += f"|target={self._typename(node.target)}" + r"\n"
            if len(node.args) > 0:
                label += _get_str_for_args_kwargs(node.args)
            if len(node.kwargs) > 0:
                label += _get_str_for_args_kwargs(node.kwargs)
            # label += f"|num_users={len(node.users)}" + r"\n"

        tensor_meta = node.meta.get("tensor_meta")
        label += self._tensor_meta_to_label(tensor_meta)

        # for original fx graph
        # print buf=buf0, n_origin=6
        buf_meta = node.meta.get("buf_meta", None)
        if buf_meta is not None:
            label += f"|buf={buf_meta.name}" + r"\n"
            label += f"|n_origin={buf_meta.n_origin}" + r"\n"

        device_id = node.meta.get("device_id", None)
        if device_id is not None:
            label += f"|device={device_id}" + r"\n"

        if isinstance(node.target, SingleDeviceCommOp):
            label += f"|comm_group_id={node.target.group.id}" + r"\n"
            for k, v in node.target.metadata().items():
                label += f"|{k}={v}" + r"\n"

        color = get_color(node)
        if color is not None:
            label += "|color={}}}".format(color)

        if node.op == "output":
            label += f"|args={node.args[0]}" + r"\n"

        # TODO: visualize prop_error message nicely
        # if prop_error_msg := node.meta.get("prop_error_msg"):
        #     label += f"|prop_error_msg=\n{escape_curly_braces(prop_error_msg)}" + r"\n"

        return label + "}"

    def _stringify_tensor_meta(self, tm: TensorMetadata) -> str:
        result = ""
        if not hasattr(tm, "dtype"):
            print("tm", tm)
        result += "|" + "dtype" + "=" + str(tm.dtype) + r"\n"
        result += "|" + "shape" + "=" + str(tuple(tm.shape)) + r"\n"
        result += "|" + "requires_grad" + "=" + str(tm.requires_grad) + r"\n"
        # Who cares about stride?
        # result += "|" + "stride" + "=" + str(tm.stride) + r"\n"
        if tm.is_quantized:
            assert tm.qparams is not None
            assert "qscheme" in tm.qparams
            qscheme = tm.qparams["qscheme"]
            if qscheme in {
                torch.per_tensor_affine,
                torch.per_tensor_symmetric,
            }:
                result += "|" + "q_scale" + "=" + str(tm.qparams["scale"]) + r"\n"
                result += "|" + "q_zero_point" + "=" + str(tm.qparams["zero_point"]) + r"\n"
            elif qscheme in {
                torch.per_channel_affine,
                torch.per_channel_symmetric,
                torch.per_channel_affine_float_qparams,
            }:
                result += "|" + "q_per_channel_scale" + "=" + str(tm.qparams["scale"]) + r"\n"
                result += (
                    "|" + "q_per_channel_zero_point" + "=" + str(tm.qparams["zero_point"]) + r"\n"
                )
                result += "|" + "q_per_channel_axis" + "=" + str(tm.qparams["axis"]) + r"\n"
            else:
                raise RuntimeError(f"Unsupported qscheme: {qscheme}")
            result += "|" + "qscheme" + "=" + str(tm.qparams["qscheme"]) + r"\n"
        return result

    def _get_node_style(self, node: torch.fx.Node) -> Dict[str, str]:
        template = super()._get_node_style(node)
        # Something went wrong during shape propagation
        if node.meta.get("prop_error_msg"):
            template["fillcolor"] = "black"
            template["fontcolor"] = "white"
            template["penwidth"] = "4"
            template["color"] = "red"
            template["style"] = "filled"
        elif is_multi_dev_comm_op(node) or is_single_dev_comm_op(node):
            template["fillcolor"] = "#FCA311"
            template["fontcolor"] = "black"
            template["penwidth"] = "4"
        elif "device_id" in node.meta:
            dev_id = node.meta["device_id"]
            if isinstance(dev_id, int):
                template["fillcolor"] = COLORS_PER_DEV_ID[dev_id]
                template["fontcolor"] = "black"
                template["penwidth"] = "4"
        return template


class ColorGetter:
    """Emit a fresh new color for new seen number, otherwise return the same color."""

    COLORS = [
        "skyblue",
        "red",
        "green",
        "yellow",
        "purple",
        "orange",
        "pink",
        "brown",
        "cyan",
        "magenta",
        "lime",
        "teal",
        "lavender",
        "tan",
        "salmon",
        "gold",
        "lightblue",
        "lightgreen",
        "lightyellow",
        "indianred4",
        "lightpink",
        "lightcyan",
        "lemonchiffon",
        "maroon",
        "lightsalmon",
        "olive",
        "sienna",
        "tomato",
        "wheat",
        "webmaroon",
    ]

    def __init__(self):
        self.seen = []

    def __call__(self, x):
        if x not in self.seen:
            self.seen.append(x)
        return self.COLORS[self.seen.index(x)]


class ColoredDrawer(FuriosaFXGDrawer):
    color_getter = ColorGetter()

    def _get_node_style(self, node: torch.fx.Node) -> Dict[str, str]:
        template = super()._get_node_style(node)
        color = get_color(node)
        if color is not None:
            template["fillcolor"] = self.color_getter(color)
            template["penwidth"] = "3"
        return template


def draw_graph(
    gm, name: str = "", mppp_config: Optional[MpppConfig] = None, visualize_color_info: bool = False
):
    """
    Draw the given graph and save it to a file if DUMP_SVG_TO environment variable is set.
    """
    from time import localtime, strftime

    save_dir = os.environ.get("DUMP_SVG_TO", None)
    if save_dir is None:
        return

    os.makedirs(save_dir, exist_ok=True)
    name += f'_{strftime("%H%M%S", localtime())}'
    svg_path = os.path.join(save_dir, f"{name}.svg")

    if visualize_color_info:
        drawer: FuriosaFXGDrawer = ColoredDrawer(gm, name)
    else:
        drawer = FuriosaFXGDrawer(gm, name)
    dot = drawer.get_dot_graph()

    if mppp_config is None:
        dot.write_svg(svg_path)
        return

    for static_id in mppp_config.static_tensors.keys():
        n = dot.get_node(static_id)
        if not n:
            continue
        n = n[0]
        n.set_color("blue")
        n.set_penwidth("3")
        n.set_style("filled, diagonals")
    dynamic_tensors = {(dspec.src, dspec.dst): dspec.spec for dspec in mppp_config.dynamic_tensors}

    for (src, dst), spec in dynamic_tensors.items():
        e = dot.get_edge(src, dst)
        if len(e) != 1:
            print(RuntimeError(f"Edge {src} -> {dst} not found"))
            continue
        e = e[0]
        e.set_label(spec._to_brief_str())
        e.set_color("blue")
        e.set_penwidth("3")
    dot.write_svg(svg_path)
