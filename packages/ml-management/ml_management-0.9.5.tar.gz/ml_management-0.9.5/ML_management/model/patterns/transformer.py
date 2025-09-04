"""Abstract base class for model transformation methods."""
from abc import ABC, abstractmethod
from typing import Annotated, Callable

from ML_management.jsonschema_inference import SkipJsonSchema
from ML_management.model.patterns.model_pattern import Model


class Transformer(Model, ABC):
    """Abstract class for model that performs transformations."""

    @abstractmethod
    def transform(self, model_fn: Annotated[Callable, SkipJsonSchema], **kwargs) -> Callable:
        """Perform model transformation.

        :param model_fn: takes a batch of input tensors and produces a final prediction tensor.
        """
        raise NotImplementedError
