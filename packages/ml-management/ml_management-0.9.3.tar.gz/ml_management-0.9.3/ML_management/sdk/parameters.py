"""Module with pydantics model representing parameters of sdk functions."""
import json
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, PositiveInt

from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import DatasetLoaderMethodName
from ML_management.executor import BaseExecutor
from ML_management.mlmanagement.upload_model_mode import UploadModelMode
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.model.model_type_to_methods_map import ModelMethodName


class ModelMethodParams(BaseModel):
    """Class for parameters for one model method.

    Attributes
    ----------
    method: ModelMethodName
        method of model.
    params: dict
        parameters for method.
        Example::

            {key1: value1, key2: value2}

    """

    method: ModelMethodName
    params: dict

    def serialize(self) -> dict:
        return {self.method.value: self.params}

    def serialize_gql(self) -> dict:
        return {"methodName": self.method.value, "methodParams": json.dumps(self.params)}


class DatasetLoaderMethodParams(BaseModel):
    """Class for parameters for one dataset loader method.

    Attributes
    ----------
    method: DatasetLoaderMethodName
        method of dataset loader.
    params: dict
        parameters for method.
        Example::

            {key1: value1, key2: value2}

    """

    method: DatasetLoaderMethodName = DatasetLoaderMethodName.get_dataset
    params: dict

    def serialize(self) -> dict:
        return {self.method.value: self.params}

    def serialize_gql(self) -> dict:
        return {"methodName": self.method.value, "methodParams": json.dumps(self.params)}


class ModelVersionChoice(BaseModel):
    """Class for model version choice in add_ml_job.

    Attributes
    ----------
    name: str
        Name of the model to interact with.
    version: Optional[int] = None
        Version of the model to interact with.
        Default: None, "latest" version is used.
    """

    name: str
    version: Optional[PositiveInt] = None

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
        }

    def serialize_gql(self):
        return {"name": self.name, "version": self.version}


class ModelForm(BaseModel):
    """Class for single model parameters for add_ml_job function.

    Attributes
    ----------
    model_version_choice: ModelVersionChoice
        parameters that determine which model to use.
    params: List[ModelMethodParams] = []
        List of ModelMethodParams with parameters of model methods.
        Example::

            [
                ModelMethodParams(method=ModelMethodName.evaluate_function, params={key1: value1, key2: value2}),
                ModelMethodParams(method=ModelMethodName.finetune_function, params={key1: value1, key2: value2})
            ]

        Default: [].
    """

    model_version_choice: ModelVersionChoice
    params: List[ModelMethodParams] = []

    def serialize(self) -> List[dict]:
        return [
            {
                "role": BaseExecutor.DEFAULT_ROLE,
                "model": self.model_version_choice.serialize(),
                "params": [method_params.serialize() for method_params in self.params],
            }
        ]

    def serialize_gql(self):
        return [
            {
                "modelParams": {
                    "listModelMethodParams": [method_params.serialize_gql() for method_params in self.params],
                    "modelVersionChoice": self.model_version_choice.serialize_gql(),
                },
                "role": BaseExecutor.DEFAULT_ROLE,
            }
        ]


class ModelWithRole(ModelForm):
    """Class for one role model with parameters for add_ml_job function.

    Same as ModelForm except parameter role: str is required.

    Attributes
    ----------
    model_version_choice: ModelVersionChoice
        parameters that determine which model to use.
    params: List[ModelMethodParams] = []
        List of ModelMethodParams with parameters of model methods.
        Example::

            [
                ModelMethodParams(method=ModelMethodName.evaluate_function, params={key1: value1, key2: value2}),
                ModelMethodParams(method=ModelMethodName.finetune_function, params={key1: value1, key2: value2})
            ]

        Default: [].
    new_model_name: Optional[str] = None
        Name of the model to save in case new model is to be created as a result of job execution.
        (regulated by executor.upload_model_mode).
        Default: None.
    new_model_description: Optional[str] = None
        Description of the new model name.
        Default: None.
    prepare_new_model_inference: bool = False
        Start preparing the environment for the inference of the new model.
        Default: False.
    role: str
        Role of the model.
    """

    role: str

    def serialize(self) -> List[dict]:
        result = super().serialize()
        result[0]["role"] = self.role
        return result

    def serialize_gql(self) -> List[dict]:
        result = super().serialize_gql()
        result[0]["role"] = self.role
        return result


