import logging
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union
from uuid import UUID

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from ..core import GQLBaseModel
from .gql_client import HLClient

__all__ = [
    "EvaluationMetric",
    "EvaluationMetricCodeEnum",
    "EvaluationMetricResult",
    "create_evaluation_metric",
    "create_evaluation_metric_result",
    "find_or_create_evaluation_metric",
]


class EvaluationMetricCodeEnum(str, Enum):
    Dice = "Dice"
    mAP = "mAP"
    MaAD = "MaAD"
    MeAD = "MeAD"
    Other = "Other"
    AP = "AP"


class EvaluationMetric(GQLBaseModel):
    model_config = ConfigDict(use_enum_values=True)

    research_plan_id: int
    code: EvaluationMetricCodeEnum
    chart: Optional[str] = None
    description: Optional[str] = None
    iou: Optional[float] = None
    name: str
    object_class_uuid: Optional[Union[UUID, str]] = None
    weighted: Optional[bool] = False
    id: Optional[int] = None

    def dict(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        if "object_class_uuid" in d:
            d["object_class_uuid"] = str(d["object_class_uuid"])
        return d

    def create(self, client: HLClient):
        class CreateResearchPlanMetricReturnType(GQLBaseModel):
            errors: Any
            research_plan_metric: Optional[EvaluationMetric] = None

        kwargs = EvaluationMetric(
            research_plan_id=self.research_plan_id,
            code=self.code,
            # chart=self.chart,  # ToDo: Add this to the Graphql
            name=self.name,
            description=self.description,
            iou=self.iou,
            weighted=self.weighted,
            object_class_uuid=str(self.object_class_uuid),
        ).gql_dict()

        result = client.createResearchPlanMetric(return_type=CreateResearchPlanMetricReturnType, **kwargs)

        if result.errors:
            raise SystemExit(str(result.errors))
        return result.research_plan_metric

    def result(self, value, training_run_id):
        """Create an evaluation metric result instance without immediately persisting it.

        This method creates an EvaluationMetricResult object that can be used to store
        evaluation results. The result must be explicitly created using the .create()
        method to persist it to Highlighter.

        Args:
            value: The numeric evaluation result value
            training_run_id: ID of the training run that produced this result

        Returns:
            EvaluationMetricResult: A result object ready for creation/persistence

        Note:
            This method replaces the previous create_result() method to provide better
            separation between result object creation and persistence.
        """
        evaluation_metric_result = EvaluationMetricResult(
            research_plan_metric_id=self.id,
            result=value,
            object_class_uuid=self.object_class_uuid,
            training_run_id=training_run_id,
        )
        return evaluation_metric_result


class EvaluationMetricResult(GQLBaseModel, extra="forbid"):
    research_plan_metric_id: int
    result: float
    # iso datetime str will be generated at instantiation
    # if not supplied manually.
    occured_at: Optional[Union[datetime, str]] = Field(
        ..., default_factory=lambda _: datetime.now(timezone.utc).isoformat()
    )
    object_class_uuid: Optional[Union[UUID, str]] = None
    training_run_id: Optional[int] = None

    @field_validator("occured_at", mode="before")
    def set_timestamp(cls, v):
        if v is None:
            v = datetime.now(timezone.utc).isoformat()
        elif isinstance(v, str):
            v = datetime.fromisoformat(v).isoformat()
        elif isinstance(v, datetime):
            v = v.isoformat()
        else:
            raise ValidationError()
        return v

    @classmethod
    def from_yaml(cls, path: Union[Path, str]):
        path = Path(path)
        with path.open("r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def create(self, client: HLClient):
        class CreateExperimentResultReturnType(BaseModel):
            errors: Any
            experimentResult: Optional[EvaluationMetricResult] = None

        mutation_result: CreateExperimentResultReturnType = client.createExperimentResult(
            return_type=CreateExperimentResultReturnType,
            **self.gql_dict(),
        )
        if mutation_result.errors:
            raise SystemExit(str(mutation_result.errors))

        return mutation_result.experimentResult


def get_existing_evaluation_metrics(client: HLClient, evaluation_id: int):
    class QueryReturnType(GQLBaseModel):
        research_plan_metrics: List[EvaluationMetric]

    query_return_type: QueryReturnType = client.researchPlan(return_type=QueryReturnType, id=evaluation_id)

    return query_return_type.research_plan_metrics


def create_evaluation_metric(
    client: HLClient,
    evaluation_id: int,
    code: Union[EvaluationMetricCodeEnum, str],
    name: str,
    chart: Optional[str] = None,
    description: Optional[str] = None,
    iou: Optional[float] = None,
    weighted: Optional[bool] = False,
    object_class_uuid: Optional[Union[UUID, str]] = None,
) -> EvaluationMetric:

    result = EvaluationMetric(
        research_plan_id=evaluation_id,
        code=code,
        chart=chart,
        name=name,
        description=description,
        iou=iou,
        weighted=weighted,
        object_class_uuid=object_class_uuid,
    ).create(client)

    return result


def find_or_create_evaluation_metric(
    client: HLClient,
    evaluation_metrics: Union[EvaluationMetric, List[EvaluationMetric]],
) -> List[EvaluationMetric]:
    if isinstance(evaluation_metrics, EvaluationMetric):
        _evaluation_metrics = [evaluation_metrics]
    elif isinstance(evaluation_metrics, list):
        _evaluation_metrics = evaluation_metrics
    else:
        raise ValueError(f"Invalid evaluation_metrics, got: {evaluation_metrics}")

    logger = logging.getLogger(__name__)
    evaluation_ids = {e.research_plan_id for e in _evaluation_metrics}
    if len(evaluation_ids) > 1:
        logger.error("All evaluation metrics must have the same research_plan_id")
        sys.exit(1)

    existing_evaluation_metrics = {
        r.name: r for r in get_existing_evaluation_metrics(client, evaluation_ids.pop())
    }
    results: List[EvaluationMetric] = []

    for metric in _evaluation_metrics:
        if metric.name in existing_evaluation_metrics:
            found_metric = existing_evaluation_metrics[metric.name]
            logger.debug(f"Found evaluation metric {found_metric.id}:({found_metric.name})")
            results.append(found_metric)
        else:
            created_metric = metric.create(client)
            logger.debug(f"Created evaluation metric {created_metric.id}:({created_metric.name})")
            results.append(created_metric)

    return results


def create_evaluation_metric_result(
    client: HLClient,
    evaluation_metric_id: int,
    result: Union[float, int],
    occured_at: Optional[Union[datetime, str]] = None,
    object_class_uuid: Optional[Union[str, UUID]] = None,
    training_run_id: Optional[int] = None,
) -> EvaluationMetricResult:
    """Create an evaluation_metric if it does not exist, optionally
    create an evaluation_metric_result if result is not None
    """
    return EvaluationMetricResult(
        research_plan_metric_id=evaluation_metric_id,
        result=result,
        occured_at=occured_at,
        object_class_uuid=object_class_uuid,
        training_run_id=training_run_id,
    ).create(client)
