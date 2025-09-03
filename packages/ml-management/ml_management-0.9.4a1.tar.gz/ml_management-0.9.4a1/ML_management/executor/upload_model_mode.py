"""Upload model mode."""
from enum import Enum


class UploadModelMode(str, Enum):
    """DEPRECATED.

    DO NOT USE. EXISTS FOR BACKWARD COMPATIBILITY ONLY.
    WILL BE DELETED IN FUTURE RELEASES.
    """

    none = "none"
    new_model = "new_model"  # log model as a new one with new name
    new_version = "new_version"  # log model as a new version of existing model
