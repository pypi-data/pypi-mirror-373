import enum
from inspect import getfullargspec

from ML_management.jsonschema_inference.jsonschema_inference import get_function_args


def method_params_prepare(model, method_name: str, params: dict) -> dict:
    prepared = params.copy()
    func = getattr(model, method_name)
    spec = getfullargspec(func)
    all_args, _ = get_function_args(spec, func)
    if "self" in all_args:
        all_args.remove("self")
    for arg in set(params.keys()).intersection(all_args):
        annotation = spec.annotations[arg]
        if hasattr(annotation, "schema"):
            prepared[arg] = annotation.model_validate(params[arg])
        elif issubclass(annotation.__class__, enum.EnumMeta):
            prepared[arg] = annotation(params[arg])
    return prepared
