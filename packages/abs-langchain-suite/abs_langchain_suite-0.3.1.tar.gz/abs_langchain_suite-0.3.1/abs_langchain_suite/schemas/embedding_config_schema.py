from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EmbeddingConfig(BaseModel):
    """Configuration for embedding generation."""
    
    model_name: str = Field(description="Name of the embedding model to use")
    dimensions: int = Field(description="Number of dimensions for the embeddings")
    batch_size: int = Field(default=100, description="Batch size for embedding generation")
    
    # Model-specific settings
    model_params: Dict[str, Any] = Field(default_factory=dict, description="Model-specific parameters")
    
    # Performance settings
    max_retries: int = Field(default=3, description="Maximum number of retries for embedding generation")
    timeout: Optional[float] = Field(default=None, description="Timeout for embedding requests")
    
    # Caching settings
    enable_caching: bool = Field(default=True, description="Enable embedding caching")
    cache_ttl: Optional[int] = Field(default=3600, description="Cache TTL in seconds") 