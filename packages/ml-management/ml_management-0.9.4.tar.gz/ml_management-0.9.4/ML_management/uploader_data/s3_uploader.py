"""DEPRECATED. Use S3Manager from ML_management.s3 for your s3 operations."""
import asyncio
from typing import Literal, Optional, Union

from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.s3 import S3Manager


class S3Uploader:
    """DEPRECATED. Use S3Manager from ML_management.s3 for your s3 operations."""

    def upload(
        self,
        local_path: str,
        bucket: str,
        upload_as_tar: bool = False,
        new_bucket_visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
        verbose: bool = True,
    ) -> Optional[asyncio.Task]:
        """
        Upload directory to bucket.

        Parameters
        ----------
        local_path: str
            path to directory with files you want to upload.
        bucket: str
            name of bucket you want to upload to.
        upload_as_tar: bool = False
            If the option is set to True, the files will be uploaded as a single tar archive. Default: False
        verbose: bool = True
            If the option is set to True and upload_as_tar set to False,
            a progress bar with the number of uploaded files will be displayed.
        new_bucket_visibility: Union[Literal['private', 'public'], VisibilityOptions]
            Visibility of this bucket to other users. Possible values VisibilityOptions.PRIVATE, PUBLIC.
            Defaults to PRIVATE.

        Returns
        -------
        Optional[asyncio.Task].
            If the files uploading to the bucket is started inside an asynchronous application,
            the method will schedule the task in the running event loop and
            return instance of asyncio.Task for further process monitoring by the application
        """
        return S3Manager().upload(
            local_path=local_path,
            bucket=bucket,
            upload_as_tar=upload_as_tar,
            new_bucket_visibility=new_bucket_visibility,
            verbose=verbose,
        )
