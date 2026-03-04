import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import numpy as np

from document_processor import DocumentChunk
from embedding_pipeline import EmbeddingPipeline

logger = logging.getLogger(__name__)

class PatentVectorStore:
    """
    Vector store with ChromaDB backend for patents and papers.
    """
    def __init__(self, 
                 embedder: EmbeddingPipeline,
                 persist_directory: str = "./chroma_db"):
        self.embedder = embedder
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # We use separate collections for patents and papers to allow targeted searches,
        # or a unified collection with metadata filtering. Let's use a unified one for simplicity
        # and rely on metadata filtering.
        self.collection_name = "patent_prior_art"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Vector store initialized at {persist_directory} for collection {self.collection_name}")

    def add_chunks(self, chunks: List[DocumentChunk], batch_size: int = 100):
        """Add document chunks to vector store with batch processing."""
        logger.info(f"Adding {len(chunks)} chunks to vector store...")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            # Generate embeddings for the batch
            texts = [chunk.content for chunk in batch]
            batch_embeddings = self.embedder.encode(texts)
            
            for idx, chunk in enumerate(batch):
                documents.append(chunk.content)
                embeddings.append(batch_embeddings[idx].tolist())
                ids.append(chunk.metadata.chunk_id)
                
                # ChromaDB metadata values must be str, int, float, or bool
                meta = {
                    "doc_type": chunk.metadata.doc_type,
                    "parent_document_id": chunk.metadata.parent_document_id,
                    "section": chunk.metadata.section,
                    "year": int(chunk.metadata.year) if chunk.metadata.year else 0,
                    "classification": chunk.metadata.classification,
                    "chunk_index": int(chunk.metadata.chunk_index)
                }
                metadatas.append(meta)
                
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Processed batch {i//batch_size + 1}")
            
    def similarity_search(self, 
                          query: str, 
                          n_results: int = 10, 
                          filter_criteria: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Perform similarity search."""
        query_embedding = self.embedder.encode(query, normalize_embeddings=True)
        
        search_params = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if filter_criteria:
            search_params["where"] = filter_criteria
            
        results = self.collection.query(**search_params)
        
        formatted_results = []
        if not results["documents"] or len(results["documents"]) == 0:
            return formatted_results
            
        for i in range(len(results["documents"][0])):
            result = {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            }
            # Distance in cosine space is usually [0, 2], lower is better.
            # Convert to similarity [0, 1]
            result["similarity_score"] = max(0.0, 1.0 - (result["distance"] / 2.0))
            formatted_results.append(result)
            
        return formatted_results
