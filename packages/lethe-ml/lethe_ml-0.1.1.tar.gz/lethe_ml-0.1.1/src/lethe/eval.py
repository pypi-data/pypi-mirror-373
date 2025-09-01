from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Union
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    matthews_corrcoef,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
import logging
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# Handle imports gracefully
try:
    from .tools.dataset import Dataset, UnlearningDataSplit
    from .algo import UnlearningResult
    from .utils.utils import Timer, timing_decorator
except ImportError:
    # Fallback for standalone execution
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))

    from tools.dataset import Dataset, UnlearningDataSplit
    from algo import UnlearningResult
    from utils.utils import timing_decorator

logger = logging.getLogger("lethe.evaluation")


class EvaluationMetrics(BaseModel):
    """Container for evaluation metrics"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Classification metrics
    accuracy: Optional[float] = Field(None, description="Classification accuracy")
    precision: Optional[float] = Field(None, description="Weighted precision")
    recall: Optional[float] = Field(None, description="Weighted recall")
    f1_score: Optional[float] = Field(None, description="Weighted F1 score")
    mcc: Optional[float] = Field(None, description="Matthews correlation coefficient")
    auc: Optional[float] = Field(None, description="Area under ROC curve")

    # Regression metrics
    mse: Optional[float] = Field(None, description="Mean squared error")
    mae: Optional[float] = Field(None, description="Mean absolute error")
    r2: Optional[float] = Field(None, description="R-squared score")

    # Unlearning-specific metrics
    forget_accuracy: Optional[float] = Field(None, description="Accuracy on forget set")
    retain_accuracy: Optional[float] = Field(None, description="Accuracy on retain set")
    unlearning_efficiency: Optional[float] = Field(
        None, description="Retain - Forget accuracy"
    )
    model_utility: Optional[float] = Field(None, description="Overall model utility")

    # Privacy metrics
    privacy_loss: Optional[float] = Field(None, description="Privacy loss estimate")
    membership_vulnerability: Optional[float] = Field(
        None, description="Membership inference vulnerability"
    )

    # Additional metrics
    additional_metrics: Dict[str, float] = Field(
        default_factory=dict, description="Custom metrics"
    )


class UnlearningEvaluationResult(BaseModel):
    """Comprehensive evaluation result for unlearning experiments"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_metrics: EvaluationMetrics = Field(
        ..., description="Original model metrics"
    )
    unlearned_metrics: EvaluationMetrics = Field(
        ..., description="Unlearned model metrics"
    )
    baseline_metrics: Optional[EvaluationMetrics] = Field(
        None, description="Baseline (retrained) metrics"
    )

    performance_degradation: Dict[str, float] = Field(
        default_factory=dict, description="Performance degradation"
    )
    unlearning_quality: float = Field(
        0.0, description="Overall unlearning quality score"
    )

    execution_time: float = Field(0.0, description="Total evaluation time")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class BaseEvaluator(ABC):
    """Base class for all evaluators"""

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def evaluate(self, model: Any, dataset: Dataset) -> EvaluationMetrics:
        """Evaluate a model on a dataset"""
        pass


class ClassificationEvaluator(BaseEvaluator):
    """Evaluator for classification tasks"""

    def __init__(self, use_probabilities: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.use_probabilities = use_probabilities

    def evaluate(self, model: Any, dataset: Dataset) -> EvaluationMetrics:
        """Evaluate classification model"""
        if not dataset.has_labels:
            raise ValueError("Classification evaluation requires labeled data")

        try:
            y_pred = model.predict(dataset.X)
            y_true = dataset.y

            # Basic metrics
            accuracy = accuracy_score(y_true, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_true, y_pred, average="weighted", zero_division=0
            )
            mcc = matthews_corrcoef(y_true, y_pred)

            metrics = EvaluationMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                mcc=mcc,
            )

            # AUC for binary/multiclass with probabilities
            if self.use_probabilities and hasattr(model, "predict_proba"):
                try:
                    y_proba = model.predict_proba(dataset.X)
                    if len(np.unique(y_true)) == 2:
                        # Binary classification
                        metrics.auc = roc_auc_score(y_true, y_proba[:, 1])
                    else:
                        # Multiclass
                        metrics.auc = roc_auc_score(y_true, y_proba, multi_class="ovr")
                except Exception as e:
                    logger.warning(f"Could not compute AUC: {e}")

            return metrics

        except Exception as e:
            logger.error(f"Classification evaluation failed: {e}")
            return EvaluationMetrics()


class RegressionEvaluator(BaseEvaluator):
    """Evaluator for regression tasks"""

    def evaluate(self, model: Any, dataset: Dataset) -> EvaluationMetrics:
        """Evaluate regression model"""
        if not dataset.has_labels:
            raise ValueError("Regression evaluation requires labeled data")

        try:
            y_pred = model.predict(dataset.X)
            y_true = dataset.y

            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)

            return EvaluationMetrics(mse=mse, mae=mae, r2=r2)

        except Exception as e:
            logger.error(f"Regression evaluation failed: {e}")
            return EvaluationMetrics()


