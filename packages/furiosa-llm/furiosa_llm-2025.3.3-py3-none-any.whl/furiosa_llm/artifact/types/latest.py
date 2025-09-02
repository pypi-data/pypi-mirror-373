import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, RootModel
from typing_extensions import Self

from furiosa_llm.models.metadata import LLMConfig, ModelMetadata

from ...models.config_types import (
    GeneratorConfig,
    ModelRewritingConfig,
    ParallelConfig,
    PipelineMetadata,
)
from .commons import ArtifactBase, SchemaVersion

logger = logging.getLogger(__name__)


SCHEMA_VERSION = SchemaVersion(major=2, minor=0)


class ArtifactMetadata(BaseModel):
    artifact_id: str
    name: str
    timestamp: int
    furiosa_llm_version: str
    furiosa_compiler_version: str


class ModelMetadataForArtifact(ModelMetadata):
    """
    Child class of ModelMetadata used for loading artifacts.
    The object doesn't cause any huggingface config / weight download
    for obtaining all configs needed for artifact loading.
    """

    config_: Optional[Dict[str, Any]] = None
    model_qname_: Optional[str] = None

    def __init__(
        self,
        pretrained_id: str,
        task_type: Optional[str] = None,
        llm_config: LLMConfig = LLMConfig(),
        hf_configs: Dict = {},
        model_weight_path: Optional[os.PathLike] = None,
        trust_remote_code: Optional[bool] = None,
        allow_bfloat16_cast_with_mcp: bool = True,
        config_: Optional[Dict[str, Any]] = None,
        model_qname_: Optional[str] = None,
        auto_bfloat16_cast: Optional[bool] = None,
    ):
        super(ModelMetadataForArtifact, self).__init__(
            pretrained_id,
            task_type,
            llm_config,
            hf_configs,
            model_weight_path,
            trust_remote_code,
            allow_bfloat16_cast_with_mcp,
            auto_bfloat16_cast,
        )
        self.config_ = config_
        self.model_qname_ = model_qname_

    @classmethod
    def from_metadata(
        cls,
        model_metadata: ModelMetadata,
        config: Optional[Dict[str, Any]] = None,
        model_qname: Optional[str] = None,
    ) -> Self:
        return cls(
            **model_metadata.model_dump(),
            config_=config,
            model_qname_=model_qname,
        )

    @property
    def config_dict(self) -> Dict[str, Any]:
        if self.config_ is None:
            return super().config_dict
        return self.config_

    @property
    def model_qname(self) -> str:
        if self.model_qname_ is None:
            return super().model_qname
        return self.model_qname_


class ModelArtifact(BaseModel):
    generator_config: GeneratorConfig
    hf_config: Dict[str, Any]
    model_metadata: ModelMetadata
    model_rewriting_config: ModelRewritingConfig
    parallel_config: ParallelConfig

    pipelines: List[Dict[str, Any]] = []
    pipeline_metadata_list: List[PipelineMetadata]

    # TODO: store this field somewhere else.
    max_prompt_len: Optional[int]

    def append_pipeline(self, pipeline_dict: Dict[str, Any]):
        self.pipelines.append(pipeline_dict)


class Artifact(ArtifactBase):
    metadata: ArtifactMetadata
    model: ModelArtifact
    speculative_model: Optional[ModelArtifact] = None
    version: SchemaVersion

    # TODO : `prefill_chunk_size` will be moved to `GeneratorConfig` later
    prefill_chunk_size: Optional[int] = None

    def export(self, path: Union[str, os.PathLike]):
        with open(path, "w") as f:
            f.write(RootModel[Artifact](self).model_dump_json(indent=2))

    @classmethod
    def from_previous_version(cls, _previous_version_artifact) -> Self:
        raise ValueError(
            "There's no previous version artifact that can be converted into this version of artifact."
        )

    @classmethod
    def load(cls, path: Union[str, os.PathLike]) -> "Artifact":

        with open(path) as f:
            artifact_data: Dict[str, Any] = json.load(f)

        artifact_schema_version = artifact_data.get("version")
        if not artifact_schema_version:
            raise ValueError(
                "Invalid or incompatible version of artifact: schema version doesn't exist."
            )
        try:
            return convert_to_latest_version(artifact_data)
        except Exception as e:
            logger.error(e)
            raise ValueError("Artifact schema mismatched.")


# Map for major schema version to corresponding Artifact type
SCHEMA_MAJOR_VERSION_MAPPING = {2: Artifact}


def convert_to_latest_version(old_artifact_data: Dict[str, Any]) -> Artifact:
    artifact_schema_major_version = old_artifact_data.get("version", {}).get("major", 0)
    assert type(artifact_schema_major_version) is int
    if artifact_schema_major_version not in SCHEMA_MAJOR_VERSION_MAPPING:
        raise ValueError(
            f"Artifact of version {artifact_schema_major_version}.x is not supported anymore. Please use more recent version."
        )

    old_version_artifact_cls = SCHEMA_MAJOR_VERSION_MAPPING[artifact_schema_major_version]
    old_artifact = old_version_artifact_cls(**old_artifact_data)

    current_converting_version: int = artifact_schema_major_version
    converted_artifact = old_artifact
    while not isinstance(converted_artifact, Artifact):
        current_converting_version += 1
        converted_artifact = SCHEMA_MAJOR_VERSION_MAPPING[current_converting_version].from_previous_version(converted_artifact)  # type: ignore[attr-defined]
    return converted_artifact
