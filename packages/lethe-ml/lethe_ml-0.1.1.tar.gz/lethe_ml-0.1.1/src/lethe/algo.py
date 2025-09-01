from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import accuracy_score
import copy
import logging
from pydantic import BaseModel, Field, ConfigDict
import sys
from pathlib import Path

try:
    # Try relative imports first (when run as package)
    from .utils.utils import Timer, timing_decorator
    from .tools.dataset import Dataset, UnlearningDataSplit
except ImportError:
    try:
        # Try absolute imports
        from lethe.utils.utils import Timer, timing_decorator
        from lethe.tools.dataset import Dataset, UnlearningDataSplit
    except ImportError:
        # Fallback for standalone execution
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        sys.path.insert(0, str(parent_dir))

        from utils.utils import Timer, timing_decorator
        from tools.dataset import Dataset

logger = logging.getLogger("lethe.algorithms")


class UnlearningResult(BaseModel):
    """Result container for unlearning operations"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    unlearned_model: Any = Field(..., description="The unlearned model")
    original_model: Any = Field(..., description="Reference to original model")
    method: str = Field(..., description="Unlearning method used")
    metrics: Dict[str, float] = Field(
        default_factory=dict, description="Performance metrics"
    )
    execution_time: float = Field(0.0, description="Time taken for unlearning")
    hyperparameters: Dict[str, Any] = Field(
        default_factory=dict, description="Method hyperparameters"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class BaseUnlearningAlgorithm(ABC):
    """Base class for all machine unlearning algorithms"""

    def __init__(self, **kwargs):
        self.hyperparameters = kwargs
        self.is_fitted = False

    @abstractmethod
    def unlearn(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset] = None
    ) -> UnlearningResult:
        """
        Abstract method for unlearning implementation

        Args:
            model: Trained model to unlearn from
            forget_data: Data to be forgotten
            retain_data: Data to be retained (optional)

        Returns:
            UnlearningResult object with unlearned model and metrics
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the unlearning algorithm"""
        pass

    def validate_inputs(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset] = None
    ) -> None:
        """Validate inputs before unlearning"""
        if not hasattr(model, "fit"):
            raise ValueError("Model must have a 'fit' method")

        if not hasattr(model, "predict"):
            raise ValueError("Model must have a 'predict' method")

        if not forget_data.has_labels:
            raise ValueError("Forget data must have labels")

        if retain_data is not None and not retain_data.has_labels:
            raise ValueError("Retain data must have labels if provided")


class NaiveRetraining(BaseUnlearningAlgorithm):
    """
    Naive retraining baseline - retrain model from scratch without forget data
    """

    def __init__(self, **model_params):
        super().__init__(**model_params)
        self.model_params = model_params

    def get_name(self) -> str:
        return "naive_retraining"

    @timing_decorator
    def unlearn(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset] = None
    ) -> UnlearningResult:
        """
        Retrain model from scratch excluding forget data
        """
        self.validate_inputs(model, forget_data, retain_data)

        if retain_data is None:
            raise ValueError("Naive retraining requires retain_data")

        # Clone the original model
        unlearned_model = copy.deepcopy(model)

        # Retrain on retain data only
        start_time = Timer("Naive retraining")
        with start_time:
            unlearned_model.fit(retain_data.X, retain_data.y)

        # Calculate metrics
        metrics = {}
        if hasattr(model, "score"):
            try:
                metrics["retain_accuracy"] = unlearned_model.score(
                    retain_data.X, retain_data.y
                )
            except Exception as e:
                logger.warning(f"Could not calculate retain accuracy: {e}")

        return UnlearningResult(
            unlearned_model=unlearned_model,
            original_model=model,
            method=self.get_name(),
            metrics=metrics,
            execution_time=start_time.duration,
            hyperparameters=self.model_params,
            metadata={"retain_samples": retain_data.n_samples},
        )


class GradientAscentUnlearning(BaseUnlearningAlgorithm):
    """
    Gradient Ascent based unlearning for neural networks and differentiable models
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        n_epochs: int = 10,
        ascent_coefficient: float = 1.0,
        **kwargs,
    ):
        super().__init__(
            learning_rate=learning_rate,
            n_epochs=n_epochs,
            ascent_coefficient=ascent_coefficient,
            **kwargs,
        )
        self.learning_rate = learning_rate
        self.n_epochs = n_epochs
        self.ascent_coefficient = ascent_coefficient

    def get_name(self) -> str:
        return "gradient_ascent"

    @timing_decorator
    def unlearn(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset] = None
    ) -> UnlearningResult:
        """
        Apply gradient ascent on forget data while maintaining performance on retain data
        """
        self.validate_inputs(model, forget_data, retain_data)

        # This is a simplified implementation for sklearn-compatible models
        # For deep learning models, you'd need to implement actual gradient operations

        unlearned_model = copy.deepcopy(model)

        start_time = Timer("Gradient ascent unlearning")

        with start_time:
            if hasattr(unlearned_model, "partial_fit"):
                # For models that support partial_fit (like SGD-based models)
                for epoch in range(self.n_epochs):
                    # Negative learning on forget data (gradient ascent)
                    try:
                        # This is a heuristic approach for sklearn models
                        # In practice, you'd implement true gradient ascent
                        if retain_data is not None:
                            # Retrain with emphasis on retain data
                            sample_weight = np.ones(len(retain_data.y))
                            unlearned_model.partial_fit(
                                retain_data.X,
                                retain_data.y,
                                sample_weight=sample_weight,
                            )
                    except Exception as e:
                        logger.warning(f"Gradient ascent epoch {epoch} failed: {e}")
                        break
            else:
                # For models without partial_fit, use data manipulation
                if retain_data is not None:
                    # Retrain on retain data only (fallback to naive retraining)
                    unlearned_model.fit(retain_data.X, retain_data.y)
                else:
                    logger.warning(
                        "No retain data provided and model doesn't support partial_fit"
                    )

        # Calculate metrics
        metrics = self._calculate_metrics(unlearned_model, forget_data, retain_data)

        return UnlearningResult(
            unlearned_model=unlearned_model,
            original_model=model,
            method=self.get_name(),
            metrics=metrics,
            execution_time=start_time.duration,
            hyperparameters=self.hyperparameters,
            metadata={
                "forget_samples": forget_data.n_samples,
                "retain_samples": retain_data.n_samples if retain_data else 0,
            },
        )

    def _calculate_metrics(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset]
    ) -> Dict[str, float]:
        """Calculate unlearning-specific metrics"""
        metrics = {}

        try:
            # Forget quality (lower is better - model should perform poorly on forget data)
            forget_pred = model.predict(forget_data.X)
            forget_accuracy = accuracy_score(forget_data.y, forget_pred)
            metrics["forget_accuracy"] = forget_accuracy

            if retain_data is not None:
                # Retain quality (higher is better - model should maintain performance)
                retain_pred = model.predict(retain_data.X)
                retain_accuracy = accuracy_score(retain_data.y, retain_pred)
                metrics["retain_accuracy"] = retain_accuracy

                # Unlearning efficiency (balance between forgetting and retaining)
                metrics["unlearning_efficiency"] = retain_accuracy - forget_accuracy

        except Exception as e:
            logger.warning(f"Error calculating metrics: {e}")

        return metrics