class UnlearningEvaluator:
    """Comprehensive evaluator for machine unlearning experiments"""

    def __init__(self, task_type: str = "classification", **kwargs):
        self.task_type = task_type
        self.config = kwargs

        if task_type == "classification":
            self.base_evaluator = ClassificationEvaluator(**kwargs)
        elif task_type == "regression":
            self.base_evaluator = RegressionEvaluator(**kwargs)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    @timing_decorator
    def evaluate_unlearning(
        self,
        original_model: Any,
        unlearned_model: Any,
        data_split: UnlearningDataSplit,
        baseline_model: Optional[Any] = None,
    ) -> UnlearningEvaluationResult:
        """
        Comprehensive evaluation of unlearning experiment

        Args:
            original_model: Original trained model
            unlearned_model: Model after unlearning
            data_split: Data split containing train/forget/retain/test sets
            baseline_model: Optional baseline model (retrained from scratch)

        Returns:
            UnlearningEvaluationResult with comprehensive metrics
        """

        # Evaluate original model
        original_metrics = self._evaluate_model_comprehensive(
            original_model, data_split
        )

        # Evaluate unlearned model
        unlearned_metrics = self._evaluate_model_comprehensive(
            unlearned_model, data_split
        )

        # Evaluate baseline if provided
        baseline_metrics = None
        if baseline_model is not None:
            baseline_metrics = self._evaluate_model_comprehensive(
                baseline_model, data_split
            )

        # Calculate performance degradation
        degradation = self._calculate_degradation(original_metrics, unlearned_metrics)

        # Calculate unlearning quality score
        quality_score = self._calculate_unlearning_quality(
            original_metrics, unlearned_metrics, baseline_metrics
        )

        return UnlearningEvaluationResult(
            original_metrics=original_metrics,
            unlearned_metrics=unlearned_metrics,
            baseline_metrics=baseline_metrics,
            performance_degradation=degradation,
            unlearning_quality=quality_score,
            metadata={
                "task_type": self.task_type,
                "forget_size": data_split.forget.n_samples,
                "retain_size": data_split.retain.n_samples,
                "test_size": data_split.test.n_samples,
            },
        )

    def _evaluate_model_comprehensive(
        self, model: Any, data_split: UnlearningDataSplit
    ) -> EvaluationMetrics:
        """Evaluate model on all data splits"""

        # Base evaluation on test set
        test_metrics = self.base_evaluator.evaluate(model, data_split.test)

        # Unlearning-specific evaluations
        try:
            # Forget set evaluation (lower is better for unlearning)
            forget_pred = model.predict(data_split.forget.X)
            forget_accuracy = accuracy_score(data_split.forget.y, forget_pred)
            test_metrics.forget_accuracy = forget_accuracy

            # Retain set evaluation (higher is better)
            retain_pred = model.predict(data_split.retain.X)
            retain_accuracy = accuracy_score(data_split.retain.y, retain_pred)
            test_metrics.retain_accuracy = retain_accuracy

            # Unlearning efficiency
            test_metrics.unlearning_efficiency = retain_accuracy - forget_accuracy

            # Model utility (overall test performance)
            test_metrics.model_utility = test_metrics.accuracy or 0.0

        except Exception as e:
            logger.warning(f"Could not compute unlearning-specific metrics: {e}")

        return test_metrics

    def _calculate_degradation(
        self, original: EvaluationMetrics, unlearned: EvaluationMetrics
    ) -> Dict[str, float]:
        """Calculate performance degradation"""
        degradation = {}

        for metric_name in ["accuracy", "precision", "recall", "f1_score", "mcc", "r2"]:
            orig_val = getattr(original, metric_name)
            unlearn_val = getattr(unlearned, metric_name)

            if orig_val is not None and unlearn_val is not None and orig_val != 0:
                degradation[f"{metric_name}_degradation"] = (
                    (orig_val - unlearn_val) / orig_val * 100
                )

        return degradation

    def _calculate_unlearning_quality(
        self,
        original: EvaluationMetrics,
        unlearned: EvaluationMetrics,
        baseline: Optional[EvaluationMetrics] = None,
    ) -> float:
        """Calculate overall unlearning quality score (0-1)"""

        # Factors for quality calculation
        factors = []

        # Factor 1: Forget performance (lower forget accuracy is better)
        if unlearned.forget_accuracy is not None:
            forget_quality = max(0, 1.0 - unlearned.forget_accuracy)
            factors.append(forget_quality)

        # Factor 2: Retain performance (should maintain high accuracy)
        if unlearned.retain_accuracy is not None:
            retain_quality = unlearned.retain_accuracy
            factors.append(retain_quality)

        # Factor 3: Overall utility preservation
        if original.accuracy is not None and unlearned.accuracy is not None:
            utility_preservation = unlearned.accuracy / original.accuracy
            factors.append(utility_preservation)

        # Factor 4: Comparison with baseline (if available)
        if (
            baseline
            and baseline.accuracy is not None
            and unlearned.accuracy is not None
        ):
            baseline_comparison = min(1.0, unlearned.accuracy / baseline.accuracy)
            factors.append(baseline_comparison)

        # Calculate weighted average
        if factors:
            return sum(factors) / len(factors)
        else:
            return 0.0


