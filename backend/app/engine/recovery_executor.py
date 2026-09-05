import random
from datetime import datetime
from typing import Dict, Any
from models import PaymentRecord, PaymentStatus, ActionType
from database import db

class RecoveryExecutor:
    """Simulates bounded recovery execution upon merchant approval or automated trigger."""

    @staticmethod
    def execute_recovery(payment: PaymentRecord, action_override: ActionType = None) -> Dict[str, Any]:
        action_type = action_override if action_override else payment.recommended_action_type
        action_name = payment.recommended_action if not action_override else f"Manual Action ({action_override.value})"

        # Probability calculation based on confidence score & strategy
        base_success_prob = payment.confidence_score if payment.confidence_score > 0 else 0.65
        
        # Action override adjustment
        if action_override and action_override != payment.recommended_action_type:
            base_success_prob *= 0.85 # Slight penalty for overriding optimal AI recommendation

        # Simulate execution
        is_success = random.random() < base_success_prob
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payment.retry_count += 1
        payment.recovery_attempted = True

        history_entry = {
            "timestamp": now_str,
            "action_type": action_type.value if hasattr(action_type, "value") else str(action_type),
            "action_name": action_name,
            "outcome": "SUCCESS" if is_success else "FAILED",
            "recovered_amount": payment.amount if is_success else 0.0
        }
        payment.recovery_attempts_history.append(history_entry)

        if is_success:
            payment.payment_status = PaymentStatus.RECOVERED
            payment.recovery_successful = True
            payment.recovered_amount = payment.amount
            payment.recovery_timestamp = now_str
            payment.recovery_eligible = False
            msg = f"Recovery attempt SUCCESSFUL via strategy '{action_name}'. Recovered ₹{payment.amount:,.2f}."
        else:
            if payment.retry_count >= payment.max_retries:
                payment.payment_status = PaymentStatus.FAILED
                payment.recovery_eligible = False
                msg = f"Recovery attempt FAILED. Maximum retries ({payment.max_retries}) reached."
            else:
                msg = f"Recovery attempt FAILED. Retry {payment.retry_count}/{payment.max_retries} recorded."

        # Save to DB
        db.update_payment(payment)

        return {
            "transaction_id": payment.transaction_id,
            "success": is_success,
            "status": payment.payment_status.value,
            "action_taken": action_name,
            "recovered_amount": payment.recovered_amount,
            "timestamp": now_str,
            "message": msg
        }
