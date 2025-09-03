"""Custom exception definition (necessary for RegistryManager)."""

from ML_management.base_exceptions import RegistryError


class VersionNotFoundError(RegistryError):
    """Define Version Not Found Exception."""

    def __init__(self, model_name: str, version: int, model_type: str = "model"):
        self.model_name = model_name
        self.model_type = model_type
        self.version = version
        self.message = f'There is no version {self.version} for {self.model_type} "{self.model_name}"'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (VersionNotFoundError, (self.model_name, self.version, self.model_type))


class MetricNotLoggedError(RegistryError):
    """Define Metric Not Logged exception."""

    def __init__(self, model_name: str, metric: str):
        self.model_name = model_name
        self.metric = metric
        self.message = f'Metric "{self.metric}" is not logged for model "{self.model_name}"'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (MetricNotLoggedError, (self.model_name, self.metric))


class ModelNotRegisteredError(RegistryError):
    """Define Model Not Registered exception."""

    def __init__(self, model_name: str, model_type: str = "model"):
        self.model_name = model_name
        self.model_type = model_type
        self.message = f'{model_type} "{model_name}" is not registered'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (ModelNotRegisteredError, (self.model_name, self.model_type))


class NoMetricProvidedError(RegistryError):
    """Define NoMetricProvidedError exception."""

    def __init__(self, criteria: str):
        self.criteria = criteria
        self.message = f'Choice criteria "{self.criteria}" is passed, but no metric name is provided'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (NoMetricProvidedError, (self.criteria))


class UnsupportedCriteriaError(RegistryError):
    """Define Unsupported Criteria exception."""

    def __init__(self, criteria: str, supported_criteria: list):
        self.criteria = criteria
        self.supported_criteria = supported_criteria
        self.message = f'Choice criteria "{self.criteria}" is unsupported, must be one of: {self.supported_criteria}'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (UnsupportedCriteriaError, (self.criteria, self.supported_criteria))


class ExperimentNotFoundNameError(RegistryError):
    """Define Experiment not found exception."""

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.message = f'There is no experiment with name "{experiment_name}"'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (ExperimentNotFoundNameError, (self.experiment_name,))


class ExperimentNotFoundIDError(RegistryError):
    """Define Experiment not found exception."""

    def __init__(self, experiment_id: str):
        self.experiment_name = experiment_id
        self.message = f'There is no experiment with id "{experiment_id}"'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (ExperimentNotFoundIDError, (self.experiment_id,))


class JobNotFoundIdError(RegistryError):
    """Define job not found exception."""

    def __init__(self, job_id: int):
        self.job_id = job_id
        self.message = f'There is no job with id "{job_id}"'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (JobNotFoundIdError, (self.job_id,))


class JobHasNoObjUuidError(RegistryError):
    """Define job has no run id exception."""

    def __init__(self, job_id: int):
        self.job_id = job_id
        self.message = f'Job with id "{job_id}" has no run. Maybe it is not started yet.'
        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (JobHasNoObjUuidError, (self.job_id,))
