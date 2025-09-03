# LangChain Suite Package

A comprehensive package providing LangChain utilities with multiple AI providers, token tracking, RAG (Retrieval-Augmented Generation), vector services, and agent support.

## Features

- **Multiple AI Providers**: Support for OpenAI, Azure OpenAI, and Claude (Anthropic)
- **Embeddings Support**: Easy text embedding generation with batch processing
- **Vector Database Integration**: Support for Cosmos DB, Pinecone, Weaviate, Chroma, and Qdrant
- **RAG Services**: Complete RAG pipeline with semantic search and retrieval chains
- **Embedding Hooks**: Automatic embedding generation and storage for CRUD operations
- **Token Usage Tracking & Logging**: Advanced logging of token usage, cost calculation, and database logging for all LLM and embedding operations
- **CLI Interface**: Command-line tool for quick AI provider interactions
- **Configuration Management**: Flexible configuration options for all components

## Logging Features

The LangChain Suite provides robust logging and token usage tracking for all LLM and embedding operations. Key features include:

- **DBTokenUsageLogger**: Callback handler that logs prompt, response, token usage, and cost to a database (SQL or NoSQL) for every LLM or embedding operation. Supports error logging and metadata.
- **Database Agnostic**: Use either SQL (via SQLAlchemy) or NoSQL (e.g., MongoDB, Cosmos DB) for logging. Implemented via `SQLDBClient` and `NoSQLDBClient`.
- **Cost Calculation**: Integrated pricing engine (`PricingService`) automatically calculates cost in USD for each operation based on provider/model/token usage.
- **Customizable Table/Collection**: Specify the table/collection name for logs.
- **Rich Metadata**: Attach custom metadata to each log entry for traceability.
- **Error Logging**: All LLM/embedding errors are logged with status and error message.

### Usage Example

```python
from abs_langchain_suite.logging.token_usage import DBTokenUsageLogger
from abs_langchain_suite.logging.db.sql_client import SQLDBClient
from abs_langchain_suite.logging.db.nosql_client import NoSQLDBClient
from abs_langchain_suite import OpenAIProvider

# SQL Example (SQLAlchemy)
sql_client = SQLDBClient(session=your_sqlalchemy_session, model_class=YourTokenUsageModel)
token_logger = DBTokenUsageLogger(sql_client, table="token_usage", metadata={"project": "my-app"})

# NoSQL Example (MongoDB/Cosmos)
nosql_client = NoSQLDBClient(db=your_nosql_db)
token_logger = DBTokenUsageLogger(nosql_client, table="token_usage", metadata={"project": "my-app"})

# Attach logger to provider
provider = OpenAIProvider(api_key="your-key", callbacks=[token_logger])
#Also you can attach with each service call
custom_logger = DBTokenUsageLogger(nosql_client, table="token_usage", metadata={"project": "my-app","feature":"chat"})
response = provider.chat("Hello world", callbacks=[custom_logger])
```

### What Gets Logged?
- Prompt and response content
- Provider and model name
- Input/output/prompt/completion/total tokens
- Cost in USD (auto-calculated)
- Custom metadata
- Error status and message (if any)

### Cost Calculation

The logger uses the built-in `PricingService` to calculate cost for OpenAI, Azure, and Anthropic models. Pricing is updated for all major models and embedding endpoints.

## Installation

```bash
pip install abs-langchain-suite
```

## Quick Start

### Basic Provider Usage

```python
from abs_langchain_suite import OpenAIProvider, AzureOpenAIProvider, ClaudeProvider

# OpenAI Provider
openai_provider = OpenAIProvider(api_key="your-openai-key")
response = openai_provider.chat("Hello, how are you?")

# Azure OpenAI Provider
azure_provider = AzureOpenAIProvider(
    api_key="your-azure-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="your-deployment"
)
response = azure_provider.chat("Explain quantum computing")

# Claude Provider
claude_provider = ClaudeProvider(api_key="your-anthropic-key")
response = claude_provider.chat("Write a short story")
```

### Using Provider Factory

```python
from abs_langchain_suite import create_provider

# Create providers using factory
openai_provider = create_provider("openai", api_key="your-key")
azure_provider = create_provider("azure", api_key="your-key", azure_endpoint="...", deployment_name="...")
claude_provider = create_provider("claude", api_key="your-key")
```

### Embeddings and Vector Operations

