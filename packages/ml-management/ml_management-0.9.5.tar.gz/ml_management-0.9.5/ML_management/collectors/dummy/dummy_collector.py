"""Dummy collectors."""
from ML_management.collectors.collector_pattern import CollectorPattern


class DummyCollector(CollectorPattern):
    """Dummy collectors."""

    def set_data(self, *_args, **_kwargs):
        """Set suitable data."""
        return ""

    @staticmethod
    def get_json_schema():
        """Return json schema."""
        schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

        return schema
