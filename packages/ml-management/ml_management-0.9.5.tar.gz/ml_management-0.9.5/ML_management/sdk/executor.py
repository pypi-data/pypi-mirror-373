from typing import Dict, List, Literal, Optional, Union

import pandas as pd
from sgqlc.operation import Operation

from ML_management.executor import BaseExecutor
from ML_management.graphql import schema
from ML_management.graphql.schema import (
    ExecutorInfo,
    ExecutorVersionInfo,
    ObjectFilterSettings,
    ObjectVersionFilterSettings,
    TagFilterSettings,
    TimestampInterval,
    UpdateObjectForm,
)
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.model.model_type_to_methods_map import ModelMethodName
from ML_management.sdk.model import get_latest_model_version
from ML_management.sdk.sdk import _entity, _print_params_by_schema, _to_datetime


def list_executor() -> pd.DataFrame:
    """
    List available executors.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with list of available executors.
    """
    op = Operation(schema.Query)
    _entity(op.list_executor)
    json_data = send_graphql_request(op)
    df = pd.DataFrame.from_dict(json_data["listExecutor"])
    if not df.empty:
        df = _to_datetime(df, ["creationTimestamp", "lastUpdatedTimestamp"])
    return df


def set_executor_tags(name: str, key: str, values: list[str]) -> ExecutorInfo:
    """
    Set executor tag.

    Parameters
    ----------
    name: str
        Name of the model.
    key: str
        Key tag.
    values: list[str]
        Value tag.

    Returns
    -------
    ExecutorInfo
        Executor instance with meta information.
    """
    op = Operation(schema.Mutation)
    set_tag = op.set_executor_tags(name=name, key=key, values=values)
    _entity(set_tag)
    executor = send_graphql_request(op=op, json_response=False).set_executor_tags
    return executor


def reset_executor_tags(name: str, key: str, values: list[str], new_key: Optional[str] = None) -> ExecutorInfo:
    """
    Reset executor tag.

    Parameters
    ----------
    name: str
        Name of the model.
    key: str
        Key tag.
    values: list[str]
        Value tag.
    new_key: Optional[str] = None
        New key of a tag.


    Returns
    -------
    ExecutorInfo
        Executor instance with meta information.
    """
    op = Operation(schema.Mutation)
    set_tag = op.reset_executor_tags(name=name, key=key, values=values, new_key=new_key)
    _entity(set_tag)
    executor = send_graphql_request(op=op, json_response=False).reset_executor_tags
    return executor


def delete_executor_tag(name: str, key: str, value: Optional[str] = None) -> ExecutorInfo:
    """
    Delete executor tag.

    Parameters
    ----------
    name: str
        Name of the model.
    key: str
        Key tag.
    value: Optional[str]=None
        value tag.
    Returns
    -------
    ExecutorInfo
        Executor instance with meta information.
    """
    op = Operation(schema.Mutation)
    delete_tag = op.delete_executor_tag(name=name, key=key, value=value)
    _entity(delete_tag)
    executor = send_graphql_request(op=op, json_response=False).delete_executor_tag
    return executor


def set_executor_description(name: str, description: str) -> ExecutorInfo:
    """
    Set executor description.

    Parameters
    ----------
    name: str
        Name of the model.
    description: str
        Description model.

    Returns
    -------
    ExecutorInfo
        Executor instance with meta information.
    """
    op = Operation(schema.Mutation)
    set_description = op.update_executor(name=name, update_executor_form=UpdateObjectForm(new_description=description))
    _entity(set_description)
    executor = send_graphql_request(op=op, json_response=False).update_executor
    return executor


def set_executor_visibility(
    name: str, visibility: Union[Literal["private", "public"], VisibilityOptions]
) -> ExecutorInfo:
    """
    Set executor visibility.

    Parameters
    ----------
    name: str
        Name of the executor.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of the executor.

    Returns
    -------
    ExecutorInfo
        Executor instance with meta information.
    """
    visibility = VisibilityOptions(visibility)
    op = Operation(schema.Mutation)
    set_visibility = op.update_executor(
        name=name, update_executor_form=UpdateObjectForm(new_visibility=visibility.name)
    )

    _entity(set_visibility)
    executor = send_graphql_request(op=op, json_response=False)
    return executor.update_executor


