"""Class inherits from base class of Model with a specific method for evaluating the model."""
from abc import ABC, abstractmethod

from ML_management.model.patterns import model_pattern


class EvaluatableModel(model_pattern.Model, ABC):
    """Implementation of evaluable model."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def evaluate_function(self, **kwargs):
        """Define evaluate function."""
        raise NotImplementedError
