export type PaymentMethod = 'CARD' | 'UPI' | 'NETBANKING' | 'WALLET';
export type PaymentStatus = 'SUCCESSFUL' | 'FAILED' | 'PENDING' | 'RECOVERABLE' | 'NON_RECOVERABLE' | 'RECOVERED';
export type FailureCategory = 'TECHNICAL' | 'CUSTOMER_RELATED' | 'RISK_RELATED' | 'NON_RECOVERABLE' | 'NONE';
export type RecoveryPriority = 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
export type ActionType = 'RETRY_DELAY' | 'SWITCH_METHOD' | 'REQUEST_DETAILS' | 'SEND_REMINDER' | 'ESCALATE_MERCHANT' | 'DO_NOT_RETRY';

export interface ActionExplanation {
  why_failed: string;
  eligibility_rationale: string;
  action_rationale: string;
  evidence_points: string[];
  target_metric: string;
}

export interface PaymentRecord {
  transaction_id: string;
  customer_id: string;
  customer_name: string;
  merchant_id: string;
  amount: number;
  currency: string;
  payment_method: PaymentMethod;
  payment_status: PaymentStatus;
  failure_reason?: string;
  failure_code?: string;
  failure_category: FailureCategory;
  retry_count: number;
  max_retries: number;
  previous_success_rate: number;
  customer_tenure_months: number;
  transaction_timestamp: string;
  risk_score: number;
  risk_factors: string[];
  recovery_eligible: boolean;
  recovery_priority: RecoveryPriority;
  recommended_action_type: ActionType;
  recommended_action: string;
  action_explanation?: ActionExplanation;
  confidence_score: number;
  estimated_recovery_value: number;
  recovery_attempted: boolean;
  recovery_successful: boolean;
  recovered_amount: number;
  recovery_timestamp?: string;
  recovery_attempts_history: Array<{
    timestamp: string;
    action_type?: string;
    action_name?: string;
    action?: string;
    outcome: string;
    recovered_amount: number;
  }>;
}

export interface AnalyticsSummary {
  total_attempts: number;
  successful_payments: number;
  failed_payments: number;
  recovery_opportunities: number;
  recovered_revenue: number;
  recovery_rate: number;
  payment_success_rate: number;
  revenue_at_risk: number;
  predicted_recovery_potential: number;
  avg_recovery_time_minutes: number;
  failure_category_breakdown: Record<string, number>;
  payment_method_breakdown: Record<string, { total: number; failed: number; recovered_revenue: number }>;
  recent_recovery_attempts: Array<{
    transaction_id: string;
    customer_name: string;
    amount: number;
    payment_method: string;
    action_taken: string;
    outcome: string;
    timestamp: string;
  }>;
}

export interface EvaluationMetrics {
  ml_evaluation: {
    model_name: string;
    test_dataset: string;
    ml_accuracy: number;
    ml_precision: number;
    ml_recall: number;
    ml_f1_score: number;
    ml_roc_auc: number;
    ml_pr_auc: number;
    confusion_matrix: {
      true_positives: number;
      false_positives: number;
      true_negatives: number;
      false_negatives: number;
    };
    class_distribution: {
      legitimate_txns: number;
      fraud_txns: number;
      fraud_ratio_pct: number;
    };
    imbalance_analysis: string;
  };
  recovery_evaluation: {
    recovery_opportunity_count: number;
    recovery_attempts: number;
    successful_recoveries: number;
    recovery_rate_pct: number;
    revenue_recovered: number;
    revenue_still_at_risk: number;
    category_breakdown: Record<string, any>;
  };
  agent_evaluation: {
    recommendation_accuracy: number;
    agent_groundedness_rate: number;
    agent_invalid_action_rate: number;
    hallucination_check: string;
    evidence_completeness: number;
  };
}

export interface AuthUser {
  merchant_id: string;
  merchant_name: string;
  email: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  merchant_id: string;
  merchant_name: string;
  email: string;
}

export interface PolicyConfig {
  max_retries_per_txn: number;
  min_retry_delay_minutes: number;
  max_automated_amount: number;
  escalation_risk_threshold: number;
  non_retryable_codes: string[];
}

export interface AuditEntry {
  timestamp: string;
  transaction_id: string;
  customer_name: string;
  failure_reason: string;
  risk_score: number;
  eligibility_decision: string;
  recommended_action: string;
  policy_applied: string;
  action_executed: string;
  result: string;
  recovered_amount: number;
  stopping_reason?: string | null;
}

export interface BatchSummary {
  batch_id: string;
  records_processed: number;
  eligible_count: number;
  revenue_at_risk: number;
  attempts_count: number;
  successful_count: number;
  failed_count: number;
  revenue_recovered: number;
  unrecovered_revenue: number;
  recovery_rate: number;
  stopped_by_guardrails_count: number;
  escalated_count: number;
  audit_log: AuditEntry[];
}

