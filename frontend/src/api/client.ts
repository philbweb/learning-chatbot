// API client for backend communication

import type {
  KnowledgeBase,
  KnowledgeBaseCreate,
  Document,
  ChatMessage,
  ChatRequest,
  ChatResponse,
  Quiz,
  QuizGenerateRequest,
  SSEEvent,
} from '../types';

const API_BASE = import.meta.env.DEV
  ? 'http://localhost:8000'
  : 'http://localhost:8000'; // TODO: Update for production

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Health check
export async function checkHealth(): Promise<{ status: string; mock_mode: boolean }> {
  return request('/health');
}

// Knowledge Bases
export async function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  return request('/api/knowledge-bases');
}

export async function getKnowledgeBase(id: string): Promise<KnowledgeBase> {
  return request(`/api/knowledge-bases/${id}`);
}

export async function createKnowledgeBase(data: KnowledgeBaseCreate): Promise<KnowledgeBase> {
  return request('/api/knowledge-bases', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateKnowledgeBase(id: string, data: KnowledgeBaseCreate): Promise<KnowledgeBase> {
  return request(`/api/knowledge-bases/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteKnowledgeBase(id: string): Promise<void> {
  await request(`/api/knowledge-bases/${id}`, { method: 'DELETE' });
}

// Documents
export async function getDocuments(kbId: string): Promise<Document[]> {
  return request(`/api/knowledge-bases/${kbId}/documents`);
}

export async function uploadDocument(
  kbId: string,
  file: File,
  onProgress?: (percent: number) => void
): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('process', 'true');

  // Use XMLHttpRequest for progress tracking
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', () => reject(new Error('Upload failed')));

    xhr.open('POST', `${API_BASE}/api/knowledge-bases/${kbId}/documents`);
    xhr.send(formData);
  });
}

export async function deleteDocument(kbId: string, docId: string): Promise<void> {
  await request(`/api/knowledge-bases/${kbId}/documents/${docId}`, { method: 'DELETE' });
}

// Chat
export async function sendMessage(kbId: string, data: ChatRequest): Promise<ChatResponse> {
  return request(`/api/chat/${kbId}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function streamChat(
  kbId: string,
  data: ChatRequest,
  onEvent: (event: SSEEvent) => void,
  onError?: (error: Error) => void
): () => void {
  const controller = new AbortController();

  fetch(`${API_BASE}/api/chat/${kbId}/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6)) as SSEEvent;
              onEvent(event);
            } catch {
              // Ignore parse errors
            }
          }
        }
      }
    })
    .catch((error) => {
      if (error.name !== 'AbortError' && onError) {
        onError(error);
      }
    });

  return () => controller.abort();
}

export async function getChatHistory(kbId: string, limit = 50): Promise<ChatMessage[]> {
  return request(`/api/chat/${kbId}/history?limit=${limit}`);
}

export async function clearChatHistory(kbId: string): Promise<void> {
  await request(`/api/chat/${kbId}/history`, { method: 'DELETE' });
}

// Quizzes
export async function getQuizzes(kbId: string): Promise<Quiz[]> {
  return request(`/api/quizzes/${kbId}`);
}

export async function getQuiz(kbId: string, quizId: string): Promise<Quiz> {
  return request(`/api/quizzes/${kbId}/${quizId}`);
}

export async function generateQuiz(kbId: string, data: QuizGenerateRequest): Promise<Quiz> {
  return request(`/api/quizzes/${kbId}/generate`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteQuiz(kbId: string, quizId: string): Promise<void> {
  await request(`/api/quizzes/${kbId}/${quizId}`, { method: 'DELETE' });
}
