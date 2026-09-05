import React, { useState } from 'react';
import { PaymentRecord } from '../types/payment';
import { RefreshCw, CheckCircle2, Search, ArrowRight, ShieldAlert, Zap, Filter } from 'lucide-react';

interface RecoveryQueuePageProps {
  opportunities: PaymentRecord[];
  onSelectPayment: (payment: PaymentRecord) => void;
  onAttemptRecovery: (payment: PaymentRecord) => void;
}

export const RecoveryQueuePage: React.FC<RecoveryQueuePageProps> = ({
  opportunities,
  onSelectPayment,
  onAttemptRecovery,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const totalValue = opportunities.reduce((acc, p) => acc + p.estimated_recovery_value, 0);

  const filtered = opportunities.filter((p) => {
    const matchesSearch =
      p.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.failure_reason.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = priorityFilter === 'ALL' || p.recovery_priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  return (
    <div className="space-y-6 pb-12 animate-fade-in text-zinc-900 dark:text-zinc-100">
      
      {/* Page Header */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-1 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400">
              <RefreshCw className="h-4 w-4" />
            </span>
            <span className="text-xs font-bold uppercase font-mono tracking-wider text-amber-600 dark:text-amber-400">
              Actionable Recovery Queue
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 mt-1">
            High-Priority Payment Recovery Opportunities
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 max-w-xl">
            {opportunities.length} payments diagnosed as eligible for recovery. Review evidence and execute bounded AI actions.
          </p>
        </div>

        <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-4 rounded-xl text-right">
          <span className="text-[10px] uppercase font-mono font-bold text-zinc-400 block">Total Recovery Potential</span>
          <p className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5">
            ₹{totalValue.toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="h-3.5 w-3.5 absolute left-3 top-2.5 text-zinc-400" />
          <input
            type="text"
            placeholder="Search TXN ID or Customer..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none"
          />
        </div>

        <div className="flex items-center space-x-2 w-full md:w-auto">
          <span className="text-xs text-zinc-500 font-mono">Priority:</span>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="py-1.5 px-3 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 focus:outline-none"
          >
            <option value="ALL">All Priorities</option>
            <option value="HIGH">High Priority Only</option>
            <option value="MEDIUM">Medium Priority</option>
          </select>
        </div>
      </div>

      {/* Queue Items Grid */}
      {filtered.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 space-y-3 shadow-sm">
          <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto" />
          <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">Recovery Queue Clear!</h3>
          <p className="text-xs text-zinc-500 max-w-md mx-auto">
            All recoverable payments have either been processed or no matching opportunities exist.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((p) => (
            <div
              key={p.transaction_id}
              className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-600 transition-all space-y-4 shadow-sm flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-zinc-900 dark:text-zinc-100">{p.transaction_id}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        p.recovery_priority === 'HIGH' ? 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300' : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300'
                      }`}>
                        {p.recovery_priority} PRIORITY
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mt-1">{p.customer_name}</h3>
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400">{p.failure_reason}</p>
                  </div>

                  <div className="text-right font-mono">
                    <span className="text-[10px] uppercase text-zinc-400 block">Amount</span>
                    <p className="text-sm font-bold text-zinc-900 dark:text-zinc-100">₹{p.amount.toLocaleString('en-IN')}</p>
                    <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400">Est. ₹{p.estimated_recovery_value.toLocaleString('en-IN')}</span>
                  </div>
                </div>

                {/* Recommended Strategy Pill */}
                <div className="p-3 rounded-lg bg-zinc-900 dark:bg-zinc-950 text-white border border-zinc-800 text-xs">
                  <span className="text-[10px] uppercase font-mono text-zinc-400 block">Recommended Action</span>
                  <p className="font-bold text-zinc-100 mt-0.5">{p.recommended_action}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
                <button
                  onClick={() => onSelectPayment(p)}
                  className="text-xs font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white"
                >
                  Inspect Evidence →
                </button>

                <button
                  onClick={() => onAttemptRecovery(p)}
                  className="px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-xs font-bold shadow-sm flex items-center space-x-1.5 transition-all"
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Execute Recovery</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
