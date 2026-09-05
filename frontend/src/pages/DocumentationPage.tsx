import React from 'react';
import { FileText, Cpu, Database, Server, Terminal, Shield, Play } from 'lucide-react';

export const DocumentationPage: React.FC = () => {
  return (
    <div className="space-y-6 pb-12 text-xs text-zinc-700 dark:text-zinc-300 animate-fade-in">
      
      {/* Header */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm">
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-mono uppercase font-bold text-zinc-400">Technical Specifications</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 mt-1">
          PayGuard AI Architecture & Documentation
        </h1>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
          Razorpay AI Builder 2026 — Track 3: AI Revenue Recovery
        </p>
      </div>

      {/* Product Positioning */}
      <div className="p-5 rounded-xl bg-zinc-900 dark:bg-zinc-950 text-white border border-zinc-800 space-y-2">
        <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-400">Product Positioning Statement</h2>
        <blockquote className="p-3 bg-zinc-800/80 rounded-lg border-l-2 border-white text-zinc-200 font-medium leading-relaxed italic text-xs">
          “PayGuard AI is an explainable payment intelligence platform that helps merchants identify recoverable payment failures, recommend the next best recovery action, and measure actual revenue recovered.”
        </blockquote>
      </div>

      {/* Workflow Architecture Diagram */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
          <Server className="h-4 w-4 text-zinc-900 dark:text-zinc-100" /> Core Workflow Architecture
        </h2>

        <div className="p-4 rounded-lg bg-zinc-950 font-mono text-[11px] text-zinc-300 leading-relaxed overflow-x-auto border border-zinc-800">
{`Payment Event
    ↓
Payment Data + Customer History
    ↓
Failure Diagnosis (Technical / Customer / Risk / Non-Recoverable)
    ↓
Recovery Eligibility Assessment (Tenure, Past Success Rate, Risk Threshold)
    ↓
Next-Best-Action Recommendation Agent (Explainable 5-Point Rationale)
    ↓
Merchant Approval / Bounded Automation Trigger
    ↓
Recovery Attempt (Smart Retry / Account Updater / Reminder / Method Switch)
    ↓
Outcome Tracking & DB State Update
    ↓
Revenue Recovery Analytics & Reconciled Dashboard Metrics`}
        </div>
      </div>

      {/* End-to-End Demo Workflow */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
          <Play className="h-4 w-4 text-emerald-600 dark:text-emerald-400" /> Guided Demo Workflow
        </h2>

        <div className="space-y-2 font-medium">
          {[
            "1. Click 'Simulate Payment Failure' (e.g. Card decline / Insufficient funds / Network timeout).",
            "2. PayGuard identifies the exact failure reason and decline code.",
            "3. System determines whether recovery is possible (eligible vs non-recoverable).",
            "4. Agent generates Next-Best-Action recommendation with 5-point explainability.",
            "5. Merchant reviews recommendation card and evidence.",
            "6. Merchant clicks 'Execute Recovery' (Simulated execution).",
            "7. Outcome is recorded in backend database.",
            "8. Dashboard instantly updates Recovered Revenue and Active Recovery Rate.",
            "9. Merchant opens AI Assistant and asks 'Explain what happened with transaction TXN-xxxx'."
          ].map((step, idx) => (
            <div key={idx} className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 flex items-center space-x-2 text-zinc-800 dark:text-zinc-200">
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">✓</span>
              <span>{step}</span>
            </div>
          ))}
        </div>
      </div>

      {/* API Reference */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
          <Terminal className="h-4 w-4 text-purple-600 dark:text-purple-400" /> REST API Specification
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 font-mono text-[11px]">
          <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">GET</span> /api/v1/payments
          </div>
          <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">GET</span> /api/v1/payments/{"{id}"}
          </div>
          <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <span className="text-zinc-900 dark:text-zinc-100 font-bold">POST</span> /api/v1/payments/simulate
          </div>
          <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <span className="text-zinc-900 dark:text-zinc-100 font-bold">POST</span> /api/v1/recovery/{"{id}"}/execute
          </div>
          <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">GET</span> /api/v1/analytics/summary
          </div>
          <div className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <span className="text-zinc-900 dark:text-zinc-100 font-bold">POST</span> /api/v1/assistant/chat
          </div>
        </div>
      </div>

    </div>
  );
};
