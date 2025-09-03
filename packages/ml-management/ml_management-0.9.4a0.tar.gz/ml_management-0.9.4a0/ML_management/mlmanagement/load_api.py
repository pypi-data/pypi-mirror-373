import importlib
import json
import os
import os.path
import subprocess
import sys
import tarfile
import tempfile
import threading
import traceback
from pathlib import Path
from typing import Literal, Optional, Tuple, Union

import yaml
from sgqlc.operation import Operation
from tqdm.autonotebook import tqdm

from ML_management import variables
from ML_management.base_exceptions import MLMClientError
from ML_management.graphql import schema
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.local_debug.debug_job_result import DebugJobLogContext
from ML_management.mlmanagement.log_api import _raise_error
from ML_management.mlmanagement.metainfo import LoadedObject, ObjectMetaInfo
from ML_management.mlmanagement.model_type import ModelType
from ML_management.session import AuthSession
from ML_management.variables import (
    CACHED_LIST_FILENAME,
    CONFIG_KEY_ARTIFACTS,
    DATA,
    FLAVOR_NAME,
    JOB_ARTIFACT_DIRNAME,
    LEGACY_DATA,
    LOCAL_REGISTRY_PATH,
    MLCONFIG,
    MLMODEL_FILE_NAME,
    get_log_service_url,
)


def download_artifacts_by_name_version(
    name: str,
    version: Optional[int],
    path: str,
    dst_path: Optional[str] = None,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType] = ModelType.MODEL,
    verbose: bool = True,
) -> str:
    """Download an artifact by name and version to a local directory, and return a local path for it.

    Parameters
    ==========
    name: str
        Name of the entity.
    version: Optional[int] = None
        Version of the entity. Default: None, "latest" version is used.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    path: str = ""
        Specific path for artifacts download. Default: "", all artifacts will be downloaded.
    dst_path: Optional[str]: None
        Destination path. Default: None.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.
    Returns
    =======
    str
        Local path to the entity folder.
    """
    model_type = ModelType(model_type)
    if variables.NO_CACHE:
        local_path = CachedLoader.download_artifacts_by_name_version(
            name=name, version=version, model_type=model_type, path=path, dst_path=dst_path, verbose=verbose
        )
    else:
        local_path = CachedLoader().cached_download_artifacts_by_name_version(
            name=name, version=version, model_type=model_type, path=path, dst_path=dst_path, verbose=verbose
        )

    return local_path


def download_job_artifacts(job_id: int, path: str = "", dst_path: Optional[str] = None, verbose: bool = True) -> str:
    """Download an artifact file or directory from a job to a local directory, and return a local path for it.

    Parameters
    ==========
    job_id: int
        Id of the job.
    path: str = ""
        Specific path for artifacts download. Default: "", all artifacts will be downloaded.
    dst_path: Optional[str]: None
        Destination path. Default: None.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.
    Returns
    =======
    str
        Local path to artifacts.
    """
    if variables.NO_CACHE:
        local_path = CachedLoader.download_job_artifacts(job_id, path, dst_path, verbose=verbose)
    else:
        local_path = CachedLoader().cached_download_job_artifacts(job_id, path, dst_path, verbose=verbose)
    return local_path


def download_job_metrics(job_id: int, dst_path: Optional[str] = None, verbose: bool = True) -> str:
    """Download  directory of metrics from a job to a local directory, and return a local path for it.

    Parameters
    ==========
    job_id: int
        Id of the job.
    dst_path: Optional[str]: None
        Destination path. Default: None.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.
    Returns
    =======
    str
        Local path to metrics.
    """
    url = get_log_service_url("download_job_metrics")
    params = {"job_id": job_id}
    return _request_download_artifacts(url, params, dst_path, f"job_{job_id}_metrics", verbose=verbose)


def _load_model_type(
    name: str,
    version: Optional[int],
    model_type: ModelType,
    install_requirements: bool = False,
    dst_path: Optional[str] = None,
    kwargs_for_init=None,
    verbose: bool = True,
) -> LoadedObject:
    """Load model from local path."""
    if variables.NO_CACHE:
        local_path = CachedLoader.download_artifacts_by_name_version(
            name=name, version=version, model_type=model_type, path="", dst_path=dst_path, verbose=verbose
        )
    else:
        local_path = CachedLoader().cached_download_artifacts_by_name_version(
            name=name, version=version, model_type=model_type, path="", dst_path=dst_path, verbose=verbose
        )
    if install_requirements:
        _set_model_version_requirements(local_path)
    loaded_model = _load_model_src(local_path, kwargs_for_init)
    with open(os.path.join(local_path, MLCONFIG)) as f:
        config = yaml.safe_load(f)

    metainfo = ObjectMetaInfo(
        name=config["name"],
        version=config.get("version", 0),
        hash_artifacts=config.get("hash_artifacts", "unknown"),
        model_type=model_type,
    )
    loaded_object = LoadedObject(loaded_object=loaded_model, local_path=local_path, metainfo=metainfo)

    return loaded_object


