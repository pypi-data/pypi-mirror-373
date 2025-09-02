import base64
import dataclasses
import json
import logging
import os
from pathlib import Path
import typing
from typing import Any, Dict, Final, List, Mapping, Optional, Set, Tuple, Union, cast

from pydantic import BaseModel
from safetensors import safe_open
import torch
from torch._dynamo.source import AttrSource, GetItemSource, LocalSource
from torch._dynamo.utils import deepcopy_to_fake_tensor
from torch._export.serde.schema import Graph
from torch._export.serde.serialize import (
    EnumEncoder,
    GraphModuleDeserializer,
    GraphModuleSerializer,
    _dataclass_to_dict,
    _dict_to_dataclass,
)
from torch._guards import Source
from torch._subclasses.fake_tensor import FakeTensor, FakeTensorMode
from torch.fx import GraphModule, Node
from torch.fx.experimental import symbolic_shapes
from typing_extensions import TypeAlias

try:
    # >= 2.2
    from torch.export.graph_signature import ExportGraphSignature  # type: ignore
except ModuleNotFoundError:
    # 2.1
    from torch._export.exported_program import CallSpec, ExportGraphSignature  # type: ignore

from furiosa_llm.parallelize.export.tensor import (
    ParamfileFormat,
    ParamFileInfo,
    ParamFileMetadata,
    deserialize_tensors,
    get_tensor_with_safetensors_fp,
    serialize_tensors,
    write_without_concurrency_issue,
)
from furiosa_llm.parallelize.node_meta import (
    SerializableMetadata,
    fill_tensor_meta_from_val_meta,
    get_original_name,
    is_weight_or_buffer,
)
from furiosa_llm.parallelize.utils import get_torch_major_version, recursive_getattr, zip_equal
from furiosa_llm.utils import get_path_via_hot_cache

_METADATA_KEY: Final[str] = "metadata"

_OWNED_PARAM_ID: Final[str] = "owned"
_SHARED_PARAM_ID_PREFIX: Final[str] = "shared"

_SUPPORTED_DYNAMO_SOURCE_TYPES: Final[Set] = {LocalSource, GetItemSource, AttrSource}

logger = logging.getLogger(__file__)


class _ConstantSavedInfo(BaseModel):
    # Reference to parameter files.
    param_files: Dict[str, ParamFileInfo]
    tensor_to_saved_file_id_and_saved_name: Dict[str, Tuple[str, str]]

    # Self containing tensors.
    blob: Optional[str]

    def __init__(
        self,
        param_files: Dict[str, ParamFileInfo],
        tensor_to_saved_file_id_and_saved_name: Dict[str, Tuple[str, str]],
        blob: Optional[str],
    ):
        super(_ConstantSavedInfo, self).__init__(
            param_files=param_files,
            tensor_to_saved_file_id_and_saved_name=tensor_to_saved_file_id_and_saved_name,
            blob=blob,
        )


class _GraphModuleMetadata(BaseModel):
    node_metas: Dict[str, SerializableMetadata]
    node_dynamo_source_info: Dict[str, Dict]
    node_names: List[str]
    constant_saved_info: Optional[_ConstantSavedInfo]
    getattr_node_targets: Dict[str, str]

    def with_constant_saved_info(
        self, constant_saved_info: _ConstantSavedInfo
    ) -> "_GraphModuleMetadata":
        return _GraphModuleMetadata(
            node_metas=self.node_metas,
            node_dynamo_source_info=self.node_dynamo_source_info,
            node_names=self.node_names,
            constant_saved_info=constant_saved_info,
            getattr_node_targets=self.getattr_node_targets,
        )


def _dynamo_source_dict_to_class(cls, data):
    """dict_to_class converter for torch._guards.Source type."""
    if cls is typing.Any:
        return data
    elif issubclass(cls, Source):
        for candidate_cls in _SUPPORTED_DYNAMO_SOURCE_TYPES:
            try:
                obj = candidate_cls(**data)
                type_hints = typing.get_type_hints(candidate_cls)
                for f in dataclasses.fields(candidate_cls):
                    name = f.name
                    new_field_obj = _dynamo_source_dict_to_class(
                        type_hints[name], getattr(obj, name)
                    )
                    data[name] = new_field_obj
                # because candidate class can be frozen class.
                return candidate_cls(**data)
            except Exception:
                pass
        assert False
    elif isinstance(data, (str, int, bool)):
        assert not issubclass(cls, Source)
        return data
    else:
        assert False


