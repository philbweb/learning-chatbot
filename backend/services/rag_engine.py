"""RAG engine for embeddings, retrieval, and generation."""

from typing import Optional, AsyncGenerator
import logging
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine."""

    def __init__(self):
        self._mock_mode_override = None  # Set during initialize if fallback needed
        self._embedding_model = None
        self._vector_store = None
        self._llm_client = None
        self._chroma_path = Path("data/chroma")

    @property
    def mock_mode(self) -> bool:
        """Check if mock mode is active."""
        if self._mock_mode_override is not None:
            return self._mock_mode_override
        return settings.is_mock_mode

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
            self._mock_mode_override = True
            return

        # Initialize persistent vector store
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._chroma_path.mkdir(parents=True, exist_ok=True)
            self._vector_store = chromadb.PersistentClient(
                path=str(self._chroma_path),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"Initialized ChromaDB at {self._chroma_path}")
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}. Falling back to mock mode.")
            self._mock_mode_override = True
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
        return self._vector_store.get_or_create_collection(
            name=f"kb_{kb_id}",
            metadata={"hnsw:space": "cosine"},
        )

    def delete_collection(self, kb_id: str) -> bool:
        """Delete a vector collection for a knowledge base."""
        if self.mock_mode or not self._vector_store:
            return True
        try:
            self._vector_store.delete_collection(name=f"kb_{kb_id}")
            logger.info(f"Deleted collection for KB {kb_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete collection: {e}")
            return False

    async def embed_text(self, text: str) -> list[float]:
        """Generate embeddings for text."""
        if self.mock_mode or not self._embedding_model:
            return [0.0] * 384

        return self._embedding_model.encode(text, normalize_embeddings=True).tolist()

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
        documents = []
        embeddings = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{chunk['document_id']}_{i}"
            embedding = await self.embed_text(chunk["content"])

            ids.append(chunk_id)
            documents.append(chunk["content"])
            embeddings.append(embedding)
            metadatas.append({
                "document_id": chunk["document_id"],
                "chunk_index": i,
            })

        # Batch add for efficiency
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Embedded {len(chunks)} chunks for KB {kb_id}")
        return ids

    async def delete_document_chunks(self, kb_id: str, document_id: str) -> bool:
        """Delete all chunks for a document from the vector store."""
        if self.mock_mode or not self._vector_store:
            return True

        try:
            collection = self.get_or_create_collection(kb_id)
            if collection:
                # Delete by metadata filter
                collection.delete(where={"document_id": document_id})
                logger.info(f"Deleted chunks for document {document_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete document chunks: {e}")
            return False

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

        # Check if collection has any documents
        if collection.count() == 0:
            logger.info(f"KB {kb_id} has no documents")
            return []

        query_embedding = await self.embed_text(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return []

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
        if context:
            context_str = "\n\n".join(
                [f"[Source {i+1}]\n{c['content']}" for i, c in enumerate(context)]
            )
            user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
        else:
            user_content = f"Question: {query}\n\nNote: No relevant context was found in the knowledge base."

        default_system = """You are a helpful learning assistant. Answer questions based on the provided context.
If the context doesn't contain relevant information, say so. Always be accurate and educational.
When citing information, reference which source it came from (e.g., "According to Source 1...")."""

        try:
            response = self._llm_client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=1024,
                system=system_prompt or default_system,
                messages=[{"role": "user", "content": user_content}],
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
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        if self.mock_mode or not self._llm_client:
            mock_response = f"[Mock Streaming Response] Based on your question: {query}"
            for word in mock_response.split():
                yield word + " "
            return

        if context:
            context_str = "\n\n".join(
                [f"[Source {i+1}]\n{c['content']}" for i, c in enumerate(context)]
            )
            user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
        else:
            user_content = f"Question: {query}\n\nNote: No relevant context was found in the knowledge base."

        default_system = """You are a helpful learning assistant. Answer questions based on the provided context.
If the context doesn't contain relevant information, say so. Always be accurate and educational.
When citing information, reference which source it came from (e.g., "According to Source 1...")."""

        try:
            with self._llm_client.messages.stream(
                model=settings.LLM_MODEL,
                max_tokens=1024,
                system=system_prompt or default_system,
                messages=[{"role": "user", "content": user_content}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            yield f"Error: {str(e)}"
