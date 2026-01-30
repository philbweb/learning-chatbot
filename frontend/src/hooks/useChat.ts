import { useState, useCallback, useRef, useEffect } from 'react';
import type { ChatSource, SSEEvent } from '../types';
import * as api from '../api/client';

interface LocalMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
  isStreaming?: boolean;
}

export function useChat(kbId: string | null) {
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<(() => void) | null>(null);

  // Load chat history when KB changes
  useEffect(() => {
    if (!kbId) {
      setMessages([]);
      return;
    }

    const loadHistory = async () => {
      try {
        const history = await api.getChatHistory(kbId);
        setMessages(
          history.map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
          }))
        );
      } catch (e) {
        console.error('Failed to load chat history:', e);
      }
    };

    loadHistory();
  }, [kbId]);

  const sendMessage = useCallback(
    async (content: string, useStreaming = true) => {
      if (!kbId || !content.trim()) return;

      setError(null);
      setLoading(true);

      // Add user message
      const userMsg: LocalMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: content.trim(),
      };
      setMessages((prev) => [...prev, userMsg]);

      if (useStreaming) {
        // Streaming response
        const assistantId = `assistant-${Date.now()}`;
        const assistantMsg: LocalMessage = {
          id: assistantId,
          role: 'assistant',
          content: '',
          isStreaming: true,
        };
        setMessages((prev) => [...prev, assistantMsg]);

        let sources: ChatSource[] | undefined;

        abortRef.current = api.streamChat(
          kbId,
          { message: content, include_sources: true },
          (event: SSEEvent) => {
            if (event.type === 'sources') {
              sources = event.data;
            } else if (event.type === 'chunk') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: m.content + event.data }
                    : m
                )
              );
            } else if (event.type === 'done') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, isStreaming: false, sources }
                    : m
                )
              );
              setLoading(false);
            }
          },
          (err) => {
            setError(err.message);
            setLoading(false);
          }
        );
      } else {
        // Non-streaming response
        try {
          const response = await api.sendMessage(kbId, {
            message: content,
            include_sources: true,
          });

          const assistantMsg: LocalMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: response.message,
            sources: response.sources || undefined,
          };
          setMessages((prev) => [...prev, assistantMsg]);
        } catch (e) {
          setError(e instanceof Error ? e.message : 'Failed to send message');
        } finally {
          setLoading(false);
        }
      }
    },
    [kbId]
  );

  const clearHistory = useCallback(async () => {
    if (!kbId) return;

    try {
      await api.clearChatHistory(kbId);
      setMessages([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to clear history');
    }
  }, [kbId]);

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setLoading(false);
      setMessages((prev) =>
        prev.map((m) => (m.isStreaming ? { ...m, isStreaming: false } : m))
      );
    }
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory,
    stopStreaming,
  };
}
