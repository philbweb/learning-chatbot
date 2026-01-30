import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { useChat } from '../hooks/useChat';

interface ChatProps {
  kbId: string;
}

export function Chat({ kbId }: ChatProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, loading, error, sendMessage, clearHistory, stopStreaming } = useChat(kbId);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    sendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-slate-100">
      {/* Header */}
      <div className="px-6 py-4 bg-white border-b border-slate-200 flex items-center justify-between">
        <h2 className="font-semibold text-slate-800">Chat</h2>
        <button
          onClick={() => {
            if (confirm('Clear chat history?')) {
              clearHistory();
            }
          }}
          className="text-sm text-slate-500 hover:text-slate-700"
        >
          Clear History
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-slate-400 py-12">
            <p className="text-lg">Ask a question about your documents</p>
            <p className="text-sm mt-2">
              Upload documents first, then start chatting
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              sources={msg.sources}
              isStreaming={msg.isStreaming}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="px-6 py-2 bg-red-50 text-red-600 text-sm">{error}</div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-slate-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          {loading ? (
            <button
              type="button"
              onClick={stopStreaming}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Stop
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
