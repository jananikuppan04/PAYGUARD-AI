import sys
from pathlib import Path

# Add backend and backend/app directories to sys.path
backend_dir = Path(__file__).resolve().parent.parent
app_dir = backend_dir / "app"
for p in [str(app_dir), str(backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from database import db
from models import PaymentStatus, FailureCategory, ActionType
from engine.failure_diagnosis import FailureDiagnosisEngine
from engine.eligibility_engine import EligibilityEngine
from engine.risk_engine import RiskEngine
from engine.recommendation_agent import RecoveryRecommendationAgent
from engine.recovery_executor import RecoveryExecutor
from engine.merchant_assistant import MerchantAssistantEngine
from engine.evaluator import EvaluationEngine

def test_database_population():
    payments = db.get_all()
    assert len(payments) >= 500, "Database should contain at least 500 records"
    analytics = db.get_analytics()
    assert analytics["total_attempts"] >= 500
    assert analytics["recovered_revenue"] >= 0

def test_failure_diagnosis():
    diag_51 = FailureDiagnosisEngine.diagnose("51")
    assert diag_51["category"] == FailureCategory.CUSTOMER_RELATED
    assert "Insufficient Funds" in diag_51["reason"]

    diag_91 = FailureDiagnosisEngine.diagnose("91")
    assert diag_91["category"] == FailureCategory.TECHNICAL

def test_eligibility_engine():
    elig_tech = EligibilityEngine.evaluate(FailureCategory.TECHNICAL, "91", 15.0, 0, 1500.0)
    assert elig_tech["eligible"] == True

    elig_fraud = EligibilityEngine.evaluate(FailureCategory.RISK_RELATED, "FRAUD_HIGH", 95.0, 0, 1500.0)
    assert elig_fraud["eligible"] == False

def test_recommendation_agent():
    payments = db.get_all(status="RECOVERABLE")
    if payments:
        p = payments[0]
        rec = RecoveryRecommendationAgent.recommend(p)
        assert rec["action_type"] in [ActionType.RETRY_DELAY, ActionType.SEND_REMINDER, ActionType.REQUEST_DETAILS, ActionType.SWITCH_METHOD]
        assert rec["explanation"] is not None
        assert len(rec["explanation"].evidence_points) > 0

def test_recovery_execution():
    payments = db.get_all(status="RECOVERABLE")
    if payments:
        target = payments[0]
        res = RecoveryExecutor.execute_recovery(target)
        assert res["transaction_id"] == target.transaction_id
        assert res["status"] in ["RECOVERED", "FAILED", "RECOVERABLE"]

def test_merchant_assistant():
    res1 = MerchantAssistantEngine.process_query("Which payments are recoverable?")
    assert "recoverable" in res1["answer"].lower()
    assert len(res1["evidence"]) > 0

    res2 = MerchantAssistantEngine.process_query("How much revenue was recovered this week?")
    assert "revenue" in res2["answer"].lower()

def test_evaluator():
    report = EvaluationEngine.get_evaluation_report()
    assert report["ml_evaluation"]["ml_recall"] >= 0.99
    assert report["ml_evaluation"]["ml_roc_auc"] >= 0.99
    assert report["ml_evaluation"]["ml_accuracy"] >= 0.95
    assert report["ml_evaluation"]["ml_precision"] > 0.10
    assert report["agent_evaluation"]["agent_groundedness_rate"] == 1.00

def test_risk_engine_lgbm():
    # Test normal payment
    low_risk = RiskEngine.assess_risk(
        amount=150.0,
        method="CARD",
        failure_code="51",
        past_success_rate=0.98,
        tenure=12
    )
    assert "risk_score" in low_risk
    assert "pretrained_lgbm_signal" in low_risk["shap_explanation"]
    assert "QuantumBankAI LightGBM" in low_risk["model_version"]

    # Test high fraud payment
    high_fraud = RiskEngine.assess_risk(
        amount=50000.0,
        method="TRANSFER",
        failure_code="FRAUD_HIGH",
        past_success_rate=0.1,
        tenure=0
    )
    assert high_fraud["risk_score"] >= 80
    assert high_fraud["risk_level"] == "CRITICAL"
