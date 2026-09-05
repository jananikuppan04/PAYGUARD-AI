import React from 'react';
import { PaymentRecord } from '../types/payment';
import { PaymentTable } from '../components/PaymentTable';
import { CreditCard, Shield, Clock, CheckCircle2, XCircle } from 'lucide-react';

interface PaymentsPageProps {
  payments: PaymentRecord[];
  onSelectPayment: (payment: PaymentRecord) => void;
  onAttemptRecovery: (payment: PaymentRecord) => void;
}

export const PaymentsPage: React.FC<PaymentsPageProps> = ({ payments, onSelectPayment, onAttemptRecovery }) => {
  const recoverableCount = payments.filter((p) => p.payment_status === 'RECOVERABLE').length;
  const recoveredCount = payments.filter((p) => p.payment_status === 'RECOVERED').length;
  const failedCount = payments.filter((p) => p.payment_status === 'FAILED').length;

  return (
    <div className="space-y-6 pb-12 animate-fade-in text-zinc-900 dark:text-zinc-100">
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-mono uppercase font-bold text-zinc-400">Payment Audit Trail</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 mt-1">
            Payment Intelligence Explorer
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
            Browse payment events, inspect diagnosis evidence, and evaluate AI recovery recommendations.
          </p>
        </div>

        {/* Counter Pills */}
        <div className="flex items-center space-x-2 text-xs font-mono font-semibold">
          <span className="px-3 py-1 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
            {recoverableCount} Recoverable
          </span>
          <span className="px-3 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            {recoveredCount} Recovered
          </span>
          <span className="px-3 py-1 rounded-lg bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800">
            {failedCount} Failed
          </span>
        </div>
      </div>

      <PaymentTable
        payments={payments}
        onSelectPayment={onSelectPayment}
        onAttemptRecovery={onAttemptRecovery}
      />
    </div>
  );
};
