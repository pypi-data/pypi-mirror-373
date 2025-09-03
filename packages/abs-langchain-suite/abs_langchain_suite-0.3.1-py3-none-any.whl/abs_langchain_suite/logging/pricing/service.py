# pricing/service.py

class PricingService:
    # Rates per thousand tokens (USD) (per 1k)
    OPENAI_CHAT = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-2024-08-06": {"input": 0.0025, "output": 0.0100, "cache-input": 0.0013},
        "gpt-4o-mini": {"input": 0.0006, "output": 0.0024},
        "o1-mini": {"input": 0.0002, "output": 0.0006},
        "o1": {"input": 0.003, "output": 0.015},
        "o1-pro": {"input": 0.15, "output": 0.6},
        "o3-mini": {"input": 0.0011, "output": 0.0044},
        "o3": {"input": 0.01, "output": 0.04},
        "gpt-4.1-nano": {"input": 0.001, "output": 0.004},
        "gpt-4.1": {"input": 0.02, "output": 0.08},
    }

    OPENAI_EMBEDDING = {
        "text-embedding-3-small": {"input": 0.02},   # $0.02 per 1K → $20 per M :contentReference[oaicite:3]{index=3}
        "text-embedding-3-large": {"input": 0.13},  # $0.13 per 1K :contentReference[oaicite:4]{index=4}
        "text-embedding-ada-002": {"input": 0.10},  # $0.10 per 1K :contentReference[oaicite:5]{index=5}
    }

    AZURE_CHAT = {k: v for k, v in OPENAI_CHAT.items()}  # same but can apply markup in future

    CLAUDE_CHAT = {
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
        "claude-haiku": {"input": 0.0008, "output": 0.004},     # Haiku 3.5 :contentReference[oaicite:6]{index=6}
        "claude-sonnet": {"input": 0.003, "output": 0.015},     # Sonnet 3.7/4 :contentReference[oaicite:7]{index=7}
        "claude-opus": {"input": 0.015, "output": 0.075},      # Opus 3/4 :contentReference[oaicite:8]{index=8}
    }

    @classmethod
    def calculate_chat_cost(cls, provider: str, model: str, input_tokens: int, output_tokens: int, cache_input_tokens: int = 0) -> float:
        provider = provider.lower()
        key = model.lower()

        table = None
        if provider in ("azure", "azureopenai"):
            table = cls.AZURE_CHAT
        elif provider == "openai":
            table = cls.OPENAI_CHAT
        elif provider in ("anthropic", "claude"):
            table = cls.CLAUDE_CHAT

        entry = next((v for k, v in table.items() if k == key), None)
        if not entry:
            return 0.0

        cost = round((input_tokens/1000)*entry["input"] + (output_tokens/1000)*entry["output"] + (cache_input_tokens/1000)*entry["cache-input"], 3)
        return cost

    @classmethod
    def calculate_embedding_cost(cls, provider: str, model: str, input_tokens: int) -> float:
        provider = provider.lower()
        if provider == "openai":
            table = cls.OPENAI_EMBEDDING
            entry = next((v for k, v in table.items() if k in model.lower()), None)
            if not entry:
                return 0.0
            return round((input_tokens/1e6)*entry["input"], 6)

        # Anthropic doesn't provide own embeddings
        return 0.0
