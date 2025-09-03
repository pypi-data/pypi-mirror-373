# abs_langchain_core/provider/provider_factory.py

from .openai_provider import OpenAIProvider
from .azure_openai_provider import AzureOpenAIProvider
from .claude_provider import ClaudeProvider
from typing import Literal

MODEL_REGISTRY = {
    "openai": OpenAIProvider,
    "azure": AzureOpenAIProvider,
    "claude": ClaudeProvider
}

def create_provider(name: Literal["openai", "azure", "claude"], **kwargs):
    return MODEL_REGISTRY[name](**kwargs)
