from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path
import shutil
from time import time
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union
import uuid

from huggingface_hub import split_torch_state_dict_into_shards
from safetensors import safe_open
from safetensors.torch import _find_shared_tensors
from safetensors.torch import load as sf_torch_load
from safetensors.torch import save as sf_torch_save
from safetensors.torch import save_file
import torch
from typing_extensions import Self

_INDEX_TENSOR_NAME = "model.safetensors.index.json"


def _tensors_with_same_storage_and_length(tensor1: torch.Tensor, tensor2: torch.Tensor) -> bool:
    return (
        tensor1.data_ptr() == tensor2.data_ptr()
        and tensor1.nelement() == tensor2.nelement()
        and tensor1.dtype == tensor2.dtype
    )


def _preprocess_for_safetensors(
    tensors: Mapping[str, torch.Tensor],
) -> Tuple[Dict[str, torch.Tensor], Dict[str, str]]:
    tensors_ = dict(tensors)

    contigous_tensor_cache = {}

    # This is needed because `_find_shared_tensors` calls `view(-1)` to get tensor's address range.
    # TODO: find way to check overlapping tensors without making it contiguous.
    for name, tensor in tensors_.items():
        try:
            tensor.view(-1)
        except RuntimeError:
            if id(tensor) not in contigous_tensor_cache:
                contigous_tensor_cache[id(tensor)] = tensor.contiguous()

            tensors_[name] = contigous_tensor_cache[id(tensor)]

    shared_pointers = _find_shared_tensors(tensors_)

    # This is a workaround for shared tensors in model dict. (`Link shared tensor <https://huggingface.co/docs/safetensors/en/torch_shared_tensors>`_).
    # ``save_model`` API can save shared tensors, but individual shared tensor cannot be loaded from it because only one of shared tensors
    # covering the entire buffer are stored. Even if there is a mapping between excluded tensors to stored one, this is not
    # sufficient because it doesn't include which part of the stored one is excluded one. So, we now restrict all shared tensors to have
    # exactly same data ptr and length, and this can cover most of the cases we are interested in.
    metadata = {}

    for names in shared_pointers:
        if len(names) > 1:
            names_ = list(names)
            # To enforce same representative tensor across executions.
            names_.sort()
            for name in names_[1:]:
                # TODO: find a way to handle shared tensors that are not exactly same.
                if not _tensors_with_same_storage_and_length(tensors[name], tensors[names_[0]]):
                    raise RuntimeError(
                        "Shared tensors that are not exactly same cannot be saved right now"
                    )
                # save mapping info for excluded one to stored one.
                metadata[name] = names_[0]
                del tensors_[name]

    # Make all tensors contiguous before saving.
    return {k: v.contiguous() for k, v in tensors_.items()}, metadata


class ParamfileFormat(str, Enum):
    SAFETENSORS = "safetensors"
    TORCHSAVE = "torch.save"
    TORCHEXPORT = "torch.export"

    @classmethod
    def from_str(cls, val: str) -> "ParamfileFormat":
        if val == "safetensors":
            return cls.SAFETENSORS
        elif val == "torch.save":
            return cls.TORCHSAVE
        elif val == "torch.export":
            return cls.TORCHEXPORT
        else:
            raise ValueError(f"Invalid param save format {val}")


def serialize_tensors(
    tensors: Mapping[str, torch.Tensor],
    format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
) -> bytes:
    if format is ParamfileFormat.SAFETENSORS:
        # Safetensors doesn't provide function for deserializing metadata with tensors.
        # So we just tensors with same storages duplicately. For efficient saving without duplication, use save_tensors.

        # tensors, metadata = _preprocess_for_safetensors(tensors)
        return sf_torch_save({k: v.contiguous() for k, v in tensors.items()})
    else:
        raise NotImplementedError(f"param save format {format} is not supported yet")


def deserialize_tensors(
    data: bytes,
    format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
) -> Dict[str, torch.Tensor]:
    if format is ParamfileFormat.SAFETENSORS:
        return sf_torch_load(data)
    else:
        raise NotImplementedError(f"param save format {format} is not supported yet")


def _save_tensors(
    tensors: Mapping[str, torch.Tensor],
    path: Union[str, os.PathLike],
    format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
) -> None:
    if format is ParamfileFormat.SAFETENSORS:
        tensors, metadata = _preprocess_for_safetensors(tensors)
        save_file(dict(tensors), path, metadata)
    else:
        raise NotImplementedError(f"param save format {format} is not supported yet")


def write_without_concurrency_issue(
    data: Union[str, bytes, Dict[str, torch.Tensor]],
    path: Union[str, os.PathLike],
    tensor_save_format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
) -> None:
    path = Path(path)
    # Write to temp file and move it when it's done.
    while True:
        try:
            tmp_filename = f"{path.name}-{time()}.tmp"
            if isinstance(data, str):
                with open(path.parent / tmp_filename, "x") as f:
                    f.write(data)
            elif isinstance(data, bytes):
                with open(path.parent / tmp_filename, "xb") as f:
                    f.write(data)
            else:
                save_tensors(data, path.parent / tmp_filename, tensor_save_format)
            break
        except FileExistsError:
            # Other process might tries to save to same tmp file. In this case, try again with other time suffix.
            pass
    os.replace(path.parent / tmp_filename, path)


