from collections import defaultdict
import copy
import gc
from itertools import chain
import json
import logging
import operator
import os
from pathlib import Path
from time import time
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from furiosa_torch_ext.torch_ext import SIDE_EFFECT_OPS, preprocess
import ray
import torch
from torch._dynamo.utils import deepcopy_to_fake_tensor
from torch._subclasses import FakeTensorMode
from torch.fx import Graph, GraphModule, Node
from torch.fx.node import _side_effectful_functions
from torch.fx.passes.fake_tensor_prop import FakeTensorProp
from torch.fx.passes.split_module import split_module
from torch.utils._pytree import tree_flatten
from transformers import PretrainedConfig

from furiosa_llm.models.metadata import ModelMetadata
from furiosa_llm.parallelize.block_slicer import (
    ModuleMarkConfig,
    add_marker_op_hooks,
    get_block_slicing_edges,
    get_blockwise_sliced_color_map,
    get_submodule_paths_in_modulelists,
    is_marker_op,
    remove_marker_nodes,
)
from furiosa_llm.parallelize.compiler_config import (
    BlockType,
    CompilerConfigContext,
)
from furiosa_llm.parallelize.export.graphmodule import deserialize_gm
from furiosa_llm.parallelize.export.tensor import (
    ParamfileFormat,
    ParamFileInfo,
    ParamFileMetadata,
    save_tensors,
    write_without_concurrency_issue,
)
from furiosa_llm.parallelize.hash import get_env_independent_hash, hash_example_inputs, hash_model
from furiosa_llm.parallelize.model_creation_info import ModelCreationInfo
from furiosa_llm.parallelize.model_rewriter.api import ModelRewriter
from furiosa_llm.parallelize.model_rewriter.ops import custom_ops  # noqa: F401
from furiosa_llm.parallelize.mppp.api import Mppp
from furiosa_llm.parallelize.mppp.config import Device, MpppConfig
from furiosa_llm.parallelize.node_meta import (
    InputKind,
    QParamKind,
    get_color,
    get_original_name,
    get_qparam_kind,
    has_original_name,
    set_color,
    set_input_kind,
    set_original_name,
    set_to_be_embedded,
    set_unsharded_tensor_meta,
)
from furiosa_llm.parallelize.pipeline.builder.arg_types import (
    LogitsSliceConfig,
    NonSharedPipelineBuildConfig,
)
from furiosa_llm.parallelize.pipeline.builder.converter import (
    ADDITIONAL_PARAM_FILE_ID,
    DEFAULT_PARAM_FILE_ID_PREFIX,
    GraphModuleConverter,
    generate_graph_metadata,
)
from furiosa_llm.parallelize.pipeline.builder.transform import (
    OpInfo,
    append_op_to_the_graph,
    replace_paged_attention_index_ops_with_furiosa_sparse_index,
)
from furiosa_llm.parallelize.pipeline.builder.utils import get_constant_tensors_with_original_name
from furiosa_llm.parallelize.pipeline.types import (
    CompSuperTask,
    DataBlobId,
    MetadataTensor,
    MetadataTensorSlice,
    ParamFileId,
    ParamInfo,
    Pipeline,
    SuperTaskKind,
    TensorGenInfo,
)
from furiosa_llm.parallelize.trace import get_aten_graph_with_metadata
from furiosa_llm.parallelize.utils import (
    get_cache_path_if_exists,
    get_fake_mode,
    get_original_model_type,
    is_aten_op,
    is_custom_op,
    zip_equal,
)
from furiosa_llm.parallelize.visualize import draw_graph

from .transform import remove_output, replicate_nodes_with_multiple_colors

logger = logging.getLogger(__file__)


def _get_example_input(
    supertask: CompSuperTask,
    pipeline: Pipeline,
    fake_mode: FakeTensorMode,
) -> Tuple[torch.Tensor, ...]:
    with fake_mode:
        return tuple(
            torch.zeros(
                pipeline.tensors[input_].shape,
                dtype=pipeline.tensors[input_].dtype.to_torch_dtype(),
            )
            for input_ in supertask.inputs
        )


def _info_log_for_ray(msg: str):
    logger.info(f"[furiosa-llm] {msg}")


def _replace_blob_ids_in_pipeline(
    pipeline: Pipeline,
    target_to_new: Mapping[DataBlobId, str],
) -> None:
    blob_id_to_users: MutableMapping[DataBlobId, List[CompSuperTask]] = defaultdict(list)

    for sup in pipeline.supertasks.values():
        if not isinstance(sup, CompSuperTask) or sup.data_blob is None:
            continue
        blob_id_to_users[sup.data_blob].append(sup)

    for target, new in target_to_new.items():
        pipeline.blobs[DataBlobId(new)] = pipeline.blobs.pop(target)
        for sup in blob_id_to_users[target]:
            assert sup.data_blob == target
            sup.data_blob = DataBlobId(new)