def _check_supported_dynamo_source(obj: Source) -> None:
    if isinstance(obj, LocalSource):
        pass
    elif isinstance(obj, GetItemSource):
        if not isinstance(obj.index, (int, str)):
            raise NotImplementedError("Int or str type indexing is allowed now")
        if obj.index_is_slice:
            raise NotImplementedError("Slice indexing is not supported")
        _check_supported_dynamo_source(obj.base)
    elif isinstance(obj, AttrSource):
        _check_supported_dynamo_source(obj.base)
    else:
        raise NotImplementedError(f"Unsupported source type: {type(obj)}")


def _get_metadata(gm: GraphModule) -> Tuple[Dict[str, SerializableMetadata], Dict[str, Any]]:
    # Returns: (dict of node metadata, dynamo source info)

    # Store some metadata for each node because those metadata is lost during serialization.
    node_metas = {}
    for node in gm.graph.nodes:
        assert node.name not in node_metas
        node_metas[node.name] = SerializableMetadata.from_node(node)

    # Store _dynamo_source info for each node if exists.
    # This information is used for matching graph placeholder nodes to original input tensors.
    dynamo_source_info = {}
    for node in gm.graph.nodes:
        if node.op != "placeholder":
            break
        if source := getattr(node, "_dynamo_source", None):
            _check_supported_dynamo_source(source)
            assert isinstance(source, Source)
            dynamo_source_info[node.name] = dataclasses.asdict(source)

    return node_metas, dynamo_source_info


def _separate_constants_in_gm(
    gm: GraphModule,
) -> Tuple[GraphModule, Dict[str, torch.Tensor], Dict[str, str]]:
    """## Lift all get_attr nodes in graph to placeholder nodes.

    ### Args:
        - `gm (GraphModule)`:

    ### Returns:
        - `Tuple[GraphModule, Dict[str, torch.Tensor], Dict[str, str]]`: Tuple of lifted graph module, constant tensors in the gm, and original targets of lifted getattr nodes.`
    """
    constants = {
        node.target: recursive_getattr(gm, node.target)
        for node in gm.graph.nodes
        if node.op == "get_attr"
    }

    fake_mode = FakeTensorMode()
    fake_gm = deepcopy_to_fake_tensor(gm, fake_mode)

    # `_dynamo_source` field is not copied with deepcopy. Copy manually.
    for fake_node, node in zip_equal(fake_gm.graph.nodes, gm.graph.nodes):
        if source_info := getattr(node, "_dynamo_source", None):
            fake_node._dynamo_source = source_info

    targets_of_lifted_nodes = {}

    try:
        first_placeholder = next(
            iter(node for node in fake_gm.graph.nodes if node.op == "placeholder")
        )
    except StopIteration:
        first_placeholder = next(iter(fake_gm.graph.nodes))

    # Replace all get_attr nodes with placeholder nodes (lifting).
    for node in tuple(node for node in fake_gm.graph.nodes if node.op == "get_attr"):
        # Insert new placeholder nodes before the first placeholder node.
        with fake_gm.graph.inserting_before(first_placeholder):
            new_placeholder_node = fake_gm.graph.placeholder(node.target)

        assert node.name not in targets_of_lifted_nodes
        targets_of_lifted_nodes[node.name] = node.target

        node.replace_all_uses_with(new_placeholder_node)
        new_placeholder_node.meta = node.meta.copy()
        new_placeholder_node.meta["val"] = recursive_getattr(fake_gm, node.target)

        fake_gm.graph.erase_node(node)
        new_placeholder_node.name = node.name
        new_placeholder_node.target = node.target

    return fake_gm, constants, targets_of_lifted_nodes


