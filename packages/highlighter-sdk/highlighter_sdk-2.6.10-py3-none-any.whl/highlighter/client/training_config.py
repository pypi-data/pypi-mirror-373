import json
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional, Union
from uuid import UUID
from warnings import warn

import yaml
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator
from typing_extensions import Annotated

from ..core.gql_base_model import GQLBaseModel
from .gql_client import HLClient
from .training_runs import TrainingRunArtefactTypeEnum

__all__ = [
    "get_training_config",
    "EntityAttributeValueTypeEnum",
    "EntityAttributeValue",
    "EntityAttribute",
    "ModelOutputType",
    "ModelInputs",
    "ModelSchemaType",
    "DatasetType",
    "ArtefactInfo",
    "TaxonPart",
    "TrainingConfigType",
]


def validate_uuid(v, key):
    validated = None
    if isinstance(v, UUID):
        validated = str(v)
    else:
        try:
            UUID(v)
            validated = v
        except:
            msg = f"'{key}' must be valid UUID, got: {v}"
            raise ValueError(msg)
    return validated


class EntityAttributeValueTypeEnum(str, Enum):
    boolean = "boolean"
    enum = "enum"
    integer = "integer"
    decimal = "decimal"
    string = "string"
    geometry = "geometry"
    array = "array"


# Custom representer for the Enum
def enum_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.value)


yaml.SafeDumper.add_representer(EntityAttributeValueTypeEnum, enum_representer)


class TaxonPart(BaseModel, extra="forbid"):
    entity_attribute_enum_id: Optional[Union[UUID, str]] = None
    entity_attribute_enum_value: Optional[str] = None
    entity_attribute_id: Union[UUID, str]
    entity_attribute_name: str
    entity_attribute_value_type: Optional[EntityAttributeValueTypeEnum] = None

    @field_validator("entity_attribute_enum_id")
    @classmethod
    def validate_entity_attribute_enum_id(cls, v):
        if v is None:
            return True
        else:
            return str(validate_uuid(v, "entity_attribute_enum_id"))

    @field_validator("entity_attribute_id")
    @classmethod
    def validate_entity_attribute_id(cls, v):
        return str(validate_uuid(v, "entity_attribute_id"))

    @property
    def value_type(self):
        return self.entity_attribute_value_type


class ModelOutputType(BaseModel, extra="forbid"):
    head: int
    position: int
    conf_thresh: Annotated[float, Field(ge=0.0, lt=1.0)]
    taxon: List[TaxonPart]

    def _validate_one_taxon(self, property_name):
        if len(self.taxon) > 1:
            raise ValueError(
                f"Can only use ModelOutputType.{property_name} if there is a single taxa in self.taxon"
            )

    @property
    def entity_attribute_enum_value(self):
        self._validate_one_taxon("entity_attribute_enum_value")
        return self.taxon[0].entity_attribute_enum_value

    @property
    def entity_attribute_enum_id(self) -> Optional[Union[UUID, str]]:
        self._validate_one_taxon("entity_attribute_enum_id")
        return self.taxon[0].entity_attribute_enum_id

    @property
    def entity_attribute_id(self) -> Union[UUID, str]:
        self._validate_one_taxon("entity_attribute_id")
        return self.taxon[0].entity_attribute_id

    @property
    def entity_attribute_name(self) -> str:
        self._validate_one_taxon("entity_attribute_name")
        return self.taxon[0].entity_attribute_name

    @property
    def entity_attribute_value_type(self) -> Optional[EntityAttributeValueTypeEnum]:
        self._validate_one_taxon("entity_attribute_value_type")
        return self.taxon[0].entity_attribute_value_type


class EntityAttribute(BaseModel, extra="forbid"):
    entity_attribute_id: Union[UUID, str]
    entity_attribute_name: str

    @field_validator("entity_attribute_id")
    @classmethod
    def validate_entity_attribute_id(cls, v):
        return str(validate_uuid(v, "entity_attribute_id"))


