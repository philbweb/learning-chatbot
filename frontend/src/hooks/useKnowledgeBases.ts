import { useState, useEffect, useCallback } from 'react';
import type { KnowledgeBase, KnowledgeBaseCreate } from '../types';
import * as api from '../api/client';

export function useKnowledgeBases() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchKnowledgeBases = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getKnowledgeBases();
      setKnowledgeBases(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch knowledge bases');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchKnowledgeBases();
  }, [fetchKnowledgeBases]);

  const createKnowledgeBase = useCallback(async (data: KnowledgeBaseCreate) => {
    const kb = await api.createKnowledgeBase(data);
    setKnowledgeBases((prev) => [kb, ...prev]);
    return kb;
  }, []);

  const updateKnowledgeBase = useCallback(async (id: string, data: KnowledgeBaseCreate) => {
    const kb = await api.updateKnowledgeBase(id, data);
    setKnowledgeBases((prev) => prev.map((k) => (k.id === id ? kb : k)));
    return kb;
  }, []);

  const deleteKnowledgeBase = useCallback(async (id: string) => {
    await api.deleteKnowledgeBase(id);
    setKnowledgeBases((prev) => prev.filter((k) => k.id !== id));
  }, []);

  return {
    knowledgeBases,
    loading,
    error,
    refresh: fetchKnowledgeBases,
    createKnowledgeBase,
    updateKnowledgeBase,
    deleteKnowledgeBase,
  };
}
