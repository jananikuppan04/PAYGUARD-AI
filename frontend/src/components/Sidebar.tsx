import React from 'react';
import { 
  LayoutDashboard, 
  CreditCard, 
  RefreshCw, 
  BarChart3, 
  CheckCircle2, 
  FileText, 
  Shield, 
  ChevronLeft, 
  ChevronRight, 
  Sun, 
  Moon, 
  LogOut, 
  User, 
  Activity,
  Sliders
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  opportunityCount: number;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  opportunityCount,
  isCollapsed,
  onToggleCollapse,
  theme,
  onToggleTheme,
  onLogout,
}) => {
  const navSections = [
    {
      group: 'OVERVIEW',
      items: [
        { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard },
      ],
    },
    {
      group: 'PAYMENT OPERATIONS',
      items: [
        { id: 'batch-operations', label: 'Recovery Operations', icon: Activity },
        { id: 'payments', label: 'Payment Intelligence', icon: CreditCard },
        { id: 'recovery-queue', label: 'Recovery Queue', icon: RefreshCw, badge: opportunityCount },
        { id: 'analytics', label: 'Revenue Analytics', icon: BarChart3 },
      ],
    },
    {
      group: 'AI & TRUST',
      items: [
        { id: 'evaluation', label: 'Model & Agent Eval', icon: CheckCircle2 },
        { id: 'docs', label: 'Architecture & Docs', icon: FileText },
      ],
    },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 bottom-0 z-40 bg-[#09090b] text-white border-r border-zinc-800/80 flex flex-col justify-between transition-all duration-200 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Top Header & Brand */}
      <div className="flex flex-col">
        <div className="h-16 px-4 flex items-center justify-between border-b border-zinc-800/80">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="h-8 w-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0">
              <Shield className="h-4 w-4 text-white" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col truncate">
                <span className="font-bold text-sm tracking-tight text-white leading-none">
                  PayGuard <span className="text-zinc-400 font-normal">AI</span>
                </span>
                <span className="text-[10px] text-zinc-400 mt-1 font-mono">v2.0 Payment Intel</span>
              </div>
            )}
          </div>

          <button
            onClick={onToggleCollapse}
            className="h-7 w-7 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-800 flex items-center justify-center transition-colors"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Product Description */}
        {!isCollapsed && (
          <div className="px-4 py-3 border-b border-zinc-800/50 bg-zinc-950/50">
            <p className="text-[11px] text-zinc-400 leading-relaxed font-medium">
              Explainable Payment Failure Risk Diagnosis & Recovery Agent
            </p>
          </div>
        )}

        {/* Navigation Sections */}
        <div className="p-3 space-y-5 overflow-y-auto max-h-[calc(100vh-14rem)]">
          {navSections.map((section) => (
            <div key={section.group} className="space-y-1">
              {!isCollapsed && (
                <p className="px-2 text-[10px] uppercase font-bold tracking-wider text-zinc-400 mb-1.5 font-mono">
                  {section.group}
                </p>
              )}
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    title={isCollapsed ? item.label : undefined}
                    className={`w-full flex items-center ${
                      isCollapsed ? 'justify-center px-0' : 'justify-between px-3'
                    } py-2 rounded-md text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-zinc-800 text-white font-semibold border border-zinc-700/80 shadow-sm'
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
                    }`}
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-white' : 'text-zinc-400'}`} />
                      {!isCollapsed && <span className="truncate">{item.label}</span>}
                    </div>

                    {!isCollapsed && item.badge !== undefined && item.badge > 0 && (
                      <span className="ml-2 bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Footer Controls */}
      <div className="p-3 border-t border-zinc-800/80 space-y-2 bg-zinc-950/80">
        
        {/* System Status Pill */}
        {!isCollapsed ? (
          <div className="px-3 py-2 rounded-md bg-zinc-900 border border-zinc-800/80 flex items-center justify-between text-[11px]">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-zinc-300 font-medium">Recovery Engine</span>
            </div>
            <span className="text-emerald-400 font-mono text-[10px]">Active</span>
          </div>
        ) : (
          <div className="flex justify-center" title="Engine Status: Active">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>
        )}

        {/* Theme & User Profile Actions */}
        <div className="flex items-center justify-between gap-1 pt-1">
          <button
            onClick={onToggleTheme}
            className={`flex items-center space-x-2 text-xs text-zinc-400 hover:text-white hover:bg-zinc-800 ${
              isCollapsed ? 'p-2 justify-center w-full' : 'px-2 py-1.5 rounded-md'
            } transition-colors`}
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          >
            {theme === 'light' ? <Moon className="h-4 w-4 shrink-0" /> : <Sun className="h-4 w-4 shrink-0" />}
            {!isCollapsed && <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>}
          </button>

          {!isCollapsed && (
            <button
              onClick={onLogout}
              className="p-1.5 rounded-md text-zinc-400 hover:text-red-400 hover:bg-red-950/30 transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* User Profile Summary */}
        {!isCollapsed && (
          <div className="pt-2 border-t border-zinc-800/60 flex items-center space-x-2.5 px-1">
            <div className="h-7 w-7 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-bold text-white">
              MA
            </div>
            <div className="flex flex-col truncate text-[11px]">
              <span className="font-semibold text-zinc-200 truncate">Merchant Admin</span>
              <span className="text-zinc-400 text-[10px] truncate">admin@payguard.ai</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
