import traceback
from typing import Literal, Optional, Union

from sgqlc.operation import Operation

from ML_management import variables
from ML_management.graphql import schema
from ML_management.graphql.schema import ExecutionJob
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.mlmanagement.batcher import Batcher
from ML_management.mlmanagement.metric_autostepper import MetricAutostepper
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.variables import DEFAULT_EXPERIMENT


class ActiveJob:
    """
    A context manager that allows for the execution of a task locally.

    This class provides a convenient way to run a job locally.

    """

    def __init__(self, secret_uuid):
        self.secret_uuid = secret_uuid
        self.job = self._start()
        self.__is_distributed = self.job.is_distributed

    def __enter__(self) -> "ActiveJob":
        return self

    def _start(self) -> ExecutionJob:
        op = Operation(schema.Mutation)
        base_query = op.start_job(secret_uuid=self.secret_uuid)
        base_query.name()
        base_query.id()
        base_query.experiment.name()
        base_query.is_distributed()
        _query_job_params(base_query)
        job = send_graphql_request(op=op, json_response=False).start_job
        variables.secret_uuid = self.secret_uuid
        return job

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__is_distributed:
            Batcher().wait_log_metrics()
            return
        exception_traceback = None
        message = None
        status = "SUCCESSFUL"
        if exc_type:
            exception_traceback = traceback.format_exc()
            message = ": ".join([exc_type.__name__, str(exc_val)])
            status = "FAILED"

        return stop_job(status, message, exception_traceback)


def start_job(
    job_name: Optional[str] = None,
    experiment_name: str = DEFAULT_EXPERIMENT,
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
) -> ActiveJob:
    """
    Create local job.

    Usage::

        with start_job('my-beautiful-job') as job:
            mlmanagement.log_metric(...)
            mlmanagement.log_artifacts(...)


    Or::

        start_job('my-beautiful-job')
        mlmanagement.log_metric(...)
        mlmanagement.log_artifacts(...)
        stop_job()


    Parameters
    ----------
    job_name: str | None=None
        Name of the new job. If not passed, it will be generated.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of this job to other users. Default: PRIVATE.

    Returns
    -------
    ActiveJob
        Active job.
    """
    visibility = VisibilityOptions(visibility)
    op = Operation(schema.Mutation)
    op.create_local_job(job_name=job_name, experiment_name=experiment_name, visibility=visibility.name)
    secret_uuid = send_graphql_request(op=op, json_response=False).create_local_job
    return ActiveJob(secret_uuid)


def stop_job(
    status: Literal["SUCCESSFUL", "FAILED"] = "SUCCESSFUL",
    message: Optional[str] = None,
    exception_traceback: Optional[str] = None,
) -> None:
    """
    Stop local job.

    Parameters
    ----------
    status: Literal["SUCCESSFUL", "FAILED"] = "SUCCESSFUL"
        Status of the job. If not passed, it will be SUCCESSFUL.
    message: Optional[str] = None
        Extra message for the job. Default: None
    exception_traceback: Optional[str] = None
        Error traceback of the job. Default: None

    Returns
    -------
    None
    """
    Batcher().wait_log_metrics()
    op = Operation(schema.Mutation)
    op.stop_job(
        secret_uuid=variables.secret_uuid, status=status, message=message, exception_traceback=exception_traceback
    )
    try:
        _ = send_graphql_request(op=op, json_response=False).stop_job
    finally:
        variables.secret_uuid = None
        MetricAutostepper().clear()


def _query_job_params(base_query):
    base_query.params()
    base_query.params.resources.gpu_number()
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
