import json
import logging
from typing import Dict, List

import click
import fastavro as avro
import yaml

from ..client import (
    ENTITY_AVRO_SCHEMA,
    HLJSONEncoder,
    PageInfo,
    SubmissionType,
    create_assessment_with_avro_file,
    get_latest_assessments_gen,
    upload_file_to_s3,
)
from ..core import GQLBaseModel, paginate
from ..datasets import Dataset
from ..datasets.formats.coco.reader import CocoReader
from ..datasets.formats.highlighter.writer import (
    CreateSubmissionPayload,
    HighlighterAssessmentsWriter,
)

ASSESSMENT_FIELDS = list(SubmissionType.__annotations__.keys())


class AnnotationsAttributesParamType(click.ParamType):
    name = "dict"

    def convert(self, value, param, ctx):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON: {e}", param, ctx)


class EAVTAttributesParamType(click.ParamType):
    name = "dict"

    def convert(self, value, param, ctx):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON: {e}", param, ctx)


@click.group("assessment")
@click.pass_context
def assessment_group(ctx):
    pass


@assessment_group.command("create")
@click.option(
    "-p",
    "--workflow-id",
    type=int,
    required=True,
    help="Destination process",
)
@click.option(
    "-u",
    "--user-id",
    type=int,
    required=False,
    help="User ID to load submission against",
)
@click.option(
    "-i",
    "--data-file-id",
    type=int,
    required=True,
    help="Image ID",
)
@click.option(
    "-s",
    "--status",
    type=str,
    required=True,
    help="Assessment status for assessment",
)
@click.option(
    "-m",
    "--capability-id",
    type=int,
    required=False,
    help="Assessment status for assessment",
)
@click.option(
    "-c",
    "--matched-image-id",
    type=int,
    required=False,
    help="Matched image ID for assessment",
)
@click.option(
    "-t",
    "--training-run-id",
    type=int,
    required=False,
    help="Training run ID for assessment",
)
@click.option(
    "-q",
    "--step-id",
    type=int,
    required=False,
    help="Image queue ID for assessment",
)
@click.option(
    "-d",
    "--data-source-id",
    type=int,
    required=False,
    help="Data source ID for assessment",
)
@click.option(
    "-a",
    "--started-at",
    type=str,
    required=False,
    help="The datetime this assessment was started",
)
@click.option(
    "-f",
    "--flag-reason",
    type=str,
    required=False,
    help="The reason this assessments is flagged",
)
@click.option(
    "-b",
    "--background-info-layer-file-data",
    type=str,
    required=False,
    help="Background information layer file data",
)
@click.option(
    "-n",
    "--annotations-attributes",
    type=AnnotationsAttributesParamType(),
    required=False,
    help="Annotations attributes",
)
@click.option(
    "-v",
    "--eavt-attributes",
    type=EAVTAttributesParamType(),
    required=False,
    help="EAVT attributes",
)
@click.option(
    "-k",
    "--task-id",
    type=str,
    required=False,
    help="Associated task ID",
)
@click.pass_context
def create(
    ctx,
    workflow_id,
    user_id,
    data_file_id,
    status,
    capability_id,
    matched_image_id,
    training_run_id,
    step_id,
    data_source_id,
    started_at,
    flag_reason,
    background_info_layer_file_data,
    annotations_attributes,
    eavt_attributes,
    task_id,
):
    client = ctx.obj["client"]

    result = client.createSubmission(
        return_type=CreateSubmissionPayload,
        projectId=workflow_id,
        userId=user_id,
        imageId=data_file_id,
        status=status,
        modelId=capability_id,
        trainingRunId=training_run_id,
        imageQueueId=step_id,
        dataSourceId=data_source_id,
        startedAt=started_at,
        flagReason=flag_reason,
        backgroundInfoLayerFileData=background_info_layer_file_data,
        taskId=task_id,
        annotationsAttributes=annotations_attributes,
        eavtAttributes=eavt_attributes,
    ).gql_dict()

    click.echo(json.dumps(result, cls=HLJSONEncoder))


