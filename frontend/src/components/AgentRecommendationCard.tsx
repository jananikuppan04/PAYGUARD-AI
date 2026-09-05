import React from 'react';
import { PaymentRecord } from '../types/payment';
import { Bot, CheckCircle2, AlertTriangle, ArrowRight, Sparkles, TrendingUp } from 'lucide-react';

interface AgentRecommendationCardProps {
  payment: PaymentRecord;
  onExecute: (actionOverride?: string) => void;
  isExecuting?: boolean;
}

export const AgentRecommendationCard: React.FC<AgentRecommendationCardProps> = ({
  payment,
  onExecute,
  isExecuting,
}) => {
  const exp = payment.action_explanation;
  const isEligible = payment.recovery_eligible;

  return (
    <div className="rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-[#121215] p-5 shadow-sm space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-md bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 text-purple-600 dark:text-purple-400">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
              PayGuard Agent Recommendation
            </h4>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">Bounded AI Recovery Execution</p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 font-mono text-xs">
          <span className="text-zinc-400">Confidence:</span>
          <span className="font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 px-1.5 py-0.5 rounded text-[11px]">
            {Math.round(payment.confidence_score * 100)}%
          </span>
        </div>
      </div>

      {/* Main Recommended Action Box */}
      <div className="p-4 rounded-lg bg-zinc-900 dark:bg-zinc-950 text-white border border-zinc-800 flex items-start justify-between">
        <div>
          <span className="text-[10px] uppercase font-mono tracking-wider text-zinc-400 block">Recommended Next Best Action</span>
          <h3 className="text-sm font-bold text-zinc-100 mt-0.5">{payment.recommended_action}</h3>
        </div>
        {payment.estimated_recovery_value > 0 && (
          <div className="text-right">
            <span className="text-[10px] uppercase font-mono text-zinc-400 block">Est. Recovery</span>
            <p className="text-sm font-bold font-mono text-emerald-400">₹{payment.estimated_recovery_value.toLocaleString('en-IN')}</p>
          </div>
        )}
      </div>

      {/* 5-Point Explainability Breakdown */}
      {exp && (
        <div className="space-y-2 text-xs">
          <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
            <span className="font-mono text-[10px] uppercase font-bold text-zinc-400 block">1. Failure Diagnosis</span>
            <p className="text-zinc-700 dark:text-zinc-300 mt-0.5">{exp.why_failed}</p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
            <span className="font-mono text-[10px] uppercase font-bold text-zinc-400 block">2. Recovery Eligibility</span>
            <p className="text-zinc-700 dark:text-zinc-300 mt-0.5">{exp.eligibility_rationale}</p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
            <span className="font-mono text-[10px] uppercase font-bold text-zinc-400 block">3. Action Rationale</span>
            <p className="text-zinc-700 dark:text-zinc-300 mt-0.5">{exp.action_rationale}</p>
          </div>

          {exp.evidence_points && exp.evidence_points.length > 0 && (
            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800">
              <span className="font-mono text-[10px] uppercase font-bold text-zinc-400 block mb-1">4. Supporting Evidence</span>
              <div className="flex flex-wrap gap-1.5">
                {exp.evidence_points.map((pt, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-[11px] text-zinc-700 dark:text-zinc-300">
                    ✓ {pt}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <div>
              <span className="font-mono text-[10px] uppercase font-bold text-zinc-400 block">5. Target Outcome Metric</span>
              <p className="text-zinc-700 dark:text-zinc-300 text-[11px] mt-0.5">{exp.target_metric}</p>
            </div>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </div>
        </div>
      )}

      {/* Execution Control */}
      {isEligible && payment.payment_status === 'RECOVERABLE' ? (
        <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800 flex items-center">
          <button
            onClick={() => onExecute()}
            disabled={isExecuting}
            className="w-full bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 font-bold py-2.5 px-4 rounded-lg shadow-sm text-xs flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            {isExecuting ? (
              <span>Executing Recovery Strategy...</span>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4" />
                <span>Approve & Execute Recovery Action</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="p-3 rounded-lg bg-zinc-100 dark:bg-zinc-900 text-xs text-zinc-600 dark:text-zinc-400 flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" />
          <span>
            {payment.payment_status === 'RECOVERED'
              ? 'Payment recovered successfully.'
              : 'Automated execution disabled due to status or risk constraints.'}
          </span>
        </div>
      )}
    </div>
  );
};
