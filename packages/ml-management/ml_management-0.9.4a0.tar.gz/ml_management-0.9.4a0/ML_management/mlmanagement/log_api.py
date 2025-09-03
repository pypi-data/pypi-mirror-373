import importlib
import io
import json
import math
import os
import sys
import tarfile
import threading
import time
import warnings
from contextlib import _GeneratorContextManager
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union

import httpx
import yaml
from sgqlc.operation import Operation
from tqdm.autonotebook import tqdm

from ML_management import variables
from ML_management.base_exceptions import *  # noqa: F403
from ML_management.base_exceptions import MLMClientError, MLMServerError
from ML_management.graphql.schema import MetricInput, ParamInput, schema
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.jsonschema_inference import infer_jsonschema
from ML_management.local_debug.local_logger import LocalLogger
from ML_management.mlmanagement.backend_api import get_debug
from ML_management.mlmanagement.batcher import Batcher
from ML_management.mlmanagement.metainfo import ObjectMetaInfo
from ML_management.mlmanagement.metric_autostepper import MetricAutostepper
from ML_management.mlmanagement.model_type import ModelType
from ML_management.mlmanagement.server_mlmanager_exceptions import *  # noqa: F403
from ML_management.mlmanagement.server_mlmanager_exceptions import (
    AuthError,
    InvalidExperimentNameError,
    ModelTypeIsNotFoundError,
)
from ML_management.mlmanagement.utils import (
    INIT_FUNCTION_NAME,
    calculate_hash_directory,
    calculate_size,
    is_model_name_valid,
    validate_predict_config,
)
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.registry.exceptions import *  # noqa: F403
from ML_management.session import AuthSession
from ML_management.variables import (
    CONDA_SIZE_LIMIT,
    CONFIG_KEY_ARTIFACTS,
    DATA,
    DEFAULT_EXPERIMENT,
    EXPERIMENT_NAME_FOR_DATASET_LOADER,
    EXPERIMENT_NAME_FOR_EXECUTOR,
    FILENAME_FOR_INFERENCE_CONFIG,
    INFERENCE_CONFIG_LIMIT,
    get_log_service_url,
)


