// Types matching backend Pydantic models

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBaseCreate {
  name: string;
  description?: string;
}

export interface Document {
  id: string;
  knowledge_base_id: string;
  filename: string;
  file_type: string;
  file_size: number | null;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  knowledge_base_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: string[] | null;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  include_sources?: boolean;
}

export interface ChatResponse {
  message: string;
  sources: ChatSource[] | null;
}

export interface ChatSource {
  content: string;
  document_id: string;
  score?: number;
}

export interface Quiz {
  id: string;
  knowledge_base_id: string;
  title: string;
  description: string | null;
  questions: QuizQuestion[];
  created_at: string;
}

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  question: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer';
  options: string[] | null;
  correct_answer: string;
  explanation: string | null;
  difficulty: string;
  created_at: string;
}

export interface QuizGenerateRequest {
  num_questions?: number;
  difficulty?: string;
  question_types?: string[];
}

// SSE event types
export interface SSESourcesEvent {
  type: 'sources';
  data: ChatSource[];
}

export interface SSEChunkEvent {
  type: 'chunk';
  data: string;
}

export interface SSEDoneEvent {
  type: 'done';
}

export type SSEEvent = SSESourcesEvent | SSEChunkEvent | SSEDoneEvent;
