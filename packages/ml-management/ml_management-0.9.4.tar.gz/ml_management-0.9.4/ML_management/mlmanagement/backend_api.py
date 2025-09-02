from ML_management import variables


def set_server_url(url: str) -> None:
    """
    Set server URL.

    If you set the URL using this function,
    it takes precedence over the URL from the environment variable 'server_url'.

    Parameters
    ==========
    url: str
        Server url.
    Returns
    =======
    None
    """
    variables.server_url = url


def set_mlm_credentials(login: str, password: str) -> None:
    """
    Set login and password for mlmanagement.

    If you set the credentials using this function,
    it takes precedence over the credentials from the environment variables.

    Parameters
    ==========
    login: str
        Your mlm login.
    passwrod: str
        Yor mlm password.
    Returns
    =======
    None
    """
    variables.mlm_login = login
    variables.mlm_password = password


def get_server_url() -> str:
    """Get the current server URL."""
    return variables.get_server_url()


def set_no_cache_load(no_cache: bool):
    """
    Set flag no cache for download artifacts.

    If you set no_cache using this function,
    it takes precedence over the environment variable NO_CACHE.

    Parameters
    ==========
    no_cache: bool

    Returns
    =======
    None
    """
    variables.NO_CACHE = no_cache


def set_local_registry_path(registry_path: str):
    """
    Set local registry path.

    If you set local registry path using this function,
    it takes precedence over the environment variable LOCAL_REGISTRY_PATH.

    Parameters
    ==========
    registry_path: str
        registry path.
    Returns
    =======
    None
    """
    variables.LOCAL_REGISTRY_PATH = registry_path


def set_debug_registry_path(registry_path: str):
    """
    Set debug registry path.

    Parameters
    ==========
    registry_path: str
        registry path.
    Returns
    =======
    None
    """
    variables.DEBUG_REGISTRY_PATH = registry_path


def get_debug() -> bool:
    """Get the current debug flag."""
    return variables.DEBUG


def set_debug(debug: bool):
    """
    Set debug flag.

    If you set the flag using this function,
    it takes precedence over the credentials from the environment variables.

    Parameters
    ==========
    debug: bool
        Your mlm login.
    Returns
    =======
    None
    """
    variables.DEBUG = debug
