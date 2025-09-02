"""Class inherits from base class of Model with a specific method for training the model."""
from abc import ABC, abstractmethod

from ML_management.model.patterns.model_pattern import Model


class TrainableModel(Model, ABC):
    """Implementation of trainable model."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def train_function(self, **kwargs):
        """Define train_function."""
        raise NotImplementedError
