"""Script for upload default dummy datasetloader."""
import os

from ML_management import mlmanagement
from ML_management.mlmanagement.visibility_options import VisibilityOptions


def upload_dummmy_data():
    mlmanagement.log_dataset_loader_src(
        description="Dummy dataset loader",
        registered_name="DummyData",
        model_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "dummy_dataset_loader"),
        visibility=VisibilityOptions.PUBLIC,
    )