def _log_object_src(
    artifact_path,
    model_path: str,
    description: str,
    experiment_name: str,
    model_type: ModelType = ModelType.MODEL,
    model_version_tags: Optional[Dict[str, Union[str, list]]] = None,
    registered_model_name: str = "default_name",
    source_model_name=None,
    source_model_version=None,
    source_executor_name=None,
    source_executor_version=None,
    source_executor_role=None,
    upload_model_mode=None,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    start_build: bool = True,
    create_venv_pack: bool = False,
    additional_local_packages: Optional[Union[List[str], str]] = None,
    force: bool = False,
    verbose: bool = True,
) -> ObjectMetaInfo:
    """
    Log a src model with custom inference logic and optional data dependencies as an artifact.

    Current run is using.
    Parameter registered_model_name must be not empty string,
            consist of alphanumeric characters, '_'
            and must start and end with an alphanumeric character.
            Validation regexp: "(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"
    You cannot specify the parameters: loader_module, data_path and the parameters: python_model, artifacts together.
    """
    from ML_management.mlmanagement.upload_model_mode import UploadModelMode  # circular import

    visibility = VisibilityOptions(visibility)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Path: {model_path} does not exist.")

    if os.path.basename(model_path) == DATA:
        raise RuntimeError(f"The folder should not be named '{DATA}'. Please rename.") from None

    conda_path = os.path.join(model_path, "conda.yaml")

    if not os.path.exists(conda_path):
        raise FileNotFoundError("There is no conda.yaml file.")

    if os.path.getsize(conda_path) > CONDA_SIZE_LIMIT:
        raise RuntimeError("conda.yaml is too big.")

    inference_config_path = os.path.join(model_path, CONFIG_KEY_ARTIFACTS, FILENAME_FOR_INFERENCE_CONFIG)
    if os.path.isfile(inference_config_path) and os.path.getsize(inference_config_path) > INFERENCE_CONFIG_LIMIT:
        raise RuntimeError(f"{FILENAME_FOR_INFERENCE_CONFIG} is too big.")

    try:
        with open(conda_path) as conda_file:
            dependencies = yaml.safe_load(conda_file)["dependencies"]  # noqa: F841
    except Exception:
        raise RuntimeError("conda.yaml not valid.") from None

    if not description or not isinstance(description, str):
        raise RuntimeError("Please fill in the description.") from None

    if not is_model_name_valid(registered_model_name):
        raise RuntimeError(
            "Parameter 'registered_model_name' must be not empty string, "
            "consist of alphanumeric characters, '_' "
            "and must start and end with an alphanumeric character."
            "Validation regexp: '(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+'"
        )
    del UploadModelMode  # need to delete this because it is not JSON serializable
    if create_venv_pack:
        validate_predict_config(path=os.path.join(f"{model_path}", "artifacts", f"{FILENAME_FOR_INFERENCE_CONFIG}"))

    if model_version_tags:
        for key, value in model_version_tags.items():
            if not isinstance(value, list):
                model_version_tags[key] = [value]
    hash_artifacts = calculate_hash_directory(model_path)

    if get_debug():
        return LocalLogger().log_model(
            registered_model_name,
            model_type,
            model_path,
            hash_artifacts,
        )

    if not force:
        versions_hash = _get_version_hash(registered_model_name, model_type, hash_artifacts, visibility)
        if versions_hash:
            warnings.warn(f"You are trying to upload a copy of an existing versions: {versions_hash}")
            return ObjectMetaInfo(
                name=versions_hash[0].name,
                version=versions_hash[0].version,
                model_type=model_type,
                hash_artifacts=hash_artifacts,
            )

    old_python_path = sys.path.copy()
    old_sys_modules = sys.modules.copy()
    try:
        model_path = os.path.abspath(model_path)
        parts = Path(model_path).parts
        extra_sys_path = str(Path(*parts[:-1]))
        module_for_importlib = ".".join(parts[-1:])
        if additional_local_packages:
            extra_sys_path = str(Path(*parts[:-2]))
            module_for_importlib = ".".join(parts[-2:])
        sys.path.append(extra_sys_path)
        get_object_func = getattr(importlib.import_module(module_for_importlib), INIT_FUNCTION_NAME)
        python_model = get_object_func()  # noqa: F841
        kwargs = {
            "artifact_path": artifact_path,
            "model_path": model_path,
            "description": description,
            "model_version_tags": model_version_tags,
            "python_model": python_model,
            "registered_model_name": registered_model_name,
            "source_model_name": source_model_name,
            "source_model_version": source_model_version,
            "source_executor_name": source_executor_name,
            "source_executor_version": source_executor_version,
            "source_executor_role": source_executor_role,
            "upload_model_mode": upload_model_mode,
            "visibility": visibility,
            "start_build": start_build,
            "create_venv_pack": create_venv_pack,
            "additional_local_packages": additional_local_packages,
            "get_object_func": get_object_func,
            "experiment_name": experiment_name,
            "hash_artifacts": hash_artifacts,
        }
        response = _request_log_model(kwargs, verbose)
        _raise_error(response)
        result = response.json()
    except Exception as err:
        raise err
    finally:
        sys.path = old_python_path
        for module in set(sys.modules) - set(old_sys_modules):
            if hasattr(sys.modules[module], "__file__"):
                if sys.modules[module].__file__ and extra_sys_path in sys.modules[module].__file__:
                    sys.modules.pop(module)

    if additional_local_packages:
        name_version = json.loads(response.content.decode("utf-8"))
        if not isinstance(additional_local_packages, list):
            additional_local_packages = [additional_local_packages]
        for package in additional_local_packages:
            response = _request_log_artifacts(
                package, DATA, name_version["name"], int(name_version["version"]), model_type, verbose
            )
            _raise_error(response)

    return ObjectMetaInfo(
        name=result["name"], version=result["version"], model_type=model_type, hash_artifacts=hash_artifacts
    )


def _get_version_hash(name: str, model_type: ModelType, hash_artifacts: str, visibility: VisibilityOptions) -> list:
    query_name = {
        ModelType.MODEL: "get_model_versions_with_hash",
        ModelType.DATASET_LOADER: "get_dataset_loader_versions_with_hash",
        ModelType.EXECUTOR: "get_executor_versions_with_hash",
    }[model_type]

    op = Operation(schema.Query)
    base = getattr(op, query_name)(name=name, hash_artifacts=hash_artifacts, visibility=visibility.name)
    base.name()
    base.version()
    result = send_graphql_request(op=op, json_response=False)
    return getattr(result, query_name)


