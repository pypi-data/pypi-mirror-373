from typing import Literal, Optional, Union

from sgqlc.operation import Operation

from ML_management.graphql import schema
from ML_management.graphql.schema import Experiment, ExperimentFilterSettings, TagFilterSettings, UpdateExperimentForm
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.mlmanagement.visibility_options import VisibilityOptions


def set_experiment_description(experiment_id: int, description: str) -> Experiment:
    """
    Set experiment description.

    Parameters
    ----------
    experiment_id: int
        Id of an experiment.
    description: str
        Description of an experiment.

    Returns
    -------
    Experiment
        Instance of a experiment with meta information.
    """
    op = Operation(schema.Mutation)
    set_description = op.update_experiment(
        experiment_id=experiment_id, update_experiment_form=UpdateExperimentForm(new_description=description)
    )
    set_description.name()
    set_description.description()
    set_description.visibility()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.update_experiment


def set_experiment_visibility(
    experiment_id: int,
    visibility: Union[Literal["private", "public"], VisibilityOptions],
) -> Experiment:
    """
    Set experiment visibility.

    Parameters
    ----------
    experiment_id: int
        Id of an experiment.
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        visibility of an experiment.

    Returns
    -------
    Experiment
        Instance of a experiment with meta information.
    """
    visibility = VisibilityOptions(visibility)
    op = Operation(schema.Mutation)
    set_visibility = op.update_experiment(
        experiment_id=experiment_id, update_experiment_form=UpdateExperimentForm(new_visibility=visibility.name)
    )
    set_visibility.name()
    set_visibility.description()
    set_visibility.visibility()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.update_experiment


def set_experiment_tags(experiment_id: int, key: str, values: list[str]) -> Experiment:
    """
    Set experiment tag.

    Parameters
    ----------
    experiment_id: int
        Id of an experiment.
    key: str
        Key of a tag.
    values: list[str]
        Value of a tag.

    Returns
    -------
    Experiment
        Instance of an experiment with meta information.
    """
    op = Operation(schema.Mutation)
    set_experiment_tags = op.set_experiment_tags(experiment_id=experiment_id, key=key, values=values)
    set_experiment_tags.name()
    set_experiment_tags.tags()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.set_experiment_tags


def reset_experiment_tags(experiment_id: int, key: str, values: list[str], new_key: Optional[str] = None) -> Experiment:
    """
    Reset experiment tag.

    Parameters
    ----------
    experiment_id: int
        Id of an experiment.
    key: str
        Key of a tag.
    values: list[str]
        Value of a tag.
    new_key: Optional[str] = None
        New key of a tag.

    Returns
    -------
    Experiment
        Instance of an experiment with meta information.
    """
    op = Operation(schema.Mutation)
    set_experiment_tags = op.reset_experiment_tags(experiment_id=experiment_id, key=key, values=values, new_key=new_key)
    set_experiment_tags.name()
    set_experiment_tags.tags()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.reset_experiment_tags


def delete_experiment_tag(experiment_id: int, key: str, value: Optional[str] = None) -> Experiment:
    """
    Delete experiment tag.

    Parameters
    ----------
    experiment_id: int
        Id of an experiment.
    key: str
        Key of a tag to delete.
    value: Optional[str]=None
        value tag.
    Returns
    -------
    Experiment
        Instance of an experiment with meta information.
    """
    op = Operation(schema.Mutation)
    set_experiment_tags = op.delete_experiment_tag(experiment_id=experiment_id, key=key, value=value)
    set_experiment_tags.name()
    set_experiment_tags.tags()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.delete_experiment_tag


def get_experiment_by_name(experiment_name: str) -> Experiment:
    """
    Get experiment by its name.

    Parameters
    ----------
    experiment_name: str
        Name of an experiment.

    Returns
    -------
    Experiment
        Instance of an experiment with meta information.
    """
    op = Operation(schema.Query)
    experiment_from_name = op.experiment_from_name(name=experiment_name)
    experiment_from_name.name()
    experiment_from_name.tags()
    experiment_from_name.description()
    experiment_from_name.experiment_id()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.experiment_from_name


def get_experiment_by_id(experiment_id: int) -> Experiment:
    """
    Get experiment by it's id.

    Parameters
    ----------
    experiment_id: int
        Id of an experiment.

    Returns
    -------
    Experiment
        Instance of an experiment with meta information.
    """
    op = Operation(schema.Query)
    experiment_from_name = op.experiment_from_id(experiment_id=experiment_id)
    experiment_from_name.name()
    experiment_from_name.tags()
    experiment_from_name.description()
    experiment_from_name.experiment_id()

    experiment = send_graphql_request(op=op, json_response=False)
    return experiment.experiment_from_id


def create_experiment(
    experiment_name: str,
    experiment_description: str = "",
    visibility: Union[Literal["private", "public"], VisibilityOptions] = VisibilityOptions.PRIVATE,
) -> Experiment:
    """
    Create experiment with given name and description.

    Parameters
    ----------
    experiment_name: str
        Name of the experiment.
    experiment_description: str = ""
        Description of the experiment. Default: "".
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        Visibility of experiment.  Default: PRIVATE.

    Returns
    -------
    Experiment
        Instance of an experiment with meta information.
    """
    op = Operation(schema.Mutation)
    create_experiment = op.create_experiment(
        experiment_name=experiment_name,
        experiment_description=experiment_description,
        visibility=VisibilityOptions(visibility).name,
    )
    create_experiment.name()
    create_experiment.description()

    experiment = send_graphql_request(op=op, json_response=False)

    return experiment.create_experiment


def pagination_experiment(
    name: Optional[str] = None,
    experiment_id: Optional[int] = None,
    description: Optional[str] = None,
    visibility: Optional[Union[Literal["private", "public"], VisibilityOptions]] = None,
    owner_ids: Optional[list[str]] = None,
    tag_key: Optional[str] = None,
    tag_value: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> list[Experiment]:
    """
    Search experiment.

    Parameters
    ----------
    name: Optional[str]=None
        Name of the executor.
    experiment_id: Optional[int]=None
        Id of an experiment.
    description: Optional[str]=None
        Description of the experiment.
    visibility: Optional[Union[Literal['private', 'public'], VisibilityOptions]]=None
        Visibility of experiment.
    owner_ids: Optional[list[str]]=None
        Ids of the experiment owner.
    tag_key: Optional[str]=None
        Key of the experiment tag.
    tag_value: Optional[str]=None
        Value of the experiment tag.
    limit: Optional[int] = None
        The maximum number of records that will be returned as a result.
    offset: Optional[int] = None
        The number of records that will be skipped before starting the selection.

    Returns
    -------
    List[Experiment]
        List of Experiment instance with meta information.
    """
    op = Operation(schema.Query)
    base_query = op.pagination_experiment(
        limit=limit,
        offset=offset,
        filter_settings=ExperimentFilterSettings(
            name=name,
            experiment_id=experiment_id,
            visibility=VisibilityOptions(visibility).name if visibility else None,
            owner_ids=owner_ids,
            description=description,
            tag=TagFilterSettings(key=tag_key, value=tag_value),
        ),
    ).list_experiment
    base_query.name()
    base_query.tags()
    base_query.description()
    base_query.experiment_id()
    base_query.visibility()
    return send_graphql_request(op, json_response=False).pagination_experiment.list_experiment
