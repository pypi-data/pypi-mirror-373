"""Define finetune executor class."""
from ML_management.executor.base_executor import BaseExecutor
from ML_management.executor.patterns import OneModelPattern
from ML_management.model.model_type_to_methods_map import ModelMethodName


class FinetuneExecutor(BaseExecutor):
    """Finetune executor from pattern with defined settings parameters."""

    def __init__(self):
        super().__init__(
            executor_models_pattern=OneModelPattern(
                desired_model_methods=[ModelMethodName.finetune_function],
            ),
        )

    def execute(self):
        """Define execute function that calls finetune_function of model with corresponding params."""
        self.model.dataset = self.dataset
        return self.model.finetune_function(**self.model_methods_parameters[ModelMethodName.finetune_function])