def log_executor_src(
    model_path: str,
    registered_name: str,
    description: str,
    start_build: bool = False,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    additional_local_packages: Optional[Union[List[str], str]] = None,
    force: bool = False,
    verbose: bool = True,
) -> ObjectMetaInfo:
    """
    Upload executor using folder with source code of the executor.

    model_path folder must contain "__init__.py" file with get_object function
    which have to return instance of the executor.
    Also model_path must contain "conda.yaml" file with dependencies of the executor
    model_path can optionally contain "artifacts" folder with files/folders,
    which would be automatically uploaded with executor
    and path to them can be accessed with self.artifacts within executor class.

    Parameters
    ----------
    model_path: str
        Path to folder with executor.
    registered_name: str
        Name of the executor.
    description: str
        Description of the executor
    start_build: bool
        Is to start build image of the executor right after it was logged. Defaults to False.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of this executor to other users. Possible values VisibilityOptions.PRIVATE, PUBLIC.
        Defaults to PRIVATE.
    additional_local_packages: Optional[Union[List[str], str]] = None
        Path or list of paths to folder with local dependencies which are not within model_path folder.
        Defaults to None.
    force: str
        This option removes the restriction on logging duplicate versions.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.

    Returns
    -------
    ObjectMetaInfo

    """
    return _log_object_src(
        artifact_path="",
        description=description,
        registered_model_name=registered_name,
        start_build=start_build,
        model_path=model_path,
        visibility=visibility,
        additional_local_packages=additional_local_packages,
        model_type=ModelType.EXECUTOR,
        experiment_name=EXPERIMENT_NAME_FOR_EXECUTOR,
        force=force,
        verbose=verbose,
    )


def log_dataset_loader_src(
    model_path: str,
    registered_name: str,
    description: str,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    additional_local_packages: Optional[Union[List[str], str]] = None,
    force: bool = False,
    verbose: bool = True,
) -> ObjectMetaInfo:
    """
    Upload dataset loader using folder with source code of the dataset loader.

    model_path folder must contain "__init__.py" file with get_object function
    which have to return instance of the dataset loader.
    Also model_path must contain "conda.yaml" file with dependencies of the dataset loader
    model_path can optionally contain "artifacts" folder with files/folders,
    which would be automatically uploaded with dataset loader
    and path to them can be accessed with self.artifacts within dataset loader class.

    Parameters
    ----------
    model_path: str
        Path to folder with dataset loader.
    registered_name: str
        Name of the dataset loader.
    description: str
        Description of the dataset loader
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of this dataset loader to other users. Possible values VisibilityOptions.PRIVATE, PUBLIC.
        Defaults to PRIVATE.
    additional_local_packages: Optional[Union[List[str], str]] = None
        Path or list of paths to folder with local dependencies which are not within model_path folder.
        Defaults to None.
    force: str
        This option removes the restriction on logging duplicate versions.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.

    Returns
    -------
    ObjectMetaInfo
    """
    return _log_object_src(
        artifact_path="",
        description=description,
        registered_model_name=registered_name,
        model_path=model_path,
        visibility=visibility,
        additional_local_packages=additional_local_packages,
        model_type=ModelType.DATASET_LOADER,
        experiment_name=EXPERIMENT_NAME_FOR_DATASET_LOADER,
        force=force,
        verbose=verbose,
    )


