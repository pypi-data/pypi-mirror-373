"""Class inherits from base class of Model with a specific method for getting loss from the model."""
from abc import ABC, abstractmethod

from ML_management.model.patterns import model_pattern


class ModelWithLosses(model_pattern.Model, ABC):
    """Implementation of model with loss function."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_losses(self, **kwargs):
        """Define get_losses function."""
        raise NotImplementedError
