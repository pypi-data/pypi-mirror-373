"""Map supported model types to their unique abstract functions."""
from enum import Enum

from ML_management.model.patterns.evaluatable_model import EvaluatableModel
from ML_management.model.patterns.gradient_model import GradientModel
from ML_management.model.patterns.model_pattern import Model
from ML_management.model.patterns.model_with_losses import ModelWithLosses
from ML_management.model.patterns.model_with_metrics import ModelWithMetrics
from ML_management.model.patterns.preprocessor import Preprocessor
from ML_management.model.patterns.retrainable_model import RetrainableModel
from ML_management.model.patterns.target_layer import TargetLayer
from ML_management.model.patterns.torch_model import TorchModel
from ML_management.model.patterns.trainable_model import TrainableModel
from ML_management.model.patterns.transformer import Transformer


class ModelMethodName(str, Enum):
    """Map supported model function names to infer jsonschemas."""

    train_function = "train_function"
    predict_function = "predict_function"
    finetune_function = "finetune_function"
    get_nn_module = "get_nn_module"
    evaluate_function = "evaluate_function"
    get_target_layer = "get_target_layer"
    get_losses = "get_losses"
    get_grad = "get_grad"
    preprocess = "preprocess"
    transform = "transform"
    reset_metrics = "reset_metrics"
    update_metrics = "update_metrics"
    compute_metrics = "compute_metrics"
    init = "__init__"


# link model pattern to it abstract functions
model_pattern_to_methods = {
    Model: [ModelMethodName.predict_function, ModelMethodName.init],
    TrainableModel: [ModelMethodName.train_function],
    RetrainableModel: [ModelMethodName.finetune_function],
    TorchModel: [ModelMethodName.get_nn_module],
    TargetLayer: [ModelMethodName.get_target_layer],
    EvaluatableModel: [ModelMethodName.evaluate_function],
    ModelWithLosses: [ModelMethodName.get_losses],
    GradientModel: [ModelMethodName.get_grad],
    Preprocessor: [ModelMethodName.preprocess],
    Transformer: [ModelMethodName.transform],
    ModelWithMetrics: [ModelMethodName.reset_metrics, ModelMethodName.update_metrics, ModelMethodName.compute_metrics],
}
