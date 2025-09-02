import json
import math
import posixpath
import sys
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import quote

import matplotlib.pyplot as plt
import pandas as pd
import websocket
from matplotlib.gridspec import GridSpec
from sgqlc.operation import Operation

from ML_management.collectors.collector_pattern_to_methods_map import (
    collector_method_schema_name,
)
from ML_management.graphql import schema
from ML_management.graphql.schema import AvailableResources, EnvParamInput, ExecutionJob, Param
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.local_debug.local_registry import LocalRegistry
from ML_management.mlmanagement.backend_api import get_debug, get_server_url
from ML_management.mlmanagement.log_api import _raise_error
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.sdk.model import get_latest_model_version
from ML_management.sdk.parameters import (
    AnyDatasetLoaderForm,
    AnyModelForm,
    DatasetLoaderForm,
    ModelForm,
    ResourcesForm,
    UploadAnyNewModelsForm,
    UploadOneNewModelForm,
)
from ML_management.sdk.types import JobType, ResourceNodeInfo
from ML_management.session import AuthSession
from ML_management.variables import get_server_websocket_url

_time_axis_for_resources = "time (min)"


def _job_fields(base_query):
    base_query.name()
    base_query.id()
    base_query.status()
    base_query.registration_timestamp()
    base_query.start_timestamp()
    base_query.end_timestamp()
    base_query.build_job.status()
    base_query.build_job.message()
    base_query.message()
    base_query.params()
    base_query.params.resources.cpus()
    base_query.params.resources.memory_per_node()
    base_query.params.resources.gpu_number()
    base_query.params.resources.gpu_type()
    base_query.params.models_schemas()
    base_query.params.list_role_model_params()
    base_query.params.list_role_data_params()
    base_query.params.list_role_data_params.data_params()
    base_query.params.list_role_data_params.role()
    base_query.params.list_role_model_params.model_params()
    base_query.params.list_role_model_params.upload_params()
    base_query.params.list_role_model_params.role()
    base_query.params.executor_params()
    base_query.params.executor_params.executor_method_params()
    base_query.params.executor_params.executor_version_choice()
    base_query.experiment.name()


def list_job_by_name(name: str) -> List[ExecutionJob]:
    """
    Return list of job object by name.

    Parameters
    ----------
    name: str
        Name of the jobs.

    Returns
    -------
    List[ExecutionJob]
        List of instance of the Job class.
    """
    op = Operation(schema.Query)

    base_query = op.list_job_from_name(name=name)
    _job_fields(base_query)

    job = send_graphql_request(op, json_response=False).list_job_from_name

    return job


def job_from_id(job_id: int) -> ExecutionJob:
    """
    Return Job object by id.

    Parameters
    ----------
    job_id: str
        Id of the job.

    Returns
    -------
    Job
        Instance of the Job class.
    """
    op = Operation(schema.Query)

    base_query = op.job_from_id(job_id=job_id)
    _job_fields(base_query)

    job = send_graphql_request(op, json_response=False)

    return job.job_from_id


def job_metric_by_id(job_id: int) -> pd.DataFrame:
    """
    Job's most recent logged metrics.

    Parameters
    ----------
    job_id: int
        Id of the job.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with the latest metrics.
    """
    if get_debug():
        metrics = LocalRegistry().get_metrics(job_id)  # TODO
        json_data = {key: max(values, key=lambda v: v["timestamp"])["value"] for key, values in metrics.items()}
    else:
        op = Operation(schema.Query)

        op.job_from_id(job_id=job_id).latest_metrics()
        json_data = send_graphql_request(op)

        json_data = json_data["jobFromId"]["latestMetrics"]

    return pd.DataFrame([json_data])


