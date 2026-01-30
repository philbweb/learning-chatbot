# CLAUDE.md - Learning Chatbot Project Context

## Project Purpose

A desktop learning application that allows users to:
- Create knowledge bases from documents (PDF, MD, TXT, DOCX)
- Ask questions and get RAG-powered answers
- Generate and take quizzes based on the content

## Current State

### Completed
- [x] Backend scaffolding (FastAPI + SQLite + aiosqlite)
- [x] Knowledge base CRUD API
- [x] Document upload and chunking (mock mode)
- [x] Chat endpoint with SSE streaming (mock mode)
- [x] Quiz generation endpoint (mock mode)
- [x] Repository pattern for data access
- [x] Frontend scaffolding (Tauri + React + TypeScript + Tailwind)
- [x] Knowledge base management UI
- [x] Document upload with drag-drop
- [x] Chat interface with SSE streaming
- [x] Quiz generation and taking UI

### Not Started
- [ ] Real RAG integration (embeddings, vector search, LLM)
- [ ] Tests (pytest for backend, vitest for frontend)
- [ ] Production build and packaging

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.11+ |
| Database | SQLite + aiosqlite |
| Vector Store | ChromaDB (planned) |
| Embeddings | sentence-transformers (planned) |
| LLM | Anthropic Claude API |
| Frontend | Tauri v2 + React 18 + TypeScript |
| Styling | Tailwind CSS |
| Build | Vite |

## Project Structure

```
learning-chatbot/
├── CLAUDE.md
├── README.md
├── backend/
│   ├── main.py                    # FastAPI app with lifespan
│   ├── config.py                  # Pydantic Settings
│   ├── requirements.txt
│   ├── .env.example
│   ├── api/
│   │   ├── chat.py               # RAG Q&A + SSE streaming
│   │   ├── knowledge_bases.py    # KB CRUD + document upload
│   │   └── quizzes.py            # Quiz CRUD + generation
│   ├── models/                   # Pydantic schemas
│   ├── services/
│   │   ├── rag_engine.py         # Embeddings + retrieval + LLM
│   │   ├── document_ingest.py    # File → chunks
│   │   └── quiz_generator.py     # Quiz generation
│   └── db/
│       ├── database.py           # SQLite setup
│       └── repositories.py       # CRUD operations
└── frontend/
    ├── src-tauri/
    │   ├── tauri.conf.json       # Tauri config (window size, title)
    │   └── src/main.rs           # Rust backend
    ├── src/
    │   ├── App.tsx               # Main app with routing
    │   ├── api/client.ts         # Backend API client
    │   ├── components/
    │   │   ├── Layout.tsx        # App shell
    │   │   ├── Sidebar.tsx       # KB navigation
    │   │   ├── Chat.tsx          # Chat interface
    │   │   ├── ChatMessage.tsx   # Message bubbles
    │   │   ├── DocumentList.tsx  # Document management
    │   │   ├── FileUpload.tsx    # Drag-drop upload
    │   │   └── QuizView.tsx      # Quiz taking UI
    │   ├── pages/
    │   │   ├── Home.tsx          # Landing page
    │   │   ├── KnowledgeBase.tsx # KB detail with tabs
    │   │   └── Quiz.tsx          # Quiz list/generation
    │   ├── hooks/
    │   │   ├── useKnowledgeBases.ts
    │   │   ├── useChat.ts
    │   │   └── useQuiz.ts
    │   └── types/index.ts        # TypeScript interfaces
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.ts
```

## Key Decisions

1. **Mock mode by default** - Backend runs without ML models for development
2. **Repository pattern** - All DB access through repository classes
3. **SSE for chat streaming** - Real-time response streaming
4. **Tauri for desktop** - Cross-platform with small binary size
5. **No Redux** - React hooks sufficient for state management
6. **SQLite** - Simple, file-based, good for single-user desktop app
7. **Tab-based KB view** - Chat, Documents, Quiz as separate tabs

## Development Commands

```bash
# Backend
cd backend
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (web dev mode)
cd frontend
npm install
npm run dev          # Vite dev server on :1420

# Frontend (Tauri desktop mode - requires Rust)
npm run tauri dev    # Opens native window
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /api/knowledge-bases | List all KBs |
| POST | /api/knowledge-bases | Create KB |
| GET | /api/knowledge-bases/{id} | Get KB |
| PUT | /api/knowledge-bases/{id} | Update KB |
| DELETE | /api/knowledge-bases/{id} | Delete KB |
| GET | /api/knowledge-bases/{id}/documents | List documents |
| POST | /api/knowledge-bases/{id}/documents | Upload document |
| DELETE | /api/knowledge-bases/{id}/documents/{doc_id} | Delete document |
| POST | /api/chat/{kb_id} | Send message (non-streaming) |
| POST | /api/chat/{kb_id}/stream | Send message (SSE streaming) |
| GET | /api/chat/{kb_id}/history | Get chat history |
| DELETE | /api/chat/{kb_id}/history | Clear chat history |
| GET | /api/quizzes/{kb_id} | List quizzes |
| POST | /api/quizzes/{kb_id}/generate | Generate quiz |
| GET | /api/quizzes/{kb_id}/{quiz_id} | Get quiz |
| DELETE | /api/quizzes/{kb_id}/{quiz_id} | Delete quiz |

## Next Steps

1. **Install Rust** - Required for Tauri desktop builds
2. **Enable real RAG** - Set MOCK_MODE=false, add ANTHROPIC_API_KEY
3. **Add tests** - pytest for backend, vitest for frontend
4. **Production build** - `npm run tauri build` for desktop app
