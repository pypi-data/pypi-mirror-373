from dataclasses import dataclass
from typing import Optional, Dict, Any, Union, List
import os

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import BasePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence
from langchain.agents import AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_core.tools import BaseTool
from .base_provider import BaseProvider
from langgraph.prebuilt.chat_agent_executor import (
    create_react_agent,
    CompiledStateGraph,
)


@dataclass
class AzureOpenAIProviderConfig:
    api_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    api_version: str = "2024-02-15-preview"
    chat_model_kwargs: Optional[Dict[str, Any]] = None
    embeddings_model_kwargs: Optional[Dict[str, Any]] = None


class AzureOpenAIProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        **kwargs
    ):
        self.config = AzureOpenAIProviderConfig(
            api_key=api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=api_version,
        )
        self.config.chat_model_kwargs = kwargs.get("chat_model_kwargs", {})
        self.config.embeddings_model_kwargs = kwargs.get("embeddings_model_kwargs", {})
        self.config.chat_model_kwargs.update(
            {
                k: v
                for k, v in kwargs.items()
                if k not in ["chat_model_kwargs", "embeddings_model_kwargs"]
            }
        )
        self._chat_model = None
        self._embeddings_model = None

    def get_chat_model(self) -> BaseChatModel:
        if not self._chat_model:
            params = {
                "api_key": self.config.api_key,
                "azure_endpoint": self.config.azure_endpoint,
                "api_version": self.config.api_version,
                **self.config.chat_model_kwargs,
            }
            self._chat_model = AzureChatOpenAI(**params)
        return self._chat_model

    def get_embeddings_model(self) -> Embeddings:
        if not self._embeddings_model:
            params = {
                "api_key": self.config.api_key,
                "azure_endpoint": self.config.azure_endpoint,
                "api_version": self.config.api_version,
                **self.config.embeddings_model_kwargs,
            }
            self._embeddings_model = AzureOpenAIEmbeddings(**params)
        return self._embeddings_model

    def chat(
        self,
        messages: Union[str, List[BaseMessage], List[Dict[str, str]]],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        chat_model = (
            self.get_chat_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_chat_model()
        )

        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
            converted_messages = [
                (
                    SystemMessage(content=m["content"])
                    if m["role"] == "system"
                    else HumanMessage(content=m["content"])
                )
                for m in messages
            ]
            messages = converted_messages

        if system_message:
            messages = [SystemMessage(content=system_message)] + messages

        return chat_model.invoke(messages).content

    async def async_chat(
        self,
        messages: Union[str, List[BaseMessage], List[Dict[str, str]]],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        chat_model = (
            self.get_chat_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_chat_model()
        )

        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
            converted_messages = [
                (
                    SystemMessage(content=m["content"])
                    if m["role"] == "system"
                    else HumanMessage(content=m["content"])
                )
                for m in messages
            ]
            messages = converted_messages

        if system_message:
            messages = [SystemMessage(content=system_message)] + messages

        return (await chat_model.ainvoke(messages)).content

    def embed_text(
        self, text: Union[str, List[str]], **kwargs
    ) -> Union[List[float], List[List[float]]]:
        model = (
            self.get_embeddings_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_embeddings_model()
        )
        return (
            model.embed_query(text)
            if isinstance(text, str)
            else model.embed_documents(text)
        )

    async def async_embed_text(
        self, text: Union[str, List[str]], **kwargs
    ) -> Union[List[float], List[List[float]]]:
        model = (
            self.get_embeddings_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_embeddings_model()
        )
        return (
            await model.aembed_query(text)
            if isinstance(text, str)
            else await model.aembed_documents(text)
        )

    def embed_documents(self, texts: List[str], **kwargs) -> List[List[float]]:
        model = (
            self.get_embeddings_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_embeddings_model()
        )
        return model.embed_documents(texts)

    async def async_embed_documents(
        self, texts: List[str], **kwargs
    ) -> List[List[float]]:
        model = (
            self.get_embeddings_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_embeddings_model()
        )
        return await model.aembed_documents(texts)

    def create_chain(
        self,
        prompt: BasePromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
        **kwargs
    ) -> RunnableSequence:
        model = (
            self.get_chat_model_with_custom_params(**kwargs)
            if kwargs
            else self.get_chat_model()
        )
        return prompt | model | output_parser if output_parser else prompt | model

    def create_chat_prompt(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(messages, **kwargs)

    def get_chat_model_with_custom_params(self, **kwargs) -> BaseChatModel:
        return AzureChatOpenAI(
            api_key=self.config.api_key,
            azure_endpoint=self.config.azure_endpoint,
            api_version=self.config.api_version,
            **{**self.config.chat_model_kwargs, **kwargs}
        )

    def get_embeddings_model_with_custom_params(self, **kwargs) -> Embeddings:
        return AzureOpenAIEmbeddings(
            api_key=self.config.api_key,
            azure_endpoint=self.config.azure_endpoint,
            api_version=self.config.api_version,
            **{**self.config.embeddings_model_kwargs, **kwargs}
        )

    def update_config(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
        self._chat_model = None
        self._embeddings_model = None

    def validate_config(self) -> bool:
        return all(
            [
                self.config.api_key,
                self.config.azure_endpoint,
            ]
        )

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
        return agent.invoke(input, **invoke_kwargs)

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
        return await agent.ainvoke(input, **invoke_kwargs)

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
        return agent.stream(input, **invoke_kwargs)

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
        return agent.astream(input, **invoke_kwargs)
