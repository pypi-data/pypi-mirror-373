"""General Job behavior."""
import json
import os
from typing import Optional

from ML_management import mlmanagement, variables
from ML_management.collectors import COLLECTORS
from ML_management.collectors.collector_pattern_to_methods_map import CollectorMethodName
from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import DatasetLoaderMethodName
from ML_management.executor.executor_pattern_to_methods_map import ExecutorMethodName
from ML_management.graphql.schema import ExecutionJob
from ML_management.job.params_prepare import method_params_prepare
from ML_management.job.utils import (
    get_collector_params,
    get_dataset_loader_name_version,
    get_dataset_loaders_params,
    get_model_params,
    get_source_models_name_version,
    prepare_artifacts,
)
from ML_management.mlmanagement.load_api import load_dataset, load_executor, load_model
from ML_management.mlmanagement.upload_model_mode import UploadModelMode
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.model.model_type_to_methods_map import ModelMethodName


class Job:
    """Class of job."""

    def __init__(
        self,
        logger,
        preload_models: Optional[dict] = None,
        preload_dataset_loaders: Optional[dict] = None,
        preload_executor=None,
    ):
        self.logger = logger
        self.role_model_map = {}
        self.role_dataset_loader_map = {}
        self.executor = None
        if preload_models:
            self.role_model_map = preload_models

        if preload_dataset_loaders:
            self.role_dataset_loader_map = preload_dataset_loaders
        if preload_executor:
            self.executor = preload_executor

    def unset_dataset(self) -> None:
        """Unset dataset for model and executor instance before logging."""
        self.executor.role_dataset_loader_map = {}
        for role in self.role_model_map:
            self.role_model_map[role].dataset = None

    def set_device(self, device) -> None:
        """Set device for executor instance variable."""
        self.executor.device = device

    def set_model_log_args(self, params):
        """Set additional arguments for log_model() to model instance."""
        new_model_names = {}
        for role_params in params.list_role_model_params:
            # if field==null, sgqlc instantiate empty class without attributes
            if not hasattr(role_params.upload_params, "upload_model_mode"):
                continue
            if role_params.upload_params.new_model_name is None:
                continue
            new_model_names[role_params.role] = role_params.upload_params.new_model_name
        for role, name_version in self.source_models_name_version.items():
            self.role_model_map[role].source_model_name = name_version["name"]
            self.role_model_map[role].source_model_version = name_version["version"]
            self.role_model_map[role].source_executor_name = self.executor_name
            self.role_model_map[role].source_executor_version = self.executor_version
            self.role_model_map[role].source_executor_role = role
            self.role_model_map[role].model_name = (
                name_version["name"] if role not in new_model_names else new_model_names[role]
            )

    @staticmethod
    def get_init_parameters_from_dict(params):
        """Get __init__ params from list of method_params."""
        for param in params:
            if param["method_name"] == ModelMethodName.init.value:
                return param["method_params"]
        return {}

    def load_models(self) -> None:
        if self.role_model_map:
            return
        for role, model in self.source_models_name_version.items():
            self.logger.info(f"Start to load model name: {model['name']} version: {model['version']}")
            self.role_model_map[role] = load_model(
                model["name"],
                model["version"],
                False,
                f"model-{role}",
                self.get_init_parameters_from_dict(self.model_params[role]["model_methods_params"]),
            ).loaded_object
            self.logger.info(f"The model name: {model['name']} version: {model['version']} was loaded successfully")

    def load_dataset_loaders(self) -> None:
        if self.role_dataset_loader_map:
            return
        for role, dataset_loader in self.dataset_loader_name_version.items():
            self.logger.info(
                f"Start to load datasetloader name: {dataset_loader['name']} version: {dataset_loader['version']}"
            )
            self.role_dataset_loader_map[role] = load_dataset(
                dataset_loader["name"],
                int(dataset_loader["version"]),
                False,
                kwargs_for_init=self.get_init_parameters_from_dict(
                    self.dataset_loader_params[role]["dataset_loader_methods_params"]
                ),
            ).loaded_object
            self.logger.info(
                f"The datasetloader name: {dataset_loader['name']} version: {dataset_loader['version']} "
                f"was loaded successfully"
            )

    def setup_dataset_loader_method_parameters(self) -> None:
        self.executor.dataset_loader_method_parameters_dict = {}
        for role, dl_params in self.dataset_loader_params.items():
            self.executor.dataset_loader_method_parameters_dict[role] = {
                DatasetLoaderMethodName(p["method_name"]): method_params_prepare(
                    self.role_dataset_loader_map[role], p["method_name"], p["method_params"]
                )
                for p in dl_params["dataset_loader_methods_params"]
            }

    def setup_models_parameters(self) -> None:
        self.executor.model_method_parameters_dict = {}
        for role, m_params in self.model_params.items():
            self.executor.model_method_parameters_dict[role] = {
                ModelMethodName(p["method_name"]): method_params_prepare(
                    self.role_model_map[role], p["method_name"], p["method_params"]
                )
                for p in m_params["model_methods_params"]
            }

    def load_entities(self, params) -> None:
        self.executor_name: str = params.executor_params.executor_version_choice.name
        self.executor_version: int = params.executor_params.executor_version_choice.version
        self.list_role_model_method_params: list = params.list_role_model_params
        self.list_role_data_params: list = params.list_role_data_params

        # MODELS
        self.model_params = get_model_params(self.list_role_model_method_params)
        self.source_models_name_version = get_source_models_name_version(self.list_role_model_method_params)
        self.load_models()

        # EXECUTOR
        if not self.executor:
            self.logger.info(f"Start to load executor name: {self.executor_name} version: {self.executor_version}")
            self.executor = load_executor(self.executor_name, self.executor_version, False).loaded_object
            self.logger.info("The executor was loaded successfully")

        # COLLECTORS
        collectors = {
            data_param_role.role: data_param_role.data_params.collector_name
            for data_param_role in self.list_role_data_params
        }
        self.logger.info("Start to load collectors")
        self.role_collectors_map = {role: COLLECTORS[collector_name]() for role, collector_name in collectors.items()}
        self.logger.info("Collectors was loaded successfully")

        # DATASETLOADERS
        self.dataset_loader_params = get_dataset_loaders_params(self.list_role_data_params)
        self.dataset_loader_name_version = get_dataset_loader_name_version(self.list_role_data_params)
        self.load_dataset_loaders()

    def setup_entities(self, params) -> None:
        if not self.is_distributed:
            self.set_model_log_args(params)

        self.executor.role_model_map = self.role_model_map
        self.executor.role_dataset_loader_map = self.role_dataset_loader_map
        self.set_device("cuda" if params.resources.gpu_number != 0 else "cpu")

        self.setup_dataset_loader_method_parameters()
        self.setup_models_parameters()

    def pull_data(self, params) -> None:
        self.list_role_data_params: list = params.list_role_data_params

        # PULL DATA BY COLLECTORS
        collector_params = get_collector_params(self.list_role_data_params)
        collector_method_name_map = {
            role: collector_param["method_name"] for role, collector_param in collector_params.items()
        }
        collector_method_params_map = {
            role: json.loads(collector_param["method_params"]) for role, collector_param in collector_params.items()
        }
        for role, collector in self.role_collectors_map.items():
            try:
                self.role_dataset_loader_map[role].data_path = getattr(
                    collector, CollectorMethodName(collector_method_name_map[role]).name
                )(**collector_method_params_map[role])
            except Exception as err:
                self.logger.info(f"Error during data collection of {role} collector.")
                raise err

        # LOAD DATA IN DATASETLOADERS
        self.executor.role_dataset_map = {}
        for role, dataset_loader in self.role_dataset_loader_map.items():
            try:
                self.executor.role_dataset_map[role] = dataset_loader.get_dataset(
                    **self.executor.dataset_loader_method_parameters_dict[role][DatasetLoaderMethodName.get_dataset]
                )
            except Exception as err:
                self.logger.info(f"Error during data loading by {role} dataset loader.")
                raise err

    def set_params_for_distributed_tasks(self) -> None:
        self.executor.nodes = os.getenv("SLURM_JOB_NODELIST", "").split(",")
        self.executor.master_addr = os.getenv("MASTER_ADDR")
        self.executor.master_port = int(os.getenv("MASTER_PORT", "0"))
        self.executor.node_rank = int(os.getenv("LOCAL_RANK", "-1"))

    def run_job(self, job: ExecutionJob):
        """General protocol."""
        experiment_name = job.experiment.name
        self.is_distributed = job.is_distributed
        params = job.params
        self.load_entities(params=params)
        self.setup_entities(params=params)
        self.pull_data(params=params)
        if self.is_distributed:
            self.set_params_for_distributed_tasks()

        self.logger.info("Start executor methods for job ...")

        try:
            executor_method_name = params.executor_params.executor_method_params.method_name
            executor_method_params = method_params_prepare(
                self.executor,
                ExecutorMethodName(executor_method_name).name,
                json.loads(params.executor_params.executor_method_params.method_params),
            )
            artifacts = getattr(self.executor, ExecutorMethodName(executor_method_name).name)(**executor_method_params)
        except Exception as err:
            self.logger.error(f"Error during execution of the job with obj_uuid {variables.secret_uuid}.")
            raise err

        if self.is_distributed:
            return
        try:
            self.unset_dataset()
            self.logger.info("Start uploading model")
            for role_params in params.list_role_model_params:
                # if field==null, sgqlc instantiate empty class without attributes
                if not hasattr(role_params.upload_params, "upload_model_mode"):
                    continue
                role = role_params.role
                upload_model_mode = role_params.upload_params.upload_model_mode
                prepare_new_model_inference = role_params.upload_params.prepare_new_model_inference
                description = role_params.upload_params.description
                start_build_new_model_image = role_params.upload_params.start_build_new_model_image
                new_model_visibility = role_params.upload_params.new_model_visibility
                registered_model_name = (
                    role_params.upload_params.new_model_name
                    if upload_model_mode == UploadModelMode.new_model
                    else self.source_models_name_version[role]["name"]
                )
                if not isinstance(registered_model_name, str):
                    raise RuntimeError(registered_model_name)

                if artifacts is not None:
                    prepare_artifacts(artifacts, role, self.role_model_map, registered_model_name)

                model_path = os.path.dirname(self.role_model_map[role].artifacts)
                # child model needs to have same additional local dependencies as a parent
                # in current folder structure we know that each folder beside model folder
                # is folder with additional local dependencies
                additional_local_dependencies = os.listdir(os.path.dirname(model_path))
                additional_local_dependencies = [
                    os.path.join(os.path.dirname(model_path), folder) for folder in additional_local_dependencies
                ]
                additional_local_dependencies.remove(model_path)
                mlmanagement.log_api._log_object_src(
                    artifact_path="",
                    description=description,
                    registered_model_name=registered_model_name,
                    source_model_name=self.source_models_name_version[role]["name"],
                    source_model_version=int(self.source_models_name_version[role]["version"]),
                    source_executor_name=self.executor_name,
                    source_executor_version=self.executor_version,
                    source_executor_role=role,
                    upload_model_mode=upload_model_mode,
                    model_path=model_path,
                    create_venv_pack=prepare_new_model_inference,
                    additional_local_packages=additional_local_dependencies,
                    experiment_name=experiment_name,
                    start_build=start_build_new_model_image,
                    visibility=VisibilityOptions[new_model_visibility],
                )
                self.logger.info(f"Model: {registered_model_name}, role: {role} logged successfully.")
        except Exception as err:
            self.logger.error(f"Error during execution of the job with obj_uuid {variables.secret_uuid}.")
            raise err
