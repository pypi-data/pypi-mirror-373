import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

import click

from ..client import HLJSONEncoder, create_data_files, multithread_graphql_file_download
from .common import _to_pathlib


def _assert_all_file_exist(file_paths: List[Path], logger):
    if not all([p.exists() for p in file_paths]):
        logger.error(f"The following files do not exist: {[p for p in file_paths if not p.exists()]}")
        sys.exit(1)


@click.group("data-file")
@click.pass_context
def data_file_group(ctx):
    pass


@data_file_group.command("read")
@click.option(
    "-i",
    "--ids",
    type=int,
    required=False,
    multiple=True,
    default=[],
    show_default=True,
)
@click.option(
    "-p",
    "--paths",
    type=str,
    required=False,
    multiple=True,
    default=[],
    show_default=True,
)
@click.option(
    "-o",
    "--data-file-dir",
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help="Where to save the data_files to",
)
@click.pass_context
def read(ctx, ids, paths, data_file_dir):
    client = ctx.obj["client"]
    data_file_ids = list(ids)

    for path in paths:
        with open(path, "r") as f:
            lines = f.readlines()
        data_file_ids.extend([data_file_id.strip() for data_file_id in lines])

    result = multithread_graphql_file_download(
        client,
        data_file_ids,
        data_file_dir,
    )