def available_metrics(job_id: int) -> List[str]:
    """
    List logged types of logged metrics in given job.

    Parameters
    ----------
    job_id: int
        Id of the job.

    Returns
    -------
    List[str]
        List with names of metrics.
    """
    if get_debug():
        return list(LocalRegistry().get_metrics(job_id).keys())  # TODO

    op = Operation(schema.Query)
    base = op.job_from_id(job_id=job_id)
    base.available_metrics()
    job = send_graphql_request(op, False)

    return job.job_from_id.available_metrics


def list_params_job(job_id: int) -> List[Param]:
    """
    List logged params in given job.

    Parameters
    ----------
    job_id: int
        Id of the job.

    Returns
    -------
    List[Param]
        List of params.
    """
    op = Operation(schema.Query)
    base = op.job_from_id(job_id=job_id)
    base.list_params()
    job = send_graphql_request(op, False)

    return job.job_from_id.list_params


def metric_history(
    job_id: int,
    metric_name: str,
    x_axis: str = "step",
    make_graph: bool = True,
    **kwargs,
) -> Tuple[List[float], List[float]]:
    """
    Lists history of given metric in given job and plots graph of metric's change over time.

    Parameters
    ----------
    job_id: int
        Id of the job.
    metric_name: str
        Name of the metric.
    x_axis: str
        Witch value use as x axis for graph or as return value. Possible options: "time", "step", "autostep".
        Time is represented in milliseconds.
    make_graph: bool
        Whether to create a metric schedule over time.
    kwargs: Any
        Any additional key arguments for plt.plot.

    Returns
    -------
    Tuple(List[float], List[float])
        First list with provided x axis of logged metric.
        Second list with values of metrics.
        Also plots graph using provided x axis and metric's values as y axis.
    """
    if get_debug():
        metrics = LocalRegistry().get_metrics(job_id).get(metric_name, {})  # TODO
    else:
        op = Operation(schema.Query)
        base = op.job_from_id(job_id=job_id)
        base.metric_history(metric=metric_name)
        json_data = send_graphql_request(op)
        metrics = json_data["jobFromId"]["metricHistory"]
    if x_axis not in ["time", "step", "autostep"]:
        raise ValueError("x_axis value must be step, autostep or time")
    if x_axis == "step":
        metrics = sorted(metrics, key=lambda x: x["step"])
        x_values = [metric["step"] for metric in metrics]
    elif x_axis == "time":
        metrics = sorted(metrics, key=lambda x: x["timestamp"])
        start_timestamp = metrics[0]["timestamp"]
        x_values = [(metric["timestamp"] - start_timestamp) / 10000 for metric in metrics]
    elif x_axis == "autostep":
        metrics = sorted(metrics, key=lambda x: x["autostep"])
        x_values = [metric["autostep"] for metric in metrics]

    metric_values = [metric["value"] for metric in metrics]

    if make_graph:
        plt.grid()
        plt.xlabel("milliseconds" if x_axis == "time" else "step")
        plt.ylabel(metric_name)
        plt.plot(x_values, metric_values, marker=".", **kwargs)

    return x_values, metric_values


def get_logs(job_id: int, stream: bool = True, file_name: Optional[str] = None) -> None:
    """
    Stream logs of the execution job by job name.

    Parameters
    ----------
    job_id: int
        Id of the execution job whose logs we want to view.
    stream: bool = True
        Stream logs or dump all available at the moment.
    file_name: Optional[str] = None
        Name of the file where to save logs. Default: None. If None prints logs to the output.
    """
    _get_logs(
        job_type=JobType.execution,
        stream=stream,
        file_name=file_name,
        params={"job_id": job_id},
    )


def cancel_job(job_id: int) -> bool:
    """
    Cancel running or planned execution job.

    Parameters
    ----------
    job_id: int
        Id of the job to cancel.
    """
    op = Operation(schema.Mutation)
    op.cancel_job(job_id=job_id)
    return send_graphql_request(op)["cancelJob"]


