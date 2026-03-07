import React from 'react';
import { User, Bot } from 'lucide-react';
import { Message } from '../context/ChatContext';
import { motion } from 'motion/react';

export const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 p-4 rounded-xl ${
        isUser ? 'bg-slate-800/50 ml-8' : 'bg-slate-800 mr-8'
      }`}
    >
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? 'bg-cyan-500/20 text-cyan-400' : 'bg-orange-500/20 text-orange-400'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>
      <div className="flex-1 text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
        {message.content}
      </div>
    </motion.div>
  );
};