def log_model_src(
    model_path: str,
    registered_name: str,
    description: str,
    start_build: bool = True,
    model_version_tags: Optional[Dict[str, Union[str, list]]] = None,
    experiment_name: str = DEFAULT_EXPERIMENT,
    create_venv_pack: bool = False,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    additional_local_packages: Optional[Union[List[str], str]] = None,
    force: bool = False,
    verbose: bool = True,
) -> ObjectMetaInfo:
    """
    Log model to remote server.

    Parameters
    ----------
    model_path: str
        Path to the folder with the model files(*model*.py, conda.yaml, __init__.py with get object function, see docs)
    registered_name: str
        The name of the model that will be assigned to the model in the model registry.
        Parameter registered_name should match regexp ``"(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"``.
    description: str
        Description of the model.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of this model to other users. Possible values VisibilityOptions.PRIVATE, PUBLIC.
        Defaults to PRIVATE.
    start_build: bool = True
        Whether to start building the image with the model requirements immediately after uploading.
        This can speed up the subsequent build of the task image. Default: True.
    model_version_tags: Optional[Dict[str, Union[str, list]]] = None
        Define model version tags. Default: None.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    create_venv_pack: bool = False
        Whether to prepare venv pack for future inference. Default: False.
    additional_local_packages: Optional[Union[List[str], str]] = None
        Path or list of paths to folder with local dependencies which are not within model_path folder.
        Defaults to None.
    force: str
        This option removes the restriction on logging duplicate versions.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.

    Returns
    =======
    ObjectMetaInfo
    """
    return _log_object_src(
        artifact_path="",
        description=description,
        registered_model_name=registered_name,
        model_path=model_path,
        start_build=start_build,
        model_version_tags=model_version_tags,
        create_venv_pack=create_venv_pack,
        visibility=visibility,
        additional_local_packages=additional_local_packages,
        model_type=ModelType.MODEL,
        experiment_name=experiment_name,
        force=force,
        verbose=verbose,
    )


def log_artifact(local_path: str, artifact_path: Optional[str] = None, verbose: bool = True) -> None:
    """
    Log a local file or directory as an artifact of the currently active run.

    If no run is active, this method will create a new active run.

    Parameters
    ==========
    local_path: str
        Path to the file to write.
    artifact_path: Optional[str] = None
        If provided, the directory to write to.
    verbose: bool = True
        Whether to disable the entire progressbar wrapper.

    Returns
    =======
    None
    """
    if get_debug():
        LocalLogger().log_artifact(local_path=local_path, artifact_path=artifact_path)
        return
    response = _request_log_artifacts(local_path, artifact_path, verbose=verbose)
    return _raise_error(response)


