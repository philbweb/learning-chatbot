import type { KnowledgeBase } from '../types';

interface SidebarProps {
  knowledgeBases: KnowledgeBase[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
}

export function Sidebar({
  knowledgeBases,
  selectedId,
  onSelect,
  onCreate,
  onDelete,
}: SidebarProps) {
  return (
    <aside className="w-64 bg-slate-800 text-white flex flex-col">
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-xl font-bold">Learning Chatbot</h1>
      </div>

      <div className="p-4">
        <button
          onClick={onCreate}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
        >
          + New Knowledge Base
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2">
        <div className="text-xs uppercase text-slate-400 px-2 py-2">
          Knowledge Bases
        </div>
        {knowledgeBases.length === 0 ? (
          <p className="text-slate-400 text-sm px-2 py-4">
            No knowledge bases yet
          </p>
        ) : (
          <ul className="space-y-1">
            {knowledgeBases.map((kb) => (
              <li key={kb.id}>
                <button
                  onClick={() => onSelect(kb.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg flex items-center justify-between group transition-colors ${
                    selectedId === kb.id
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-300 hover:bg-slate-700/50'
                  }`}
                >
                  <span className="truncate">{kb.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm(`Delete "${kb.name}"?`)) {
                        onDelete(kb.id);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-400 p-1"
                    title="Delete"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </button>
              </li>
            ))}
          </ul>
        )}
      </nav>

      <div className="p-4 border-t border-slate-700 text-xs text-slate-400">
        <button
          onClick={() => onSelect(null)}
          className="hover:text-white transition-colors"
        >
          Back to Home
        </button>
      </div>
    </aside>
  );
}