class EntityAttributeValue(BaseModel, extra="forbid"):
    entity_attribute_enum_id: Optional[Union[UUID, str]] = None
    entity_attribute_enum_value: Optional[str] = None
    entity_attribute_id: Union[UUID, str]
    entity_attribute_name: str
    entity_attribute_value_type: EntityAttributeValueTypeEnum
    entity_attribute_value: Any = None

    @field_validator("entity_attribute_enum_id")
    @classmethod
    def validate_entity_attribute_enum_id(cls, v):
        if v is None:
            return v
        return str(validate_uuid(v, "entity_attribute_enum_id"))

    @field_validator("entity_attribute_id")
    @classmethod
    def validate_entity_attribute_id(cls, v):
        return str(validate_uuid(v, "entity_attribute_id"))

    @property
    def value_type(self):
        return self.entity_attribute_value_type

    @property
    def value(self):
        if self.value_type == EntityAttributeValueTypeEnum.enum:
            return self.entity_attribute_enum_id
        else:
            return self.entity_attribute_value


class ModelInputs(BaseModel, extra="forbid"):
    entity_attributes: List[EntityAttribute]
    filters: List[List[EntityAttributeValue]]


class ModelSchemaType(BaseModel, extra="forbid"):
    model_config = ConfigDict(protected_namespaces=())

    model_inputs: ModelInputs
    model_outputs: List[ModelOutputType]

    @field_validator("model_outputs")
    @classmethod
    def validate_model_output_positions(cls, model_outputs):
        if len(model_outputs) == 0:
            #####################################################################
            # ❗❗❗ Remove when all inference capabilities are using TrainingConfig
            # as oposed schema's tied up in ManifestV1
            #####################################################################
            return model_outputs

        model_outputs = sorted(model_outputs, key=lambda o: (o.head, o.position))
        if (model_outputs[0].position != 0) and (model_outputs[0].head != 0):
            raise ValueError("model_outputs ids must start at 0")

        num_heads = len(set([o.head for o in model_outputs]))
        for head_idx in range(num_heads):
            for pos_idx, o in enumerate([_o for _o in model_outputs if _o.head == head_idx]):
                if head_idx != o.head:
                    raise ValueError("model_output.head values must start at 0 and be contigious")
                if pos_idx != o.position:
                    raise ValueError("model_output.position values must start at 0 and be contigious")

        return model_outputs

    def get_input_select_attribute_ids(self) -> List[str]:
        return [str(i.entity_attribute_id) for i in self.model_inputs.entity_attributes]

    def get_input_filter_attribute_ids(self) -> List[str]:
        filter_attr_ids = []
        for input_filter in self.model_inputs.filters:
            filter_attr_ids.append([str(i.entity_attribute_id) for i in input_filter])
        return filter_attr_ids

    def get_input_filter_attribute_values(self) -> List[Any]:
        filter_values = []
        for input_filter in self.model_inputs.filters:
            filter_values.append([i.value for i in input_filter])

        filter_values = [v if len(v) > 0 else None for v in filter_values]
        return filter_values

    def get_head_model_outputs(self, head: int):
        model_outputs = [m for m in self.model_outputs if m.head == head]
        return model_outputs

    def get_head_output_attribute_ids(self, head: int) -> List[str]:
        head_model_outputs = self.get_head_model_outputs(head)
        return [str(m.entity_attribute_id) for m in head_model_outputs]

    def get_head_output_attribute_names(self, head: int) -> List[str]:
        head_model_outputs = self.get_head_model_outputs(head)
        return [str(m.entity_attribute_name) for m in head_model_outputs]

    def get_head_output_attribute_enum_ids(self, head: int) -> List[str]:
        head_model_outputs = self.get_head_model_outputs(head)
        return [str(m.entity_attribute_enum_id) for m in head_model_outputs]

    def get_head_output_attribute_enum_values(self, head: int) -> List[str]:
        head_model_outputs = self.get_head_model_outputs(head)
        return [str(m.entity_attribute_enum_value) for m in head_model_outputs]

    def get_head_output_value_type(self, head: int) -> Optional[EntityAttributeValueTypeEnum]:
        """Will return None if the entity_attribute_value_type is also None
        because it is an Optional parameter of ModelOutputType
        """
        head_model_outputs = self.get_head_model_outputs(head)
        head_output_value_types = {m.entity_attribute_value_type for m in head_model_outputs}
        assert len(head_output_value_types) == 1
        return head_output_value_types.pop()


def _validate_hash_signature_not_none(v, args) -> str:
    assert (
        v is not None
    ), f"dataset({args.data['id']}) hash_signature is None. This is likely becuase it has not been locked"
    return v


class DatasetType(BaseModel, extra="forbid"):
    id: int
    hash_signature: Annotated[str, BeforeValidator(_validate_hash_signature_not_none)]


