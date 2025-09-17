'use client';

import React from 'react';
import { 
  MessageSquare, 
  FileText, 
  History, 
  Settings, 
  X,
  Upload,
  Search,
  BarChart3
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentView: string;
  onViewChange: (view: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, currentView, onViewChange }) => {
  const menuItems = [
    {
      id: 'chat',
      label: 'Chat',
      icon: MessageSquare,
      description: 'Ask questions about your documents'
    },
    {
      id: 'documents',
      label: 'Documents',
      icon: FileText,
      description: 'Manage your documents'
    },
    {
      id: 'history',
      label: 'Query History',
      icon: History,
      description: 'View past queries and answers'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      description: 'Configure your preferences'
    }
  ];

  const quickActions = [
    {
      id: 'upload',
      label: 'Upload Document',
      icon: Upload,
      action: () => onViewChange('documents')
    },
    {
      id: 'search',
      label: 'Quick Search',
      icon: Search,
      action: () => onViewChange('chat')
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      action: () => console.log('Analytics clicked')
    }
  ];

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out z-50
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 md:static md:shadow-none
      `}>
        <div className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Knowledge Assistant
            </h2>
            <button
              onClick={onClose}
              className="md:hidden p-1 rounded-md hover:bg-gray-100"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>
          
          {/* Navigation */}
          <nav className="space-y-2 mb-8">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => onViewChange(item.id)}
                  className={`
                    w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors
                    ${isActive 
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500' 
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <div>
                    <div className="font-medium">{item.label}</div>
                    <div className="text-xs text-gray-500">{item.description}</div>
                  </div>
                </button>
              );
            })}
          </nav>
          
          {/* Quick Actions */}
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {quickActions.map((action) => {
                const Icon = action.icon;
                
                return (
                  <button
                    key={action.id}
                    onClick={action.action}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{action.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* System Status */}
          <div className="mt-8 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">System Status</span>
            </div>
            <div className="text-xs text-gray-600 space-y-1">
              <div>• Vector Store: Online</div>
              <div>• LLM Service: Online</div>
              <div>• Embedding Service: Online</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
