import json
import logging

import click

from ..client import EvaluationMetric, EvaluationMetricResult, HLJSONEncoder
from ..client.evaluation import (
    EvaluationMetricCodeEnum,
    create_evaluation_metric_result,
    find_or_create_evaluation_metric,
    get_existing_evaluation_metrics,
)


@click.group("evaluation")
@click.pass_context
def evaluation_group(ctx):
    pass


@evaluation_group.command("create-metric")
@click.argument("evaluation_id", type=int)
@click.argument(
    "code",
    type=click.Choice(tuple(EvaluationMetricCodeEnum.__members__.values())),
)
@click.argument("metric_name", type=str)
@click.option("--description", "-d", type=str, default=None)
@click.option(
    "--iou",
    type=click.FloatRange(min=0.0, max=1.0),
    default=None,
    help="Intersection-Over-Union. A measure of overlap",
)
@click.option("--weighted", type=bool, default=False, help="Is the metric weighted")
@click.option(
    "--object-class-uuid", "-o", type=str, default=None, help="The object class this metric refers to"
)
@click.pass_context
def create_metric(ctx, evaluation_id, code, metric_name, description, iou, weighted, object_class_uuid):
    """Create an evaluation metric record

    \b
    Args:
        evaluation_id: https://...highlighter.ai/research_plans/<EVALUATION_ID>
        metric_name: Human readable name
        code: Select from common metrics or use 'Other'

    \b
    Example:
        hl evaluation create-metric -d 'useful description' 123 Other foo
    """

    evaluation_metric: EvaluationMetric
    evaluation_metric = find_or_create_evaluation_metric(
        ctx.obj["client"],
        EvaluationMetric(
            research_plan_id=evaluation_id,
            code=code,
            description=description,
            iou=iou,
            name=metric_name,
            object_class_uuid=object_class_uuid,
            weighted=weighted,
        ),
    )[0]
    click.echo(json.dumps(evaluation_metric.model_dump(), cls=HLJSONEncoder))


@evaluation_group.command("create-result")
@click.argument("evaluation_metric_id", type=int)
@click.argument("result", type=float)
@click.option("--occured-at", type=click.DateTime(), default=None)
@click.option("--object-class-uuid", "-o", type=str, default=None)
@click.option("--training-run-id", "-t", type=int, default=None)
@click.option(
    "--lookup",
    "-l",
    type=click.Tuple((int, str)),
    default=None,
    help="Lookup the evaluation_metric_id, EVALUATION_ID, METRIC_NAME. Must set evaluation_metric_id to 0",
)
@click.pass_context
def create_result(ctx, evaluation_metric_id, result, occured_at, object_class_uuid, training_run_id, lookup):
    """Create an evaluation metric result

    \b
    Args:
        evaluation_metric_id: The id of the evaluation metric. To lookup by name
        instead, set this to 0 and use --lookup option
        result: float

    \b
    Examples:
        # Set an ExperimentResult with a known experiment_metric_id
        hl evaluation create-result 123 4.2
        \b
        # Set an ExperimentResult using the --lookup flag
        # we know the evaluation_id is 42 and the metric_name is 'Foo'
        # Note:
        #  - The metric_name is case sensitive
        #  - We set evaluation_metric_id to 0
        hl evaluation create-result --lookup 42 Foo 0 4.2


    """
    logger = logging.getLogger(__name__)
    assert evaluation_metric_id >= 0, f"evaluation_metric_id must be >= 0, got: {evaluation_metric_id}"

    client = ctx.obj["client"]
    if evaluation_metric_id == 0:
        assert lookup is not None, "To lookup an EvaluationMetric by name you must set the " "--lookup option"

        evaluation_id, metric_name = lookup
        existing_evaluation_metrics = {
            r.name: r for r in get_existing_evaluation_metrics(client, evaluation_id)
        }
        evaluation_metric = existing_evaluation_metrics.get(metric_name, None)
        assert evaluation_metric is not None, (
            f"Could not find an EvaluationMetric named '{metric_name}' " f"in Evaluation({evaluation_id})"
        )
        logger.info(f"Found existing metric: {evaluation_metric}")
        evaluation_metric_id = evaluation_metric.id

    assert isinstance(
        evaluation_metric_id, int
    ), f"evaluation_metric_id must be an int, got: {evaluation_metric_id}"

    metric_result: EvaluationMetricResult
    metric_result = create_evaluation_metric_result(
        client,
        evaluation_metric_id,
        result,
        occured_at=occured_at,
        object_class_uuid=object_class_uuid,
        training_run_id=training_run_id,
    )
    click.echo(json.dumps(metric_result.model_dump(), cls=HLJSONEncoder))
