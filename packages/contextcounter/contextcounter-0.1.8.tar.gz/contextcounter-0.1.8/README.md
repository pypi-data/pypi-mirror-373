# 📦 ContextCounter

**ContextCounter** is a lightweight Python library for:

- 🔍 **Fetching context window limits** across LLM providers (OpenAI, Anthropic, Gemini)  
- 📊 **Counting tokens** in text or chat messages, with safe fallbacks  
- ✅ **Checking if you’re about to exceed context**  
- 🛠 **Detailed analytics**: count tool calls, reasoning tokens, and token splits by role

It works out-of-the-box with no dependencies, and can optionally integrate with official SDKs for precise context sizes.

---

## 🚀 Installation

```bash
pip install contextcounter
```

Optional extras (for better accuracy):

```bash
pip install "contextcounter[openai]"       # precise OpenAI context limits
pip install "contextcounter[anthropic]"    # precise Anthropic context limits
pip install "contextcounter[tokenizers]"   # local tokenizers (tiktoken, transformers)
```

---

## ⚡ Quickstart

```python
from contextcounter import ContextInspector

# create inspector bound to a provider (openai, anthropic, google/vertex)
ctx = ContextInspector(provider="openai")

# fetch context window for a model
limit = ctx.get_limit("gpt-4o")
print("Context window:", limit)

# count tokens in free text
tokens = ctx.count_text("Hello world", model="gpt-4o")
print("Tokens:", tokens)

# count tokens in a chat-style message list
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Summarize this in 5 points."},
]
msg_tokens = ctx.count_messages(messages, model="gpt-4o")
print("Message tokens:", msg_tokens)

# check if it will exceed
print("Will exceed?", ctx.will_exceed(msg_tokens, "gpt-4o", reserve=2048))
```

---

## 📖 API Reference

### `ContextInspector`

```python
from contextcounter import ContextInspector

ctx = ContextInspector(provider="openai")
```

- **`provider`**: `"openai" | "anthropic" | "google" | "vertex" | None`  
  - If given, you don’t need to repeat provider in every function.  
- **`gemini_overrides`** *(dict, optional)*: override documented Gemini limits (default is `1_000_000` tokens).

---

### `ctx.get_limit(model: str) -> int | None`

Returns the maximum context window for the given model.

- For **OpenAI** models: will query live API if `openai` package is installed & authenticated.  
- For **Anthropic**: will query live API if `anthropic` package is installed & authenticated.  
- For **Gemini**: uses documented defaults (`1,000,000`) unless overridden.  
- Fallback: internal static defaults.

```python
ctx = ContextInspector(provider="anthropic")
print(ctx.get_limit("claude-3-7-sonnet"))  # 200000
```

---

### `ctx.count_text(text: str, model: str | None = None) -> int`

Returns the number of tokens in a plain text string.

- Tries **tiktoken** if available (for OpenAI models).  
- Falls back to **GPT-2 tokenizer** if `transformers` installed.  
- Last resort: **heuristic** (≈1 token per ~3.7 characters).

```python
print(ctx.count_text("Hello world", model="gpt-4o"))  # → 5 (approx.)
```

---

### `ctx.count_messages(messages: list, model: str | None = None) -> int`

Returns the number of tokens in a chat-style message list.

- Adds **structural overhead tokens** per message (default: 3 tokens, 6 for system role).  
- Handles content as strings or lists (for multimodal formats).

```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Tell me a joke."}
]
print(ctx.count_messages(messages, model="gpt-4o"))  # → ~20
```

---

### `ctx.will_exceed(tokens: int, model: str, reserve: int = 1024) -> bool | None`

Checks whether a given token count plus a **reserve buffer** will exceed the model’s context window.

- Returns `True` if it will exceed, `False` otherwise, `None` if limit unknown.

```python
tokens = ctx.count_messages(messages, model="gpt-4o")
print(ctx.will_exceed(tokens, "gpt-4o", reserve=2048))
```

---

### Standalone Functions

If you don’t want to use the `ContextInspector` class, you can import the core functions:

```python
from contextcounter import get_context_limit, count_text, count_messages

print(get_context_limit("gpt-4o", provider="openai"))
print(count_text("Hello", model="gpt-4o", provider="openai"))
```

---

## 🔎 Detailed Analytics

In addition to simple counts, ContextCounter can provide **detailed breakdowns**:  
- Number of tool calls  
- Token usage by role (system/user/assistant/tool)  
- Prompt vs. completion split  
- Reasoning tokens (when provided by the API usage object)  

### `analyze_messages`

```python
from contextcounter import analyze_messages

report = analyze_messages(messages, model="gpt-4o", provider="openai")
print(report)
# {
#   "total_tokens": 123,
#   "by_role": {"system": 10, "user": 45, "assistant": 60, "tool": 8, "other": 0},
#   "details": [
#       {"role":"system","content_tokens":4,"overhead":6,"tool_calls":0},
#       {"role":"user","content_tokens":42,"overhead":3,"tool_calls":0},
#       {"role":"assistant","content_tokens":57,"overhead":3,"tool_calls":2},
#   ],
#   "num_messages": 3,
#   "num_tool_calls": 2
# }
```

---

### `split_prompt_completion`

```python
from contextcounter import split_prompt_completion

split = split_prompt_completion(messages, response_text="assistant reply...", model="gpt-4o", provider="openai")
print(split)
# {"prompt_tokens": 88, "completion_tokens": 35, "total_tokens": 123}
```

---

### `summarize_provider_usage`

Normalize `usage` dictionaries from API responses (OpenAI, Anthropic, etc.) into a consistent schema.

```python
from contextcounter import summarize_provider_usage

openai_usage = {
    "prompt_tokens": 81,
    "completion_tokens": 40,
    "total_tokens": 121,
    "reasoning_tokens": 12,
}
norm = summarize_provider_usage(openai_usage, provider="openai")
print(norm)
# {"prompt_tokens":81,"completion_tokens":40,"reasoning_tokens":12,"total_tokens":121}
```

---

## 🔧 Supported Models & Defaults

| Provider   | Model Example           | Context Limit (tokens) |
|------------|-------------------------|-------------------------|
| OpenAI     | gpt-4o, gpt-4.1         | 128,000                |
| OpenAI     | o3                      | 200,000                |
| Anthropic  | claude-3-7-sonnet       | 200,000                |
| Anthropic  | claude-3-5-sonnet/haiku | 200,000                |
| Google     | gemini-1.5-pro/flash    | 1,000,000              |

> Live API calls (OpenAI, Anthropic) will override these defaults if you have SDKs installed + credentials configured.

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📌 Roadmap

- ✅ Token counting across providers  
- ✅ Context limit retrieval with fallbacks  
- ✅ Tool call counting + split by role  
- ✅ Prompt vs. completion split  
- ✅ Reasoning tokens via provider usage normalization  
- 🔜 Native Gemini token counting (when tokenizer becomes public)  
- 🔜 More granular overhead estimation per provider  

---

## 📄 License

MIT © Nemlig ADK
