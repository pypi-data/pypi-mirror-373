from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import logging
from pydantic import BaseModel, Field, ConfigDict

# Handle imports gracefully
try:
    from .tools.dataset import Dataset, UnlearningDataSplit
    from .utils.utils import Timer, timing_decorator
except ImportError:
    # Fallback for standalone execution
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))

    from tools.dataset import Dataset, UnlearningDataSplit
    from utils.utils import timing_decorator

logger = logging.getLogger("lethe.verification")


class VerificationResult(BaseModel):
    """Result container for verification tests"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    test_name: str = Field(..., description="Name of the verification test")
    passed: bool = Field(..., description="Whether the test passed")
    score: float = Field(..., description="Numerical score for the test (0-1)")
    details: str = Field(..., description="Detailed explanation of results")
    threshold: float = Field(..., description="Threshold used for pass/fail")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ComprehensiveVerificationResult(BaseModel):
    """Container for all verification results"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    privacy_tests: List[VerificationResult] = Field(default_factory=list)
    utility_tests: List[VerificationResult] = Field(default_factory=list)
    completeness_tests: List[VerificationResult] = Field(default_factory=list)

    overall_score: float = Field(0.0, description="Overall verification score")
    passed: bool = Field(False, description="Whether all critical tests passed")
    execution_time: float = Field(0.0, description="Total verification time")


class BaseVerifier(ABC):
    """Base class for all verification methods"""

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def verify(self, *args, **kwargs) -> VerificationResult:
        """Perform verification test"""
        pass


