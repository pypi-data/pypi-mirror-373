import warnings
from dataclasses import dataclass
from typing import Union

from ML_management.dataset_loader import DatasetLoaderPattern
from ML_management.executor import BaseExecutor
from ML_management.mlmanagement.model_type import ModelType
from ML_management.model import Model

warnings.warn(
    "ObjectMetaInfo and LoadedObject will be moved to ML_management.types.metainfo in future versions.",
    DeprecationWarning,
)


@dataclass
class ObjectMetaInfo:
    """
    Represents a logged object with its metadata.

    Returned when logging an entity.

    Attributes:
        name (str): Name of the entity.
        version (int): Version of the entity.
        hash_artifacts (str): Hash of the entity artifacts.
        model_type (ModelType): Entity type.
    """

    name: str
    version: int
    hash_artifacts: str
    model_type: ModelType


@dataclass
class LoadedObject:
    """
    Represents a loaded object with its metadata.

    Returned when loading an entity.

    Attributes:
        local_path (str): Local path where the object is stored.
        loaded_object (Union[BaseExecutor, DatasetLoaderPattern, Model]): The loaded class instance.
        metainfo (ObjectMetaInfo): Metadata information about the loaded object.
    """

    local_path: str
    loaded_object: Union[BaseExecutor, DatasetLoaderPattern, Model]
    metainfo: ObjectMetaInfo
