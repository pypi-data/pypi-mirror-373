from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable

from ..provider.base_provider import BaseProvider


class RAGService:
    def __init__(
        self,
        provider: BaseProvider,
        vector_store: Optional[VectorStore] = None,
        retriever: Optional[BaseRetriever] = None,
    ):
        self.provider = provider
        self.embeddings_model = self._resolve_embeddings_model()
        self.chat_model = self.provider.get_chat_model()
        self.vector_store = vector_store
        self.retriever = retriever

    def _resolve_embeddings_model(self) -> Embeddings:
        """Get embeddings model or fallback for Claude."""
        try:
            return self.provider.get_embeddings_model()
        except NotImplementedError:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings()

    def build_vector_store(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> FAISS:
        """Build and return a FAISS vector store."""
        return FAISS.from_texts(
            texts=texts, embedding=self.embeddings_model, metadatas=metadatas
        )

    def get_retriever(
        self,
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[dict]] = None,
    ) -> BaseRetriever:
        """Get retriever using vector store or texts."""
        if self.retriever:
            return self.retriever

        if self.vector_store:
            self.retriever = self.vector_store.as_retriever()
            return self.retriever

        if texts is None:
            raise ValueError("Must provide either retriever, vector_store, or texts.")

        self.vector_store = self.build_vector_store(texts, metadatas)
        self.retriever = self.vector_store.as_retriever()
        return self.retriever

    def semantic_search(
        self,
        query: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        k: int = 3,
    ) -> List[Document]:
        """Perform semantic search and return top-k relevant documents."""
        retriever = self.get_retriever(texts, metadatas)
        return retriever.get_relevant_documents(query)

    def build_rag_chain(
        self,
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[dict]] = None,
        chain_type: str = "stuff",
    ) -> Runnable:
        """Build a retrieval chain using LangChain's `create_retrieval_chain`."""
        retriever = self.get_retriever(texts, metadatas)
        return create_retrieval_chain(
            retriever=retriever,
            llm=self.chat_model,
            chain_type=chain_type,
        )

    def run_rag(
        self,
        query: str,
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[dict]] = None,
        chain_type: str = "stuff",
    ) -> str:
        """Run the full RAG pipeline using LangChain's Runnable chain."""
        chain = self.build_rag_chain(texts, metadatas, chain_type)
        return chain.invoke(query)