def _check_gm_and_get_serializer(gm: GraphModule) -> GraphModuleSerializer:
    constant_not_scalar = False
    for node in gm.graph.nodes:
        if node.op != "get_attr":
            continue
        actual_tensor = recursive_getattr(gm, node.target)
        assert not isinstance(
            actual_tensor, FakeTensor
        ), "``GraphModule`` containing ``FakeTensor`` cannot be serialized"
        if len(actual_tensor.size()) > 0:
            # If constant is not a scalar tensor.
            constant_not_scalar = True
    if constant_not_scalar:
        logger.warning(
            "Tensor with size will be included in serialized graph. Serialized graph size might be large."
        )

    torch_version = get_torch_major_version()
    if torch_version == "2.1":
        serializer = GraphModuleSerializer(
            ExportGraphSignature([], [], [], [], {}, {}, {}, None), CallSpec(None, None), []  # type: ignore
        )
    elif torch_version in ("2.2", "2.4", "2.5"):
        serializer = GraphModuleSerializer(ExportGraphSignature([], []), [])  # type: ignore
    else:
        raise NotImplementedError(f"Unsupported torch version: {torch_version}")
    return serializer


def _convert_gm_into_dict_and_get_some_metadata(
    gm: GraphModule, include_node_metadata: bool = False
) -> Tuple[GraphModule, Dict[str, torch.Tensor], Dict, _GraphModuleMetadata]:
    """Returns: (GraphModule with get_attr nodes lifted, tensor_constants dict, FX graph converted into dict, GraphModule metadata without constant_saved_info)"""
    serializer = _check_gm_and_get_serializer(gm)
    gm, constants, getattr_node_to_target = _separate_constants_in_gm(gm)

    # Serialize graph.
    serialized_graph = serializer.serialize_graph(gm)
    graph_dict = _dataclass_to_dict(serialized_graph)

    # Some node names can be changed during serialization. So save original names.
    node_names = [node.name for node in gm.graph.nodes]

    if include_node_metadata:
        node_metas, node_dynamo_source_info = _get_metadata(gm)
    else:
        node_metas = node_dynamo_source_info = {}

    graphmodule_metadata = _GraphModuleMetadata(
        node_metas=node_metas,
        node_dynamo_source_info=node_dynamo_source_info,
        node_names=node_names,
        # NOTE: constant saved info will be added later.
        constant_saved_info=None,
        getattr_node_targets=getattr_node_to_target,
    )
    return gm, constants, graph_dict, graphmodule_metadata


def _serialize_tensors_to_str(constants: Mapping[str, torch.Tensor]) -> str:
    return base64.b64encode(serialize_tensors(constants)).decode()


def serialize_gm(
    gm: GraphModule,
    include_node_metadata: bool = False,
) -> str:
    gm, constants, graph_dict, graphmodule_metadata_wo_constant_saved_info = (
        _convert_gm_into_dict_and_get_some_metadata(gm, include_node_metadata=include_node_metadata)
    )

    # Serialize constant tensors.
    serialized_constants = _serialize_tensors_to_str(constants)
    constant_saved_info = _ConstantSavedInfo(
        param_files={},
        tensor_to_saved_file_id_and_saved_name={},
        blob=serialized_constants,
    )

    graphmodule_metadata_wo_constant_saved_info = (
        graphmodule_metadata_wo_constant_saved_info.with_constant_saved_info(constant_saved_info)
    )

    graph_dict[_METADATA_KEY] = graphmodule_metadata_wo_constant_saved_info.model_dump()

    ser_json = json.dumps(graph_dict, cls=EnumEncoder)

    return base64.b64encode(ser_json.encode("utf-8")).decode("utf-8")


OriginalName: TypeAlias = str
GraphName: TypeAlias = str


