import fcntl
import os
from dataclasses import dataclass
from pathlib import Path


def get_upload_paths(local_path: str):
    """Return all file paths in folder."""
    if os.path.isfile(local_path):
        file_size = os.stat(local_path).st_size  # size of file, in bytes
        return [
            StorageFilePath(storage_path=os.path.basename(local_path), local_path=local_path, size=file_size)
        ], file_size

    local_files = [str(path) for path in Path(local_path).rglob("*") if path.is_file()]

    upload_paths = []
    size = 0
    for local_file_path in local_files:
        storage_file_path = os.path.relpath(local_file_path, local_path)
        file_size = os.stat(local_file_path).st_size  # size of file, in bytes
        upload_paths.append(StorageFilePath(storage_path=storage_file_path, local_path=local_file_path, size=file_size))
        size += file_size

    return upload_paths, size


def get_upload_size(local_path: str):
    """Return size of folder or file."""
    return sum(f.stat().st_size for f in Path(local_path).glob("**/*") if f.is_file())


def get_bucket_size(bucket: str, remote_paths: list, paginator):
    """Return size of bucket."""
    total_bucket_size = 0
    for remote_path in remote_paths:
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=remote_path)
        for page in page_iterator:
            for obj in page.get("Contents", []):
                total_bucket_size += obj["Size"]
    return total_bucket_size


def get_bucket_info(bucket: str, remote_paths: list, paginator):
    """Return size of bucket."""
    total_bucket_size = 0
    bucket_info = {}
    for remote_path in remote_paths:
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=remote_path)
        for page in page_iterator:
            for obj in page.get("Contents", []):
                bucket_info[obj["Key"]] = {"LastModified": obj["LastModified"], "Size": obj["Size"]}
                total_bucket_size += obj["Size"]
    return total_bucket_size, bucket_info


@dataclass
class StorageFilePath:
    """Define paths for file in S3 Storage."""

    local_path: str
    storage_path: str
    size: int

    def __post_init__(self):
        """Check the types of variables."""
        assert isinstance(self.local_path, str)
        assert isinstance(self.storage_path, str)
        assert isinstance(self.size, int)


class FileLock:
    """Lock the synchronization by '.<bucket_name>' file as mutex."""

    def __init__(self, path: str, bucket: str) -> None:
        lock_directory = os.path.join(path, ".lock_files")
        self.lock_filename = os.path.join(lock_directory, "." + bucket)
        os.makedirs(lock_directory, exist_ok=True)

    def __enter__(self):
        self.fd = os.open(self.lock_filename, os.O_RDWR | os.O_CREAT)
        fcntl.lockf(self.fd, fcntl.LOCK_EX)

    def __exit__(self, _type, value, tb):
        fcntl.lockf(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)
