"""Embedding service for converting text to vector representations."""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Union, List
from config.settings import EMBEDDING_MODEL, CANONICAL_CATEGORIES


class EmbeddingService:
    """Service for generating text embeddings."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern for model loading."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding model (only once)."""
        if self._model is None:
            print(f"Loading embedding model: {EMBEDDING_MODEL}")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
    
    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text string or list of strings
            
        Returns:
            numpy array of embeddings (1D for single text, 2D for list)
        """
        if isinstance(text, str):
            return self._model.encode(text, convert_to_numpy=True)
        else:
            return self._model.encode(text, convert_to_numpy=True)
    
    def bytes_to_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """
        Convert bytes from database back to numpy array.
        
        Args:
            embedding_bytes: Embedding stored as bytes
            
        Returns:
            numpy array embedding
        """
        return np.frombuffer(embedding_bytes, dtype=np.float32)
    
    def embed_to_bytes(self, text: str) -> bytes:
        """
        Generate embedding and convert to bytes for storage.

        Args:
            text: Text to embed
            
        Returns:
            Embedding as bytes
        """
        embedding = self.embed(text)
        return embedding.astype(np.float32).tobytes()


# Global instance
_embedding_service = EmbeddingService()


def text_to_embedding(text: str) -> np.ndarray:
    """
    Convert text to embedding vector.
    
    Args:
        text: Text to convert
        
    Returns:
        numpy array embedding vector
    """
    return _embedding_service.embed(text)

def embed_to_bytes(text: str) -> bytes:
    """
    Convert text to embedding and return as bytes for database storage.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding as bytes
    """
    return _embedding_service.embed_to_bytes(text)


def get_category_embedding(category: str) -> np.ndarray:
    """
    Get embedding for a canonical category.
    
    Args:
        category: Category name
        
    Returns:
        Embedding vector for the category
    """
    if category not in CANONICAL_CATEGORIES:
        # Find closest match
        category_lower = category.lower()
        for canonical in CANONICAL_CATEGORIES:
            if canonical.lower() in category_lower or category_lower in canonical.lower():
                category = canonical
                break
    
    return text_to_embedding(category)