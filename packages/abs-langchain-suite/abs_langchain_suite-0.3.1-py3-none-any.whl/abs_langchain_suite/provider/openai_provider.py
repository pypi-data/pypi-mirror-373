"""
OpenAI Provider Class for LangChain Core

This module provides a generic class that encapsulates all OpenAI provider services
for easy access and management in LangChain applications.
"""

from typing import Optional, Dict, Any, List, Union
import os
from dataclasses import dataclass

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import BasePromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langgraph.prebuilt.chat_agent_executor import (
    create_react_agent,
    CompiledStateGraph,
)
from langgraph.prebuilt.chat_agent_executor import (
    create_react_agent,
    CompiledStateGraph,
)
from langchain.agents.agent_types import AgentType
from langchain_core.tools import BaseTool
from abs_exception_core.exceptions import GenericHttpError
from .base_provider import BaseProvider


@dataclass
class OpenAIProviderConfig:
    """Configuration class for OpenAI provider settings."""

    api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    dimensions: int = 1536

    # For future agent/tool support
    callbacks: Optional[List[Any]] = None  # Can include LangChain callback handlers

    chat_model_kwargs: Optional[Dict[str, Any]] = None
    embeddings_model_kwargs: Optional[Dict[str, Any]] = None


class OpenAIProvider(BaseProvider):
    """
    Generic OpenAI Provider Class

    This class provides a unified interface to access all OpenAI services
    including chat models, embeddings, and other LangChain integrations.
    """

    def __init__(
        self, api_key: Optional[str] = None, model_name: str = "gpt-3.5-turbo", **kwargs
    ):
        """
        Initialize the OpenAI provider with configuration.

        Args:
            api_key: OpenAI API key (will use environment variable if not provided)
            model_name: Model name for chat (default: "gpt-3.5-turbo")
            **kwargs: All other parameters for chat and embeddings models
        """
        # Initialize config with essential parameters
        self.config = OpenAIProviderConfig(api_key=api_key, model_name=model_name)

        # Setup environment variables if needed
        self._setup_config()
        self.config.streaming = kwargs.get("streaming", False)
        self.config.callbacks = kwargs.get("callbacks", None)

        # Initialize model kwargs from kwargs
        self.config.chat_model_kwargs = kwargs.get("chat_model_kwargs", {})
        self.config.embeddings_model_kwargs = kwargs.get("embeddings_model_kwargs", {})

        # Add all other kwargs to chat_model_kwargs (these will be common parameters)
        common_params = {
            k: v
            for k, v in kwargs.items()
            if k
            not in [
                "chat_model_kwargs",
                "embeddings_model_kwargs",
                "callbacks",
            ]
        }
        self.config.chat_model_kwargs.update(common_params)

        self._chat_model: Optional[BaseChatModel] = None
        self._embeddings_model: Optional[Embeddings] = None

    def _setup_config(self):
        """Setup configuration with environment variables if not provided."""
        if not self.config.api_key:
            self.config.api_key = os.getenv("OPENAI_API_KEY")

    def set_callbacks(self, callbacks: List[Any]):
        self.config.callbacks = callbacks
        self._chat_model = None

    def set_streaming(self, streaming: bool = True):
        self.config.streaming = streaming
        self._chat_model = None

    def get_chat_model(self) -> BaseChatModel:
        if self._chat_model is None:
            params = {
                "api_key": self.config.api_key,
                "model": self.config.model_name,
                "streaming": self.config.streaming,
                "callbacks": self.config.callbacks,
            }
            if self.config.chat_model_kwargs:
                params.update(self.config.chat_model_kwargs)
            params = {k: v for k, v in params.items() if v is not None}
            self._chat_model = ChatOpenAI(**params)
        return self._chat_model

    def get_embeddings_model(self) -> Embeddings:
        """
        Get or create the embeddings model instance.

        Returns:
            OpenAIEmbeddings instance configured with current settings.
        """
        if self._embeddings_model is None:
            # Start with essential parameters
            params = {"api_key": self.config.api_key, "model": "text-embedding-ada-002"}

            # Add all custom kwargs
            if self.config.embeddings_model_kwargs:
                params.update(self.config.embeddings_model_kwargs)

            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}

            self._embeddings_model = OpenAIEmbeddings(**params)
        return self._embeddings_model

    def chat(
        self,
        messages: Union[str, List[BaseMessage], List[Dict[str, str]]],
        system_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Send a chat message and get a response.

        Args:
            messages: The message(s) to send. Can be a string, list of BaseMessage,
                     or list of dicts with 'role' and 'content' keys.
            system_message: Optional system message to prepend.
            **kwargs: Additional parameters to pass to the chat model

        Returns:
            The response from the chat model.
        """
        # Use custom model if kwargs provided, otherwise use cached model
        if kwargs:
            chat_model = self.get_chat_model_with_custom_params(**kwargs)
        else:
            chat_model = self.get_chat_model()

        # Convert messages to proper format
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
            # Convert dict format to BaseMessage objects
            converted_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    converted_messages.append(SystemMessage(content=msg["content"]))
                else:
                    converted_messages.append(HumanMessage(content=msg["content"]))
            messages = converted_messages

        # Add system message if provided
        if system_message:
            messages = [SystemMessage(content=system_message)] + messages

        response = chat_model.invoke(messages)
        return response.content

    async def async_chat(
        self,
        messages: Union[str, List[BaseMessage], List[Dict[str, str]]],
        system_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Async version of chat.

        Args:
            messages: The message(s) to send.
            system_message: Optional system message to prepend.
            **kwargs: Custom chat model params.

        Returns:
            The response from the chat model (string).
        """
        chat_model = (
            self.get_chat_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_chat_model()
        )

        # Convert messages to BaseMessage format
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
            converted_messages = []
            for msg in messages:
                role = msg.get("role")
                if role == "system":
                    converted_messages.append(SystemMessage(content=msg["content"]))
                else:
                    converted_messages.append(HumanMessage(content=msg["content"]))
            messages = converted_messages

        if system_message:
            messages = [SystemMessage(content=system_message)] + messages

        response = await chat_model.ainvoke(messages)
        return response.content

    def embed_text(
        self, text: Union[str, List[str]], **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text.

        Args:
            text: Single text string or list of text strings to embed.
            **kwargs: Additional parameters to pass to the embeddings model

        Returns:
            Embedding vector(s) as list(s) of floats.
        """
        # Use custom model if kwargs provided, otherwise use cached model
        if kwargs:
            embeddings_model = self.get_embeddings_model_with_custom_params(**kwargs)
        else:
            embeddings_model = self.get_embeddings_model()

        if isinstance(text, str):
            return embeddings_model.embed_query(text)
        else:
            return embeddings_model.embed_documents(text)

    async def async_embed_text(
        self, text: Union[str, List[str]], **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Async embedding generator.

        Args:
            text: Input string or list of strings.
            **kwargs: Optional embedding params.

        Returns:
            Embedding vector(s).
        """
        embeddings_model = (
            self.get_embeddings_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_embeddings_model()
        )

        if isinstance(text, str):
            return await embeddings_model.aembed_query(text)
        else:
            return await embeddings_model.aembed_documents(text)

    async def async_embed_documents(
        self, texts: List[str], batch_size: int = 100, **kwargs
    ) -> List[List[float]]:
        """Embed a list of documents.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            EmbeddingResponse with results

        Raises:
            GenericHttpError: If embedding fails
        """
        try:
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = self._embeddings_model.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)

            return {
                "embeddings": all_embeddings,
                "model_name": self.config.model_name,
                "dimensions": self.config.dimensions,
            }
        except Exception as e:
            raise GenericHttpError(f"Failed to embed documents: {str(e)}")

    def embed_documents(self, texts: List[str], batch_size: int = 100, **kwargs):
        """Embed a list of documents.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            EmbeddingResponse with results

        Raises:
            GenericHttpError: If embedding fails
        """
        try:
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = self._embeddings_model.embed_documents(batch, **kwargs)
                all_embeddings.extend(batch_embeddings)

            return {
                "embeddings": all_embeddings,
                "model_name": self.config.model_name,
                "dimensions": self.config.dimensions,
            }
        except Exception as e:
            raise GenericHttpError(f"Failed to embed documents: {str(e)}")

    def create_chain(
        self,
        prompt: BasePromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
        **kwargs,
    ) -> RunnableSequence:
        """
        Create a LangChain runnable sequence.

        Args:
            prompt: The prompt template to use.
            output_parser: Optional output parser for the response.
            **kwargs: Additional parameters to pass to the chat model

        Returns:
            RunnableSequence that can be invoked with inputs.
        """
        # Use custom model if kwargs provided, otherwise use cached model
        if kwargs:
            chat_model = self.get_chat_model_with_custom_params(**kwargs)
        else:
            chat_model = self.get_chat_model()

        if output_parser:
            return prompt | chat_model | output_parser
        else:
            return prompt | chat_model

    async def async_create_chain(
        self,
        prompt: BasePromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
        **kwargs,
    ) -> RunnableSequence:
        """
        Async-compatible chain builder.
        """
        chat_model = (
            self.get_chat_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_chat_model()
        )
        return (
            prompt | chat_model | output_parser
            if output_parser
            else prompt | chat_model
        )

    def create_chat_prompt(
        self,
        messages: List[Dict[str, str]],
        input_variables: Optional[List[str]] = None,
        **kwargs,
    ) -> ChatPromptTemplate:
        """
        Create a chat prompt template.

        Args:
            messages: List of message templates with 'role' and 'content' keys.
            input_variables: Variables that will be formatted in the prompt.
            **kwargs: Additional parameters to pass to ChatPromptTemplate.from_messages

        Returns:
            ChatPromptTemplate instance.
        """
        return ChatPromptTemplate.from_messages(messages, **kwargs)

    def update_config(self, **kwargs):
        """
        Update the provider configuration.

        Args:
            **kwargs: Configuration parameters to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Reset models to force recreation with new config
        self._chat_model = None
        self._embeddings_model = None

    def update_chat_model_kwargs(self, **kwargs):
        """
        Update custom parameters for the chat model.

        Args:
            **kwargs: Custom parameters to pass to ChatOpenAI
        """
        if self.config.chat_model_kwargs is None:
            self.config.chat_model_kwargs = {}
        self.config.chat_model_kwargs.update(kwargs)
        self._chat_model = None  # Reset to force recreation

    def update_embeddings_model_kwargs(self, **kwargs):
        """
        Update custom parameters for the embeddings model.

        Args:
            **kwargs: Custom parameters to pass to OpenAIEmbeddings
        """
        if self.config.embeddings_model_kwargs is None:
            self.config.embeddings_model_kwargs = {}
        self.config.embeddings_model_kwargs.update(kwargs)
        self._embeddings_model = None  # Reset to force recreation

    def get_chat_model_with_custom_params(self, **kwargs) -> BaseChatModel:
        params = {
            "api_key": self.config.api_key,
            "model": self.config.model_name,
            "streaming": self.config.streaming,
            "callbacks": self.config.callbacks,
        }
        if self.config.chat_model_kwargs:
            params.update(self.config.chat_model_kwargs)
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}
        return ChatOpenAI(**params)

    def get_embeddings_model_with_custom_params(self, **kwargs) -> Embeddings:
        """
        Get embeddings model with custom parameters (doesn't affect the cached model).

        Args:
            **kwargs: Custom parameters to pass to OpenAIEmbeddings

        Returns:
            OpenAIEmbeddings instance with custom parameters
        """
        # Start with essential parameters
        params = {"api_key": self.config.api_key, "model": "text-embedding-ada-002"}

        # Add all custom kwargs from config
        if self.config.embeddings_model_kwargs:
            params.update(self.config.embeddings_model_kwargs)

        # Merge with provided kwargs (provided kwargs take precedence)
        params.update(kwargs)

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        return OpenAIEmbeddings(**params)

    def get_raw_chat_model(self, **kwargs) -> BaseChatModel:
        """
        Get the raw chat model instance with optional custom parameters.

        Args:
            **kwargs: Custom parameters to pass to ChatOpenAI

        Returns:
            ChatOpenAI instance
        """
        if kwargs:
            return self.get_chat_model_with_custom_params(**kwargs)
        return self.get_chat_model()

    def get_raw_embeddings_model(self, **kwargs) -> Embeddings:
        """
        Get the raw embeddings model instance with optional custom parameters.

        Args:
            **kwargs: Custom parameters to pass to OpenAIEmbeddings

        Returns:
            OpenAIEmbeddings instance
        """
        if kwargs:
            return self.get_embeddings_model_with_custom_params(**kwargs)
        return self.get_embeddings_model()

    def get_config(self, **kwargs) -> OpenAIProviderConfig:
        """
        Get the current configuration.

        Args:
            **kwargs: Additional parameters (unused, for consistency)

        Returns:
            Current configuration object.
        """
        return self.config

    def validate_config(self, **kwargs) -> bool:
        """
        Validate the current configuration.

        Args:
            **kwargs: Additional parameters (unused, for consistency)

        Returns:
            True if configuration is valid, False otherwise.
        """
        if not self.config.api_key:
            return False
        return True

    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"OpenAIProvider(model={self.config.model_name})"

    def __str__(self) -> str:
        """String representation of the provider."""
        return self.__repr__()

    def run_agent(
        self,
        tools: List[BaseTool],
        prompt: Optional[BasePromptTemplate] = None,
        input: dict = {},
        agent_kwargs: Optional[Dict[str, Any]] = {},
        invoke_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Any:
        agent: CompiledStateGraph = create_react_agent(
            tools=tools, prompt=prompt, model=self.get_chat_model(), **agent_kwargs
        )
        return agent.invoke(input, invoke_kwargs)

    async def async_run_agent(
        self,
        tools: List[BaseTool],
        prompt: Optional[BasePromptTemplate] = None,
        input: dict = {},
        agent_kwargs: Optional[Dict[str, Any]] = {},
        invoke_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Any:
        agent: CompiledStateGraph = create_react_agent(
            tools=tools, prompt=prompt, model=self.get_chat_model(), **agent_kwargs
        )
        return await agent.ainvoke(input, invoke_kwargs)
    
    def stream_agent(
        self,
        tools: List[BaseTool],
        prompt: Optional[BasePromptTemplate] = None,
        input: dict = {},
        agent_kwargs: Optional[Dict[str, Any]] = {},
        invoke_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Any:
        agent: CompiledStateGraph = create_react_agent(
            tools=tools, prompt=prompt, model=self.get_chat_model(), **agent_kwargs
        )
        return agent.stream(input, invoke_kwargs)
    
    async def async_stream_agent(
        self,
        tools: List[BaseTool],
        prompt: Optional[BasePromptTemplate] = None,
        input: dict = {},
        agent_kwargs: Optional[Dict[str, Any]] = {},
        invoke_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Any:
        agent: CompiledStateGraph = create_react_agent(
            tools=tools, prompt=prompt, model=self.get_chat_model(), **agent_kwargs
        )
        return agent.astream(input, invoke_kwargs)
    


# Convenience function for quick setup
def create_openai_provider(
    api_key: Optional[str] = None, model_name: str = "gpt-3.5-turbo", **kwargs
) -> OpenAIProvider:
    """
    Convenience function to create an OpenAI provider with common settings.

    Args:
        api_key: OpenAI API key
        model_name: Model to use for chat
        **kwargs: All other parameters for chat and embeddings models

    Returns:
        Configured OpenAIProvider instance
    """
    return OpenAIProvider(api_key=api_key, model_name=model_name, **kwargs)