# IMPORTANT: Compiler config generation part in this function must be kept same as `GraphModuleConverter._get_data_blob_id`.
def _compile_supertasks_in_pipeline(
    pipeline: Pipeline,
    target_ir: str,
    # current context: model_type, beam_size, phase, bucket
    compiler_config_context: CompilerConfigContext,
    model_metadata: Optional[ModelMetadata],
    blockwise_compile_used: bool,
    serialize_compiled_graphs: bool = False,
    cache_dir: Optional[os.PathLike] = None,
) -> None:
    """Compile all supertasks in pipeline, converting them to edf kind supertasks.

    Args:
        pipeline (Pipeline): pipeline to be compiled.
        target_ir (str): target ir for compilation.
        compiler_config_context (CompilerConfigContext): CompilerConfigContext to be used for compilation.
        model_metadata (Optional[ModelMetadata]): When inter-chip tensor parallelism is used,
            this is needed to determine the dimension to be sharded. Otherwise, it's not necessary.
        blockwise_compile_used (bool): Whether `pipeline` was built with blockwise compile.
        serialize_compiled_graphs (bool, optional): Whether to serialize compiled result or remain it as `CompiledGraph` object. Defaults to False.
        cache_dir (Optional[os.PathLike], optional): Cache directoy used for compilation. Defaults to None.
    """

    fake_mode = FakeTensorMode(allow_non_fake_inputs=True)

    compiled_blobs = set()
    # Dump an intermediate artifact (e.g., DFG, ir graphs, dot graphs) for debugging purpose
    dump_path = os.getenv("FURIOSA_COMPILE_DUMP_PATH")
    blob_id_to_gm_hash = {}

    tensor_to_consumer_kinds = defaultdict(list)

    for supertask_id, supertask in pipeline.supertasks.items():
        for input_ in supertask.inputs:
            tensor_to_consumer_kinds[input_].append(supertask.kind)

    for supertask_id, supertask in pipeline.supertasks.items():
        if not isinstance(supertask, CompSuperTask):
            continue
        if supertask.kind is not SuperTaskKind.FX:
            raise NotImplementedError("Supertask kind other than FX cannot be compiled now")
        if supertask.data_blob is not None:
            if supertask.data_blob in compiled_blobs:
                # already compiled
                supertask.kind = SuperTaskKind.from_str(target_ir)
                continue
            blob = pipeline.blobs[supertask.data_blob]
        else:
            assert isinstance(supertask.data, str)
            blob = supertask.data

        gm = deserialize_gm(blob)
        example_input = _get_example_input(supertask, pipeline, fake_mode)
        target_npu = GraphModuleConverter.get_target_npu_from_device(
            pipeline.devices[supertask.device]
        )

        _info_log_for_ray(
            f"Compiling pipeline {pipeline.name}, supertask {supertask_id} for {target_npu}."
        )

        compiler_config = None
        compiler_config_context = copy.deepcopy(compiler_config_context)
        num_pe = pipeline.devices[supertask.device].num_pe_per_chip
        num_chips = pipeline.devices[supertask.device].num_chip
        compiler_config_context.num_pe_per_chip = num_pe
        compiler_config_context.num_chip = num_chips

        if blockwise_compile_used:
            block_type = pipeline.get_block_type_from_supertask_id(supertask_id)
        else:
            block_type = BlockType.WHOLE
        logger.info("Block type: %s", block_type)

        compiler_config_context.block_type = block_type

        compiler_config = compiler_config_context.load_config()
        logger.info(f"Using compiler config {compiler_config}")

        output_consumer_info = [tensor_to_consumer_kinds[output] for output in supertask.outputs]

        graph_metadata = generate_graph_metadata(
            compiler_config_context,
            gm,
            num_chips,
            output_consumer_info,
        )

        _info_log_for_ray(f"Generated graph metadata: {graph_metadata}")

        compile_result, hash_val = GraphModuleConverter.compile_gm_and_get_preprocessed_gm_hash(
            gm,
            example_input,
            target_npu,
            target_ir,
            compiler_config,
            graph_metadata,
            dump_path,
            cache_dir,
        )
        _info_log_for_ray(
            f"Finished compiling pipeline {pipeline.name}, supertask {supertask_id} for {target_npu}."
        )

        assert len(compile_result.graphs) == 1

        logger.debug(f"Output graph metadata: {compile_result.graph_metadata}")

        compiled_graph: Any = compile_result.graphs[0]

        if serialize_compiled_graphs:
            compiled_graph = compiled_graph.serialize()

        if supertask.data_blob is not None:
            # replace data_blobs
            pipeline.blobs[supertask.data_blob] = compiled_graph  # type: ignore [assignment]
            blob_id_to_gm_hash[supertask.data_blob] = hash_val
            compiled_blobs.add(supertask.data_blob)
        else:
            supertask.data = compiled_graph  # type: ignore [assignment]
        supertask.kind = SuperTaskKind.from_str(target_ir)

    # Replace old blob ids to preprocessed gm's hash values.
    # This is just for debugging purpose.
    _replace_blob_ids_in_pipeline(pipeline, blob_id_to_gm_hash)


def _get_sliced_torch_where_get_attr_nodes(gm: GraphModule) -> Tuple[Node, ...]:
    """Find get_attr nodes if it's used as ``torch.ops.aten.where``'s condition tensor (first input tensor) after a slice operation."""

    cache = set()
    to_be_embedded = set()
    for node in gm.graph.nodes:
        if not (node.op == "call_function" and node.target == torch.ops.aten.where.self):
            continue

        queue: List[Tuple[Node, bool]] = [(node.args[0], False)]

        while queue:
            node, found_slice = queue.pop()
            if node.op == "get_attr" and found_slice:
                to_be_embedded.add(node)
                continue
            flattened_args, _ = tree_flatten((node.args, node.kwargs))
            for arg in flattened_args:
                if not isinstance(arg, Node) or arg in cache:
                    continue
                cache.add(arg)
                queue.append((arg, found_slice or arg.target == torch.ops.aten.slice.Tensor))
    return tuple(to_be_embedded)


def _get_zero_point_for_dpe_qparam_nodes(gm: GraphModule) -> Tuple[Node, ...]:
    """Get zero point qparam get_attr nodes running on DPE."""
    zp_for_dpe_nodes = tuple(
        node
        for node in gm.graph.nodes
        if node.op == "get_attr" and get_qparam_kind(node) == QParamKind.ZERO_POINT_FOR_DPE
    )

    for node in zp_for_dpe_nodes:
        actual_tensor = getattr(gm, node.target)
        # This assumption is not valid for fp8 models.
        if actual_tensor.dim() != 0 and tuple(actual_tensor.shape) != (1,):
            raise RuntimeError(
                f"Non-scalar dpe zero-point qparam {node.name} found, all dpe zero-point qparams should be scalar tensors for compilation."
            )
        if actual_tensor.count_nonzero() > 0:
            # TODO: remove this after compiler issue is fixed.
            logger.warning(
                f"non-zero dpe zero-point qparam found: {node.name}, this may cause inefficient compilation."
            )

    return zp_for_dpe_nodes


def _mark_constants_to_be_embedded(gm: GraphModule) -> None:
    """Mark some constants (get_attr nodes) to be embedded in FX graph as it is."""
    for node in _get_sliced_torch_where_get_attr_nodes(gm) + _get_zero_point_for_dpe_qparam_nodes(
        gm
    ):
        set_to_be_embedded(node)


def _get_commit_id() -> str:
    import furiosa_llm

    if furiosa_llm.__version__:
        return furiosa_llm.__version__.hash
    else:
        import git  # type: ignore

        repo = git.Repo(Path(__file__).parent, search_parent_directories=True)
        return repo.head.object.hexsha


