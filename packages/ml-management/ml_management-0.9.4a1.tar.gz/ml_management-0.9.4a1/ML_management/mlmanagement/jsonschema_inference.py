import warnings

warnings.warn(
    "SkipJsonSchema will be moved to ML_management.jsonschema_inference in future versions.", DeprecationWarning
)


class SkipJsonSchema:
    """
    This class has been moved to ML_management.jsonschema_inference.

        .. deprecated::
    """

    def __class_getitem__(cls, _type):
        return cls()
