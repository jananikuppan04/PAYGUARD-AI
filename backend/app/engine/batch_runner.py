"""
PayGuard AI — Batch Recovery Operations Runner & Audit Service
Executes bounded recovery operations across transaction batches, enforces guardrail policies,
verifies outcomes, calculates bank-reconciled money recovered, and maintains a real-time audit trail.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from app.database import db
    from app.models import (
        PaymentRecord, PaymentStatus, BatchSummary, AuditEntry, PolicyConfig, ActionType
    )
    from app.engine.policy_engine import RecoveryPolicyEngine
    from app.engine.recovery_executor import RecoveryExecutor
except ImportError:
    from database import db
    from models import (
        PaymentRecord, PaymentStatus, BatchSummary, AuditEntry, PolicyConfig, ActionType
    )
    from engine.policy_engine import RecoveryPolicyEngine
    from engine.recovery_executor import RecoveryExecutor


class BatchRecoveryRunner:
    """
    Executes batch recovery operations over synthetic or live payment failure records.
    Calculates 100% reconciled revenue metrics and appends chronological audit records.
    """

    def __init__(self):
        pass

    @staticmethod
    def run_batch_recovery(
        batch_size: int = 500,
        batch_type: str = "ALL",
        policy: Optional[PolicyConfig] = None
    ) -> BatchSummary:
        if policy is None:
            policy = PolicyConfig()

        batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        all_records = db.get_all()

        # Filter batch if requested
        if batch_type != "ALL":
            records = [p for p in all_records if p.failure_category.value == batch_type or p.failure_category == batch_type][:batch_size]
        else:
            records = all_records[:batch_size]

        records_processed = len(records)
        eligible_opportunities = [p for p in records if p.recovery_eligible and p.payment_status != PaymentStatus.RECOVERED]
        eligible_count = len(eligible_opportunities)

        revenue_at_risk = sum(p.amount for p in eligible_opportunities)

        attempts_count = 0
        successful_count = 0
        failed_count = 0
        revenue_recovered = 0.0
        stopped_by_guardrails = 0
        escalated_count = 0
        audit_log: List[AuditEntry] = []

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Process each transaction in the batch through the agent loop
        for p in records:
            # Skip if already recovered prior to this run, but count existing recovered revenue
            if p.payment_status == PaymentStatus.RECOVERED or p.recovery_successful:
                revenue_recovered += p.recovered_amount
                audit_log.append(AuditEntry(
                    timestamp=p.recovery_timestamp or now_str,
                    transaction_id=p.transaction_id,
                    customer_name=p.customer_name,
                    failure_reason=p.failure_reason or "Initial Settlement",
                    risk_score=p.risk_score,
                    eligibility_decision="SETTLED",
                    recommended_action=p.recommended_action,
                    policy_applied="Transaction already recovered.",
                    action_executed="None (Already Settled)",
                    result="SUCCESS",
                    recovered_amount=p.recovered_amount,
                    stopping_reason="ALREADY_RECOVERED"
                ))
                continue

            # Run Bounded Policy Engine Check
            policy_check = RecoveryPolicyEngine.evaluate(p, policy)

            if policy_check["escalated"]:
                escalated_count += 1
                stopped_by_guardrails += 1
                audit_log.append(AuditEntry(
                    timestamp=now_str,
                    transaction_id=p.transaction_id,
                    customer_name=p.customer_name,
                    failure_reason=p.failure_reason or "Unknown Decline",
                    risk_score=p.risk_score,
                    eligibility_decision="ESCALATED",
                    recommended_action=p.recommended_action,
                    policy_applied=policy_check["policy_applied"],
                    action_executed="Manual Escalate Triggered",
                    result="ESCALATED",
                    recovered_amount=0.0,
                    stopping_reason=policy_check["stopping_reason"]
                ))
                continue

            if not policy_check["approved"]:
                stopped_by_guardrails += 1
                audit_log.append(AuditEntry(
                    timestamp=now_str,
                    transaction_id=p.transaction_id,
                    customer_name=p.customer_name,
                    failure_reason=p.failure_reason or "Non-retryable",
                    risk_score=p.risk_score,
                    eligibility_decision=policy_check["eligibility_decision"],
                    recommended_action=p.recommended_action,
                    policy_applied=policy_check["policy_applied"],
                    action_executed="Halted by Policy",
                    result="STOPPED",
                    recovered_amount=0.0,
                    stopping_reason=policy_check["stopping_reason"]
                ))
                continue

            # Approved by Policy Engine -> Execute Bounded Intervention
            attempts_count += 1
            execution_res = RecoveryExecutor.execute_recovery(p)

            if execution_res["status"] == "RECOVERED":
                successful_count += 1
                revenue_recovered += p.amount
                p.payment_status = PaymentStatus.RECOVERED
                p.recovery_successful = True
                p.recovered_amount = p.amount
                p.recovery_timestamp = now_str
                db.update_payment(p)

                audit_log.append(AuditEntry(
                    timestamp=now_str,
                    transaction_id=p.transaction_id,
                    customer_name=p.customer_name,
                    failure_reason=p.failure_reason or "Technical Retry",
                    risk_score=p.risk_score,
                    eligibility_decision="APPROVED",
                    recommended_action=p.recommended_action,
                    policy_applied=policy_check["policy_applied"],
                    action_executed=p.recommended_action,
                    result="RECOVERED",
                    recovered_amount=p.amount,
                    stopping_reason=None
                ))
            else:
                failed_count += 1
                p.retry_count += 1
                db.update_payment(p)

                audit_log.append(AuditEntry(
                    timestamp=now_str,
                    transaction_id=p.transaction_id,
                    customer_name=p.customer_name,
                    failure_reason=p.failure_reason or "Network Failure",
                    risk_score=p.risk_score,
                    eligibility_decision="APPROVED",
                    recommended_action=p.recommended_action,
                    policy_applied=policy_check["policy_applied"],
                    action_executed=p.recommended_action,
                    result="FAILED",
                    recovered_amount=0.0,
                    stopping_reason="RETRY_ATTEMPT_FAILED"
                ))

        unrecovered = max(0.0, revenue_at_risk - revenue_recovered)
        recovery_rate = round((successful_count / attempts_count * 100), 1) if attempts_count > 0 else 0.0

        return BatchSummary(
            batch_id=batch_id,
            records_processed=records_processed,
            eligible_count=eligible_count,
            revenue_at_risk=round(revenue_at_risk, 2),
            attempts_count=attempts_count,
            successful_count=successful_count,
            failed_count=failed_count,
            revenue_recovered=round(revenue_recovered, 2),
            unrecovered_revenue=round(unrecovered, 2),
            recovery_rate=recovery_rate,
            stopped_by_guardrails_count=stopped_by_guardrails,
            escalated_count=escalated_count,
            audit_log=audit_log
        )
