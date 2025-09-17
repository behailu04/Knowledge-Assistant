'use client';

import React from 'react';
import { Menu, Settings, MessageSquare, FileText, History } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar: () => void;
  currentView: string;
  onViewChange: (view: string) => void;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar, currentView, onViewChange }) => {
  const getViewIcon = (view: string) => {
    switch (view) {
      case 'chat':
        return <MessageSquare className="w-5 h-5" />;
      case 'documents':
        return <FileText className="w-5 h-5" />;
      case 'history':
        return <History className="w-5 h-5" />;
      case 'settings':
        return <Settings className="w-5 h-5" />;
      default:
        return <MessageSquare className="w-5 h-5" />;
    }
  };

  const getViewTitle = (view: string) => {
    switch (view) {
      case 'chat':
        return 'Chat';
      case 'documents':
        return 'Documents';
      case 'history':
        return 'Query History';
      case 'settings':
        return 'Settings';
      default:
        return 'Knowledge Assistant';
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-md hover:bg-gray-100 transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          
          <div className="flex items-center space-x-2">
            {getViewIcon(currentView)}
            <h1 className="text-xl font-semibold text-gray-900">
              {getViewTitle(currentView)}
            </h1>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>System Online</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Tenant: org_123</span>
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">U</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
