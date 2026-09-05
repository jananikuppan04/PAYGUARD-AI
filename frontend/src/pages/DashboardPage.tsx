import React, { useState } from 'react';
import { AnalyticsSummary, PaymentRecord } from '../types/payment';
import { KpiCard } from '../components/KpiCard';
import { 
  CreditCard, 
  CheckCircle2, 
  RefreshCw, 
  DollarSign, 
  TrendingUp, 
  ShieldAlert, 
  PieChart as PieIcon, 
  ArrowRight, 
  Calendar, 
  Clock, 
  Bot, 
  Sparkles,
  Zap
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

interface DashboardPageProps {
  analytics: AnalyticsSummary | null;
  payments: PaymentRecord[];
  onSelectPayment: (payment: PaymentRecord) => void;
  onNavigateTab: (tab: string) => void;
  onOpenSimulate?: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  analytics,
  payments,
  onSelectPayment,
  onNavigateTab,
  onOpenSimulate,
}) => {
  const [dateRange, setDateRange] = useState('7d');

  if (!analytics) {
    return (
      <div className="p-12 text-center text-zinc-500 font-mono text-xs">
        Loading PayGuard Intelligence Dashboard...
      </div>
    );
  }

  const categoryColors: Record<string, string> = {
    TECHNICAL: '#10b981',        // Emerald
    CUSTOMER_RELATED: '#f59e0b', // Amber
    RISK_RELATED: '#ef4444',     // Red
    NON_RECOVERABLE: '#71717a',  // Gray
  };

  const pieData = Object.entries(analytics.failure_category_breakdown).map(([key, val]) => ({
    name: key.replace('_', ' '),
    value: val,
    color: categoryColors[key] || '#8b5cf6',
  }));

  const methodData = Object.entries(analytics.payment_method_breakdown).map(([key, data]) => ({
    method: key,
    failed: data.failed,
    recovered_revenue: data.recovered_revenue,
  }));

  const recoveryQueueOpportunities = payments.filter((p) => p.payment_status === 'RECOVERABLE');

  return (
    <div className="space-y-6 pb-12 animate-fade-in text-zinc-900 dark:text-zinc-100">
      
      {/* 1. Page Header (Clean White / Dark Minimal) */}
      <div className="p-6 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono uppercase font-bold text-zinc-400">Explainable AI Revenue Recovery Agent</span>
              <span className="text-zinc-300 dark:text-zinc-700">•</span>
              <span className="text-[10px] font-mono font-semibold text-emerald-600 dark:text-emerald-400">Live Agent Engine Active</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 mt-1">
              PayGuard AI Control Center
            </h1>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
              Detect revenue at risk. Diagnose the cause. Recover money intelligently with bounded agent guardrails.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => onNavigateTab('batch-operations')}
              className="px-3.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-xs font-bold shadow-sm flex items-center space-x-1.5 transition-all"
            >
              <Zap className="h-3.5 w-3.5 text-purple-400 dark:text-purple-600" />
              <span>Recovery Operations (500)</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>

            <button
              onClick={() => onNavigateTab('recovery-queue')}
              className="px-3.5 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 text-xs font-bold shadow-sm flex items-center space-x-1.5 transition-all"
            >
              <span>Queue ({recoveryQueueOpportunities.length})</span>
            </button>
          </div>
        </div>

        {/* Agent Loop Banner */}
        <div className="pt-3 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between overflow-x-auto text-[11px] font-mono font-semibold text-zinc-500 dark:text-zinc-400">
          <span className="text-zinc-900 dark:text-zinc-100">CORE LOOP:</span>
          <span>1. Detect</span>
          <span>→</span>
          <span>2. Diagnose</span>
          <span>→</span>
          <span>3. Decide</span>
          <span>→</span>
          <span className="text-purple-600 dark:text-purple-400">4. Check Rules</span>
          <span>→</span>
          <span className="text-zinc-900 dark:text-zinc-100">5. Execute</span>
          <span>→</span>
          <span className="text-emerald-600 dark:text-emerald-400 font-bold">6. Verify & Measure</span>
          <span>→</span>
          <span>7. Audit</span>
        </div>
      </div>

      {/* 2. KPI Summary Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Recovered Revenue"
          value={`₹${analytics.recovered_revenue.toLocaleString('en-IN')}`}
          subtext={`From ${analytics.recent_recovery_attempts.length} verified attempts`}
          icon={DollarSign}
          color="emerald"
          trend="+18.4%"
          trendUp={true}
        />
        <KpiCard
          title="Revenue At Risk"
          value={`₹${analytics.revenue_at_risk.toLocaleString('en-IN')}`}
          subtext={`${analytics.recovery_opportunities} actionable opportunities`}
          icon={ShieldAlert}
          color="amber"
        />
        <KpiCard
          title="Active Recovery Rate"
          value={`${analytics.recovery_rate}%`}
          subtext={`Avg recovery time: ${analytics.avg_recovery_time_minutes} min`}
          icon={TrendingUp}
          color="blue"
          trend="+4.2%"
          trendUp={true}
        />
        <KpiCard
          title="Payment Success Rate"
          value={`${analytics.payment_success_rate}%`}
          subtext={`${analytics.successful_payments} / ${analytics.total_attempts} total attempts`}
          icon={CheckCircle2}
          color="purple"
        />
      </div>

      {/* 3. Payment Failure Analytics Charts (2-Column Grid) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Payment Failure Category Distribution */}
        <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-700 dark:text-zinc-300 flex items-center gap-2">
              <PieIcon className="h-4 w-4 text-zinc-900 dark:text-zinc-100" /> Payment Failure Category Distribution
            </h3>
            <span className="text-[11px] font-mono text-zinc-400">Total Failed: {analytics.failed_payments}</span>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', color: '#fff', borderRadius: 8, fontSize: 12 }} />
                <Legend formatter={(value) => <span className="text-xs font-medium text-zinc-700 dark:text-zinc-300 capitalize">{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recovered Revenue by Payment Method */}
        <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-700 dark:text-zinc-300 flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-emerald-600 dark:text-emerald-400" /> Recovered Revenue by Payment Method
            </h3>
            <span className="text-[11px] font-mono text-zinc-400">INR (₹)</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={methodData} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                <XAxis dataKey="method" stroke="#a1a1aa" fontSize={11} />
                <YAxis stroke="#a1a1aa" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', color: '#fff', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="recovered_revenue" fill="#10b981" radius={[4, 4, 0, 0]} name="Recovered Revenue (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* 4. Actionable Recovery Queue Preview (Wide Operational Section) */}
      <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
          <div className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4 text-amber-500" />
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
              Recovery Queue Preview
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
              {recoveryQueueOpportunities.length} Actionable Items
            </span>
          </div>

          <button
            onClick={() => onNavigateTab('recovery-queue')}
            className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 hover:underline flex items-center space-x-1"
          >
            <span>View full queue</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Operational Preview Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-zinc-700 dark:text-zinc-300">
            <thead className="bg-zinc-50 dark:bg-zinc-900/60 text-zinc-400 uppercase tracking-wider font-mono text-[10px] border-b border-zinc-200 dark:border-zinc-800">
              <tr>
                <th className="py-2.5 px-3">Transaction ID</th>
                <th className="py-2.5 px-3">Decline Reason</th>
                <th className="py-2.5 px-3">Amount</th>
                <th className="py-2.5 px-3">Risk Level</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800/80">
              {recoveryQueueOpportunities.slice(0, 5).map((p) => (
                <tr
                  key={p.transaction_id}
                  onClick={() => onSelectPayment(p)}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors cursor-pointer"
                >
                  <td className="py-2.5 px-3 font-mono font-bold text-zinc-900 dark:text-zinc-100">
                    {p.transaction_id}
                  </td>
                  <td className="py-2.5 px-3 font-medium text-zinc-800 dark:text-zinc-200 max-w-xs truncate">
                    {p.failure_reason}
                  </td>
                  <td className="py-2.5 px-3 font-bold font-mono text-zinc-900 dark:text-zinc-100">
                    ₹{p.amount.toLocaleString('en-IN')}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px]">
                    <span className={`px-2 py-0.5 rounded ${
                      p.risk_level === 'HIGH' || p.risk_level === 'CRITICAL' ? 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 font-bold' :
                      p.risk_level === 'MEDIUM' ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 font-semibold' :
                      'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
                    }`}>
                      {p.risk_level} ({p.risk_score})
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-bold">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                      Eligible
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectPayment(p);
                      }}
                      className="px-3 py-1 rounded bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-[11px] font-bold transition-colors"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. AI Risk Insights & Recent Recovery Activity (2-Column Grid) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* AI Risk Insights */}
        <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <Bot className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-900 dark:text-zinc-100">
              AI Risk & Recovery Insights
            </h3>
          </div>

          <div className="space-y-2.5 text-xs text-zinc-600 dark:text-zinc-400">
            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 space-y-1">
              <span className="font-bold text-zinc-900 dark:text-zinc-100 block">High Technical Recovery Success</span>
              <p className="text-[11px] leading-relaxed">
                96% of Code 91 issuer timeouts were successfully recovered via automated Smart Retry after a 15-minute delay window.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800 space-y-1">
              <span className="font-bold text-zinc-900 dark:text-zinc-100 block">Low Risk Customer Reminders</span>
              <p className="text-[11px] leading-relaxed">
                Code 51 insufficient funds for customers with tenure &gt; 6 months yielded ₹1,48,000 recovered following automated WhatsApp payment link reminders.
              </p>
            </div>
          </div>
        </div>

        {/* Recent Recovery Activity Log */}
        <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-zinc-500" />
              <h3 className="text-xs font-bold uppercase tracking-wider font-mono text-zinc-900 dark:text-zinc-100">
                Recent Recovery Execution Activity
              </h3>
            </div>
            <button
              onClick={() => onNavigateTab('payments')}
              className="text-[11px] text-zinc-500 hover:text-zinc-900 dark:hover:text-white font-medium"
            >
              All Activity →
            </button>
          </div>

          <div className="space-y-2 text-xs">
            {analytics.recent_recovery_attempts.slice(0, 4).map((att, idx) => (
              <div
                key={idx}
                onClick={() => {
                  const target = payments.find((p) => p.transaction_id === att.transaction_id);
                  if (target) onSelectPayment(target);
                }}
                className="p-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800/80 flex items-center justify-between cursor-pointer hover:border-zinc-400 transition-colors"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-zinc-900 dark:text-zinc-100">{att.transaction_id}</span>
                    <span className="text-[10px] text-zinc-500">• {att.customer_name}</span>
                  </div>
                  <p className="text-[11px] text-zinc-500 mt-0.5">{att.action_taken}</p>
                </div>

                <div className="text-right">
                  <span className="font-mono font-bold text-zinc-900 dark:text-zinc-100 block">
                    ₹{att.amount.toLocaleString('en-IN')}
                  </span>
                  <span className={`px-1.5 py-0.5 rounded font-mono font-bold text-[9px] ${
                    att.outcome === 'SUCCESS' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300' : 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300'
                  }`}>
                    {att.outcome}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