def get_build_logs(
    model_name: str,
    model_version: Optional[int] = None,
    stream: bool = True,
    file_name: Optional[str] = None,
) -> None:
    """
    Stream logs of the build job by model name and version.

    Parameters
    ----------
    model_name: str
        The name of the model whose docker image creation logs you want to view.
    model_version: Optional[int] = None
        The version of the model whose docker image creation logs you want to view.
        Default: None, "latest" version is used.
    stream: bool = True
        Stream logs or dump all available at the moment.
    file_name: Optional[str] = None
        Name of the file where to save logs. Default: None. If None prints logs to the output.
    """
    if model_version is None:
        model_version = get_latest_model_version(model_name).version

    _get_logs(
        job_type=JobType.build,
        stream=stream,
        file_name=file_name,
        params={"model_name": model_name, "model_version": model_version},
    )


def get_venv_build_logs(
    model_name: str,
    model_version: Optional[int] = None,
    stream: bool = True,
    file_name: Optional[str] = None,
) -> None:
    """
    Stream logs of the venv archive creating job by model name and version.

    Parameters
    ----------
    model_name: str
        The name of the model whose venv archive creation logs you want to view.
    model_version: Optional[int] = None
        The version of the model whose venv archive creation logs you want to view.
        Default: None, "latest" version is used.
    stream: bool = True
        Stream logs or dump all available at the moment.
    file_name: Optional[str] = None
        Name of the file where to save logs. Default: None. If None prints logs to the output.
    """
    if model_version is None:
        model_version = get_latest_model_version(model_name).version

    _get_logs(
        job_type=JobType.venv,
        stream=stream,
        file_name=file_name,
        params={"model_name": model_name, "model_version": model_version},
    )


def _get_logs(
    job_type: JobType,
    params: Dict[str, Any],
    stream: bool = True,
    file_name: Optional[str] = None,
) -> None:
    url = _get_logs_url(params=params, stream=stream, job_type=job_type)
    if stream:
        ws = None
        file = sys.stdout
        try:
            ws = AuthSession().instantiate_websocket_connection(url)
            if file_name:
                file = open(file_name, "w")
            while True:
                data = ws.recv()
                if not data:
                    return
                data = json.loads(data)
                if "status" not in data or data["status"] != "OK":
                    raise RuntimeError("Internal Server Error")
                print("\n".join(data["logs"]), file=file)
        except KeyboardInterrupt:
            pass
        except websocket._exceptions.WebSocketBadStatusException:
            possible_reasons_msg = (
                "Model with that name and version does not exist or does not have build job"
                if job_type is not JobType.execution
                else "Job with that name does not exist"
            )
            print(
                "<Connection refused. Check your query parameters, they may be incorrect.>\n"
                "<Possible reasons:>\n"
                f"<{possible_reasons_msg}>"
            )
        except Exception as err:
            print(err)
        finally:
            if ws is not None:
                ws.close()
            if file_name:
                file.close()
        return

    with AuthSession().get(url, stream=True) as resp:
        _raise_error(resp)
        if file_name:
            with open(file_name, "a") as f:
                for line in resp.iter_lines():
                    if line:
                        f.writelines([line, "\n"])
        else:
            for line in resp.iter_lines():
                if line:
                    print(line)


def _get_logs_url(params: Dict[str, Any], job_type: JobType, stream: bool = True) -> str:
    server_url = get_server_websocket_url() if stream else get_server_url()
    url_base = posixpath.join(server_url, "logs-api")
    url_encoded_params = "&".join(f"{quote(str(key))}={quote(str(value))}" for key, value in params.items())
    local_path = f"{f'stream/{job_type.value}' if stream else f'filedump/{job_type.value}'}?{url_encoded_params}"
    return posixpath.join(url_base, local_path)


def get_available_resources() -> AvailableResources:
    op = Operation(schema.Query)
    base_query = op.available_resources()
    base_query.gpus.type()
    base_query.gpus.number()
    response = send_graphql_request(op, json_response=False)
    return response.available_resources


