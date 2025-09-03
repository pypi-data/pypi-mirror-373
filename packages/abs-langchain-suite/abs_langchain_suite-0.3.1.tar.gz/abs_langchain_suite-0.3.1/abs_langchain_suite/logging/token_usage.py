from langchain_core.callbacks import BaseCallbackHandler
from datetime import datetime, UTC
from time import perf_counter
from .pricing.service import PricingService


class DBTokenUsageLogger(BaseCallbackHandler):
    def __init__(self, db_client, table="token_usage",metadata={},**kwargs):
        self.db_client = db_client
        self.table = table
        self.metadata = metadata
        self.provider = kwargs.get("provider", kwargs.get("llm", "unknown"))
        self.model_name = kwargs.get("model_name", kwargs.get("model", "unknown"))
        self.pricing_service = PricingService()
        self._start_time = None

    def on_llm_start(self, serialized, prompts, **kwargs):
        self._start_time = perf_counter()
        # Log prompt(s)
        if hasattr(prompts, "messages"):
            for message in prompts.messages:
                if message.type == "human":
                    self.db_client.write(self.table, {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "provider": self.provider,
                        "model_name": self.model_name,
                        "prompt": message.content,
                        "token_usage": 0,
                        "metadata": self.metadata,
                        "created_at": datetime.now(UTC).isoformat(),
                    })
        elif hasattr(prompts, "content"):
            self.db_client.write(self.table, {
                "timestamp": datetime.now(UTC).isoformat(),
                "provider": self.provider,
                "model_name": self.model_name,
                "prompt": prompts.content,
                "token_usage": 0,
                "metadata": self.metadata,
                "created_at": datetime.now(UTC).isoformat(),
            })

    def on_llm_end(self, response, **kwargs):
        end_time = perf_counter()
        duration = None
        if self._start_time is not None:
            duration = end_time - self._start_time
        usage = None
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage")
        elif hasattr(response, "usage_metadata"):
            usage = response.usage_metadata

        if (hasattr(response, 'generations')):
            generation = response.generations[0][0] if response.generations and response.generations[0] else None
            message = getattr(generation, "message", None)

        if usage is None:
            usage = getattr(message, "usage_metadata", {})

        if usage:
            try:
                cost_usd = self.pricing_service.calculate_chat_cost(
                    provider=self.provider,
                    model=self.model_name,
                    input_tokens=usage.get("input_tokens", usage.get("prompt_tokens", 0)),
                    output_tokens=usage.get("output_tokens", usage.get("completion_tokens", 0)),
                    cache_input_tokens=usage.get("prompt_tokens_details", {}).get("cached_tokens", 0),
                )
            except Exception as e:
                cost_usd = 0
            token_usage = {
                "provider": self.provider,
                "model_name": self.model_name,
                "input_tokens": usage.get("input_tokens", usage.get("prompt_tokens", 0)),
                "output_tokens": usage.get("output_tokens", usage.get("completion_tokens", 0)),
                "completion_tokens_details":usage.get("completion_tokens_details",{}),
                "prompt_tokens_details":usage.get("prompt_tokens_details",{}),
                "total_tokens": usage.get("total_tokens", 0),
                "cost_usd": cost_usd,
            }
            usage_log = {
                "usage": token_usage,
                "provider": self.provider,
                "metadata": self.metadata,
                "duration": duration,
                "created_at": datetime.now(UTC).isoformat(),
            }
            self.db_client.write(self.table, usage_log)

    def on_embedding_end(self, response, **kwargs):
        usage = response.get("usage", {}) if isinstance(response, dict) else None
        if usage:
            try:
                cost_usd = self.pricing_service.calculate_embedding_cost(
                    provider=self.provider,
                    model=self.model_name,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=0,
                )
            except Exception as e:
                cost_usd = 0
            token_usage = {
                "provider": self.provider,
                "model_name": self.model_name,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": 0,
                "total_tokens": usage.get("total_tokens", 0),
                "cost_usd": cost_usd,
            }
            usage_log = {
                "usage": token_usage,
                "metadata": self.metadata,
                "provider": self.provider,
                "created_at": datetime.now(UTC).isoformat(),
            }
            self.db_client.write(self.table, usage_log)

    def on_llm_error(self, error, **kwargs):
        end_time = perf_counter()
        duration = None
        if self._start_time is not None:
            duration = end_time - self._start_time
        model_name = kwargs.get("model_name", kwargs.get("model", "unknown"))
        token_usage = {
            "provider": self.provider,
            "model_name": self.model_name,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0,
        }
        usage_log = {
            "usage": token_usage,
            "provider": self.provider,
            "status": "error",
            "error_message": str(error),
            "metadata": self.metadata,
            "duration": duration,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.db_client.write(self.table, usage_log)