class InfluenceFunctionUnlearning(BaseUnlearningAlgorithm):
    """
    Influence function based unlearning using first-order approximation
    """

    def __init__(self, damping: float = 0.01, scale: float = 25.0, **kwargs):
        super().__init__(damping=damping, scale=scale, **kwargs)
        self.damping = damping
        self.scale = scale

    def get_name(self) -> str:
        return "influence_function"

    @timing_decorator
    def unlearn(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset] = None
    ) -> UnlearningResult:
        """
        Use influence functions to approximate parameter changes
        """
        self.validate_inputs(model, forget_data, retain_data)

        # This is a simplified implementation
        # Full influence function implementation requires computing Hessian inverse

        unlearned_model = copy.deepcopy(model)

        start_time = Timer("Influence function unlearning")

        with start_time:
            # For sklearn models, we approximate by retraining without forget data
            # In practice, you'd implement the influence function computation
            if retain_data is not None:
                # Simple approximation: retrain on retain data
                unlearned_model.fit(retain_data.X, retain_data.y)
            else:
                logger.warning(
                    "Influence function unlearning requires retain data for sklearn models"
                )

        metrics = self._calculate_metrics(unlearned_model, forget_data, retain_data)

        return UnlearningResult(
            unlearned_model=unlearned_model,
            original_model=model,
            method=self.get_name(),
            metrics=metrics,
            execution_time=start_time.duration,
            hyperparameters=self.hyperparameters,
            metadata={"approximation": "first_order"},
        )

    def _calculate_metrics(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset]
    ) -> Dict[str, float]:
        """Calculate influence-based metrics"""
        metrics = {}

        try:
            if hasattr(model, "predict_proba"):
                # Use probability-based metrics for better sensitivity
                forget_proba = model.predict_proba(forget_data.X)
                metrics["forget_confidence"] = np.mean(np.max(forget_proba, axis=1))

                if retain_data is not None:
                    retain_proba = model.predict_proba(retain_data.X)
                    metrics["retain_confidence"] = np.mean(np.max(retain_proba, axis=1))
            else:
                # Fallback to accuracy
                forget_pred = model.predict(forget_data.X)
                metrics["forget_accuracy"] = accuracy_score(forget_data.y, forget_pred)

                if retain_data is not None:
                    retain_pred = model.predict(retain_data.X)
                    metrics["retain_accuracy"] = accuracy_score(
                        retain_data.y, retain_pred
                    )

        except Exception as e:
            logger.warning(f"Error calculating influence metrics: {e}")

        return metrics


