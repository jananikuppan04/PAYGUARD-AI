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
    <div className="p-5 rounded-2xl bg-[#111111] border border-[#1e1e1e] shadow-xs hover:shadow-sm hover:border-zinc-700 transition-all flex flex-col justify-between min-h-[145px]">
      
      {/* Top Header Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="h-6 w-6 rounded-full bg-zinc-800/90 border border-zinc-700 flex items-center justify-center text-zinc-300 text-xs font-medium">
            <Icon className="h-3.5 w-3.5" />
          </div>
          <span className="text-xs font-semibold text-zinc-400">{title}</span>
        </div>

        {trend && (
          <div className="flex items-center space-x-0.5 text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full bg-emerald-950/40 text-emerald-400 border border-emerald-800/60">
            {trendUp ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            <span>{trend}</span>
          </div>
        )}
      </div>

      {/* Main Metric Value */}
      <div className="mt-3">
        <h2 className="text-[26px] font-bold tracking-tight text-white font-sans leading-none">
          {value}
        </h2>
        {subtext && (
          <p className="text-xs text-zinc-400 mt-2 font-normal">
            {subtext}
          </p>
        )}
      </div>

    </div>
  );
};
