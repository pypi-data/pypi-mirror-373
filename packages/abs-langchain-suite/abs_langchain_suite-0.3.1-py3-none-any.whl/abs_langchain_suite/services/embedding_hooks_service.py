from typing import TypeVar, Type, Optional, Dict, Any, List, Generic
from pydantic import BaseModel
from ..embeddings.embedding_service import EmbeddingService
from ..schemas.embedding_config_schema import EmbeddingConfig
from ..schemas.vector_config_schema import BaseVectorConfig
from ..embeddings.vector_service import VectorServiceFactory
from abs_exception_core.exceptions import (
    GenericHttpError,
    NotFoundError
)
import asyncio

T = TypeVar('T', bound=BaseModel)


class EmbeddingHookMixin(Generic[T]):
    """Mixin to add embedding capabilities to services.
    
    This mixin provides methods to handle embedding generation and storage
    for CRUD operations on models that need vector embeddings.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        embedding_config: EmbeddingConfig,
        vector_config: BaseVectorConfig
    ):
        """Initialize the embedding hook mixin.
        
        Args:
            embedding_service: Configured embedding service
            embedding_config: Configuration for each model type
            vector_config: Vector database configuration
            logger: Optional usage logger
        """
        self.embedding_service = embedding_service
        self.embedding_config = embedding_config
        self.vector_config = vector_config
        self.vector_service = VectorServiceFactory.create_service(vector_config)

    async def embed_on_create(
        self,
        record_id: str,
        text: str,
        record: T
    ) -> None:
        """Generate and store embedding for a new record if enabled.
        
        Args:
            record: The record to embed
            model_type: Type of the record
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            # Generate embedding
            embedding = await self.embedding_service.aembed_query(text)

            # Convert record to dict if it's a Pydantic model
            record_dict = record.model_dump() if hasattr(record, 'model_dump') else record

            await self.vector_service.create_item(record_id, embedding, record_dict)

        except Exception as e:
            raise GenericHttpError(status_code=500, detail=f"Failed to embed on create: {str(e)}")

    async def embed_on_update(
        self,
        record_id: str,
        record: T,
        text: str
    ) -> None:
        """Update embedding if the target field has changed.
        
        Args:
            record_id: ID of the record
            record: Updated record
            text: Text to embed
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            # Get the Document from the Vector database
            document = self.vector_service.read_item(record_id)
            if not document:
                await self.embed_on_create(record_id, text, record)
                return

            # Generate the embedding
            embedding = await self.embedding_service.aembed_query(text)

            # Convert record to dict if it's a Pydantic model
            record_dict = record.model_dump() if hasattr(record, 'model_dump') else record

            # Update in Vector database
            await self.vector_service.update_item(record_id, embedding, record_dict)

        except Exception as e:
            raise GenericHttpError(status_code=500, detail=f"Failed to embed on update: {str(e)}")

    async def delete_vector(
        self,
        record_id: str
    ) -> None:
        """Delete vector embedding if enabled.
        
        Args:
            record_id: ID of the record
            model_type: Type of the record
            
        Raises:
            EmbeddingError: If deletion fails
        """
        try:
            await self.vector_service.delete_item(record_id)
        except Exception as e:
            raise GenericHttpError(status_code=500, detail=f"Failed to delete vector: {str(e)}")

    async def bulk_delete_vector(self, records: list[dict]):
        try:
            tasks = [
                self.vector_service.delete_item(rec['id'])
                for rec in records
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            raise GenericHttpError(status_code=500, detail=f"Parallel bulk deletion failed: {e}")


    async def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        projection_fields: list[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar records using vector similarity.
        
        Args:
            query_text: Text to search for
            model_type: Type of records to search
            limit: Maximum number of results
            min_score: Minimum similarity score
            
        Returns:
            List of similar records with scores
            
        Raises:
            EmbeddingError: If search fails
        """
        #TODO: NEED TO IMPROVE
        try:
            # Generate query embedding
            query_vector = await self.embedding_service.aembed_query(query_text)
            results = await self.vector_service.search_similar(query_vector, limit, projection_fields)

            return results

        except Exception as e:
            raise GenericHttpError(status_code=500, detail=f"Failed to search similar: {str(e)}") 