@data_file_group.command("create")
@click.option(
    "-u",
    "--data-source-uuid",
    type=str,
    required=True,
)
@click.option(
    "-d",
    "--data-file-dir",
    type=click.Path(exists=True, file_okay=False),
    required=False,
    default="",
    help="Directory of data_files to upload",
    callback=_to_pathlib,
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, dir_okay=False),
    required=False,
    default=None,
    help=".txt file or coco.json",
    callback=_to_pathlib,
)
@click.option(
    "-m",
    "--multipart-filesize",
    type=str,
    required=False,
)
@click.pass_context
def create(ctx, data_source_uuid, data_file_dir, file, multipart_filesize):
    """Upload a collection of data_files to a Datasource

    \b
    Options:
        data_file_dir: A directory of data_files to upload, if 'file' is passed
        this will serve as the root directory for the data_file file names.
        If None this it is assumed the full path is available within 'file'

        file:
            Option 1 (None): No file is passed, we simply try to upload all files
            in `data_file_dir`. After the upload a directory at <data_file_dir>_with_hl_ids
            will be created containing simlinks mapping the newly created Highlighter
            data_file ids to the original paths.

            Option 2 (.txt): A text file with each line a path to a data_file
            to upload. After the upload a directory at <file.name>_with_hl_ids
            will be created containing simlinks mapping the newly created Highlighter
            data_file ids to the original paths.

            Option 3 (.json): A valid coco detection/segmentation dataset. If
            `data_file_dir` is used it will be prepended to all `images.file_name`
            fields. After the upload a directory at <file.name>_with_hl_ids
            will be created containing an `images` directory of symlinks mapping
            the newly created Highlighter data_file ids to the original paths and
            a copy of the original coco json file with the updated file_path
            pointing to the image file symlinks
    """
    client = ctx.obj["client"]
    logger = logging.getLogger(__name__)

    class CocoFilePathSource:
        def __init__(self, coco_json: Path, file_dir: Path):
            self.coco_json = coco_json
            self.file_dir = file_dir
            self.output_root = self.coco_json.parent / f"{self.coco_json.stem}_with_hl_ids"
            self.output_json = self.output_root / self.coco_json.name
            self.output_images_dir = self.output_root / "images"
            self.output_images_dir.mkdir(parents=True, exist_ok=True)

            with Path(file).open("r") as f:
                self.coco_data = json.load(f)
                self.file_paths = [self.file_dir / i["file_name"] for i in self.coco_data["images"]]
                _assert_all_file_exist(self.file_paths, logger)

        def get_data_file_paths(self):
            return self.file_paths

        def update_data_file_ids(self, file_path_to_id: Dict[str, str]):
            old_id_to_new_id = {}
            for image_record in self.coco_data["images"]:
                original_file_path = self.file_dir / image_record["file_name"]
                new_id = file_path_to_id[str(original_file_path)]
                old_id_to_new_id[image_record["id"]] = new_id
                image_record["id"] = new_id

                link_path = (self.output_images_dir / f"{new_id}{original_file_path.suffix}").absolute()

                if link_path.exists():
                    os.unlink(link_path)

                link_path.symlink_to(original_file_path.absolute())

                image_record["file_name"] = str(link_path.name)

            for annotation_record in self.coco_data["annotations"]:
                old_image_id = annotation_record["image_id"]
                annotation_record["image_id"] = old_id_to_new_id[old_image_id]

            with self.output_json.open("w") as f:
                json.dump(self.coco_data, f)

        def message(self):
            return f"Duplicate of {self.coco_json} created with Highlighter file_ids created at {self.output_root}"

    class TextFilePathSource:
        def __init__(self, text_file_path: Path, file_dir: Path):
            self.text_file_path = text_file_path
            self.file_dir = file_dir
            self.output_dir = self.text_file_path.parent / f"{self.text_file_path.stem}_with_hl_ids"

            with Path(file).open("r") as f:
                self.file_paths = [self.file_dir / line.strip() for line in f.readlines()]
                _assert_all_file_exist(self.file_paths, logger)

        def get_data_file_paths(self):
            return self.file_paths

        def update_data_file_ids(self, file_path_to_id: Dict[str, str]):
            # Create the new directory if it doesn't exist
            self.output_dir.mkdir(exist_ok=True)

            # Iterate over the original and new filenames
            for original_path, data_file_id in file_path_to_id.items():
                # Create the full paths to the original and new files
                original_path = Path(original_path).absolute()
                link_path = (self.output_dir / f"{data_file_id}{original_path.suffix}").absolute()
                if link_path.exists():
                    os.unlink(link_path)

                # Check if the original file exists
                # Create a symlink to the original data_file with the new filename
                link_path.symlink_to(original_path)

        def message(self):
            return f"Directory of symlinks with Highlighter file_ids created at {self.output_dir}"

    class DirFilePathSource:
        def __init__(self, file_dir: Path):
            self.file_dir = file_dir
            self.output_dir = Path(f"{self.file_dir}_with_hl_ids")

        def get_data_file_paths(self):
            def path_iterator():
                for p in os.scandir(str(self.file_dir)):
                    if p.is_file():
                        yield Path(p.path)

            return path_iterator()

        def update_data_file_ids(self, file_path_to_id: Dict[str, str]):
            # Create the new directory if it doesn't exist
            self.output_dir.mkdir(exist_ok=True)

            # Iterate over the original and new filenames
            for original_path, data_file_id in file_path_to_id.items():
                # Create the full paths to the original and new files
                original_path = Path(original_path).absolute()
                link_path = (self.output_dir / f"{data_file_id}{original_path.suffix}").absolute()
                if link_path.exists():
                    os.unlink(link_path)

                # Check if the original file exists
                # Create a symlink to the original data_file with the new filename
                link_path.symlink_to(original_path)

        def message(self):
            return f"Directory of symlinks with Highlighter file_ids created at {self.output_dir}"

    if file is None:
        # If no file passed but we have data_file_dir then
        # we must be uploading a dir of data_files
        file_path_src = DirFilePathSource(data_file_dir)

    elif Path(file).suffix == ".json":
        # Json must be a coco file
        file_path_src = CocoFilePathSource(file, data_file_dir)

    else:
        # If not json it must be a text file
        file_path_src = TextFilePathSource(file, data_file_dir)

    data_file_path_to_id, failed_data_file_paths = create_data_files(
        client,
        file_path_src.get_data_file_paths(),
        data_source_uuid,
        progress=True,
        multipart_filesize=multipart_filesize,
    )

    file_path_src.update_data_file_ids(data_file_path_to_id)

    logger.info(
        f"{len(data_file_path_to_id)} succeeded, {len(failed_data_file_paths)} failed -> {failed_data_file_paths}"
    )
    logger.info(file_path_src.message())

    click.echo(
        json.dumps(
            {
                "data_file_path_to_id": data_file_path_to_id,
                "failed_data_file_paths": failed_data_file_paths,
            },
            cls=HLJSONEncoder,
        )
    )
