# Core functionality
from .algo import (
    unlearn,
    UnlearningAlgorithmFactory,
    UnlearningResult,
    NaiveRetraining,
    GradientAscentUnlearning,
    InfluenceFunctionUnlearning,
    SISAUnlearning,
)

from .eval import (
    UnlearningEvaluator,
    EvaluationMetrics,
    UnlearningEvaluationResult,
    evaluate_unlearning_result,
)

from .verify import (
    UnlearningVerifier,
    VerificationResult,
    ComprehensiveVerificationResult,
    verify_unlearning_simple,
)

from .tools.dataset import (
    Dataset,
    UnlearningDataSplit,
    DatasetLoader,
    UnlearningDataSplitter,
    DatasetType,
)

from .utils.utils import ExperimentConfig, Timer, setup_logging, DataUtils, ModelUtils


# Convenience functions
def quick_unlearn(model, method, forget_data, retain_data=None, **kwargs):
    """
    Quick unlearning with evaluation and verification

    Args:
        model: Trained model
        method: Unlearning method name
        forget_data: Data to forget (Dataset object or tuple (X, y))
        retain_data: Data to retain (Dataset object or tuple (X, y))
        **kwargs: Additional parameters

    Returns:
        Dictionary with unlearning result, evaluation, and verification
    """
    # Convert data if needed
    if not isinstance(forget_data, Dataset):
        forget_data = Dataset(X=forget_data[0], y=forget_data[1])

    if retain_data and not isinstance(retain_data, Dataset):
        retain_data = Dataset(X=retain_data[0], y=retain_data[1])

    # Perform unlearning
    unlearn_result = unlearn(model, method, forget_data, retain_data, **kwargs)

    return {
        "unlearning_result": unlearn_result,
        "execution_time": unlearn_result.execution_time,
        "metrics": unlearn_result.metrics,
    }


# Package metadata
__all__ = [
    # Core functions
    "unlearn",
    "quick_unlearn",
    # Algorithms
    "UnlearningAlgorithmFactory",
    "UnlearningResult",
    "NaiveRetraining",
    "GradientAscentUnlearning",
    "InfluenceFunctionUnlearning",
    "SISAUnlearning",
    # Evaluation
    "UnlearningEvaluator",
    "EvaluationMetrics",
    "UnlearningEvaluationResult",
    "evaluate_unlearning_result",
    # Verification
    "UnlearningVerifier",
    "VerificationResult",
    "ComprehensiveVerificationResult",
    "verify_unlearning_simple",
    # Data handling
    "Dataset",
    "UnlearningDataSplit",
    "DatasetLoader",
    "UnlearningDataSplitter",
    "DatasetType",
    # Utilities
    "ExperimentConfig",
    "Timer",
    "setup_logging",
    "DataUtils",
    "ModelUtils",
]
