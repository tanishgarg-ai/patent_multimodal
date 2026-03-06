import logging
import uuid
from typing import List, Dict, Any, Optional
import tiktoken
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Metadata for individual chunks"""
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_document_id: str = ""
    chunk_index: int = 0
    token_count: int = 0
    doc_type: str = ""
    section: str = ""
    year: int = 0
    classification: str = ""
    pdf_url: str = ""
    # other metadata mapped from document

@dataclass
class DocumentChunk:
    """Individual document chunk with content and metadata"""
    content: str
    metadata: ChunkMetadata
    embedding: Optional[np.ndarray] = None

class PatentChunker:
    """
    Advanced chunking system adapted for Patent texts.
    Uses tiktoken for token-aware chunking.
    """
    def __init__(
        self,
        chunk_size_tokens: int = 500,
        chunk_overlap_tokens: int = 100,
    ):
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base") # default tiktoken 
        logger.info(f"Initialized PatentChunker: size={chunk_size_tokens}, overlap={chunk_overlap_tokens}")

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """Chunk a list of document dicts."""
        all_chunks = []
        for doc in documents:
            doc_chunks = self._chunk_single_document(doc)
            all_chunks.extend(doc_chunks)
        logger.info(f"Created {len(all_chunks)} total chunks from {len(documents)} documents.")
        return all_chunks

    def _chunk_single_document(self, doc: Dict[str, Any]) -> List[DocumentChunk]:
        """Chunk a single document based on sections."""
        chunks = []
        doc_type = doc.get("doc_type", "unknown")
        doc_id = doc.get("patent_id") or doc.get("paper_id") or str(uuid.uuid4())
        year = doc.get("year")
        if not year and "publication_date" in doc:
            try:
                year = int(doc["publication_date"].split("-")[0])
            except:
                year = 0
        classification = doc.get("classification", "")
        pdf_url = doc.get("pdf_url", "")

        # For patents we structure per section
        sections_to_chunk = {
            "title": doc.get("title", ""),
            "abstract": doc.get("abstract", ""),
            "claims": doc.get("claims", ""),
            "description": doc.get("description", "")
        }

        chunk_index = 0
        for section_name, text in sections_to_chunk.items():
            if not text:
                continue
                
            tokens = self.tokenizer.encode(text)
            start = 0
            while start < len(tokens):
                end = min(start + self.chunk_size_tokens, len(tokens))
                
                # Check for clean boundary (simple heuristic: don't break mid-word)
                # Actually tiktoken encodes subwords, so exact decoding is safe.
                chunk_tokens = tokens[start:end]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                
                metadata = ChunkMetadata(
                    parent_document_id=doc_id,
                    chunk_index=chunk_index,
                    token_count=len(chunk_tokens),
                    doc_type=doc_type,
                    section=section_name,
                    year=year,
                    classification=classification,
                    pdf_url=pdf_url
                )
                
                chunks.append(DocumentChunk(content=chunk_text, metadata=metadata))
                chunk_index += 1
                
                # Advace by size minus overlap
                start += (self.chunk_size_tokens - self.chunk_overlap_tokens)
                if start >= len(tokens):
                    break

        return chunks
