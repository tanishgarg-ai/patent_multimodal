import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface Document {
  filename: string;
  status: string;
  chunks_added: number;
  patent_id: string;
  pdf_url: string;
}

export interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
}

export interface AnalysisResult {
  analysis_report: string;
  patents: any[];
  papers: any[];
  similarity_scores: any[];
  novelty_assessment: any;
  graph_data: any;
}

interface ChatContextType {
  documents: Document[];
  setDocuments: React.Dispatch<React.SetStateAction<Document[]>>;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  analysisResult: AnalysisResult | null;
  setAnalysisResult: React.Dispatch<React.SetStateAction<AnalysisResult | null>>;
  isAnalyzing: boolean;
  setIsAnalyzing: React.Dispatch<React.SetStateAction<boolean>>;
  selectedPdfUrl: string | null;
  setSelectedPdfUrl: React.Dispatch<React.SetStateAction<string | null>>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedPdfUrl, setSelectedPdfUrl] = useState<string | null>(null);

  return (
    <ChatContext.Provider
      value={{
        documents,
        setDocuments,
        messages,
        setMessages,
        analysisResult,
        setAnalysisResult,
        isAnalyzing,
        setIsAnalyzing,
        selectedPdfUrl,
        setSelectedPdfUrl,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};
