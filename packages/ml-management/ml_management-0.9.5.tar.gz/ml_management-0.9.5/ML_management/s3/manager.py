"""S3 Manager for operations with s3 data."""
import concurrent.futures
import datetime
import math
import mimetypes
import os
import posixpath
import random
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from http import HTTPStatus
from pathlib import Path
from typing import List, Literal, Optional, Union

import boto3
import magic
from boto3.s3.transfer import TransferConfig
from botocore.awsrequest import AWSRequest, AWSResponse
from botocore.config import Config
from botocore.exceptions import ClientError
from pydantic import BaseModel
from tqdm.autonotebook import tqdm

from ML_management import variables
from ML_management.local_debug.local_logger import LocalLogger
from ML_management.mlmanagement import get_debug
from ML_management.mlmanagement.load_api import _untar_folder
from ML_management.mlmanagement.log_api import _tar_folder
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.s3.utils import (
    FileLock,
    get_bucket_info,
    get_bucket_size,
    get_upload_paths,
    get_upload_size,
)
from ML_management.session import AuthSession
from ML_management.variables import LOCAL_REGISTRY_PATH

KB = 1024
MB = KB * KB
MAX_PARTS = 10000
MAX_KEYS = 1000
DEFAULT_MULTIPART_CHUNKSIZE = 8 * MB
S3_DATA = "s3_data"


class S3BucketNotFoundError(Exception):
    """Define Bucket Not Found Exception."""

    def __init__(self, bucket: str):
        self.bucket = bucket
        self.message = f'Bucket "{bucket}" does not exist'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (S3BucketNotFoundError, (self.bucket,))


class S3ObjectNotFoundError(Exception):
    """Define Version Not Found Exception."""

    def __init__(self, path: str, bucket: str):
        self.path = path
        self.bucket = bucket
        self.message = f'Object "{path}" is not found in "{bucket}" bucket'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (S3ObjectNotFoundError, (self.path, self.bucket))


class S3UpdateVisibilityError(Exception):
    """Define Version Not Found Exception."""

    def __init__(self, bucket: str, code: int, message: str):
        self.code = code
        self.bucket = bucket
        self.message = f"Error status {code} when trying to update bucket {bucket} visibility with message '{message}'."
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (S3UpdateVisibilityError, (self.bucket, self.code, self.message))


class FileIsNotTarError(Exception):
    """Define exception when tar is expected but not given."""

    def __init__(self, filename: str):
        self.filename = filename
        self.message = f"Expected tar file, but file {self.filename} does not have '.tar' extension"
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (FileIsNotTarError, (self.filename,))


class AmbiguousFileChoiceError(Exception):
    """Define exception when there is not exactly one file in bucket to choice."""

    def __init__(self, number_of_files: int):
        self.number_of_files = number_of_files
        if not number_of_files:
            appendix = " bucket is empty"
        else:
            appendix = "there is more than one file in bucket. Specify one file name with 'remote_paths' parameter"
        self.message = f"Expected one tar file in bucket, but {appendix}."
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (AmbiguousFileChoiceError, (self.number_of_files,))


class TimestampInterval(BaseModel):
    """Input wrapper for timestamp interval."""

    start: Optional[int]
    end: Optional[int]

    def __init__(self, start: Optional[int] = None, end: Optional[int] = None):
        if start and end and end < start:
            raise ValueError(
                f"The specified time interval from {start} to {end} is invalid: at least "
                f"one value should be present, and the end parameter should not exceed start."
            )
        super().__init__(start=start, end=end)

    def to_params(self):
        params = {}

        if self.start:
            params["creation_datetime_start_interval"] = self.start
        if self.end:
            params["creation_datetime_end_interval"] = self.end

        return params


class BucketFilterSettings(BaseModel):
    """Filter settings for list buckets."""

    name: Optional[str] = None
    visibility: Optional[str] = None
    creation_datetime_interval: Optional[TimestampInterval] = None
    owner_ids: Optional[list[str]] = None

    def to_params(self):
        params = {}
        for key, value in self.dict().items():
            if key == "creation_datetime_interval" and value:
                params.update(self.creation_datetime_interval.to_params())
            if value:
                params[key] = value
        return params


