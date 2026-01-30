# Learning Chatbot

A multi-knowledge-base learning platform inspired by [Linton AI's implementation](https://linton.ai/the-cofounder-of-openai-says-if-you-learn-whats-in-these-30-papers-you-ll-know-90-of-what-d142751c8bf4) of Ilya Sutskever's 30 AI papers chatbot.

## Concept

Build a personal learning tool that lets you:
- Load different **knowledge bases** (papers, books, courses) and switch between them
- Ask questions and get **cited answers** via RAG (Retrieval-Augmented Generation)
- Follow **curated learning paths** through material
- Test understanding with **quizzes**
- Adjust explanation **complexity** (ELI5 → Expert)
- Visualize **connections** between concepts via knowledge graph

## What is RAG?

**Retrieval-Augmented Generation** - a technique that makes LLMs accurate about specific documents:

1. **Chunk** documents into pieces (~500 words each)
2. **Embed** chunks into vectors (numerical meaning representation)
3. **Store** in searchable vector database
4. **On question:** find similar chunks → pass to LLM with question → get cited answer

## Tech Stack (Reusing local-ai-character-app patterns)

| Layer | Technology |
|-------|------------|
| Desktop Shell | Tauri 2.0 |
| Frontend | SvelteKit + Tailwind CSS |
| Backend | FastAPI (Python) |
| Embeddings | OpenAI text-embedding-3-small (or local alternative) |
| Vector Store | ChromaDB or FAISS |
| LLM | Claude API (or local via MLX) |
| Database | SQLite |

## Planned Structure

```
learning-chatbot/
├── backend/
│   ├── main.py
│   ├── services/
│   │   ├── rag_engine.py        # Embeddings + vector search
│   │   ├── document_ingest.py   # PDF/MD → chunks → embeddings
│   │   └── quiz_generator.py
│   └── api/
│       ├── chat.py              # Q&A endpoint
│       ├── knowledge_bases.py   # CRUD for KBs
│       └── quizzes.py
├── frontend/
│   └── src/
│       ├── routes/
│       │   ├── +page.svelte           # KB selector / dashboard
│       │   ├── chat/+page.svelte      # Q&A interface
│       │   ├── paths/+page.svelte     # Learning paths
│       │   └── quiz/+page.svelte      # Quiz mode
│       └── lib/
│           ├── components/
│           │   ├── ComplexitySlider.svelte
│           │   └── KnowledgeGraph.svelte
│           └── stores/
├── src-tauri/
├── knowledge-bases/             # Your document collections
│   ├── ai-papers/
│   │   ├── config.yaml
│   │   ├── documents/
│   │   └── learning_paths.yaml
│   └── [other-topics]/
└── data/                        # Vector stores, embeddings cache
```

## Key Features (from original)

1. **AI-Powered Q&A** - Semantic search with citations
2. **Learning Paths** - Curated sequences through material
3. **Knowledge Graph** - Interactive visualization of paper connections
4. **Quiz Mode** - Multiple difficulties and topics
5. **Complexity Slider** - ELI5 to Expert explanations
6. **Offline-Capable** - Papers stored locally, only API needed for AI features

## Why Tauri + SvelteKit over Streamlit?

The original uses Streamlit (quick prototype). We're using Tauri + SvelteKit because:
- Full UI control (not limited to widgets)
- True reactive SPA (no page reloads)
- Native desktop performance
- Proper state management
- Better for knowledge graph visualization (D3.js)
- Already have the stack from local-ai-character-app

## Next Steps

1. Scaffold backend with FastAPI
2. Implement RAG engine (document ingestion + vector search)
3. Copy frontend patterns from local-ai-character-app
4. Build Q&A chat interface
5. Add knowledge base selector
6. Implement learning paths
7. Add quiz mode
8. Add knowledge graph visualization
