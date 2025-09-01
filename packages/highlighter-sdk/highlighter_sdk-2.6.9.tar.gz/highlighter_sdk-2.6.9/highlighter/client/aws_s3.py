import hashlib
import mimetypes
import os
import warnings
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from typing import IO, Dict, List, Optional, Tuple, Union

import magic
import requests
import tqdm
from pydantic import BaseModel

import highlighter.core.decorators as decorators

from .base_models import CompleteFileMultipartUploadPayload, PresignedUrlType
from .gql_client import HLClient

C_1MB = 1000_000
C_200MB = 200 * C_1MB

# Description
# ~~~~~~~~~~~
# AWS S3 support functions and data structures.
#
# To Do
# ~~~~~
# - Complete and consistent error handling


__all__ = [
    "download_file_from_s3",
    "list_files_in_s3",
    "upload_file_to_s3",
    "upload_file_to_s3_in_memory",
    "upload_file_to_s3_io",
    "upload_large_file_threaded_mem",
]


def size_to_bytes(size_str):
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

    # Find the position where the numeric part ends and unit starts
    for i in range(len(size_str)):
        if not size_str[i].isdigit() and size_str[i] != ".":
            break

    # Extracting the number and the unit from the size string
    number, unit = size_str[:i], size_str[i:].upper()

    # Converting the number to float for fractional sizes (if any)
    number = float(number)

    if unit in units:
        return int(number * units[unit])
    else:
        raise ValueError("Invalid size unit. Use B, KB, MB, GB, or TB.")


def get_presigned_url(client: HLClient, filename=None):
    result = client.presignedUrl(
        return_type=PresignedUrlType,
        filename=filename,
    )
    return result


def upload_file_to_s3(
    client: HLClient,
    pathname: str,
    mimetype: Optional[str] = None,
    multipart_filesize: Optional[str] = None,
) -> dict:
    with open(pathname, "rb") as fp:
        file_size = os.stat(pathname).st_size
        file_size_in_gb = file_size / 1024 / 1024 / 1024

        SIZE_5GB_IN_BYTES = 5 * 1024 * 1024 * 1024  # 5GB in bytes
        multipart_filelimit = SIZE_5GB_IN_BYTES
        if multipart_filesize is not None:
            multipart_filelimit = size_to_bytes(multipart_filesize)

        if file_size >= multipart_filelimit:
            warnings.warn(f"File size is {file_size_in_gb:.2f} GB, using multipart upload")
            key, storage, file_name, _url = upload_large_file_threaded_mem(client, pathname)
            if mimetype is None:
                mimetype = guess_mimetype(file_name)

            return {
                "id": key,
                "storage": storage,
                "metadata": {
                    "size": file_size,  # in bytes
                    "filename": file_name,
                    "mimeType": mimetype,
                },
            }

        else:
            return upload_file_to_s3_io(
                client,
                fp,
                os.path.basename(pathname),
                file_size,
                mimetype=mimetype,
            )


def upload_file_to_s3_in_memory(
    client: HLClient, bytes: bytes, img_name: str, mimetype: Optional[str] = None
) -> dict:
    io_obj = BytesIO(bytes)
    return upload_file_to_s3_io(
        client,
        io_obj,
        img_name,
        len(bytes),
        mimetype=mimetype,
    )


# FIXME: Move to data_file.py
def guess_mimetype(file_name: str) -> Optional[str]:
    custom_mimetype_lookup = {
        ".OnnxOpset11": "application/octet-stream",
        ".OnnxOpset14": "application/octet-stream",
        ".avro": "application/avro",
        # Commented out for now, we can add these as needed
        # once we're happy with the mimetype value
        # ".TorchScriptV1": "application/octet-stream",
        # ".TensorFlowV1": "application/octet-stream",
        # ".DeprecatedMmpond": "application/octet-stream",
        # ".DeprecatedClassilvier": "application/octet-stream",
        # ".DeprecatedSilverclassify": "application/octet-stream",
        # ".OnnxRuntimeAmd64": "application/octet-stream",
        # ".OnnxRuntimeArm": "application/octet-stream",
    }
    file_extention = Path(file_name).suffix
    mimetype: Optional[str] = custom_mimetype_lookup.get(
        file_extention, mimetypes.MimeTypes().guess_type(str(file_name))[0]
    )
    return mimetype


def infer_mime_type(filename: str) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_file(filename)


def split_into_filepointers(filename: str, size: int, fp_iter_size: int, is_bytes: bool = True) -> List[IO]:
    file_size = os.path.getsize(filename)
    assert fp_iter_size <= size
    fps = []
    for offset in range(0, file_size, size):
        fp = open(filename, "rb" if is_bytes else "r")
        fp.seek(offset)
        fps.append(fp)
    return fps


