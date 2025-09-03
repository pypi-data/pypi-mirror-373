"""Methods for working with files and folders."""
import os
from dataclasses import dataclass
from pathlib import Path


def get_upload_paths(local_path: str):
    """Return all file paths in folder."""
    if os.path.isfile(local_path):
        return [StorageFilePath(storage_path=os.path.basename(local_path), local_path=local_path)]

    local_files = [str(path) for path in Path(local_path).rglob("*") if path.is_file()]

    upload_paths = []
    for local_file_path in local_files:
        storage_file_path = os.path.relpath(local_file_path, local_path)
        upload_paths.append(StorageFilePath(storage_path=storage_file_path, local_path=local_file_path))

    return upload_paths


@dataclass
class StorageFilePath:
    """Define paths for file in S3 Storage."""

    local_path: str
    storage_path: str

    def __post_init__(self):
        """Check the types of variables."""
        assert isinstance(self.local_path, str)
        assert isinstance(self.storage_path, str)
