"""Dataset loader template for custom dataset loader."""
from abc import ABC, abstractmethod


class DatasetLoaderPattern(ABC):
    """Define dataset loader.

    Attributes
    ----------
    artifacts : str
        Local path to artifacts.
        That parameters will be set automatically in job before the 'get_dataset' func would be executed.
    data_path: str
        A path to data to be loaded.

    """

    def __init__(self):
        """Init dataset loader class."""
        self.artifacts: str
        self.data_path = None

    @abstractmethod
    def get_dataset(self, **dataset_params):
        """
        Return dataset.

        To get data_path use self.data_path parameter, which also will be set in the job.
        'dataset_params' are dataset_loader parameters. One has to define it as ordinary kwargs
        with type annotation.
        """
        raise NotImplementedError