def delete_executor(executor_name: str) -> bool:
    """
    Delete executor and all of it's versions.

    Parameters
    ----------
    executor_name: str
        Name of the executor to delete.

    Returns
    -------
    bool
        Operation success status.
    """
    op = Operation(schema.Mutation)
    op.delete_executor(name=executor_name)
    return send_graphql_request(op)["deleteExecutor"]


def list_executor_version(name: str) -> pd.DataFrame:
    """
    List available versions of the executor with such name.

    Parameters
    ----------
    name: str
        Name of the executor.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with a list of available executor versions.
    """
    op = Operation(schema.Query)
    base_query = op.executor_from_name(name=name).list_executor_version
    base_query.version()
    base_query.creation_timestamp()
    base_query.name()
    json_data = send_graphql_request(op)

    df = pd.DataFrame.from_dict(json_data["executorFromName"]["listExecutorVersion"])
    df = _to_datetime(df, ["creationTimestamp"])

    return df.sort_values(by=["version"], ignore_index=True)


def print_model_schema_for_executor(
    executor_name: str, models: List[dict], executor_version: Optional[int] = None
) -> None:
    """
    Print model schema for particular executor.

    Parameters
    ----------
    executor_name: str
        Name of the executor.
    models: List[dict]
        Necessary information about the model.

        Example1::

            [
                {"name": "simple_model"} # str
            ]

        Example2::

            [
                {
                    "name": "model_name1", # str
                    "role": "role1", # Optional[str]
                    "version": version # Optional[int]
                },
                {
                    "name": "model_name2", # str
                    "role": "role2", # Optional[str]
                    "version": version # Optional[int]
                }
            ]
    executor_version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    """
    models_methods_schemas = _get_model_schema_for_executor(
        executor_name=executor_name,
        executor_version=executor_version,
        models=models,
    )
    for model_methods_schemas in models_methods_schemas:
        role = model_methods_schemas["role"]
        for model in models:
            if ("role" in model and model["role"] == role) or "role" not in model:
                model_name = model["name"]

        print(f"Model name: {model_name}, model role: {role}")
        for model_methods_schema in model_methods_schemas["listMethodSchemas"]:
            _print_params_by_schema(
                model_methods_schema["jsonSchema"], ModelMethodName(model_methods_schema["schemaName"]).name
            )
        print()


def cancel_build_job_for_executor_version(executor_name: str, executor_version: int) -> bool:
    """
    Cancel running or planned build job of executor's image.

    Parameters
    ----------
    executor_name: str
        The name of the executor.
    executor_version: int
        The version of the executor.

    Returns
    -------
    bool
        Operation success status.
    """
    op = Operation(schema.Mutation)
    op.cancel_build_job_for_executor_version(name=executor_name, version=executor_version)
    return send_graphql_request(op)["cancelBuildJobForExecutorVersion"]


def delete_executor_version(executor_name: str, executor_version: int):
    """
    Delete version of a executor.

    Parameters
    ----------
    executor_name: str
        The name of the executor.
    executor_version: int
        The version of the executor.

    Returns
    -------
    None
    """
    op = Operation(schema.Mutation)
    executor_version_choice = schema.ObjectVersionInput(name=executor_name, version=executor_version)
    op.delete_executor_version_from_name_version(executor_version=executor_version_choice)

    send_graphql_request(op, json_response=False)


def _get_model_schema_for_executor(executor_name: str, executor_version: Optional[int], models: list) -> dict:
    role_models = []

    for model in models:
        model_name = model["name"]
        model_version = model.get("version", None)
        if model_version is None:
            model_version = get_latest_model_version(model_name).version
        model_role = model.get("role", BaseExecutor.DEFAULT_ROLE)

        current_model = schema.ObjectVersionInput(name=model_name, version=model_version)
        current_role = schema.RoleObjectVersionInput(role=model_role, object_version=current_model)

        role_models.append(current_role)

    op = Operation(schema.Query)

    _executor_version = schema.ObjectVersionOptionalInput(name=executor_name, version=executor_version)
    base_query = (
        op.executor_version_from_name_version(executor_version=_executor_version)
        .job_json_schema_for_models(models=role_models)
        .list_role_model_method_schemas
    )

    base_query.role()
    base_query.list_method_schemas.schema_name()
    base_query.list_method_schemas.json_schema()

    json_data = send_graphql_request(op)
    return json_data["executorVersionFromNameVersion"]["jobJsonSchemaForModels"]["listRoleModelMethodSchemas"]


