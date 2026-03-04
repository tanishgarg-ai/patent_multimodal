import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MultimodalModule:
    """
    Optional multimodal extension for patent diagrams.
    Uses CLIP (via sentence-transformers) to compute image embeddings.
    """
    def __init__(self, model_name: str = "clip-ViT-B-32"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded multimodal model: {model_name}")
            self.enabled = True
        except Exception as e:
            logger.warning(f"Failed to load multimodal model {model_name}. CLIP may not be installed. Error: {e}")
            self.enabled = False

    def encode_image(self, image_path: str) -> Optional[np.ndarray]:
        """Encode an image from disk."""
        if not self.enabled:
            return None
            
        try:
            from PIL import Image
            img = Image.open(image_path)
            embedding = self.model.encode(img)
            return embedding
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None
