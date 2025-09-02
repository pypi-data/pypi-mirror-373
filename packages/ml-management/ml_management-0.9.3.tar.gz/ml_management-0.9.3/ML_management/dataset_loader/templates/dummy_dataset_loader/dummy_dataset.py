"""Define simple dataset_loader class."""
from ML_management.dataset_loader.dataset_loader_pattern import DatasetLoaderPattern


class DummyDataWrapper(DatasetLoaderPattern):
    """Dummy dataset loader class."""

    def get_dataset(self):
        """Return None."""
        return None
