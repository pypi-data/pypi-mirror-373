"""Map supported collector function name to infer jsonschema."""
from enum import Enum

from ML_management.collectors import collector_pattern

collector_method_schema_name = "collector_method"


class CollectorMethodName(str, Enum):
    """Map supported collector function name to infer jsonschema."""

    set_data = collector_method_schema_name


set_data_pattern_to_methods = {collector_pattern.CollectorPattern: [CollectorMethodName.set_data]}