class AnyModelForm(BaseModel):
    """Class for definition of arbitrary number of models used in job with their roles.

    Attributes
    ----------
    models: List[ModelWithRole]

        Example (Both instances of ModelWithRole and usual list of dicts may be used)::

            [
                ModelWithRole(
                    role="role_one",
                    model_version_choice=ModelVersionChoice(
                        name="model_1_name",
                        version=1,  # Optional. Default: latest version
                    )
                    params=[
                        ModelMethodParams(
                            method=ModelMethodName.evaluate_function,
                            params={key1: value1, key2: value2}
                        ),
                        ModelMethodParams(
                            method=ModelMethodName.finetune_function,
                            params={key1: value1, key2: value2}
                        )
                    ]
                    new_model_name="some_name"  # Optional. Default: None
                    new_model_description="some_description" # Optional. Default: None
                ),
                ModelWithRole(
                    role="role_two",
                    model_version_choice=ModelVersionChoice(name="model_2_name"),
                    params=[
                        ModelMethodParams(
                            method=ModelMethodName.evaluate_function,
                            params={key1: value1, key2: value2}
                        ),
                        ModelMethodParams(
                            method=ModelMethodName.finetune_function,
                            params={key1: value1, key2: value2}
                        )
                    ]
                )
            ]

    """

    models: List[ModelWithRole]

    def serialize(self) -> List[dict]:
        if len(self.models) == 0:
            return []

        result = self.models[0].serialize()
        for model in self.models[1:]:
            result.extend(model.serialize())
        return result

    def serialize_gql(self) -> List[dict]:
        if len(self.models) == 0:
            return []

        result = self.models[0].serialize_gql()
        for model in self.models[1:]:
            result.extend(model.serialize_gql())
        return result


class DatasetLoaderForm(BaseModel):
    """Class for single dataset loader parameters for add_ml_job function.

    Attributes
    ----------
    name: str
        Name of the DatasetLoader that the model will use.
    version: Optional[int] = None
        Version of the DatasetLoader that the model will interact with.
        Default: None, "latest" version is used.
    params: List[DatasetLoaderMethodParams] = []
        List of DatasetLoaderMethodParams with parameters of model methods.
        Example::

            [
                DatasetLoaderMethodParams(
                    # by default params are set for DatasetLoaderMethodName.get_dataset method
                    params={key1: value1, key2: value2}
                ),
                DatasetLoaderMethodParams(
                    method=DatasetLoaderMethodName.<some_method>,
                    params={key1: value1, key2: value2}
                )
            ]

        Default: [].
    collector_name: {"s3", }
        Name of the collector to interact with. Default: "s3"
    collector_params: dict
        Dictionary of collector parameters.
        Example::

            {"bucket": "mnist"}

    """

    name: str
    params: List[DatasetLoaderMethodParams] = []
    collector_params: dict
    version: Optional[PositiveInt] = None
    collector_name: str = "s3"

    def serialize(self) -> List[dict]:
        return [
            {
                "role": BaseExecutor.DEFAULT_ROLE,
                "data_params": {
                    "collector_name": self.collector_name,
                    "collector_params": self.collector_params,
                    "dataset_loader_name": self.name,
                    "dataset_loader_version": self.version,
                    "dataset_loader_params": [method_params.serialize() for method_params in self.params],
                },
            }
        ]

    def serialize_gql(self) -> List[dict]:
        return [
            {
                "dataParams": {
                    "collectorMethodParams": {
                        "methodName": "collector_method",
                        "methodParams": json.dumps(self.collector_params),
                    },
                    "collectorName": self.collector_name,
                    "datasetLoaderVersionChoice": {"name": self.name, "version": self.version},
                    "listDatasetLoaderMethodParams": [method_params.serialize_gql() for method_params in self.params],
                },
                "role": BaseExecutor.DEFAULT_ROLE,
            }
        ]


