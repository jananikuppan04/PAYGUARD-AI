import React from 'react';
import { PaymentRecord } from '../types/payment';
import { X, CheckCircle2, AlertTriangle, Shield, ArrowRight, Zap, RefreshCw } from 'lucide-react';

interface PaymentDetailModalProps {
  payment: PaymentRecord | null;
  onClose: () => void;
  onAttemptRecovery: (transaction_id: string, actionOverride?: string) => void;
}

export const PaymentDetailModal: React.FC<PaymentDetailModalProps> = ({
  payment,
  onClose,
  onAttemptRecovery,
}) => {
  if (!payment) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 backdrop-blur-xs flex justify-end">
      
      {/* Slide-over Right Drawer Container */}
      <div className="w-full max-w-xl bg-white dark:bg-[#121215] border-l border-zinc-200 dark:border-zinc-800 h-full flex flex-col shadow-2xl animate-fade-in text-zinc-900 dark:text-zinc-100">
        
        {/* Drawer Header */}
        <div className="p-5 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-900/60">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-sm text-zinc-900 dark:text-zinc-100">
                {payment.transaction_id}
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                payment.payment_status === 'RECOVERED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800' :
                payment.payment_status === 'RECOVERABLE' ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800' :
                'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800'
              }`}>
                {payment.payment_status}
              </span>
            </div>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
              Payment Intelligence & Bounded Recovery Audit
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-500 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Drawer Body - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-3 p-4 rounded-lg bg-zinc-50 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/80 text-xs">
            <div>
              <span className="text-[10px] uppercase font-mono text-zinc-400 block">Customer</span>
              <span className="font-bold text-zinc-900 dark:text-zinc-100">{payment.customer_name}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-zinc-400 block">Amount</span>
              <span className="font-mono font-bold text-zinc-900 dark:text-zinc-100 text-sm">
                ₹{payment.amount.toLocaleString('en-IN')}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-zinc-400 block">Method</span>
              <span className="font-medium text-zinc-800 dark:text-zinc-200">{payment.payment_method}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-zinc-400 block">Decline Code</span>
              <span className="font-mono font-bold text-zinc-800 dark:text-zinc-200">{payment.decline_code}</span>
            </div>
          </div>

          {/* AI Failure Diagnosis */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-500 dark:text-zinc-400 flex items-center space-x-1.5">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
              <span>AI Failure Diagnosis</span>
            </h4>
            <div className="p-4 rounded-lg bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-zinc-900 dark:text-zinc-100">{payment.failure_reason}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300">
                  {payment.failure_category}
                </span>
              </div>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed text-[11px]">
                Categorized based on gateway decline code <code className="font-mono text-zinc-900 dark:text-zinc-100">{payment.decline_code}</code>. Diagnosed continuous risk score: <strong className="text-zinc-900 dark:text-zinc-100">{payment.risk_score} / 100</strong> ({payment.risk_level}).
              </p>
            </div>
          </div>

          {/* SHAP Risk Attribution */}
          {payment.shap_explanation && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-500 dark:text-zinc-400 flex items-center space-x-1.5">
                <Shield className="h-3.5 w-3.5 text-blue-500" />
                <span>SHAP Risk Factors</span>
              </h4>
              <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 space-y-1.5 text-xs">
                {Object.entries(payment.shap_explanation).map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between text-[11px]">
                    <span className="text-zinc-600 dark:text-zinc-400 font-mono">{key}</span>
                    <span className="font-mono font-bold text-zinc-900 dark:text-zinc-100">{String(val)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Policy Guardrail Rules Evaluation */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-500 dark:text-zinc-400 flex items-center space-x-1.5">
              <Shield className="h-3.5 w-3.5 text-emerald-500" />
              <span>Bounded Policy Guardrail Evaluation</span>
            </h4>
            <div className="p-3.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 space-y-2 text-xs font-mono">
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2 rounded bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex justify-between items-center">
                  <span className="text-zinc-500">Max Retries (2):</span>
                  <span className={payment.payment_status === 'FAILED' ? 'text-red-500 font-bold' : 'text-emerald-600 dark:text-emerald-400 font-bold'}>
                    {payment.payment_status === 'FAILED' ? '2/2 (EXCEEDED)' : '1/2 (PASS)'}
                  </span>
                </div>
                <div className="p-2 rounded bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex justify-between items-center">
                  <span className="text-zinc-500">Auto Limit (₹50k):</span>
                  <span className={payment.amount > 50000 ? 'text-amber-500 font-bold' : 'text-emerald-600 dark:text-emerald-400 font-bold'}>
                    {payment.amount > 50000 ? 'OVER LIMIT' : 'PASS'}
                  </span>
                </div>
                <div className="p-2 rounded bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex justify-between items-center">
                  <span className="text-zinc-500">Fraud Risk (&lt;80):</span>
                  <span className={payment.risk_score >= 80 ? 'text-red-500 font-bold' : 'text-emerald-600 dark:text-emerald-400 font-bold'}>
                    {payment.risk_score}/100 {payment.risk_score >= 80 ? '(ESCALATE)' : '(PASS)'}
                  </span>
                </div>
                <div className="p-2 rounded bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex justify-between items-center">
                  <span className="text-zinc-500">Decline Code:</span>
                  <span className={payment.decline_code === '14' ? 'text-red-500 font-bold' : 'text-emerald-600 dark:text-emerald-400 font-bold'}>
                    {payment.decline_code} {payment.decline_code === '14' ? '(NON-RETRY)' : '(ELIGIBLE)'}
                  </span>
                </div>
              </div>

              {/* Stopping Reason Warning Pill */}
              {(payment.payment_status === 'FAILED' || payment.decline_code === '14' || payment.risk_score >= 80) && (
                <div className="mt-2 p-2 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-[11px] text-amber-800 dark:text-amber-300 font-sans flex items-center space-x-2">
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-600 dark:text-amber-400" />
                  <span>
                    <strong>Policy Stopping Rule Applied: </strong> 
                    {payment.decline_code === '14' ? 'Non-retryable invalid card code 14.' : 
                     payment.risk_score >= 80 ? 'High fraud risk score requires manual compliance approval.' : 
                     'Maximum policy retry attempts reached. Automated recovery halted.'}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Recovery Recommendation Agent */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-500 dark:text-zinc-400 flex items-center space-x-1.5">
              <Zap className="h-3.5 w-3.5 text-purple-500" />
              <span>Bounded Recovery Recommendation</span>
            </h4>
            <div className="p-4 rounded-lg bg-zinc-900 dark:bg-zinc-950 text-white border border-zinc-800 space-y-3 text-xs">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <span className="text-[10px] uppercase font-mono text-zinc-400">Next Best Action</span>
                <span className="text-emerald-400 font-mono font-bold text-[10px]">Bounded Policy Trigger</span>
              </div>
              <p className="font-bold text-sm text-zinc-100">{payment.recommended_action}</p>

              {payment.explanation_5point && (
                <div className="space-y-2 pt-2 border-t border-zinc-800 text-[11px] text-zinc-300">
                  <div>
                    <span className="text-zinc-500 font-mono block text-[10px]">1. WHY FAILED</span>
                    <p>{payment.explanation_5point.why_failed}</p>
                  </div>
                  <div>
                    <span className="text-zinc-500 font-mono block text-[10px]">2. ELIGIBILITY EVIDENCE</span>
                    <p>{payment.explanation_5point.why_eligible}</p>
                  </div>
                  <div>
                    <span className="text-zinc-500 font-mono block text-[10px]">3. OPTIMAL ACTION</span>
                    <p>{payment.explanation_5point.why_optimal_action}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Step-by-Step Audit Log Timeline */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-500 dark:text-zinc-400 flex items-center space-x-1.5">
              <RefreshCw className="h-3.5 w-3.5 text-blue-500" />
              <span>Real-Time Recovery Audit Log</span>
            </h4>
            <div className="p-3.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 space-y-3 text-xs">
              <div className="relative pl-4 border-l-2 border-zinc-200 dark:border-zinc-800 space-y-3 text-[11px]">
                <div className="relative">
                  <span className="absolute -left-[21px] top-0.5 h-2.5 w-2.5 rounded-full bg-zinc-900 dark:bg-zinc-100"></span>
                  <p className="font-mono text-[10px] text-zinc-400">Step 1 — Ingestion & Risk Scoring</p>
                  <p className="font-medium text-zinc-800 dark:text-zinc-200">
                    Payment ingested ({payment.payment_method}, ₹{payment.amount.toLocaleString('en-IN')}). Diagnosed decline code <code className="font-mono">{payment.decline_code}</code> with SHAP risk score {payment.risk_score}/100.
                  </p>
                </div>

                <div className="relative">
                  <span className="absolute -left-[21px] top-0.5 h-2.5 w-2.5 rounded-full bg-purple-500"></span>
                  <p className="font-mono text-[10px] text-zinc-400">Step 2 — Bounded Policy Evaluation</p>
                  <p className="font-medium text-zinc-800 dark:text-zinc-200">
                    Enforced max retries (&lt;=2), auto-recovery amount (&lt;=₹50k), and non-retryable fraud rules. Action determined: <span className="font-bold text-purple-600 dark:text-purple-400">{payment.recommended_action}</span>.
                  </p>
                </div>

                <div className="relative">
                  <span className="absolute -left-[21px] top-0.5 h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                  <p className="font-mono text-[10px] text-zinc-400">Step 3 — Execution & Settlement</p>
                  <p className="font-medium text-zinc-800 dark:text-zinc-200">
                    {payment.payment_status === 'RECOVERED' ? (
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                        Intervention succeeded. 100% reconciled recovery of ₹{payment.amount.toLocaleString('en-IN')}.
                      </span>
                    ) : payment.payment_status === 'RECOVERABLE' ? (
                      <span className="text-amber-600 dark:text-amber-400 font-medium">
                        Queued for optimal intervention window. Ready for single-click execution.
                      </span>
                    ) : (
                      <span className="text-red-600 dark:text-red-400 font-medium">
                        Bounded recovery halted by policy stopping rules. Human compliance review logged.
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Drawer Footer Actions */}
        <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60 flex items-center justify-between gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-xs font-semibold transition-colors"
          >
            Close Detail
          </button>

          {payment.payment_status === 'RECOVERABLE' && (
            <button
              onClick={() => onAttemptRecovery(payment.transaction_id)}
              className="flex-1 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-xs font-bold shadow-sm flex items-center justify-center space-x-2 transition-all"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>Execute Bounded Recovery</span>
            </button>
          )}
        </div>

      </div>

    </div>
  );
};
