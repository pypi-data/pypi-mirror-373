import hashlib
import tarfile
import tempfile
from pathlib import Path
from typing import Union

import yaml

from ....client import HLClient
from ...dataset import Dataset, S3Files
from ...interfaces import IWriter

PathLike = Union[str, Path]


class AwsS3Writer(IWriter):
    format_name = "aws-s3"

    def __init__(
        self,
        dataset_id: int,
        data_files_cache_dir: PathLike,
        bucket_name: str,
        prefix: str,
        client: HLClient,
    ):
        self.dataset_id = dataset_id
        self.data_files_cache_dir = Path(data_files_cache_dir)
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.client = client

    def write(
        self,
        dataset: Dataset,
    ):
        if self.prefix is None:
            prefix = Path(str(self.dataset_id))
        else:
            prefix = Path(f"{self.prefix}/{self.dataset_id}")

        def prepend_dataset_id(filename: str, dataset_id=self.dataset_id) -> str:
            filename = Path(filename)
            new_name = f"{dataset_id}_{filename.stem}{filename.suffix}"

            return str(filename.parent / new_name)

        idf = dataset.images_df
        id_to_new_id = {i: f"{self.dataset_id}_{i}" for i in idf.data_file_id}
        id_to_new_filename = {
            i: prepend_dataset_id(f) for i, f in zip(dataset.idf.data_file_id, dataset.idf.filename)
        }

        idf = dataset.idf.copy()
        idf["old_filename"] = idf.loc[:, "filename"]
        idf.loc[:, "filename"] = idf.data_file_id.map(id_to_new_filename)
        idf.loc[:, "data_file_id"] = idf.data_file_id.map(id_to_new_id)

        adf = dataset.adf.copy()
        adf.loc[:, "data_file_id"] = adf.data_file_id.map(id_to_new_id)

        tmp_dataset = Dataset(images_df=idf, annotations_df=adf)

        # Files will be added to the archive so to preserve the
        # path in the records.json:images:filename
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path("zzz-tmp")
            tmp_tar_path = Path(tmp_dir) / "files.tar"
            with tarfile.open(str(tmp_tar_path), "w") as tar:
                for old_filename, new_filename in zip(idf.old_filename, idf.filename):
                    file_location = self.data_files_cache_dir / old_filename
                    file_path_in_archive = Path("files") / new_filename

                    tar.add(str(file_location), arcname=str(file_path_in_archive))

            # Calculate MD5 sum of files archive
            with tmp_tar_path.open("rb") as f:
                files_md5 = hashlib.md5(f.read()).hexdigest()

            s3 = self.client.get_s3_client()
            files_s3_prefix = prefix / f"files_{self.dataset_id}_{files_md5}.tar"

            tmp_dataset.cloud_files_info = [
                S3Files(bucket_name=self.bucket_name, prefix=str(prefix), files=[files_s3_prefix.name])
            ]

            records_json_path = tmp_dir / "records.json"
            tmp_dataset.write_json(
                records_json_path,
            )
            ## Calculate MD5 sum of records.json
            with open(records_json_path, "rb") as f:
                records_md5 = hashlib.md5(f.read()).hexdigest()

            records_s3_prefix = prefix / f"records_{self.dataset_id}_{records_md5}.json"

            manifest = {"files": [files_s3_prefix.name], "records": [records_s3_prefix.name]}
            manifest_path = tmp_dir / "manifest.yaml"
            with manifest_path.open("w") as f:
                yaml.dump(manifest, f)

            manifest_s3_prefix = prefix / "manifest.yaml"

            print(f"Uploading {tmp_tar_path} to s3://{self.bucket_name}/{files_s3_prefix}")
            s3.upload_file(str(tmp_tar_path), self.bucket_name, str(files_s3_prefix))
            print(f"Uploading {records_json_path} to s3://{self.bucket_name}/{records_s3_prefix}")
            s3.upload_file(str(records_json_path), self.bucket_name, str(records_s3_prefix))
            print(f"Uploading {manifest_path} to s3://{self.bucket_name}/{manifest_s3_prefix}")
            s3.upload_file(str(manifest_path), self.bucket_name, str(manifest_s3_prefix))
