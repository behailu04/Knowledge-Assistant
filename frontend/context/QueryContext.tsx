'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import axios from 'axios';

interface Message {
  id: number;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: any[];
  confidence?: number;
  reasoning_traces?: any[];
  hop_count?: number;
  processing_time?: number;
  error?: string;
}

interface QueryContextType {
  messages: Message[];
  currentQuery: any;
  sendMessage: (message: Omit<Message, 'id' | 'timestamp'>) => Promise<void>;
  clearMessages: () => void;
  setCurrentQuery: (query: any) => void;
}

const QueryContext = createContext<QueryContextType | undefined>(undefined);

export const useQuery = () => {
  const context = useContext(QueryContext);
  if (!context) {
    throw new Error('useQuery must be used within a QueryProvider');
  }
  return context;
};

export const QueryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuery, setCurrentQuery] = useState<any>(null);

  const sendMessage = useCallback(async (message: Omit<Message, 'id' | 'timestamp'>) => {
    const userMessage: Message = {
      ...message,
      id: Date.now(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await axios.post('/api/v1/query', {
        tenant_id: 'org_123',
        user_id: 'u_456',
        question: message.content,
        max_hops: 3,
        options: {
          use_cot: true,
          self_consistency_samples: 5
        }
      });

      const assistantMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
        sources: response.data.sources,
        confidence: response.data.confidence,
        reasoning_traces: response.data.reasoning_traces,
        hop_count: response.data.hop_count,
        processing_time: response.data.processing_time,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setCurrentQuery(response.data);

    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your query. Please try again.',
        timestamp: new Date(),
        error: error.response?.data?.detail || error.message,
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentQuery(null);
  }, []);

  return (
    <QueryContext.Provider value={{
      messages,
      currentQuery,
      sendMessage,
      clearMessages,
      setCurrentQuery,
    }}>
      {children}
    </QueryContext.Provider>
  );
};