class DatasetLoaderWithRole(DatasetLoaderForm):
    """Class for one role dataset loader with parameters for add_ml_job function.

    Same as DatasetLoaderForm except parameter role: str is required.

    Attributes
    ----------
    name: str
        Name of the DatasetLoader that the model will use.
    version: Optional[int] = None
        Version of the DatasetLoader that the model will interact with.
        Default: None, "latest" version is used.
    params: List[DatasetLoaderMethodParams] = []
        List of DatasetLoaderMethodParams with parameters of model methods.
        Example::

            [
                DatasetLoaderMethodParams(
                    # by default params are set for DatasetLoaderMethodName.get_dataset method
                    params={key1: value1, key2: value2}
                ),
                DatasetLoaderMethodParams(
                    method=DatasetLoaderMethodName.<some_method>,
                    params={key1: value1, key2: value2}
                )
            ]

        Default: [].
    collector_name: {"s3", }
        Name of the collector to interact with.
        Default: "s3"
    collector_params: dict
        Dictionary of collector parameters.
        Example::

            {"bucket": "mnist"}

    role: str
        Role of the DatasetLoader.
    """

    role: str

    def serialize(self) -> List[dict]:
        result = super().serialize()
        result[0]["role"] = self.role
        return result

    def serialize_gql(self) -> List[dict]:
        result = super().serialize_gql()
        result[0]["role"] = self.role
        return result


class AnyDatasetLoaderForm(BaseModel):
    """Class for definition of arbitrary number of dataset_loaders used in job with their roles.

    Attributes
    ----------
    datasetloaders: List[DatasetLoaderWithRole]

        Example (Both instances of DatasetLoaderWithRole and usual list of dicts may be used)::

            [
                DatasetLoaderWithRole(
                    role="data1",
                    name="multiple_two_datasets",
                    version=1,  # Optional. Default: latest version
                    params=[
                        DatasetLoaderMethodParams(
                            # by default params are set for DatasetLoaderMethodName.get_dataset method
                            params={key1: value1, key2: value2}
                        ),
                        DatasetLoaderMethodParams(
                            method=DatasetLoaderMethodName.get_dataset,  # or other method
                            params={key1: value1, key2: value2}
                        )
                    ],
                    collector_name="s3",
                    collector_params={"bucket": "mnist"}
                ),
                DatasetLoaderWithRole(
                    role="data2",
                    name="multiple_two_datasets",
                    collector_name="s3",
                    collector_params={"bucket": "mnist"}
                )
            ]

    """

    dataset_loaders: List[DatasetLoaderWithRole]

    def serialize(self) -> List[dict]:
        if len(self.dataset_loaders) == 0:
            return []

        result = self.dataset_loaders[0].serialize()
        for model in self.dataset_loaders[1:]:
            result.extend(model.serialize())
        return result

    def serialize_gql(self) -> List[dict]:
        if len(self.dataset_loaders) == 0:
            return []

        result = self.dataset_loaders[0].serialize_gql()
        for model in self.dataset_loaders[1:]:
            result.extend(model.serialize_gql())
        return result


class UploadOneNewModelForm(BaseModel):
    """Class for definition of parameters of one new model to be uploaded.

    Attributes
    ----------
    upload_model_mode: UploadModelMode
        Option how to upload a new model.
    new_model_name: Optional[str] = None
        Name of the model to save in case new model is to be created as a result of job execution.
        (regulated by upload_model_mode).
        Default: None.
    new_model_description: Optional[str] = None
        Description of the new model name.
        Default: None.
    prepare_new_model_inference: bool = False
        Start preparing the environment for the inference of the new model.
        Default: False.
    start_build_new_model_image: bool = True
        Start build image for the new model.
        Default: True.
    new_model_visibility: Union[Literal[VisibilityOptions.PRIVATE, VisibilityOptions.PUBLIC], VisibilityOptions]
        Visibility of the new model to other users. Default: PRIVATE.
    """

    upload_model_mode: UploadModelMode
    new_model_name: Optional[str] = None
    new_model_description: Optional[str] = None
    prepare_new_model_inference: bool = False
    start_build_new_model_image: bool = True
    new_model_visibility: Union[
        Literal[VisibilityOptions.PRIVATE, VisibilityOptions.PUBLIC], VisibilityOptions
    ] = VisibilityOptions.PRIVATE

    def serialize(self) -> dict:
        return {
            BaseExecutor.DEFAULT_ROLE: {
                "upload_model_mode": self.upload_model_mode.name,
                "new_model_name": self.new_model_name,
                "prepare_new_model_inference": self.prepare_new_model_inference,
                "start_build_new_model_image": self.start_build_new_model_image,
                "new_model_visibility": VisibilityOptions(self.new_model_visibility).name,
                "description": self.new_model_description,
            }
        }

    def serialize_gql(self) -> dict:
        return {
            BaseExecutor.DEFAULT_ROLE: {
                "uploadModelMode": self.upload_model_mode.name,
                "newModelName": self.new_model_name,
                "prepareNewModelInference": self.prepare_new_model_inference,
                "startBuildNewModelImage": self.start_build_new_model_image,
                "newModelVisibility": VisibilityOptions(self.new_model_visibility).name,
                "description": self.new_model_description,
            }
        }


