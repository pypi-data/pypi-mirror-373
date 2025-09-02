"""Define train executor class."""
from ML_management.executor.base_executor import BaseExecutor
from ML_management.executor.patterns import OneModelPattern
from ML_management.model.model_type_to_methods_map import ModelMethodName


class TrainExecutor(BaseExecutor):
    """Train executor from pattern with defined settings parameters."""

    def __init__(self):
        super().__init__(
            executor_models_pattern=OneModelPattern(
                desired_model_methods=[ModelMethodName.train_function],
            ),
        )

    def execute(self):
        """Define execute function that calls train_function of model with corresponding params."""
        self.model.dataset = self.dataset
        return self.model.train_function(**self.model_methods_parameters[ModelMethodName.train_function])