class ParamFileMetadata:
    base_path: str
    is_single_file: bool
    filename_to_tensors: Dict[str, List[str]]
    tensor_to_filename: Dict[str, str]
    metadata: Dict[str, Any]

    format: ParamfileFormat = ParamfileFormat.SAFETENSORS

    def __init__(
        self,
        base_path: Union[str, os.PathLike],
        is_single_file: bool,
        tensor_to_filename: Dict[str, str],
        metadata: Dict[str, Any],
    ) -> None:
        self.base_path = os.fspath(base_path)
        self.is_single_file = is_single_file
        self.tensor_to_filename = tensor_to_filename
        self.filename_to_tensors = {}
        for tensor_name, fname in tensor_to_filename.items():
            self.filename_to_tensors.setdefault(fname, []).append(tensor_name)
        self.metadata = metadata

    def __post_init__(self):
        tensor_names_per_filenames = [
            tensor_names for tensor_names in self.filename_to_tensors.values()
        ]
        if sum(len(tensor_names) for tensor_names in tensor_names_per_filenames) != len(
            set(
                tensor_name
                for tensor_names in tensor_names_per_filenames
                for tensor_name in tensor_names
            )
        ):
            raise ValueError("Some tensors are saved in multiple files.")

    @property
    def filepath_to_tensors(self) -> Dict[str, List[str]]:
        if self.is_single_file:
            return {self.base_path: list(self.tensor_to_filename.keys())}
        return {
            os.path.join(self.base_path, fname): list(tensor_names)
            for fname, tensor_names in self.filename_to_tensors.items()
        }

    @property
    def tensor_to_filepath(self) -> Dict[str, str]:
        if self.is_single_file:
            return {tensor_name: self.base_path for tensor_name in self.tensor_to_filename.keys()}
        return {
            tensor_name: os.path.join(self.base_path, fname)
            for tensor_name, fname in self.tensor_to_filename.items()
        }

    @classmethod
    def load(
        cls,
        path: Union[str, os.PathLike],
        saved_format: ParamfileFormat = ParamfileFormat.SAFETENSORS,
    ) -> Self:
        if saved_format is ParamfileFormat.SAFETENSORS:
            file_ext = ".safetensors"
        else:
            raise NotImplementedError(f"Save format {saved_format} is not supported yet.")

        metadata = {}
        if os.path.isfile(path):
            # Consist of single file.
            path = os.fspath(path)
            is_single_file = True

            tensor_names = get_saved_param_names(ParamFileInfo(path, saved_format))
            tensor_to_filename = {tensor_name: "base" for tensor_name in tensor_names}
        elif os.path.isdir(path):
            is_single_file = False
            if os.path.exists(Path(path) / _INDEX_TENSOR_NAME):
                # index file exists. get information from it.
                with open(Path(path) / _INDEX_TENSOR_NAME, "r") as f:
                    index_file = json.load(f)
                tensor_to_filename = index_file["weight_map"]
                metadata = index_file["metadata"]
            else:
                # Index file does not exist. Read all param files in the directory.
                tensor_to_filename = {}
                for filename in os.listdir(path):
                    if not filename.endswith(file_ext):
                        continue
                    abs_file_path = os.fspath(os.path.join(path, filename))
                    tensor_names = get_saved_param_names(ParamFileInfo(abs_file_path, saved_format))
                    for tensor_name in tensor_names:
                        assert (
                            tensor_name not in tensor_to_filename
                        ), f"Duplicate tensor name {tensor_name} found in {filename}"
                        tensor_to_filename[tensor_name] = filename
        else:
            raise FileNotFoundError(f"Invalid path: {path}")

        return cls(
            base_path=os.fspath(path),
            is_single_file=is_single_file,
            tensor_to_filename=tensor_to_filename,
            metadata=metadata,
        )

    def get_param_files(self) -> List[str]:
        return list(self.filepath_to_tensors.keys())

    def get_saved_param_names(self) -> List[str]:
        return list(self.tensor_to_filepath.keys())

    def get_saved_param_file(self, tensor_name: str) -> Optional[str]:
        if filename := self.tensor_to_filepath.get(tensor_name):
            return os.path.join(self.base_path, filename)
        return None

    def save(
        self,
        tensors_to_save: Mapping[str, torch.Tensor],
        path: Union[str, os.PathLike],
    ) -> None:
        if not os.path.isdir(path):
            raise ValueError(f"`root_dir` must be a directory: {path}")

        # Save index file.
        index_file = {
            "weight_map": self.tensor_to_filename,
            "metadata": self.metadata,
        }
        with open(Path(path) / _INDEX_TENSOR_NAME, "x") as f:
            json.dump(index_file, f)

        # Save parameters.
        for fname, tensor_names in self.filepath_to_tensors.items():
            cur_tensors_to_save = {
                tensor_name: tensors_to_save[tensor_name] for tensor_name in tensor_names
            }

            save_tensors(
                cur_tensors_to_save,
                fname,
                format=self.format,
            )

    def load_tensors(
        self,
    ) -> Dict[str, torch.Tensor]:
        """
        Load tensors from the saved files.
        """
        tensors: Dict[str, torch.Tensor] = {}
        for fname in self.get_param_files():
            file_path = os.path.join(self.base_path, fname)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist.")
            tensors.update(load_tensors(file_path, format=self.format))
        return tensors

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParamFileMetadata):
            return False
        return (
            self.base_path == other.base_path
            and self.is_single_file == other.is_single_file
            and self.tensor_to_filename == other.tensor_to_filename
            and self.metadata == other.metadata
            and self.format == other.format
        )


