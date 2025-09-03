"""Map supported executor function name to infer jsonschema to tag."""
from enum import Enum

from ML_management.executor import base_executor


class ExecutorMethodName(str, Enum):
    """Map supported executor function name to infer jsonschema."""

    execute = "execute"


executor_pattern_to_methods = {base_executor.BaseExecutor: [ExecutorMethodName.execute]}
