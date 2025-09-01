import json
import logging
import tempfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import ConfigDict, Field, field_validator

from ..core import DEPRECATED_CAPABILITY_IMPLEMENTATION_FILE, GQLBaseModel
from .aws_s3 import upload_file_to_s3
from .gql_client import HLClient
from .io import download_bytes

logger = logging.getLogger(__name__)

__all__ = [
    "TrainingRunArtefactTypeEnum",
    "TrainingRunArtefactType",
    "TrainingRunType",
    "get_training_run_artefacts",
    "get_training_run_artefact",
    "get_latest_training_run_artefact",
    "get_capability_implementation_file_url",
    "create_training_run_artefact",
]


def _get_now_str():
    return datetime.now().isoformat()


class TrainingRunArtefactTypeEnum(str, Enum):
    OnnxOpset11 = "OnnxOpset11"
    OnnxOpset14 = "OnnxOpset14"
    TorchScriptV1 = "TorchScriptV1"
    TensorFlowV1 = "TensorFlowV1"
    DeprecatedMmpond = "DeprecatedMmpond"
    DeprecatedClassilvier = "DeprecatedClassilvier"
    DeprecatedSilverclassify = "DeprecatedSilverclassify"
    OnnxRuntimeAmd64 = "OnnxRuntimeAmd64"
    OnnxRuntimeArm = "OnnxRuntimeArm"
    DeprecatedCapabilityImplementationFile = DEPRECATED_CAPABILITY_IMPLEMENTATION_FILE
    TextEmbedder = "TextEmbedder"


