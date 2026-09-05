from typing import Dict, Any
from models import FailureCategory, RecoveryPriority

class EligibilityEngine:
    """Evaluates whether a failed payment is eligible for recovery and assigns priority."""

    @staticmethod
    def evaluate(failure_category: FailureCategory, failure_code: str, risk_score: float, retry_count: int, amount: float) -> Dict[str, Any]:
        if failure_category == FailureCategory.NON_RECOVERABLE:
            return {
                "eligible": False,
                "priority": RecoveryPriority.NONE,
                "reason": "Permanently invalid payment instrument (Decline Code 14). Retrying is prohibited."
            }

        if failure_code == "FRAUD_HIGH" or risk_score >= 80.0:
            return {
                "eligible": False,
                "priority": RecoveryPriority.NONE,
                "reason": "High fraud risk score (>80/100) or stolen card anomaly. Automated recovery blocked."
            }

        if retry_count >= 3:
            return {
                "eligible": False,
                "priority": RecoveryPriority.NONE,
                "reason": "Maximum retry limit (3 retries) reached for this transaction. Escalate to manual merchant workflow."
            }

        # Calculate Priority
        if failure_category == FailureCategory.TECHNICAL:
            priority = RecoveryPriority.HIGH if amount >= 1000 else RecoveryPriority.MEDIUM
        elif failure_category == FailureCategory.CUSTOMER_RELATED:
            priority = RecoveryPriority.HIGH if amount >= 2500 else RecoveryPriority.MEDIUM
        else:
            priority = RecoveryPriority.LOW

        return {
            "eligible": True,
            "priority": priority,
            "reason": f"Payment is recoverable under category '{failure_category.value}'. Risk score is acceptable ({risk_score}/100)."
        }
