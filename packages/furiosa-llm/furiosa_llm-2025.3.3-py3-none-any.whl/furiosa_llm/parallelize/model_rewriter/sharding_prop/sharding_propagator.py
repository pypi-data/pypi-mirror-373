from itertools import chain
import logging
import operator
from typing import Any, Dict, Iterable, List, Tuple, Union, cast

import torch
from torch._ops import OpOverload
from torch.distributed._tensor.placement_types import DTensorSpec
from torch.distributed.tensor._op_schema import OpSchema as TorchOpSchema
from torch.fx import GraphModule, Node
from torch.fx.interpreter import Interpreter
from torch.utils._pytree import tree_flatten, tree_unflatten

import furiosa_llm.parallelize.model_rewriter.mppp_config as mrw
from furiosa_llm.parallelize.node_meta import get_spec, has_spec, set_spec
from furiosa_llm.utils import get_logger_with_tz

aten = torch.ops.aten
logger = get_logger_with_tz(logging.getLogger(__name__))


class OpSchema(TorchOpSchema):
    """
    This class is a wrapper around torch.distributed._tensor.op_schema.OpSchema
    to provide a clean list of args spec list consisting of either torch's ShardSpec
    or furiosa_llm's ShardSpec.
    """

    @property
    def args_spec(self) -> Tuple[Union[DTensorSpec, mrw.ShardSpec], ...]:
        """
        args_spec: Tuple[ShardSpec, ...]: contains a clean list of args spec list
            with NO non-DTensor positional arguments (i.e. int/float/tuple, etc)
            mainly used by sharding propagation to propagate the output spec
        """
        # filter out non-relevant values from args schema to get a clean spec list
        # this would mainly be used by sharding propagation rules
        return tuple(
            item for item in self.args_schema if isinstance(item, (DTensorSpec, mrw.ShardSpec))
        )