class TrainingRunArtefactType(GQLBaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[str] = None
    file_url: str
    type: TrainingRunArtefactTypeEnum
    updated_at: Optional[str] = Field(default_factory=_get_now_str)
    inference_config: Dict = {}  # Graphql expects at least an empty dict not None
    training_config: Dict = {}  # Graphql expects at least an empty dict not None
    supporting_files: Dict = {}  # Graphql expects at least an empty dict not None

    @field_validator("inference_config", "training_config", "supporting_files", mode="before")
    @classmethod
    def none_to_empty_dict(cls, v):
        if v is None:
            return {}
        return v

    @classmethod
    def from_yaml(cls, path: Union[Path, str]):
        path = Path(path)
        with path.open("r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def dump_yaml(self, path: Union[Path, str]):
        path = Path(path)
        with path.open("w") as f:
            yaml.dump(self.model_dump(), f)

    def create(self, client: HLClient, training_run_id: int):
        """Create and upload a training run artefact to Highlighter.

        This method handles the complete workflow of artefact creation including:
        - Uploading the artefact file to S3
        - Creating the artefact record in Highlighter via GraphQL
        - Setting up the associated capability for inference

        Args:
            client: Authenticated HLClient instance for GraphQL operations
            training_run_id: ID of the training run to associate this artefact with

        Returns:
            The created training run artefact with assigned ID

        Raises:
            Exception: If artefact creation fails or returns errors
        """
        from .capabilities import create_capability_for_artefact

        artefact_file_data = upload_file_to_s3(
            client,
            self.file_url,
            mimetype="application/octet-stream",
        )
        logger.info(f"Created file in s3:\n{artefact_file_data}")

        class _TrainingRunArtefactType(GQLBaseModel):
            id: str

        class CreateTrainingRunPayload(GQLBaseModel):
            errors: List[str]
            training_run_artefact: Optional[_TrainingRunArtefactType] = None

        artefact_result = client.createTrainingRunArtefact(
            return_type=CreateTrainingRunPayload,
            trainingRunId=training_run_id,
            type=self.type,
            fileData=artefact_file_data,
            inferenceConfig=self.inference_config,
            trainingConfig=self.training_config,
        )
        logger.info(f"create artefact result: {artefact_result}")

        create_capability_for_artefact(
            client=client,
            artefact_id=artefact_result.training_run_artefact.id,
            training_run_id=training_run_id,
            inference_config=self.inference_config,
        )
        return artefact_result.training_run_artefact


class TrainingRunType(GQLBaseModel):
    model_config = ConfigDict(use_enum_values=True, protected_namespaces=())

    id: int
    name: str
    updated_at: str
    model_implementation_file_url: Optional[str] = None
    training_logs_file_url: Optional[str] = None
    training_run_artefacts: List[TrainingRunArtefactType] = []
    training_config: Optional[Any] = None


def _download_training_run_artefact(
    training_run_artefact: TrainingRunArtefactType,
    file_url_save_path: Optional[str] = None,
):
    if file_url_save_path is None:
        file_url_save_path = f"{tempfile.mkdtemp()}/{training_run_artefact.id}"

    download_bytes(training_run_artefact.file_url, Path(file_url_save_path))

    training_run_artefact.file_url = str(file_url_save_path)
    return training_run_artefact


def get_training_run_artefacts(
    hl_client: HLClient,
    training_run_id: int,
    filter_by_artefact_type: Optional[Union[str, TrainingRunArtefactTypeEnum]] = None,
) -> List[TrainingRunArtefactType]:
    """Return a list of artefacts for a training run
    sorted newest to oldest according to TrainingRunArtefactType.updated_at

    If `filter_by_artefact_type` is set then will only retrun artefacts with
    matching TrainingRunArtefactType.type
    """

    training_run: TrainingRunType = hl_client.trainingRun(
        return_type=TrainingRunType,
        id=training_run_id,
    )

    if training_run.model_implementation_file_url is not None:
        # If TrainingRun.updated_at is None then we set it to
        # datetime.min for the purposes of sorting.
        capability_implementation_file_artefact: TrainingRunArtefactType
        capability_implementation_file_artefact = TrainingRunArtefactType(
            id=None,
            file_url=training_run.model_implementation_file_url,
            type=TrainingRunArtefactTypeEnum.DeprecatedCapabilityImplementationFile,
            updated_at=datetime.min.isoformat() if training_run.updated_at else training_run.updated_at,
            inference_config={},
            training_config={},
            supporting_files={},
        )
        training_run.training_run_artefacts.append(capability_implementation_file_artefact)

    if filter_by_artefact_type is not None:
        artefact_type = TrainingRunArtefactTypeEnum(filter_by_artefact_type)
        training_run.training_run_artefacts = [
            a for a in training_run.training_run_artefacts if a.type == artefact_type
        ]

    return sorted(training_run.training_run_artefacts, key=lambda x: x.updated_at, reverse=True)


def get_training_run_artefact(
    hl_client: HLClient,
    training_run_artefact_id: str,
    download_file_url: bool = False,
    file_url_save_path: Optional[str] = None,
) -> TrainingRunArtefactType:
    """Get the TrainingRunArtefact object for a given training_run_artefact_id.

    If `download_file_url` is `True` then download either to a temporary
    directory or `file_url_save_path`. Once downloaded TrainingRunArtefact.file_url
    will be updated to the location where is has been downloaded to.
    """

    training_run_artefact: TrainingRunArtefactType
    training_run_artefact = hl_client.trainingRunArtefact(
        return_type=TrainingRunArtefactType, id=training_run_artefact_id
    )

    if download_file_url:
        training_run_artefact = _download_training_run_artefact(
            training_run_artefact, file_url_save_path=file_url_save_path
        )

    return training_run_artefact


def get_latest_training_run_artefact(
    hl_client: HLClient,
    training_run_id: int,
    download_file_url: bool = False,
    file_url_save_path: Optional[str] = None,
    filter_by_artefact_type: Optional[Union[str, TrainingRunArtefactTypeEnum]] = None,
) -> Optional[TrainingRunArtefactType]:
    """Get the TrainingRunArtefact with the most recent updated_at value.

    If `download_file_url` is `True` then download either to a temporary
    directory or `file_url_save_path`. Once downloaded TrainingRunArtefact.file_url
    will be updated to the location where is has been downloaded to.
    """
    training_run_artefacts: List[TrainingRunArtefactType] = get_training_run_artefacts(
        hl_client, training_run_id, filter_by_artefact_type=filter_by_artefact_type
    )

    if len(training_run_artefacts) == 0:
        return None
    training_run_artefact: TrainingRunArtefactType = training_run_artefacts[0]

    if download_file_url:
        abs_file_url_save_path = str(Path(file_url_save_path).absolute())
        training_run_artefact = _download_training_run_artefact(
            training_run_artefact, file_url_save_path=abs_file_url_save_path
        )

    return training_run_artefact


def get_capability_implementation_file_url(
    hl_client: HLClient,
    training_run_id: int,
) -> Optional[str]:
    result: TrainingRunType = hl_client.trainingRun(
        return_type=TrainingRunType,
        id=training_run_id,
    )
    return result.model_implementation_file_url


def create_training_run_artefact(
    hl_client: HLClient,
    training_run_id: int,
    artefact_path: str,
    training_run_artefact_type: TrainingRunArtefactTypeEnum,
    checkpoint_name: str,
    training_config: Union[Path, str, Dict],
    inference_config: Union[Path, str, Dict],
) -> TrainingRunArtefactType:
    if not isinstance(training_config, dict):
        training_config_path = Path(training_config)
        with training_config_path.open("r") as f:
            training_config = {
                training_config_path.name: f.read(),
            }

    if not isinstance(inference_config, dict):
        inference_config_path = Path(inference_config)
        with inference_config_path.open("r") as f:
            loaders = {
                ".yaml": yaml.safe_load,
                ".yml": yaml.safe_load,
                ".json": json.load,
            }

            inference_config = loaders[inference_config_path.suffix](f)

    artefact_file_data = upload_file_to_s3(
        hl_client,
        artefact_path,
    )
    print(f"Created file in s3:\n{artefact_file_data}")

    class CreateTrainingRunPayload(GQLBaseModel):
        errors: List[str]
        training_run_artefact: Optional[TrainingRunArtefactType] = None

    result = hl_client.createTrainingRunArtefact(
        return_type=CreateTrainingRunPayload,
        trainingRunId=training_run_id,
        type=training_run_artefact_type,
        checkpoint=checkpoint_name,
        fileData=artefact_file_data,
        inferenceConfig=inference_config,
        trainingConfig=training_config,
    )
    if result.errors:
        raise ValueError(f"{result.errors}")

    return result.training_run_artefact
