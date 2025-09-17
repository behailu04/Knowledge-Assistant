'use client';

import React, { useState } from 'react';
import { Brain, ChevronDown, ChevronRight, CheckCircle, Clock } from 'lucide-react';

interface ReasoningTrace {
  trace_id: string;
  steps: string[];
  vote_score: number;
  reasoning: string;
  answer?: string;
}

interface ReasoningTraceProps {
  traces: ReasoningTrace[];
}

const ReasoningTraceComponent: React.FC<ReasoningTraceProps> = ({ traces }) => {
  const [expandedTraces, setExpandedTraces] = useState<Set<number>>(new Set());

  const toggleTrace = (index: number) => {
    const newExpanded = new Set(expandedTraces);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedTraces(newExpanded);
  };

  const getVoteColor = (voteScore: number) => {
    if (voteScore >= 0.8) return 'text-green-600';
    if (voteScore >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getVoteLabel = (voteScore: number) => {
    if (voteScore >= 0.8) return 'High';
    if (voteScore >= 0.6) return 'Medium';
    return 'Low';
  };

  if (!traces || traces.length === 0) {
    return null;
  }

  return (
    <div className="mt-4">
      <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center space-x-2">
        <Brain className="w-4 h-4" />
        <span>Reasoning Traces ({traces.length})</span>
      </h4>
      
      <div className="space-y-2">
        {traces.map((trace, index) => {
          const isExpanded = expandedTraces.has(index);
          const voteColor = getVoteColor(trace.vote_score);
          const voteLabel = getVoteLabel(trace.vote_score);
          
          return (
            <div key={trace.trace_id || index} className="reasoning-trace">
              <div 
                className="cursor-pointer"
                onClick={() => toggleTrace(index)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    )}
                    <span className="text-sm font-medium">
                      Trace {index + 1}
                    </span>
                    {trace.steps && trace.steps.length > 0 && (
                      <span className="text-xs text-gray-500">
                        • {trace.steps.length} steps
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs font-medium ${voteColor}`}>
                      {voteLabel} ({Math.round(trace.vote_score * 100)}%)
                    </span>
                    <CheckCircle className="w-3 h-3 text-gray-400" />
                  </div>
                </div>
              </div>
              
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-blue-200">
                  {/* Reasoning Steps */}
                  {trace.steps && trace.steps.length > 0 && (
                    <div className="mb-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">Steps:</div>
                      <div className="space-y-2">
                        {trace.steps.map((step, stepIndex) => (
                          <div key={stepIndex} className="flex items-start space-x-2">
                            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs font-medium text-blue-700 flex-shrink-0">
                              {stepIndex + 1}
                            </div>
                            <div className="text-sm text-gray-700 flex-1">
                              {step}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Full Reasoning Text */}
                  {trace.reasoning && (
                    <div className="mb-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">Reasoning:</div>
                      <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded border-l-4 border-blue-300">
                        {trace.reasoning}
                      </div>
                    </div>
                  )}
                  
                  {/* Answer */}
                  {trace.answer && (
                    <div className="mb-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">Answer:</div>
                      <div className="text-sm text-gray-800 bg-gray-50 p-3 rounded">
                        {trace.answer}
                      </div>
                    </div>
                  )}
                  
                  {/* Trace Metadata */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Trace ID: {trace.trace_id?.slice(-8) || 'Unknown'}</span>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>Vote Score: {trace.vote_score?.toFixed(3) || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Summary */}
      {traces.length > 1 && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-sm font-medium text-gray-700 mb-2">Self-Consistency Summary</div>
          <div className="text-xs text-gray-600">
            Generated {traces.length} reasoning traces with different approaches. 
            The final answer is based on consensus from these traces.
          </div>
        </div>
      )}
    </div>
  );
};

export default ReasoningTraceComponent;
