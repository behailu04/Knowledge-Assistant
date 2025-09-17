'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import ChatInterface from '@/components/ChatInterface';
import DocumentManager from '@/components/DocumentManager';
import QueryHistory from '@/components/QueryHistory';
import Settings from '@/components/Settings';
import { QueryProvider } from '@/context/QueryContext';
import { DocumentProvider } from '@/context/DocumentContext';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('chat');

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'chat':
        return <ChatInterface onViewChange={setCurrentView} />;
      case 'documents':
        return <DocumentManager onViewChange={setCurrentView} />;
      case 'history':
        return <QueryHistory onViewChange={setCurrentView} />;
      case 'settings':
        return <Settings onViewChange={setCurrentView} />;
      default:
        return <ChatInterface onViewChange={setCurrentView} />;
    }
  };

  return (
    <QueryProvider>
      <DocumentProvider>
        <div className="min-h-screen bg-gray-50">
          <Header 
            onToggleSidebar={toggleSidebar}
            currentView={currentView}
            onViewChange={setCurrentView}
          />
          
          <div className="flex">
            <Sidebar 
              isOpen={sidebarOpen}
              onClose={() => setSidebarOpen(false)}
              currentView={currentView}
              onViewChange={setCurrentView}
            />
            
            <main className={`flex-1 transition-all duration-300 ${
              sidebarOpen ? 'ml-64' : 'ml-0'
            }`}>
              {renderCurrentView()}
            </main>
          </div>
        </div>
      </DocumentProvider>
    </QueryProvider>
  );
}