def print_executor_schema(name: str, version: Optional[int] = None) -> None:
    """
    Print executor schema.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    """
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.executor_method_schema()
    json_data = send_graphql_request(op)

    json_data = json_data["executorVersionFromNameVersion"]["executorMethodSchema"]
    _print_params_by_schema(json_schema=json_data, schema_type="Executor")


def print_executor_roles(name: str, version: Optional[int] = None) -> None:
    """
    Print the roles required by the executor.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    """
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.desired_model_methods()
    base_query.desired_dataset_loader_methods()
    json_data = send_graphql_request(op)
    print("Desired model methods:", json_data["executorVersionFromNameVersion"]["desiredModelMethods"])
    print("Desired dataset loader methods:", json_data["executorVersionFromNameVersion"]["desiredDatasetLoaderMethods"])


def get_required_model_classes_by_executor(name: str, version: Optional[int] = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Return the names of classes for the model to be inherited from, by the name of the executor.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    List[str]:
        List of model class names to be inherited from.
    """
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.desired_model_patterns()
    json_data = send_graphql_request(op)
    return json_data["executorVersionFromNameVersion"]["desiredModelPatterns"]


def get_required_dataset_loader_classes_by_executor(
    name: str, version: Optional[int] = None
) -> Dict[str, List[Dict[str, str]]]:
    """
    Return the names of classes for the dataset loader to be inherited from, by the name of the executor.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    List[str]:
        List of dataset loader class names to be inherited from.
    """
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.desired_dataset_loader_patterns()
    json_data = send_graphql_request(op)
    return json_data["executorVersionFromNameVersion"]["desiredDatasetLoaderPatterns"]


def set_executor_version_description(name: str, version: int, description: str) -> ExecutorVersionInfo:
    """
    Set executor version description.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: int
        Version of the executor.
    description: str
        Description executor version.

    Returns
    -------
    ExecutorVersionInfo
        Executor version instance with meta information.
    """
    op = Operation(schema.Mutation)
    choice = schema.ObjectVersionInput(name=name, version=version)
    set_description = op.update_executor_version(
        executor_version=choice, update_executor_version_form=UpdateObjectForm(new_description=description)
    )
    set_description.name()
    set_description.version()
    set_description.description()

    executor = send_graphql_request(op=op, json_response=False)
    return executor.update_executor_version


def set_executor_version_visibility(
    name: str,
    version: int,
    visibility: Union[Literal["private", "public"], VisibilityOptions],
) -> ExecutorVersionInfo:
    """
    Set executor version visibility.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: int
        Version of the executor.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility executor version.

    Returns
    -------
    ExecutorVersionInfo
        Executor version instance with meta information.
    """
    visibility = VisibilityOptions(visibility)
    op = Operation(schema.Mutation)
    choice = schema.ObjectVersionInput(name=name, version=version)
    set_visibility = op.update_executor_version(
        executor_version=choice, update_executor_version_form=UpdateObjectForm(new_visibility=visibility.name)
    )
    set_visibility.name()
    set_visibility.version()
    set_visibility.visibility()

    executor = send_graphql_request(op=op, json_response=False)
    return executor.update_executor_version


def set_executor_version_tags(name: str, version: int, key: str, values: list[str]) -> ExecutorVersionInfo:
    """
    Set executor version tags.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: int
        Version of the executor.
    key: str
        Key tag.
    values: list[str]
        Value tag.

    Returns
    -------
    ExecutorVersionInfo
        Executor version instance with meta information.
    """
    op = Operation(schema.Mutation)
    choice = schema.ObjectVersionInput(name=name, version=version)
    set_tag = op.set_executor_version_tags(executor_version=choice, key=key, values=values)
    set_tag.name()
    set_tag.version()
    set_tag.tags()
    executor = send_graphql_request(op=op, json_response=False).set_executor_version_tags
    return executor


def reset_executor_version_tags(
    name: str, version: int, key: str, values: list[str], new_key: Optional[str] = None
) -> ExecutorVersionInfo:
    """
    Reset executor version tags.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: int
        Version of the executor.
    key: str
        Key tag.
    values: list[str]
        Value tag.
    new_key: Optional[str] = None
        New key of a tag.

    Returns
    -------
    ExecutorVersionInfo
        Executor version instance with meta information.
    """
    op = Operation(schema.Mutation)
    choice = schema.ObjectVersionInput(name=name, version=version)
    set_tag = op.reset_executor_version_tags(executor_version=choice, key=key, values=values, new_key=new_key)
    set_tag.name()
    set_tag.version()
    set_tag.tags()
    executor = send_graphql_request(op=op, json_response=False).reset_executor_version_tags
    return executor


def delete_executor_version_tag(name: str, version: int, key: str, value: Optional[str] = None) -> ExecutorVersionInfo:
    """
    Delete executor version tag.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: int
        Version of the executor.
    key: str
        Key tag.
    value: Optional[str]=None
        value tag.

    Returns
    -------
    ExecutorVersionInfo
        Executor version instance with meta information.
    """
    op = Operation(schema.Mutation)
    choice = schema.ObjectVersionInput(name=name, version=version)
    delete_tag = op.delete_executor_version_tag(executor_version=choice, key=key, value=value)
    delete_tag.name()
    delete_tag.version()
    delete_tag.tags()
    executor = send_graphql_request(op=op, json_response=False).delete_executor_version_tag
    return executor


def get_executor_version(name: str, version: Optional[int] = None) -> ExecutorVersionInfo:
    """
    Meta information about the executor version by the executor name and version.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    ExecutorVersionInfo
        ExecutorVersion instance with meta information.
    """
    op = Operation(schema.Query)
    executor_version_choice = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version_choice)
    base_query.name()
    base_query.version()
    base_query.tags()
    base_query.description()
    base_query.creation_timestamp()
    data = send_graphql_request(op, json_response=False).executor_version_from_name_version
    return data


def get_executor_version_conda_env(name: str, version: int) -> dict:
    """
    Condas configuration for the executor version by the executor name and version.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    Dict
        Dict with conda configuration.
    """
    op = Operation(schema.Query)
    _model_version = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=_model_version)
    base_query.get_conda_env()
    model_version = send_graphql_request(op, json_response=False)
    return model_version.executor_version_from_name_version.get_conda_env


def get_executor_version_requirements(name: str, version: int) -> list:
    """
    Requirements for the executor version by the executor name and version.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    List
        List of requirements.
    """
    op = Operation(schema.Query)
    _model_version = schema.ObjectVersionOptionalInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=_model_version)
    base_query.list_requirements()
    model_version = send_graphql_request(op, json_response=False)
    return model_version.executor_version_from_name_version.list_requirements


def get_latest_executor_version(name: str) -> ExecutorVersionInfo:
    """
    Latest executor version by the executor name.

    Parameters
    ----------
    name: str
        Name of the executor.

    Returns
    -------
    ExecutorVersionInfo
        ExecutorVersion instance with meta information.
    """
    return get_executor_version(name)


def get_initial_executor_version(name: str) -> ExecutorVersionInfo:
    """
    Initial executor version by the executor name.

    Parameters
    ----------
    name: str
        Name of the executor.

    Returns
    -------
    ExecutorVersionInfo
        ExecutorVersion instance with meta information.
    """
    op = Operation(schema.Query)
    version = op.executor_from_name(name=name).init_executor_version()
    version.name()
    version.version()
    version.tags()
    version.description()
    executor_version = send_graphql_request(op, json_response=False)
    return executor_version.executor_from_name.init_executor_version


def pagination_executor(
    name: Optional[str] = None,
    tag_key: Optional[str] = None,
    tag_value: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[Union[Literal["private", "public"], VisibilityOptions]] = None,
    owner_ids: Optional[list[str]] = None,
    creation_from: Optional[int] = None,
    creation_to: Optional[int] = None,
    last_updated_from: Optional[int] = None,
    last_updated_to: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[ExecutorInfo]:
    """
    Search executors.

    Parameters
    ----------
    name: Optional[str]=None
        Name of the executor.
    tag_key: Optional[str]=None
        Key of the executor tag.
    tag_value: Optional[str]=None
        Value of the executor tag.
    description: Optional[str]=None
        Description of the executor.
    visibility: Optional[Union[Literal['private', 'public'], VisibilityOptions]]=None
        Visibility of executor.
    owner_ids: Optional[list[str]]=None
        Ids of the executor owner.
    creation_from: Optional[int]=None
        Creation timestamp from of the executor.
    creation_to: Optional[int]=None
        Creation timestamp from of the executor.
    last_updated_from: Optional[int]=None
        Last updated timestamp from of the executor.
    last_updated_to: Optional[int]=None
        Last updated timestamp from of the executor.
    limit: Optional[int] = None
        The maximum number of records that will be returned as a result.
    offset: Optional[int] = None
        The number of records that will be skipped before starting the selection.

    Returns
    -------
    List[ExecutorInfo]
        List of ExecutorInfo instance with meta information.
    """
    op = Operation(schema.Query)
    visibility = VisibilityOptions(visibility) if visibility else visibility
    base_query = op.pagination_executor(
        limit=limit,
        offset=offset,
        filter_settings=ObjectFilterSettings(
            name=name,
            description=description,
            visibility=visibility,
            owner_ids=owner_ids,
            tag=TagFilterSettings(key=tag_key, value=tag_value),
            creation_interval=TimestampInterval(start=creation_from, end=creation_to),
            last_updated_interval=TimestampInterval(start=last_updated_from, end=last_updated_to),
        ),
    ).list_executor
    _entity(base_query)
    return send_graphql_request(op, json_response=False).pagination_executor.list_executor


def pagination_executor_version(
    name: str,
    version: Optional[int] = None,
    tag_key: Optional[str] = None,
    tag_value: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[VisibilityOptions] = None,
    owner_ids: Optional[list[str]] = None,
    creation_from: Optional[int] = None,
    creation_to: Optional[int] = None,
    last_updated_from: Optional[int] = None,
    last_updated_to: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[ExecutorVersionInfo]:
    """
    Search executor versions.

    Parameters
    ----------
    name: Optional[str]=None
        Name of the executor.
    version: Optional[int] = None
        Version of the executor.
    tag_key: Optional[str]=None
        Key of the executor tag.
    tag_value: Optional[str]=None
        Value of the executor tag.
    description: Optional[str]=None
        Description of the executor version.
    visibility: Optional[str]=None
        Visibility of executor version.
    owner_ids: Optional[list[str]]=None
        Ids of the executor version owner.
    creation_from: Optional[int]=None
        Creation timestamp from of the executor version.
    creation_to: Optional[int]=None
        Creation timestamp from of the executor version.
    last_updated_from: Optional[int]=None
        Last updated timestamp from of the executor version.
    last_updated_to: Optional[int]=None
        Last updated timestamp from of the executor version.
    limit: Optional[int] = None
        The maximum number of records that will be returned as a result.
    offset: Optional[int] = None
        The number of records that will be skipped before starting the selection.

    Returns
    -------
    List[ExecutorVersionInfo]
        List of ExecutorVersionInfo instance with meta information.
    """
    op = Operation(schema.Query)
    base_query = (
        op.executor_from_name(name=name)
        .pagination_executor_version(
            limit=limit,
            offset=offset,
            filter_settings=ObjectVersionFilterSettings(
                version=version,
                description=description,
                visibility=visibility,
                owner_ids=owner_ids,
                tag=TagFilterSettings(key=tag_key, value=tag_value),
                creation_interval=TimestampInterval(start=creation_from, end=creation_to),
                last_updated_interval=TimestampInterval(start=last_updated_from, end=last_updated_to),
            ),
        )
        .list_executor_version
    )
    base_query.name()
    base_query.version()
    base_query.tags()
    base_query.description()
    return send_graphql_request(
        op, json_response=False
    ).executor_from_name.pagination_executor_version.list_executor_version
