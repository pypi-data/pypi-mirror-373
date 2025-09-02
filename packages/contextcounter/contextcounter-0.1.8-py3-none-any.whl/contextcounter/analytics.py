from __future__ import annotations
from typing import Any, Dict, Iterable, Optional, Tuple, Union
from .counter import count_text

Message = Dict[str, Any]

def _extract_text_from_content(content: Union[str, list, dict]) -> str:
    # Flattens common multimodal formats to text
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict) and "text" in p:
                parts.append(str(p["text"]))
            elif isinstance(p, str):
                parts.append(p)
        return "\n".join(parts)
    if isinstance(content, dict):
        # Some SDKs put { "type": "text", "text": "..." }
        return str(content.get("text", "")) if "text" in content else ""
    return ""

def _count_tool_calls_in_message(m: Message) -> int:
    # OpenAI-style: assistant message includes "tool_calls": [...]
    tc = m.get("tool_calls")
    if isinstance(tc, list):
        return len(tc)
    # Some schemas use role="tool" messages (each is one call result)
    if m.get("role") == "tool":
        return 1
    return 0

def analyze_messages(
    messages: Iterable[Message],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    message_overhead_tokens: int = 3,
    system_overhead_tokens: int = 6,
) -> Dict[str, Any]:
    """
    Returns a rich breakdown:
    {
      "total_tokens": int,
      "by_role": {"system": int, "user": int, "assistant": int, "tool": int},
      "details": [{"role": ..., "content_tokens": int, "overhead": int, "tool_calls": int}, ...],
      "num_messages": int,
      "num_tool_calls": int
    }
    """
    by_role = {"system": 0, "user": 0, "assistant": 0, "tool": 0, "other": 0}
    details = []
    total = 0
    tool_calls_total = 0
    num_messages = 0

    for m in messages:
        num_messages += 1
        role = str(m.get("role", "other"))
        content = _extract_text_from_content(m.get("content", ""))

        content_tokens = count_text(content, model=model, provider=provider)
        overhead = system_overhead_tokens if role == "system" else message_overhead_tokens
        tool_calls = _count_tool_calls_in_message(m)

        part_total = content_tokens + overhead
        total += part_total
        by_role[role] = by_role.get(role, 0) + part_total
        tool_calls_total += tool_calls

        details.append({
            "role": role,
            "content_tokens": content_tokens,
            "overhead": overhead,
            "tool_calls": tool_calls,
        })

    return {
        "total_tokens": total,
        "by_role": by_role,
        "details": details,
        "num_messages": num_messages,
        "num_tool_calls": tool_calls_total,
    }

def split_prompt_completion(
    request_messages: Iterable[Message],
    response_text: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    message_overhead_tokens: int = 3,
    system_overhead_tokens: int = 6,
) -> Dict[str, int]:
    """
    Offline estimate of prompt vs. completion tokens.
    If you pass response_text (assistant text), we'll compute completion tokens too.
    """
    breakdown = analyze_messages(
        request_messages,
        model=model,
        provider=provider,
        message_overhead_tokens=message_overhead_tokens,
        system_overhead_tokens=system_overhead_tokens,
    )
    prompt_tokens = breakdown["total_tokens"]

    completion_tokens = 0
    if response_text is not None:
        completion_tokens = count_text(response_text, model=model, provider=provider) + message_overhead_tokens

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }

def summarize_provider_usage(
    usage: Dict[str, Any],
    provider: Optional[str] = None
) -> Dict[str, Optional[int]]:
    """
    Normalize provider 'usage' objects (if you have them from API responses)
    into a common schema:
    {
      "prompt_tokens": int|None,
      "completion_tokens": int|None,
      "reasoning_tokens": int|None,
      "total_tokens": int|None
    }

    - OpenAI: response.usage may include .prompt_tokens, .completion_tokens, .total_tokens, .reasoning_tokens (o3/o4)
    - Anthropic: response.usage often has .input_tokens, .output_tokens, maybe .cache_creation_input_tokens, .reasoning_tokens (varies)
    """
    prov = (provider or "").lower()
    norm = {"prompt_tokens": None, "completion_tokens": None, "reasoning_tokens": None, "total_tokens": None}

    # Try OpenAI-like keys
    for k_src, k_dst in [
        ("prompt_tokens", "prompt_tokens"),
        ("completion_tokens", "completion_tokens"),
        ("total_tokens", "total_tokens"),
        ("reasoning_tokens", "reasoning_tokens"),
    ]:
        if k_src in usage:
            norm[k_dst] = usage.get(k_src)

    # Try Anthropic-like keys if still missing
    if prov == "anthropic" or (norm["prompt_tokens"] is None and "input_tokens" in usage):
        norm["prompt_tokens"] = usage.get("input_tokens", norm["prompt_tokens"])
    if prov == "anthropic" or (norm["completion_tokens"] is None and "output_tokens" in usage):
        norm["completion_tokens"] = usage.get("output_tokens", norm["completion_tokens"])
    if norm["total_tokens"] is None and norm["prompt_tokens"] is not None and norm["completion_tokens"] is not None:
        norm["total_tokens"] = norm["prompt_tokens"] + norm["completion_tokens"]

    # Anthropic sometimes exposes reasoning tokens under different keys; pass through if found
    for maybe in ("reasoning_tokens", "output_tokens_reasoning"):
        if usage.get(maybe) is not None and norm["reasoning_tokens"] is None:
            norm["reasoning_tokens"] = usage.get(maybe)

    return norm
