"""Upload model mode."""
from enum import Enum


class UploadModelMode(str, Enum):
    """Define how to log model after job execution."""

    new_model = "new_model"  # log model as a new one with new name
    new_version = "new_version"  # log model as a new version of existing model
