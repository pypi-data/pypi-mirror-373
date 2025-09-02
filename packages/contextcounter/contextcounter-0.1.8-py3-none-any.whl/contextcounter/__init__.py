from __future__ import annotations
from typing import Any, Iterable, Dict

from .counter import count_text, count_messages
from .analytics import analyze_messages, split_prompt_completion, summarize_provider_usage
from .providers import openai_context_window, anthropic_context_window, gemini_context_window

def get_context_limit(model: str, provider: str | None = None, gemini_overrides: dict | None = None) -> int | None:
    p = (provider or "").lower()
    name = (model or "").lower()

    if p in {"openai","azure-openai"} or any(k in name for k in ("gpt","o3","o4")):
        return openai_context_window(model)
    if p in {"anthropic"} or "claude" in name:
        return anthropic_context_window(model)
    if p in {"google","vertex","google-vertex"} or any(k in name for k in ("gemini","flash")):
        return gemini_context_window(model, overrides=gemini_overrides or {})
    return None

class ContextInspector:
    def __init__(self, provider: str | None = None, gemini_overrides: dict | None = None):
        self.provider = provider
        self._gemini_overrides = gemini_overrides or {}

    def count_text(self, text: str, model: str | None = None) -> int:
        return count_text(text, model=model, provider=self.provider)

    def count_messages(self, messages: Iterable[Dict[str, Any]], model: str | None = None) -> int:
        return count_messages(messages, model=model, provider=self.provider)
    
    def get_limit(self, model: str) -> int | None:
        return get_context_limit(model, provider=self.provider, gemini_overrides=self._gemini_overrides)

    def will_exceed(self, tokens: int, model: str, reserve: int = 1024) -> bool | None:
        limit = self.get_limit(model)
        return None if limit is None else (tokens + reserve > limit)

__all__ = [
    "ContextInspector",
    "count_text",
    "count_messages",
    "get_context_limit",
    "analyze_messages",
    "split_prompt_completion",
    "summarize_provider_usage",
]
