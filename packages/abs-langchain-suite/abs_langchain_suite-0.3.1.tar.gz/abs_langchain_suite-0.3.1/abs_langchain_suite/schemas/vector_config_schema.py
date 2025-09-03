from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class BaseVectorConfig(BaseModel):
    """Base configuration for vector databases."""
    
    vector_field: str = Field(default="vector", description="Field name for storing vectors")
    database_name: Optional[str] = Field(default=None, description="Name of the database")
    collection_name: Optional[str] = Field(default=None, description="Name of the collection/container")
    
    # Connection settings
    connection_string: Optional[str] = Field(default=None, description="Connection string for the database")
    api_key: Optional[str] = Field(default=None, description="API key for the service")
    
    # Additional configuration
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional configuration metadata")


class CosmosVectorConfig(BaseVectorConfig):
    """Configuration specifically for Azure Cosmos DB."""
    
    database: Any = Field(description="Cosmos DB database client")
    container_name: str = Field(description="Cosmos DB container name")
    
    class Config:
        arbitrary_types_allowed = True


class PineconeVectorConfig(BaseVectorConfig):
    """Configuration for Pinecone vector database."""
    
    environment: str = Field(description="Pinecone environment")
    index_name: str = Field(description="Pinecone index name")
    namespace: Optional[str] = Field(default=None, description="Pinecone namespace")


class WeaviateVectorConfig(BaseVectorConfig):
    """Configuration for Weaviate vector database."""
    
    url: str = Field(description="Weaviate server URL")
    class_name: str = Field(description="Weaviate class name")
    auth_client_secret: Optional[str] = Field(default=None, description="Weaviate auth secret")


class ChromaVectorConfig(BaseVectorConfig):
    """Configuration for Chroma vector database."""
    
    persist_directory: str = Field(description="Directory to persist Chroma data")
    collection_name: str = Field(description="Chroma collection name")


class QdrantVectorConfig(BaseVectorConfig):
    """Configuration for Qdrant vector database."""
    
    url: str = Field(description="Qdrant server URL")
    collection_name: str = Field(description="Qdrant collection name")
    api_key: Optional[str] = Field(default=None, description="Qdrant API key") 