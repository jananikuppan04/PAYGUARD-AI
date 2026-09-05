import React from 'react';
import { LucideIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  color?: 'emerald' | 'amber' | 'blue' | 'purple' | 'red';
  trend?: string;
  trendUp?: boolean;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  trend,
  trendUp = true,
}) => {
  return (
    <div className="p-5 rounded-xl bg-white dark:bg-[#121215] border border-zinc-200 dark:border-zinc-800 shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-all flex flex-col justify-between space-y-3">
      
      {/* Top Header Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="h-7 w-7 rounded-lg bg-zinc-100 dark:bg-zinc-800/80 border border-zinc-200 dark:border-zinc-700/60 flex items-center justify-center text-zinc-700 dark:text-zinc-300">
            <Icon className="h-3.5 w-3.5" />
          </div>
          <span className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">{title}</span>
        </div>

        {trend && (
          <div className={`flex items-center space-x-0.5 text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full ${
            trendUp 
              ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60' 
              : 'bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800/60'
          }`}>
            {trendUp ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            <span>{trend}</span>
          </div>
        )}
      </div>

      {/* Main Metric Value */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 font-mono">
          {value}
        </h2>
        {subtext && (
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1 font-medium">
            {subtext}
          </p>
        )}
      </div>

    </div>
  );
};