def load_dataset(
    name: str,
    version: Optional[int] = None,
    install_requirements: bool = False,
    dst_path: Optional[str] = None,
    kwargs_for_init: Optional[dict] = None,
    verbose: bool = True,
) -> LoadedObject:
    """Download all model's files for loading model locally.

    Parameters
    ==========
    name: str
        Name of the dataset.
    version: Optional[int] = None
        Version of the dataset. Default: None, "latest" version is used.
    install_requirements: bool = False
        Whether to install dataset requirements. Default: False.
    dst_path: Optional[str]: None
        Destination path. Default: None.
    kwargs_for_init: Optional[dict]: None
        Kwargs for __init__ function of dataset loader when it would be loaded.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.
    Returns
    =======
    LoadedObject
        The object of the dataset to use.
    """
    return _load_model_type(
        name, version, ModelType.DATASET_LOADER, install_requirements, dst_path, kwargs_for_init, verbose
    )


def _set_model_version_requirements(local_path) -> None:
    """Installing requirements of the model locally."""
    with open(os.path.join(local_path, "requirements.txt")) as req:
        requirements = list(
            filter(
                lambda x: "ml-management" not in x.lower() and "mlflow" not in x.lower() and len(x),
                req.read().split("\n"),
            )
        )
    try:
        if requirements:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    "--default-timeout=100",
                    *requirements,
                ]
            )

    except Exception:
        print(traceback.format_exc())


def load_model(
    name: str,
    version: Optional[int] = None,
    install_requirements: bool = False,
    dst_path: Optional[str] = None,
    kwargs_for_init=None,
    verbose: bool = True,
) -> LoadedObject:
    """Download all model's files for loading model locally.

    Parameters
    ==========
    name: str
        Name of the model.
    version: Optional[int] = None
        Version of the model. Default: None, "latest" version is used.
    install_requirements: bool = False
        Whether to install model requirements. Default: False.
    dst_path: Optional[str]: None
        Destination path. Default: None.
    kwargs_for_init: Optional[dict]: None
        Kwargs for __init__ function of model when it would be loaded.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.
    Returns
    =======
    LoadedObject
        The object of the model to use.
    """
    return _load_model_type(name, version, ModelType.MODEL, install_requirements, dst_path, kwargs_for_init, verbose)


def load_executor(
    name: str,
    version: Optional[int] = None,
    install_requirements: bool = False,
    dst_path: Optional[str] = None,
    verbose: bool = True,
) -> LoadedObject:
    """Download all model's files for loading model locally.

    Parameters
    ==========
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    install_requirements: bool = False
        Whether to install executor requirements. Default: False.
    dst_path: Optional[str]: None
        Destination path. Default: None.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.
    Returns
    =======
    LoadedObject
        The object of the executor to use.
    """
    return _load_model_type(name, version, ModelType.EXECUTOR, install_requirements, dst_path, verbose=verbose)


def _untar_folder(buff, to_folder):
    try:
        with tarfile.open(mode="r|", fileobj=buff) as tar:
            print("START TAR", flush=True)
            tar.extractall(to_folder)
            print("END TAR", flush=True)
        print("END TARFILE OPEN", flush=True)
    except Exception as err:
        raise MLMClientError("Some error during untar the content.") from err


