from typing import List, Optional
from ..provider import BaseProvider
from ..schemas.embedding_config_schema import EmbeddingConfig
from abs_exception_core.exceptions import GenericHttpError

class EmbeddingService:
    """Service for generating embeddings using various LLM providers."""
    
    def __init__(self, provider: BaseProvider, config: Optional[EmbeddingConfig] = None):
        """Initialize the embedding service.
        
        Args:
            provider: LLM provider for generating embeddings
            config: Embedding configuration
        """
        self.provider = provider
        self.config = config

    async def aembed_query(self, text: str) -> List[float]:
        """Generate embedding for a single text query.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        return await self.provider.async_embed_text(text)
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            batch_embeddings = await self.provider.async_embed_documents(batch)
            embeddings.extend(batch_embeddings)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Synchronous version of embed_query.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        return self.provider.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Synchronous version of embed_documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = []
        if self.config is None:
            self.config = EmbeddingConfig(batch_size=100)
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            batch_embeddings = self.provider.embed_documents(batch)
            embeddings.extend(batch_embeddings)
        return embeddings 