"""General testing of the sdk."""
import os
import unittest
from typing import Union

import pandas

import ML_management.sdk.dataset_loader
import ML_management.sdk.executor
import ML_management.sdk.job
import ML_management.sdk.model
from ML_management.graphql.schema import DatasetLoaderInfo, ExecutionJob, ExecutorInfo, ModelInfo, ModelVersionInfo
from ML_management.mlmanagement import set_server_url
from ML_management.sdk.parameters import (
    AnyModelForm,
    DatasetLoaderForm,
    DatasetLoaderMethodParams,
    ModelVersionChoice,
    ModelWithRole,
)

os.environ["kc_access"] = "kc_access"
os.environ["kc_state"] = "kc_state"

NAME = "name"
VERSION = 1
PARAMS = {}
ROLE = "single"


class TestSDK(unittest.TestCase):
    """Tests that sdk is supported by current server introspection."""

    def setUp(self):
        """Set mock_server url."""
        set_server_url("http://localhost:4000/")

    def test_list_model(self):
        """Test sdk.list_model method returns correct answer."""
        list_model = ML_management.sdk.model.list_model()
        # mock server generates non-empty result by introspection.
        self.assertGreater(len(list_model), 0)
        # sdk returns an object of the correct type.
        self.assertIsInstance(list_model, pandas.core.frame.DataFrame)

    def test_list_dataset_loader(self):
        """Test sdk.list_dataset_loader method returns correct answer."""
        list_dataset_loader = ML_management.sdk.dataset_loader.list_dataset_loader()
        # mock server generates non-empty result by introspection.
        self.assertGreater(len(list_dataset_loader), 0)
        # sdk returns an object of the correct type.
        self.assertIsInstance(list_dataset_loader, pandas.core.frame.DataFrame)

    def test_list_executor(self):
        """Test sdk.list_executor method returns correct answer."""
        list_executor = ML_management.sdk.executor.list_executor()
        # mock server generates non-empty result by introspection.
        self.assertGreater(len(list_executor), 0)
        # sdk returns an object of the correct type.
        self.assertIsInstance(list_executor, pandas.core.frame.DataFrame)

    def test_add_ml_job(self):
        """Test sdk.add_ml_job method returns correct answer."""
        self.assertIsInstance(
            ML_management.sdk.job.add_ml_job(
                job_executor_name=NAME,
                executor_params=PARAMS,
                models_pattern=AnyModelForm(
                    models=[
                        ModelWithRole(role=ROLE, model_version_choice=ModelVersionChoice(name=NAME, version=VERSION))
                    ]
                ),
                data_pattern=DatasetLoaderForm(
                    name=NAME,
                    version=VERSION,
                    params=[DatasetLoaderMethodParams(params=PARAMS)],
                    collector_params=PARAMS,
                ),
                job_executor_version=VERSION,
            ),
            ExecutionJob,
        )

    def test_list_job_by_name(self):
        """Test sdk.job.list_job_by_name method returns correct answer."""
        jobs = ML_management.sdk.job.list_job_by_name("job_name")
        self.assertIsInstance(jobs, list)

    def test_job_metric_by_name(self):
        """Test sdk.job_metric_by_name method returns correct answer."""
        metric = ML_management.sdk.job.job_metric_by_id(job_id=VERSION)
        # mock server generates non-empty result by introspection.
        self.assertEqual(len(metric), 1)
        # sdk returns an object of the correct type.
        self.assertIsInstance(ML_management.sdk.job.job_metric_by_id(job_id=VERSION), pandas.core.frame.DataFrame)

    def test_list_model_version(self):
        """Test sdk.list_model_version method returns correct answer."""
        list_model_version = ML_management.sdk.model.list_model_version(name=NAME)
        # mock server generates non-empty result by introspection.
        self.assertGreater(len(list_model_version), 0)
        # sdk returns an object of the correct type.
        self.assertIsInstance(list_model_version, pandas.core.frame.DataFrame)

    def test_list_dataset_loader_version(self):
        """Test sdk.list_dataset_loader_version method returns correct answer."""
        list_dataset_loader_version = ML_management.sdk.dataset_loader.list_dataset_loader_version(name=NAME)
        # mock server generates non-empty result by introspection.
        self.assertGreater(len(list_dataset_loader_version), 0)
        # sdk returns an object of the correct type.
        self.assertIsInstance(list_dataset_loader_version, pandas.core.frame.DataFrame)

    def test_list_executor_version(self):
        """Test sdk.list_executor_version method returns correct answer."""
        list_executor_version = ML_management.sdk.executor.list_executor_version(name=NAME)
        # mock server generates non-empty result by introspection.
        self.assertGreater(len(list_executor_version), 0)
        # sdk returns an object of the correct type.
        self.assertIsInstance(list_executor_version, pandas.core.frame.DataFrame)

    def test_model_version_metainfo(self):
        """Test sdk.model_version_metainfo method returns correct answer."""
        self.assertIsInstance(ML_management.sdk.model.get_model_version(name=NAME, version=VERSION), ModelVersionInfo)

    def test_rebuild_model_version_image(self):
        """Test sdk.rebuild_model_version_image method returns correct answer."""
        self.assertIsInstance(ML_management.sdk.model.rebuild_model_version_image(name=NAME, version=VERSION), bool)

    def test_available_metrics(self):
        """Test sdk.available_metrics method returns correct answer."""
        self.assertIsInstance(ML_management.sdk.job.available_metrics(VERSION), list)
        self.assertIsInstance(ML_management.sdk.job.available_metrics(VERSION)[0], str)

    def test_get_required_classes_by_executor(self):
        """Test sdk.get_required_classes_by_executor method returns correct answer."""
        required_classes = ML_management.sdk.executor.get_required_model_classes_by_executor(name=NAME, version=VERSION)
        self.assertEqual(required_classes, {})

    def test_print_model_schema_for_executor(self):
        """Test a successful sdk.print_model_schema_for_executor call."""
        ML_management.sdk.executor.print_model_schema_for_executor(
            executor_name=NAME, models=[{"name": NAME, "version": VERSION, "role": ROLE}], executor_version=VERSION
        )

    def test_print_datasetloader_schema(self):
        """Test a successful sdk.print_datasetloader_schema call."""
        ML_management.sdk.dataset_loader.print_dataset_loader_schema(name=NAME, version=VERSION)

    def test_print_executor_schema(self):
        """Test a successful sdk.print_executor_schema call."""
        ML_management.sdk.executor.print_executor_schema(name=NAME, version=VERSION)

    def test_print_executor_roles(self):
        """Test a successful sdk.print_executor_roles call."""
        ML_management.sdk.executor.print_executor_roles(name=NAME, version=VERSION)

    def test_cancels(self):
        """Test a successful sdk.cancel_* calls."""
        self.assertIsInstance(
            ML_management.sdk.model.cancel_build_job_for_model_version(model_name=NAME, model_version=VERSION), bool
        )
        self.assertIsInstance(
            ML_management.sdk.executor.cancel_build_job_for_executor_version(
                executor_name=NAME, executor_version=VERSION
            ),
            bool,
        )
        self.assertIsInstance(
            ML_management.sdk.model.cancel_venv_build_job_for_model_version(model_name=NAME, model_version=VERSION),
            bool,
        )
        self.assertIsInstance(ML_management.sdk.job.cancel_job(VERSION), bool)

    def test_delete_objects(self):
        """Test a successful sdk.delete_* calls."""
        self.assertIsInstance(
            ML_management.sdk.model.delete_model_version(model_name=NAME, model_version=VERSION), Union[ModelInfo, None]
        )
        self.assertIsInstance(ML_management.sdk.model.delete_model(model_name=NAME), bool)
        self.assertIsInstance(
            ML_management.sdk.executor.delete_executor_version(executor_name=NAME, executor_version=VERSION),
            Union[ExecutorInfo, None],
        )
        self.assertIsInstance(ML_management.sdk.executor.delete_executor(executor_name=NAME), bool)
        self.assertIsInstance(ML_management.sdk.dataset_loader.delete_dataset_loader(dataset_loader_name=NAME), bool)
        self.assertIsInstance(
            ML_management.sdk.dataset_loader.delete_dataset_loader_version(
                dataset_loader_name=NAME, dataset_loader_version=VERSION
            ),
            Union[DatasetLoaderInfo, None],
        )


if __name__ == "__main__":
    unittest.main()
