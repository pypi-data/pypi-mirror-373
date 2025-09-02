"""Local collector."""
from ML_management.collectors.collector_pattern import CollectorPattern


class LocalCollector(CollectorPattern):
    """Local collectors."""

    def set_data(self, local_path: str) -> str:
        """Set suitable data."""
        return local_path

    @staticmethod
    def get_json_schema():
        """Return json schema."""
        schema = {
            "type": "object",
            "properties": {"local_path": {"type": "string"}},
            "required": ["local_path"],
            "additionalProperties": False,
        }

        return schema
