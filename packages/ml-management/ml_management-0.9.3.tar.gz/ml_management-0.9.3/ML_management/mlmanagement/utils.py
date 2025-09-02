"""Functions for internal usage."""
import hashlib
import json
import os
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from ML_management.variables import FILENAME_FOR_INFERENCE_CONFIG

INIT_FUNCTION_NAME = "get_object"

HASH_IGNORE_PATH = ["__pycache__"]

HASH_CHUNK_SIZE = 4096 * 1024

model_name_pattern = re.compile("(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+")

valid_data_types = [
    "bool",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "int8",
    "int16",
    "int32",
    "int64",
    "float16",
    "float32",
    "float64",
]


class InferenceParams(BaseModel):
    name: str
    data_type: str
    dims: List[int]

    @field_validator("data_type")
    @classmethod
    def data_type_check(cls, value):
        assert value in valid_data_types, (
            f"{FILENAME_FOR_INFERENCE_CONFIG}: Every object in 'input' or 'output' list "
            f"should have one of the following data types: {valid_data_types}"
        )


class PredictConfig(BaseModel):
    cfg: Dict[str, List[InferenceParams]]

    @field_validator("cfg")
    @classmethod
    def cfg_check(cls, value):
        assert (
            "input" in value and "output" in value
        ), f"File {FILENAME_FOR_INFERENCE_CONFIG} should contain both 'input' and 'output' keys"


def is_model_name_valid(name: str):
    return model_name_pattern.fullmatch(name) is not None


def validate_predict_config(path: Optional[str]):
    if path is None or not os.path.isfile(path):
        raise RuntimeError(
            f"File {FILENAME_FOR_INFERENCE_CONFIG} was not found in artifacts. "
            "It is required, when create_venv_pack=True"
        )

    with open(path) as f:
        try:
            data = json.load(f)
        except Exception as err:
            raise RuntimeError(f"File {FILENAME_FOR_INFERENCE_CONFIG} should be valid json.") from err

    PredictConfig(cfg=data)


def hash_file(filepath: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def calculate_hash_directory(directory: str) -> str:
    hash_sha256 = hashlib.sha256()

    for root, _, files in sorted(os.walk(directory)):
        if any(root.endswith(ignore) for ignore in HASH_IGNORE_PATH):
            continue
        for name in sorted(files):
            filepath = os.path.join(root, name)
            file_hash = hash_file(filepath)
            hash_sha256.update(os.path.relpath(filepath, directory).encode("utf-8"))
            hash_sha256.update(file_hash.encode("utf-8"))

    return hash_sha256.hexdigest()


def calculate_size(local_path: str) -> int:
    if os.path.isfile(local_path):
        return os.path.getsize(local_path)
    total_size = 0
    for root, _, files in os.walk(local_path):
        for name in files:
            filepath = os.path.join(root, name)
            total_size += os.path.getsize(filepath)

    return total_size
