"""Executor template for custom executor."""

from ML_management.executor.base_executor import BaseExecutor
from ML_management.executor.patterns import ArbitraryModelsPattern


class NoModelExecutorPattern(BaseExecutor):
    """DEPRECATED.

    Exists only for backward compatibility.
    Instead use BaseExecutor from ML_management.executor.base_executor.
    """

    def __init__(self) -> None:
        super().__init__(
            executor_models_pattern=ArbitraryModelsPattern(desired_models=[]),
        )
