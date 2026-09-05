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

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const AUTH_BASE = '/api/v1/auth';

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
    const res = await axios.post(`${AUTH_BASE}/login`, { email, password });
    localStorage.setItem('payguard_token', res.data.access_token);
    return res.data;
  },

  signup: async (email: string, password: string, merchant_name: string): Promise<TokenResponse> => {
    const res = await axios.post(`${AUTH_BASE}/signup`, { email, password, merchant_name });
    localStorage.setItem('payguard_token', res.data.access_token);
    return res.data;
  },

  getMe: async (): Promise<AuthUser> => {
    const res = await authAxios.get(`${AUTH_BASE}/me`);
    return res.data;
  },

  logout: () => {
    localStorage.removeItem('payguard_token');
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
      console.warn("API disconnect fallback", e);
      return [];
    }
  },

  getPaymentById: async (id: string): Promise<PaymentRecord> => {
    const res = await axios.get(`${API_BASE}/payments/${id}`);
    return res.data;
  },

  simulatePayment: async (data: { amount: number; payment_method: string; scenario: string }): Promise<PaymentRecord> => {
    const res = await axios.post(`${API_BASE}/payments/simulate`, data);
    return res.data;
  },

  assessRecovery: async (id: string) => {
    const res = await axios.post(`${API_BASE}/payments/${id}/assess-recovery`);
    return res.data;
  },

  recommendAction: async (id: string) => {
    const res = await axios.post(`${API_BASE}/payments/${id}/recommend-action`);
    return res.data;
  },

  attemptRecovery: async (id: string, action_override?: string) => {
    const res = await axios.post(`${API_BASE}/payments/${id}/attempt-recovery`, { action_override });
    return res.data;
  },

  // ── Recovery & Batch Operations ────────────────────────────────────────
  getOpportunities: async (): Promise<PaymentRecord[]> => {
    const res = await axios.get(`${API_BASE}/recovery/opportunities`);
    return res.data;
  },

  getAnalytics: async (): Promise<AnalyticsSummary> => {
    const res = await axios.get(`${API_BASE}/recovery/analytics`);
    return res.data;
  },

  runBatchRecovery: async (data?: { batch_size?: number; batch_type?: string; policy_override?: PolicyConfig }): Promise<BatchSummary> => {
    const res = await axios.post(`${API_BASE}/recovery/batch/run`, data || { batch_size: 500, batch_type: 'ALL' });
    return res.data;
  },

  getBatchSummary: async (): Promise<BatchSummary> => {
    const res = await axios.get(`${API_BASE}/recovery/batch/summary`);
    return res.data;
  },

  getPolicyConfig: async (): Promise<PolicyConfig> => {
    const res = await axios.get(`${API_BASE}/recovery/policy/config`);
    return res.data;
  },

  updatePolicyConfig: async (config: PolicyConfig): Promise<PolicyConfig> => {
    const res = await axios.post(`${API_BASE}/recovery/policy/config`, config);
    return res.data;
  },

  getAuditLog: async (): Promise<AuditEntry[]> => {
    const res = await axios.get(`${API_BASE}/recovery/audit-log`);
    return res.data;
  },

  // ── Risk ──────────────────────────────────────────────────────────────
  getRiskExplain: async (id: string) => {
    const res = await axios.get(`${API_BASE}/risk/explain/${id}`);
    return res.data;
  },

  // ── Assistant ─────────────────────────────────────────────────────────
  chatAssistant: async (query: string, transaction_id?: string) => {
    const res = await axios.post(`${API_BASE}/assistant/chat`, { query, transaction_id });
    return res.data;
  },

  askAssistant: async (query: string, transaction_id?: string) => {
    const res = await axios.post(`${API_BASE}/assistant/chat`, { query, transaction_id });
    return res.data;
  }

  // ── Evaluation ────────────────────────────────────────────────────────
  ,getEvaluation: async (): Promise<EvaluationMetrics> => {
    const res = await axios.get(`${API_BASE}/evaluation`);
    return res.data;
  }
};
