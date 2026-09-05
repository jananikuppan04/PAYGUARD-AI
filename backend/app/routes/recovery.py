from fastapi import APIRouter
from typing import List, Dict, Any, Optional
try:
    from app.models import PaymentRecord, AnalyticsSummary, PolicyConfig, BatchSummary, BatchRunRequest, AuditEntry
    from app.database import db
    from app.engine.batch_runner import BatchRecoveryRunner
    from app.engine.policy_engine import RecoveryPolicyEngine
except ImportError:
    from models import PaymentRecord, AnalyticsSummary, PolicyConfig, BatchSummary, BatchRunRequest, AuditEntry
    from database import db
    from engine.batch_runner import BatchRecoveryRunner
    from engine.policy_engine import RecoveryPolicyEngine

router = APIRouter(prefix="/api/v1/recovery", tags=["Recovery Agent"])

# Global Active Policy Config State
active_policy_config = PolicyConfig()

@router.get("/opportunities", response_model=List[PaymentRecord])
async def get_opportunities():
    all_opps = db.get_all(status="RECOVERABLE")
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
    all_opps.sort(key=lambda x: (priority_order.get(x.recovery_priority.value if hasattr(x.recovery_priority, 'value') else x.recovery_priority, 4), -x.estimated_recovery_value))
    return all_opps

@router.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics():
    return db.get_analytics()

@router.post("/batch/run", response_model=BatchSummary)
async def run_batch_recovery(req: BatchRunRequest):
    policy = req.policy_override or active_policy_config
    summary = BatchRecoveryRunner.run_batch_recovery(
        batch_size=req.batch_size,
        batch_type=req.batch_type,
        policy=policy
    )
    return summary

@router.get("/batch/summary", response_model=BatchSummary)
async def get_batch_summary():
    # Return batch summary for active dataset
    summary = BatchRecoveryRunner.run_batch_recovery(
        batch_size=500,
        batch_type="ALL",
        policy=active_policy_config
    )
    return summary

@router.get("/policy/config", response_model=PolicyConfig)
async def get_policy_config():
    return active_policy_config

@router.post("/policy/config", response_model=PolicyConfig)
async def update_policy_config(config: PolicyConfig):
    global active_policy_config
    active_policy_config = config
    return active_policy_config

@router.get("/audit-log", response_model=List[AuditEntry])
async def get_audit_log():
    summary = BatchRecoveryRunner.run_batch_recovery(
        batch_size=500,
        batch_type="ALL",
        policy=active_policy_config
    )
    return summary.audit_log
