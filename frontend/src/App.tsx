import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { PaymentsPage } from './pages/PaymentsPage';
import { RecoveryQueuePage } from './pages/RecoveryQueuePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { DocumentationPage } from './pages/DocumentationPage';
import { LoginPage } from './pages/LoginPage';
import { BatchOperationsPage } from './pages/BatchOperationsPage';
import { PaymentDetailModal } from './components/PaymentDetailModal';
import { SimulatePaymentModal } from './components/SimulatePaymentModal';
import { MerchantAssistantDrawer } from './components/MerchantAssistantDrawer';
import { PaymentRecord, AnalyticsSummary } from './types/payment';
import { api } from './services/api';

import { Zap } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [selectedPayment, setSelectedPayment] = useState<PaymentRecord | null>(null);
  const [isSimulateOpen, setIsSimulateOpen] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>("Live Payment Event Broadcasted (₹2999)");
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(api.isAuthenticated());
  
  // Theme & Sidebar States
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Apply dark mode class to html document element
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Show login screen if unauthenticated
  if (!isAuthenticated) {
    return <LoginPage onAuthSuccess={() => setIsAuthenticated(true)} />;
  }

  const refreshData = async () => {
    try {
      const [pList, aSummary] = await Promise.all([
        api.getPayments(),
        api.getAnalytics()
      ]);
      setPayments(pList);
      setAnalytics(aSummary);
    } catch (e) {
      console.error("Error refreshing data:", e);
    }
  };

  useEffect(() => {
    refreshData();

    // WebSocket connection for live payment events
    let ws: WebSocket | null = null;
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${window.location.host}/ws/payments`;
      ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'PAYMENT_EVENT') {
            showToast(`Live Event: ${data.data.message} (₹${data.data.amount})`);
            refreshData();
          }
        } catch (e) {}
      };
    } catch (e) {}

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleSimulatePayment = async (data: { amount: number; payment_method: any; scenario: string }) => {
    const newTxn = await api.simulatePayment(data);
    showToast(`Payment ${newTxn.transaction_id} Simulated: ${newTxn.payment_status}`);
    await refreshData();
    setSelectedPayment(newTxn);
  };

  const handleAttemptRecovery = async (transaction_id: string, actionOverride?: string) => {
    const res = await api.attemptRecovery(transaction_id, actionOverride);
    showToast(res.message);
    await refreshData();
    if (selectedPayment && selectedPayment.transaction_id === transaction_id) {
      const updated = await api.getPaymentById(transaction_id);
      setSelectedPayment(updated);
    }
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
  };

  const opportunities = payments.filter((p) => p.payment_status === 'RECOVERABLE');

  return (
    <div className={`min-h-screen bg-[#F8FAFC] dark:bg-[#0a0a0a] text-zinc-900 dark:text-zinc-100 flex flex-col font-sans transition-colors`}>
      
      {/* Toast Banner (Matches Screenshot) */}
      {toastMessage && (
        <div className="fixed top-20 right-8 z-50 bg-[#18181b] text-white font-medium text-xs px-4 py-2.5 rounded-lg shadow-2xl border border-zinc-700/80 flex items-center space-x-2 animate-fade-in font-sans">
          <Zap className="h-3.5 w-3.5 text-amber-400 fill-amber-400 shrink-0" />
          <span className="font-semibold text-[11px] tracking-tight">Live Event: {toastMessage}</span>
        </div>
      )}

      {/* Left Fixed Black Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        opportunityCount={opportunities.length}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        theme={theme}
        onToggleTheme={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        onLogout={handleLogout}
      />

      {/* Main Content Area Container (Padded left to accommodate fixed black sidebar) */}
      <div className={`flex-1 flex flex-col transition-all duration-200 ${isSidebarCollapsed ? 'pl-16' : 'pl-64'}`}>
        
        {/* Top Navbar */}
        <Navbar
          activeTab={activeTab}
          onOpenSimulate={() => setIsSimulateOpen(true)}
          onToggleAssistant={() => setIsAssistantOpen(!isAssistantOpen)}
          theme={theme}
          onToggleTheme={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        />

        {/* Dynamic Page Component */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              analytics={analytics}
              payments={payments}
              onSelectPayment={(p) => setSelectedPayment(p)}
              onNavigateTab={setActiveTab}
              onOpenSimulate={() => setIsSimulateOpen(true)}
            />
          )}

          {activeTab === 'batch-operations' && (
            <BatchOperationsPage
              onSelectPayment={(p) => setSelectedPayment(p)}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'payments' && (
            <PaymentsPage
              payments={payments}
              onSelectPayment={(p) => setSelectedPayment(p)}
              onAttemptRecovery={(p) => handleAttemptRecovery(p.transaction_id)}
            />
          )}

          {activeTab === 'recovery-queue' && (
            <RecoveryQueuePage
              opportunities={opportunities}
              onSelectPayment={(p) => setSelectedPayment(p)}
              onAttemptRecovery={(p) => handleAttemptRecovery(p.transaction_id)}
            />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsPage analytics={analytics} />
          )}

          {activeTab === 'evaluation' && (
            <EvaluationPage />
          )}

          {activeTab === 'docs' && (
            <DocumentationPage />
          )}
        </main>

      </div>

      {/* Modals & Drawers */}
      <PaymentDetailModal
        payment={selectedPayment}
        onClose={() => setSelectedPayment(null)}
        onAttemptRecovery={handleAttemptRecovery}
      />

      <SimulatePaymentModal
        isOpen={isSimulateOpen}
        onClose={() => setIsSimulateOpen(false)}
        onSimulate={handleSimulatePayment}
      />

      <MerchantAssistantDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        selectedTxnId={selectedPayment?.transaction_id}
      />

    </div>
  );
}

export default App;
