import { useState } from 'react';
import type { KnowledgeBase } from '../types';
import { Chat } from '../components/Chat';
import { DocumentList } from '../components/DocumentList';
import { Quiz } from './Quiz';

type Tab = 'chat' | 'documents' | 'quiz';

interface KnowledgeBasePageProps {
  kb: KnowledgeBase;
}

export function KnowledgeBasePage({ kb }: KnowledgeBasePageProps) {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'documents', label: 'Documents', icon: '📚' },
    { id: 'quiz', label: 'Quiz', icon: '📝' },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <h1 className="text-xl font-bold text-slate-800">{kb.name}</h1>
        {kb.description && (
          <p className="text-sm text-slate-500 mt-1">{kb.description}</p>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-slate-200 px-6">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-1 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' && <Chat kbId={kb.id} />}
        {activeTab === 'documents' && <DocumentList kbId={kb.id} />}
        {activeTab === 'quiz' && <Quiz kbId={kb.id} />}
      </div>
    </div>
  );
}
