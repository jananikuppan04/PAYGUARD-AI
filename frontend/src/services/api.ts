import axios from 'axios';
import { 
  PaymentRecord, 
  AnalyticsSummary, 
  EvaluationMetrics, 
  AuthUser, 
  TokenResponse,
  PolicyConfig,
  BatchSummary,
  AuditEntry 
} from '../types/payment';

import { 
  MOCK_PAYMENTS, 
  MOCK_ANALYTICS, 
  MOCK_EVALUATION, 
  MOCK_POLICY_CONFIG, 
  MOCK_BATCH_SUMMARY, 
  MOCK_AUDIT_LOG 
} from './mockData';

// Mutable local state for demo/Vercel fallback
let localPayments: PaymentRecord[] = [...MOCK_PAYMENTS];
let localAnalytics: AnalyticsSummary = { ...MOCK_ANALYTICS };
let localPolicy: PolicyConfig = { ...MOCK_POLICY_CONFIG };
let localAudit: AuditEntry[] = [...MOCK_AUDIT_LOG];

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const AUTH_BASE = `${API_BASE}/auth`;

// Axios instance with token injection
const authAxios = axios.create();
authAxios.interceptors.request.use((config) => {
  const token = localStorage.getItem('payguard_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // ── Auth ─────────────────────────────────────────────────────────────
  login: async (email: string, password: string): Promise<TokenResponse> => {
    try {
      const res = await axios.post(`${AUTH_BASE}/login`, { email, password });
      localStorage.setItem('payguard_token', res.data.access_token);
      localStorage.setItem('payguard_user', JSON.stringify(res.data));
      return res.data;
    } catch (err) {
      console.warn("Backend auth unavailable, initializing client demo session");
      const demoToken = `demo_token_${Date.now()}`;
      localStorage.setItem('payguard_token', demoToken);
      const demoData: TokenResponse = {
        access_token: demoToken,
        token_type: 'bearer',
        merchant_name: email.split('@')[0] || 'Merchant Admin',
        user_id: 'USER-DEMO-01'
      };
      localStorage.setItem('payguard_user', JSON.stringify(demoData));
      return demoData;
    }
  },

  signup: async (email: string, password: string, merchant_name: string): Promise<TokenResponse> => {
    try {
      const res = await axios.post(`${AUTH_BASE}/signup`, { email, password, merchant_name });
      localStorage.setItem('payguard_token', res.data.access_token);
      localStorage.setItem('payguard_user', JSON.stringify(res.data));
      return res.data;
    } catch (err) {
      console.warn("Backend auth unavailable, initializing client demo session");
      const demoToken = `demo_token_${Date.now()}`;
      localStorage.setItem('payguard_token', demoToken);
      const demoData: TokenResponse = {
        access_token: demoToken,
        token_type: 'bearer',
        merchant_name: merchant_name || 'Merchant Admin',
        user_id: 'USER-DEMO-01'
      };
      localStorage.setItem('payguard_user', JSON.stringify(demoData));
      return demoData;
    }
  },

  getMe: async (): Promise<AuthUser> => {
    try {
      const res = await authAxios.get(`${AUTH_BASE}/me`);
      return res.data;
    } catch (e) {
      return {
        id: 'USER-DEMO-01',
        email: 'admin@payguard.ai',
        merchant_name: 'Merchant Admin',
        role: 'admin',
        created_at: '2026-01-01'
      };
    }
  },

  logout: () => {
    localStorage.removeItem('payguard_token');
    localStorage.removeItem('payguard_user');
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('payguard_token');
  },

  // ── Payments ──────────────────────────────────────────────────────────
  getPayments: async (params?: { status?: string; category?: string; method?: string; priority?: string }): Promise<PaymentRecord[]> => {
    try {
      const res = await axios.get(`${API_BASE}/payments`, { params });
      return res.data;
    } catch (e) {
      let filtered = [...localPayments];
      if (params?.status) filtered = filtered.filter(p => p.payment_status === params.status);
      if (params?.category) filtered = filtered.filter(p => p.failure_category === params.category);
      if (params?.method) filtered = filtered.filter(p => p.payment_method === params.method);
      if (params?.priority) filtered = filtered.filter(p => p.recovery_priority === params.priority);
      return filtered;
    }
  },

  getPaymentById: async (id: string): Promise<PaymentRecord> => {
    try {
      const res = await axios.get(`${API_BASE}/payments/${id}`);
      return res.data;
    } catch (e) {
      const found = localPayments.find(p => p.transaction_id === id);
      if (found) return found;
      return localPayments[0];
    }
  },

  simulatePayment: async (data: { amount: number; payment_method: string; scenario: string }): Promise<PaymentRecord> => {
    try {
      const res = await axios.post(`${API_BASE}/payments/simulate`, data);
      return res.data;
    } catch (e) {
      const newId = `TXN-${1000 + localPayments.length + 1}`;
      const isDeclined = data.scenario !== 'SUCCESS';
      const newRecord: PaymentRecord = {
        transaction_id: newId,
        customer_id: `CUST-${Math.floor(Math.random() * 800) + 100}`,
        customer_name: 'Simulated Customer',
        merchant_id: 'MERCHANT_RAZOR_01',
        amount: data.amount,
        payment_method: data.payment_method as any,
        payment_status: isDeclined ? 'RECOVERABLE' : 'SUCCESSFUL',
        failure_reason: isDeclined ? 'Acquirer Gateway Timeout (Decline Code 91)' : undefined,
        failure_code: isDeclined ? '91' : undefined,
        failure_category: isDeclined ? ('TECHNICAL' as any) : ('NONE' as any),
        retry_count: 0,
        max_retries: 3,
        previous_success_rate: 0.88,
        customer_tenure_months: 12,
        transaction_timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        risk_score: 18.5,
        risk_factors: ['Simulated Gateway Event', 'Low Anomaly Score'],
        recovery_eligible: isDeclined,
        recovery_priority: 'HIGH' as any,
        recommended_action_type: 'RETRY_DELAY' as any,
        recommended_action: 'Smart Retry via Secondary Backup Gateway after 15 min delay',
        confidence_score: 0.94,
        estimated_recovery_value: isDeclined ? data.amount * 0.94 : 0,
        recovery_attempted: false,
        recovery_successful: false,
        recovered_amount: 0,
        recovery_attempts_history: []
      };
      localPayments.unshift(newRecord);
      return newRecord;
    }
  },

  assessRecovery: async (id: string) => {
    try {
      const res = await axios.post(`${API_BASE}/payments/${id}/assess-recovery`);
      return res.data;
    } catch (e) {
      return {
        transaction_id: id,
        eligible: true,
        priority: 'HIGH',
        category: 'TECHNICAL',
        confidence_score: 0.92,
        rationale: 'Customer account in good standing; transient bank gateway timeout.'
      };
    }
  },

  recommendAction: async (id: string) => {
    try {
      const res = await axios.post(`${API_BASE}/payments/${id}/recommend-action`);
      return res.data;
    } catch (e) {
      return {
        transaction_id: id,
        recommended_action_type: 'RETRY_DELAY',
        recommended_action: 'Smart Retry via Backup Gateway after 15 min delay',
        confidence_score: 0.92,
        estimated_recovery_value: 2999
      };
    }
  },

  attemptRecovery: async (id: string, action_override?: string) => {
    try {
      const res = await axios.post(`${API_BASE}/payments/${id}/attempt-recovery`, { action_override });
      return res.data;
    } catch (e) {
      const idx = localPayments.findIndex(p => p.transaction_id === id);
      if (idx !== -1) {
        localPayments[idx].payment_status = 'RECOVERED';
        localPayments[idx].recovery_attempted = true;
        localPayments[idx].recovery_successful = true;
        localPayments[idx].recovered_amount = localPayments[idx].amount;
        localPayments[idx].recovery_timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        localAnalytics.recovered_revenue += localPayments[idx].amount;
      }
      return {
        success: true,
        message: `Recovery initiated for ${id}: Optimal recovery action executed successfully.`,
        transaction_id: id
      };
    }
  },

  // ── Recovery & Batch Operations ────────────────────────────────────────
  getOpportunities: async (): Promise<PaymentRecord[]> => {
    try {
      const res = await axios.get(`${API_BASE}/recovery/opportunities`);
      return res.data;
    } catch (e) {
      return localPayments.filter(p => p.payment_status === 'RECOVERABLE');
    }
  },

  getAnalytics: async (): Promise<AnalyticsSummary> => {
    try {
      const res = await axios.get(`${API_BASE}/recovery/analytics`);
      return res.data;
    } catch (e) {
      return localAnalytics;
    }
  },

  runBatchRecovery: async (data?: { batch_size?: number; batch_type?: string; policy_override?: PolicyConfig }): Promise<BatchSummary> => {
    try {
      const res = await axios.post(`${API_BASE}/recovery/batch/run`, data || { batch_size: 500, batch_type: 'ALL' });
      return res.data;
    } catch (e) {
      return localBatchSummary;
    }
  },

  getBatchSummary: async (): Promise<BatchSummary> => {
    try {
      const res = await axios.get(`${API_BASE}/recovery/batch/summary`);
      return res.data;
    } catch (e) {
      return localBatchSummary;
    }
  },

  getPolicyConfig: async (): Promise<PolicyConfig> => {
    try {
      const res = await axios.get(`${API_BASE}/recovery/policy/config`);
      return res.data;
    } catch (e) {
      return localPolicy;
    }
  },

  updatePolicyConfig: async (config: PolicyConfig): Promise<PolicyConfig> => {
    try {
      const res = await axios.post(`${API_BASE}/recovery/policy/config`, config);
      return res.data;
    } catch (e) {
      localPolicy = { ...config };
      return localPolicy;
    }
  },

  getAuditLog: async (): Promise<AuditEntry[]> => {
    try {
      const res = await axios.get(`${API_BASE}/recovery/audit-log`);
      return res.data;
    } catch (e) {
      return localAudit;
    }
  },

  // ── Risk ──────────────────────────────────────────────────────────────
  getRiskExplain: async (id: string) => {
    try {
      const res = await axios.get(`${API_BASE}/risk/explain/${id}`);
      return res.data;
    } catch (e) {
      const txn = localPayments.find(p => p.transaction_id === id);
      return {
        transaction_id: id,
        risk_score: txn?.risk_score || 24.5,
        risk_level: 'LOW',
        anomaly_score: 0.12,
        top_contributing_features: [
          { feature: 'customer_tenure_months', impact: -0.42, description: 'Long customer tenure reduces risk profile' },
          { feature: 'previous_success_rate', impact: -0.35, description: 'High historical completion rate' },
          { feature: 'amount_vs_historical_avg', impact: +0.18, description: 'Amount is within normal purchasing range' }
        ],
        explanation: 'Transaction passed anti-fraud guardrails. Decline was determined to be transient gateway latency.'
      };
    }
  },

  // ── Assistant ─────────────────────────────────────────────────────────
  chatAssistant: async (query: string, transaction_id?: string) => {
    try {
      const res = await axios.post(`${API_BASE}/assistant/chat`, { query, transaction_id });
      return res.data;
    } catch (e) {
      const q = query.toLowerCase();
      let responseText = "PayGuard AI autonomous recovery engine is monitoring payment traffic across gateways. All recovery actions adhere strictly to merchant guardrails (max 3 retries, minimum 15-minute backoff, and zero retries for flagged card anomalies).";
      
      if (q.includes('code 91') || q.includes('timeout') || q.includes('technical')) {
        responseText = "Code 91 indicates an Issuer Gateway Timeout during 3DS authorization. PayGuard's recommended action is Smart Retry via secondary acquirer node after a 15-minute backoff window, achieving a 96% success rate.";
      } else if (q.includes('code 51') || q.includes('insufficient')) {
        responseText = "Code 51 represents Insufficient Funds. For tenured customers (>6 months), PayGuard triggers an automated WhatsApp payment link reminder after 2 hours, resulting in ₹1,48,000 in recovered revenue.";
      } else if (q.includes('recovery rate') || q.includes('revenue')) {
        responseText = `Current active recovery rate is ${localAnalytics.recovery_rate}% with ₹${localAnalytics.recovered_revenue.toLocaleString('en-IN')} recovered across ${localAnalytics.recent_recovery_attempts.length} verified operations. Total revenue currently at risk is ₹${localAnalytics.revenue_at_risk.toLocaleString('en-IN')}.`;
      } else if (transaction_id) {
        responseText = `Analysis for ${transaction_id}: Risk Score is 18.5/100 (Low Risk). Technical failure diagnosed as transient gateway latency. Recommended action: Smart Retry via Backup Gateway.`;
      }

      return {
        query,
        response: responseText,
        confidence: 0.96,
        sources: ['PayGuard Policy Engine', 'Razorpay Gateway Intelligence', 'XGBoost Risk Assessor'],
        recommended_action: 'Smart Retry via Secondary Gateway',
        transaction_id
      };
    }
  },

  askAssistant: async (query: string, transaction_id?: string) => {
    return api.chatAssistant(query, transaction_id);
  },

  // ── Evaluation ────────────────────────────────────────────────────────
  getEvaluation: async (): Promise<EvaluationMetrics> => {
    try {
      const res = await axios.get(`${API_BASE}/evaluation`);
      return res.data;
    } catch (e) {
      return MOCK_EVALUATION;
    }
  }
};