def _request_log_model(kwargs: dict, verbose: bool = True):
    """
    Send request for log_model function.

    Steps for log model:
    0) Infer jsonschema, raise if it is invalid
    1) open temporary directory
    2) Do init model locally
    3) Pack it to tar file
    4) Send it to server to log model there.
    """
    delete_args_for_save_model_func = [
        "description",
        "model_version_tags",
        "artifact_path",
        "registered_model_name",
        "await_registration_for",
        # now, extra arguments
        "upload_model_mode",
        "source_model_name",
        "source_model_version",
        "visibility",
        "source_executor_name",
        "source_executor_version",
        "source_executor_role",
        "start_build",
        "create_venv_pack",
    ]  # not need for save_model

    extra_imports_args = [
        "submodules",
        "module_name",
        "used_modules_names",
        "extra_modules_names",
        "root_module_name",
        "linter_check",
    ]

    delete_args_for_log_func = [
        "python_model",
        "artifacts",
        "conda_env",
        "pip_requirements",
        "extra_pip_requirements",
        "additional_local_packages",
        "conda_file",
        "dependencies",
        "get_object_func",
    ]  # not need for log model on server

    for delete_arg in extra_imports_args:
        kwargs.pop(delete_arg, None)
    kwargs_for_save_model = kwargs.copy()
    for delete_arg in delete_args_for_save_model_func:
        kwargs_for_save_model.pop(delete_arg, None)
    python_model = kwargs_for_save_model["python_model"]
    get_object_func = kwargs_for_save_model.get("get_object_func")
    # import some modules here because of circular import
    from ML_management.dataset_loader.dataset_loader_pattern import DatasetLoaderPattern
    from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import (
        dataset_loader_pattern_to_methods,
    )
    from ML_management.executor.base_executor import BaseExecutor
    from ML_management.executor.executor_pattern_to_methods_map import executor_pattern_to_methods
    from ML_management.model.model_type_to_methods_map import model_pattern_to_methods
    from ML_management.model.patterns.model_pattern import Model

    experiment_name = kwargs.get("experiment_name", DEFAULT_EXPERIMENT)

    if python_model is not None:
        if isinstance(python_model, Model):
            kwargs["model_type"] = ModelType.MODEL
            model_to_methods = model_pattern_to_methods
            if experiment_name in [
                EXPERIMENT_NAME_FOR_EXECUTOR,
                EXPERIMENT_NAME_FOR_DATASET_LOADER,
            ]:
                raise InvalidExperimentNameError(ModelType.MODEL.value, experiment_name)
        elif isinstance(python_model, BaseExecutor):
            kwargs["model_type"] = ModelType.EXECUTOR
            model_to_methods = executor_pattern_to_methods

            if experiment_name != EXPERIMENT_NAME_FOR_EXECUTOR:
                raise InvalidExperimentNameError(ModelType.EXECUTOR.value, experiment_name)
            # collect all needed model's methods
            kwargs["desired_model_methods"] = python_model.desired_model_methods
            kwargs["desired_dataset_loader_methods"] = python_model.desired_dataset_loader_methods
        elif isinstance(python_model, DatasetLoaderPattern):
            kwargs["model_type"] = ModelType.DATASET_LOADER
            model_to_methods = dataset_loader_pattern_to_methods
            if experiment_name != EXPERIMENT_NAME_FOR_DATASET_LOADER:
                raise InvalidExperimentNameError(kwargs["model_type"].value, experiment_name)
        else:
            raise ModelTypeIsNotFoundError()

        # now we need to infer schemas for methods.
        methods_schema = {}
        for model_type, methods_name_to_schema_map in model_to_methods.items():
            if isinstance(python_model, model_type):
                for method_name_to_schema in methods_name_to_schema_map:
                    model_method = getattr(python_model, method_name_to_schema.value, None)
                    model_method_schema = infer_jsonschema(model_method, get_object_func)
                    methods_schema[method_name_to_schema.value] = model_method_schema

        kwargs["model_method_schemas"] = methods_schema

        for delete_arg in delete_args_for_log_func:
            kwargs.pop(delete_arg, None)

        log_request = {
            "secret_uuid": variables.secret_uuid,
        }

        artifacts_path = os.path.join(kwargs["model_path"], CONFIG_KEY_ARTIFACTS)
        if os.path.isfile(artifacts_path):
            raise Exception(f"The artifact file {artifacts_path} is invalid. The artifact must be a directory.")

        model_folder = kwargs["model_path"]

        del kwargs["model_path"]
        kwargs["loader_module"] = "ML_management.loader.loader"
        log_request["kwargs"] = kwargs
        return _open_pipe_send_request(model_folder, log_request, url=get_log_service_url("log_model"), verbose=verbose)

    else:
        raise Exception("python_model parameter must be specified")


def _request_log_artifacts(
    local_path,
    artifact_path,
    name: Optional[str] = None,
    version: Optional[int] = None,
    model_type: Optional[ModelType] = None,
    verbose: bool = True,
):
    """Send request for log artifact."""
    log_artifact_request = {
        "artifact_path": artifact_path,
        "secret_uuid": variables.secret_uuid,
        "model_type": model_type,
        "name": name,
        "version": version,
    }
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Path: {local_path} does not exist.")
    if not os.path.isdir(local_path):
        basename = os.path.basename(os.path.normpath(local_path))
        with open(local_path, "rb") as file:
            url = get_log_service_url("log_artifact")

            # upload multipart
            data = {"log_request": json.dumps(log_artifact_request)}
            headers = {"Transfer-Encoding": "chunked"}

            file_content_type = "application/octet-stream"

            files = {"file": (basename, file, file_content_type)}

            with AuthSession().post(
                url=url,
                stream=False,
                data=data,
                files=files,
                headers=headers,
            ) as response:
                return response

    return _open_pipe_send_request(
        local_path, log_artifact_request, url=get_log_service_url("log_artifact"), verbose=verbose
    )


def _raise_error(response: httpx.Response):
    if response.status_code == 500:
        raise MLMServerError("Internal server error.")
    if response.status_code != 200:
        detail = response.read().decode()
        if not detail:
            raise MLMServerError("Internal server error.")
        try:
            detail = json.loads(detail).get("detail")
        except Exception:
            raise MLMServerError(f"Server error '{detail}' with code {response.status_code}") from None
        if not (
            isinstance(detail, dict) and "exception_class" in detail and ("params" in detail or "message" in detail)
        ):
            raise MLMServerError(detail)
        if "params" in detail:
            error = getattr(sys.modules[__name__], detail["exception_class"])(**detail["params"])
        else:
            error = getattr(sys.modules[__name__], detail["exception_class"])(detail["message"])
        if isinstance(error, AuthError):
            error.args = (
                f"{error.args[0]}. "
                "Possible reason: you are trying to upload a version of an object owned by another user.",
            )
        raise error


