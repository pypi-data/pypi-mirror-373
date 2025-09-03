"""DatasetLoader template for dataset with base splits."""
from abc import abstractmethod

from ML_management.dataset_loader.dataset_loader_pattern import DatasetLoaderPattern


class BaseSplitsDatasetLoader(DatasetLoaderPattern):
    """Implementation of the DatasetLoader that performs basic splitting of data into training/validation/test parts."""

    def __init__(self):
        """Init dataset loader class."""
        super().__init__()

    @abstractmethod
    def get_train_data(self, **kwargs):
        """Define get_train_data function."""
        raise NotImplementedError

    @abstractmethod
    def get_validation_data(self, **kwargs):
        """Define get_validation_data function."""
        raise NotImplementedError

    @abstractmethod
    def get_test_data(self, **kwargs):
        """Define get_test_data function."""
        raise NotImplementedError
