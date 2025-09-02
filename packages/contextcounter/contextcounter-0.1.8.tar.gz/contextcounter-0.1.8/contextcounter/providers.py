from __future__ import annotations
from functools import lru_cache
from typing import Optional, Dict

def _try_import(mod: str):
    try:
        return __import__(mod)
    except Exception:
        return None

@lru_cache(maxsize=128)
def openai_context_window(model: str) -> Optional[int]:
    if not _try_import("openai"): return None
    from openai import OpenAI
    try:
        info = OpenAI().models.retrieve(model)
        return getattr(info, "context_window", None)
    except Exception:
        return None

@lru_cache(maxsize=128)
def anthropic_context_window(model: str) -> Optional[int]:
    if not _try_import("anthropic"): return None
    import anthropic
    try:
        info = anthropic.Anthropic().models.retrieve(model)
        return info.get("max_context_tokens") if isinstance(info, dict) else getattr(info, "max_context_tokens", None)
    except Exception:
        return None

GEMINI_DEFAULTS: Dict[str, int] = {
    "gemini-2.5-pro": 1_048_576,       
    "gemini-2.5-flash": 1_048_576,      
    "gemini-2.0-flash": 1_048_576,  
    "gemini-2.0-flash-lite": 1_048_576,  
    "gemini-1.5-pro": 2_097_152,         
    "gemini-1.5-flash": 1_048_576
}

def gemini_context_window(model: str, overrides: Optional[Dict[str, int]] = None) -> Optional[int]:
    table = {**GEMINI_DEFAULTS, **(overrides or {})}
    if model in table: return table[model]
    lo = model.lower()
    for k, v in table.items():
        if k in lo: return v
    return None
