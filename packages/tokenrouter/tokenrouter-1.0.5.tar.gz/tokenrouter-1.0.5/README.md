# TokenRouter Python SDK

Official Python SDK for TokenRouter — an intelligent LLM router that provides OpenAI‑compatible endpoints and a native routing endpoint.

This README focuses on the routing interfaces you’ll use today:
- client.create(...) → Native routing endpoint (/route)
- client.chat.completions.create(...) → OpenAI chat completions (/v1/chat/completions)
- client.completions.create(...) → OpenAI legacy text completions (/v1/completions)

All calls are BYOK. Provide your TokenRouter API key, and configure provider keys in TokenRouter.

## Installation

```bash
pip install tokenrouter
```

## Quick Start (Native Route)

```python
from tokenrouter import TokenRouter

client = TokenRouter(
    api_key="tr_...",
    base_url="http://localhost:8000"  # or https://api.tokenrouter.io
)

response = client.create(
  model="auto",
  mode="balanced",
  model_preferences=["gpt-4o", "gpt-4o-mini"],
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
)

print(response.choices[0].message.content)
```

## Endpoints

### Native Route (/route)

OpenAI‑like request/response shape plus TokenRouter metadata: cost_usd, latency_ms, routed_model, routed_provider, service_tier, etc.

Non‑streaming
```python
response = client.create(
  model="auto",
  mode="balanced",
  model_preferences=["gpt-4o", "gpt-4o-mini"],
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
)
print(response.choices[0].message.content)
```

Streaming
```python
for chunk in client.create(
  model="auto",
  stream=True,
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Stream a short greeting."}
  ],
):
  delta = (chunk.choices[0].get("delta", {}) if chunk.choices else {})
  if delta.get("content"):
    print(delta["content"], end="")
```

### Chat Completions (/v1/chat/completions)

OpenAI‑compatible chat completions.

Non‑streaming
```python
response = client.chat.completions.create(
  model="auto",
  mode="balanced",
  model_preferences=["gpt-4o", "gpt-4o-mini"],
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
)
print(response.choices[0].message.content)
```

Streaming
```python
for chunk in client.chat.completions.create(
  model="auto",
  stream=True,
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
):
  delta = (chunk.choices[0].get("delta", {}) if chunk.choices else {})
  if delta.get("content"):
    print(delta["content"], end="")
```

### Legacy Completions (/v1/completions)

OpenAI legacy text completion format. The SDK returns the raw OpenAI‑style dict.

Non‑streaming
```python
resp = client.completions.create(
  model="auto",
  prompt="Say this is a test",
  mode="balanced",
)
print(resp["choices"][0]["text"])  # text completion shape
```

Streaming
```python
for chunk in client.completions.create(
  model="auto",
  prompt="Stream this as text",
  stream=True,
):
  if chunk.get("choices"):
    print(chunk["choices"][0].get("text", ""), end="")
```

## Errors

```python
from tokenrouter import AuthenticationError, RateLimitError, InvalidRequestError, APIConnectionError

try:
  response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="auto"
  )
  print(response.choices[0].message.content)
except RateLimitError as e:
  print(f"Rate limited, retry after: {e.retry_after}s")
except AuthenticationError:
  print("Invalid API key")
except InvalidRequestError as e:
  print(f"Invalid request: {e}")
except APIConnectionError as e:
  print(f"Connection error: {e}")
```

## Environment

```bash
export TOKENROUTER_API_KEY=tr_your-api-key
# Optional
export TOKENROUTER_BASE_URL=https://api.tokenrouter.io
```

## Using OpenAI SDK against TokenRouter

```python
from openai import OpenAI
client = OpenAI(api_key="sk_...", base_url="https://api.tokenrouter.io/v1")
response = client.chat.completions.create(
  model="auto",
  messages=[{"role": "user", "content": "Hello"}],
)
```