def _save_constants_and_get_constant_saved_info(
    gm: GraphModule,
    constants: Mapping[str, torch.Tensor],
    constant_tensor_path: Optional[Path],
    existing_param_file_metadata: Optional[ParamFileMetadata] = None,
) -> _ConstantSavedInfo:
    # Constants are named by their name in the graph.
    constants_to_save: Dict[GraphName, torch.Tensor] = dict(constants)
    original_to_graph_name: Dict[OriginalName, GraphName] = {}

    for node in gm.graph.nodes:
        if not is_weight_or_buffer(node):
            continue
        original_name = cast(OriginalName, get_original_name(node))
        assert isinstance(node.target, str)
        original_to_graph_name[original_name] = node.target

    param_files: Dict[str, ParamFileInfo] = {}
    graph_name_to_param_file_id_and_original_name: Dict[GraphName, Tuple[str, OriginalName]] = {}

    existing_tensors = []

    if existing_param_file_metadata:
        file_path_to_param_id: Dict[str, str] = {}

        for tensor_name, param_file_path in existing_param_file_metadata.tensor_to_filepath.items():
            if tensor_name not in original_to_graph_name:
                continue
            if param_file_path not in file_path_to_param_id:
                new_param_file_id = f"{_SHARED_PARAM_ID_PREFIX}_{len(file_path_to_param_id)}"
                file_path_to_param_id[param_file_path] = new_param_file_id

                param_file_info = ParamFileInfo(
                    param_file_path, existing_param_file_metadata.format
                )
                assert new_param_file_id not in param_files
                param_files[new_param_file_id] = param_file_info

            param_file_id = file_path_to_param_id[param_file_path]

            # exclude weights already saved in existing param file.
            name_in_graph = original_to_graph_name[tensor_name]
            constants_to_save.pop(name_in_graph)
            existing_tensors.append(tensor_name)
            graph_name_to_param_file_id_and_original_name[name_in_graph] = (
                param_file_id,
                tensor_name,
            )

    logger.info(
        f"{len(existing_tensors)} weights will not be saved for GraphModule caching, there's already param file containing them."
    )

    # Save constant tensors that are not in param files referenced by `param_file_metadata`.
    blob = None
    if constants_to_save:
        if constant_tensor_path:
            assert _OWNED_PARAM_ID not in param_files
            param_files[_OWNED_PARAM_ID] = ParamFileInfo(
                constant_tensor_path.as_posix(), ParamfileFormat.SAFETENSORS
            )

            for constant_name in constants_to_save:
                graph_name_to_param_file_id_and_original_name[constant_name] = (
                    _OWNED_PARAM_ID,
                    constant_name,
                )

            # If `constant_tensor_path` is given, save constant tensors to separate file and Add information about constant file path.
            write_without_concurrency_issue(
                constants_to_save,
                constant_tensor_path,
            )
        else:
            # If `constant_tensor_path` is not given, serialize constants and bundle it with the graph.
            blob = _serialize_tensors_to_str(constants_to_save)
    return _ConstantSavedInfo(param_files, graph_name_to_param_file_id_and_original_name, blob=blob)


def save_gm(
    gm: GraphModule,
    path: Path,
    constant_tensor_path: Optional[Path],
    include_node_metadata: bool = False,
    existing_param_file_metadata: Optional[ParamFileMetadata] = None,
) -> None:
    gm, constants, serialized_graph, graphmodule_metadata_wo_constant_saved_info = (
        _convert_gm_into_dict_and_get_some_metadata(gm, include_node_metadata=include_node_metadata)
    )
    constant_saved_info = _save_constants_and_get_constant_saved_info(
        gm, constants, constant_tensor_path, existing_param_file_metadata
    )
    graphmodule_metadata = graphmodule_metadata_wo_constant_saved_info.with_constant_saved_info(
        constant_saved_info
    )
    serialized_graph[_METADATA_KEY] = graphmodule_metadata.model_dump()

    ser_json = json.dumps(serialized_graph, cls=EnumEncoder)
    serialized = base64.b64encode(ser_json.encode("utf-8"))
    write_without_concurrency_issue(serialized, path)


def load_gm(
    path: Union[str, os.PathLike],
    fill_tensor_meta: bool,
) -> GraphModule:
    with open(path, "r") as f:
        return deserialize_gm(f.read(), fill_tensor_meta=fill_tensor_meta)


