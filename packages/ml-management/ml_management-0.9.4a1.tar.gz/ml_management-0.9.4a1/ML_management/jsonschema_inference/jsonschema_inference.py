"""Module for automatic jsonschema inference."""
import typing
import warnings
from copy import copy
from enum import Enum
from inspect import formatannotation, getfullargspec

from jsonschema import SchemaError
from jsonschema.validators import Draft4Validator
from pydantic.json_schema import GenerateJsonSchema

from ML_management.jsonschema_inference.jsonschema_exceptions import (
    DictKeysMustBeStringsError,
    FunctionContainsVarArgsError,
    FunctionContainsVarKwArgsError,
    InvalidSchemaError,
    InvalidStructureAnnotationError,
    NoAnnotationError,
    UnsupportedTypeError,
)

JSON_SCHEMA_DRAFT = "http://json-schema.org/draft-04/schema#"

type_map = {
    "bool": {"type": "boolean"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "str": {"type": "string"},
}
generic_type_map = {
    "list": typing.List,
    "dict": typing.Dict,
    "set": typing.Set,
    "tuple": typing.Tuple,
}


class CustomGenerateJsonSchema(GenerateJsonSchema):
    def field_title_should_be_set(self, _) -> bool:
        return False


class SkipJsonSchema:
    """
    Annotation wrapper for system parameters to skip them in JSON schema.

    Usage example::

        def my_function(arg: Annotated[np.ndarray, SkipJsonSchema]) -> None:
            print(arg)

    """

    def __class_getitem__(cls, _type):  # for backward compatibility with older models
        return cls()


def __get_or_raise(type_name, from_optional: bool = False):
    if type_name in type_map:
        field = copy(type_map[type_name])
        if from_optional:
            field["type"] = [field["type"], "null"]
        return field
    else:
        raise UnsupportedTypeError(annotation=type_name, supported_types=list(type_map.keys()))


def __is_optional(annotation):
    repr_annotation = repr(annotation)
    if repr_annotation.startswith("typing.Optional"):
        return True
    elif (
        repr_annotation.startswith("typing.Union")
        and repr_annotation.strip("]").endswith("NoneType")
        and len(annotation.__args__) == 2
    ):
        # python 3.8 casts Optional to Union[arg, None]
        return True
    else:
        return False


def __get_json_schema_from_annotation(annotation, from_optional: bool = False, arg_name=""):
    if annotation.__class__.__name__ == "UnionType":
        args = list(annotation.__args__)
        if type(None) in annotation.__args__:
            from_optional = True
            args.remove(type(None))
        return __get_json_schema_from_annotation(typing.Union[tuple(args)], from_optional)

    if annotation.__module__ == "typing":
        if __is_optional(annotation):
            return __get_json_schema_from_annotation(
                annotation.__args__[0], from_optional=True
            )  # Optional[int] translates to type: [integer, null], and the field is not required
        else:
            formatted_annotation = formatannotation(annotation)

            # this is the only way to reliably get annotation name (e.g. "List")
            annotation_name = formatted_annotation.partition("[")[0]
            if not hasattr(annotation, "__args__"):
                raise InvalidStructureAnnotationError(annotation=formatted_annotation)
            if annotation_name in ["List", "Tuple"]:
                return {
                    "type": "array" if not from_optional else ["array", "null"],
                    "items": __get_json_schema_from_annotation(annotation.__args__[0]),
                }
            elif annotation_name == "Dict":
                key_annotation = annotation.__args__[0]
                if hasattr(key_annotation, "__name__"):
                    if key_annotation.__name__ != "str":
                        raise DictKeysMustBeStringsError(annotation=formatted_annotation)
                else:
                    raise DictKeysMustBeStringsError(annotation=formatted_annotation)
                return {
                    "type": "object" if not from_optional else ["object", "null"],
                    "additionalProperties": __get_json_schema_from_annotation(annotation.__args__[1]),
                }
            elif annotation_name == "Union":
                union_types = [__get_json_schema_from_annotation(ann) for ann in annotation.__args__]
                marked_as_null = False
                for type_ in union_types:
                    if type_ == {"type": "null"}:
                        marked_as_null = True
                        break
                if not marked_as_null and from_optional:
                    union_types.extend([{"type": "null"}])
                return {"anyOf": union_types}
            else:
                raise UnsupportedTypeError(
                    annotation=formatannotation(annotation),
                    supported_types=list(type_map.keys()),
                )

    elif annotation.__module__ == "builtins":
        if hasattr(annotation, "__name__"):
            if annotation.__name__ in generic_type_map:
                return __get_json_schema_from_annotation(
                    generic_type_map[annotation.__name__][annotation.__args__], from_optional
                )
            return __get_or_raise(annotation.__name__, from_optional=from_optional)
    elif hasattr(annotation, "model_json_schema"):
        schema = annotation.model_json_schema(
            ref_template=f"#/properties/{arg_name}/$defs/" + "{model}", schema_generator=CustomGenerateJsonSchema
        )
        schema.pop("title", None)
        return schema
    elif issubclass(annotation, Enum):
        return {
            "enum": [member.value for member in annotation],
            "type": "string" if not from_optional else ["string", "null"],
        }

    else:
        raise UnsupportedTypeError(
            annotation=formatannotation(annotation),
            supported_types=list(type_map.keys()),
        )


def get_function_args(spec, func):
    """Get all arguments of function."""
    # FullArgSpec(args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations)
    pos_args_defaults = {}
    if spec.defaults:
        for arg, default in zip(spec.args[-len(spec.defaults) :], spec.defaults):
            pos_args_defaults[arg] = default
    if spec.varargs:
        raise FunctionContainsVarArgsError(function_name=func.__name__)
    if spec.varkw:
        raise FunctionContainsVarKwArgsError(function_name=func.__name__)

    # annotations are not inferred from default yet, but i can do it myself from kwonlydefaults
    pos_args = spec.args if spec.args else []
    kw_only_args = spec.kwonlyargs if spec.kwonlyargs else []
    all_args = pos_args + kw_only_args
    kw_only_args_defaults = spec.kwonlydefaults if spec.kwonlydefaults else {}
    all_defaults = {**pos_args_defaults, **kw_only_args_defaults}

    return all_args, all_defaults


def infer_jsonschema(func, get_object_func):
    """Infer jsonschema from callable by its signature."""
    from ML_management.model.model_type_to_methods_map import ModelMethodName  # circular import

    spec = getfullargspec(func)
    all_args, all_defaults = get_function_args(spec, func)
    schema = {
        "$schema": JSON_SCHEMA_DRAFT,
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
    if "self" in all_args:
        all_args.remove("self")

    if func.__name__ == ModelMethodName.init.value and get_object_func:
        spec_get_object = getfullargspec(get_object_func)
        all_args_get_object, _ = get_function_args(spec_get_object, get_object_func)
        if not set(all_args_get_object) == set(all_args):
            warnings.warn(
                "get_object function arguments do not match __init__ arguments. "
                "You won't be able to pass none default arguments into __init__ function."
            )
            all_args = []
            all_defaults = []

    required = []
    for arg in all_args:
        if arg not in spec.annotations:
            raise NoAnnotationError(arg=arg)

        # skip system parameters
        if (
            typing.get_origin(spec.annotations[arg]) is typing.Annotated
            and spec.annotations[arg].__metadata__
            and spec.annotations[arg].__metadata__[0] is SkipJsonSchema
        ) or isinstance(spec.annotations[arg], SkipJsonSchema):
            continue

        schema["properties"][arg] = __get_json_schema_from_annotation(spec.annotations[arg], arg_name=arg)
        if arg in all_defaults:
            schema["properties"][arg]["default"] = all_defaults[arg]
        if arg not in all_defaults and not __is_optional(spec.annotations[arg]):
            required.append(arg)

    if required:
        schema["required"] = required
    try:
        Draft4Validator.check_schema(schema)
    except SchemaError as err:
        raise InvalidSchemaError(schema=schema, original_message=str(err)) from None
    return schema
