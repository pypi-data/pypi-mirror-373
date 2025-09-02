"""Abstract class of Collector for Job."""
from abc import ABC, abstractmethod

# That's copied from server, excluding splitters


class CollectorPattern(ABC):
    """Abstract class of Collector for Job."""

    @abstractmethod
    def set_data(self, *args, **kwargs):
        """Set suitable data."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_json_schema():
        """
        Every dataset should define json schema for its set_data parameters.

        https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.1.1

        The value of keyword "type" MUST be either a string or an array.
        If it is an array, elements of the array MUST be strings and MUST be unique.

        String values MUST be one of the six primitive types
        ("null", "boolean", "object", "array", "number", or "string"),
        or "integer" which matches any number with a zero fractional part.

        Parameters are optional by default. Requiered parameters are specified as array by key "required".
        """
        raise NotImplementedError
