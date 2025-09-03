from enum import Enum
from typing import List

from pydantic import BaseModel


class JobType(str, Enum):
    """Enum job type."""

    build = "build"
    execution = "execution"
    venv = "venv"


class ResourceDataType(str, Enum):
    """Enum resource data type."""

    ROW = "row"
    PERCENT = "percent"


class ResourcePoint(BaseModel):
    """Description of the resource usage at the point."""

    value: float
    timestamp: float


class ResourcesInfo(BaseModel):
    """Specific resource usage."""

    resource_name: str
    points: List[ResourcePoint]
    data_type: ResourceDataType


class ResourceNodeInfo(BaseModel):
    """Node resource usage."""

    node_name: str
    resources: List[ResourcesInfo]
