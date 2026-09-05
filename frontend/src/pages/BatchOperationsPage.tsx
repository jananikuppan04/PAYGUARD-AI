import React, { useState, useEffect } from 'react';
import { BatchSummary, PolicyConfig, AuditEntry, PaymentRecord } from '../types/payment';
import { api } from '../services/api';
import { 
  Play, 
  RefreshCw, 
  ShieldAlert, 
  DollarSign, 
  TrendingUp, 
  CheckCircle2, 
  AlertTriangle, 
  Sliders, 
  Clock, 
  FileText, 
  Search, 
  ArrowRight,
  ShieldCheck,
  Bot
} from 'lucide-react';

interface BatchOperationsPageProps {
  onSelectPayment: (payment: PaymentRecord) => void;
  onNavigateTab?: (tab: string) => void;
}

export const BatchOperationsPage: React.FC<BatchOperationsPageProps> = ({ onSelectPayment, onNavigateTab }) => {
  const [batchData, setBatchData] = useState<BatchSummary | null>(null);
  const [policyConfig, setPolicyConfig] = useState<PolicyConfig | null>(null);
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterResult, setFilterResult] = useState('ALL');
  const [selectedBatchType, setSelectedBatchType] = useState('ALL');
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  // Policy form state
  const [maxRetries, setMaxRetries] = useState(2);
  const [maxAmount, setMaxAmount] = useState(50000);
  const [escalationRisk, setEscalationRisk] = useState(80);

  const fetchBatchData = async () => {
    setIsLoading(true);
    try {
      const [bSum, pConfig, pList] = await Promise.all([
        api.getBatchSummary(),
        api.getPolicyConfig(),
        api.getPayments()
      ]);
      setBatchData(bSum);
      setPolicyConfig(pConfig);
      setPayments(pList);
      if (pConfig) {
        setMaxRetries(pConfig.max_retries_per_txn);
        setMaxAmount(pConfig.max_automated_amount);
        setEscalationRisk(pConfig.escalation_risk_threshold);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBatchData();
  }, []);

  const handleRunBatchExecution = async () => {
    setIsLoading(true);
    try {
      const updated = await api.runBatchRecovery({
        batch_size: 500,
        batch_type: selectedBatchType,
        policy_override: policyConfig || undefined
      });
      setBatchData(updated);
      const updatedPayments = await api.getPayments();
      setPayments(updatedPayments);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updatedConfig = await api.updatePolicyConfig({
        max_retries_per_txn: Number(maxRetries),
        min_retry_delay_minutes: 15,
        max_automated_amount: Number(maxAmount),
        escalation_risk_threshold: Number(escalationRisk),
        non_retryable_codes: ["14", "FRAUD_HIGH"]
      });
      setPolicyConfig(updatedConfig);
      setIsConfigOpen(false);
      await handleRunBatchExecution();
    } catch (e) {
      console.error(e);
    }
  };

  const filteredAuditLog = (batchData?.audit_log || []).filter((entry) => {
    const matchesSearch = 
      entry.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.failure_reason.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesResult = 
      filterResult === 'ALL' || 
      (filterResult === 'RECOVERED' && entry.result === 'RECOVERED') ||
      (filterResult === 'STOPPED' && entry.result === 'STOPPED') ||
      (filterResult === 'ESCALATED' && entry.result === 'ESCALATED');

    return matchesSearch && matchesResult;
  });

  return (
    <div className="space-y-6 pb-12 animate-fade-in text-zinc-900 dark:text-zinc-100">
      
      {/* Agent Core Loop Banner & Header */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="p-1 rounded bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400">
                <Bot className="h-4 w-4" />
              </span>
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400">
                Batch Recovery Operations Control Center
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 mt-1">
              AI Revenue Recovery Agent Execution
            </h1>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
              Detect revenue at risk, enforce policy guardrails, execute bounded recovery actions, and reconcile actual money recovered across batch opportunities.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsConfigOpen(true)}
              className="px-3.5 py-2 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 text-xs font-semibold hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors flex items-center space-x-2"
            >
              <Sliders className="h-3.5 w-3.5 text-zinc-400" />
              <span>Configure Guardrails</span>
            </button>

            <button
              onClick={handleRunBatchExecution}
              disabled={isLoading}
              className="px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-xs font-bold shadow-sm flex items-center space-x-2 transition-all disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>Executing Batch...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Run Batch Agent Recovery</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Core Agent Loop Pipeline Pill Bar */}
        <div className="pt-3 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between overflow-x-auto text-[11px] font-mono font-semibold text-zinc-500 dark:text-zinc-400">
          <span className="text-zinc-900 dark:text-zinc-100">AGENT LOOP:</span>
          <span>1. Detect Risk</span>
          <span>→</span>
          <span>2. Diagnose Failure</span>
          <span>→</span>
          <span>3. Check Eligibility</span>
          <span>→</span>
          <span className="text-purple-600 dark:text-purple-400">4. Guardrail Policy</span>
          <span>→</span>
          <span className="text-zinc-900 dark:text-zinc-100">5. Bounded Execute</span>
          <span>→</span>
          <span className="text-emerald-600 dark:text-emerald-400 font-bold">6. Reconcile Revenue</span>
          <span>→</span>
          <span>7. Audit Trail</span>
        </div>
      </div>

      {/* Batch Overview Summary Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
        <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-1">
          <span className="text-[10px] uppercase font-bold text-zinc-400">Batch Analyzed</span>
          <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{batchData?.records_processed || 500}</p>
          <span className="text-[10px] text-zinc-500">Transactions</span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-1">
          <span className="text-[10px] uppercase font-bold text-zinc-400">Revenue at Risk</span>
          <p className="text-xl font-bold text-amber-600 dark:text-amber-400">₹{batchData?.revenue_at_risk.toLocaleString('en-IN') || '0'}</p>
          <span className="text-[10px] text-zinc-500">{batchData?.eligible_count || 0} Eligible</span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-1">
          <span className="text-[10px] uppercase font-bold text-zinc-400">Money Recovered</span>
          <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400">₹{batchData?.revenue_recovered.toLocaleString('en-IN') || '0'}</p>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">100% Reconciled</span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-1">
          <span className="text-[10px] uppercase font-bold text-zinc-400">Recovery Rate</span>
          <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{batchData?.recovery_rate || 0}%</p>
          <span className="text-[10px] text-zinc-500">{batchData?.successful_count || 0} Recovered</span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-1">
          <span className="text-[10px] uppercase font-bold text-zinc-400">Policy Stopped</span>
          <p className="text-xl font-bold text-zinc-700 dark:text-zinc-300">{batchData?.stopped_by_guardrails_count || 0}</p>
          <span className="text-[10px] text-zinc-500">Guardrail Rules</span>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-1">
          <span className="text-[10px] uppercase font-bold text-zinc-400">Escalated Review</span>
          <p className="text-xl font-bold text-red-600 dark:text-red-400">{batchData?.escalated_count || 0}</p>
          <span className="text-[10px] text-zinc-500">Manual Approval</span>
        </div>
      </div>

      {/* Active Guardrails Policy Status Panel */}
      <div className="p-4 rounded-xl bg-zinc-900 dark:bg-zinc-950 text-white border border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center space-x-3">
          <ShieldCheck className="h-5 w-5 text-emerald-400 shrink-0" />
          <div>
            <span className="text-[10px] uppercase font-bold text-zinc-400 block">Active Bounded Recovery Policy Guardrails</span>
            <p className="font-bold text-zinc-100">
              Max Retries: <span className="text-emerald-400">{policyConfig?.max_retries_per_txn || 2}</span> | Max Auto Amount: <span className="text-emerald-400">₹{(policyConfig?.max_automated_amount || 50000).toLocaleString()}</span> | Fraud Threshold: <span className="text-emerald-400">{policyConfig?.escalation_risk_threshold || 80}/100</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="px-2.5 py-1 rounded bg-zinc-800 border border-zinc-700 text-zinc-300 text-[10px]">
            Non-Retryable Codes: 14, FRAUD_HIGH
          </span>
          <button
            onClick={() => setIsConfigOpen(true)}
            className="px-3 py-1 rounded bg-white text-zinc-900 font-bold hover:bg-zinc-100 transition-colors text-[11px]"
          >
            Edit Policy
          </button>
        </div>
      </div>

      {/* Batch Transaction Operations Audit Table */}
      <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-3">
          <div>
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 flex items-center space-x-2">
              <FileText className="h-4 w-4 text-zinc-500" />
              <span>Batch Interventions & Policy Audit Log</span>
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Chronological decision log with explicit eligibility rationale and stopping reasons.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="h-3.5 w-3.5 absolute left-3 top-2.5 text-zinc-400" />
              <input
                type="text"
                placeholder="Search TXN ID or Customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none"
              />
            </div>

            <select
              value={filterResult}
              onChange={(e) => setFilterResult(e.target.value)}
              className="py-1.5 px-3 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none font-mono"
            >
              <option value="ALL">All Outcomes</option>
              <option value="RECOVERED">Recovered Money</option>
              <option value="STOPPED">Stopped by Policy</option>
              <option value="ESCALATED">Escalated to Review</option>
            </select>
          </div>
        </div>

        {/* Audit Log Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-zinc-700 dark:text-zinc-300">
            <thead className="bg-zinc-50 dark:bg-zinc-900/60 text-zinc-400 uppercase tracking-wider font-mono text-[10px] border-b border-zinc-200 dark:border-zinc-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Transaction ID</th>
                <th className="py-2.5 px-3">Customer</th>
                <th className="py-2.5 px-3">Failure Reason</th>
                <th className="py-2.5 px-3">Risk</th>
                <th className="py-2.5 px-3">Intervention Action</th>
                <th className="py-2.5 px-3">Result</th>
                <th className="py-2.5 px-3 font-right">Money Recovered</th>
                <th className="py-2.5 px-3">Stopping Reason / Policy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800/80 font-mono text-[11px]">
              {filteredAuditLog.slice(0, 15).map((log, idx) => (
                <tr
                  key={idx}
                  onClick={() => {
                    const target = payments.find((p) => p.transaction_id === log.transaction_id);
                    if (target) onSelectPayment(target);
                  }}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors cursor-pointer"
                >
                  <td className="py-2.5 px-3 text-zinc-400 text-[10px]">{log.timestamp}</td>
                  <td className="py-2.5 px-3 font-bold text-zinc-900 dark:text-zinc-100">{log.transaction_id}</td>
                  <td className="py-2.5 px-3 font-sans font-medium text-zinc-800 dark:text-zinc-200">{log.customer_name}</td>
                  <td className="py-2.5 px-3 max-w-xs truncate text-zinc-600 dark:text-zinc-400 font-sans">{log.failure_reason}</td>
                  <td className="py-2.5 px-3">{log.risk_score}</td>
                  <td className="py-2.5 px-3 max-w-xs truncate font-sans text-zinc-800 dark:text-zinc-200">{log.action_executed}</td>
                  <td className="py-2.5 px-3 font-bold">
                    <span className={`px-2 py-0.5 rounded text-[9px] ${
                      log.result === 'RECOVERED' ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800' :
                      log.result === 'ESCALATED' ? 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800' :
                      'bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700'
                    }`}>
                      {log.result}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-bold text-emerald-600 dark:text-emerald-400">
                    {log.recovered_amount > 0 ? `₹${log.recovered_amount.toLocaleString('en-IN')}` : '—'}
                  </td>
                  <td className="py-2.5 px-3 max-w-xs truncate text-[10px] text-zinc-500 font-sans">
                    {log.stopping_reason ? (
                      <span className="font-mono text-amber-600 dark:text-amber-400">{log.stopping_reason}</span>
                    ) : (
                      log.policy_applied
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>

      {/* Policy Guardrails Config Modal */}
      {isConfigOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 shadow-2xl space-y-4 text-xs font-sans text-zinc-900 dark:text-zinc-100">
            <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
              <h3 className="font-bold text-sm">Configure Recovery Guardrails & Policies</h3>
              <button onClick={() => setIsConfigOpen(false)} className="text-zinc-400 hover:text-zinc-900 dark:hover:text-white">✕</button>
            </div>

            <form onSubmit={handleSavePolicy} className="space-y-3.5">
              <div>
                <label className="block text-[11px] font-mono uppercase font-bold text-zinc-500 mb-1">Max Retries per Transaction</label>
                <input
                  type="number"
                  value={maxRetries}
                  onChange={(e) => setMaxRetries(Number(e.target.value))}
                  min={1}
                  max={5}
                  className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase font-bold text-zinc-500 mb-1">Max Automated Amount Limit (₹)</label>
                <input
                  type="number"
                  value={maxAmount}
                  onChange={(e) => setMaxAmount(Number(e.target.value))}
                  min={1000}
                  className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase font-bold text-zinc-500 mb-1">Manual Fraud Escalation Threshold (0-100)</label>
                <input
                  type="number"
                  value={escalationRisk}
                  onChange={(e) => setEscalationRisk(Number(e.target.value))}
                  min={50}
                  max={99}
                  className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none font-mono"
                />
              </div>

              <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsConfigOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 font-bold"
                >
                  Save Guardrail Rules
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