class ProgressFile(io.RawIOBase):
    def __init__(self, file_obj, pbar):
        self.file_obj = file_obj
        self.pbar = pbar

    def read(self, size=-1):
        data = self.file_obj.read(size)
        self.pbar.update(len(data))
        return data


def _open_pipe_send_request(folder, request_dict, url, verbose: bool = True):
    total_size = calculate_size(folder)

    r, w = os.pipe()

    try:
        thread = threading.Thread(target=_tar_folder, args=(w, folder))
        thread.start()
    except Exception as err:
        os.close(r)
        os.close(w)
        raise err
    with tqdm(
        total=total_size,
        disable=not verbose,
        unit_scale=True,
        unit_divisor=1024,
        unit="File",
    ) as pbar:
        with open(r, "rb") as buff:
            progress_file = ProgressFile(buff, pbar)

            with _request(url, request_dict, progress_file, os.path.basename(folder), True) as response:
                return response


def _request(
    url,
    request_dict,
    file=None,
    basename=None,
    is_tar=False,
    stream=False,
) -> _GeneratorContextManager:
    """Create log request and send it to server."""
    if not file:
        return AuthSession().post(url=url, stream=stream, json=request_dict)

    # upload multipart
    data = {"log_request": json.dumps(request_dict)}
    headers = {"Transfer-Encoding": "chunked"}

    file_content_type = "application/octet-stream"
    if is_tar:
        file_content_type = "application/x-tar"

    files = {"file": (basename, file, file_content_type)}

    return AuthSession().post(
        url=url,
        stream=stream,
        data=data,
        files=files,
        headers=headers,
    )


def _tar_folder(w, model_folder):
    try:
        with open(w, "wb") as buff:
            with tarfile.open(mode="w|", fileobj=buff) as tar:
                tar.add(model_folder, arcname=os.path.basename(model_folder))
    except Exception as err:
        raise MLMClientError("Some error during tar the content.") from err


def log_metric(key: str, value: float, step: int = 0, no_wait=False):
    """
    Log a metric under the current job.

    Parameters
    ==========
    key: str
        Metric name (string).
        This string may only contain alphanumerics, underscores (_), dashes (-),
        periods (.), spaces ( ), and slashes (/).
        All backend stores will support keys up to length 250, but some may support larger keys.

    value: float
        Metric value (float). Note that some special values such as +/-
        Infinity may be replaced by other values depending on the store.
        For example, the SQLAlchemy store replaces +/- Infinity with max / min float values.
        All backend stores will support values up to length 5000, but some may support larger values.

    step: int
        Metric step (int). Defaults to zero if unspecified.

    no_wait: bool
        The no_wait flag allows you to log metrics directly, without using optimization (batching).

    Returns
    =======
    None
    """
    if not variables.secret_uuid:
        raise MLMClientError("The log_metric function must be called from the active job.")
    if not (isinstance(value, (float, int)) and math.isfinite(value)):
        warnings.warn(f"The log_metric function can log only float or integer values. Value {value} is not log.")
        return

    if not isinstance(key, str):
        warnings.warn(
            f"The log_metric function can log only str name metric and float or integer values. "
            f"{key}: {value} is not log."
        )
        return
    timestamp = int(time.time() * 10e6)
    autostep = MetricAutostepper().get_next_step(key)

    metric = {"key": key, "value": value, "step": step, "timestamp": timestamp, "autostep": autostep}
    if get_debug():
        LocalLogger().log_metrics([metric])
        return

    if no_wait:
        op = Operation(schema.Mutation)
        op.log_metric(
            metric=MetricInput(**metric),
            secret_uuid=variables.secret_uuid,
        )
        try:
            return send_graphql_request(op, json_response=False).log_metric
        except Exception as err:
            warnings.warn(str(err))
    else:
        Batcher().log_metrics([MetricInput(key=key, value=value, step=step, timestamp=timestamp, autostep=autostep)])