def deserialize_gm(json_program: str, fill_tensor_meta: bool = True) -> GraphModule:
    json_program = base64.decodebytes(json_program.encode("utf-8")).decode("utf-8")
    graph = json.loads(json_program)

    graphmodule_metadata = _GraphModuleMetadata.model_validate(graph.pop(_METADATA_KEY))
    serialized_graph = _dict_to_dataclass(Graph, graph)
    assert isinstance(serialized_graph, Graph)

    gm_serializer = GraphModuleDeserializer()
    gm_serializer.shape_env = symbolic_shapes.ShapeEnv(assume_static_by_default=True)

    torch_version = get_torch_major_version()
    if torch_version == "2.1":
        fake_tensor_mode = FakeTensorMode(shape_env=gm_serializer.shape_env)  # type: ignore
    elif torch_version == "2.2":
        fake_tensor_mode = FakeTensorMode(
            shape_env=gm_serializer.shape_env, static_shapes=True  # type: ignore
        )
    elif torch_version in ("2.4", "2.5"):
        fake_tensor_mode = FakeTensorMode(
            shape_env=gm_serializer.shape_env,
            allow_fallback_kernels=False,
            allow_non_fake_inputs=True,
        )
    else:
        raise NotImplementedError(f"Unsupported torch version: {torch_version}")

    gm_serializer.fake_tensor_mode = fake_tensor_mode
    gm_serializer.symbol_name_to_symbol = {}
    gm_serializer.symbol_name_to_range = {}
    gm_serializer.deserialize_graph(serialized_graph)

    # Update node names if information exists.
    for node, original_name in zip_equal(
        gm_serializer.graph.nodes, graphmodule_metadata.node_names
    ):
        assert isinstance(node, Node)
        node.name = original_name

    # Update metadata if serialized node metadata exists.
    if graphmodule_metadata.node_metas:
        for node in gm_serializer.graph.nodes:
            node.meta.update(
                graphmodule_metadata.node_metas[node.name].model_dump(exclude_none=True)
            )

    # If constant tensor path exists, load constant tensors from the file and replace dummy parameter/buffers of the model with them.
    constant_tensor_saved_info = graphmodule_metadata.constant_saved_info
    assert isinstance(constant_tensor_saved_info, _ConstantSavedInfo)

    # Get constant tensors from referenced param files.
    opened_file_cache = {}
    for tensor_name, (
        constant_file_id,
        saved_name,
    ) in constant_tensor_saved_info.tensor_to_saved_file_id_and_saved_name.items():
        param_file_info = constant_tensor_saved_info.param_files[constant_file_id]
        if param_file_info.format != ParamfileFormat.SAFETENSORS:
            raise NotImplementedError
        param_file_info_path = get_path_via_hot_cache(param_file_info.path)
        if param_file_info_path not in opened_file_cache:
            logger.info(f"[CACHE] Accessing {param_file_info_path}")
            opened_file_cache[param_file_info_path] = safe_open(
                param_file_info_path, framework="pt", device="cpu"
            )
        file_ptr = opened_file_cache[param_file_info_path]

        val = get_tensor_with_safetensors_fp(file_ptr, saved_name)  # type: ignore
        # NOTE: Information about whether the constant was buffer or parameter is gone here. Is this okay..?
        setattr(gm_serializer.module, tensor_name, val)

    del opened_file_cache

    # Get self-containing constant tensors.
    if constant_tensor_saved_info.blob:
        constants = deserialize_tensors(
            base64.decodebytes(constant_tensor_saved_info.blob.encode())
        )
        for k, v in constants.items():
            if hasattr(gm_serializer.module, k):
                raise ValueError("This field already exists.")
            setattr(gm_serializer.module, k, v)

    getattr_node_targets = dict(graphmodule_metadata.getattr_node_targets)
    for node in gm_serializer.graph.nodes:
        assert node.op == "placeholder"
        constant_name = getattr_node_targets.pop(node.name, None)
        if not constant_name:
            assert not getattr_node_targets
            break
        with gm_serializer.graph.inserting_before(node):
            get_attr_node = gm_serializer.graph.get_attr(constant_name)
        node.replace_all_uses_with(get_attr_node)
        gm_serializer.graph.erase_node(node)
        get_attr_node.name = node.name
        get_attr_node.meta = node.meta.copy()

    # Update _dynamo_source info if exists
    dynamo_source_info = graphmodule_metadata.node_dynamo_source_info
    if dynamo_source_info:
        placeholder_nodes = [node for node in gm_serializer.graph.nodes if node.op == "placeholder"]
        assert len(placeholder_nodes) == len(dynamo_source_info)

        for node in placeholder_nodes:
            source_info = dynamo_source_info[node.name]
            node._dynamo_source = _dynamo_source_dict_to_class(Source, source_info)

    gm = GraphModule(gm_serializer.module, gm_serializer.graph)

    if fill_tensor_meta:
        fill_tensor_meta_from_val_meta(gm)

    return gm