class ShardingPropagator(Interpreter):

    def __init__(
        self,
        module: GraphModule,
        mppp_config: mrw.MpppConfig,
        garbage_collect_values: bool = True,
    ):
        super().__init__(module, garbage_collect_values)
        self.static_tensors = mppp_config.static_tensors
        self.dynamic_tensors = {
            (dspec.src, dspec.dst): dspec.spec for dspec in mppp_config.dynamic_tensors
        }

        node_to_index: Dict[Node, int] = {}
        for idx, node in enumerate(self.module.graph.nodes):
            node_to_index[node] = idx
            if has_spec(node):
                raise ValueError(f"Node {node.name} already has spec before sharding propagation.")
        self.node_to_index = node_to_index

    def get_spec(self, src: Node, dst: Node) -> mrw.ShardSpec:
        """get spec of ``src``, when it's used by ``dst``."""
        if spec := self.dynamic_tensors.get((src.name, dst.name)):
            return spec
        else:
            spec_ = get_spec(src)
            assert isinstance(spec_, mrw.ShardSpec)
            return spec_

    def has_spec(self, src: Node, dst: Node) -> bool:
        """check if ``src`` has spec when it's used by ``dst``."""
        return (src.name, dst.name) in self.dynamic_tensors or has_spec(src)

    def _get_arg_schema_and_placements(
        self,
        node: Node,
        flat_args_list: List[Any],
    ) -> Tuple[
        List[Union[Any, mrw.ShardSpec]],
        List[mrw.ShardSpec],
    ]:
        flat_args_schema: List[Union[Any, mrw.ShardSpec]] = []
        placements: List[mrw.ShardSpec] = []
        for arg in flat_args_list:
            if isinstance(arg, Node):
                if not self.has_spec(arg, node):
                    raise RuntimeError(
                        f"{arg.name} node doesn't have tensor distribution spec in the graph"
                    )
                placement_spec = self.get_spec(arg, node)
                placement_spec.tensor_meta = arg.meta.get("tensor_meta")

                placements.append(placement_spec)
                flat_args_schema.append(placement_spec)
            else:
                flat_args_schema.append(arg)
        return flat_args_schema, placements

    def run_node(self, node: Node) -> Any:
        total_nodes = len(self.node_to_index) - 1
        node_idx = self.node_to_index[node]
        logger.debug(
            f"\n{'='*20} running {node_idx}/{total_nodes}"
            f"({(node_idx / total_nodes) * 100:.2f}%) {node.name} {'='*20}"
        )

        if node.op == "output":
            output_node_args = cast(Iterable[Node], node.args[0])
            set_spec(node, tuple(self.get_spec(arg, node) for arg in output_node_args))
            return

        env_args, env_kwargs = self.fetch_args_kwargs_from_env(node)

        val = node.meta.get(
            "val", getattr(self.module, node.target) if node.op == "get_attr" else None  # type: ignore [arg-type]
        )
        assert val is not None, f"can't find node {node.name} in module"
        logger.debug(f"node.name: {node.name}, val: {val}, args: {env_args}, kwargs: {env_kwargs}")

        if has_spec(node):
            return val

        if node.op == "call_function":
            flat_args_list, args_spec = tree_flatten(node.args)
            flat_kwargs_list, kwargs_spec = tree_flatten(node.kwargs)
            placements = []

            if node.target == operator.getitem:
                assert len(flat_args_list) == 2 and len(flat_kwargs_list) == 0
                assert isinstance(flat_args_list[0], Node) and isinstance(flat_args_list[1], int)
                arg_node, idx = flat_args_list

                spec = self.get_spec(arg_node, node)
                if isinstance(spec, (tuple, list)):
                    spec = spec[idx]
                set_spec(node, spec)
                return val

            flat_args_schema, args_placements = self._get_arg_schema_and_placements(
                node, flat_args_list
            )

            placements.extend(args_placements)
            flat_kwargs_schema, kwargs_placements = self._get_arg_schema_and_placements(
                node, flat_kwargs_list
            )
            placements.extend(kwargs_placements)

            op_overload = cast(OpOverload, node.target)

            # check all input tensors' ShardSpec have same device mesh.
            device_mesh = None

            def _check_same_dev_mesh(arg):
                nonlocal device_mesh
                if isinstance(arg, DTensorSpec):
                    if device_mesh is None:
                        device_mesh = arg.mesh
                    elif device_mesh != arg.mesh:
                        err_msg = f"this op receives tensors with more than one device mesh: {device_mesh}, {arg.mesh}"
                        node.meta["prop_error_msg"] = err_msg
                        raise RuntimeError(err_msg)
                elif isinstance(arg, (list, tuple)):
                    for a in arg:
                        _check_same_dev_mesh(a)

            _check_same_dev_mesh(chain(flat_args_schema, flat_kwargs_schema))

            a = tree_unflatten(flat_args_schema, args_spec)
            k = tree_unflatten(flat_kwargs_schema, kwargs_spec)

            a = list(a)
            k = dict(k)

            # This is needed because many propagation rules cannot handle arguments with kwargs. Remove those as much as possible.
            for idx, arg in enumerate(op_overload._schema.arguments):
                if arg.name not in k:
                    continue
                if arg.kwarg_only:
                    # Remove kwarg whose value is its default value.
                    if arg.has_default_value() and arg.default_value == k[arg.name]:
                        del k[arg.name]
                        continue
                else:
                    # Convert non-kwarg-only kwarg into positional arguments.
                    assert idx == len(a)
                    a.append(k.pop(arg.name))
            a = tuple(a)

            op_schema = OpSchema(op_overload._schema, a, k)

            def all_replicated(specs) -> bool:
                nonlocal device_mesh
                if isinstance(specs, (list, tuple)):
                    return all(all_replicated(spec) for spec in specs)
                elif isinstance(specs, DTensorSpec):
                    return all(p.is_replicate() for p in specs.placements)
                else:
                    raise ValueError(f"Invalid type object {specs}")

            # We consider the case where all inputs are replicated.
            if not all_replicated(placements):
                node.meta["prop_error_msg"] = (
                    f"Cannot find appropriate propagation rule for op {op_overload} with input arg spec {op_schema.args_spec}"
                )
                raise NotImplementedError(
                    "ShardingPropagator only supports cases where all inputs are replicated."
                )
            set_spec(node, placements[-1])
            return val

        return val

    def propagate(self) -> None:
        # Make node_name to node map
        node_name_to_node: Dict[str, Node] = {node.name: node for node in self.module.graph.nodes}

        for node_name, spec in self.static_tensors.items():
            try:
                node = node_name_to_node[node_name]
            except KeyError:
                raise KeyError(f"invalid mppp config, can't find static tensor named {node_name}")
            set_spec(node, spec)

        for (src, dst), spec in self.dynamic_tensors.items():
            for node_id in (src, dst):
                if node_id not in node_name_to_node:
                    raise ValueError(f"invalid mppp config, can't find node named {node_id}")
            node = node_name_to_node[src]

            if dst not in map(lambda x: x.name, node.users):
                raise ValueError(
                    f"invalid mppp config, can't find dynamic tensor {src} -> {dst} (users={node.users.keys()})"
                )

        super().run()
