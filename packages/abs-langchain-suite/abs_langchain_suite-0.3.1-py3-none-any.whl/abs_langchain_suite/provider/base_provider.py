from abc import ABC, abstractmethod
from typing import Union, List, Any
from langchain_core.messages import BaseMessage
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_core.tools import BaseTool

class BaseProvider(ABC):
    @abstractmethod
    def get_chat_model(self) -> BaseChatModel: ...

    @abstractmethod
    def get_embeddings_model(self) -> Embeddings: ...

    @abstractmethod
    def chat(self, messages: Union[str, List[BaseMessage], List[dict]], system_message: str = None, **kwargs) -> str: ...

    @abstractmethod
    async def async_chat(self, messages: Union[str, List[BaseMessage], List[dict]], system_message: str = None, **kwargs) -> str: ...

    @abstractmethod
    def embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]: ...

    @abstractmethod
    async def async_embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]: ...

    @abstractmethod
    async def async_embed_documents(self, texts: List[str], **kwargs) -> List[List[float]]: ...

    @abstractmethod
    def embed_documents(self, texts: List[str], **kwargs) -> List[List[float]]: ...

    @abstractmethod
    def create_chain(self, prompt: BasePromptTemplate, output_parser: BaseOutputParser = None, **kwargs) -> RunnableSequence: ...

    @abstractmethod
    def create_chat_prompt(self, messages: List[dict], **kwargs) -> BasePromptTemplate: ...

    @abstractmethod
    def update_config(self, **kwargs): ...

    @abstractmethod
    def validate_config(self) -> bool: ...

    @abstractmethod
    def run_agent(self, tools: List[BaseTool], prompt: BasePromptTemplate, input: dict) -> Any: ...
