import React, { useState } from 'react';
import { X, Play, Shield, CheckCircle2, AlertTriangle, ArrowRight, RefreshCw, Zap } from 'lucide-react';
import { PaymentRecord } from '../types/payment';

interface SimulatePaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSimulate: (data: { amount: number; payment_method: any; scenario: string }) => Promise<void>;
}

export const SimulatePaymentModal: React.FC<SimulatePaymentModalProps> = ({
  isOpen,
  onClose,
  onSimulate,
}) => {
  const [amount, setAmount] = useState<number>(2499);
  const [method, setMethod] = useState<string>('CARD');
  const [scenario, setScenario] = useState<string>('TECHNICAL_51');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onSimulate({
        amount: Number(amount),
        payment_method: method,
        scenario,
      });
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const steps = [
    { num: 1, title: 'Detect' },
    { num: 2, title: 'Ingest' },
    { num: 3, title: 'AI Diagnose' },
    { num: 4, title: 'Eligibility' },
    { num: 5, title: 'Policy Rules' },
    { num: 6, title: 'Execute' },
    { num: 7, title: 'Reconcile' },
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-2xl overflow-hidden animate-fade-in text-zinc-900 dark:text-zinc-100">
        
        {/* Header */}
        <div className="p-5 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-900/60">
          <div>
            <div className="flex items-center space-x-2">
              <Play className="h-4 w-4 text-zinc-900 dark:text-zinc-100" />
              <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100">
                Simulate Payment Failure Workflow
              </h3>
            </div>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Interactive 7-step payment failure, risk diagnosis, and recovery agent execution.
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-500 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Step Indicator Bar */}
        <div className="px-5 py-3 border-b border-zinc-200 dark:border-zinc-800/60 bg-zinc-100/50 dark:bg-zinc-950/50 flex items-center justify-between text-[10px] font-mono text-zinc-400">
          {steps.map((s, idx) => (
            <React.Fragment key={s.num}>
              <div className={`flex items-center space-x-1 ${s.num === 1 ? 'text-zinc-900 dark:text-zinc-100 font-bold' : ''}`}>
                <span className={`h-4 w-4 rounded-full flex items-center justify-center text-[9px] ${
                  s.num === 1 ? 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 font-bold' : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
                }`}>
                  {s.num}
                </span>
                <span className="hidden sm:inline">{s.title}</span>
              </div>
              {idx < steps.length - 1 && <span className="text-zinc-300 dark:text-zinc-700">→</span>}
            </React.Fragment>
          ))}
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          
          {/* Step 1: Payment Input */}
          <div className="space-y-3">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider font-mono text-zinc-600 dark:text-zinc-400 mb-1">
                Transaction Amount (INR ₹)
              </label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                min={1}
                required
                className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 font-mono text-sm focus:outline-none focus:border-zinc-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider font-mono text-zinc-600 dark:text-zinc-400 mb-1">
                  Payment Method
                </label>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none"
                >
                  <option value="CARD">Credit / Debit Card</option>
                  <option value="UPI">UPI Transfer</option>
                  <option value="NETBANKING">Netbanking</option>
                  <option value="WALLET">Mobile Wallet</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider font-mono text-zinc-600 dark:text-zinc-400 mb-1">
                  Decline Scenario
                </label>
                <select
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none"
                >
                  <option value="TECHNICAL_51">Code 51: Insufficient Funds (Customer)</option>
                  <option value="TECHNICAL_91">Code 91: Issuer Timeout (Technical)</option>
                  <option value="FRAUD_HIGH">Code 05: High Risk Fraud Signal</option>
                  <option value="NON_RECOVERABLE_14">Code 14: Invalid Card Number (Permanent)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Workflow Step Explanation Card */}
          <div className="p-3.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800/80 space-y-1">
            <span className="text-[10px] uppercase font-bold font-mono text-zinc-400 block">Expected AI Processing</span>
            <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed">
              Upon simulation, PayGuard AI will ingest the event, run continuous XGBoost/LightGBM risk scoring, extract SHAP attributions, generate a 5-point explanation, and add an actionable item to the Recovery Queue.
            </p>
          </div>

          {/* Footer Actions */}
          <div className="pt-3 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 font-semibold transition-colors"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 font-bold shadow-sm flex items-center space-x-2 transition-all disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Simulating Event...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Trigger Failure Simulation</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
};
