"""S3 Collector for downloading files and folders."""
from typing import List, Optional

from ML_management.collectors.collector_pattern import CollectorPattern
from ML_management.s3 import S3Manager


class S3Collector(CollectorPattern):
    """Collector for S3 paths using ML_management.s3.manager.S3Manager."""

    @staticmethod
    def get_json_schema():
        """Return json schema."""
        return {
            "type": "object",
            "properties": {
                "bucket": {"type": "string"},
                "untar_data": {"type": "boolean", "default": False},
                "remote_paths": {"type": ["array", None], "items": {"type": "string"}, "default": None},
                "sync": {"type": "boolean", "default": True},
                "clear_local": {"type": "boolean", "default": False},
            },
            "required": ["bucket"],
            "additionalProperties": False,
        }

    def set_data(
        self,
        *,
        bucket: str,
        untar_data: bool = False,
        remote_paths: Optional[List[str]] = None,
        verbose: bool = True,
        sync: bool = True,
        clear_local: bool = False,
    ) -> str:
        """
        Set data.

        :type local_path: string
        :param local_path: Local path to save data to.  Defaults to "s3_data".

        :type bucket: string
        :param bucket: Bucket containing requested files.

        :type remote_paths: list(string)
        :param remote_paths: List of paths relative to passed bucket.  Each path
            can represent either a single file, or a folder.  If a path represents
            a folder (should end with a slash), then all contents of a folder are recursively downloaded.

        :type verbose: bool
        :param verbose: Whether to disable the entire progressbar wrapper.

        :type sync: bool
        :param sync: Whether to synchronize local folder and remote s3 data.

        :type clear_local: bool
        :param clear_local: Whether to clear local folder before downloading.
        """
        return S3Manager().set_data(
            bucket=bucket,
            untar_data=untar_data,
            remote_paths=remote_paths,
            verbose=verbose,
            sync=sync,
            clear_local=clear_local,
        )
