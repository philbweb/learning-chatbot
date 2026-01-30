"""RAG engine for embeddings, retrieval, and generation."""

from typing import Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine."""

    def __init__(self):
        self.mock_mode = settings.MOCK_MODE
        self._embedding_model = None
        self._vector_store = None
        self._llm_client = None

    async def initialize(self) -> None:
        """Initialize the RAG components."""
        if self.mock_mode:
            logger.info("RAG engine initialized in mock mode")
            return

        # Initialize embedding model
        try:
            from sentence_transformers import SentenceTransformer

            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}. Falling back to mock mode.")
            self.mock_mode = True
            return

        # Initialize vector store
        try:
            import chromadb

            self._vector_store = chromadb.Client()
            logger.info("Initialized ChromaDB vector store")
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}. Falling back to mock mode.")
            self.mock_mode = True
            return

        # Initialize LLM client
        if settings.ANTHROPIC_API_KEY:
            try:
                import anthropic

                self._llm_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Initialized Anthropic client")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}")

    def get_or_create_collection(self, kb_id: str):
        """Get or create a vector collection for a knowledge base."""
        if self.mock_mode or not self._vector_store:
            return None
        return self._vector_store.get_or_create_collection(name=f"kb_{kb_id}")

    async def embed_text(self, text: str) -> list[float]:
        """Generate embeddings for text."""
        if self.mock_mode or not self._embedding_model:
            # Return mock embedding
            return [0.0] * 384

        return self._embedding_model.encode(text).tolist()

    async def embed_chunks(
        self, kb_id: str, chunks: list[dict]
    ) -> list[str]:
        """Embed and store document chunks in the vector store."""
        if self.mock_mode:
            logger.info(f"Mock: Would embed {len(chunks)} chunks for KB {kb_id}")
            return [f"mock_embedding_{i}" for i in range(len(chunks))]

        collection = self.get_or_create_collection(kb_id)
        if not collection:
            return []

        ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{chunk['document_id']}_{i}"
            embedding = await self.embed_text(chunk["content"])

            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk["content"]],
                metadatas=[{"document_id": chunk["document_id"], "chunk_index": i}],
            )
            ids.append(chunk_id)

        return ids

    async def search(
        self, kb_id: str, query: str, top_k: int = 5
    ) -> list[dict]:
        """Search for relevant chunks."""
        if self.mock_mode:
            logger.info(f"Mock: Would search KB {kb_id} for: {query}")
            return [
                {
                    "content": f"Mock result {i+1} for query: {query}",
                    "document_id": f"mock_doc_{i}",
                    "score": 0.9 - (i * 0.1),
                }
                for i in range(min(top_k, 3))
            ]

        collection = self.get_or_create_collection(kb_id)
        if not collection:
            return []

        query_embedding = await self.embed_text(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

        return [
            {
                "content": doc,
                "document_id": meta["document_id"],
                "score": 1 - dist,  # Convert distance to similarity
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    async def generate_response(
        self,
        query: str,
        context: list[dict],
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate a response using retrieved context."""
        if self.mock_mode or not self._llm_client:
            context_text = "\n".join([c["content"] for c in context[:3]])
            return f"[Mock Response]\n\nBased on the following context:\n{context_text[:200]}...\n\nMock answer to: {query}"

        # Build context string
        context_str = "\n\n".join(
            [f"[Source {i+1}]\n{c['content']}" for i, c in enumerate(context)]
        )

        default_system = """You are a helpful learning assistant. Answer questions based on the provided context.
If the context doesn't contain relevant information, say so. Always be accurate and educational."""

        try:
            response = self._llm_client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=1024,
                system=system_prompt or default_system,
                messages=[
                    {
                        "role": "user",
                        "content": f"Context:\n{context_str}\n\nQuestion: {query}",
                    }
                ],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"I encountered an error generating a response: {str(e)}"

    async def generate_stream(
        self,
        query: str,
        context: list[dict],
        system_prompt: Optional[str] = None,
    ):
        """Generate a streaming response."""
        if self.mock_mode or not self._llm_client:
            # Mock streaming response
            mock_response = f"[Mock Streaming Response] Based on your question: {query}"
            for word in mock_response.split():
                yield word + " "
            return

        context_str = "\n\n".join(
            [f"[Source {i+1}]\n{c['content']}" for i, c in enumerate(context)]
        )

        default_system = """You are a helpful learning assistant. Answer questions based on the provided context.
If the context doesn't contain relevant information, say so. Always be accurate and educational."""

        try:
            with self._llm_client.messages.stream(
                model=settings.LLM_MODEL,
                max_tokens=1024,
                system=system_prompt or default_system,
                messages=[
                    {
                        "role": "user",
                        "content": f"Context:\n{context_str}\n\nQuestion: {query}",
                    }
                ],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            yield f"Error: {str(e)}"