@assessment_group.command("create-from-dataset")
@click.option(
    "-f",
    "--dataset-format",
    type=click.Choice(["hdf", "coco", "json"]),
    required=True,
    help="The format the data is on disk",
)
@click.option(
    "-d",
    "--data-path",
    type=click.Path(dir_okay=False, exists=True),
    required=True,
    help="Path to data file",
)
@click.option(
    "-p",
    "--workflow-id",
    type=int,
    required=True,
    help="Destination workflow",
)
@click.option(
    "-u",
    "--user-id",
    type=int,
    required=False,
    help="User id to load assessments against",
    default=None,
)
@click.option(
    "-s",
    "--data-source-ids",
    type=int,
    required=False,
    help="Where the existing data_files are in Highlighter",
    default=None,
    multiple=True,
)
@click.option(
    "--fix-invalid-polygons/--no-fix-invalid-polygons",
    type=bool,
    required=False,
    help="Try to convert self-intersecting Polygons to MultiPolygon from 'coco' dataset",
    default=False,
)
@click.pass_context
def create_from_dataset(
    ctx,
    dataset_format,
    data_path,
    workflow_id,
    user_id,
    data_source_ids,
    fix_invalid_polygons,
):
    """Create assessments from an on disk dataset.

    It is expected that data_files have been uploaded already to one of the provided
    --data-source-ids. If you use `hl data_file create` with a coco dataset it will
    produce a directory containing an augmented coco dataset with symlinks mapping
    the Highlighter data_file_id to the original file path. We recommend this workflow
    in most cases.

    """
    client = ctx.obj["client"]
    logger = logging.getLogger(__name__)

    if dataset_format == "hdf":
        if fix_invalid_polygons:
            logger.info(
                "--fix-invalid-polygons only used for --dataset-format 'coco'. It has no effect when using 'hdf'"
            )
        ds = Dataset.read_hdf(path=data_path)
    elif dataset_format == "json":
        if fix_invalid_polygons:
            logger.info(
                "--fix-invalid-polygons only used for --dataset-format 'coco'. It has no effect when using 'json'"
            )
        ds = Dataset.read_json(path=data_path)
    elif dataset_format == "coco":
        reader = CocoReader(data_path, fix_invalid_polygons=fix_invalid_polygons)
        ds = Dataset.load_from_reader(reader)
    else:
        raise ValueError(f"Invalid dataset_format: {dataset_format}")

    # Get data_file ids in data_source
    class Image(GQLBaseModel):
        id: int
        original_source_url: str

    class ImageConnection(GQLBaseModel):
        page_info: PageInfo
        nodes: List[Image]

    if data_source_ids:
        original_source_url_to_id: Dict[str, int] = {
            i.original_source_url: i.id
            for i in paginate(client.imageConnection, ImageConnection, dataSourceId=data_source_ids)
        }

        # update data_file_ids
        old_id_filename = ds.data_files_df.loc[:, ["data_file_id", "filename"]].values
        old_id_to_new_id = {
            old_id: original_source_url_to_id[filename] for old_id, filename in old_id_filename
        }
        ds.data_files_df.loc[:, "data_file_id"] = ds.data_files_df.data_file_id.map(old_id_to_new_id)
        ds.annotations_df.loc[:, "data_file_id"] = ds.annotations_df.data_file_id.map(old_id_to_new_id)

    writer = HighlighterAssessmentsWriter(client, workflow_id, user_id=user_id)
    writer.write(ds)


@assessment_group.command("create-from-avro")
@click.option(
    "--avro-file",
    type=click.Path(dir_okay=False, exists=True),
    required=True,
    help="Path to Avro binary data file",
)
@click.option(
    "--file-id",
    type=int,
    required=True,
    help="Highlighter file ID for a video file",
)
@click.option(
    "--process-id",
    type=int,
    required=True,
    help="Highlighter Process ID for the assessment",
)
@click.pass_context
def create_from_avro(ctx, avro_file, file_id, workflow_id):
    client = ctx.obj["client"]
    # Check Avro file against schema
    with open(avro_file, "rb") as f:
        list(avro.reader(f, reader_schema=ENTITY_AVRO_SCHEMA))
    file_info = upload_file_to_s3(client, avro_file, mimetype="application/octet-stream")
    create_assessment_with_avro_file(client, workflow_id, file_id, file_info)
    print(f"Successfully created assessment on file {file_id} in workflow {workflow_id}")


@assessment_group.command(
    "read",
    help="Read assessments given a query. For simple queries us --query for more "
    "complex queries use --yaml-file. NOTE: !!!  graphQL query keys use camelCase  !!!",
)
@click.option(
    "-q",
    "--query",
    type=str,
    required=False,
    default=None,
    help="simple query yaml string",
)
@click.option(
    "-y",
    "--yaml-file",
    type=click.Path(exists=True, dir_okay=False),
    required=False,
    default=None,
    help="yaml file containing a query params that would be a pain to type in the prompt",
)
@click.option(
    "-c",
    "--count",
    type=int,
    required=False,
    default=None,
    help="Only show the first --count results",
)
@click.option(
    "-f",
    "--fields",
    type=str,
    required=False,
    default=None,
    multiple=True,
    help="Name of fields you wish to return, valid fields are: "
    f"{ASSESSMENT_FIELDS}. If blank will return all.",
)
@click.pass_context
def read(ctx, query, yaml_file, count, fields):
    client = ctx.obj["client"]

    if query is not None:
        query_args = yaml.safe_load(query)

    elif yaml_file is not None:
        with open(yaml_file, "r") as f:
            query_args = yaml.safe_load(f)

    else:
        raise ValueError("Expected one of --query or --yaml-file to be set")

    subs_gen = get_latest_assessments_gen(
        client,
        **query_args,
    )

    if count is None:
        count = float("inf")

    output_list = []
    for i, sub in enumerate(subs_gen, 1):
        sub_dict = sub.gql_dict()

        if fields:
            sub_dict = {f: sub_dict[f] for f in fields}

        output_list.append(sub_dict)

        if i == count:
            break

    click.echo(json.dumps(output_list, cls=HLJSONEncoder))