def log_metrics(metrics: Dict[str, float], step: int = 0, no_wait=False):
    """
    Log a metrics under the current job.

    Parameters
    ==========
    metrics: dict[str, float]
        Key(string): metric name.
        This string may only contain alphanumerics, underscores (_), dashes (-),
        periods (.), spaces ( ), and slashes (/).
        All backend stores will support keys up to length 250, but some may support larger keys.
        Value(float): metric value. Note that some special values such as +/-
        Infinity may be replaced by other values depending on the store.
        For example, the SQLAlchemy store replaces +/- Infinity with max / min float values.
        All backend stores will support values up to length 5000, but some may support larger values.

    step: int
        Metric step (int). Defaults to zero if unspecified.

    no_wait: bool
        The no_wait flag allows you to log metrics directly, without using optimization (batching).

    Returns
    =======
    None
    """
    if not variables.secret_uuid:
        raise MLMClientError("The log_metric function must be called from the active job.")

    metrics_to_log = {}
    for key, value in metrics.items():
        if not (isinstance(value, (float, int)) and math.isfinite(value)):
            warnings.warn(f"The log_metrics function can log only float or integer values. {key}: {value} is not log.")
            continue
        if not isinstance(key, str):
            warnings.warn(
                f"The log_metrics function can log only str name metric and float or integer values. "
                f"{key}: {value} is not log."
            )
            continue
        metrics_to_log[key] = value
    timestamp = int(time.time() * 10e6)

    metrics = [
        {
            "key": key,
            "value": value,
            "step": step,
            "timestamp": timestamp,
            "autostep": MetricAutostepper().get_next_step(key),
        }
        for key, value in metrics_to_log.items()
    ]

    if get_debug():
        LocalLogger().log_metrics(metrics)
        return
    metrics = [MetricInput(**m) for m in metrics]
    if no_wait:
        op = Operation(schema.Mutation)
        op.log_metrics(
            metrics=metrics,
            secret_uuid=variables.secret_uuid,
        )
        try:
            return send_graphql_request(op, json_response=False).log_metrics
        except Exception as err:
            warnings.warn(str(err))
    else:
        Batcher().log_metrics(metrics)


def _log_param(key: str, value: str):
    """
    Log str parameter (e.g. model hyperparameter) under the current job.

    Parameters
    ==========
    key: str
        Param name (string).
        This string may only contain alphanumerics, underscores (_), dashes (-),
        periods (.), spaces ( ), and slashes (/).
        All backend stores will support keys up to length 250, but some may support larger keys.

    value: str
        Param value (string).

    Returns
    =======
    None
    """
    if not isinstance(value, str):
        warnings.warn(f"The log_param function can log only string values. Value {value} is not log.")
        return
    if not variables.secret_uuid:
        raise MLMClientError("The log_param function must be called from the active job.")

    if get_debug():
        LocalLogger().log_params({key: value})
        return
    op = Operation(schema.Mutation)
    op.log_param(param=ParamInput(key=key, value=value), secret_uuid=variables.secret_uuid)
    try:
        return send_graphql_request(op, json_response=False).log_param
    except Exception as err:
        warnings.warn(str(err))


def _log_params(params: Dict[str, str]):
    """
    Log a batch of params for the current job.

    Parameters
    ==========
    params: dict
        Key parameter value pairs.
        Кey is the name of the parameter (string).
        This string may only contain alphanumerics, underscores (_), dashes (-),
        periods (.), spaces ( ), and slashes (/).
        All backend stores will support keys up to length 250, but some may support larger keys.
        Param value (string).

    Returns
    =======
    None
    """
    if not variables.secret_uuid:
        raise MLMClientError("The log_metric function must be called from the active job.")

    for key, value in params:
        if not isinstance(value, str):
            warnings.warn(f"The log_params function can log only string values. Value {value} is not logged.")
        params.pop(key)
    if not params:
        return
    if get_debug():
        LocalLogger().log_params(params)
        return

    op = Operation(schema.Mutation)
    op.log_params(
        params=[ParamInput(key=key, value=value) for key, value in params.items()], secret_uuid=variables.secret_uuid
    )
    try:
        return send_graphql_request(op, json_response=False).log_params
    except Exception as err:
        warnings.warn(str(err))
