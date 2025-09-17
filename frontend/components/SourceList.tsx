'use client';

import React, { useState } from 'react';
import { ExternalLink, FileText, ChevronDown, ChevronRight } from 'lucide-react';

interface Source {
  doc_id: string;
  chunk_id: string;
  snippet: string;
  score: number;
  heading?: string;
  metadata?: Record<string, any>;
}

interface SourceListProps {
  sources: Source[];
}

const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

  const toggleSource = (index: number) => {
    const newExpanded = new Set(expandedSources);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSources(newExpanded);
  };

  const getConfidenceClass = (score: number) => {
    if (score >= 0.8) return 'high-confidence';
    if (score >= 0.6) return 'medium-confidence';
    return 'low-confidence';
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4">
      <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center space-x-2">
        <FileText className="w-4 h-4" />
        <span>Sources ({sources.length})</span>
      </h4>
      
      <div className="space-y-2">
        {sources.map((source, index) => {
          const isExpanded = expandedSources.has(index);
          const confidenceClass = getConfidenceClass(source.score);
          const confidenceColor = getConfidenceColor(source.score);
          const confidenceLabel = getConfidenceLabel(source.score);
          
          return (
            <div key={index} className={`source-item ${confidenceClass}`}>
              <div 
                className="cursor-pointer"
                onClick={() => toggleSource(index)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    )}
                    <span className="text-sm font-medium">
                      Document {source.doc_id?.slice(-8) || 'Unknown'}
                    </span>
                    {source.heading && (
                      <span className="text-xs text-gray-500">
                        • {source.heading}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs font-medium ${confidenceColor}`}>
                      {confidenceLabel} ({Math.round(source.score * 100)}%)
                    </span>
                    <ExternalLink className="w-3 h-3 text-gray-400" />
                  </div>
                </div>
              </div>
              
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-sm text-gray-700 leading-relaxed">
                    {source.snippet}
                  </div>
                  
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                    <span>Chunk ID: {source.chunk_id?.slice(-8) || 'Unknown'}</span>
                    <span>Score: {source.score?.toFixed(3) || 'N/A'}</span>
                  </div>
                  
                  {source.metadata && Object.keys(source.metadata).length > 0 && (
                    <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                      <div className="font-medium text-gray-700 mb-1">Metadata:</div>
                      <div className="space-y-1">
                        {Object.entries(source.metadata).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-600">{key}:</span>
                            <span className="text-gray-800">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SourceList;
