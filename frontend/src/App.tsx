import { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { useKnowledgeBases } from './hooks/useKnowledgeBases';
import * as api from './api/client';

function App() {
  const [selectedKbId, setSelectedKbId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [connected, setConnected] = useState<boolean | null>(null);

  const {
    knowledgeBases,
    loading,
    createKnowledgeBase,
    deleteKnowledgeBase,
  } = useKnowledgeBases();

  // Check backend connection
  useEffect(() => {
    api
      .checkHealth()
      .then(() => setConnected(true))
      .catch(() => setConnected(false));
  }, []);

  const selectedKb = knowledgeBases.find((kb) => kb.id === selectedKbId);

  const handleCreateKb = () => {
    setShowCreateModal(true);
  };

  const handleSubmitCreate = async (name: string, description: string) => {
    try {
      const kb = await createKnowledgeBase({ name, description });
      setSelectedKbId(kb.id);
      setShowCreateModal(false);
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to create knowledge base');
    }
  };

  const handleDeleteKb = async (id: string) => {
    try {
      await deleteKnowledgeBase(id);
      if (selectedKbId === id) {
        setSelectedKbId(null);
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete knowledge base');
    }
  };

  // Connection error
  if (connected === false) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center p-8">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-xl font-bold text-slate-800 mb-2">
            Backend Not Connected
          </h1>
          <p className="text-slate-600 mb-4">
            Make sure the backend server is running on port 8000
          </p>
          <code className="block bg-slate-800 text-green-400 p-3 rounded text-sm">
            cd backend && uvicorn main:app --reload
          </code>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Loading
  if (connected === null || loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Layout
        knowledgeBases={knowledgeBases}
        selectedKbId={selectedKbId}
        onSelectKb={setSelectedKbId}
        onCreateKb={handleCreateKb}
        onDeleteKb={handleDeleteKb}
      >
        {selectedKb ? (
          <KnowledgeBasePage kb={selectedKb} />
        ) : (
          <Home onCreateKb={handleCreateKb} />
        )}
      </Layout>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateKbModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleSubmitCreate}
        />
      )}
    </>
  );
}

function CreateKbModal({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: (name: string, description: string) => void;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onSubmit(name.trim(), description.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4">
        <h2 className="text-xl font-bold text-slate-800 mb-4">
          Create Knowledge Base
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Machine Learning Notes"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the content..."
              rows={3}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-slate-600 hover:text-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
