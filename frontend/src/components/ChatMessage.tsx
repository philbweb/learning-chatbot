import type { ChatSource } from '../types';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
  isStreaming?: boolean;
}

export function ChatMessage({ role, content, sources, isStreaming }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-white text-slate-800 shadow-sm border border-slate-200 rounded-bl-md'
        }`}
      >
        <div className="whitespace-pre-wrap">{content}</div>
        {isStreaming && (
          <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
        )}

        {sources && sources.length > 0 && (
          <details className="mt-3 text-sm">
            <summary className="cursor-pointer text-slate-500 hover:text-slate-700">
              Sources ({sources.length})
            </summary>
            <ul className="mt-2 space-y-2 text-xs text-slate-600">
              {sources.map((source, i) => (
                <li key={i} className="p-2 bg-slate-50 rounded border border-slate-200">
                  <p className="line-clamp-3">{source.content}</p>
                  {source.score && (
                    <p className="mt-1 text-slate-400">
                      Relevance: {Math.round(source.score * 100)}%
                    </p>
                  )}
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}
