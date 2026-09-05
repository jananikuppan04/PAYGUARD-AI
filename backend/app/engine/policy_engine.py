"""
PayGuard AI — Bounded Recovery Policy Engine & Guardrails
Enforces safety rules, maximum retry limits, transaction amount thresholds,
non-retryable decline codes, and policy-based escalations.
"""

from typing import Dict, Any, Tuple, Optional
try:
    from app.models import PaymentRecord, PolicyConfig, PaymentStatus
except ImportError:
    from models import PaymentRecord, PolicyConfig, PaymentStatus

class RecoveryPolicyEngine:
    """
    Evaluates payment records against active guardrail policies to produce
    bounded recovery decisions with clear stopping reasons.
    """
    
    @staticmethod
    def evaluate(record: PaymentRecord, policy: Optional[PolicyConfig] = None) -> Dict[str, Any]:
        if policy is None:
            policy = PolicyConfig()
            
        txn_id = record.transaction_id
        amount = record.amount
        code = record.failure_code or ""
        risk_score = record.risk_score
        retry_count = record.retry_count
        status = record.payment_status

        # Rule 1: Already Recovered Check
        if status == PaymentStatus.RECOVERED or record.recovery_successful:
            return {
                "approved": False,
                "escalated": False,
                "stopping_reason": "ALREADY_RECOVERED",
                "policy_applied": "Transaction has already been successfully recovered.",
                "eligibility_decision": "SETTLED"
            }

        # Rule 2: Permanently Non-Retryable Failure Code Check
        if code in policy.non_retryable_codes or not record.recovery_eligible:
            return {
                "approved": False,
                "escalated": False,
                "stopping_reason": "PERMANENTLY_INVALID",
                "policy_applied": f"Decline Code '{code}' is permanently non-retryable. Retrying would incur gateway penalty fees.",
                "eligibility_decision": "NON_RECOVERABLE"
            }

        # Rule 3: High Risk Fraud Escalation Threshold Check
        if risk_score >= policy.escalation_risk_threshold:
            return {
                "approved": False,
                "escalated": True,
                "stopping_reason": "FRAUD_ESCALATION",
                "policy_applied": f"Risk Score ({risk_score:.1f}/100) exceeds automation threshold (>{policy.escalation_risk_threshold:.1f}). Escalated for manual merchant review.",
                "eligibility_decision": "ESCALATED"
            }

        # Rule 4: Maximum Automated Transaction Amount Check
        if amount > policy.max_automated_amount:
            return {
                "approved": False,
                "escalated": True,
                "stopping_reason": "AMOUNT_EXCEEDED",
                "policy_applied": f"Transaction amount (₹{amount:,.2f}) exceeds maximum automated limit (₹{policy.max_automated_amount:,.2f}). Escalated for manual approval.",
                "eligibility_decision": "ESCALATED"
            }

        # Rule 5: Maximum Retry Limit Check
        if retry_count >= policy.max_retries_per_txn:
            return {
                "approved": False,
                "escalated": False,
                "stopping_reason": "RETRY_LIMIT_REACHED",
                "policy_applied": f"Reached maximum allowed recovery retries ({retry_count}/{policy.max_retries_per_txn}). Automated retries halted.",
                "eligibility_decision": "STOPPED"
            }

        # Rule 6: All Guardrails Passed -> Approved for Bounded Execution
        return {
            "approved": True,
            "escalated": False,
            "stopping_reason": None,
            "policy_applied": f"Policy checks passed. Retries ({retry_count}/{policy.max_retries_per_txn}), Amount (₹{amount:,.2f} <= ₹{policy.max_automated_amount:,.2f}), Risk ({risk_score:.1f} < {policy.escalation_risk_threshold:.1f}).",
            "eligibility_decision": "APPROVED"
        }
