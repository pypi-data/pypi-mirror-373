"""
Bucketfs-related functions.
"""

import logging
import pathlib

import exasol.bucketfs as bfs

_logger = logging.getLogger(__name__)


def _file_in_bucket(file_name: str, bucket: bfs.Bucket) -> bool:
    """
    Checks that given file name is present in bucket.
    :param file_name: name to check
    :param bucket: bucket object
    :return: True if name is present, else False
    """
    try:
        return file_name in list(bucket)
    except TypeError as e:
        # SaaSBucket is not iterable, need to handle it here
        if e.args[0].endswith("not iterable"):
            return False
        raise e


def put_file(
    bucket: bfs.Bucket, file_path: pathlib.Path, skip_if_exists: bool = True
) -> bfs.path.BucketPath:
    """
    Uploads given file into bucketfs
    :param bucket: bucket to use
    :param file_path: local file path to uplaod. File have to exist.
    :param skip_if_exists: Do not upload if file already present in the bucketfs.
    :return: Path in the bucketfs.
    """
    if not file_path.exists():
        raise ValueError(f"Local file doesn't exist: {file_path}")
    local_name = file_path.name
    if skip_if_exists and _file_in_bucket(local_name, bucket):
        _logger.info("File %s is already present in the bucketfs", local_name)
    else:
        _logger.info("Uploading file %s to bucketfs", local_name)
        with file_path.open("rb") as file:
            bucket.upload(local_name, file)
    return bfs.path.BucketPath(local_name, bucket)