def add_ml_job(
    job_executor_name: str,
    executor_params: dict,
    models_pattern: Union[ModelForm, AnyModelForm],
    data_pattern: Union[DatasetLoaderForm, AnyDatasetLoaderForm],
    resources: ResourcesForm | None = None,
    upload_models_params: Union[UploadOneNewModelForm, UploadAnyNewModelsForm, None] = None,
    job_executor_version: Optional[int] = None,
    experiment_name: str = "Default",
    job_name: Optional[str] = None,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    additional_system_packages: Optional[List[str]] = None,
    env_variables: Optional[Dict[str, str]] = None,
) -> ExecutionJob:
    """
    Create execution job.

    The job created by this function will run on only one node.
    If the resources of one node are insufficient, the job will be rejected.
    To use the ability to run on multiple nodes, use the add_ml_job_distributed function.

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
    resources: ResourcesForm
        Resources required for job execution.
        They will be allocated on one node, if it is not possible, job will be rejected.
    upload_models_params: Union[UploadOneNewModelForm, UploadAnyNewModelsForm],
        Parameters to log new models. If you want to log new model or model version,
        you have to specify this parameter. Default: None.
        The value None means that no new model will be uploaded.
    job_executor_version: Optional[int] = None
        Version of the executor that will execute the job. Default: None, "latest" version is used.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    job_name: Optional[str] = None
        Name of the created job.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of this job to other users. Default: PRIVATE.
    additional_system_packages: Optional[List[str]] = None
        List of system libraries for Debian family distributions that need to be installed in the job. Default: None
    env_variables: Optional[Dict[str, str]] = None
        Environment variables that will be set before starting the job.

    Returns
    -------
    ExecutionJob
        Instance of the Job class.
    """
    if not isinstance(models_pattern, ModelForm) and not isinstance(models_pattern, AnyModelForm):
        raise TypeError("Parameter models must have type ModelForm or AnyModelForm.")
    if not isinstance(data_pattern, DatasetLoaderForm) and not isinstance(data_pattern, AnyDatasetLoaderForm):
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
    if resources is None:
        resources = ResourcesForm()
    if not isinstance(resources, ResourcesForm):
        raise TypeError("Parameter resources must have type ResourcesForm.")
    return _add_job(
        job_executor_name=job_executor_name,
        executor_params=executor_params,
        models_pattern=models_pattern,
        data_pattern=data_pattern,
        resources=resources,
        upload_models_params=upload_models_params,
        job_executor_version=job_executor_version,
        experiment_name=experiment_name,
        job_name=job_name,
        visibility=visibility,
        additional_system_packages=additional_system_packages,
        env_variables=env_variables,
    )


def add_ml_job_distributed(
    job_executor_name: str,
    executor_params: dict,
    models_pattern: Union[ModelForm, AnyModelForm],
    data_pattern: Union[DatasetLoaderForm, AnyDatasetLoaderForm],
    resources: ResourcesForm,
    job_executor_version: Optional[int] = None,
    experiment_name: str = "Default",
    job_name: Optional[str] = None,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    additional_system_packages: Optional[List[str]] = None,
    env_variables: Optional[Dict[str, str]] = None,
) -> ExecutionJob:
    """
    Create execution job.

    The job created by this function can be executed on an arbitrary number of nodes greater than or equal to 1.
    The computing cluster distributes all resources equally among the allocated nodes.
    If such an equal distribution is not possible, the job will be rejected.
    To use the only one node, use the add_ml_job function.

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
    resources: ResourcesForm
        Resources required for job execution.
        They will be allocated on one node, if it is not possible, job will be rejected.
    job_executor_version: Optional[int] = None
        Version of the executor that will execute the job. Default: None, "latest" version is used.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    job_name: Optional[str] = None
        Name of the created job.
    visibility: Union[Literal["private", "public"], VisibilityOptions]
        Visibility of this job to other users. Default: PRIVATE.
    additional_system_packages: Optional[List[str]] = None
        List of system libraries for Debian family distributions that need to be installed in the job. Default: None
    env_variables: Optional[Dict[str, str]] = None
        Environment variables that will be set before starting the job.

    Returns
    -------
    ExecutionJob
        Instance of the Job class.
    """
    if not isinstance(models_pattern, ModelForm) and not isinstance(models_pattern, AnyModelForm):
        raise TypeError("Parameter models must have type ModelForm or AnyModelForm.")
    if not isinstance(data_pattern, DatasetLoaderForm) and not isinstance(data_pattern, AnyDatasetLoaderForm):
        raise TypeError("Parameter data_pattern must have type DatasetLoaderForm or AnyDatasetLoaderForm.")
    if not isinstance(resources, ResourcesForm):
        raise TypeError("Parameter resources must have type ResourcesForm.")
    return _add_job(
        job_executor_name=job_executor_name,
        executor_params=executor_params,
        models_pattern=models_pattern,
        data_pattern=data_pattern,
        resources=resources,
        job_executor_version=job_executor_version,
        experiment_name=experiment_name,
        job_name=job_name,
        visibility=visibility,
        additional_system_packages=additional_system_packages,
        is_distributed=True,
        env_variables=env_variables,
    )


