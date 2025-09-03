from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..schemas.vector_config_schema import BaseVectorConfig, CosmosVectorConfig


class VectorService(ABC):
    """Abstract base class for vector database services."""

    def __init__(self, config: BaseVectorConfig):
        """Initialize the vector service.

        Args:
            config: Vector database configuration
        """
        self.config = config


    @abstractmethod
    def read_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Read an item from the vector database.
        """
        pass

    @abstractmethod
    async def create_item(
        self, item_id: str, vector: List[float], metadata: Dict[str, Any]
    ) -> None:
        """Create a new item in the vector database.

        Args:
            item_id: Unique identifier for the item
            vector: Vector embedding
            metadata: Additional metadata
        """
        pass

    @abstractmethod
    async def update_item(
        self, item_id: str, vector: List[float], metadata: Dict[str, Any]
    ) -> None:
        """Update an existing item in the vector database.

        Args:
            item_id: Unique identifier for the item
            vector: Vector embedding
            metadata: Additional metadata
        """
        pass

    @abstractmethod
    async def delete_item(self, item_id: str) -> None:
        """Delete an item from the vector database.

        Args:
            item_id: Unique identifier for the item
        """
        pass

    @abstractmethod
    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        projection_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors.

        Args:
            query_vector: Query vector
            limit: Maximum number of results
            projection_fields: Fields to include in results

        Returns:
            List of similar items with scores
        """
        pass


class CosmosVectorService(VectorService):
    """Vector service implementation for Azure Cosmos DB."""

    def __init__(self, config: CosmosVectorConfig):
        super().__init__(config)
        # For Cosmos DB, we need the database client
        if hasattr(config, "database"):
            self.database = config.database
            self._container = self.database.get_container_client(config.container_name)
        else:
            raise ValueError("Cosmos DB config must include database client")

    def read_item(self, item_id: str) -> Dict[str, Any]:
        """Read an item from Cosmos DB."""
        return self._container.read_item(item=str(item_id), partition_key=str(item_id))

    async def create_item(
        self, item_id: str, vector: List[float], metadata: Dict[str, Any]
    ) -> None:
        """Create a new item in Cosmos DB."""
        vector_doc = {"id": str(item_id), self.config.vector_field: vector, **metadata}
        self._container.create_item(body=vector_doc)

    async def update_item(
        self, item_id: str, vector: List[float], metadata: Dict[str, Any]
    ) -> None:
        """Update an existing item in Cosmos DB."""
        vector_doc = {"id": str(item_id), self.config.vector_field: vector, **metadata}
        self._container.upsert_item(body=vector_doc)

    async def delete_item(self, item_id: str) -> None:
        """Delete an item from Cosmos DB."""
        self._container.delete_item(item=str(item_id), partition_key=str(item_id))

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        projection_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in Cosmos DB."""
        fields_str = "*"
        if projection_fields:
            fields_str = ", ".join([f"c.{field}" for field in projection_fields])

        query = f"""
        SELECT TOP {limit} {fields_str}, 
        VectorDistance(c.{self.config.vector_field}, {query_vector}) as score 
        FROM c 
        ORDER BY VectorDistance(c.{self.config.vector_field}, {query_vector})
        """

        results = list(
            self._container.query_items(query=query, enable_cross_partition_query=True)
        )

        return results


class VectorServiceFactory:
    """Factory for creating vector services based on configuration."""

    @staticmethod
    def create_service(config: BaseVectorConfig) -> VectorService:
        """Create a vector service based on the configuration type.

        Args:
            config: Vector database configuration

        Returns:
            Appropriate vector service implementation
        """
        if hasattr(config, "database") and hasattr(config, "container_name"):
            # This is a Cosmos DB config
            return CosmosVectorService(config)
        elif hasattr(config, "environment") and hasattr(config, "index_name"):
            # This is a Pinecone config
            # TODO: Implement PineconeVectorService
            raise NotImplementedError("Pinecone vector service not yet implemented")
        elif hasattr(config, "url") and hasattr(config, "class_name"):
            # This is a Weaviate config
            # TODO: Implement WeaviateVectorService
            raise NotImplementedError("Weaviate vector service not yet implemented")
        else:
            raise ValueError(
                f"Unsupported vector database configuration: {type(config)}"
            )