class ArtefactInfo(GQLBaseModel):
    """camelCase dict keys are intended as these args will be passed to a graphql mutation"""

    type: TrainingRunArtefactTypeEnum
    training_run_id: int
    artefact_path: str
    checkpoint: str
    inference_config: Dict
    training_config: Dict

    def to_dict(self) -> dict:
        returnDict = self.model_dump()
        returnDict["type"] = str(self.type.name)
        return returnDict


class TrainingConfigType(BaseModel, extra="forbid"):
    # Configure the BaseModel to allow us to populate the BaseModel using
    # alias or the name
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    base_conf: Optional[str] = None
    config_overrides: Dict
    data: Dict[str, List[DatasetType]]

    # model_config is a reserved name in pydantic so we've renamed to base_config
    trainer_arguments: Dict = Field(..., alias="model_arguments")
    trainer_config: Dict = Field(..., alias="model_config")
    input_output_schema: ModelSchemaType = Field(..., alias="model_schema")

    training_run_id: int
    research_plan_id: Optional[int] = None
    experiment_id: Optional[int] = None

    @property
    def model_schema(self):
        warn("TrainingConfigType.model_schema->input_output_schema", DeprecationWarning, stacklevel=2)
        return self.input_output_schema

    def get_dataset_ids(self, purpose: str):
        purposes = ["train", "test", "dev"]
        if purpose not in purposes:
            raise KeyError(f"Invalid dataset purpose, expected one of {purposes} " f"got: {purpose}")

        return [d.id for d in self.data.get(f"datasets_{purpose}", [])]

    def get_dataset_purpose_id_lookup(self) -> Dict[str, List[int]]:
        purposes = ["train", "test", "dev"]
        return {p: self.get_dataset_ids(p) for p in purposes}

    @classmethod
    def _from_dict(cls, data):
        RENAMED_FIELDS = (
            ("model_arguments", "trainer_arguments"),
            ("model_config", "trainer_config"),
            ("model_schema", "input_output_schema"),
        )

        for old_name, new_name in RENAMED_FIELDS:
            if old_name in data:
                val = data.pop(old_name)
                data[new_name] = val
        return cls(**data)

    @classmethod
    def from_json(cls, json_path: Path):
        with json_path.open("r") as f:
            data = json.load(f)
        return cls._from_dict(data)

    @classmethod
    def from_yaml(cls, yaml_path: Path):
        with yaml_path.open("r") as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    def dump(self, fmt: str, path: Union[str, Path]):
        path = Path(path)
        dumpers = {
            "yaml": self._dump_yaml,
            "json": self._dump_json,
        }
        dumper = dumpers[fmt]
        dumper(path)

    def _dump_yaml(self, path: Path):

        with path.open("w") as f:
            yaml.safe_dump(self.model_dump(), f, default_flow_style=False)

    def _dump_json(self, path: Path):
        with path.open("w") as f:
            json.dump(self.model_dump(), f, indent=2)

    @property
    def evaluation_id(self) -> Optional[int]:
        return self.research_plan_id

    @classmethod
    def from_highlighter(cls, client: HLClient, training_run_id: int):
        return get_training_config(client, training_run_id)


def _update_model_outputs_to_use_taxon(model_outputs):
    updated_model_outputs = []
    for mo in model_outputs:
        if "taxon" in mo:
            updated_model_outputs.append(mo)
        else:
            taxa = {}
            for key in (
                "entity_attribute_id",
                "entity_attribute_name",
                "entity_attribute_value_type",
                "entity_attribute_enum_id",
                "entity_attribute_enum_value",
            ):
                taxa[key] = mo.pop(key, None)
            mo["taxon"] = [taxa]
            updated_model_outputs.append(mo)
    return updated_model_outputs


def get_training_config(
    client: HLClient,
    training_run_id: int,
) -> TrainingConfigType:
    class TrainingRunType(GQLBaseModel):
        training_config: dict

    result = client.trainingRun(
        return_type=TrainingRunType,
        id=training_run_id,
    )

    # ToDo: Intermediate backward compat code mapping single attr model model_outputs
    # to taxon model_outputs as per https://github.com/silverpond/highlighter-web/pull/44
    # when this is on master we can remove this code.
    training_config = result.training_config
    training_config["model_schema"]["model_outputs"] = _update_model_outputs_to_use_taxon(
        training_config["model_schema"]["model_outputs"],
    )
    ### END ###

    return TrainingConfigType(**result.training_config)