def _add_job(
    job_executor_name: str,
    executor_params: dict,
    models_pattern: Union[ModelForm, AnyModelForm],
    data_pattern: Union[DatasetLoaderForm, AnyDatasetLoaderForm],
    resources: ResourcesForm,
    upload_models_params: Union[UploadOneNewModelForm, UploadAnyNewModelsForm, None] = None,
    job_executor_version: Optional[int] = None,
    experiment_name: str = "Default",
    job_name: Optional[str] = None,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
    additional_system_packages: Optional[List[str]] = None,
    is_distributed: bool = False,
    env_variables: Optional[Dict[str, str]] = None,
) -> ExecutionJob:
    visibility = VisibilityOptions(visibility)
    models = models_pattern.serialize()
    data_params = data_pattern.serialize()
    if not is_distributed and upload_models_params is None:
        raise ValueError("upload_models_params can not be None for not distributed job.")
    if not is_distributed:
        upload_params = upload_models_params.serialize()
        _validate_upload_params(models, upload_params)
    else:
        upload_params = {}
    list_role_data_params = []
    for data_param_role in data_params:
        data_inner_params: dict = data_param_role["data_params"]
        dataset_loader_name = data_inner_params["dataset_loader_name"]
        dataset_loader_version = data_inner_params.get("dataset_loader_version", None)
        dataset_loader_version_choice = schema.ObjectVersionOptionalInput(
            name=dataset_loader_name, version=dataset_loader_version
        )

        collector_name = data_inner_params["collector_name"]

        collector_method_params = schema.MethodParamsInput(
            method_name=collector_method_schema_name,
            method_params=json.dumps(data_inner_params["collector_params"]),
        )

        list_dataset_loader_method_params = []
        for item in data_inner_params["dataset_loader_params"]:
            for key in item:
                list_dataset_loader_method_params.append(
                    schema.MethodParamsInput(method_name=key, method_params=json.dumps(item[key]))
                )

        current_dataset_loader_params = schema.DataParamsInput(
            dataset_loader_version_choice=dataset_loader_version_choice,
            collector_name=collector_name,
            list_dataset_loader_method_params=list_dataset_loader_method_params,
            collector_method_params=collector_method_params,
        )

        list_role_data_params.append(
            schema.RoleDataParamsInput(role=data_param_role["role"], data_params=current_dataset_loader_params)
        )

    op = Operation(schema.Query)
    _executor_version = schema.ObjectVersionOptionalInput(name=job_executor_name, version=job_executor_version)

    executor_version_choice = schema.ObjectVersionOptionalInput(name=job_executor_name, version=job_executor_version)

    executor_model_schema = op.executor_version_from_name_version(executor_version=_executor_version)
    executor_model_schema.executor_method_schema_name()

    executor_version_obj = send_graphql_request(op, json_response=False)
    executor_method_schema = executor_version_obj.executor_version_from_name_version.executor_method_schema_name

    executor_method_params = schema.MethodParamsInput(
        method_name=executor_method_schema, method_params=json.dumps(executor_params)
    )

    list_role_model_params = []

    for model in models:
        version = model["model"].get("version")
        model_version_choice = schema.ModelVersionChoice(
            name=model["model"]["name"],
            version=version,
        )

        model_methods_params = []

        for item in model["params"]:
            for key in item:
                model_methods_params.append(
                    schema.MethodParamsInput(method_name=key, method_params=json.dumps(item[key]))
                )

        current_model_params = schema.ModelParamsInput(
            model_version_choice=model_version_choice,
            list_model_method_params=model_methods_params,
        )
        role = model["role"]
        model_role = schema.RoleModelParamsInput(
            role=role,
            model_params=current_model_params,
            upload_params=None if role not in upload_params else schema.UploadModelParamsInput(**upload_params[role]),
        )
        list_role_model_params.append(model_role)

    executor_params = schema.ExecutorParamsInput(
        executor_method_params=executor_method_params,
        executor_version_choice=executor_version_choice,
    )

    resources = schema.ResourcesInput(
        cpus=resources.cpus,
        memory_per_node=resources.memory_per_node,
        gpu_number=resources.gpu_number,
        gpu_type=resources.gpu_type,
    )
    op = Operation(schema.Mutation)
    mutation = op.add_ml_job(
        form=schema.JobParameters(
            executor_params=executor_params,
            list_role_model_params=list_role_model_params,
            list_role_data_params=list_role_data_params,
            experiment_name=experiment_name,
            visibility=VisibilityOptions(visibility).name,
            additional_system_packages=additional_system_packages,
            job_name=job_name,
            resources=resources,
            is_distributed=is_distributed,
            env_variables=[EnvParamInput(key=key, value=value) for key, value in env_variables.items()]
            if env_variables
            else None,
        )
    )

    mutation.name()
    mutation.id()

    job = send_graphql_request(op, json_response=False)

    return job.add_ml_job