```python
from abs_langchain_suite import OpenAIProvider
from abs_langchain_suite.embeddings import EmbeddingService
from abs_langchain_suite.schemas import EmbeddingConfig

# Create embedding service
provider = OpenAIProvider(api_key="your-key")
config = EmbeddingConfig(
    model_name="text-embedding-3-small",
    dimensions=1536,
    batch_size=100
)
embedding_service = EmbeddingService(provider, config)

# Generate embeddings
embedding = embedding_service.embed_query("Sample text")
embeddings = embedding_service.embed_documents(["Doc 1", "Doc 2", "Doc 3"])
```

### RAG (Retrieval-Augmented Generation)

```python
from abs_langchain_suite import OpenAIProvider
from abs_langchain_suite.services import RAGService

# Setup RAG service
provider = OpenAIProvider(api_key="your-key")
rag_service = RAGService(provider)

# Your documents
documents = [
    "Python is a programming language.",
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks."
]

# Perform semantic search
results = rag_service.semantic_search(
    query="What is Python?",
    texts=documents,
    k=2
)

# Build and run RAG chain
response = rag_service.run_rag(
    query="Explain machine learning",
    texts=documents,
    chain_type="stuff"
)
```

### Vector Database Integration

```python
from abs_langchain_suite.embeddings import VectorServiceFactory
from abs_langchain_suite.schemas import CosmosVectorConfig

# Configure Cosmos DB
cosmos_config = CosmosVectorConfig(
    database=your_cosmos_database,
    container_name="vectors",
    vector_field="embedding"
)

# Create vector service
vector_service = VectorServiceFactory.create_service(cosmos_config)

# Store vectors
await vector_service.create_item(
    item_id="doc_1",
    vector=[0.1, 0.2, 0.3, ...],
    metadata={"title": "Sample Document", "content": "..."}
)

# Search similar vectors
results = await vector_service.search_similar(
    query_vector=[0.1, 0.2, 0.3, ...],
    limit=5
)
```

### Embedding Hooks for CRUD Operations

```python
from abs_langchain_suite.services import EmbeddingHookMixin
from abs_langchain_suite.embeddings import EmbeddingService
from abs_langchain_suite.schemas import EmbeddingConfig, CosmosVectorConfig

class DocumentService(EmbeddingHookMixin):
    def __init__(self):
        provider = OpenAIProvider(api_key="your-key")
        embedding_config = EmbeddingConfig(model_name="text-embedding-3-small")
        vector_config = CosmosVectorConfig(database=db, container_name="documents")
        
        embedding_service = EmbeddingService(provider, embedding_config)
        super().__init__(embedding_service, embedding_config, vector_config)
    
    async def create_document(self, document_id: str, content: str, metadata: dict):
        # Your document creation logic
        document = {"id": document_id, "content": content, **metadata}
        
        # Automatically generate and store embedding
        await self.embed_on_create(document_id, content, document)
        
        return document
    
    async def search_similar_documents(self, query: str, limit: int = 10):
        return await self.search_similar(query, limit)
```

### Token Usage Tracking

```python
from abs_langchain_suite.logging import DBTokenUsageLogger
from abs_langchain_suite.logging.db import SQLClient
from abs_langchain_suite import OpenAIProvider

# Setup token usage logger
db_client = SQLClient(connection_string="your-db-connection")
token_logger = DBTokenUsageLogger(db_client, table="token_usage")

# Create provider with token tracking
provider = OpenAIProvider(
    api_key="your-key",
    callbacks=[token_logger]
)

# All interactions will now log token usage
response = provider.chat("Hello world")
```

## CLI Usage

The package includes a command-line interface for quick interactions:

```bash
# Basic usage
provider-cli --provider openai --api_key YOUR_KEY --message "Hello world"

# With custom model
provider-cli --provider openai --api_key YOUR_KEY --model_name gpt-4 --message "Explain AI"

# Azure OpenAI
provider-cli --provider azure --api_key YOUR_KEY --azure_endpoint "https://your-resource.openai.azure.com/" --deployment_name "your-deployment" --message "Hello"

# Claude
provider-cli --provider claude --api_key YOUR_KEY --message "Write a poem"
```

## Configuration

### Provider Configuration

All providers support extensive configuration options:

```python
# OpenAI Provider
openai_provider = OpenAIProvider(
    api_key="your-key",
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=1000,
    streaming=True,
    base_url="https://api.openai.com/v1"
)

# Azure OpenAI Provider
azure_provider = AzureOpenAIProvider(
    api_key="your-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="your-deployment",
    api_version="2024-02-15-preview",
    temperature=0.3
)

# Claude Provider
claude_provider = ClaudeProvider(
    api_key="your-key",
    model_name="claude-3-sonnet-20240229",
    max_tokens=1000,
    temperature=0.5
)
```

### Embedding Configuration

```python
from abs_langchain_suite.schemas import EmbeddingConfig

config = EmbeddingConfig(
    model_name="text-embedding-3-small",
    dimensions=1536,
    batch_size=100,
    max_retries=3,
    timeout=30.0,
    enable_caching=True,
    cache_ttl=3600
)
```

### Vector Database Configuration

```python
# Cosmos DB
from abs_langchain_suite.schemas import CosmosVectorConfig

cosmos_config = CosmosVectorConfig(
    database=your_cosmos_database,
    container_name="vectors",
    vector_field="embedding"
)

# Pinecone (future implementation)
from abs_langchain_suite.schemas import PineconeVectorConfig

pinecone_config = PineconeVectorConfig(
    environment="us-west1-gcp",
    index_name="my-index",
    namespace="my-namespace"
)
```

## Advanced Features

### Custom Chains and Prompts

```python
from abs_langchain_suite import OpenAIProvider
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

provider = OpenAIProvider(api_key="your-key")

# Create custom prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant specialized in {domain}."),
    ("human", "Answer this question: {question}")
])

# Create chain with custom parameters
chain = provider.create_chain(
    prompt,
    output_parser=StrOutputParser(),
    temperature=0.1,
    max_tokens=200
)

# Use the chain
result = chain.invoke({
    "domain": "machine learning",
    "question": "What is supervised learning?"
})
```

### Async Operations

All providers support async operations:

```python
import asyncio

async def main():
    provider = OpenAIProvider(api_key="your-key")
    
    # Async chat
    response = await provider.async_chat("Hello world")
    
    # Async embeddings
    embedding = await provider.async_embed_text("Sample text")
    embeddings = await provider.async_embed_documents(["Doc 1", "Doc 2"])

asyncio.run(main())
```

### Agent Support

```python
from abs_langchain_suite import OpenAIProvider
from langchain_core.tools import BaseTool

provider = OpenAIProvider(api_key="your-key")

# Define tools
tools = [
    # Your custom tools here
]

# Create prompt for agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to tools."),
    ("human", "{input}")
])

# Run agent
result = provider.run_agent(tools, prompt, {"input": "What's the weather like?"})
```

## Environment Variables

The package automatically reads these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_BASE_URL`: Custom base URL for OpenAI
- `OPENAI_ORGANIZATION`: Organization ID
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint
- `ANTHROPIC_API_KEY`: Your Anthropic API key

## API Reference

### Providers

- `OpenAIProvider`: OpenAI API integration
- `AzureOpenAIProvider`: Azure OpenAI integration
- `ClaudeProvider`: Anthropic Claude integration
- `BaseProvider`: Abstract base class for custom providers
- `create_provider()`: Factory function for creating providers

### Services

- `RAGService`: Complete RAG pipeline implementation
- `EmbeddingService`: Embedding generation and management
- `EmbeddingHookMixin`: Mixin for automatic embedding in CRUD operations

### Vector Services

- `VectorService`: Abstract base for vector database operations
- `CosmosVectorService`: Azure Cosmos DB implementation
- `VectorServiceFactory`: Factory for creating vector services

### Schemas

- `EmbeddingConfig`: Configuration for embedding generation
- `BaseVectorConfig`: Base vector database configuration
- `CosmosVectorConfig`: Cosmos DB specific configuration
- `PineconeVectorConfig`: Pinecone specific configuration
- `WeaviateVectorConfig`: Weaviate specific configuration
- `ChromaVectorConfig`: Chroma specific configuration
- `QdrantVectorConfig`: Qdrant specific configuration

### Logging

- `DBTokenUsageLogger`: Database token usage tracking and logging callback for LLM/embedding operations
- `BaseDBClient`: Abstract base for database clients
- `SQLDBClient`: SQL database client (SQLAlchemy-based)
- `NoSQLDBClient`: NoSQL database client (MongoDB/Cosmos-compatible)
- `PricingService`: Cost calculation for LLM and embedding operations

## Examples

See the `examples/` directory for comprehensive usage examples covering all features.

## License

MIT License
