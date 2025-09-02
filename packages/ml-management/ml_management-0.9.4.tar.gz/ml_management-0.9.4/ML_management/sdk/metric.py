from sgqlc.operation import Operation

from ML_management.graphql.schema import schema
from ML_management.graphql.send_graphql_request import send_graphql_request


def list_metric_jobs(metric_name: str, job_ids: list[int]) -> list[dict]:
    """
    Return metrics by job ids and metric_name.

    Parameters
    ----------
    metric_name: str
        Name of the metric.
    job_ids: list[int]
        List of job ids.

    Returns
    -------
    list[dict]
        List of metrics.
    """
    op = Operation(schema.Query)

    op.list_metric_jobs(metric_name=metric_name, job_ids=job_ids)

    metrics = send_graphql_request(op, json_response=False)

    return metrics.list_metric_jobs