def _validate_upload_params(models: List[dict], upload_params: dict):
    """Validate that params are consistent with models."""
    upload_roles = set(upload_params.keys())
    models_roles = {m["role"] for m in models}
    if not upload_roles.issubset(models_roles):
        raise ValueError(
            "The upload_models_params parameter should contain only those roles that are specified for the models."
        )


def set_job_visibility(job_id: int, visibility: Union[Literal["private", "public"], VisibilityOptions]) -> ExecutionJob:
    """
    Set job visibility.

    Parameters
    ----------
    job_id: int
        Id of the job.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of a job.

    Returns
    -------
    ExecutionJob
        Instance of a job with meta information.
    """
    op = Operation(schema.Mutation)
    set_visibility = op.update_job(job_id=job_id, visibility=VisibilityOptions(visibility).name)
    set_visibility.name()
    set_visibility.visibility()

    job = send_graphql_request(op=op, json_response=False)
    return job.update_job


def delete_finished_job(job_id: int):
    """
    Delete finished job.

    Parameters
    ----------
    job_id: int
        Id of the job.

    Returns
    -------
    None
    """
    op = Operation(schema.Mutation)
    op.delete_finished_job(job_id=job_id)
    send_graphql_request(op=op, json_response=False)


def job_resource_usage(
    job_name: str, step: int = 30, make_graph: bool = True
) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
    """
    Lists history of resources usage by job and plots graph of resources change over time.

    Parameters
    ----------
    job_name: str
        Name of the job.
    step: int
        The step parameter controls how many data points are returned (and in turn the number of instant
        queries executed) from the range query.
    make_graph: bool
        Whether to create a resource usage schedule over time.

    Returns
    -------
    Dict[str, Dict[str, Dict[str, List[float]]]]
        Resources usage by job.
        Example::

            {
                'node_name':
                {
                    'GPU Utilization': {
                        'time (min)': List[float],
                        'values': List[float],
                        }
                    'GPU Memory Usage (GB)': {
                        'time (min)': List[float],
                        'values': List[float],
                        }
                    ...
                },
                ...
            }

    """
    if step <= 0 or type(step) is not int:
        raise ValueError("Parameter step must be a positive integer.")

    url_base = posixpath.join(get_server_url(), "resource-monitoring")
    local_path = f"snapshot/{job_name}?step={step}"
    url = posixpath.join(url_base, local_path)

    job_resources = []

    with AuthSession().get(url) as resp:
        _raise_error(resp)
        for node in json.loads(resp._content):
            job_resources.append(ResourceNodeInfo.model_validate(node))

    resources_usage_dict = {}

    for resource_node_info_type in job_resources:
        current_resource_usage_dict = {}
        for resource in resource_node_info_type.resources:
            timestamps = []
            values = []
            for point in resource.points:
                timestamps.append((point.timestamp - resource.points[0].timestamp) / 60)
                values.append(point.value)

            if len(timestamps) != 0 and len(values) != 0:
                current_resource_usage_dict[resource.resource_name] = {
                    _time_axis_for_resources: timestamps,
                    "values": values,
                }
        resources_usage_dict[resource_node_info_type.node_name] = current_resource_usage_dict

    if make_graph:
        for node_name in resources_usage_dict.keys():
            if len(resources_usage_dict[node_name]) > 0:
                _print_node_resources(resources_usage_dict[node_name], node_name)
            else:
                print("Nothing to plot.")

    return resources_usage_dict


