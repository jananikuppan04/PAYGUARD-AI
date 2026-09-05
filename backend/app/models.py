from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class PaymentMethod(str, Enum):
    CARD = "CARD"
    UPI = "UPI"
    NETBANKING = "NETBANKING"
    WALLET = "WALLET"

class PaymentStatus(str, Enum):
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RECOVERABLE = "RECOVERABLE"
    NON_RECOVERABLE = "NON_RECOVERABLE"
    RECOVERED = "RECOVERED"

class FailureCategory(str, Enum):
    TECHNICAL = "TECHNICAL"
    CUSTOMER_RELATED = "CUSTOMER_RELATED"
    RISK_RELATED = "RISK_RELATED"
    NON_RECOVERABLE = "NON_RECOVERABLE"
    NONE = "NONE"

class RecoveryPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class ActionType(str, Enum):
    RETRY_DELAY = "RETRY_DELAY"
    SWITCH_METHOD = "SWITCH_METHOD"
    REQUEST_DETAILS = "REQUEST_DETAILS"
    SEND_REMINDER = "SEND_REMINDER"
    ESCALATE_MERCHANT = "ESCALATE_MERCHANT"
    DO_NOT_RETRY = "DO_NOT_RETRY"

class ActionExplanation(BaseModel):
    why_failed: str
    eligibility_rationale: str
    action_rationale: str
    evidence_points: List[str]
    target_metric: str

class PaymentRecord(BaseModel):
    transaction_id: str
    customer_id: str
    customer_name: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    failure_category: FailureCategory = FailureCategory.NONE
    retry_count: int = 0
    max_retries: int = 3
    previous_success_rate: float = 0.85
    customer_tenure_months: int = 12
    transaction_timestamp: str
    risk_score: float = 15.0
    risk_factors: List[str] = []
    recovery_eligible: bool = False
    recovery_priority: RecoveryPriority = RecoveryPriority.NONE
    recommended_action_type: ActionType = ActionType.DO_NOT_RETRY
    recommended_action: str = "No action required"
    action_explanation: Optional[ActionExplanation] = None
    confidence_score: float = 0.90
    estimated_recovery_value: float = 0.0
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovered_amount: float = 0.0
    recovery_timestamp: Optional[str] = None
    recovery_attempts_history: List[Dict[str, Any]] = []

class SimulatePaymentRequest(BaseModel):
    amount: float = 1500.0
    payment_method: PaymentMethod = PaymentMethod.CARD
    customer_id: Optional[str] = None
    scenario: str = "INSIGHT_FUNDS" # "INSIGHT_FUNDS", "EXPIRED_CARD", "NETWORK_TIMEOUT", "HIGH_FRAUD_RISK", "INVALID_ACCOUNT", "SUCCESSFUL"

class AttemptRecoveryRequest(BaseModel):
    action_override: Optional[ActionType] = None
    notes: Optional[str] = None

class AssistantChatRequest(BaseModel):
    query: str
    transaction_id: Optional[str] = None

class AssistantChatResponse(BaseModel):
    answer: str
    evidence: List[Dict[str, Any]] = []
    suggested_actions: List[str] = []

class AnalyticsSummary(BaseModel):
    total_attempts: int
    successful_payments: int
    failed_payments: int
    recovery_opportunities: int
    recovered_revenue: float
    recovery_rate: float
    payment_success_rate: float
    revenue_at_risk: float
    predicted_recovery_potential: float
    avg_recovery_time_minutes: float
    failure_category_breakdown: Dict[str, int]
    payment_method_breakdown: Dict[str, Dict[str, float]]
    recent_recovery_attempts: List[Dict[str, Any]]

class EvaluationMetrics(BaseModel):
    ml_precision: float
    ml_recall: float
    ml_f1_score: float
    ml_roc_auc: float
    confusion_matrix: Dict[str, int]
    recovery_opportunity_count: int
    recovery_attempts_count: int
    successful_recoveries_count: int
    actual_recovery_rate: float
    recovered_revenue: float
    revenue_still_at_risk: float
    agent_recommendation_accuracy: float
    agent_groundedness_rate: float
    agent_invalid_action_rate: float

class PolicyConfig(BaseModel):
    max_retries_per_txn: int = 2
    min_retry_delay_minutes: int = 15
    max_automated_amount: float = 50000.0
    escalation_risk_threshold: float = 80.0
    non_retryable_codes: List[str] = ["14", "FRAUD_HIGH"]

class AuditEntry(BaseModel):
    timestamp: str
    transaction_id: str
    customer_name: str
    failure_reason: str
    risk_score: float
    eligibility_decision: str
    recommended_action: str
    policy_applied: str
    action_executed: str
    result: str
    recovered_amount: float
    stopping_reason: Optional[str] = None

class BatchSummary(BaseModel):
    batch_id: str
    records_processed: int
    eligible_count: int
    revenue_at_risk: float
    attempts_count: int
    successful_count: int
    failed_count: int
    revenue_recovered: float
    unrecovered_revenue: float
    recovery_rate: float
    stopped_by_guardrails_count: int
    escalated_count: int
    audit_log: List[AuditEntry] = []

class BatchRunRequest(BaseModel):
    batch_size: int = 500
    batch_type: str = "ALL" # "ALL", "TECHNICAL", "CUSTOMER", "RISK"
    policy_override: Optional[PolicyConfig] = None

# ── Authentication & User Models ─────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    merchant_name: str = "My Business"
    merchant_id: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    merchant_id: str
    merchant_name: str
    email: str

class MerchantUser(BaseModel):
    merchant_id: str
    email: str
    merchant_name: str
    hashed_password: str
    created_at: str
    role: str = "merchant"

