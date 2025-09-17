'use client';

import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw, 
  Database, 
  Brain, 
  Zap,
  Shield,
  Bell,
  Palette,
  Globe
} from 'lucide-react';

interface SettingsProps {
  onViewChange: (view: string) => void;
}

const Settings: React.FC<SettingsProps> = ({ onViewChange }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    // General settings
    language: 'en',
    theme: 'light',
    notifications: true,
    
    // Query settings
    maxHops: 3,
    selfConsistencySamples: 5,
    useChainOfThought: true,
    
    // Model settings
    embeddingModel: 'sentence-transformers/all-MiniLM-L6-v2',
    llmProvider: 'openai',
    llmModel: 'gpt-3.5-turbo',
    
    // Retrieval settings
    topKRetrieval: 50,
    topNRerank: 5,
    similarityThreshold: 0.7,
    
    // Security settings
    enableAuditLogs: true,
    dataRetentionDays: 90,
    enableEncryption: true
  });

  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Settings saved:', settings);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'query', label: 'Query Settings', icon: Brain },
    { id: 'models', label: 'Models', icon: Database },
    { id: 'retrieval', label: 'Retrieval', icon: Zap },
    { id: 'security', label: 'Security', icon: Shield },
  ];

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={settings.language}
          onChange={(e) => setSettings({ ...settings, language: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Theme
        </label>
        <div className="flex space-x-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="light"
              checked={settings.theme === 'light'}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
              className="mr-2"
            />
            Light
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="dark"
              checked={settings.theme === 'dark'}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
              className="mr-2"
            />
            Dark
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="auto"
              checked={settings.theme === 'auto'}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
              className="mr-2"
            />
            Auto
          </label>
        </div>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.notifications}
            onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
            className="mr-2"
          />
          Enable notifications
        </label>
      </div>
    </div>
  );

  const renderQuerySettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Hops
        </label>
        <input
          type="number"
          min="1"
          max="5"
          value={settings.maxHops}
          onChange={(e) => setSettings({ ...settings, maxHops: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">Maximum number of reasoning hops for multi-hop queries</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Self-Consistency Samples
        </label>
        <input
          type="number"
          min="1"
          max="10"
          value={settings.selfConsistencySamples}
          onChange={(e) => setSettings({ ...settings, selfConsistencySamples: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">Number of reasoning traces for self-consistency</p>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.useChainOfThought}
            onChange={(e) => setSettings({ ...settings, useChainOfThought: e.target.checked })}
            className="mr-2"
          />
          Enable Chain-of-Thought reasoning
        </label>
      </div>
    </div>
  );

  const renderModelSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Embedding Model
        </label>
        <select
          value={settings.embeddingModel}
          onChange={(e) => setSettings({ ...settings, embeddingModel: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="sentence-transformers/all-MiniLM-L6-v2">all-MiniLM-L6-v2</option>
          <option value="sentence-transformers/all-mpnet-base-v2">all-mpnet-base-v2</option>
          <option value="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2">paraphrase-multilingual-MiniLM-L12-v2</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          LLM Provider
        </label>
        <select
          value={settings.llmProvider}
          onChange={(e) => setSettings({ ...settings, llmProvider: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="ollama">Ollama (Local)</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          LLM Model
        </label>
        <select
          value={settings.llmModel}
          onChange={(e) => setSettings({ ...settings, llmModel: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="llama2:7b">Llama 2 7B</option>
          <option value="llama2:13b">Llama 2 13B</option>
          <option value="codellama:7b">Code Llama 7B</option>
          <option value="mistral:7b">Mistral 7B</option>
          <option value="neural-chat:7b">Neural Chat 7B</option>
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="gpt-4">GPT-4</option>
        </select>
      </div>
    </div>
  );

  const renderRetrievalSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Top-K Retrieval
        </label>
        <input
          type="number"
          min="10"
          max="100"
          value={settings.topKRetrieval}
          onChange={(e) => setSettings({ ...settings, topKRetrieval: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">Number of initial candidates to retrieve</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Top-N Rerank
        </label>
        <input
          type="number"
          min="1"
          max="20"
          value={settings.topNRerank}
          onChange={(e) => setSettings({ ...settings, topNRerank: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">Number of final results after reranking</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Similarity Threshold
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={settings.similarityThreshold}
          onChange={(e) => setSettings({ ...settings, similarityThreshold: parseFloat(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0.0</span>
          <span>{settings.similarityThreshold}</span>
          <span>1.0</span>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.enableAuditLogs}
            onChange={(e) => setSettings({ ...settings, enableAuditLogs: e.target.checked })}
            className="mr-2"
          />
          Enable audit logs
        </label>
        <p className="text-xs text-gray-500 mt-1">Log all queries and document access for compliance</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Data Retention (Days)
        </label>
        <input
          type="number"
          min="1"
          max="365"
          value={settings.dataRetentionDays}
          onChange={(e) => setSettings({ ...settings, dataRetentionDays: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.enableEncryption}
            onChange={(e) => setSettings({ ...settings, enableEncryption: e.target.checked })}
            className="mr-2"
          />
          Enable encryption at rest
        </label>
        <p className="text-xs text-gray-500 mt-1">Encrypt stored documents and embeddings</p>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings();
      case 'query':
        return renderQuerySettings();
      case 'models':
        return renderModelSettings();
      case 'retrieval':
        return renderRetrievalSettings();
      case 'security':
        return renderSecuritySettings();
      default:
        return renderGeneralSettings();
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2 flex items-center space-x-2">
          <SettingsIcon className="w-6 h-6" />
          <span>Settings</span>
        </h2>
        <p className="text-gray-600">
          Configure your Knowledge Assistant preferences
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>

        {/* Actions */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 rounded-b-lg">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onViewChange('chat')}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {saving ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>{saving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