def _request_download_artifacts(
    url, params: dict, dst_path: Optional[str] = None, extra_dst_path: str = "", verbose: bool = True
):
    path = params.get("path", "")
    with AuthSession().get(url=url, params=params, stream=True) as response:
        _raise_error(response)
        untar = response.headers.get("untar") == "True"
        if dst_path is None:
            dst_path = tempfile.mkdtemp()
        dst_path = os.path.abspath(os.path.normpath(dst_path))
        local_path = os.path.normpath(os.path.join(dst_path, extra_dst_path, os.path.normpath(path)))
        total_size = int(response.headers.get("x-total-size"))

        with tqdm(
            total=total_size,
            disable=not verbose,
            unit_scale=True,
            unit_divisor=1024,
            unit="File",
        ) as pbar:
            if untar:
                r, w = os.pipe()
                with open(r, "rb") as buff:
                    try:
                        thread = threading.Thread(target=_untar_folder, args=(buff, local_path))
                        thread.start()
                    except Exception as err:
                        os.close(r)
                        os.close(w)
                        raise err

                    with open(w, "wb") as wfd:
                        print("BEFORE ALL WRITE", flush = True)
                        for chunk in response.iter_raw():
                            wfd.write(chunk)
                            wfd.flush()
                            pbar.update(len(chunk))
                        print("AFTER ALL WRITE", flush = True)
                        thread.join()
                        print("AFTER JOIN", flush = True)
                    print("AFTER CLOSING WRITE", flush = True)
                    return local_path
            else:
                dirs = os.path.dirname(local_path)
                if not os.path.exists(dirs):
                    os.makedirs(dirs)
                with open(local_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                        pbar.update(len(chunk))
                return local_path


def _load_model_src(local_path: str, kwargs_for_init: Optional[dict]):
    if not kwargs_for_init:
        kwargs_for_init = {}
    config_path = os.path.join(local_path, MLCONFIG)
    if os.path.exists(config_path):
        with open(config_path) as file:
            conf = yaml.safe_load(file)

        load_model_path = os.path.join(local_path, conf["load_model_path"])

    elif os.path.exists(os.path.join(local_path, MLMODEL_FILE_NAME)):
        with open(os.path.join(local_path, MLMODEL_FILE_NAME)) as file:
            conf = yaml.safe_load(file)

        # legacy data entity code path for backward compatibility
        code_data_path = (
            conf["flavors"][FLAVOR_NAME][DATA]
            if DATA in conf["flavors"][FLAVOR_NAME]
            else conf["flavors"][FLAVOR_NAME][LEGACY_DATA]
        )
        load_model_path = os.path.join(local_path, code_data_path)

    else:
        raise RuntimeError("MLConfig does not exist.")

    from ML_management.mlmanagement.utils import INIT_FUNCTION_NAME  # circular import

    parts = Path(load_model_path).parts
    extra_sys_path = str(Path(*parts[:-2]))
    module_for_importlib = ".".join(parts[-2:])

    if extra_sys_path not in sys.path:
        sys.path.append(extra_sys_path)
        if DebugJobLogContext().job_name:
            DebugJobLogContext().extra_sys_path.append(extra_sys_path)
    python_model = getattr(importlib.import_module(module_for_importlib), INIT_FUNCTION_NAME)(**kwargs_for_init)
    artifacts = Path(load_model_path) / CONFIG_KEY_ARTIFACTS
    if not artifacts.exists():
        artifacts.mkdir()

    python_model.artifacts = str(artifacts)

    return python_model


def _load_from_src(model_path: str, kwargs_for_init: Optional[dict] = None):
    if not kwargs_for_init:
        kwargs_for_init = {}

    model_path = os.path.abspath(model_path)
    parts = Path(model_path).parts
    extra_sys_path = str(Path(*parts[:-2]))
    module_for_importlib = ".".join(parts[-2:])
    sys.path.append(extra_sys_path)
    if DebugJobLogContext().job_name:
        DebugJobLogContext().extra_sys_path.append(extra_sys_path)
    from ML_management.mlmanagement.utils import INIT_FUNCTION_NAME  # circular import

    python_model = getattr(importlib.import_module(module_for_importlib), INIT_FUNCTION_NAME)(**kwargs_for_init)
    artifacts = Path(model_path) / CONFIG_KEY_ARTIFACTS
    if not artifacts.exists():
        artifacts.mkdir()

    python_model.artifacts = str(artifacts)

    return python_model


class CachedLoader:
    entity_key_pattern: str = "{model_type}:{name}:{version}"

    def __init__(self, registry_path: str = LOCAL_REGISTRY_PATH):
        self.registry_path = registry_path
        os.makedirs(registry_path, exist_ok=True)
        for type_entity in [ModelType.EXECUTOR.value, ModelType.MODEL.value, ModelType.DATASET_LOADER.value]:
            cache_path = os.path.join(registry_path, type_entity)
            os.makedirs(cache_path, exist_ok=True)
            list_path = os.path.join(cache_path, CACHED_LIST_FILENAME)
            if not os.path.exists(list_path):
                with open(list_path, "w") as f:
                    json.dump({}, f)

        job_artifacts = os.path.join(registry_path, JOB_ARTIFACT_DIRNAME)
        os.makedirs(job_artifacts, exist_ok=True)
        list_path = os.path.join(job_artifacts, CACHED_LIST_FILENAME)
        if not os.path.exists(list_path):
            with open(list_path, "w") as f:
                json.dump({}, f)

    @staticmethod
    def download_artifacts_by_name_version(
        name: str,
        version: Optional[int],
        model_type: ModelType,
        path: str,
        dst_path: Optional[str] = None,
        verbose: bool = True,
    ) -> str:
        url = get_log_service_url("download_artifacts_by_name_version")
        params = {
            "path": os.path.normpath(path) if path else path,
            "name": name,
            "model_type": model_type.value,
        }
        if version:
            params["version"] = version

        local_path = _request_download_artifacts(url, params, dst_path, verbose=verbose)
        return local_path

    def cached_download_artifacts_by_name_version(
        self,
        name: str,
        version: Optional[int],
        model_type: ModelType,
        path: str,
        dst_path: Optional[str] = None,
        verbose: bool = True,
    ) -> str:
        list_path = os.path.join(self.registry_path, model_type.value, CACHED_LIST_FILENAME)
        path = os.path.normpath(path) if path else path
        if not version:
            version = self._get_latest_object_version(name, model_type)

        key = self.entity_key_pattern.format(model_type=model_type, name=name, version=version)

        if dst_path is None:
            dst_path = os.path.join(self.registry_path, model_type.value, name, str(version))
            expected_cache_path = os.path.join(dst_path, path)
            if self._check_exist_cache(list_path, key, path) and os.path.exists(expected_cache_path):
                return os.path.abspath(expected_cache_path)

        local_path = self.download_artifacts_by_name_version(
            name=name, version=version, model_type=model_type, path=path, dst_path=dst_path, verbose=verbose
        )
        self._add_list_cache(list_path, key, path)
        return local_path

    @staticmethod
    def download_job_artifacts(
        job_id: int, path: str = "", dst_path: Optional[str] = None, verbose: bool = True
    ) -> str:
        url = get_log_service_url("download_job_artifacts")
        params = {"path": os.path.normpath(path) if path else path, "job_id": job_id}
        local_path = _request_download_artifacts(url, params, dst_path, verbose=verbose)
        return local_path

    def cached_download_job_artifacts(
        self, job_id: int, path: str = "", dst_path: Optional[str] = None, verbose: bool = True
    ) -> str:
        list_path = os.path.join(self.registry_path, JOB_ARTIFACT_DIRNAME, CACHED_LIST_FILENAME)
        path = os.path.normpath(path) if path else path
        if dst_path is None:
            dst_path = os.path.join(self.registry_path, JOB_ARTIFACT_DIRNAME, str(job_id))
            expected_cache_path = os.path.join(dst_path, path)

            if self._check_exist_cache(list_path, job_id, path) and os.path.exists(expected_cache_path):
                return os.path.abspath(expected_cache_path)

        local_path = self.download_job_artifacts(job_id, path, dst_path, verbose=verbose)
        self._add_list_cache(list_path, job_id, path)
        return local_path

    @staticmethod
    def _add_list_cache(list_path, key, path):
        with open(list_path) as f:
            entities = json.load(f)
        if path == "":
            entities[key] = [path]
        elif "" not in entities.get(key, []):
            entities[key] = entities.get(key, []) + [path]
        with open(list_path, "w") as f:
            json.dump(entities, f, indent=4)

    @staticmethod
    def _check_exist_cache(list_path: str, key: Union[int, Tuple[str, str]], path: str) -> bool:
        with open(list_path) as f:
            jobs = json.load(f)
        request_cached = jobs.get(key, [])
        if "" in request_cached:
            return True
        result = list(
            filter(
                lambda p: (Path(path).is_relative_to(Path(p))),
                request_cached,
            )
        )
        return bool(result)

    @staticmethod
    def _get_latest_object_version(name: str, model_type: ModelType) -> int:
        op = Operation(schema.Query)
        _version = schema.ObjectVersionOptionalInput(name=name, version=None)
        base_query = getattr(op, f"{model_type.value}_version_from_name_version")(
            **{f"{model_type.value}_version": _version}
        )
        base_query.version()
        version = send_graphql_request(op, json_response=False)
        return getattr(version, f"{model_type.value}_version_from_name_version").version
