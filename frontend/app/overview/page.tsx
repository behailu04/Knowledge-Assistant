'use client';

import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';

// Mock data for the dashboard
const mockData = {
  totalQueries: 1247,
  totalDocuments: 89,
  activeUsers: 23,
  avgResponseTime: 1.2,
  successRate: 94.5,
  monthlyQueries: [
    { month: 'Jan', queries: 120, documents: 15 },
    { month: 'Feb', queries: 180, documents: 22 },
    { month: 'Mar', queries: 250, documents: 28 },
    { month: 'Apr', queries: 320, documents: 35 },
    { month: 'May', queries: 280, documents: 31 },
    { month: 'Jun', queries: 197, documents: 25 }
  ],
  queryTypes: [
    { name: 'Simple RAG', value: 45, color: '#8884d8' },
    { name: 'Multi-hop', value: 30, color: '#82ca9d' },
    { name: 'Self-consistency', value: 25, color: '#ffc658' }
  ],
  hourlyQueries: [
    { hour: '00:00', queries: 12 },
    { hour: '02:00', queries: 8 },
    { hour: '04:00', queries: 5 },
    { hour: '06:00', queries: 15 },
    { hour: '08:00', queries: 45 },
    { hour: '10:00', queries: 78 },
    { hour: '12:00', queries: 92 },
    { hour: '14:00', queries: 85 },
    { hour: '16:00', queries: 67 },
    { hour: '18:00', queries: 43 },
    { hour: '20:00', queries: 28 },
    { hour: '22:00', queries: 18 }
  ],
  topDocuments: [
    { name: 'Product Manual v2.1', queries: 156, lastAccessed: '2 hours ago' },
    { name: 'API Documentation', queries: 134, lastAccessed: '1 hour ago' },
    { name: 'User Guide', queries: 98, lastAccessed: '3 hours ago' },
    { name: 'Troubleshooting Guide', queries: 87, lastAccessed: '5 hours ago' },
    { name: 'Release Notes', queries: 76, lastAccessed: '1 day ago' }
  ],
  recentQueries: [
    { id: 1, question: 'How do I configure the API?', timestamp: '2 min ago', type: 'Multi-hop', confidence: 0.92 },
    { id: 2, question: 'What are the system requirements?', timestamp: '5 min ago', type: 'Simple RAG', confidence: 0.88 },
    { id: 3, question: 'How to troubleshoot connection issues?', timestamp: '8 min ago', type: 'Self-consistency', confidence: 0.95 },
    { id: 4, question: 'What is the pricing model?', timestamp: '12 min ago', type: 'Simple RAG', confidence: 0.91 },
    { id: 5, question: 'How to integrate with our system?', timestamp: '15 min ago', type: 'Multi-hop', confidence: 0.89 }
  ]
};

const StatCard = ({ title, value, change, icon, color = 'blue' }: {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ReactNode;
  color?: string;
}) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500'
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm ${change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

const QueryTypeBadge = ({ type }: { type: string }) => {
  const colors = {
    'Simple RAG': 'bg-blue-100 text-blue-800',
    'Multi-hop': 'bg-green-100 text-green-800',
    'Self-consistency': 'bg-purple-100 text-purple-800'
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
      {type}
    </span>
  );
};

export default function OverviewPage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Knowledge Assistant Dashboard</h1>
              <p className="text-gray-600 mt-1">Real-time analytics and insights</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleString()}
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Refresh Data
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Queries"
            value={mockData.totalQueries.toLocaleString()}
            change="+12% from last month"
            icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
            color="blue"
          />
          <StatCard
            title="Documents Processed"
            value={mockData.totalDocuments}
            change="+8% from last month"
            icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
            color="green"
          />
          <StatCard
            title="Active Users"
            value={mockData.activeUsers}
            change="+5% from last week"
            icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" /></svg>}
            color="purple"
          />
          <StatCard
            title="Avg Response Time"
            value={`${mockData.avgResponseTime}s`}
            change="-15% from last month"
            icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="orange"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Monthly Queries Chart */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Query Volume</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={mockData.monthlyQueries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="queries" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Query Types Distribution */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Query Types Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={mockData.queryTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {mockData.queryTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hourly Activity and Top Documents */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Hourly Activity */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Query Activity</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockData.hourlyQueries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="queries" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Top Documents */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Accessed Documents</h3>
            <div className="space-y-4">
              {mockData.topDocuments.map((doc, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{doc.name}</h4>
                    <p className="text-sm text-gray-500">Last accessed: {doc.lastAccessed}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{doc.queries}</p>
                    <p className="text-sm text-gray-500">queries</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Queries */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Queries</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Question
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mockData.recentQueries.map((query) => (
                  <tr key={query.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{query.question}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <QueryTypeBadge type={query.type} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${query.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{(query.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {query.timestamp}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