class UploadOneNewModelWithRole(UploadOneNewModelForm):
    """Class for definition of parameters of one new model to be uploaded.

    Same as UploadOneNewModelForm except parameter role: str is required.

    Attributes
    ----------
    upload_model_mode: UploadModelMode
        Option how to upload a new model.
    new_model_name: Optional[str] = None
        Name of the model to save in case new model is to be created as a result of job execution.
        (regulated by upload_model_mode).
        Default: None.
    new_model_description: Optional[str] = None
        Description of the new model name.
        Default: None.
    prepare_new_model_inference: bool = False
        Start preparing the environment for the inference of the new model.
        Default: False.
    start_build_new_model_image: bool = True
        Start build image for the new model.
        Default: True.
    new_model_visibility: Union[Literal[VisibilityOptions.PRIVATE, VisibilityOptions.PUBLIC], VisibilityOptions]
        Visibility of the new model to other users. Default: PRIVATE.
    """

    role: str

    def serialize(self) -> dict:
        result = super().serialize()
        result = {self.role: list(result.values())[0]}
        return result

    def serialize_gql(self) -> dict:
        result = super().serialize_gql()
        result = {self.role: list(result.values())[0]}
        return result


class UploadAnyNewModelsForm(BaseModel):
    """Class for definition of parameters new models to be uploaded."""

    upload_models_params: List[UploadOneNewModelWithRole]

    def serialize(self) -> dict:
        if len(self.upload_models_params) == 0:
            return {}

        result = self.upload_models_params[0].serialize()
        for params in self.upload_models_params[1:]:
            result.update(params.serialize())
        if len(self.upload_models_params) != len(result):
            raise ValueError("All roles must be different, you can not pass same role twice.")
        return result

    def serialize_gql(self) -> dict:
        if len(self.upload_models_params) == 0:
            return {}

        result = self.upload_models_params[0].serialize_gql()
        for params in self.upload_models_params[1:]:
            result.update(params.serialize_gql())
        if len(self.upload_models_params) != len(result):
            raise ValueError("All roles must be different, you can not pass same role twice.")
        return result


class ResourcesForm(BaseModel):
    """Class for definition of resources required for job execution.

    The computing cluster distributes all resources equally among the allocated nodes.
    If such an equal distribution is not possible, the job will be rejected.

    Attributes
    ----------
    cpus: PositiveInt
        Number of cpus to use in job. Default: 1.
    memory_per_node: PositiveInt
        Number of memory in GB that is required for job process on one node.
        If job has started successfully this amount of memory is guaranteed for you,
        but exceeding the amount of this memory can lead to OOM-kill result.
        IMPORTANT: some job execution backends may spend this memory for job image unpacking,
        it is always true in case of distributed jobs, because they are supported only by one execution backend.
        Default: 8.
    gpu_number: int
        Number of gpu to be used in job. Default: 0.
    gpu_type: Optional[str]
        Type of gpu to be used in job. If you require specific gpu type, i.e. A100,
        you should specify this parameter. Default: None.
    """

    cpus: PositiveInt = 1
    memory_per_node: PositiveInt = 8
    gpu_number: int = Field(0, ge=0)
    gpu_type: Optional[str] = None