class EvaluationReport:
    """Generate comprehensive evaluation reports"""

    @staticmethod
    def generate_text_report(result: UnlearningEvaluationResult) -> str:
        """Generate a text-based evaluation report"""

        lines = [
            "# Machine Unlearning Evaluation Report",
            "=" * 50,
            "",
            f"**Task Type**: {result.metadata.get('task_type', 'Unknown')}",
            f"**Forget Set Size**: {result.metadata.get('forget_size', 'Unknown')}",
            f"**Retain Set Size**: {result.metadata.get('retain_size', 'Unknown')}",
            f"**Test Set Size**: {result.metadata.get('test_size', 'Unknown')}",
            f"**Unlearning Quality Score**: {result.unlearning_quality:.4f}",
            "",
            "## Performance Metrics",
            "",
        ]

        # Original vs Unlearned comparison
        metrics = ["accuracy", "precision", "recall", "f1_score"]

        for metric in metrics:
            orig_val = getattr(result.original_metrics, metric)
            unlearn_val = getattr(result.unlearned_metrics, metric)

            if orig_val is not None and unlearn_val is not None:
                lines.extend(
                    [
                        f"**{metric.title()}**:",
                        f"  - Original: {orig_val:.4f}",
                        f"  - Unlearned: {unlearn_val:.4f}",
                        f"  - Degradation: {result.performance_degradation.get(f'{metric}_degradation', 0):.2f}%",
                        "",
                    ]
                )

        # Unlearning-specific metrics
        if result.unlearned_metrics.forget_accuracy is not None:
            lines.extend(
                [
                    "## Unlearning-Specific Metrics",
                    "",
                    f"**Forget Accuracy**: {result.unlearned_metrics.forget_accuracy:.4f} (lower is better)",
                    f"**Retain Accuracy**: {result.unlearned_metrics.retain_accuracy:.4f} (higher is better)",
                    f"**Unlearning Efficiency**: {result.unlearned_metrics.unlearning_efficiency:.4f}",
                    "",
                ]
            )

        return "\n".join(lines)

    @staticmethod
    def save_report(
        result: UnlearningEvaluationResult, filepath: Union[str, Path]
    ) -> None:
        """Save evaluation report to file"""
        report = EvaluationReport.generate_text_report(result)

        with open(filepath, "w") as f:
            f.write(report)

        logger.info(f"Evaluation report saved to {filepath}")


# Utility functions
def evaluate_unlearning_result(
    unlearning_result: UnlearningResult,
    data_split: UnlearningDataSplit,
    task_type: str = "classification",
) -> UnlearningEvaluationResult:
    """
    Convenience function to evaluate an UnlearningResult

    Args:
        unlearning_result: Result from unlearning algorithm
        data_split: Data split used for unlearning
        task_type: Type of ML task

    Returns:
        UnlearningEvaluationResult
    """
    evaluator = UnlearningEvaluator(task_type=task_type)

    return evaluator.evaluate_unlearning(
        original_model=unlearning_result.original_model,
        unlearned_model=unlearning_result.unlearned_model,
        data_split=data_split,
    )


# Example usage and testing
if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    # Create synthetic data
    X, y = make_classification(
        n_samples=1000, n_features=10, n_classes=3, n_informative=3, random_state=42
    )

    # Create data splits
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_retain, X_forget, y_retain, y_forget = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )

    # Create datasets
    from tools.dataset import Dataset, UnlearningDataSplitter

    full_dataset = Dataset(X=X, y=y)
    splitter = UnlearningDataSplitter()
    data_split = splitter.create_unlearning_split(
        full_dataset, forget_ratio=0.15, test_ratio=0.3
    )

    # Train models
    original_model = RandomForestClassifier(n_estimators=50, random_state=42)
    original_model.fit(data_split.train.X, data_split.train.y)

    unlearned_model = RandomForestClassifier(n_estimators=50, random_state=42)
    unlearned_model.fit(data_split.retain.X, data_split.retain.y)  # Naive retraining

    # Evaluate
    evaluator = UnlearningEvaluator(task_type="classification")
    result = evaluator.evaluate_unlearning(
        original_model=original_model,
        unlearned_model=unlearned_model,
        data_split=data_split,
    )

    # Generate report
    report = EvaluationReport.generate_text_report(result)
    print(report)

    print(f"\nUnlearning Quality Score: {result.unlearning_quality:.4f}")
    print(f"Execution Time: {result.execution_time:.4f}s")
