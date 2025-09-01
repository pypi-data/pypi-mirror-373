from pathlib import Path
from typing import Optional

# These 4 imports are made availiable from this file
# for backwards compatability.
from .base_models import *
from .cropping import *
from .dataset import *
from .formats.aws_s3.writer import AwsS3Writer
from .formats.coco.common import CocoCategory, bbox_to_wkt, segmentation_to_wkt
from .formats.coco.reader import CocoReader
from .formats.coco.writer import CocoWriter
from .formats.highlighter.reader import HighlighterAssessmentsReader
from .formats.highlighter.writer import HighlighterAssessmentsWriter
from .formats.torch_image_folder.reader import TorchImageFolderReader
from .formats.torch_image_folder.writer import TorchImageFolderWriter
from .formats.yolo.writer import YoloWriter
from .splits import SUPPORTED_SPLIT_FNS, RandomSplitter, get_split_fn

READERS = {
    CocoReader.format_name: CocoReader,
    HighlighterAssessmentsReader.format_name: HighlighterAssessmentsReader,
    TorchImageFolderReader.format_name: TorchImageFolderReader,
}

WRITERS = {
    CocoWriter.format_name: CocoWriter,
    HighlighterAssessmentsWriter.format_name: HighlighterAssessmentsWriter,
    TorchImageFolderWriter.format_name: TorchImageFolderWriter,
    AwsS3Writer.format_name: AwsS3Writer,
}


def get_reader(name):
    return READERS[name]


def get_writer(name):
    return WRITERS[name]


def read_dataset_from_highlighter(
    client: "HLClient",
    dataset_id: int,
    datasets_cache_dir: Optional[Path] = None,
    data_files_cache_dir: Optional[Path] = None,
    page_size: int = 200,
):
    """Reads and initializes a dataset stored in HL"""
    ds = Dataset.read_from(
        dataset_format=DatasetFormat.HIGHLIGHTER_DATASET,
        client=client,
        dataset_id=dataset_id,
        datasets_cache_dir=datasets_cache_dir,
        data_files_cache_dir=data_files_cache_dir,
        page_size=page_size,
    )

    return ds


def write_assessments_to_highlighter(client, ds, workflow_id, user_id=None):
    """Write a dataset as assessments to a highlighter workflow

    Args:
        client (highlighter.gql_client.HLClient): graphql client
        ds (highlighter.datasets.Dataset): dataset to write
        workflow_id (int): id of workflow to write new assessments to
        user_id (int): id of the user to be the 'submitter' e.g. 493, default=None

    Returns:
        _type_: dataset with updated assessment id's and hashes (edited in place)
    """
    writer = get_writer("highlighter_assessments")(client, workflow_id, user_id=user_id)

    writer.write(ds)

    return ds
