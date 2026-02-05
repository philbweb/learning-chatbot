# Learning Chatbot - Command Reference

## @ Commands (shortcuts)

| Command | Description |
|---------|-------------|
| *None defined yet* | |

## CLI Commands

### Backend

| Command | Description |
|---------|-------------|
| `cd backend && source .venv/bin/activate` | Activate virtual environment |
| `pip install -r requirements.txt` | Install Python dependencies |
| `uvicorn main:app --reload` | Start backend dev server |

### Frontend (Web Dev Mode)

| Command | Description |
|---------|-------------|
| `cd frontend && npm install` | Install frontend dependencies |
| `npm run dev` | Start Vite dev server on :1420 |

### Frontend (Tauri Desktop Mode)

| Command | Description |
|---------|-------------|
| `npm run tauri dev` | Opens native desktop window (requires Rust) |

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
