import json
import logging
import os
import shutil
import sys
import warnings
from typing import Optional, Union

from ML_management import variables
from ML_management.executor import BaseExecutor
from ML_management.graphql.schema import ExecutionJob
from ML_management.job.job import Job
from ML_management.local_debug.debug_job_result import DebugJobLogContext, DebugJobResult
from ML_management.local_debug.local_logger import LocalLogger
from ML_management.mlmanagement.backend_api import get_debug, set_debug
from ML_management.mlmanagement.load_api import _load_from_src, load_dataset, load_executor, load_model
from ML_management.model.model_type_to_methods_map import ModelMethodName
from ML_management.sdk.parameters import (
    AnyDatasetLoaderForm,
    AnyModelForm,
    DatasetLoaderForm,
    ModelForm,
    UploadAnyNewModelsForm,
    UploadOneNewModelForm,
)
from ML_management.variables import DEBUG_REGISTRY_PATH, LOCAL_REGISTRY_PATH

LOCAL_DEBUG_DIR = "mlm_registry"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class DebugContext:
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.old_debug = True

    def __enter__(self):
        self.old_debug = get_debug()
        set_debug(True)
        DebugJobLogContext().job_name = self.job_name
        DebugJobLogContext().old_python_path = sys.path.copy()
        DebugJobLogContext().old_sys_modules = sys.modules.copy()
        DebugJobLogContext().job_id = LocalLogger().get_job_id()
        variables.secret_uuid = DebugJobLogContext().job_id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_debug(self.old_debug)
        variables.secret_uuid = None
        sys.path = DebugJobLogContext().old_python_path
        for module in set(sys.modules) - set(DebugJobLogContext().old_sys_modules):
            if hasattr(sys.modules[module], "__file__"):
                if sys.modules[module].__file__ and any(
                    extra in sys.modules[module].__file__ for extra in DebugJobLogContext().extra_sys_path
                ):
                    sys.modules.pop(module)
        DebugJobLogContext().clear()


