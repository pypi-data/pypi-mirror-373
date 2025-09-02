"""Enum of existing model types."""
from enum import Enum


class ModelType(str, Enum):
    """Model type class."""

    MODEL = "model"
    EXECUTOR = "executor"
    DATASET_LOADER = "dataset_loader"
