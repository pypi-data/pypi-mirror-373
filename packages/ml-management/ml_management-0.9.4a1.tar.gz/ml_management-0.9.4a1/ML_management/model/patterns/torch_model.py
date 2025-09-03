"""Class inherits from base class of Model with a specific method for torch module."""
from abc import ABC, abstractmethod

from ML_management.model.patterns import model_pattern


class TorchModel(model_pattern.Model, ABC):
    """Implementation of torch model."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_nn_module(self, **kwargs):
        """Define nn_module."""
        raise NotImplementedError
