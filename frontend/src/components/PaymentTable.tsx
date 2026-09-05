import React, { useState } from 'react';
import { PaymentRecord } from '../types/payment';
import { Search, Filter, ChevronLeft, ChevronRight, Eye, RefreshCw, CheckCircle2, ShieldAlert } from 'lucide-react';

interface PaymentTableProps {
  payments: PaymentRecord[];
  onSelectPayment: (payment: PaymentRecord) => void;
  onAttemptRecovery?: (payment: PaymentRecord) => void;
  title?: string;
  showFilters?: boolean;
}

export const PaymentTable: React.FC<PaymentTableProps> = ({
  payments,
  onSelectPayment,
  onAttemptRecovery,
  title = "Payment Operations Directory",
  showFilters = true,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Filtering Logic
  const filtered = payments.filter((p) => {
    const matchesSearch = 
      p.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.failure_reason.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'ALL' || p.payment_status === statusFilter;
    const matchesCategory = categoryFilter === 'ALL' || p.failure_category === categoryFilter;

    return matchesSearch && matchesStatus && matchesCategory;
  });

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const paginated = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'RECOVERED':
        return 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60';
      case 'RECOVERABLE':
        return 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/60';
      case 'FAILED':
        return 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800/60';
      default:
        return 'bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border-zinc-200 dark:border-zinc-700';
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
      case 'HIGH':
        return 'bg-red-100 dark:bg-red-950/50 text-red-700 dark:text-red-300 font-bold';
      case 'MEDIUM':
        return 'bg-amber-100 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 font-semibold';
      default:
        return 'bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-400 font-medium';
    }
  };

  return (
    <div className="bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-sm overflow-hidden space-y-4">
      
      {/* Table Header & Controls */}
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{title}</h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
            Showing {filtered.length} total payment records
          </p>
        </div>

        {showFilters && (
          <div className="flex flex-wrap items-center gap-2">
            {/* Search Input */}
            <div className="relative">
              <Search className="h-3.5 w-3.5 absolute left-3 top-2.5 text-zinc-400" />
              <input
                type="text"
                placeholder="Search TXN ID or Customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:border-zinc-400"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="py-1.5 px-2.5 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-800 dark:text-zinc-200 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="RECOVERABLE">Eligible / Recoverable</option>
              <option value="RECOVERED">Recovered Revenue</option>
              <option value="FAILED">Failed</option>
            </select>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="py-1.5 px-2.5 text-xs bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-zinc-800 dark:text-zinc-200 focus:outline-none"
            >
              <option value="ALL">All Decline Types</option>
              <option value="TECHNICAL">Technical Failure</option>
              <option value="CUSTOMER_RELATED">Customer Related</option>
              <option value="RISK_RELATED">Risk Related</option>
              <option value="NON_RECOVERABLE">Non-Recoverable</option>
            </select>
          </div>
        )}
      </div>

      {/* Table Body */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-zinc-700 dark:text-zinc-300">
          <thead className="bg-zinc-50 dark:bg-zinc-900/60 text-zinc-500 dark:text-zinc-400 uppercase tracking-wider font-mono text-[10px] border-b border-zinc-200 dark:border-zinc-800">
            <tr>
              <th className="py-3 px-4">Transaction ID</th>
              <th className="py-3 px-4">Customer</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Failure Reason</th>
              <th className="py-3 px-4">Risk Level</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800/80">
            {paginated.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-zinc-400 text-xs">
                  No payment records matching search criteria.
                </td>
              </tr>
            ) : (
              paginated.map((p) => (
                <tr
                  key={p.transaction_id}
                  onClick={() => onSelectPayment(p)}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors cursor-pointer"
                >
                  <td className="py-3 px-4 font-mono font-bold text-zinc-900 dark:text-zinc-100">
                    {p.transaction_id}
                  </td>
                  <td className="py-3 px-4 font-medium text-zinc-800 dark:text-zinc-200">
                    {p.customer_name}
                  </td>
                  <td className="py-3 px-4 font-bold font-mono text-zinc-900 dark:text-zinc-100">
                    ₹{p.amount.toLocaleString('en-IN')}
                  </td>
                  <td className="py-3 px-4 max-w-xs truncate text-zinc-600 dark:text-zinc-400">
                    {p.failure_reason}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono ${getRiskBadge(p.risk_level)}`}>
                      {p.risk_level} ({p.risk_score})
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusBadge(p.payment_status)}`}>
                      {p.payment_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end space-x-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => onSelectPayment(p)}
                        className="px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 text-[11px] font-medium transition-colors"
                      >
                        Inspect
                      </button>

                      {p.payment_status === 'RECOVERABLE' && onAttemptRecovery && (
                        <button
                          onClick={() => onAttemptRecovery(p)}
                          className="px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-[11px] font-bold transition-colors"
                        >
                          Execute
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-3 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <div className="flex items-center space-x-1">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            className="p-1 rounded border border-zinc-200 dark:border-zinc-800 disabled:opacity-40 hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            className="p-1 rounded border border-zinc-200 dark:border-zinc-800 disabled:opacity-40 hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

    </div>
  );
};
