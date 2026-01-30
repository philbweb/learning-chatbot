import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import type { KnowledgeBase } from '../types';

interface LayoutProps {
  knowledgeBases: KnowledgeBase[];
  selectedKbId: string | null;
  onSelectKb: (id: string | null) => void;
  onCreateKb: () => void;
  onDeleteKb: (id: string) => void;
  children: ReactNode;
}

export function Layout({
  knowledgeBases,
  selectedKbId,
  onSelectKb,
  onCreateKb,
  onDeleteKb,
  children,
}: LayoutProps) {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar
        knowledgeBases={knowledgeBases}
        selectedId={selectedKbId}
        onSelect={onSelectKb}
        onCreate={onCreateKb}
        onDelete={onDeleteKb}
      />
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
}
