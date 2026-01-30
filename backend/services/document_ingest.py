"""Document ingestion service for processing files into chunks."""

import logging
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class DocumentIngestService:
    """Service for ingesting and processing documents."""

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.mock_mode = settings.is_mock_mode

    async def extract_text(self, file_path: Path, file_type: str) -> str:
        """Extract text content from a file."""
        if self.mock_mode:
            logger.info(f"Mock: Would extract text from {file_path}")
            return f"Mock content extracted from {file_path.name}"

        extractors = {
            "pdf": self._extract_pdf,
            "md": self._extract_markdown,
            "txt": self._extract_text,
            "docx": self._extract_docx,
        }

        extractor = extractors.get(file_type.lower())
        if not extractor:
            raise ValueError(f"Unsupported file type: {file_type}")

        return await extractor(file_path)

    async def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

    async def _extract_markdown(self, file_path: Path) -> str:
        """Extract text from Markdown file."""
        try:
            import markdown
            from html import unescape
            import re

            with open(file_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Convert to HTML then strip tags for plain text
            html = markdown.markdown(md_content)
            # Simple HTML tag removal
            text = re.sub(r"<[^>]+>", "", html)
            return unescape(text)
        except Exception as e:
            logger.error(f"Markdown extraction failed: {e}")
            raise

    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise

    async def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document

            doc = Document(file_path)
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise

    def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> list[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap

        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence or paragraph boundary
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break > start + chunk_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence break
                    for sep in [". ", "! ", "? ", "\n"]:
                        sent_break = text.rfind(sep, start, end)
                        if sent_break > start + chunk_size // 2:
                            end = sent_break + len(sep)
                            break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start with overlap
            start = end - chunk_overlap
            if start >= len(text):
                break

        return chunks

    async def process_file(
        self, file_path: Path, file_type: str, document_id: str
    ) -> list[dict]:
        """Process a file and return chunks with metadata."""
        if self.mock_mode:
            logger.info(f"Mock: Would process {file_path}")
            return [
                {
                    "document_id": document_id,
                    "content": f"Mock chunk {i+1} from {file_path.name}",
                    "chunk_index": i,
                    "metadata": {"source": str(file_path), "page": i + 1},
                }
                for i in range(3)
            ]

        text = await self.extract_text(file_path, file_type)
        chunks = self.chunk_text(text)

        return [
            {
                "document_id": document_id,
                "content": chunk,
                "chunk_index": i,
                "metadata": {"source": str(file_path)},
            }
            for i, chunk in enumerate(chunks)
        ]
