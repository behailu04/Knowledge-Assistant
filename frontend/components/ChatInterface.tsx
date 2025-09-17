'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, FileText, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';
import { useQuery } from '@/context/QueryContext';
import MessageBubble from './MessageBubble';
import SourceList from './SourceList';
import ReasoningTrace from './ReasoningTrace';

interface ChatInterfaceProps {
  onViewChange: (view: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onViewChange }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { 
    messages, 
    sendMessage, 
    clearMessages,
    currentQuery,
    setCurrentQuery 
  } = useQuery();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      type: 'user' as const,
      content: input.trim(),
    };

    setInput('');
    setIsLoading(true);

    try {
      await sendMessage(userMessage);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Chat with your documents</h2>
            <p className="text-sm text-gray-600">
              Ask questions about your uploaded documents. I can help with multi-hop reasoning and provide evidence-backed answers.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={clearMessages}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
            >
              Clear Chat
            </button>
            <button
              onClick={() => onViewChange('documents')}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
            >
              Upload Documents
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Knowledge Assistant
            </h3>
            <p className="text-gray-600 mb-6 max-w-md">
              Start by uploading some documents, then ask me questions about them. 
              I can perform multi-hop reasoning and provide evidence-backed answers.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <h4 className="font-medium text-gray-900 mb-2">Example Questions</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• "What are the main points in the contract?"</li>
                  <li>• "Which domains expire in the next 30 days?"</li>
                  <li>• "Compare the terms in documents A and B"</li>
                </ul>
              </div>
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <h4 className="font-medium text-gray-900 mb-2">Features</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Multi-hop reasoning</li>
                  <li>• Evidence verification</li>
                  <li>• Source citations</li>
                  <li>• Confidence scoring</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="animate-fade-in">
              <MessageBubble message={message} />
              
              {/* Show sources and reasoning for assistant messages */}
              {message.type === 'assistant' && message.sources && (
                <div className="ml-12 mt-2 space-y-3">
                  {/* Confidence Score */}
                  {message.confidence !== undefined && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">Confidence:</span>
                      <span className={`confidence-badge ${getConfidenceColor(message.confidence)}`}>
                        {getConfidenceLabel(message.confidence)} ({Math.round(message.confidence * 100)}%)
                      </span>
                    </div>
                  )}
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <SourceList sources={message.sources} />
                  )}
                  
                  {/* Reasoning Traces */}
                  {message.reasoning_traces && message.reasoning_traces.length > 0 && (
                    <ReasoningTrace traces={message.reasoning_traces} />
                  )}
                  
                  {/* Processing Info */}
                  {message.processing_time && (
                    <div className="text-xs text-gray-500">
                      Processed in {message.processing_time.toFixed(2)}s
                      {message.hop_count && message.hop_count > 1 && ` • ${message.hop_count} hops`}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-600 animate-fade-in">
            <Loader className="w-4 h-4 animate-spin" />
            <span>Thinking...</span>
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <form onSubmit={handleSubmit} className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Send</span>
          </button>
        </form>
        
        <div className="mt-2 text-xs text-gray-500">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
