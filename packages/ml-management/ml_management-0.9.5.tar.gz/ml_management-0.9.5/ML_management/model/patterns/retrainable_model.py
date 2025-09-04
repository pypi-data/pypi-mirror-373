"""Сlass inherits from base class of TrainaleModel with a specific method for fine-tuning the model."""
from abc import ABC, abstractmethod

import ML_management.model.patterns.trainable_model as trainableModel

# TODO does Retrainable model have to be Trainable?


class RetrainableModel(trainableModel.TrainableModel, ABC):
    """Implementation of retrainable model."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def finetune_function(self, **kwargs):
        """Define finetune_mode."""
        raise NotImplementedError
