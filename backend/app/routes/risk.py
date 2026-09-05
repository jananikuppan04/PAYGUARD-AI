from fastapi import APIRouter, HTTPException
from database import db
from engine.risk_engine import RiskEngine

router = APIRouter(prefix="/api/v1/risk", tags=["Risk"])

@router.get("/summary")
async def risk_summary():
    all_payments = db.get_all()
    total = len(all_payments)
    high_risk = sum(1 for p in all_payments if p.risk_score >= 75)
    med_risk = sum(1 for p in all_payments if 25 <= p.risk_score < 75)
    low_risk = sum(1 for p in all_payments if p.risk_score < 25)

    return {
        "total_assessed": total,
        "high_risk_count": high_risk,
        "medium_risk_count": med_risk,
        "low_risk_count": low_risk,
        "avg_risk_score": round(sum(p.risk_score for p in all_payments) / total, 1) if total > 0 else 0.0,
        "risk_distribution": {
            "CRITICAL (>80)": sum(1 for p in all_payments if p.risk_score >= 80),
            "HIGH (50-79)": sum(1 for p in all_payments if 50 <= p.risk_score < 80),
            "MEDIUM (25-49)": sum(1 for p in all_payments if 25 <= p.risk_score < 50),
            "LOW (<25)": low_risk
        }
    }

@router.get("/explain/{transaction_id}")
async def explain_risk(transaction_id: str):
    payment = db.get_by_id(transaction_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    risk_info = RiskEngine.assess_risk(
        payment.amount,
        payment.payment_method.value,
        payment.failure_code or "91",
        payment.customer_tenure_months,
        payment.previous_success_rate
    )

    return {
        "transaction_id": payment.transaction_id,
        "amount": payment.amount,
        "method": payment.payment_method.value,
        "failure_code": payment.failure_code,
        "risk_assessment": risk_info
    }
