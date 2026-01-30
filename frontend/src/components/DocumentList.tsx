import { useState, useEffect } from 'react';
import type { Document } from '../types';
import * as api from '../api/client';
import { FileUpload } from './FileUpload';

interface DocumentListProps {
  kbId: string;
}

export function DocumentList({ kbId }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const docs = await api.getDocuments(kbId);
      setDocuments(docs);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [kbId]);

  const handleUpload = async (file: File) => {
    try {
      setError(null);
      const doc = await api.uploadDocument(kbId, file);
      setDocuments((prev) => [doc, ...prev]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed');
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Delete this document?')) return;

    try {
      await api.deleteDocument(kbId, docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed');
    }
  };

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return 'Unknown size';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'md':
        return '📝';
      case 'txt':
        return '📃';
      case 'docx':
        return '📋';
      default:
        return '📎';
    }
  };

  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Documents</h3>

      <FileUpload onUpload={handleUpload} />

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg">
          {error}
        </div>
      )}

      {loading ? (
        <div className="mt-6 text-center text-slate-400">Loading...</div>
      ) : documents.length === 0 ? (
        <div className="mt-6 text-center text-slate-400">
          <p>No documents yet</p>
          <p className="text-sm">Upload PDF, Markdown, or text files</p>
        </div>
      ) : (
        <ul className="mt-6 space-y-2">
          {documents.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between p-3 bg-white rounded-lg border border-slate-200 hover:border-slate-300 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-2xl">{getFileIcon(doc.file_type)}</span>
                <div className="min-w-0">
                  <p className="font-medium text-slate-800 truncate">
                    {doc.filename}
                  </p>
                  <p className="text-xs text-slate-400">
                    {doc.file_type.toUpperCase()} • {formatFileSize(doc.file_size)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-slate-400 hover:text-red-500 p-2"
                title="Delete"
              >
                <svg
                  className="w-5 h-5"
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
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
