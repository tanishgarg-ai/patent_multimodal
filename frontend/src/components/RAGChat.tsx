import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MessageSquare } from 'lucide-react';
import { useChatContext } from '../context/ChatContext';
import { ChatMessage } from './ChatMessage';
import { analyzeInvention } from '../services/api';

export const RAGChat = () => {
  const { messages, setMessages, setAnalysisResult, isAnalyzing, setIsAnalyzing } = useChatContext();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAnalyzing]);

  const handleSend = async () => {
    if (!input.trim() || isAnalyzing) return;

    const userMessage = { id: Date.now().toString(), role: 'user' as const, content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsAnalyzing(true);

    try {
      const result = await analyzeInvention(userMessage.content);
      setAnalysisResult(result);
      
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai' as const,
        content: result.analysis_report || 'Analysis complete. Check the insights panel for details.',
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai' as const,
        content: 'Sorry, I encountered an error while analyzing your invention. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      <div className="p-4 border-b border-slate-800 flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-cyan-400" />
        <h2 className="text-lg font-semibold text-slate-100">Investigation Chat</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
            <MessageSquare className="w-12 h-12 text-slate-700" />
            <p className="text-center max-w-sm">
              Describe your invention here. I will analyze it against the uploaded patents and identify prior art.
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isAnalyzing && (
          <div className="flex items-center gap-3 text-slate-400 p-4 bg-slate-800/50 rounded-xl mr-8">
            <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
            <div className="text-sm flex flex-col">
              <span className="font-medium text-slate-300">Analyzing invention...</span>
              <span className="text-xs opacity-70">Searching patents & generating novelty assessment</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-slate-900 border-t border-slate-800">
        <div className="relative flex items-end gap-2 bg-slate-800 rounded-xl border border-slate-700 focus-within:border-cyan-500/50 transition-colors p-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your invention (e.g., 'My invention uses LiDAR and deep learning for drone navigation...')"
            className="flex-1 bg-transparent text-slate-200 placeholder-slate-500 resize-none outline-none max-h-32 min-h-[44px] py-2 px-2 text-sm"
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isAnalyzing}
            className="p-2.5 bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-900 rounded-lg transition-colors shrink-0 mb-0.5"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
