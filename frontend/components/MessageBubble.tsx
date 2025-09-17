'use client';

import React from 'react';
import { User, Bot, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

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

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const formatTime = (timestamp: Date) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getMessageIcon = () => {
    switch (message.type) {
      case 'user':
        return <User className="w-5 h-5" />;
      case 'assistant':
        return <Bot className="w-5 h-5" />;
      case 'system':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <Bot className="w-5 h-5" />;
    }
  };

  const getMessageStyles = () => {
    switch (message.type) {
      case 'user':
        return 'chat-message user';
      case 'assistant':
        return 'chat-message assistant';
      case 'system':
        return 'chat-message system';
      default:
        return 'chat-message assistant';
    }
  };

  return (
    <div className={getMessageStyles()}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            message.type === 'user' 
              ? 'bg-blue-500 text-white' 
              : message.type === 'system'
              ? 'bg-yellow-500 text-white'
              : 'bg-green-500 text-white'
          }`}>
            {getMessageIcon()}
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm font-medium text-gray-900">
              {message.type === 'user' ? 'You' : 
               message.type === 'system' ? 'System' : 'Assistant'}
            </span>
            <span className="text-xs text-gray-500">
              {formatTime(message.timestamp)}
            </span>
          </div>
          
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                code: ({ children }) => (
                  <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto text-sm">
                    {children}
                  </pre>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-700">
                    {children}
                  </blockquote>
                ),
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
          
          {/* Error message */}
          {message.error && (
            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4" />
                <span>Error: {message.error}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
