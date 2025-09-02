import json
import os
import warnings
from shutil import SameFileError, copy2, copytree
from typing import Union


def get_model_params(list_role_model_method_params: list) -> dict[str, dict[str, list[dict[str, Union[str, dict]]]]]:
    return {
        role_model.role: {
            "model_methods_params": [
                {
                    "method_name": model_method_params.method_name,
                    "method_params": json.loads(model_method_params.method_params),
                }
                for model_method_params in role_model.model_params.list_model_method_params
            ]
        }
        for role_model in list_role_model_method_params
    }


def get_source_models_name_version(list_role_model_method_params: list) -> dict[str, dict[str, Union[str, int]]]:
    return {
        role_param.role: {
            "name": role_param.model_params.model_version_choice.name,
            "version": role_param.model_params.model_version_choice.version,
        }
        for role_param in list_role_model_method_params
    }


def get_new_model_names(list_role_model_method_params: list) -> dict[str, str]:
    return {role_param.role: role_param.model_params.new_model_name for role_param in list_role_model_method_params}


def get_dataset_loaders_params(list_role_data_params: list) -> dict:
    return {
        data_param_role.role: {
            "dataset_loader_methods_params": [
                {
                    "method_name": dataset_loader_method_params.method_name,
                    "method_params": json.loads(dataset_loader_method_params.method_params),
                }
                for dataset_loader_method_params in data_param_role.data_params.list_dataset_loader_method_params
            ]
        }
        for data_param_role in list_role_data_params
    }


def get_dataset_loader_name_version(list_role_data_params: list) -> dict:
    return {
        role_param.role: {
            "name": role_param.data_params.dataset_loader_version_choice.name,
            "version": role_param.data_params.dataset_loader_version_choice.version,
        }
        for role_param in list_role_data_params
    }


def get_collector_params(list_role_data_params: list) -> dict:
    return {
        data_param_role.role: {
            "method_name": data_param_role.data_params.collector_method_params.method_name,
            "method_params": data_param_role.data_params.collector_method_params.method_params,
        }
        for data_param_role in list_role_data_params
    }


def prepare_artifacts(artifacts, role, role_model_map, registered_model_name) -> None:
    src_artifacts = None
    if len(role_model_map) == 1 and isinstance(artifacts, str):
        src_artifacts = artifacts
    elif isinstance(artifacts, dict) and role in artifacts:
        src_artifacts = artifacts.get(role)
    else:
        warnings.warn(
            "Artifacts returned from executor must be str for single model "
            "or dict with model roles for multiple models. "
            "Artifacts returned from executor for "
            "model {registered_model_name} were not logged.".format(registered_model_name=registered_model_name)
        )
    if not src_artifacts:
        return
    dst_artifacts = role_model_map[role].artifacts
    if not os.path.exists(src_artifacts):
        warnings.warn(
            "Artifact's path returned from executor for "
            "model {registered_model_name} does not exists.".format(registered_model_name=registered_model_name)
        )
        return

    if os.path.isdir(src_artifacts):
        copytree(src_artifacts, dst_artifacts)
        return

    try:
        copy2(src_artifacts, dst_artifacts)
    except SameFileError:
        pass