def save_tensors(
    tensors: Mapping[str, torch.Tensor],
    path: Union[str, os.PathLike],
    format: str = "safetensors",
    max_shard_size: Optional[Union[int, str]] = None,
) -> ParamFileMetadata:
    if format != "safetensors":
        raise NotImplementedError(f"Unsupported param save format {format}")
    if max_shard_size is None:
        _save_tensors(tensors, path, ParamfileFormat.from_str(format))
        return ParamFileMetadata.load(path)

    # If `max_shard_size` is specified, split the tensors into multiple files with size <= max_shard_size.
    state_dict_split = split_torch_state_dict_into_shards(
        dict(tensors), max_shard_size=max_shard_size
    )

    filename_to_tensors = {
        filename: tensor_names
        for filename, tensor_names in state_dict_split.filename_to_tensors.items()
    }
    metadata = state_dict_split.metadata

    tmp_dir_path = Path(path).parent / f"{Path(path).name}-{uuid.uuid4().__str__()}.tmp"
    assert not tmp_dir_path.exists(), f"Temporary directory {tmp_dir_path} already exists."

    try:
        os.makedirs(tmp_dir_path)

        # Save into temporary directory first and then move it to the original path
        # to avoid concurrency issues.
        param_file_metadata = ParamFileMetadata(
            base_path=os.fspath(tmp_dir_path),
            is_single_file=False,
            tensor_to_filename={
                tensor_name: fname
                for fname, tensor_names in filename_to_tensors.items()
                for tensor_name in tensor_names
            },
            metadata=metadata,
        )

        # Write tensor and metadata.
        param_file_metadata.save(tensors, tmp_dir_path)

        # Update param file metadata and move to original path
        param_file_metadata.base_path = os.fspath(path)

        try:
            os.replace(tmp_dir_path, path)
        except OSError:
            # If the path already exists, we cannot replace it. In this case,
            # we convert this error to FileExistsError to notify the caller
            # that the file already exists.
            raise FileExistsError(f"File {path} already exists. Cannot replace it.")
    finally:
        # Clean up temporary directory.
        shutil.rmtree(tmp_dir_path, ignore_errors=True)

    return param_file_metadata


def save_model(
    model: torch.nn.Module,
    path: Union[str, os.PathLike],
    format: str = "safetensors",
    max_shard_size: Optional[Union[int, str]] = None,
) -> ParamFileMetadata:
    merged_tensors = model.state_dict() | dict(model.named_buffers())
    return save_tensors(
        merged_tensors,
        path,
        format=format,
        max_shard_size=max_shard_size,
    )


def load_tensors(
    path: Union[os.PathLike, str], format: ParamfileFormat = ParamfileFormat.SAFETENSORS
) -> Dict[str, torch.Tensor]:
    tensors: Dict[str, torch.Tensor] = {}

    if format == ParamfileFormat.SAFETENSORS:
        # The example shows safe_open with 'with clause'; https://huggingface.co/docs/safetensors/index
        # It still causes 'error: "safe_open" has no attribute "__enter__"'. Why? for workaround, ignore it.
        with safe_open(path, framework="pt", device="cpu") as f:  # type: ignore
            for key in f.keys():
                tensors[key] = f.get_tensor(key)
            if metadata := f.metadata():
                for alias_name, saved_name in metadata.items():
                    # Add alias tensors.
                    tensors[alias_name] = tensors[saved_name]
        return tensors
    else:
        raise NotImplementedError(f"param save format {format} is not supported yet")


def get_tensor_with_safetensors_fp(f, tensor_name: str) -> torch.Tensor:
    if metadata := f.metadata():
        tensor_name = metadata.get(tensor_name, tensor_name)
    return f.get_tensor(tensor_name)


@dataclass
class ParamFileInfo:
    path: str
    format: ParamfileFormat

    def __hash__(self):
        return hash(json.dumps({"path": self.path, "format": self.format}))


def get_saved_param_names(param_info: ParamFileInfo) -> List[str]:
    if param_info.format is ParamfileFormat.SAFETENSORS:
        with safe_open(param_info.path, framework="pt", device="cpu") as f:  # type: ignore
            keys = list(f.keys())
            if metadata := f.metadata():
                keys += list(metadata.keys())
            return keys
    else:
        raise NotImplementedError(f"param saved format {param_info.format} is not supported yet")
