"""Class inherits from base class of Model with a specific method for torch target layer."""
from abc import ABC, abstractmethod

from ML_management.model.patterns import model_pattern


class TargetLayer(model_pattern.Model, ABC):
    """Implementation of model with target_layer function."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_target_layer(self, **kwargs):
        """Define target_layer."""
        raise NotImplementedError