class ObjectInfo(BaseModel):
    """
    Info about the object from the bucket.

    Attributes:
        name (str): Name of the object.
        last_modified (datetime): Creation date of the object.
        size (int): Size in bytes of the object
    """

    name: str
    last_modified: datetime.datetime
    size: int


class BucketInfo(BaseModel):
    """
    Info about the bucket.

    Attributes:
        name (str): Name of the bucket.
        prefix (str): the prefix passed in the request.
        max_keys (int): The maximum number of keys returned in the response.
        key_count (int): The number of keys returned with this request.
        next_continuation_token (Optional[str]): If сontinuation_token was sent with the request,
            it is included in the response. You can use the returned next_continuation_token
            for pagination of the list response.
        contents (List[ObjectInfo]): Info about each object returned.

    """

    name: str
    prefix: str
    max_keys: int
    key_count: int
    next_continuation_token: Optional[str]
    contents: List[ObjectInfo]


class S3Manager:
    """Manager for operations with s3 objects."""

    def __init__(self) -> None:
        """Init creds."""
        self.default_url = variables.get_s3_gateway_url()
        self.default_access_key_id, self.default_secret_access_key = variables.get_s3_credentials()
        self.session = AuthSession()

    def list_objects(
        self, bucket: str, max_keys: int = MAX_KEYS, prefix: str = "", continuation_token: Optional[str] = None
    ) -> BucketInfo:
        """
        Returns some(up to 1,000) or all of the objects in a bucket.

        Parameters
        ----------
        bucket: str
            Name of bucket you want to show.
        prefix: str = ""
            the file or folder will be show to the bucket with this prefix.
            Example: if prefix = "foo", file "bar" would be show to the bucket as "foo/bar"
        max_keys: int
            The maximum number of keys returned in the response. If 0 is passed, it will return all objects.
            Defaults to 1000.

        continuation_token:Optional[str] = None
            If ContinuationToken was sent with the request, it is included in the response.
            You can use the returned ContinuationToken for pagination of the list response.

        Returns
        -------
        BucketInfo instance with meta information.
        """
        with self._get_sync_boto_client() as s3_client:
            if max_keys > 0:
                kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": max_keys}
                if continuation_token is not None:
                    kwargs["ContinuationToken"] = continuation_token
                response = s3_client.list_objects_v2(**kwargs)
                contents = [
                    ObjectInfo(name=content["Key"], last_modified=content["LastModified"], size=content["Size"])
                    for content in response.get("Contents", [])
                ]
                key_count = response["KeyCount"]
                max_keys = response["MaxKeys"]
                next_continuation_token = response.get("NextContinuationToken", None)
            else:
                next_continuation_token = None
                paginator = s3_client.get_paginator("list_objects_v2")
                page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
                contents = []
                key_count = 0
                for page in page_iterator:
                    key_count += page["KeyCount"]
                    contents.extend(
                        ObjectInfo(name=content["Key"], last_modified=content["LastModified"], size=content["Size"])
                        for content in page["Contents"]
                    )
        return BucketInfo(
            name=bucket,
            prefix=prefix,
            max_keys=max_keys,
            key_count=key_count,
            contents=contents,
            next_continuation_token=next_continuation_token,
        )

    @contextmanager
    def _get_sync_boto_client(self):
        s3_client = boto3.client(
            service_name="s3",
            use_ssl=True,
            endpoint_url=posixpath.join(self.default_url, "s3/"),
            aws_access_key_id=self.default_access_key_id,
            aws_secret_access_key=self.default_secret_access_key,
            config=Config(request_checksum_calculation="when_required"),
        )
        event_system = s3_client.meta.events
        event_system.register("before-sign.s3.*", self._add_auth_cookies)
        event_system.register("after-call.s3.*", self._update_auth_cookies)
        yield s3_client

    def list_buckets(self, filter_settings: Optional[BucketFilterSettings] = None) -> List[str]:
        """Get list names of available buckets."""
        params = None
        if filter_settings:
            params = filter_settings.to_params()
        with self.session.get(posixpath.join(self.default_url, "list-buckets"), params=params) as response:
            buckets_info: list[dict[str, str]] = response.json()["buckets"]
            return [bucket["name"] for bucket in buckets_info]

    def create_bucket(
        self,
        name: str,
        visibility: Union[Literal["private", "public"], VisibilityOptions],
    ) -> None:
        """Create new bucket with specified name and visibility."""
        visibility = VisibilityOptions(visibility)
        with self.session.post(
            posixpath.join(self.default_url, "create-bucket"), json={"name": name, "visibility": visibility.value}
        ) as response:
            if response.status_code != HTTPStatus.CREATED:
                raise RuntimeError(f"Failed to create bucket: {response.text}")

    def update_bucket_visibility(
        self,
        bucket: str,
        new_visibility: Union[Literal["private", "public"], VisibilityOptions],
    ) -> None:
        """Update bucket visibility."""
        new_visibility = VisibilityOptions(new_visibility)
        if bucket not in self.list_buckets():
            raise S3BucketNotFoundError(bucket)
        with self.session.post(
            posixpath.join(self.default_url, "update-bucket-auth", bucket),
            json={"visibility": new_visibility.value},
        ) as response:
            if not response.is_success:
                raise S3UpdateVisibilityError(bucket, response.status_code, response.text)

    def delete_bucket(self, bucket: str, verbose: bool = True, max_workers: Optional[int] = None) -> None:
        """Delete bucket."""
        self.delete_by_prefix(bucket=bucket, prefix="", verbose=verbose, max_workers=max_workers)
        with self._get_sync_boto_client() as s3_client:
            s3_client.delete_bucket(Bucket=bucket)

    def delete_by_prefix(self, bucket: str, prefix: str, verbose: bool = True, max_workers: Optional[int] = None):
        """Delete all objects with specified prefix in key.

        Parameters
        ----------
        bucket: str
            name of bucket you want to delete directory from.
        prefix: str
            path to your objects or dir
        max_workers: Optional[int] = None
            Maximum number of worker threads for parallel requests per file. Default: None
        verbose: bool = True
            If the option is set to True and upload_as_tar set to False,
            a progress bar with the number of uploaded files will be displayed.

            Example::

            |    Directories structure:
            |    ├───dockerfile
            |    ├───a.py
            |    ├───dir1
            |            ├───empty.txt
            |            └───dir2
            |                    ├───new.txt
            |                    ├───x.png
            |                    └───ipsum
            |                            └───y.png
            |    To delete dir1    use prefix="dir1"
            |    To delete dir2    use prefix="dir1/dir2"
            |    To delete new.txt use prefix="dir1/dir2/new.txt"
        """
        if bucket not in self.list_buckets():
            raise S3BucketNotFoundError(bucket)

        with self._get_sync_boto_client() as s3_client:
            paginator = s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

            total_size = 0
            for page in page_iterator:
                total_size += page["KeyCount"]
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

            with tqdm(
                total=total_size,
                disable=not verbose,
                unit_scale=True,
                unit_divisor=1024,
                unit="File",
            ) as pbar:
                futures = []
                with ThreadPoolExecutor(max_workers=max_workers) as thread_executor:
                    for page in page_iterator:
                        for obj in page.get("Contents", []):
                            object_key = obj.get("Key")
                            futures.append(
                                thread_executor.submit(
                                    self._delete_one_object,
                                    bucket=bucket,
                                    key=object_key,
                                    s3_client=s3_client,
                                    pbar=pbar,
                                )
                            )

                    tasks = concurrent.futures.wait(futures, return_when="FIRST_EXCEPTION")
                    try:
                        for error_task in tasks.done:
                            error_task.result()
                    except Exception as e:
                        for task in tasks.not_done:
                            task.cancel()
                        raise e

    def upload(
        self,
        local_path: str,
        bucket: str,
        upload_as_tar: bool = False,
        new_bucket_visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
        max_workers: Optional[int] = None,
        verbose: bool = True,
        prefix: str = "",
    ):
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
        max_workers: Optional[int] = None
            Maximum number of worker threads for parallel requests per file. Default: None
        verbose: bool = True
            If the option is set to True and upload_as_tar set to False,
            a progress bar with the number of uploaded files will be displayed.
        prefix: str = ""
            the file or folder will be uploaded to the bucket with this prefix.
            Example: if prefix = "foo", file "bar" would be uploaded to the bucket as "foo/bar"
        new_bucket_visibility: Union[Literal['private', 'public'], VisibilityOptions]
            Visibility of this bucket to other users. Possible values VisibilityOptions.PRIVATE, PUBLIC.
            Defaults to PRIVATE.
        """
        new_bucket_visibility = VisibilityOptions(new_bucket_visibility)

        if get_debug():
            LocalLogger().upload_bucket(local_path, bucket, prefix)
            return
        prefix = prefix.strip("/")
        if upload_as_tar:
            self._upload_as_tar(
                local_path=local_path,
                bucket=bucket,
                prefix=prefix,
                new_bucket_visibility=new_bucket_visibility,
                verbose=verbose,
            )
        else:
            self._upload_files(
                local_path=local_path,
                bucket=bucket,
                prefix=prefix,
                new_bucket_visibility=new_bucket_visibility,
                verbose=verbose,
                max_workers=max_workers,
            )

    def set_data(
        self,
        *,
        local_path: Optional[str] = None,
        bucket: str,
        untar_data: bool = False,
        remote_paths: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
        verbose: bool = True,
        sync: bool = True,
        clear_local: bool = False,
    ) -> str:
        """
        Set data.

        :type local_path: Optional[str]
        :param local_path: Local path to save data to.  Defaults to MLM_REGISTRY_PATH or S3_DATA when caching disable.

        :type bucket: string
        :param bucket: Bucket containing requested files.

        :type untar_data: bool
        :param untar_data: If the option is set to True,
            the tar file from the bucket will be downloaded and untarred into the folder.

        :type remote_paths: list(string)
        :param remote_paths: List of paths relative to passed bucket.  Each path
            can represent either a single file, or a folder.  If a path represents
            a folder (should end with a slash), then all contents of a folder are recursively downloaded.

        :type max_workers: Optional[int]
        :param max_workers: Maximum number of worker threads for parallel requests per file.

        :type verbose: bool
        :param verbose: Whether to disable the entire progressbar wrapper.

        :type sync: bool
        :param sync: Whether to synchronize local folder and remote s3 data or just download files again.

        :type clear_local: bool
        :param clear_local: Whether to clear local folder before downloading.
        """
        if local_path is None and not variables.NO_CACHE:
            local_path = os.path.join(LOCAL_REGISTRY_PATH, "row_data")
        elif local_path is None:
            local_path = S3_DATA

        if bucket not in self.list_buckets():
            raise S3BucketNotFoundError(bucket)

        print("Start to downloading bucket...")
        with FileLock(local_path, bucket):
            local_path = os.path.join(local_path, bucket)

            if os.path.exists(local_path) and clear_local:
                shutil.rmtree(local_path, ignore_errors=True)

            if untar_data:
                return self._download_data_tar(
                    local_path=local_path, bucket=bucket, remote_paths=remote_paths, verbose=verbose, sync=sync
                )

            return self._download_files(
                local_path=local_path,
                bucket=bucket,
                remote_paths=remote_paths,
                verbose=verbose,
                max_workers=max_workers,
                sync=sync,
            )

    def _delete_one_object(self, bucket: str, key: str, s3_client, pbar, retries: int = 3):
        # do retries if there are some network troubles, cause bucket and dir deleting depends on it,
        # if object was deleted earlier, s3_client.delete_object has no effect
        while retries > 0:
            try:
                s3_client.delete_object(Bucket=bucket, Key=key)
                pbar.update()
                break
            except Exception:
                retries -= 1
                if retries == 0:
                    raise
                time.sleep(random.randint(1, 9) * 1e-4)

    def _upload_as_tar(
        self, local_path: str, bucket: str, prefix: str, new_bucket_visibility: VisibilityOptions, verbose: bool
    ) -> None:
        local_path = os.path.normpath(local_path)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Path: {local_path} does not exist")

        total_size = get_upload_size(local_path)

        multipart_chunksize = math.ceil(total_size / MAX_PARTS)  # in bytes
        if multipart_chunksize < DEFAULT_MULTIPART_CHUNKSIZE:
            multipart_chunksize = DEFAULT_MULTIPART_CHUNKSIZE

        r, w = os.pipe()

        try:
            thread = threading.Thread(target=_tar_folder, args=(w, local_path), daemon=True)
            thread.start()
        except Exception as err:
            os.close(r)
            os.close(w)
            raise err
        with self._get_sync_boto_client() as s3_client:
            buckets = self.list_buckets()
            if bucket not in buckets:
                self.create_bucket(name=bucket, visibility=new_bucket_visibility)
            try:
                with tqdm(
                    total=total_size,
                    disable=not verbose,
                    unit_scale=True,
                    unit_divisor=1024,
                    unit="B",
                ) as pbar:
                    with open(r, "rb") as fileobj:
                        s3_client.upload_fileobj(
                            Fileobj=fileobj,
                            Bucket=bucket,
                            Key=os.path.join(prefix, f"{os.path.basename(local_path)}.tar"),
                            Callback=pbar.update,
                            ExtraArgs={"ContentType": "application/x-tar"},
                            Config=TransferConfig(multipart_chunksize=multipart_chunksize),
                        )
            finally:
                thread.join()

    def _upload_files(
        self,
        local_path: str,
        bucket: str,
        prefix: str,
        new_bucket_visibility: Union[Literal["private", "public"], VisibilityOptions],
        max_workers: Optional[int],
        verbose: bool = True,
    ):
        new_bucket_visibility = VisibilityOptions(new_bucket_visibility)
        local_path = os.path.normpath(local_path)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Path: {local_path} does not exist")
        with self._get_sync_boto_client() as s3_client:
            buckets = self.list_buckets()
            if bucket not in buckets:
                self.create_bucket(name=bucket, visibility=new_bucket_visibility)

            upload_paths, total_size = get_upload_paths(local_path)

            with tqdm(
                total=total_size,
                disable=not verbose,
                unit_scale=True,
                unit_divisor=1024,
                unit="B",
            ) as pbar:
                futures = []
                with ThreadPoolExecutor(max_workers=max_workers) as thread_executor:
                    for path in upload_paths:
                        media_type = mimetypes.guess_type(path.local_path)[0]
                        if not media_type:
                            media_type = magic.from_file(path.local_path, mime=True)

                        multipart_chunksize = math.ceil(path.size / MAX_PARTS)  # in bytes
                        if multipart_chunksize < DEFAULT_MULTIPART_CHUNKSIZE:
                            multipart_chunksize = DEFAULT_MULTIPART_CHUNKSIZE
                        futures.append(
                            thread_executor.submit(
                                s3_client.upload_file,
                                Filename=path.local_path,
                                Bucket=bucket,
                                Key=os.path.join(prefix, path.storage_path),
                                Callback=pbar.update,
                                ExtraArgs={"ContentType": media_type},
                                Config=TransferConfig(multipart_chunksize=multipart_chunksize),
                            )
                        )
                    tasks = concurrent.futures.wait(futures, return_when="FIRST_EXCEPTION")
                    try:
                        for error_task in tasks.done:
                            error_task.result()
                    except Exception as e:
                        for task in tasks.not_done:
                            task.cancel()
                        raise e

    def _set_data_sync(
        self,
        local_path: str,
        bucket: str,
        remote_paths: List[str],
        max_workers: Optional[int] = None,
        verbose: bool = True,
    ):
        """Synchronize bucket and local folder."""
        with self._get_sync_boto_client() as s3_client:
            paginator = s3_client.get_paginator("list_objects_v2")

            total_bucket_size, bucket_info = get_bucket_info(bucket, remote_paths, paginator)
            # get only local_paths with prefix in remote_paths
            local_files = []

            for remote_path in remote_paths:
                full_remote_path = os.path.join(local_path, remote_path)
                if Path(full_remote_path).is_file():
                    local_files.append(Path(full_remote_path))
                else:
                    local_files.extend(list(Path(full_remote_path).rglob("*")))  # breadth-first search

            with tqdm(
                total=total_bucket_size,
                unit_scale=True,
                unit_divisor=1024,
                disable=not verbose,
                unit="B",
            ) as pbar:
                futures = []
                with ThreadPoolExecutor(max_workers=max_workers) as thread_executor:
                    for path in reversed(local_files):
                        rel_path = path.relative_to(local_path)
                        if str(rel_path) not in bucket_info:
                            if path.is_file():
                                os.remove(path)
                            else:
                                # rm dir if empty
                                if not os.listdir(path):
                                    os.rmdir(path)
                            continue

                        local_last_modified = datetime.datetime.fromtimestamp(
                            os.path.getmtime(path), tz=datetime.timezone.utc
                        )
                        bucket_file_last_modified = bucket_info[str(rel_path)]["LastModified"].replace(
                            tzinfo=datetime.timezone.utc
                        )
                        if local_last_modified > bucket_file_last_modified:
                            pbar.update(bucket_info[str(rel_path)]["Size"])
                            bucket_info.pop(str(rel_path), None)
                            continue

                        bucket_info.pop(str(rel_path), None)

                        futures.append(
                            thread_executor.submit(
                                self._download_one_object,
                                bucket,
                                str(rel_path),
                                os.path.dirname(path),
                                path,
                                s3_client,
                                pbar.update,
                            )
                        )

                    for key in bucket_info.keys():
                        futures.append(
                            thread_executor.submit(
                                self._download_one_object,
                                bucket,
                                key,
                                os.path.dirname(os.path.join(local_path, key)),
                                os.path.join(local_path, key),
                                s3_client,
                                pbar.update,
                            )
                        )

                    tasks = concurrent.futures.wait(futures, return_when="FIRST_EXCEPTION")
                    try:
                        for error_task in tasks.done:
                            error_task.result()
                    except Exception as e:
                        for task in tasks.not_done:
                            task.cancel()
                        raise e

        return local_path

    def _download_data_tar(
        self,
        *,
        local_path: str,
        bucket: str,
        verbose: bool,
        remote_paths: Optional[List[str]] = None,
        sync: bool,
    ) -> str:
        remote_paths = remote_paths if remote_paths else None
        if remote_paths is not None and len(remote_paths) != 1:
            raise RuntimeError(f"Expected one tar object, but {len(remote_paths)} were given.")

        with self._get_sync_boto_client() as s3_client:
            if remote_paths is not None:
                tar_name = remote_paths[0]
                if not tar_name.endswith(".tar"):
                    raise FileIsNotTarError(tar_name)
            else:
                try:
                    # check that there is only one file in bucket
                    # If there is more than 1 file, raise exception about ambiguous choice
                    paginator = s3_client.get_paginator("list_objects_v2")
                    page_iterator = paginator.paginate(Bucket=bucket, Prefix="", PaginationConfig={"MaxItems": 2})
                    first_page = next(iter(page_iterator))
                    files = first_page.get("Contents", [])
                    if len(files) != 1:
                        raise AmbiguousFileChoiceError(number_of_files=len(files))
                    tar_name: str = files[0]["Key"]
                    tar_size: int = files[0]["Size"]
                    if not tar_name.endswith(".tar"):
                        raise FileIsNotTarError(tar_name)
                except ClientError as err:
                    if err.response["Error"]["Code"] == "NoSuchBucket":
                        raise S3BucketNotFoundError(bucket=bucket) from None
                    else:
                        raise

            try:
                head_object = s3_client.head_object(Bucket=bucket, Key=tar_name)
                tar_size = head_object["ContentLength"]

            except ClientError as err:
                if err.response["Error"]["Code"] == "NoSuchBucket":
                    raise S3BucketNotFoundError(bucket=bucket) from None
                if err.response["Error"]["Code"] == "404":
                    raise S3ObjectNotFoundError(path=tar_name, bucket=bucket) from None
                else:
                    raise

            local_path = os.path.join(local_path, tar_name.removesuffix(".tar"))

            if sync and os.path.exists(local_path):
                print("Bucket exist in local cache, synchronize with remote.")
                local_last_modified = min(
                    datetime.datetime.fromtimestamp(os.path.getatime(root), tz=datetime.timezone.utc)
                    for root, _, _ in os.walk(local_path)
                )
                if local_last_modified > head_object["LastModified"]:
                    with tqdm(
                        total=tar_size,
                        unit_scale=True,
                        unit_divisor=1024,
                        disable=not verbose,
                        unit="B",
                    ) as pbar:
                        pbar.update(tar_size)
                    return local_path
            if os.path.exists(local_path):
                shutil.rmtree(local_path, ignore_errors=True)

            return self._download_tar(
                local_path=local_path,
                s3_client=s3_client,
                tar_name=tar_name,
                tar_size=tar_size,
                bucket=bucket,
                verbose=verbose,
            )

    def _download_tar(
        self, local_path: str, tar_name: str, tar_size: int, bucket: str, verbose: bool, s3_client
    ) -> str:
        r, w = os.pipe()
        with open(r, "rb") as buff:
            try:
                thread = threading.Thread(target=_untar_folder, args=(buff, os.path.dirname(local_path)), daemon=True)
                thread.start()
            except Exception as err:
                os.close(r)
                os.close(w)
                raise err
            try:
                with open(w, "wb") as fileobj:
                    with tqdm(
                        total=tar_size,
                        unit_scale=True,
                        unit_divisor=1024,
                        disable=not verbose,
                        unit="B",
                    ) as pbar:
                        s3_client.download_fileobj(Fileobj=fileobj, Bucket=bucket, Key=tar_name, Callback=pbar.update)
            except ClientError as err:
                if err.response["Error"]["Code"] == "404":
                    raise S3ObjectNotFoundError(path=tar_name, bucket=bucket) from None
                raise
            finally:
                thread.join()
            return local_path

    def _download_files(
        self,
        *,
        local_path: str,
        bucket: str,
        remote_paths: Optional[List[str]] = None,
        max_workers: Optional[int],
        verbose: bool = True,
        sync: bool,
    ) -> str:
        remote_paths = remote_paths if remote_paths else [""]

        if sync and os.path.exists(local_path):
            print("Bucket exist in local cache, synchronize with remote.")
            return self._set_data_sync(local_path, bucket, remote_paths, max_workers, verbose)

        with self._get_sync_boto_client() as s3_client:
            paginator = s3_client.get_paginator("list_objects_v2")

            total_bucket_size = get_bucket_size(bucket, remote_paths, paginator)

            with tqdm(
                total=total_bucket_size,
                unit_scale=True,
                unit_divisor=1024,
                disable=not verbose,
                unit="B",
            ) as pbar:
                futures = []
                with ThreadPoolExecutor(max_workers=max_workers) as thread_executor:
                    for remote_path in remote_paths:
                        page_iterator = paginator.paginate(Bucket=bucket, Prefix=remote_path)
                        for page in page_iterator:
                            if page["KeyCount"] == 0 and remote_path != "":
                                raise S3ObjectNotFoundError(path=remote_path, bucket=bucket)
                            for obj in page.get("Contents", []):
                                file_path = obj.get("Key")

                                local_dir_path = os.path.join(local_path, posixpath.dirname(file_path))
                                local_file_path = os.path.join(local_path, file_path)
                                futures.append(
                                    thread_executor.submit(
                                        self._download_one_object,
                                        bucket,
                                        file_path,
                                        local_dir_path,
                                        local_file_path,
                                        s3_client,
                                        pbar.update,
                                    )
                                )

                    tasks = concurrent.futures.wait(futures, return_when="FIRST_EXCEPTION")
                    try:
                        for error_task in tasks.done:
                            error_task.result()
                    except Exception as e:
                        for task in tasks.not_done:
                            task.cancel()
                        raise e
            return local_path

    # arguments to callback are passed like kwargs, so kwargs must be present in signature
    def _add_auth_cookies(self, request: AWSRequest, **kwargs) -> None:  # noqa
        request.headers.add_header("Cookie", self.session._get_cookie_header())

    # arguments to callback are passed like kwargs, so kwargs must be present in signature
    def _update_auth_cookies(self, http_response: AWSResponse, **kwargs) -> None:  # noqa
        cookie_header = http_response.headers.get("set-cookie")
        if cookie_header is None:
            return
        cookies: list[str] = cookie_header.split("; ")
        for cookie in cookies:
            if "kc-access" not in cookie:
                continue
            _, new_access_token = cookie.split("=", maxsplit=1)
            self.session.cookies["kc-access"] = new_access_token
            break

    def _download_one_object(
        self, bucket: str, key: str, local_dir_path: str, local_file_path: str, s3_client, callback
    ):
        if not os.path.exists(local_dir_path):
            os.makedirs(local_dir_path, exist_ok=True)
        s3_client.download_file(bucket, key, local_file_path, Callback=callback)
