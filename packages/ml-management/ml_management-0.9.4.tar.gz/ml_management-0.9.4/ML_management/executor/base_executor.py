"""Executor template for custom executor."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from ML_management.dataset_loader import DatasetLoaderPattern
from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import DatasetLoaderMethodName
from ML_management.executor.patterns import (
    DEFAULT_ROLE,
    ArbitraryDatasetLoaderPattern,
    ArbitraryModelsPattern,
    OneDatasetLoaderPattern,
    OneModelPattern,
)
from ML_management.model.model_type_to_methods_map import ModelMethodName
from ML_management.model.patterns.model_pattern import Model

default_dataset_loader_pattern = OneDatasetLoaderPattern()


class BaseExecutor(ABC):
    """Define custom job executor."""

    DEFAULT_ROLE = DEFAULT_ROLE

    def __init__(
        self,
        executor_models_pattern: Union[OneModelPattern, ArbitraryModelsPattern],
        executor_dataset_loaders_pattern: Union[OneDatasetLoaderPattern, ArbitraryDatasetLoaderPattern, None] = None,
    ) -> None:
        """
        Init Executor class.

        Parameters
        ----------
        executor_models_pattern: Union[OneModelPattern, ArbitraryModelsPattern]
            Pattern of interaction with models.
        executor_datasets_pattern: Union[OneDatasetLoaderPattern, ArbitraryDatasetLoaderPattern
            Pattern of datasets usage. Default: OneDatasetLoaderPattern()

        Returns
        -------
        None

        """
        if executor_dataset_loaders_pattern is None:
            executor_dataset_loaders_pattern = default_dataset_loader_pattern

        if not isinstance(executor_models_pattern, OneModelPattern) and not isinstance(
            executor_models_pattern, ArbitraryModelsPattern
        ):
            raise TypeError(
                "param executor_models_pattern must be instance of OneModelPattern or ArbitraryModelsPattern"
            )
        if not isinstance(executor_dataset_loaders_pattern, OneDatasetLoaderPattern) and not isinstance(
            executor_dataset_loaders_pattern, ArbitraryDatasetLoaderPattern
        ):
            raise TypeError(
                "param executor_datasets_pattern must be instance of OneDatasetPattern or ArbitraryDatasetPattern"
            )
        self.desired_model_methods = executor_models_pattern.serialize()
        self.desired_dataset_loader_methods = executor_dataset_loaders_pattern.serialize()
        for methods_list in self.desired_dataset_loader_methods.values():
            if DatasetLoaderMethodName.get_dataset not in methods_list:
                raise RuntimeError(
                    "Every dataset loader must have DatasetLoaderMethodName.get_dataset method in desired methods."
                )
        # because each class always have init and we do not want init in desired methods written by user.
        for role, methods_list in self.desired_model_methods.items():
            if ModelMethodName.init not in methods_list:
                self.desired_model_methods[role].append(ModelMethodName.init)

        for role, methods_list in self.desired_dataset_loader_methods.items():
            if DatasetLoaderMethodName.init not in methods_list:
                self.desired_dataset_loader_methods[role].append(ModelMethodName.init)

        # That parameters will be set automatically while loading the model.
        self.artifacts: str

        # That parameter will be set automatically in job before the 'execute' func would be executed.
        self.role_dataset_loader_map: Dict[str, DatasetLoaderPattern] = {}
        self.device = None
        self.role_model_map: Dict[str, Model] = {}
        self.role_dataset_map: Dict[str, Any] = {}
        self.dataset_loader_method_parameters_dict: Dict[str, Dict[DatasetLoaderMethodName, dict]] = {}
        self.model_method_parameters_dict: Dict[str, Dict[ModelMethodName, dict]] = {}

    @abstractmethod
    def execute(self, **executor_params):
        """
        Do execution step.

        Attributes
        ----------
        artifacts: str
            local path to artifacts.
        role_model_map: Dict[str, Model]
            role to model map. Default: {}.
        role_dataset_loader_map: Dict[str, DatasetLoaderPattern]
            role to dataset loader map. Default: {}.
        role_dataset_map: Dict[str, Any]
            role to dataset map.
            Dataset is an object obtained as a result of calling the 'get_dataset' function
            from a dataset loader with the same role. Default: {}.
        device: str
            name of the device ('cpu' - CPU, 'cuda' - GPU instance). Default: None.
        model_method_parameters_dict: Dict[str, Dict[ModelMethodName, dict]]
            the dict of parameters for each desired_model_methods.
            One could use it in execute() function like that::

                def execute(self):
                    self.role_model_map["role_model"].train_function(
                        **self.model_method_parameters_dict["role_model"][ModelMethodName.train_function]
                    )

            In that case method 'execute' calls train_function method of the model with corresponding parameters
            for that method. Default: {}.
        dataset_loader_method_parameters_dict: Dict[str, Dict[DatasetLoaderMethodName, dict]]
            the dict of params for each desired_dataset_loader_methods.
            One could use it in execute() function like that::

                def execute(self):
                    self.role_dataset_loader_map["role_dataset"].get_dataset(
                        **self.dataset_loader_method_parameters_dict["role_dataset"][DatasetLoaderMethodName.get_dataset]
                    )

            In that case method 'execute' calls get_dataset method of the dataset loader with corresponding parameters
            for that method. Default: {}.

        Returns
        -------
        None
        """
        raise NotImplementedError

    @property
    def model(self) -> Model:
        """Property returning a single model.

        :return: python model
        """
        if len(self.role_model_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.role_model_map.values())[0]

    @model.setter
    def model(self, model):
        """Property to change the model.

        :param: python model
        """
        if len(self.role_model_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        self.role_model_map[list(self.role_model_map.keys())[0]] = model

    @property
    def dataset_loader(self) -> DatasetLoaderPattern:
        """Property returning a single dataset loader.

        :return: dataset loader object
        """
        if len(self.role_dataset_loader_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset loader")
        return list(self.role_dataset_loader_map.values())[0]

    @dataset_loader.setter
    def dataset_loader(self, dataset_loader: DatasetLoaderPattern):
        """Property to change the dataset loader.

        :param: dataset loader object
        """
        if len(self.role_dataset_loader_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset loader")
        self.role_dataset_loader_map[list(self.role_dataset_loader_map.keys())[0]] = dataset_loader

    @property
    def model_methods_parameters(self) -> Dict[ModelMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: the dict of parameters for each desired_model_methods
        """
        if len(self.model_method_parameters_dict) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.model_method_parameters_dict.values())[0]

    @property
    def dataset_loader_methods_parameters(self) -> Dict[DatasetLoaderMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: the dict of parameters for each desired_dataset_loader_methods
        """
        if len(self.dataset_loader_method_parameters_dict) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.dataset_loader_method_parameters_dict.values())[0]

    @property
    def dataset(self):
        """Property returning a single dataset.

        :return: dataset object
        """
        if len(self.role_dataset_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset")
        return list(self.role_dataset_map.values())[0]

    @dataset.setter
    def dataset(self, dataset: Any):
        """Property to change the dataset.

        :param: dataset object
        """
        if len(self.role_dataset_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset")
        self.role_dataset_map[list(self.role_dataset_map.keys())[0]] = dataset


class BaseExecutorDistributed(BaseExecutor):
    """Define custom job executor for job that can be executed in distributed mode."""

    def __init__(
        self,
        executor_models_pattern: Union[OneModelPattern, ArbitraryModelsPattern],
        executor_dataset_loaders_pattern: Union[OneDatasetLoaderPattern, ArbitraryDatasetLoaderPattern, None] = None,
    ) -> None:
        super().__init__(
            executor_models_pattern=executor_models_pattern,
            executor_dataset_loaders_pattern=executor_dataset_loaders_pattern,
        )
        # attributes related to distributed job execution
        self.nodes: list[str] = []
        self.master_addr: Optional[str] = None
        self.master_port: Optional[int] = None
        self.node_rank: Optional[int] = None

    @property
    def nodes_number(self) -> int:
        return len(self.nodes)
