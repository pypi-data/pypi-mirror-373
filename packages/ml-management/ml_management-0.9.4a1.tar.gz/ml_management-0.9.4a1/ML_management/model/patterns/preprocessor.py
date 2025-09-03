"""Abstract base class for preprocessing methods."""
from abc import ABC, abstractmethod
from typing import Annotated, Any

from ML_management.jsonschema_inference import SkipJsonSchema
from ML_management.model.patterns.model_pattern import Model

Tensor = Any


class Preprocessor(Model, ABC):
    """Abstract class for model that performs preprocessing."""

    @abstractmethod
    def preprocess(self, input_batch: Annotated[Tensor, SkipJsonSchema], **kwargs) -> Tensor:
        """Perform data preprocessing."""
        raise NotImplementedError

    def predict_function(self, input_batch: Annotated[Tensor, SkipJsonSchema]):
        return self.preprocess(input_batch)
