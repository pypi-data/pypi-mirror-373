"""Define Abstract class for Model with necessary methods and methods to implement."""
import inspect
import os
from abc import ABC, abstractmethod
from pathlib import Path

from ML_management.variables import CONFIG_KEY_ARTIFACTS


class Model(ABC):
    """
    Abstract class for model that Job will use.

    Attributes
    ----------
        self.artifacts: str
            Local path to artifacts.

        self.dataset: DatasetLoader object
            Instance of user's dataset.

    """

    def __new__(cls, *args, **kwargs):  # noqa: ARG003
        """Get object of Model class."""
        self = super().__new__(cls)
        # For now it was impossible to set self.artifacts before init func of model,
        # so it was impossible to use it inside init.
        # Because inside the job container code we have a fixed folder and file structure,
        # we can predetermine artifacts path.
        # It has to be beside file __init__.py  with get_object function.
        self.artifacts = str(
            Path(os.path.dirname(inspect.getframeinfo(inspect.currentframe().f_back)[0])) / CONFIG_KEY_ARTIFACTS
        )
        self.dataset = None

        return self

    @abstractmethod
    def predict_function(self, **kwargs):
        """Every model should make predictions."""
        raise NotImplementedError

    def to_device(self, device: str) -> None:  # noqa: B027
        """
        Define model migration to specific device.

        Devices are marked with following notation:

        cpu - CPU instance

        cuda:<number: int> - GPU instance
        """
        pass
