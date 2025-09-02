"""Enum of existing model types."""
import warnings
from enum import Enum

warnings.warn("ModelType will be moved to ML_management.types.model_type in future versions.", DeprecationWarning)


class ModelType(str, Enum):
    """Model type class."""

    MODEL = "model"
    EXECUTOR = "executor"
    DATASET_LOADER = "dataset_loader"
