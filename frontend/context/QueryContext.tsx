'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { apiService, QueryRequest, QueryResponse } from '@/lib/api';

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
      const queryRequest: QueryRequest = {
        tenant_id: 'org_123',
        user_id: 'u_456',
        question: message.content,
        options: {
          use_multi_hop: true,
          use_self_consistency: true,
          use_cot: true,
          self_consistency_samples: 5,
          max_hops: 3
        }
      };

      const response: QueryResponse = await apiService.processQuery(queryRequest);

      const assistantMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence,
        reasoning_traces: response.reasoning_traces,
        hop_count: response.hop_count,
        processing_time: response.processing_time,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setCurrentQuery(response);

    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your query. Please try again.',
        timestamp: new Date(),
        error: error.message || 'Unknown error occurred',
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
