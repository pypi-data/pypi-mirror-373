"""DatasetLoader template for poisoned dataset."""
from abc import abstractmethod
from typing import List

from ML_management.dataset_loader.dataset_loader_pattern import DatasetLoaderPattern


class PoisonedImagesDatasetLoader(DatasetLoaderPattern):
    """Implementation of the DatasetLoader for interacting with poisoned data."""

    def __init__(self):
        """Init dataset loader class."""
        super().__init__()

    @abstractmethod
    def get_images_names(self, **kwargs) -> List[str]:
        """Define get_images_names function."""
        raise NotImplementedError

    @abstractmethod
    def get_is_poisoned_by_names(self, names: List[str], **kwargs) -> List[bool]:
        """Define get_is_poisoned_by_names function."""
        raise NotImplementedError

    @abstractmethod
    def get_clean_labels_by_names(self, names: List[str], **kwargs) -> List[int]:
        """Define get_clean_labels_by_names function."""
        raise NotImplementedError

    @abstractmethod
    def get_labels_by_names(self, names: List[str], **kwargs) -> List[int]:
        """Define get_labels_by_names function."""
        raise NotImplementedError

    @abstractmethod
    def get_image_by_name(self, name: str, **kwargs) -> "tensor":  # type: ignore # noqa
        """Define get_image_by_name function."""
        raise NotImplementedError