def _add_block_id_info(
    original_model_type: Type,
    aten_gm: GraphModule,
    num_blocks_per_supertask: Union[int, Sequence[int]],
    embedding_layer_as_single_block: bool,
    use_marker_based_block_slicer: bool,
) -> None:
    """Add block id info for nodes in ``aten_gm``."""
    if use_marker_based_block_slicer:
        if embedding_layer_as_single_block:
            raise NotImplementedError(
                "Marker based block slicing with embedding as single block is not supported yet."
            )
        assert any(is_marker_op(node) for node in aten_gm.graph.nodes)
        # Get block id map for nodes. Nodes with same block id belongs to same block.
        get_blockwise_sliced_color_map(aten_gm, method="marker", mark_color_to_meta=True)
        remove_marker_nodes(aten_gm)
    else:
        slicing_edges = get_block_slicing_edges(
            aten_gm, original_model_type, embedding_layer_as_single_block
        )

        # Get block id map for nodes. Nodes with same block id belongs to same block.
        get_blockwise_sliced_color_map(
            aten_gm, method="split_by_edges", split_edges=slicing_edges, mark_color_to_meta=True
        )

    all_colors: Set[int] = set()
    for node in aten_gm.graph.nodes:
        if colors := get_color(node):
            all_colors.update(colors)

    if isinstance(num_blocks_per_supertask, Sequence):
        color_to_new_color = []

        acc = 0
        for i, num_blocks in enumerate(num_blocks_per_supertask):
            for _ in range(num_blocks):
                color_to_new_color.append(i)
            acc += num_blocks

        if acc != len(all_colors):
            raise ValueError(
                f"num_blocks_per_supertask {num_blocks_per_supertask} does not match the number of colors {len(all_colors)}."
            )
    else:
        assert isinstance(num_blocks_per_supertask, int)
        color_to_new_color = [i // num_blocks_per_supertask for i in range(len(all_colors))]

    # Change block ids according to `num_blocks_per_supertask``.
    for node in aten_gm.graph.nodes:
        colors = get_color(node)
        if colors is None:
            continue
        new_colors = [color_to_new_color[color] for color in colors]
        set_color(node, new_colors)


ANONYMOUS_CONSTANT_NAME_PREFIX = "ANONYMOUS_CONSTANT_"


def _add_original_name_to_anonymous_get_attr_nodes(gm: GraphModule) -> None:
    existing_original_names = set(
        get_original_name(node) for node in gm.graph.nodes if has_original_name(node)
    )
    cnt = 0
    for node in gm.graph.nodes:
        if node.op != "get_attr" or has_original_name(node):
            continue
        constant_name = f"{ANONYMOUS_CONSTANT_NAME_PREFIX}{cnt}"
        cnt += 1
        assert (
            constant_name not in existing_original_names
        ), f"constant name {constant_name} already exists in the model."
        set_original_name(node, constant_name)


def _is_anonymous_node(node: Node) -> bool:
    return has_original_name(node) and get_original_name(node).startswith(
        ANONYMOUS_CONSTANT_NAME_PREFIX
    )


def _apply_last_block_slice(
    model: Union[torch.nn.Module, ModelCreationInfo], graph: Graph, slice_direction: str
):
    logger.info("Add slice op at the end of the graph.")

    if not isinstance(model, ModelCreationInfo):
        raise NotImplementedError("Prefill last block slice is not supported for this model.")
    slice_dim = model.metadata.seq_dim_in_logits

    # Find logits node
    output_node = next(iter(reversed(graph.nodes)))
    assert output_node.op == "output"

    output_tensor_nodes = output_node.args[0]

    if len(output_tensor_nodes) == 1:
        logits_node = output_tensor_nodes[0]
    else:
        original_names = get_original_name(output_node)
        assert isinstance(original_names, tuple)
        assert len(output_tensor_nodes) == len(original_names)
        logits_index = original_names.index("logits")
        logits_node = output_tensor_nodes[logits_index]

    if slice_direction == "left":
        args: Tuple = (slice_dim, 0, 1)
    elif slice_direction == "right":
        args = (slice_dim, -1)
    else:
        raise ValueError(f"Invalid slice direction {slice_direction}.")
    append_op_to_the_graph(graph, OpInfo(torch.ops.aten.slice.Tensor, args), logits_node)


class PipelineBuilder:
    model: Union[torch.nn.Module, ModelCreationInfo]
    model_config: Optional[PretrainedConfig]

    def __init__(
        self,
        model: Union[torch.nn.Module, ModelCreationInfo],
        model_config: Optional[PretrainedConfig],
        tmp_dir: Union[str, os.PathLike],
        is_beam_search_kv_cache_sharing_model: bool,
    ):
        self.model = model
        self.model_config = model_config
        self.tmp_dir = Path(tmp_dir)
        self.is_beam_search_kv_cache_sharing_model = is_beam_search_kv_cache_sharing_model

    def __gen_pipeline_hash(
        self,
        example_args: Sequence[Any],
        example_kwargs: Dict[str, Any],
        mppp_config: MpppConfig,
        param_file_metadata: ParamFileMetadata,
        comp_supertask_kind: SuperTaskKind,
        use_blockwise_compile: bool,
        do_decompositions_for_model_rewrite: bool,
        padding_block_idx: Optional[int],
        sparse_select_version: str,
        embed_all_constants_into_graph: bool,
        num_blocks_per_supertask: Sequence[int],
        *args,
    ) -> str:
        if isinstance(self.model, ModelCreationInfo):
            original_model_type = self.model.metadata.get_optimized_cls()
            model_config = self.model.metadata.config
            # In tests, _weights_hash can be None
            weights_hash = self.model.metadata._weights_hash or model_config.name_or_path
            qformat_qparam_path = self.model.get_qparam_qformat_path()
            quantization_config = self.model.metadata.quantization_config
            seed = self.model.seed
            is_random_weight_model = self.model.random_weight_model
            allow_bfloat16_cast_with_mcp = self.model.metadata.allow_bfloat16_cast_with_mcp
        else:
            # TODO
            raise NotImplementedError("Don't support pipeline hashing for non-metadata models.")

        saved_param_names = param_file_metadata.get_saved_param_names()
        saved_param_names.sort()

        to_be_hashed = (
            _get_commit_id(),
            hash_model(  # Keep the consistency with other hash_model() usages
                original_model_type,
                model_config,
                quantization_config,
                qformat_qparam_path,
                weights_hash,
                seed,
                is_random_weight_model,
                allow_bfloat16_cast_with_mcp,
            ),
            hash_example_inputs(example_args, example_kwargs),
            mppp_config.to_json(),
            json.dumps(saved_param_names),
            str(comp_supertask_kind),
            str(use_blockwise_compile),
            str(do_decompositions_for_model_rewrite),
            str(padding_block_idx),
            str(num_blocks_per_supertask),
            str(embed_all_constants_into_graph),
            sparse_select_version,
        ) + tuple(str(arg) for arg in args)

        return get_env_independent_hash(to_be_hashed)

    @staticmethod
    def __is_aten_graph(graph: Graph) -> bool:
        return all(
            node.op in ("placeholder", "get_attr", "output")
            or (
                node.op == "call_function"
                and (
                    is_aten_op(node.target)
                    or is_custom_op(node.target)
                    or node.target == operator.getitem
                )
            )
            for node in graph.nodes
        )

    @staticmethod
    def _add_unsharded_tensor_meta(
        graph: Graph,
    ):
        # store unsharded shape info for placeholder/output nodes.
        for node in graph.nodes:
            if node.op == "placeholder":
                set_unsharded_tensor_meta(node, node.meta["tensor_meta"])
            elif node.op == "output":
                set_unsharded_tensor_meta(
                    node, tuple(arg.meta["tensor_meta"] for arg in node.args[0])
                )

    def __additional_param_file_path(self, pipeline_name: str) -> Path:
        cnt = 0
        while os.path.exists(self.tmp_dir / f"add_const_file-{pipeline_name}-{cnt}.safetensors"):
            cnt += 1
        return self.tmp_dir / f"add_const_file-{pipeline_name}-{cnt}.safetensors"

    def save_additional_params(
        self,
        example_args: Sequence[Any],
        example_kwargs: Dict[str, Any],
        file_path: os.PathLike,
        target_params: Sequence[str],
        save_format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
        cache_dir: Optional[os.PathLike] = None,
    ) -> None:
        """Save parameters in ``model``, but not in ``excludes`` to ``file_path``."""
        assert not os.path.exists(file_path)

        # Some additional params appear in aten-level, so lower it to aten level.
        aten_gm = get_aten_graph_with_metadata(
            self.model,
            example_args,
            example_kwargs,
            cache_dir=cache_dir,
        )[0]

        _add_original_name_to_anonymous_get_attr_nodes(aten_gm)

        all_tensor_constants = get_constant_tensors_with_original_name(aten_gm)
        constants_to_be_saved = {name: all_tensor_constants[name] for name in target_params}

        # Save additional params to ``file_path`` if exists.
        if constants_to_be_saved:
            save_tensors(constants_to_be_saved, file_path, save_format)

    def __gen_pipeline(
        self,
        aten_gm: Optional[GraphModule],
        pipeline_name: str,
        example_args: Sequence[Any],
        example_kwargs: Dict[str, Any],
        mppp_config: MpppConfig,
        param_file_metadata: ParamFileMetadata,
        export_path: Optional[Path],
        comp_supertask_kind: SuperTaskKind,
        # current context: model_qname, beam_size, phase, bucket
        compiler_config_context: CompilerConfigContext,
        input_names: Optional[Sequence[str]],
        output_names: Optional[Sequence[str]],
        one_supertask_per_device: bool,
        use_blockwise_compile: bool,
        use_marker_based_block_slicer: bool,
        embedding_layer_as_single_block: bool,
        do_decompositions_for_model_rewrite: bool,
        padding_block_idx: Optional[int],
        sparse_select_version: str,
        embed_all_constants_into_graph: bool,
        num_blocks_per_supertask: Union[int, Sequence[int]],
        logits_slice_config: Optional[LogitsSliceConfig],
        add_valid_length_input_tensor: bool,
        cache_dir: Optional[os.PathLike],
    ) -> Pipeline:
        if not aten_gm:
            aten_gm = self._get_transformed_aten_graph_with_original_names(
                example_args,
                example_kwargs,
                input_names,
                output_names,
                do_decompositions_for_model_rewrite,
                cache_dir,
                param_file_metadata,
                padding_block_idx,
                sparse_select_version,
                logits_slice_config,
                use_marker_based_block_slicer,
                check_compilability=comp_supertask_kind is not SuperTaskKind.FX,
            )

        logger.info("Add metadata and rewrite fx graph.")
        start = time()

        # What we want to do is to prevent only side-effect ops with no user from being eliminated by dead code elimination.
        # But union of ``_side_effectful_functions`` and ``SIDE_EFFECT_OPS`` contains only some of those side-effect ops.
        # TODO: Find a way to get a list of all side-effect aten ops.
        for node in aten_gm.graph.nodes:
            if (
                node.op != "output"
                and len(node.users) == 0
                and node.target not in _side_effectful_functions.union(SIDE_EFFECT_OPS)
            ):
                logger.warning(
                    f"Node with no user found, this might means meaningful nodes can disappear during postprocess: {node}"
                )

        assert PipelineBuilder.__is_aten_graph(aten_gm.graph)

        # Add original name for anonymous get_attr nodes, which are not given name by `add_original_name_info` and `add_qparam_info`.
        _add_original_name_to_anonymous_get_attr_nodes(aten_gm)

        # mark some tensor constants (get_attr nodes) to be embedded in FX graph as it is
        # (instead of converting them as placeholders in future stages).
        _mark_constants_to_be_embedded(aten_gm)

        # NOTE: add block id info before graph transformations because those transformations
        # might make it hard to find block boundaries.
        if use_blockwise_compile:
            if isinstance(self.model, ModelCreationInfo):
                original_model_type = self.model.metadata.get_optimized_cls()
            else:
                assert isinstance(self.model, torch.nn.Module)
                original_model_type = get_original_model_type(self.model)

            # Add block id information for nodes if possible.
            # TODO: do this before any transformation and make all transformations preserve this information.
            _add_block_id_info(
                original_model_type,
                aten_gm,
                num_blocks_per_supertask,
                embedding_layer_as_single_block,
                use_marker_based_block_slicer,
            )
            draw_graph(aten_gm, "blockwise_sliced_graph", visualize_color_info=True)
        # All marker nodes should be removed before model rewriting stage.
        if use_marker_based_block_slicer:
            remove_marker_nodes(aten_gm)

        # Get constants that are not saved in given parameter file.
        # This will be passed to PipelineConverter.
        constants_not_in_param_file = get_constant_tensors_with_original_name(
            aten_gm,
        )

        # Exclude already saved ones
        for name in param_file_metadata.get_saved_param_names():
            constants_not_in_param_file.pop(name, None)

        # Save parameters not in parameter saved file referenced by ``param_file_info`` (e.g., qparam).
        additional_param_file_info = ParamFileInfo(
            str(self.__additional_param_file_path(pipeline_name)), ParamfileFormat.SAFETENSORS
        )

        PipelineBuilder._add_unsharded_tensor_meta(aten_gm.graph)

        fake_mode = get_fake_mode(chain(aten_gm.parameters(), aten_gm.buffers()))
        fake_args_for_aten_gm = tuple(
            fake_mode.from_tensor(node.meta["val"])
            for node in aten_gm.graph.nodes
            if node.op == "placeholder"
        )

        model_rewriter = ModelRewriter(aten_gm, mppp_config)

        rewritten_model = model_rewriter.rewrite(fake_args_for_aten_gm)

        logger.info("Adding metadata and rewriting fx graph took %.2f seconds.", time() - start)

        start = time()

        # Update `num_blocks_per_graph` info in compiler config.
        compiler_config_context.num_blocks_per_graph = num_blocks_per_supertask
        pipeline = GraphModuleConverter(
            rewritten_model,
            self.model.metadata if isinstance(self.model, ModelCreationInfo) else None,
            mppp_config.devices,
            model_rewriter.get_device_id_map(),
        ).convert(
            pipeline_name,
            param_file_metadata,
            comp_supertask_kind,
            compiler_config_context,
            one_supertask_per_device,
            additional_param_file_info,
            constants_not_in_param_file,
            use_blockwise_compile,
            embed_all_constants_into_graph,
            add_valid_length_input_tensor,
            cache_dir=cache_dir,
        )
        logger.info("Converting GraphModule to pipeline took %.2f seconds.", time() - start)

        if export_path is not None:
            write_without_concurrency_issue(pipeline.to_json(), export_path)

        return pipeline

    @staticmethod
    def __replace_original_tensor_names(
        origin: MutableMapping[str, MetadataTensor],
        slices: Mapping[str, MetadataTensorSlice],
        new_names: Sequence[str],
    ) -> bool:
        need_resave = False
        replace_map = {}

        # Find original tensor names that need to be replaced.
        for cur_name, original_tensor_info in tuple(origin.items()):
            new_name = new_names[original_tensor_info.idx]
            if cur_name != new_name:
                origin[new_name] = original_tensor_info
                need_resave = True
                replace_map[cur_name] = new_name

        # Replace original tensor names in tensor slices.
        for tensor_slice_meta in slices.values():
            if tensor_slice_meta.origin in replace_map:
                tensor_slice_meta.origin = replace_map[tensor_slice_meta.origin]
        return need_resave

    def build_pipelines(
        self,
        devices: Sequence[Device],
        mppp: Mppp,
        non_shared_configs: Sequence[NonSharedPipelineBuildConfig],
        param_file_metadata: ParamFileMetadata,
        comp_supertask_kind: SuperTaskKind = SuperTaskKind.FX,
        cache_dir: Optional[Path] = None,
        one_supertask_per_device: bool = False,
        use_blockwise_compile: bool = False,
        embedding_layer_as_single_block: bool = False,
        do_decompositions_for_model_rewrite: bool = False,
        sparse_select_version: str = "v1.5",
        embed_all_constants_into_graph: bool = False,
        padding_block_idx: Optional[int] = None,
        add_valid_length_input_tensor: bool = False,
        param_saved_format: str = "safetensors",
        num_pipeline_builder_workers: int = 1,
        num_compile_workers: int = 1,
    ) -> List[Pipeline]:
        input_samples_in_metadata_with_name_copied = copy.copy(non_shared_configs)
        try:
            ray.init(num_cpus=max([num_pipeline_builder_workers - 1, num_compile_workers - 1]))
            pipelines = self.build_fx_pipelines_in_parallel(
                devices=devices,
                mppp=mppp,
                non_shared_configs=non_shared_configs,
                param_file_metadata=param_file_metadata,
                cache_dir=cache_dir,
                one_supertask_per_device=one_supertask_per_device,
                use_blockwise_compile=use_blockwise_compile,
                embedding_layer_as_single_block=embedding_layer_as_single_block,
                do_decompositions_for_model_rewrite=do_decompositions_for_model_rewrite,
                sparse_select_version=sparse_select_version,
                embed_all_constants_into_graph=embed_all_constants_into_graph,
                num_pipeline_builder_workers=num_pipeline_builder_workers,
                padding_block_idx=padding_block_idx,
                add_valid_length_input_tensor=add_valid_length_input_tensor,
                param_saved_format=param_saved_format,
            )
            assert all(isinstance(pipeline, Pipeline) for pipeline in pipelines)

            if comp_supertask_kind is SuperTaskKind.FX:
                return pipelines

            # order should be preserved
            compile_config_contexts = [
                input_sample.compile_config
                for input_sample in input_samples_in_metadata_with_name_copied
            ]
            # Update `num_blocks_per_graph` info in compiler config.
            for compiler_config_context, non_shared_config in zip_equal(
                compile_config_contexts, non_shared_configs
            ):
                compiler_config_context.num_blocks_per_graph = (
                    non_shared_config.num_blocks_per_supertask
                )

            model_metadata = (
                self.model.metadata if isinstance(self.model, ModelCreationInfo) else None
            )

            return PipelineBuilder.compile_supertasks_in_parallel(
                pipelines,
                compile_config_contexts,
                comp_supertask_kind.to_ir_kind(),
                model_metadata,
                num_compile_workers,
                use_blockwise_compile,
                cache_dir=cache_dir,
            )
        except:
            msg = "Encountered exception!\n"
            cfgs = copy.deepcopy(non_shared_configs)
            for cfg in cfgs:
                cfg.kwargs_data.pop('past_key_values', None)
            msg += f"non_shared_configs(w/o past_kv): {cfgs}\n"
            print(msg)
            raise
        finally:
            ray.shutdown()

    def build_fx_pipelines_in_parallel(
        self,
        devices: Sequence[Device],
        mppp: Mppp,
        non_shared_configs: Sequence[NonSharedPipelineBuildConfig],
        param_file_metadata: Union[ParamFileMetadata, ParamFileInfo],
        cache_dir: Optional[Path] = None,
        one_supertask_per_device: bool = False,
        use_blockwise_compile: bool = False,
        embedding_layer_as_single_block: bool = False,
        do_decompositions_for_model_rewrite: bool = False,
        sparse_select_version: str = "v1.5",
        embed_all_constants_into_graph: bool = False,
        num_pipeline_builder_workers: int = 1,
        padding_block_idx: Optional[int] = None,
        add_valid_length_input_tensor: bool = False,
        param_saved_format: str = "safetensors",
    ) -> List[Pipeline]:  #

        assert num_pipeline_builder_workers > 0

        tasks: List[List[NonSharedPipelineBuildConfig]] = [
            list() for _ in range(num_pipeline_builder_workers)
        ]
        # split task into remote task and local task
        div, remain = divmod(len(non_shared_configs), num_pipeline_builder_workers)
        num_tasks = [div] * num_pipeline_builder_workers
        for i in range(remain):
            num_tasks[i] += 1

        non_shared_configs = list(non_shared_configs)
        for i, task in enumerate(tasks):
            while len(task) < num_tasks[i]:
                task.append(non_shared_configs.pop(0))
        assert len(non_shared_configs) == 0
        assert len(tasks) == num_pipeline_builder_workers
        assert all(len(task) == num_tasks[i] for i, task in enumerate(tasks))

        local_task = tasks[0]  # only on local task
        remote_tasks = tasks[1:] if len(tasks) >= 2 else list()

        other_args = (
            devices,
            param_file_metadata,
            cache_dir,
            mppp,
            one_supertask_per_device,
            use_blockwise_compile,
            embedding_layer_as_single_block,
            do_decompositions_for_model_rewrite,
            padding_block_idx,
            add_valid_length_input_tensor,
            sparse_select_version,
            embed_all_constants_into_graph,
        )
        if num_pipeline_builder_workers == 1:
            ## solely do local run
            pipelines_local = PipelineBuilder.__build_fx_pipelines_aux(
                self, non_shared_configs=local_task, other_args=other_args
            )
            return pipelines_local

        assert remote_tasks

        ## remote runs
        common_args = ray.put(other_args)
        remote_tasks_to_call = [
            PipelineBuilder.__build_fx_pipelines_with_ray.remote(self, task, common_args)
            for task in remote_tasks
        ]

        pipelines_local = PipelineBuilder.__build_fx_pipelines_aux(
            self, non_shared_configs=local_task, other_args=other_args
        )
        pipelines_remote = ray.get(remote_tasks_to_call)
        pipelines_remote = [pipeline for pipelines in pipelines_remote for pipeline in pipelines]

        return pipelines_local + pipelines_remote

    @staticmethod
    @ray.remote
    def __build_fx_pipelines_with_ray(
        builder: "PipelineBuilder",
        non_shared_configs: Sequence[NonSharedPipelineBuildConfig],
        other_args: Sequence,
    ) -> List[Pipeline]:

        return PipelineBuilder.__build_fx_pipelines_aux(builder, non_shared_configs, other_args)

    @staticmethod
    def __build_fx_pipelines_aux(
        builder: "PipelineBuilder",
        non_shared_configs: Sequence[NonSharedPipelineBuildConfig],
        other_args: Sequence,
    ) -> List[Pipeline]:
        (
            devices,
            param_file_metadata,
            cache_dir,
            mppp,
            one_supertask_per_device,
            use_blockwise_compile,
            embedding_layer_as_single_block,
            do_decompositions_for_model_rewrite,
            padding_block_idx,
            add_valid_length_input_tensor,
            sparse_select_version,
            embed_all_constants_into_graph,
        ) = other_args

        pipelines = list()

        for config in non_shared_configs:
            example_input_by_tensor_metadata_args = config.args_data
            example_input_by_tensor_metadata_kwargs = config.kwargs_data
            pipeline_name = config.pipeline_name
            compiler_config_context = config.compile_config

            # this example input is assumed to include TensorMetaData,
            # but turn in into fake tensor in here

            fake_mode = FakeTensorMode(allow_non_fake_inputs=True)

            # Convert all actual tensors and TensorGenInfo objects to fake tensors.
            with TensorGenInfo.deepcopy_to_fake_tensor_mode(fake_mode):
                example_input_in_fake_tensor_args = deepcopy_to_fake_tensor(
                    example_input_by_tensor_metadata_args, fake_mode
                )
                example_input_in_fake_tensor_kwargs = deepcopy_to_fake_tensor(
                    example_input_by_tensor_metadata_kwargs, fake_mode
                )

            _info_log_for_ray(f"Generating pipeline {pipeline_name}")
            pipeline = builder.build(
                pipeline_name,
                devices,
                example_input_in_fake_tensor_args,
                example_input_in_fake_tensor_kwargs,
                mppp,
                param_file_metadata,
                compiler_config_context,
                SuperTaskKind.FX,
                cache_dir=cache_dir,
                one_supertask_per_device=one_supertask_per_device,
                use_blockwise_compile=use_blockwise_compile,
                embedding_layer_as_single_block=embedding_layer_as_single_block,
                do_decompositions_for_model_rewrite=do_decompositions_for_model_rewrite,
                padding_block_idx=padding_block_idx,
                sparse_select_version=sparse_select_version,
                embed_all_constants_into_graph=embed_all_constants_into_graph,
                num_blocks_per_supertask=config.num_blocks_per_supertask,
                logits_slice_config=config.logits_slice_config,
                add_valid_length_input_tensor=add_valid_length_input_tensor,
            )
            gc.collect()
            pipelines.append(pipeline)
        return pipelines

    @staticmethod
    def compile_supertasks_in_parallel(
        pipelines: Sequence[Pipeline],
        compile_config_contexts: Sequence[CompilerConfigContext],
        target_ir: str,
        model_metadata: Optional[ModelMetadata],
        num_workers: int,
        blockwise_compile_used: bool,
        cache_dir: Optional[os.PathLike] = None,
    ) -> List[Pipeline]:
        assert len(pipelines) == len(compile_config_contexts)

        if num_workers == 1:
            for pipeline, compile_config in zip(pipelines, compile_config_contexts):
                _compile_supertasks_in_pipeline(
                    pipeline,
                    target_ir,
                    compile_config,
                    model_metadata,
                    blockwise_compile_used,
                    cache_dir=cache_dir,
                )
            return list(pipelines)
        else:  # do parallel run
            pipelines_with_compile_config = list(zip_equal(pipelines, compile_config_contexts))

            share, remainder = divmod(len(pipelines_with_compile_config), num_workers)
            remote_pipelines_ray_tasks = [
                PipelineBuilder.__compile_supertasks_with_ray.remote(
                    pipelines_with_compile_config[
                        worker_idx * share
                        + min(worker_idx, remainder) : (worker_idx + 1) * share
                        + min(worker_idx + 1, remainder)
                    ],
                    target_ir,
                    model_metadata,
                    blockwise_compile_used,
                    cache_dir,
                )
                for worker_idx in range(1, num_workers)
            ]

            local_pipelines = PipelineBuilder.__compile_supertasks_aux(
                pipelines_with_compile_config[: share + min(1, remainder)],
                target_ir,
                model_metadata,
                blockwise_compile_used,
                cache_dir=cache_dir,
            )
            remote_pipelines: List[Pipeline] = sum(ray.get(remote_pipelines_ray_tasks), [])

            for pipeline in remote_pipelines:
                for task in pipeline.supertasks.values():
                    if not isinstance(task, CompSuperTask) or task.kind is SuperTaskKind.FX:
                        continue
                    try:
                        from furiosa.native_compiler import CompiledGraph  # type: ignore[import]
                    except ImportError:
                        logger.error("furiosa-native-compiler is required to load EDF format")
                        raise

                    if task.data is not None:
                        if isinstance(task.data, bytes):
                            task.data = CompiledGraph.deserialize(task.data, tag="")
                    else:
                        assert task.data_blob is not None
                        data = pipeline.blobs[task.data_blob]  # type: ignore[attr-defined]
                        if isinstance(data, bytes):
                            pipeline.blobs[task.data_blob] = CompiledGraph.deserialize(  # type: ignore[assignment, arg-type, attr-defined]
                                data, tag=task.data_blob
                            )

            return local_pipelines + remote_pipelines  # type: ignore

    @staticmethod
    def __compile_supertasks_aux(
        pipelines: Sequence[Tuple[Pipeline, CompilerConfigContext]],
        target_ir: str,
        model_metadata: Optional[ModelMetadata],
        blockwise_compile_used: bool,
        serialize_compiled_graphs: bool = False,
        cache_dir: Optional[os.PathLike] = None,
    ) -> List[Pipeline]:
        for pipeline, compiler_config_context in pipelines:
            start = time()
            _info_log_for_ray(f"Compiling supertasks in {pipeline.name}.")
            _compile_supertasks_in_pipeline(
                pipeline,
                target_ir,
                compiler_config_context,
                model_metadata,
                blockwise_compile_used,
                serialize_compiled_graphs=serialize_compiled_graphs,
                cache_dir=cache_dir,
            )
            _info_log_for_ray(
                f"Finished compiling supertasks in {pipeline.name}, elapsed: {time() - start:.2f}s."
            )

        return list(map(operator.itemgetter(0), pipelines))

    @staticmethod
    @ray.remote
    def __compile_supertasks_with_ray(
        pipelines: Sequence[Tuple[Pipeline, CompilerConfigContext]],
        target_ir: str,
        model_metadata: Optional[ModelMetadata],
        blockwise_compile_used: bool,
        cache_dir: Optional[os.PathLike],
    ) -> List[Pipeline]:
        return PipelineBuilder.__compile_supertasks_aux(
            pipelines,
            target_ir,
            model_metadata,
            blockwise_compile_used,
            serialize_compiled_graphs=True,
            cache_dir=cache_dir,
        )

    def build(
        self,
        pipeline_name: str,
        devices: Sequence[Device],
        example_args: Sequence[Any],
        example_kwargs: Dict[str, Any],
        mppp_or_mppp_config: Union[MpppConfig, Mppp],
        param_file_metadata: Union[ParamFileMetadata, ParamFileInfo],
        # current context: model_qname, beam_size, phase, bucket
        compiler_config_context: CompilerConfigContext,
        comp_supertask_kind: SuperTaskKind = SuperTaskKind.FX,
        input_names: Optional[Sequence[str]] = None,
        output_names: Optional[Sequence[str]] = None,
        cache_dir: Optional[Path] = None,
        one_supertask_per_device: bool = False,
        use_blockwise_compile: bool = False,
        embedding_layer_as_single_block: bool = False,
        do_decompositions_for_model_rewrite: bool = False,
        padding_block_idx: Optional[int] = None,
        sparse_select_version: str = "v1.5",
        embed_all_constants_into_graph: bool = False,
        num_blocks_per_supertask: Union[int, Sequence[int]] = 1,
        logits_slice_config: Optional[LogitsSliceConfig] = None,
        add_valid_length_input_tensor: bool = False,
    ) -> Pipeline:
        if isinstance(param_file_metadata, ParamFileInfo):
            param_file_metadata = ParamFileMetadata.load(
                param_file_metadata.path, param_file_metadata.format
            )

        # Use marker based block slicer if MCP is not used.
        use_marker_based_block_slicer = isinstance(self.model, ModelCreationInfo) and (
            not self.model.metadata.quantization_config
            or not self.model.metadata.quantization_config.use_mcp
        )

        if isinstance(mppp_or_mppp_config, Mppp):
            # Add original name information and do all graph transformations before generating mppp config.
            # Original name information might be needed for mppp config generation (e.g., block slicer).
            # And Graph transformations might affect mppp config to be generated.
            aten_gm = self._get_transformed_aten_graph_with_original_names(
                example_args,
                example_kwargs,
                input_names,
                output_names,
                do_decompositions_for_model_rewrite,
                cache_dir,
                param_file_metadata,
                padding_block_idx,
                sparse_select_version,
                logits_slice_config,
                use_marker_based_block_slicer,
                check_compilability=comp_supertask_kind is not SuperTaskKind.FX,
            )

            mppp_config = mppp_or_mppp_config.gen_config(
                self.model,
                self.model_config,
                devices,
                example_args,
                example_kwargs,
                graph_module=aten_gm,
                other_configs={"use_marker_based_block_slicer": use_marker_based_block_slicer},
            )
        else:
            mppp_config = mppp_or_mppp_config
            aten_gm = None

        # We cache models only if model is `ModelCreationInfo` now.
        # TODO: add caching support for ordinary nn.Module.
        if (
            cache_dir is not None
            and isinstance(self.model, ModelCreationInfo)
            and self.model.is_hashable()
            and os.getenv("FURIOSA_DISABLE_PIPELINE_CACHE") != "1"
        ):
            if isinstance(num_blocks_per_supertask, int):
                num_hidden_layers = self.model.metadata.num_hidden_layers
                num_blocks_per_supertask_: Sequence[int] = [
                    layer_idx // num_blocks_per_supertask for layer_idx in range(num_hidden_layers)
                ]
            else:
                num_blocks_per_supertask_ = num_blocks_per_supertask

            # name is not used for hashing because it doesn't affect other fields of pipeline.
            pipeline_hash = self.__gen_pipeline_hash(
                example_args,
                example_kwargs,
                mppp_config,
                param_file_metadata,
                comp_supertask_kind,
                use_blockwise_compile,
                do_decompositions_for_model_rewrite,
                padding_block_idx,
                sparse_select_version,
                embed_all_constants_into_graph,
                num_blocks_per_supertask_,
                logits_slice_config,
                use_marker_based_block_slicer,
                add_valid_length_input_tensor,
            )
            need_resave = False
            need_additional_param_save = False  # whether parameters not in parameter file referenced by ``param_info`` exists.
            additional_params_to_be_saved = []
            additional_param_file_path = self.__additional_param_file_path(pipeline_name)
            export_path = cache_dir / "pipelines" / f"{pipeline_name}-{pipeline_hash}.json"
            os.makedirs(cache_dir / "pipelines", exist_ok=True)

            cached_pipeline_path = get_cache_path_if_exists(pipeline_hash, "json", cache_dir)

            if cached_pipeline_path:
                # cached pipeline exists.
                cached_pipeline = Pipeline.load(cached_pipeline_path)
                if cached_pipeline.name != pipeline_name:
                    need_resave = True
                    cached_pipeline.name = pipeline_name

                if input_names is not None:
                    need_resave &= PipelineBuilder.__replace_original_tensor_names(
                        cached_pipeline.metadata.tensors.inputs,
                        cached_pipeline.metadata.tensor_slices.inputs,
                        input_names,
                    )
                if output_names is not None:
                    need_resave &= PipelineBuilder.__replace_original_tensor_names(
                        cached_pipeline.metadata.tensors.outputs,
                        cached_pipeline.metadata.tensor_slices.outputs,
                        output_names,
                    )

                new_param_files: Dict[ParamFileId, ParamFileInfo] = {}
                param_file_path_to_id: Dict[str, ParamFileId] = {}
                for tensor_info in cached_pipeline.tensors.values():
                    if not isinstance(tensor_info, ParamInfo):
                        continue
                    cached_param_file_info = cached_pipeline.param_files[
                        tensor_info.value.param_file
                    ]

                    need_resave = True
                    if saved_param_file_path := param_file_metadata.get_saved_param_file(
                        tensor_info.value.name
                    ):
                        # check given param file has same param names as
                        # param file used for cached pipeline
                        if cached_param_file_info.path != saved_param_file_path:
                            saved_param_file_path = os.fspath(saved_param_file_path)
                            if saved_param_file_path not in param_file_path_to_id:
                                new_param_file_id = ParamFileId(
                                    f"{DEFAULT_PARAM_FILE_ID_PREFIX}_{len(param_file_path_to_id)}"
                                )
                                assert new_param_file_id not in new_param_files
                                param_file_path_to_id[saved_param_file_path] = new_param_file_id
                                new_param_files[new_param_file_id] = ParamFileInfo(
                                    saved_param_file_path,
                                    param_file_metadata.format,
                                )
                            new_param_file_id = param_file_path_to_id[saved_param_file_path]
                            tensor_info.value.param_file = new_param_file_id
                            need_resave = True
                    else:
                        # This param doesn't exist in given param file. Add this to  ``additional_params_to_be_saved``.
                        tensor_info.value.param_file = ADDITIONAL_PARAM_FILE_ID
                        need_additional_param_save = True
                        additional_params_to_be_saved.append(tensor_info.value.name)
                        need_resave = True

                additional_file_save_format = ParamfileFormat.SAFETENSORS
                if need_additional_param_save:
                    new_param_files[ADDITIONAL_PARAM_FILE_ID] = ParamFileInfo(
                        os.fspath(additional_param_file_path), additional_file_save_format
                    )

                cached_pipeline.param_files = new_param_files

                if need_additional_param_save:
                    self.save_additional_params(
                        example_args,
                        example_kwargs,
                        additional_param_file_path,
                        additional_params_to_be_saved,
                        additional_file_save_format,
                        cache_dir=cache_dir,
                    )

                # if name, param info or input/output names is different from cached one,
                # reexport the pipeline.
                if need_resave:
                    write_without_concurrency_issue(cached_pipeline.to_json(), export_path)

                return cached_pipeline
        else:
            # don't cache
            export_path = None

        # Don't cache if comp_supertask_kind != "fx" because other formats
        # cannot be serialized properly.
        # FIXME: cache other formats after fixing issues.
        if comp_supertask_kind != "fx":
            export_path = None

        return self.__gen_pipeline(
            aten_gm,
            pipeline_name,
            example_args,
            example_kwargs,
            mppp_config,
            param_file_metadata,
            export_path,
            comp_supertask_kind,
            compiler_config_context,
            input_names,
            output_names,
            one_supertask_per_device,
            use_blockwise_compile,
            use_marker_based_block_slicer,
            embedding_layer_as_single_block,
            do_decompositions_for_model_rewrite,
            padding_block_idx,
            sparse_select_version,
            embed_all_constants_into_graph,
            num_blocks_per_supertask,
            logits_slice_config,
            add_valid_length_input_tensor,
            cache_dir=cache_dir,
        )

    def _transform_graph(
        self,
        gm: GraphModule,
        padding_block_idx: Optional[int],
        sparse_select_version: str,
        logits_slice_config: Optional[LogitsSliceConfig],
    ) -> None:
        """Transform graph in-place."""
        if logits_slice_config:
            if logits_slice_config.slice_size == 0:
                remove_output(gm.graph, eliminate_dead_code=True)
            else:
                if not logits_slice_config.slice_direction:
                    raise ValueError("slice direction must be given when slice size is not 0.")
                _apply_last_block_slice(self.model, gm.graph, logits_slice_config.slice_direction)

        if padding_block_idx is not None:
            replace_paged_attention_index_ops_with_furiosa_sparse_index(
                gm.graph,
                padding_block_idx,
                self.is_beam_search_kv_cache_sharing_model,
                sparse_select_version,
            )
        gm.recompile()

    def _get_transformed_aten_graph_with_original_names(
        self,
        # Args for tracing
        example_args: Sequence[Any],
        example_kwargs: Dict[str, Any],
        input_names: Optional[Sequence[str]],
        output_names: Optional[Sequence[str]],
        do_decompositions_for_model_rewrite: bool,
        cache_dir: Optional[os.PathLike],
        param_file_info: ParamFileMetadata,
        # Args for graph transformation
        padding_block_idx: Optional[int],
        sparse_select_version: str,
        logits_slice_config: Optional[LogitsSliceConfig],
        use_marker_based_block_slicer: bool,
        check_compilability: bool,
    ) -> GraphModule:
        if use_marker_based_block_slicer:
            module_mark_config = ModuleMarkConfig(include_submodules_in_modulelists=True)
        else:
            module_mark_config = None

        aten_gm = get_aten_graph_with_metadata(
            self.model,
            example_args,
            example_kwargs,
            input_names=input_names,
            output_names=output_names,
            do_decompositions_for_model_rewrite=do_decompositions_for_model_rewrite,
            cache_dir=cache_dir,
            param_file_metadata=param_file_info,
            module_mark_config=module_mark_config,
            check_compilability=check_compilability,
        )[0]

        self._transform_graph(
            aten_gm,
            padding_block_idx,
            sparse_select_version,
            logits_slice_config,
        )
        return aten_gm


def partition_graph_with_marker(
    model: torch.nn.Module,
    example_args: Sequence,
    example_kwargs: Mapping[str, Any],
    module_selector: Optional[Callable[[str, torch.nn.Module], bool]] = None,
    include_modules_in_module_lists: bool = False,
    aten_graph: bool = True,
    include_common_ancestor_in_first_partition: bool = False,
    dynamic_shape: bool = False,
    dynamic_shapes_config: Optional[Union[Dict[str, Any], Tuple[Any], List[Any]]] = None,
    do_preprocess_for_compile: bool = False,
) -> GraphModule:
    """Trace model and get sub fx graph partitions using marker.

    Args:
        model (torch.nn.Module): model to be traced.
        example_args (Sequence): Positional arguments for tracing.
        example_kwargs (Mapping[str, Any]): Keyword arguments for tracing.
        module_selector (Optional[Callable[[str, torch.nn.Module], bool]], optional): Selects which submodule to be one partition.
            The function should accept two arguments: submodule path and submodule itself, and return True
            if the submodule is selected.
        include_modules_in_module_lists (bool, optional): If true, submodules in `torch.nn.ModuleList` is included in
            target modules and each of them becomes independent sub fx graph. Defaults to False.
        aten_graph (bool, optional): If true, ATen IR level fx graph is returned. Otherwise, Torch IR level fx graph is returned.
            Defaults to True.
        include_common_ancestor_in_first_partition (bool, optional): If True, common ancestor nodes that belong to multiple partitions are
            only included in first partition containing them. Otherwise, common nodes are replicated to all block
        dynamic_shape (bool, optional): Whether to get dynamic shape graph. Defaults to False.
        dynamic_shapes_config (Optional[Union[Dict[str, Any], Tuple[Any], List[Any]]], optional): Dynamic shape config
            which will be passed to `dynamic_shapes` argument of `torch._dynamo.export`. Defaults to None.
        do_preprocess_for_compile (bool, optional): If true, the sub graphmodules are preprocessed for compilation.
            This includes functionalization and decomposition.
    Returns:
        GraphModule: contains multiple sub graphmodules each of which corresponds to each piece.
            Each submodule's placeholder node has input kind (i.e., whether it is originally an input, constant or intermediate tensor)
            information and this can be obtained by calling `get_input_kind` for the placeholder node.
    """

    if include_modules_in_module_lists:
        additional_target_module_paths = set(get_submodule_paths_in_modulelists(model))
    else:
        additional_target_module_paths = set()

    def submodule_selector(path: str, submodule: torch.nn.Module) -> bool:
        return (module_selector is not None and module_selector(path, submodule)) or (
            path in additional_target_module_paths
        )

    hook_remover = add_marker_op_hooks(
        model,
        submodule_selector,
        allow_overlapping_submodule_selection=False,
    )

    # Tracing marker module might affect or be affected by other `torch._dynamo.export` calls.
    torch._dynamo.reset()
    gm = torch._dynamo.export(
        model,
        aten_graph=aten_graph,
        tracing_mode="symbolic" if dynamic_shape else "static",
        dynamic_shapes=dynamic_shapes_config,
    )(*example_args, **example_kwargs).graph_module
    torch._dynamo.reset()

    hook_remover()

    _, color_to_module_name = get_blockwise_sliced_color_map(
        gm,
        method="marker",
        mark_common_ancestor_as_first_layer=include_common_ancestor_in_first_partition,
    )

    remove_marker_nodes(gm)
    replicate_nodes_with_multiple_colors(gm)

    def splitter(node):
        colors = get_color(node)
        assert len(colors) == 1
        return color_to_module_name[colors[0]]

    splitted = split_module(gm, gm, splitter)

    assert isinstance(splitted, GraphModule)

    if do_preprocess_for_compile:
        # fill "val" metadata for all nodes in `splitted`.
        example_args = []
        for node in splitted.graph.find_nodes(op="placeholder"):
            if not node.users:
                arg = node.meta.get("val")
            else:
                arg = node.meta["val"]
            example_args.append(arg)
        FakeTensorProp(splitted, FakeTensorMode(allow_non_fake_inputs=True)).propagate(
            *example_args
        )

        for node in splitted.graph.nodes:
            if node.op != "call_module":
                continue
            sub_gm = splitted.get_submodule(node.target)

            args = []

            for arg in node.args:
                if isinstance(arg, Node):
                    arg = arg.meta["val"]
                args.append(arg)

            sub_gm = preprocess(
                sub_gm,
                args,
            )
            splitted.set_submodule(node.target, sub_gm)

    # Add input kind information for each sub graphmodule inputs.
    for node in splitted.graph.find_nodes(op="call_module"):
        sub_gm = splitted.get_submodule(node.target)
        for arg_node_in_container, ph_node_in_submodule in zip_equal(
            node.args, sub_gm.graph.find_nodes(op="placeholder")
        ):
            if arg_node_in_container.op == "get_attr":
                set_input_kind(ph_node_in_submodule, InputKind.CONSTANT_TENSOR)
            elif arg_node_in_container.op == "placeholder":
                set_input_kind(ph_node_in_submodule, InputKind.USER_INPUT)
            else:
                set_input_kind(ph_node_in_submodule, InputKind.INTERMEDIATE_TENSOR)

    return splitted
