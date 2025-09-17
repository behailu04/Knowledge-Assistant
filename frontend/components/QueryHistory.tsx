'use client';

import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Clock, 
  MessageSquare, 
  FileText,
  ChevronDown,
  ChevronRight,
  Filter,
  Calendar
} from 'lucide-react';

interface QueryHistoryProps {
  onViewChange: (view: string) => void;
}

interface Query {
  query_id: string;
  question: string;
  answer: string;
  confidence: number;
  created_at: string;
  processing_time: number;
  hop_count: number;
  sources: Array<{
    doc_id: string;
    chunk_id: string;
    snippet: string;
    score: number;
  }>;
}

const QueryHistory: React.FC<QueryHistoryProps> = ({ onViewChange }) => {
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedQueries, setExpandedQueries] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchQueries();
  }, []);

  const fetchQueries = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockQueries: Query[] = [
        {
          query_id: 'q1',
          question: 'What are the main points in the contract?',
          answer: 'The contract outlines several key points including payment terms, delivery schedules, and quality standards...',
          confidence: 0.85,
          created_at: '2024-01-15T10:30:00Z',
          processing_time: 2.3,
          hop_count: 2,
          sources: [
            { doc_id: 'd1', chunk_id: 'c1', snippet: 'Contract terms...', score: 0.92 },
            { doc_id: 'd1', chunk_id: 'c2', snippet: 'Payment schedule...', score: 0.88 }
          ]
        },
        {
          query_id: 'q2',
          question: 'Which domains expire in the next 30 days?',
          answer: 'Based on the SSL certificate data, the following domains expire within 30 days: example.com (expires 2024-02-10), test.org (expires 2024-02-15)...',
          confidence: 0.92,
          created_at: '2024-01-15T09:15:00Z',
          processing_time: 1.8,
          hop_count: 3,
          sources: [
            { doc_id: 'd2', chunk_id: 'c3', snippet: 'SSL certificate data...', score: 0.95 },
            { doc_id: 'd2', chunk_id: 'c4', snippet: 'Domain expiration dates...', score: 0.89 }
          ]
        },
        {
          query_id: 'q3',
          question: 'Compare the terms in documents A and B',
          answer: 'After analyzing both documents, here are the key differences: Document A has stricter payment terms (30 days vs 45 days), while Document B includes additional quality assurance clauses...',
          confidence: 0.78,
          created_at: '2024-01-14T16:45:00Z',
          processing_time: 4.2,
          hop_count: 4,
          sources: [
            { doc_id: 'd1', chunk_id: 'c5', snippet: 'Document A terms...', score: 0.87 },
            { doc_id: 'd3', chunk_id: 'c6', snippet: 'Document B terms...', score: 0.84 }
          ]
        }
      ];
      
      setQueries(mockQueries);
    } catch (error) {
      console.error('Error fetching queries:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleQuery = (queryId: string) => {
    const newExpanded = new Set(expandedQueries);
    if (newExpanded.has(queryId)) {
      newExpanded.delete(queryId);
    } else {
      newExpanded.add(queryId);
    }
    setExpandedQueries(newExpanded);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredQueries = queries.filter(query => {
    const matchesSearch = query.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         query.answer.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesFilter = true;
    if (filter === 'high-confidence') {
      matchesFilter = query.confidence >= 0.8;
    } else if (filter === 'multi-hop') {
      matchesFilter = query.hop_count > 1;
    }
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading query history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2 flex items-center space-x-2">
          <History className="w-6 h-6" />
          <span>Query History</span>
        </h2>
        <p className="text-gray-600">
          View and analyze your past queries and their results
        </p>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search queries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Queries</option>
                <option value="high-confidence">High Confidence</option>
                <option value="multi-hop">Multi-hop</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Query List */}
      <div className="space-y-4">
        {filteredQueries.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No queries found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || filter !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Start by asking questions about your documents'
              }
            </p>
            {!searchTerm && filter === 'all' && (
              <button
                onClick={() => onViewChange('chat')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start Chatting
              </button>
            )}
          </div>
        ) : (
          filteredQueries.map((query) => {
            const isExpanded = expandedQueries.has(query.query_id);
            
            return (
              <div key={query.query_id} className="query-item">
                <div 
                  className="cursor-pointer"
                  onClick={() => toggleQuery(query.query_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 mb-1 line-clamp-2">
                        {query.question}
                      </h3>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatDate(query.created_at)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <span className={`font-medium ${getConfidenceColor(query.confidence)}`}>
                            {getConfidenceLabel(query.confidence)} ({Math.round(query.confidence * 100)}%)
                          </span>
                        </div>
                        {query.hop_count > 1 && (
                          <div className="flex items-center space-x-1">
                            <FileText className="w-3 h-3" />
                            <span>{query.hop_count} hops</span>
                          </div>
                        )}
                        <span>{query.processing_time}s</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>
                
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    {/* Answer */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Answer:</h4>
                      <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                        {query.answer}
                      </div>
                    </div>
                    
                    {/* Sources */}
                    {query.sources && query.sources.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">
                          Sources ({query.sources.length}):
                        </h4>
                        <div className="space-y-2">
                          {query.sources.map((source, index) => (
                            <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                              <div className="flex justify-between items-start">
                                <span className="text-gray-600">
                                  Document {source.doc_id?.slice(-8)} • Chunk {source.chunk_id?.slice(-8)}
                                </span>
                                <span className="text-gray-500">
                                  {Math.round(source.score * 100)}%
                                </span>
                              </div>
                              <div className="text-gray-700 mt-1">
                                {source.snippet}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Query Details */}
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>Query ID: {query.query_id}</div>
                      <div>Processing Time: {query.processing_time}s</div>
                      <div>Hops: {query.hop_count}</div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default QueryHistory;
