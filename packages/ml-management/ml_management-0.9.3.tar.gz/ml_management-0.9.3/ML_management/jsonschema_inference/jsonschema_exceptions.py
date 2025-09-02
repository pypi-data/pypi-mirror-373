"""Custom exception definition for jsonschema inference."""
from typing import List


class DictKeysMustBeStringsError(Exception):
    """Define DictKeysMustBeStringsError exception."""

    def __init__(self, annotation: str):
        self.annotation = annotation
        self.message = "Dict keys must be strings: {annotation}".format(annotation=annotation)

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (DictKeysMustBeStringsError, (self.annotation))


class InvalidStructureAnnotationError(Exception):
    """Define InvalidListAnnotationError exception."""

    def __init__(self, annotation: str):
        self.annotation = annotation
        self.message = "Structure has no type annotation for it's elements: {annotation}. \
        You maybe forget to specify it in [].".format(
            annotation=annotation
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidStructureAnnotationError, (self.annotation))


class InvalidSchemaError(Exception):
    """Define InvalidSchemaError exception."""

    def __init__(self, schema: dict, original_message: str):
        self.schema = schema
        self.original_message = original_message
        self.message = "Inferred jsonschema is not valid. Please, report this bug \
            to developers. Schema: {schema}, original exception message: {original_message}".format(
            schema=schema, original_message=original_message
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidSchemaError, (self.schema, self.original_message))


class NoAnnotationError(Exception):
    """Define NoAnnotationError exception."""

    def __init__(self, arg: str):
        self.arg = arg
        self.message = "Argument '{arg}' has no type annotation".format(arg=arg)

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (NoAnnotationError, (self.arg))


class UnsupportedTypeError(Exception):
    """Define UnsupportedTypeError exception."""

    def __init__(self, annotation: str, supported_types: List[str]):
        self.annotation = annotation
        self.supported_types = supported_types
        self.message = "Only {supported_types} and typing.List, typing.Dict, \
            typing.Union and typing.Optional are supported. Cause: {annotation}".format(
            annotation=annotation, supported_types=", ".join(supported_types)
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (UnsupportedTypeError, (self.annotation, self.supported_types))


class FunctionContainsVarArgsError(Exception):
    """Define FunctionContainsVarArgsError exception."""

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.message = "Function '{function_name}' contains a variable number positional arguments i.e. *args".format(
            function_name=function_name
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (FunctionContainsVarArgsError, (self.function_name))


class FunctionContainsVarKwArgsError(Exception):
    """Define FunctionContainsVarKwArgsError exception."""

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.message = "Function '{function_name}' contains a variable number keyword arguments i.e. **kwargs".format(
            function_name=function_name
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (FunctionContainsVarKwArgsError, (self.function_name))