def add_ml_job_local(
    job_executor_name: str,
    executor_params: dict,
    models_pattern: Union[ModelForm, AnyModelForm],
    data_pattern: Union[DatasetLoaderForm, AnyDatasetLoaderForm],
    job_name: str,
    job_executor_version: Optional[int] = None,
    upload_models_params: Union[UploadOneNewModelForm, UploadAnyNewModelsForm, None] = None,
    gpu: bool = False,
    model_paths: Optional[Union[dict, str]] = None,
    dataset_loader_paths: Optional[Union[dict, str]] = None,
    executor_path: Optional[str] = None,
) -> DebugJobResult:
    """
    Create local job for debugging purposes.

    Parameters
    ----------
    job_executor_name: str
        Name of the executor that will execute the job.
    executor_params: Dict[str, ...]
        Dictionary of executor parameters.
        Example::

            {
                'executor_param1': 'value1',
                'executor_param2': 'value2',
                'executor_param3': 'value3',
                ...
            }

    models_pattern: Union[ModelForm, AnyModelForm]
        Necessary information for using the models.
    data_pattern: Union[DatasetLoaderForm, AnyDatasetLoaderForm]
        Necessary information for using the datasets.
    gpu: bool = False
        Whether to use GPU for this job or not. Default: False
    job_executor_version: Optional[int] = None
        Version of the executor that will execute the job. Default: None, "latest" version is used.
    upload_models_params: Union[UploadOneNewModelForm, UploadAnyNewModelsForm],
        Parameters to log new models. If you want to log new model or model version,
        you have to specify this parameter. Default: None.
        The value None means that no new model will be uploaded.
    job_name: Optional[str] = None
        Name of the created job.
    model_paths: Optional[Union[dict, str]] = None
        Local paths to the models.
    dataset_loader_paths: Optional[Union[dict, str]] = None
        Local paths to the dataset loaders.
    executor_path: Optional[Union[dict, str]] = None
        Local path to the executor.

    Returns
    -------
    DebugJobResult
        Result of the Job.
    """
    if not get_debug():
        warnings.warn("The debug environment variable must be set to True.")

    if not isinstance(models_pattern, (ModelForm, AnyModelForm)):
        raise TypeError("Parameter models must have type ModelForm or AnyModelForm.")
    if not isinstance(data_pattern, (DatasetLoaderForm, AnyDatasetLoaderForm)):
        raise TypeError("Parameter data_pattern must have type DatasetLoaderForm or AnyDatasetLoaderForm.")
    if (
        upload_models_params is not None
        and not isinstance(upload_models_params, UploadOneNewModelForm)
        and not isinstance(upload_models_params, UploadAnyNewModelsForm)
    ):
        raise TypeError(
            "Parameter upload_params must have type UploadOneNewModelForm or UploadAnyNewModelsForm or be None."
        )
    if upload_models_params is None:
        upload_models_params = UploadAnyNewModelsForm(upload_models_params=[])
    logger.info("Start Job")
    with DebugContext(job_name):
        models = models_pattern.serialize_gql()
        data_params = data_pattern.serialize_gql()
        upload_params = upload_models_params.serialize_gql()

        if executor_path:
            preload_executor = _load_from_src(executor_path, None)

        else:
            preload_executor = load_executor(job_executor_name, job_executor_version, install_requirements=True)
            job_executor_version = preload_executor.metainfo.version
            preload_executor = preload_executor.loaded_object

        if job_executor_version is None:
            job_executor_version = 0
        preload_models = {}
        if model_paths and not isinstance(model_paths, dict):
            model_paths = {BaseExecutor.DEFAULT_ROLE: model_paths}
        elif not model_paths:
            model_paths = {}

        model_roles_expected = {model["role"] for model in models}
        if set(model_paths.keys()) - model_roles_expected:
            raise ValueError(f"Extra model roles passed: {set(model_paths.keys()) - model_roles_expected}")

        preload_dataset_loaders = {}
        if dataset_loader_paths and not isinstance(dataset_loader_paths, dict):
            dataset_loader_paths = {BaseExecutor.DEFAULT_ROLE: dataset_loader_paths}
        elif not dataset_loader_paths:
            dataset_loader_paths = {}

        dataset_loader_roles_expected = {dataset_loader["role"] for dataset_loader in data_params}
        if set(dataset_loader_paths.keys()) - dataset_loader_roles_expected:
            raise ValueError(
                f"Extra dataset loader roles passed: {set(model_paths.keys()) - dataset_loader_roles_expected}"
            )
        models_roles = set()
        for model in models:
            role = model["role"]
            models_roles.add(role)
            kwargs_for_init = _get_init_parameters_from_dict(model["modelParams"]["listModelMethodParams"])

            if role in upload_params:
                model["uploadParams"] = upload_params[role]
                if model["uploadParams"]["newModelName"] is None:
                    model["uploadParams"]["newModelName"] = model["modelParams"]["modelVersionChoice"]["name"]
            else:
                model["uploadParams"] = None
            if role in model_paths:
                preload_models[role] = _load_from_src(model_paths[role], kwargs_for_init)
                if not model["modelParams"]["modelVersionChoice"]["version"]:
                    model["modelParams"]["modelVersionChoice"]["version"] = 0
                continue
            preload_model = load_model(
                model["modelParams"]["modelVersionChoice"]["name"],
                model["modelParams"]["modelVersionChoice"]["version"],
                install_requirements=True,
                kwargs_for_init=kwargs_for_init,
            )
            model["modelParams"]["modelVersionChoice"]["version"] = preload_model.metainfo.version
            preload_models[role] = preload_model.loaded_object
        if not set(upload_params.keys()).issubset(models_roles):
            raise ValueError("Roles in upload params must be subset of roles in model params.")

        for dataset_loader in data_params:
            role = dataset_loader["role"]
            kwargs_for_init = _get_init_parameters_from_dict(
                dataset_loader["dataParams"]["listDatasetLoaderMethodParams"]
            )
            if role in dataset_loader_paths:
                preload_dataset_loaders[role] = _load_from_src(dataset_loader_paths[role], kwargs_for_init)

                if not dataset_loader["dataParams"]["datasetLoaderVersionChoice"]["version"]:
                    dataset_loader["dataParams"]["datasetLoaderVersionChoice"]["version"] = 0
                continue
            preload_dataset_loader = load_dataset(
                dataset_loader["dataParams"]["datasetLoaderVersionChoice"]["name"],
                dataset_loader["dataParams"]["datasetLoaderVersionChoice"]["version"],
                install_requirements=True,
                kwargs_for_init=kwargs_for_init,
            )
            dataset_loader["dataParams"]["datasetLoaderVersionChoice"][
                "version"
            ] = preload_dataset_loader.metainfo.version
            preload_dataset_loaders[role] = preload_dataset_loader.loaded_object

        ep = {
            "executorMethodParams": {"methodName": "execute", "methodParams": json.dumps(executor_params)},
            "executorVersionChoice": {"name": job_executor_name, "version": job_executor_version},
        }

        params = {
            "listRoleModelParams": models,
            "listRoleDataParams": data_params,
            "executorParams": ep,
            "resources": {"cpus": 1, "memoryPerNode": 1000, "gpuNumber": 1 if gpu else 0, "gpuType": None},
        }
        job = ExecutionJob(
            {"params": params, "name": job_name, "experiment": {"name": "Default"}, "isDistributed": False}
        )
        Job(
            logger=logger,
            preload_executor=preload_executor,
            preload_models=preload_models,
            preload_dataset_loaders=preload_dataset_loaders,
        ).run_job(job)
        logger.info("Job completed successfully")
        job_result = DebugJobLogContext().get_result()
        print(job_result)
        return job_result


def _get_init_parameters_from_dict(params):
    """Get __init__ params from list of method_params."""
    for param in params:
        if param["methodName"] == ModelMethodName.init.value:
            return json.loads(param["methodParams"])
    return {}


def local_prune(cache: bool = True, local_registry: bool = True):
    """
    Сlear the cache and local registry directories.

    Parameters
    ----------
    cache:bool=True
        Flag for clearing the cache.

    local_registry:bool=True
        Flag for clearing the local registry.


    Returns
    -------
    None
    """
    if local_registry and os.path.exists(LOCAL_REGISTRY_PATH):
        shutil.rmtree(LOCAL_REGISTRY_PATH)

    if cache and os.path.exists(DEBUG_REGISTRY_PATH):
        shutil.rmtree(DEBUG_REGISTRY_PATH)
