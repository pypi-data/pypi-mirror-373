"""Common variables."""
import os
import posixpath
from typing import Optional, Tuple

server_url = None
s3_url = None
s3_username = "PLACEHOLDER"
s3_password = "PLACEHOLDER"
mlm_login = None
mlm_password = None

secret_uuid = None

CONFIG_KEY_ARTIFACTS = "artifacts"
DEFAULT_EXPERIMENT = "Default"
MLCONFIG = "MLConfig.yaml"
MLMODEL_FILE_NAME = "MLmodel"
DATA = "entity_code_data"
LEGACY_DATA = "data"
FLAVOR_NAME = "python_function"
CONDA_SIZE_LIMIT = 50000
INFERENCE_CONFIG_LIMIT = 50000

METRIC_ACCUMULATION_DURATION = None
TIMEOUT_LOG_METRIC_BATCH = None
BUTCH_POLLING_FREQUENCY = None

EXPERIMENT_NAME_FOR_EXECUTOR = "executors"
EXPERIMENT_NAME_FOR_DATASET_LOADER = "dataset_loaders"
FILENAME_FOR_INFERENCE_CONFIG = "predict_config.json"
SERVER_META = posixpath.join("bff", "meta.json")

LOCAL_REGISTRY_PATH = os.path.abspath(
    os.path.expanduser(os.environ.get("LOCAL_REGISTRY_PATH", "~/.mlm_registry_cache"))
)
CACHED_LIST_FILENAME = "list.json"
JOB_ARTIFACT_DIRNAME = "job_artifacts"
NO_CACHE = bool(os.environ.get("NO_CACHE", False))

DEBUG = False
DEBUG_REGISTRY_PATH = os.path.abspath(
    os.path.expanduser(os.environ.get("DEBUG_REGISTRY_PATH", "~/.mlm_debug_registry"))
)


def get_metric_accumulation_duration() -> float:
    return (
        METRIC_ACCUMULATION_DURATION
        if METRIC_ACCUMULATION_DURATION
        else float(os.environ.get("METRIC_ACCUMULATION_DURATION", 1))
    )


def get_timeout_log_metric_batch() -> float:
    return (
        TIMEOUT_LOG_METRIC_BATCH if TIMEOUT_LOG_METRIC_BATCH else float(os.environ.get("TIMEOUT_LOG_METRIC_BATCH", 20))
    )


def get_butch_polling_frequency() -> float:
    return BUTCH_POLLING_FREQUENCY if BUTCH_POLLING_FREQUENCY else float(os.environ.get("BUTCH_POLLING_FREQUENCY", 0.3))


def get_log_service_url(function_name: str) -> str:
    """Get server '/log-object' endpoint URL for log_model, log_artifact, download_artifacts functions."""
    log_object_url = os.environ.get("log_object_url")
    base_url = log_object_url if log_object_url is not None else get_server_url()
    return posixpath.join(base_url, "log-object", function_name.replace("_", "-"))


def get_server_url() -> str:
    """
    Get server URL.

    If you set the URL using 'mlmanagement.set_server_url' function,
    it takes precedence over the URL from the environment variable 'server_url'
    """
    return os.environ.get("server_url", "https://local.tai-dev.intra.ispras.ru") if not server_url else server_url


def get_s3_gateway_url() -> str:
    """
    Get s3 URL.

    If you set the URL using 'mlmanagement.set_s3_url' function,
    it takes precedence over the URL from the environment variable 'S3_URL'
    """
    return os.environ.get("S3_URL", get_server_url()) if not s3_url else s3_url


def get_s3_credentials() -> Tuple[str, str]:
    """Get s3 credentials."""
    return s3_username, s3_password


def get_mlm_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get mlm credentials.

    If you set the URL using 'mlmanagement.set_mlm_credentials' function,
    it takes precedence over the URL from the environment variables 'MLM_LOGIN' and 'MLM_PASSWORD'.
    Environment variables 'login' and 'password' have last priority.
    """
    login = (
        (os.getenv("login") if not os.getenv("MLM_LOGIN") else os.getenv("MLM_LOGIN")) if not mlm_login else mlm_login
    )
    password = (
        (os.getenv("password") if not os.getenv("MLM_PASSWORD") else os.getenv("MLM_PASSWORD"))
        if not mlm_password
        else mlm_password
    )

    return login, password


def get_server_websocket_url() -> str:
    """Get the current websocket server URL."""
    url = get_server_url()
    splitted_url = url.split("/")
    splitted_url[0] = "wss:" if "https" in url else "ws:"
    return "/".join(splitted_url)