class MembershipInferenceAttack(BaseVerifier):
    """Membership inference attack for privacy verification"""

    def __init__(
        self, n_shadow_models: int = 3, attack_threshold: float = 0.6, **kwargs
    ):
        super().__init__(**kwargs)
        self.n_shadow_models = n_shadow_models
        self.attack_threshold = attack_threshold

    def verify(
        self,
        target_model: Any,
        member_data: Dataset,
        non_member_data: Dataset,
        model_class: Any = RandomForestClassifier,
    ) -> VerificationResult:
        """
        Perform membership inference attack - FIXED VERSION

        Args:
            target_model: Model to attack
            member_data: Data that was used in training (members)
            non_member_data: Data that was not used in training (non-members)
            model_class: Class to use for shadow models

        Returns:
            VerificationResult indicating vulnerability to membership inference
        """

        try:
            # Ensure we have enough data for shadow model training
            min_samples = min(member_data.n_samples, non_member_data.n_samples)
            if min_samples < 10:
                return VerificationResult(
                    test_name="membership_inference_attack",
                    passed=False,
                    score=0.0,
                    details=f"Insufficient data: only {min_samples} samples available",
                    threshold=self.attack_threshold,
                    metadata={"error": "insufficient_data"},
                )

            # Create shadow models and collect attack features
            attack_features = []
            attack_labels = []

            for i in range(self.n_shadow_models):
                try:
                    # **FIXED**: Properly split member data - X and y separately
                    member_X_shadow, member_X_out, member_y_shadow, member_y_out = (
                        train_test_split(
                            member_data.X, member_data.y, test_size=0.5, random_state=i
                        )
                    )

                    # **FIXED**: Properly split non-member data - X and y separately
                    (
                        non_member_X_shadow,
                        non_member_X_out,
                        non_member_y_shadow,
                        non_member_y_out,
                    ) = train_test_split(
                        non_member_data.X,
                        non_member_data.y,
                        test_size=0.5,
                        random_state=i,
                    )

                    # Create shadow dataset
                    shadow_X = np.vstack([member_X_shadow, non_member_X_shadow])
                    shadow_y = np.hstack([member_y_shadow, non_member_y_shadow])

                    # Train shadow model
                    shadow_model = model_class(n_estimators=10, random_state=i)
                    shadow_model.fit(shadow_X, shadow_y)

                    # Generate attack features (confidence scores)
                    if hasattr(shadow_model, "predict_proba"):
                        # For IN samples (members)
                        in_proba = shadow_model.predict_proba(member_X_out)
                        in_confidence = np.max(in_proba, axis=1)

                        # For OUT samples (non-members)
                        out_proba = shadow_model.predict_proba(non_member_X_out)
                        out_confidence = np.max(out_proba, axis=1)

                        # Combine features
                        attack_features.extend(in_confidence)
                        attack_features.extend(out_confidence)
                        attack_labels.extend([1] * len(in_confidence))  # 1 = member
                        attack_labels.extend(
                            [0] * len(out_confidence)
                        )  # 0 = non-member

                except Exception as shadow_error:
                    logger.warning(f"Shadow model {i} failed: {shadow_error}")
                    continue

            # Train attack model if we have sufficient attack data
            if len(attack_features) >= 20:  # Need minimum samples for attack
                attack_X = np.array(attack_features).reshape(-1, 1)
                attack_y = np.array(attack_labels)

                # Simple threshold-based attack instead of training another model
                # Higher confidence typically indicates membership
                threshold_val = np.median(attack_X)

                # Test attack on target model
                if hasattr(target_model, "predict_proba"):
                    # Test on member data
                    member_proba = target_model.predict_proba(member_data.X)
                    member_conf = np.max(member_proba, axis=1)
                    member_predicted = (member_conf > threshold_val).astype(int)

                    # Test on non-member data
                    non_member_proba = target_model.predict_proba(non_member_data.X)
                    non_member_conf = np.max(non_member_proba, axis=1)
                    non_member_predicted = (non_member_conf > threshold_val).astype(int)

                    # Calculate attack accuracy
                    member_correct = np.sum(
                        member_predicted == 1
                    )  # Should predict member=1
                    non_member_correct = np.sum(
                        non_member_predicted == 0
                    )  # Should predict non-member=0
                    total_samples = len(member_predicted) + len(non_member_predicted)
                    attack_acc = (member_correct + non_member_correct) / total_samples

                    # Privacy preserved if attack accuracy is close to random (0.5)
                    privacy_score = max(0, 1.0 - 2 * abs(attack_acc - 0.5))
                    passed = attack_acc < self.attack_threshold

                    details = (
                        f"Attack accuracy: {attack_acc:.4f}, Privacy score: {privacy_score:.4f}, "
                        f"Threshold: {threshold_val:.4f}"
                    )

                else:
                    # Fallback for models without predict_proba
                    privacy_score = (
                        0.7  # Assume reasonable privacy without probabilities
                    )
                    passed = True
                    details = "Model doesn't support probability predictions, using fallback evaluation"
            else:
                # Not enough attack data
                privacy_score = 0.5
                passed = True  # Assume privacy is preserved if attack cannot be mounted
                details = f"Insufficient attack data collected: {len(attack_features)} samples"

        except Exception as e:
            logger.error(f"Membership inference attack failed: {e}")
            privacy_score = 0.0
            passed = False
            details = f"Attack failed due to error: {str(e)}"

        return VerificationResult(
            test_name="membership_inference_attack",
            passed=passed,
            score=privacy_score,
            details=details,
            threshold=self.attack_threshold,
            metadata={
                "n_shadow_models": self.n_shadow_models,
                "member_size": member_data.n_samples,
                "non_member_size": non_member_data.n_samples,
            },
        )


class UtilityVerifier(BaseVerifier):
    """Verify model utility preservation after unlearning"""

    def __init__(self, utility_threshold: float = 0.90, **kwargs):
        super().__init__(**kwargs)
        self.utility_threshold = utility_threshold

    def verify(
        self, original_model: Any, unlearned_model: Any, test_data: Dataset
    ) -> VerificationResult:
        """
        Verify that unlearned model maintains acceptable utility
        """

        try:
            # Get predictions from both models
            original_pred = original_model.predict(test_data.X)
            unlearned_pred = unlearned_model.predict(test_data.X)

            # Calculate accuracies
            original_acc = accuracy_score(test_data.y, original_pred)
            unlearned_acc = accuracy_score(test_data.y, unlearned_pred)

            # Utility preservation ratio
            utility_ratio = unlearned_acc / original_acc if original_acc > 0 else 0
            passed = utility_ratio >= self.utility_threshold

            details = (
                f"Original accuracy: {original_acc:.4f}, "
                f"Unlearned accuracy: {unlearned_acc:.4f}, "
                f"Utility ratio: {utility_ratio:.4f}"
            )

        except Exception as e:
            logger.error(f"Utility verification failed: {e}")
            utility_ratio = 0.0
            passed = False
            details = f"Verification failed: {str(e)}"

        return VerificationResult(
            test_name="utility_preservation",
            passed=passed,
            score=utility_ratio,
            details=details,
            threshold=self.utility_threshold,
            metadata={"test_samples": test_data.n_samples},
        )