def upload_large_file_threaded_mem(
    client: HLClient, filepath: str, *, part_size: int = C_1MB * 100, n_workers: int = 4
) -> Tuple[bool, Optional[str]]:
    thread_client = HLClient.from_credential(api_token=client.api_token, endpoint_url=client.endpoint_url)

    if not os.path.isfile(filepath):
        raise ValueError(f"{filepath} doesn't exist")

    class CreateFileMultipartUploadPayload(BaseModel):
        errors: List[str]
        key: Optional[str] = None
        uploadId: Optional[str] = None

    fps = split_into_filepointers(filepath, part_size, fp_iter_size=C_1MB * 2)
    filename = os.path.basename(filepath)
    resp = thread_client.createFileMultipartUpload(
        return_type=CreateFileMultipartUploadPayload,
        filename=filename,
        contentType=infer_mime_type(filepath),
    )
    if resp.errors:
        raise ValueError(f"{resp.errors}")
    upload_id = resp.uploadId
    key = resp.key

    def upload_worker(part_n: int, data: IO):
        with data:
            thread_client = HLClient.from_credential(
                api_token=client.api_token, endpoint_url=client.endpoint_url
            )
            result = thread_client.presignedUploadPartUrl(
                return_type=PresignedUrlType,
                uploadId=upload_id,
                key=key,
                partNumber=part_n,
            )
            signed_url = result.url

            resp = decorators.network_fn_decorator(requests.put)(
                signed_url, data=data.read(part_size), timeout=300
            )
        if not resp.ok:
            return None
        etag = resp.headers["ETAG"]
        return {"eTag": etag, "partNumber": part_n}

    #####################################################################################################
    with ThreadPoolExecutor(n_workers) as executor:
        parts = []
        n_part = len(fps)
        for x in tqdm.tqdm(executor.map(upload_worker, range(1, n_part + 1), fps), total=n_part):
            if x is None:
                abort_file_multipart_upload(key=key, upload_id=upload_id)
                raise ValueError("one of the parts failed!")
            parts.append(x)

    def complete_file_multipart_upload(upload_id: str, key: str, parts: List[Dict]):
        complete_upload_client = HLClient.from_credential(
            api_token=client.api_token, endpoint_url=client.endpoint_url
        )

        result = complete_upload_client.complete_file_multipart_upload(
            uploadId=upload_id,
            key=key,
            parts=parts,
            return_type=CompleteFileMultipartUploadPayload,
        )

        return result

    resp = complete_file_multipart_upload(key=key, upload_id=upload_id, parts=parts)

    # TODO: make this less horrible
    segments = key.split("/")
    return "/".join(segments[1:]), segments[0], filename, resp.url


def upload_file_to_s3_io(
    client: HLClient,
    fp: IO,
    file_name: str,
    file_size: int,
    mimetype: Optional[str] = None,
) -> dict:
    presigned_url = get_presigned_url(client, filename=file_name)
    files = {"file": fp}

    response = decorators.network_fn_decorator(requests.post)(
        presigned_url.url, files=files, data=presigned_url.fields, timeout=300
    )
    # a successful upload returns 204

    if response.status_code < 200 or response.status_code >= 300:
        # raise error here
        return None

    if mimetype is None:
        mimetype = guess_mimetype(file_name)
    if mimetype is None:
        raise ValueError(
            f"Unable to guess mimetype from {file_name}. "
            "Pass one manaully using the 'mimetype' optional arg. "
            "You crazy nerd! 🤓"
        )
    return {
        "id": presigned_url.key,
        "storage": presigned_url.storage,
        "metadata": {
            "size": file_size,  # in bytes
            "filename": file_name,
            "mimeType": mimetype,
        },
    }


def download_file_from_s3(
    client: Union[HLClient, "boto3.s3.client"],
    bucket_name: str,
    prefix: str,
    output_path: str,
    md5sum: str = None,
):
    """Download a file from an s3 bucket:

    bucket_name:---|
                ___|_____
           s3://my_bucket/path/to/file
                          ‾‾‾‾‾|‾‾‾‾‾‾
    prefix:--------------------|


    client: HLClient object with valid aws-s3 cloud credentials. See HLClient
            doc string for more info.

    bucket_name: Name of s3 bucket, see diagram at top of this doc string

    prefix: Path to file witin bucket, see diagram at top of this doc string

    output_path: Location to save downloaded file. The parent directory must
                 exist. If it does not this function will fail.

    md5sum: The md5 hash string of the file being downloaded. If not supplied
            not check will be performed.


    """
    if isinstance(client, HLClient):
        s3_client = client.get_s3_client()
    else:
        s3_client = client

    assert Path(
        output_path
    ).parent.exists(), f"Parent directory of output_path must exist, got: {output_path}"

    decorators.network_fn_decorator(s3_client.download_file)(bucket_name, prefix, output_path)

    if md5sum is not None:
        assert md5sum == hashlib.md5(open(output_path, "rb").read()).hexdigest()

    s3_client.close()


def list_files_in_s3(
    client: Union[HLClient, "boto3.s3.client"],
    bucket_name: str,
    prefix: str,
):
    """List files inside an s3 bucket

    bucket_name:---|
                ___|_____
           s3://my_bucket/path/to/file
                          ‾‾‾‾‾|‾‾‾‾‾‾
    prefix:--------------------|


    client: HLClient object with valid aws-s3 cloud credentials. See HLClient
            doc string for more info.

    bucket_name: Name of s3 bucket, see diagram at top of this doc string

    prefix: Path to file witin bucket, see diagram at top of this doc string

    """
    # TODO: Add pagination to support buckets with large numbers of files.

    if isinstance(client, HLClient):
        s3_client = client.get_s3_client()
    else:
        s3_client = client

    objects = decorators.network_fn_decorator(s3_client.list_objects)(Bucket=bucket_name, Prefix=prefix)
    contents = objects.get("Contents", [])
    s3_client.close()
    return [c["Key"] for c in contents]
