import React, { useState } from 'react';
import { X, Send, Bot, User, Sparkles, RefreshCw, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

interface MerchantAssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedTxnId?: string;
}

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  evidence?: string[];
  timestamp: string;
}

export const MerchantAssistantDrawer: React.FC<MerchantAssistantDrawerProps> = ({
  isOpen,
  onClose,
  selectedTxnId,
}) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: "Hello! I'm PayGuard AI Assistant. I can help analyze payment failure reasons, explain continuous risk scores, or list recoverable transactions. Ask me anything about your payment operations!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  if (!isOpen) return null;

  const suggestedPrompts = [
    'Why did payment success rate decrease?',
    'Show me highest-value recovery opportunities.',
    'Explain current revenue at risk.',
    'Which payment methods are failing most?',
    'Summarize today recovery performance.',
  ];

  const handleSend = async (queryText?: string) => {
    const query = queryText || input;
    if (!query.trim() || isLoading) return;

    const userMsg: Message = {
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput('');
    setIsLoading(true);

    try {
      const res = await api.askAssistant(query, selectedTxnId);
      const assistantMsg: Message = {
        sender: 'assistant',
        text: res.answer,
        evidence: res.evidence,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: 'Sorry, I encountered an error connecting to the PayGuard AI backend. Please verify backend server status.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white dark:bg-[#121215] border-l border-zinc-200 dark:border-zinc-800 h-full flex flex-col shadow-2xl animate-fade-in text-zinc-900 dark:text-zinc-100">
        
        {/* Header */}
        <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-900/60">
          <div className="flex items-center space-x-2">
            <div className="h-7 w-7 rounded-lg bg-purple-100 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 flex items-center justify-center text-purple-600 dark:text-purple-400">
              <Bot className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-zinc-900 dark:text-zinc-100">
                PayGuard AI Assistant
              </h3>
              <p className="text-[10px] text-zinc-500 dark:text-zinc-400 font-mono">
                100% Grounded Payment Intelligence
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-md text-zinc-400 hover:text-zinc-900 dark:hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Suggested Prompt Chips */}
        <div className="p-3 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/40">
          <p className="text-[10px] font-mono uppercase font-bold text-zinc-400 mb-1.5">
            Suggested Prompts
          </p>
          <div className="flex flex-wrap gap-1.5">
            {suggestedPrompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handleSend(p)}
                className="text-[10px] px-2 py-1 rounded bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors text-left"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Conversation Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex space-x-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'assistant' && (
                <div className="h-6 w-6 rounded-full bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 flex items-center justify-center shrink-0 text-[10px] font-bold">
                  AI
                </div>
              )}

              <div
                className={`max-w-[85%] p-3 rounded-xl ${
                  m.sender === 'user'
                    ? 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 font-medium'
                    : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border border-zinc-200 dark:border-zinc-800'
                }`}
              >
                <p className="leading-relaxed">{m.text}</p>

                {m.evidence && m.evidence.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-zinc-200 dark:border-zinc-800 text-[10px] text-zinc-500 space-y-1">
                    <span className="font-mono font-bold block text-zinc-400">GROUNDED EVIDENCE:</span>
                    {m.evidence.map((e, ei) => (
                      <p key={ei} className="font-mono text-zinc-600 dark:text-zinc-400">• {e}</p>
                    ))}
                  </div>
                )}

                <span className="block text-[9px] text-zinc-400 mt-1 text-right font-mono">
                  {m.timestamp}
                </span>
              </div>

              {m.sender === 'user' && (
                <div className="h-6 w-6 rounded-full bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 flex items-center justify-center shrink-0 text-[10px] font-bold">
                  U
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center space-x-2 text-zinc-400 text-xs italic">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              <span>Analyzing payment database facts...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-[#121215]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask about payments, risk, or revenue..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg text-xs text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:border-zinc-400"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-3 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 font-bold transition-colors disabled:opacity-40"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
};