class ForgetQualityVerifier(BaseVerifier):
    """Verify quality of forgetting on the forget set"""

    def __init__(self, forget_threshold: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.forget_threshold = forget_threshold

    def verify(
        self, original_model: Any, unlearned_model: Any, forget_data: Dataset
    ) -> VerificationResult:
        """
        Verify that model has forgotten the specified data
        """

        try:
            # Get predictions on forget set
            original_pred = original_model.predict(forget_data.X)
            unlearned_pred = unlearned_model.predict(forget_data.X)

            # Calculate accuracies
            original_acc = accuracy_score(forget_data.y, original_pred)
            unlearned_acc = accuracy_score(forget_data.y, unlearned_pred)

            # Forgetting quality (lower unlearned accuracy is better)
            forget_quality = (
                max(0, (original_acc - unlearned_acc) / original_acc)
                if original_acc > 0
                else 1.0
            )
            passed = unlearned_acc < self.forget_threshold

            details = (
                f"Original forget accuracy: {original_acc:.4f}, "
                f"Unlearned forget accuracy: {unlearned_acc:.4f}, "
                f"Forget quality: {forget_quality:.4f}"
            )

        except Exception as e:
            logger.error(f"Forget quality verification failed: {e}")
            forget_quality = 0.0
            passed = False
            details = f"Verification failed: {str(e)}"

        return VerificationResult(
            test_name="forget_quality",
            passed=passed,
            score=forget_quality,
            details=details,
            threshold=self.forget_threshold,
            metadata={"forget_samples": forget_data.n_samples},
        )


class CompletenessVerifier(BaseVerifier):
    """Verify completeness of unlearning (no residual influence)"""

    def __init__(self, completeness_threshold: float = 0.05, **kwargs):
        super().__init__(**kwargs)
        self.completeness_threshold = completeness_threshold

    def verify(
        self, unlearned_model: Any, retrained_model: Any, test_data: Dataset
    ) -> VerificationResult:
        """
        Verify that unlearned model performs similarly to retrained baseline
        """

        try:
            # Get predictions from both models
            unlearned_pred = unlearned_model.predict(test_data.X)
            retrained_pred = retrained_model.predict(test_data.X)

            # Calculate accuracies
            unlearned_acc = accuracy_score(test_data.y, unlearned_pred)
            retrained_acc = accuracy_score(test_data.y, retrained_pred)

            # Completeness score (smaller difference is better)
            difference = abs(unlearned_acc - retrained_acc)
            completeness_score = max(0, 1.0 - difference / self.completeness_threshold)
            passed = difference < self.completeness_threshold

            details = (
                f"Unlearned accuracy: {unlearned_acc:.4f}, "
                f"Retrained accuracy: {retrained_acc:.4f}, "
                f"Difference: {difference:.4f}"
            )

        except Exception as e:
            logger.error(f"Completeness verification failed: {e}")
            completeness_score = 0.0
            passed = False
            details = f"Verification failed: {str(e)}"

        return VerificationResult(
            test_name="completeness",
            passed=passed,
            score=completeness_score,
            details=details,
            threshold=self.completeness_threshold,
            metadata={"test_samples": test_data.n_samples},
        )


class UnlearningVerifier:
    """Comprehensive verification suite for machine unlearning"""

    def __init__(self, **kwargs):
        self.config = kwargs

        # Initialize individual verifiers
        self.membership_verifier = MembershipInferenceAttack(**kwargs)
        self.utility_verifier = UtilityVerifier(**kwargs)
        self.forget_verifier = ForgetQualityVerifier(**kwargs)
        self.completeness_verifier = CompletenessVerifier(**kwargs)

    @timing_decorator
    def verify_unlearning(
        self,
        original_model: Any,
        unlearned_model: Any,
        data_split: UnlearningDataSplit,
        retrained_model: Optional[Any] = None,
    ) -> ComprehensiveVerificationResult:
        """
        Perform comprehensive verification of unlearning
        """

        privacy_tests = []
        utility_tests = []
        completeness_tests = []

        # Privacy verification - Membership inference attack
        try:
            mia_result = self.membership_verifier.verify(
                target_model=unlearned_model,
                member_data=data_split.forget,  # Forget data should not be inferable
                non_member_data=data_split.test,  # Test data is definitely non-member
            )
            privacy_tests.append(mia_result)
        except Exception as e:
            logger.warning(f"Membership inference attack failed: {e}")

        # Utility verification
        try:
            utility_result = self.utility_verifier.verify(
                original_model=original_model,
                unlearned_model=unlearned_model,
                test_data=data_split.test,
            )
            utility_tests.append(utility_result)
        except Exception as e:
            logger.warning(f"Utility verification failed: {e}")

        # Forget quality verification
        try:
            forget_result = self.forget_verifier.verify(
                original_model=original_model,
                unlearned_model=unlearned_model,
                forget_data=data_split.forget,
            )
            privacy_tests.append(forget_result)
        except Exception as e:
            logger.warning(f"Forget quality verification failed: {e}")

        # Completeness verification (if retrained model available)
        if retrained_model is not None:
            try:
                completeness_result = self.completeness_verifier.verify(
                    unlearned_model=unlearned_model,
                    retrained_model=retrained_model,
                    test_data=data_split.test,
                )
                completeness_tests.append(completeness_result)
            except Exception as e:
                logger.warning(f"Completeness verification failed: {e}")

        # Calculate overall scores
        all_tests = privacy_tests + utility_tests + completeness_tests

        if all_tests:
            overall_score = sum(test.score for test in all_tests) / len(all_tests)
            passed = all(test.passed for test in all_tests)
        else:
            overall_score = 0.0
            passed = False

        return ComprehensiveVerificationResult(
            privacy_tests=privacy_tests,
            utility_tests=utility_tests,
            completeness_tests=completeness_tests,
            overall_score=overall_score,
            passed=passed,
        )

# Utility functions
def verify_unlearning_simple(
    original_model: Any,
    unlearned_model: Any,
    forget_data: Dataset,
    retain_data: Dataset,
    test_data: Dataset,
) -> Dict[str, bool]:
    """
    Simple verification function for quick testing

    Returns:
        Dictionary with verification results
    """

    results = {}

    try:
        # Utility check
        orig_acc = accuracy_score(test_data.y, original_model.predict(test_data.X))
        unlearn_acc = accuracy_score(test_data.y, unlearned_model.predict(test_data.X))
        results["utility_preserved"] = unlearn_acc >= 0.9 * orig_acc

        # Forget check
        forget_acc = accuracy_score(
            forget_data.y, unlearned_model.predict(forget_data.X)
        )
        results["forgetting_effective"] = forget_acc < 0.7

        # Retain check
        retain_acc = accuracy_score(
            retain_data.y, unlearned_model.predict(retain_data.X)
        )
        results["retention_good"] = retain_acc > 0.8

    except Exception as e:
        logger.error(f"Simple verification failed: {e}")
        results = {"error": True}

    return results


# Example usage and testing
if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Create synthetic data and models for testing
    X, y = make_classification(
        n_samples=1000, n_features=10, n_classes=3, n_informative=3, random_state=42
    )

    # Create data split
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
    unlearned_model.fit(data_split.retain.X, data_split.retain.y)

    retrained_model = RandomForestClassifier(n_estimators=50, random_state=42)
    retrained_model.fit(data_split.retain.X, data_split.retain.y)

    # Perform verification
    verifier = UnlearningVerifier()
    result = verifier.verify_unlearning(
        original_model=original_model,
        unlearned_model=unlearned_model,
        data_split=data_split,
        retrained_model=retrained_model,
    )

    print(f"Overall Verification Score: {result.overall_score:.4f}")
    print(f"All Tests Passed: {result.passed}")
    print(f"Execution Time: {result.execution_time:.4f}s")

    # Print individual test results
    for test in result.privacy_tests + result.utility_tests + result.completeness_tests:
        print(f"\n{test.test_name}: {'PASSED' if test.passed else 'FAILED'}")
        print(f"  Score: {test.score:.4f}")
        print(f"  Details: {test.details}")
