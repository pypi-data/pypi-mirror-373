"""Class inherits from base class of Model with a specific method for updating and computing metrics."""
from abc import ABC, abstractmethod
from typing import Annotated, Any, Dict

from ML_management.jsonschema_inference import SkipJsonSchema
from ML_management.model.patterns.model_pattern import Model

Tensor = Any


class ModelWithMetrics(Model, ABC):
    """Implementation of model with specific methods for reseting, updating and computing metrics."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def reset_metrics(self) -> None:
        """Define function to reset internal variables."""
        raise NotImplementedError

    @abstractmethod
    def update_metrics(
        self, outputs_batch: Annotated[Tensor, SkipJsonSchema], targets: Annotated[Tensor, SkipJsonSchema], **kwargs
    ) -> None:
        """Define function to update internal variables with provided (outputs_batch, targets)."""
        raise NotImplementedError

    @abstractmethod
    def compute_metrics(self, **kwargs) -> Dict[str, float]:
        """Define function to compute the metrics and return the results in dictionary format."""
        raise NotImplementedError
