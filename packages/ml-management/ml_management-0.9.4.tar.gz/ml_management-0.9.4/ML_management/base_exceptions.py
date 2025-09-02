class MLMBaseError(Exception):
    """Base exception for all custom exceptions."""

    pass


class MLMServerError(MLMBaseError):
    """Base exception for all server mlmanager exceptions."""

    pass


class RegistryError(MLMBaseError):
    """Base exception for all registry exceptions."""

    pass


class MLMClientError(MLMBaseError):
    """Base exception for all client-side specific exceptions."""

    pass
