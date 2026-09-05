import React from 'react';
import { Shield, Play, Bot, Bell, Sun, Moon, CheckCircle2 } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  onOpenSimulate: () => void;
  onToggleAssistant: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  onOpenSimulate,
  onToggleAssistant,
  theme,
  onToggleTheme,
}) => {
  const getTabTitle = (tab: string) => {
    switch (tab) {
      case 'dashboard': return 'Executive Overview';
      case 'batch-operations': return 'Batch Recovery Operations';
      case 'payments': return 'Payment Intelligence';
      case 'recovery-queue': return 'Actionable Recovery Queue';
      case 'analytics': return 'Revenue Analytics';
      case 'evaluation': return 'Model & Agent Evaluation';
      case 'docs': return 'Architecture & Documentation';
      default: return 'Overview';
    }
  };

  return (
    <header className="h-16 bg-white dark:bg-[#09090b] border-b border-zinc-200 dark:border-zinc-800 sticky top-0 z-30 px-6 flex items-center justify-between transition-colors">
      
      {/* Left Title & Breadcrumb */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-zinc-400 dark:text-zinc-500 font-mono">PayGuard AI</span>
          <span className="text-zinc-300 dark:text-zinc-700">/</span>
          <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">
            {getTabTitle(activeTab)}
          </span>
        </div>
      </div>

      {/* Right Action Bar */}
      <div className="flex items-center space-x-3">
        
        {/* Status Indicator Pill */}
        <div className="hidden lg:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs font-medium">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-mono font-semibold">Live Engine Active</span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={onToggleTheme}
          className="h-9 w-9 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 flex items-center justify-center transition-colors"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </button>

        {/* Notification Bell */}
        <button
          className="h-9 w-9 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 flex items-center justify-center transition-colors relative"
          title="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-amber-500"></span>
        </button>

        {/* Ask AI Assistant Trigger */}
        <button
          onClick={onToggleAssistant}
          className="flex items-center space-x-2 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 text-xs font-semibold px-3 py-2 rounded-lg border border-zinc-200 dark:border-zinc-700 transition-colors"
        >
          <Bot className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          <span className="hidden sm:inline">Ask AI Assistant</span>
        </button>

        {/* Simulate Payment Failure Primary Button */}
        <button
          onClick={onOpenSimulate}
          className="flex items-center space-x-2 bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 text-xs font-semibold px-3.5 py-2 rounded-lg shadow-sm transition-all hover:scale-[1.01] active:scale-[0.99]"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          <span>Simulate Payment Failure</span>
        </button>

      </div>
    </header>
  );
};
