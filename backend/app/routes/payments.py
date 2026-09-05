import random
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models import (
    PaymentRecord, SimulatePaymentRequest, AttemptRecoveryRequest,
    PaymentStatus, PaymentMethod, FailureCategory, RecoveryPriority
)
from database import db
from engine.risk_engine import RiskEngine
from engine.failure_diagnosis import FailureDiagnosisEngine
from engine.eligibility_engine import EligibilityEngine
from engine.recommendation_agent import RecoveryRecommendationAgent
from engine.recovery_executor import RecoveryExecutor

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.get("", response_model=List[PaymentRecord])
async def list_payments(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    return db.get_all(status=status, category=category, method=method, priority=priority)

@router.get("/{transaction_id}", response_model=PaymentRecord)
async def get_payment(transaction_id: str):
    payment = db.get_by_id(transaction_id)
    if not payment:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")
    return payment

@router.post("/simulate", response_model=PaymentRecord)
async def simulate_payment(req: SimulatePaymentRequest):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_id = f"TXN-{random.randint(9000, 9999)}"
    cust_id = req.customer_id if req.customer_id else f"CUST-{random.randint(100, 999)}"
    cust_name = f"Simulated Customer #{new_id[-4:]}"

    scenario_map = {
        "INSIGHT_FUNDS": "51",
        "EXPIRED_CARD": "54",
        "NETWORK_TIMEOUT": "91",
        "HIGH_FRAUD_RISK": "FRAUD_HIGH",
        "INVALID_ACCOUNT": "14",
        "SUCCESSFUL": "NONE"
    }
    f_code = scenario_map.get(req.scenario, "51")

    if req.scenario == "SUCCESSFUL":
        record = PaymentRecord(
            transaction_id=new_id,
            customer_id=cust_id,
            customer_name=cust_name,
            merchant_id="MERCHANT_RAZOR_01",
            amount=req.amount,
            payment_method=req.payment_method,
            payment_status=PaymentStatus.SUCCESSFUL,
            failure_reason=None,
            failure_code=None,
            failure_category=FailureCategory.NONE,
            transaction_timestamp=now_str,
            risk_score=8.5,
            risk_factors=["Clean Transaction Profile"],
            recovery_eligible=False,
            recommended_action="Payment Completed Successfully"
        )
    else:
        diag = FailureDiagnosisEngine.diagnose(f_code)
        risk_data = RiskEngine.assess_risk(req.amount, req.payment_method.value, f_code, 12, 0.90)
        elig_data = EligibilityEngine.evaluate(diag["category"], f_code, risk_data["risk_score"], 0, req.amount)

        status = PaymentStatus.RECOVERABLE if elig_data["eligible"] else (
            PaymentStatus.NON_RECOVERABLE if diag["category"] == FailureCategory.NON_RECOVERABLE else PaymentStatus.FAILED
        )

        record = PaymentRecord(
            transaction_id=new_id,
            customer_id=cust_id,
            customer_name=cust_name,
            merchant_id="MERCHANT_RAZOR_01",
            amount=req.amount,
            payment_method=req.payment_method,
            payment_status=status,
            failure_reason=diag["reason"],
            failure_code=f_code,
            failure_category=diag["category"],
            transaction_timestamp=now_str,
            risk_score=risk_data["risk_score"],
            risk_factors=risk_data["risk_factors"],
            recovery_eligible=elig_data["eligible"],
            recovery_priority=elig_data["priority"]
        )

        # Generate recommendation
        rec_data = RecoveryRecommendationAgent.recommend(record)
        record.recommended_action_type = rec_data["action_type"]
        record.recommended_action = rec_data["action"]
        record.confidence_score = rec_data["confidence"]
        record.estimated_recovery_value = rec_data["estimated_value"]
        record.action_explanation = rec_data["explanation"]

    db.add_payment(record)
    return record

@router.post("/{transaction_id}/assess-recovery")
async def assess_recovery(transaction_id: str):
    payment = db.get_by_id(transaction_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    diag = FailureDiagnosisEngine.diagnose(payment.failure_code or "91")
    risk = RiskEngine.assess_risk(payment.amount, payment.payment_method.value, payment.failure_code or "91", payment.customer_tenure_months, payment.previous_success_rate)
    elig = EligibilityEngine.evaluate(diag["category"], payment.failure_code or "91", risk["risk_score"], payment.retry_count, payment.amount)

    payment.failure_category = diag["category"]
    payment.risk_score = risk["risk_score"]
    payment.risk_factors = risk["risk_factors"]
    payment.recovery_eligible = elig["eligible"]
    payment.recovery_priority = elig["priority"]

    db.update_payment(payment)
    return {
        "transaction_id": payment.transaction_id,
        "diagnosis": diag,
        "risk_assessment": risk,
        "eligibility": elig
    }

@router.post("/{transaction_id}/recommend-action")
async def recommend_action(transaction_id: str):
    payment = db.get_by_id(transaction_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    rec_data = RecoveryRecommendationAgent.recommend(payment)
    payment.recommended_action_type = rec_data["action_type"]
    payment.recommended_action = rec_data["action"]
    payment.confidence_score = rec_data["confidence"]
    payment.estimated_recovery_value = rec_data["estimated_value"]
    payment.action_explanation = rec_data["explanation"]

    db.update_payment(payment)
    return rec_data

@router.post("/{transaction_id}/attempt-recovery")
async def attempt_recovery(transaction_id: str, req: Optional[AttemptRecoveryRequest] = None):
    payment = db.get_by_id(transaction_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    override = req.action_override if req else None
    result = RecoveryExecutor.execute_recovery(payment, action_override=override)
    return result
