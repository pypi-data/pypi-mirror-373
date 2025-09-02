"""Map supported dataset loader function name to infer jsonschema."""
from enum import Enum

from ML_management.dataset_loader.base_splits_dataset_loader import BaseSplitsDatasetLoader
from ML_management.dataset_loader.dataset_loader_pattern import DatasetLoaderPattern
from ML_management.dataset_loader.poisoned_images_dataset_loader import PoisonedImagesDatasetLoader


class DatasetLoaderMethodName(str, Enum):
    """Map supported dataset loader function name to infer jsonschema."""

    get_dataset = "get_dataset"
    get_images_names = "get_images_names"
    get_is_poisoned_by_names = "get_is_poisoned_by_names"
    get_labels_by_names = "get_labels_by_names"
    get_image_by_name = "get_image_by_name"
    get_clean_labels_by_names = "get_clean_labels_by_names"
    get_train_data = "get_train_data"
    get_validation_data = "get_validation_data"
    get_test_data = "get_test_data"
    init = "__init__"


dataset_loader_pattern_to_methods = {
    DatasetLoaderPattern: [DatasetLoaderMethodName.get_dataset, DatasetLoaderMethodName.init],
    PoisonedImagesDatasetLoader: [
        DatasetLoaderMethodName.get_images_names,
        DatasetLoaderMethodName.get_is_poisoned_by_names,
        DatasetLoaderMethodName.get_labels_by_names,
        DatasetLoaderMethodName.get_image_by_name,
        DatasetLoaderMethodName.get_clean_labels_by_names,
    ],
    BaseSplitsDatasetLoader: [
        DatasetLoaderMethodName.get_train_data,
        DatasetLoaderMethodName.get_validation_data,
        DatasetLoaderMethodName.get_test_data,
    ],
}
