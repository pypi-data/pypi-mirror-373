from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import BasePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence
from langgraph.prebuilt.chat_agent_executor import (
    create_react_agent,
    CompiledStateGraph,
)
from langchain.agents.agent_types import AgentType
from langchain_core.tools import BaseTool
from .base_provider import BaseProvider


@dataclass
class ClaudeProviderConfig:
    api_key: Optional[str] = None
    model_name: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    chat_model_kwargs: Optional[Dict[str, Any]] = None


class ClaudeProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        **kwargs
    ):
        self.config = ClaudeProviderConfig(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            model_name=model_name,
            temperature=temperature,
            chat_model_kwargs=kwargs.get("chat_model_kwargs", {}),
        )
        self.config.chat_model_kwargs.update(
            {k: v for k, v in kwargs.items() if k != "chat_model_kwargs"}
        )
        self._chat_model = None

    def get_chat_model(self) -> BaseChatModel:
        if not self._chat_model:
            params = {
                "api_key": self.config.api_key,
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                **self.config.chat_model_kwargs,
            }
            self._chat_model = ChatAnthropic(**params)
        return self._chat_model

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
            messages = [
                (
                    SystemMessage(content=m["content"])
                    if m["role"] == "system"
                    else HumanMessage(content=m["content"])
                )
                for m in messages
            ]
        if system_message:
            messages = [SystemMessage(content=system_message)] + messages
        return (await chat_model.ainvoke(messages)).content

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
            messages = [
                (
                    SystemMessage(content=m["content"])
                    if m["role"] == "system"
                    else HumanMessage(content=m["content"])
                )
                for m in messages
            ]
        if system_message:
            messages = [SystemMessage(content=system_message)] + messages
        return chat_model.invoke(messages).content

    def get_chat_model_with_custom_params(self, **kwargs) -> BaseChatModel:
        base_params = {
            "api_key": self.config.api_key,
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            **self.config.chat_model_kwargs,
        }
        base_params.update(kwargs)
        return ChatAnthropic(**base_params)

    def embed_text(self, text: Union[str, List[str]], **kwargs) -> List[float]:
        raise NotImplementedError(
            "Claude does not support native embeddings via LangChain."
        )

    async def async_embed_text(
        self, text: Union[str, List[str]], **kwargs
    ) -> List[float]:
        raise NotImplementedError(
            "Claude does not support native embeddings via LangChain."
        )

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

    def update_config(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
        self._chat_model = None

    def validate_config(self) -> bool:
        return bool(self.config.api_key)

    def run_agent(
        self,
        tools: List[BaseTool],
        prompt: Optional[BasePromptTemplate] = None,
        input: dict = {},
        agent_kwargs: Optional[Dict[str, Any]] = None,
        invoke_kwargs: Optional[Dict[str, Any]] = None,
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

    def embed_documents(self, texts: List[str], **kwargs) -> List[List[float]]:
        raise NotImplementedError(
            "Claude does not support native embeddings via LangChain."
        )

    async def async_embed_documents(
        self, texts: List[str], **kwargs
    ) -> List[List[float]]:
        raise NotImplementedError(
            "Claude does not support native embeddings via LangChain."
        )

    def get_embeddings_model(self):
        raise NotImplementedError(
            "Claude does not support native embeddings via LangChain."
        )
