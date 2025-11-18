from sentence_transformers import SentenceTransformer
import numpy as np
from core.logging_config import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    def __init__(self, model_path: str):
        logger.info("Loading SentenceTransformer model from %s", model_path)
        try:
            self.model = SentenceTransformer(model_path)
        except Exception:
            logger.exception("Failed to load SentenceTransformer model")
            raise

    def embed(self, texts: list[str]) -> np.ndarray:
        try:
            return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        except Exception:
            logger.exception("Embedding generation failed for batch of size %d", len(texts) if hasattr(texts, '__len__') else -1)
            raise

    def embed_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        try:
            return self.embed([text])[0]
        except Exception:
            logger.exception("Embedding generation failed for single text")
            raise