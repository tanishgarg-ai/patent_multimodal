import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingPipeline:
    """Wrapper for sentence-transformers with caching and batch embedding."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32, normalize_embeddings: bool = True) -> np.ndarray:
        """Encode text(s) into embeddings."""
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
            
        logger.debug(f"Encoding {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize_embeddings,
            show_progress_bar=False
        )
        
        if is_single:
            return embeddings[0]
        return embeddings
