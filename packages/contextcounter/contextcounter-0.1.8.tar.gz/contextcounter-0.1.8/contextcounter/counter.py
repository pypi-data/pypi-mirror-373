from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
import importlib, math

Message = Dict[str, Any]

def _maybe_import(mod: str):
    try: return importlib.import_module(mod)
    except Exception: return None

def _openai_len(text: str, model_hint: Optional[str]) -> Optional[int]:
    tk = _maybe_import("tiktoken")
    if not tk: return None
    enc_name = "o200k_base" if model_hint and any(k in model_hint.lower() for k in ["o3","o4","gpt-4.1","gpt-4o"]) else "cl100k_base"
    try: return len(tk.get_encoding(enc_name).encode(text or ""))
    except Exception: return None

def _gpt2_len(text: str) -> Optional[int]:
    tf = _maybe_import("transformers")
    if not tf: return None
    try:
        tok = tf.GPT2TokenizerFast.from_pretrained("gpt2")
        return len(tok.encode(text or ""))
    except Exception:
        return None

def _heur_len(text: str) -> int:
    return math.ceil(len(text or "") / 3.7)

def count_text(text: str, model: Optional[str] = None, provider: Optional[str] = None) -> int:
    name = (model or "").lower()
    prov = (provider or "").lower()

    # ---- Gemini path (try exact SDK preflight first) ----
    if prov in {"google","vertex","google-vertex"} or any(k in name for k in ["gemini","flash"]):
        n = _gemini_len(text, model_hint=model)
        if n is not None:
            return n
        # graceful fallback if SDK unavailable/errored
        for fn in (_gpt2_len, lambda t: _openai_len(t, None)):
            n = fn(text)
            if n is not None: return n
        return _heur_len(text)

    # ---- OpenAI path (tiktoken) ----
    if prov in {"openai","azure-openai"} or any(k in name for k in ["gpt","o3","o4"]):
        for fn in (lambda t: _openai_len(t, model), _gpt2_len):
            n = fn(text)
            if n is not None: return n
        return _heur_len(text)

    # ---- Unknown provider path ----
    for fn in (_gpt2_len, lambda t: _openai_len(t, None)):
        n = fn(text)
        if n is not None: return n
    return _heur_len(text)

def count_messages(messages: Iterable[Message], model: Optional[str] = None,
                   provider: Optional[str] = None, message_overhead_tokens: int = 3,
                   system_overhead_tokens: int = 6) -> int:
    total = 0
    for m in messages:
        content = m.get("content","")
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict) and "text" in p: parts.append(str(p["text"]))
                elif isinstance(p, str): parts.append(p)
            content = "\n".join(parts)
        total += count_text(str(content), model=model, provider=provider)
        total += system_overhead_tokens if m.get("role") == "system" else message_overhead_tokens
    return total


def _gemini_len(text: str, model_hint: str) -> Optional[int]:
    try:
        # Lazy import to avoid hard dependency
        from google import genai
        from google.genai.types import HttpOptions

        client = genai.Client(http_options=HttpOptions(api_version="v1"))
        resp = client.models.count_tokens(model=model_hint, contents=text)
        # Try common shapes
        if isinstance(resp, dict):
            return resp.get("total_tokens") or resp.get("totalTokens")
        return getattr(resp, "total_tokens", None) or getattr(resp, "totalTokens", None)
    except Exception:
        return None
        