class SISAUnlearning(BaseUnlearningAlgorithm):
    """
    SISA (Sharded, Isolated, Sliced, and Aggregated) unlearning
    """

    def __init__(self, n_shards: int = 5, aggregation_method: str = "voting", **kwargs):
        super().__init__(
            n_shards=n_shards, aggregation_method=aggregation_method, **kwargs
        )
        self.n_shards = n_shards
        self.aggregation_method = aggregation_method
        self.shard_models = []

    def get_name(self) -> str:
        return "sisa"

    @timing_decorator
    def unlearn(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset] = None
    ) -> UnlearningResult:
        """
        Implement SISA unlearning by sharding and retraining affected shards
        """
        self.validate_inputs(model, forget_data, retain_data)

        if retain_data is None:
            raise ValueError("SISA unlearning requires retain_data")

        start_time = Timer("SISA unlearning")

        with start_time:
            # Create data shards
            shard_size = len(retain_data.X) // self.n_shards
            self.shard_models = []

            for i in range(self.n_shards):
                start_idx = i * shard_size
                end_idx = (
                    (i + 1) * shard_size
                    if i < self.n_shards - 1
                    else len(retain_data.X)
                )

                # Create shard data
                shard_X = retain_data.X[start_idx:end_idx]
                shard_y = retain_data.y[start_idx:end_idx]

                # Train model on shard
                shard_model = copy.deepcopy(model)
                shard_model.fit(shard_X, shard_y)
                self.shard_models.append(shard_model)

        # Create ensemble model
        unlearned_model = SISAEnsemble(self.shard_models, self.aggregation_method)

        metrics = self._calculate_metrics(unlearned_model, forget_data, retain_data)

        return UnlearningResult(
            unlearned_model=unlearned_model,
            original_model=model,
            method=self.get_name(),
            metrics=metrics,
            execution_time=start_time.duration,
            hyperparameters=self.hyperparameters,
            metadata={
                "n_shards": self.n_shards,
                "shard_sizes": [len(retain_data.X) // self.n_shards] * self.n_shards,
            },
        )

    def _calculate_metrics(
        self, model: Any, forget_data: Dataset, retain_data: Optional[Dataset]
    ) -> Dict[str, float]:
        """Calculate SISA-specific metrics"""
        metrics = {}

        try:
            forget_pred = model.predict(forget_data.X)
            metrics["forget_accuracy"] = accuracy_score(forget_data.y, forget_pred)

            if retain_data is not None:
                retain_pred = model.predict(retain_data.X)
                metrics["retain_accuracy"] = accuracy_score(retain_data.y, retain_pred)

        except Exception as e:
            logger.warning(f"Error calculating SISA metrics: {e}")

        return metrics


class SISAEnsemble:
    """Ensemble model for SISA unlearning"""

    def __init__(self, models: List[Any], aggregation_method: str = "voting"):
        self.models = models
        self.aggregation_method = aggregation_method

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using ensemble of shard models"""
        predictions = np.array([model.predict(X) for model in self.models])

        if self.aggregation_method == "voting":
            # Majority voting
            return np.array(
                [np.bincount(predictions[:, i]).argmax() for i in range(X.shape[0])]
            )
        elif self.aggregation_method == "averaging":
            # For regression or probability averaging
            return np.mean(predictions, axis=0)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities using ensemble"""
        if hasattr(self.models[0], "predict_proba"):
            probabilities = np.array([model.predict_proba(X) for model in self.models])
            return np.mean(probabilities, axis=0)
        else:
            raise AttributeError("Base models don't support predict_proba")


class UnlearningAlgorithmFactory:
    """Factory class for creating unlearning algorithms"""

    _algorithms = {
        "naive_retraining": NaiveRetraining,
        "gradient_ascent": GradientAscentUnlearning,
        "influence_function": InfluenceFunctionUnlearning,
        "sisa": SISAUnlearning,
    }

    @classmethod
    def create_algorithm(cls, algorithm_name: str, **kwargs) -> BaseUnlearningAlgorithm:
        """Create an unlearning algorithm instance"""
        if algorithm_name not in cls._algorithms:
            available = ", ".join(cls._algorithms.keys())
            raise ValueError(
                f"Unknown algorithm '{algorithm_name}'. Available: {available}"
            )

        algorithm_class = cls._algorithms[algorithm_name]
        return algorithm_class(**kwargs)

    @classmethod
    def list_algorithms(cls) -> List[str]:
        """List all available algorithms"""
        return list(cls._algorithms.keys())

    @classmethod
    def register_algorithm(cls, name: str, algorithm_class: type) -> None:
        """Register a new algorithm"""
        if not issubclass(algorithm_class, BaseUnlearningAlgorithm):
            raise ValueError("Algorithm must inherit from BaseUnlearningAlgorithm")
        cls._algorithms[name] = algorithm_class


# Utility functions for easy access
def unlearn(
    model: Any,
    method: str,
    forget_data: Dataset,
    retain_data: Optional[Dataset] = None,
    **kwargs,
) -> UnlearningResult:
    """
    Convenience function to perform unlearning with specified method

    Args:
        model: Trained model to unlearn from
        method: Unlearning method name
        forget_data: Data to be forgotten
        retain_data: Data to be retained
        **kwargs: Additional parameters for the unlearning algorithm

    Returns:
        UnlearningResult object
    """
    algorithm = UnlearningAlgorithmFactory.create_algorithm(method, **kwargs)
    return algorithm.unlearn(model, forget_data, retain_data)


# Example usage and testing
'''
if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Create synthetic dataset
    X, y = make_classification(
        n_samples=1000, n_features=10, n_classes=3, random_state=42, n_informative=3
    )

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_retain, X_forget, y_retain, y_forget = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )

    # Create datasets
    forget_dataset = Dataset(X=X_forget, y=y_forget)
    retain_dataset = Dataset(X=X_retain, y=y_retain)

    # Train original model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    print("Original model accuracy:", model.score(X_test, y_test))

    # Test different unlearning methods
    methods = ["naive_retraining", "gradient_ascent", "sisa"]

    for method in methods:
        print(f"\nTesting {method}:")
        try:
            result = unlearn(model, method, forget_dataset, retain_dataset)
            test_accuracy = result.unlearned_model.predict(X_test)
            test_accuracy = accuracy_score(y_test, test_accuracy)

            print(f"  - Execution time: {result.execution_time:.4f}s")
            print(f"  - Test accuracy: {test_accuracy:.4f}")
            print(f"  - Metrics: {result.metrics}")

        except Exception as e:
            print(f"  - Error: {e}")

    # List all available algorithms
    print(f"\nAvailable algorithms: {UnlearningAlgorithmFactory.list_algorithms()}")
'''