def _format_axes(fig, data: List[Tuple[List[int], List[int]]]) -> None:
    """Axes formatter for printing job resources.

    Parameters
    ----------
    fig:
        _description_
    data: List[Tuple[List[int], List[int]]]
        Data to insert into axes. [([timestamps], [values])]
    """
    for i, ax in enumerate(fig.axes):
        if len(data[i][0]) == 1 and len(data[i][1]) == 1:
            ax.plot(data[i][0], data[i][1], "o")
        else:
            ax.plot(data[i][0], data[i][1])
        ax.grid(True)
        if "%" in ax.get_title():
            ax.set_ylim(0, 100)


def _print_node_resources(data: Dict, node_name: str) -> None:
    """Print resource usage by node_name.

    Parameters
    ----------
    data: Dict
        Resource usage by node data.
        Example::

        {
            'GPU Utilization': {
                'timestamps (sec)': List[int],
                'values': List[int],
                }
            'GPU Memory Usage (GB)': {
                'timestamps (sec)': List[int],
                'values': List[int],
                }
            ...
        }

    node_name: str
        Name of the node.
    """
    pict_names = list(data.keys())

    num_rows = math.ceil(len(pict_names) / 2)

    if num_rows > 1:
        size = (12, 8)
    else:
        size = (10, 4)

    fig = plt.figure(constrained_layout=True, figsize=size)
    gs = GridSpec(num_rows, 2, figure=fig)

    num_columns = 2

    for row in range(num_rows - 1):
        for column in range(num_columns):
            fig.add_subplot(gs[row, column], title=pict_names[row * num_columns + column])

    if len(pict_names) % 2 == 0:
        fig.add_subplot(gs[num_rows - 1, 0], title=pict_names[-2], xlabel=_time_axis_for_resources)
        fig.add_subplot(gs[num_rows - 1, 1], title=pict_names[-1], xlabel=_time_axis_for_resources)
    else:
        fig.add_subplot(gs[num_rows - 1, :], title=pict_names[-1], xlabel=_time_axis_for_resources)

    fig.suptitle(f"Resources usage by node: {node_name}")
    _format_axes(fig, [(data[i][_time_axis_for_resources], data[i]["values"]) for i in data.keys()])
    plt.show()
