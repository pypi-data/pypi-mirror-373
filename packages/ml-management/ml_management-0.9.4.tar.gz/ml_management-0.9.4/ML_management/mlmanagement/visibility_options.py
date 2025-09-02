"""Visibility options."""
from enum import Enum


class VisibilityOptions(str, Enum):
    """Define is object visible for all users by default."""

    PUBLIC = "public"
    PRIVATE = "private"
