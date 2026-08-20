# Phase 10 — Multiple LLM Providers for the MCP Client

## Goal

Extend the Phase 9 MCP application so the same MCP server can work with multiple LLM providers without changing the MCP server or business logic.

Providers:
- OpenAI
- Google Gemini
- Anthropic Claude
- OpenRouter
- Local Llama through Ollama

## Architecture

```text
User -> main.py -> LLMProvider
                    |-> OpenAIProvider
                    |-> GeminiProvider
                    |-> AnthropicProvider
                    |-> OpenRouterProvider
                    |-> OllamaProvider
                    |
                    v
                 MCP Client
                    |
               MCP protocol
                    v
                 MCP Server
                    v
          Business / Security / DB
```

The MCP server must remain provider-independent.

## 1. Project Structure

```text
phase10_llm_providers/
├── main.py
├── config.py
├── llm/
│   ├── __init__.py
│   ├── base.py
│   ├── models.py
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   ├── anthropic_provider.py
│   ├── openrouter_provider.py
│   └── ollama_provider.py
├── mcp/
│   ├── __init__.py
│   └── client.py
├── server.py
├── database.py
├── repository.py
├── models.py
├── security.py
├── audit.py
└── seed.py
```

Reuse the files from previous phases.

## 2. Install Dependencies

Use pip, not uv.

```powershell
pip install google-genai anthropic ollama openai
pip list | findstr "mcp openai anthropic google-genai ollama"
```

## 3. Provider-Independent Models

`llm/models.py`:

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
```

## 4. Provider Interface

`llm/base.py`:

```python
from abc import ABC, abstractmethod
from .models import LLMResponse


class LLMProvider(ABC):

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:
        raise NotImplementedError
```

## 5. Generic MCP Tools

The MCP client must expose provider-independent tools. Do not convert MCP tools directly to OpenAI format.

Add to `mcp/client.py`:

```python
def convert_tools(tools) -> list[dict]:
    return [
        {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        }
        for tool in tools.tools
    ]
```

Generic tool format:

```python
{
    "name": "find_customer",
    "description": "Find customers by name",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
}
```

## 6. Generic Messages

User:

```python
{"role": "user", "content": "Find John"}
```

Assistant:

```python
{"role": "assistant", "content": "I found John."}
```

Assistant tool request:

```python
{
    "role": "assistant",
    "tool_calls": [{
        "id": "call-123",
        "name": "find_customer",
        "arguments": {"name": "John"}
    }]
}
```

Tool result:

```python
{
    "role": "tool",
    "tool_call_id": "call-123",
    "name": "find_customer",
    "content": "..."
}
```

Each adapter converts this into its native format.

## 7. OpenAI Provider

`llm/openai_provider.py`:

```python
import json
from openai import AsyncOpenAI
from .base import LLMProvider
from .models import LLMResponse, ToolCall


class OpenAIProvider(LLMProvider):

    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in tools
        ]

    async def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._convert_tools(tools),
            tool_choice="auto",
        )
        message = response.choices[0].message
        calls = [
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=json.loads(call.function.arguments),
            )
            for call in (message.tool_calls or [])
        ]
        return LLMResponse(text=message.content, tool_calls=calls)
```

## 8. OpenRouter Provider

OpenRouter provides an OpenAI-compatible API.

`llm/openrouter_provider.py`:

```python
import json
from openai import AsyncOpenAI
from .base import LLMProvider
from .models import LLMResponse, ToolCall


class OpenRouterProvider(LLMProvider):

    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in tools
        ]

    @staticmethod
    def _convert_messages(messages: list[dict]) -> list[dict]:
        result = []
        for message in messages:
            role = message["role"]
            if role in {"system", "user"}:
                result.append({"role": role, "content": message.get("content", "")})
            elif role == "assistant":
                if message.get("tool_calls"):
                    result.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": call["id"],
                                "type": "function",
                                "function": {
                                    "name": call["name"],
                                    "arguments": json.dumps(call["arguments"]),
                                },
                            }
                            for call in message["tool_calls"]
                        ],
                    })
                else:
                    result.append({"role": "assistant", "content": message.get("content", "")})
            elif role == "tool":
                result.append({
                    "role": "tool",
                    "tool_call_id": message["tool_call_id"],
                    "content": message.get("content", ""),
                })
        return result

    async def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self._convert_messages(messages),
            tools=self._convert_tools(tools),
            tool_choice="auto",
        )
        message = response.choices[0].message
        calls = [
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=json.loads(call.function.arguments),
            )
            for call in (message.tool_calls or [])
        ]
        return LLMResponse(text=message.content, tool_calls=calls)
```

## 9. Claude Provider

`llm/anthropic_provider.py`:

```python
from anthropic import AsyncAnthropic
from .base import LLMProvider
from .models import LLMResponse, ToolCall


class AnthropicProvider(LLMProvider):

    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"],
            }
            for tool in tools
        ]

    @staticmethod
    def _convert_messages(messages: list[dict]) -> list[dict]:
        result = []
        for message in messages:
            role = message["role"]
            if role == "user":
                result.append({"role": "user", "content": message.get("content", "")})
            elif role == "assistant":
                if message.get("tool_calls"):
                    result.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": call["id"],
                                "name": call["name"],
                                "input": call["arguments"],
                            }
                            for call in message["tool_calls"]
                        ],
                    })
                else:
                    result.append({"role": "assistant", "content": message.get("content", "")})
            elif role == "tool":
                result.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": message["tool_call_id"],
                        "content": message.get("content", ""),
                    }],
                })
        return result

    async def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        system = None
        non_system_messages = []
        for message in messages:
            if message["role"] == "system":
                system = message.get("content", "")
            else:
                non_system_messages.append(message)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=self._convert_messages(non_system_messages),
            tools=self._convert_tools(tools),
        )

        text_parts = []
        calls = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        return LLMResponse(
            text="".join(text_parts) or None,
            tool_calls=calls,
        )
```

## 10. Gemini Provider

Use the current `google-genai` SDK. Keep all Gemini-specific request/response conversion inside this file.

`llm/gemini_provider.py`:

```python
from google import genai
from .base import LLMProvider
from .models import LLMResponse


class GeminiProvider(LLMProvider):

    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        raise NotImplementedError(
            "Implement against the installed google-genai version."
        )
```

Before completing this adapter, check the installed SDK:

```powershell
pip show google-genai
```

Then implement against that version's current function-calling API. Do not put Gemini-specific objects into `main.py`.

## 11. Local Llama Through Ollama

Install Ollama separately and pull a model:

```powershell
ollama pull llama3.1:8b
pip install ollama
```

`llm/ollama_provider.py`:

```python
from ollama import AsyncClient
from .base import LLMProvider
from .models import LLMResponse, ToolCall


class OllamaProvider(LLMProvider):

    def __init__(self, model: str, host: str = "http://localhost:11434") -> None:
        self.client = AsyncClient(host=host)
        self.model = model

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in tools
        ]

    @staticmethod
    def _convert_messages(messages: list[dict]) -> list[dict]:
        result = []
        for message in messages:
            role = message["role"]
            if role in {"system", "user"}:
                result.append({"role": role, "content": message.get("content", "")})
            elif role == "assistant":
                if message.get("tool_calls"):
                    result.append({
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {"function": {
                                "name": call["name"],
                                "arguments": call["arguments"],
                            }}
                            for call in message["tool_calls"]
                        ],
                    })
                else:
                    result.append({"role": "assistant", "content": message.get("content", "")})
            elif role == "tool":
                result.append({
                    "role": "tool",
                    "tool_name": message["name"],
                    "content": message.get("content", ""),
                })
        return result

    async def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        response = await self.client.chat(
            model=self.model,
            messages=self._convert_messages(messages),
            tools=self._convert_tools(tools),
        )
        message = response.message
        calls = []
        for index, call in enumerate(message.tool_calls or []):
            calls.append(ToolCall(
                id=f"ollama-call-{index}",
                name=call.function.name,
                arguments=dict(call.function.arguments),
            ))
        return LLMResponse(
            text=message.content or None,
            tool_calls=calls,
        )
```

## 12. Configuration

`config.py`:

```python
import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
```

Treat model names as configuration values.

## 13. Provider Factory

`llm/__init__.py`:

```python
from config import (
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
    LLM_PROVIDER,
    OLLAMA_HOST, OLLAMA_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    OPENROUTER_API_KEY, OPENROUTER_MODEL,
)
from .anthropic_provider import AnthropicProvider
from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider


def create_provider() -> LLMProvider:
    provider = LLM_PROVIDER.lower()

    if provider == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        return OpenAIProvider(OPENAI_API_KEY, OPENAI_MODEL)

    if provider == "gemini":
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        return GeminiProvider(GEMINI_API_KEY, GEMINI_MODEL)

    if provider in {"claude", "anthropic"}:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        return AnthropicProvider(ANTHROPIC_API_KEY, ANTHROPIC_MODEL)

    if provider == "openrouter":
        if not OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")
        return OpenRouterProvider(OPENROUTER_API_KEY, OPENROUTER_MODEL)

    if provider in {"llama", "ollama"}:
        return OllamaProvider(OLLAMA_MODEL, OLLAMA_HOST)

    raise RuntimeError(f"Unknown LLM provider: {LLM_PROVIDER}")
```

## 14. Main Agent Loop

`main.py` must not import any provider SDK. It should only use `create_provider()`.

Use the Phase 9 agent loop and add a maximum tool-call step count:

```python
MAX_AGENT_STEPS = 10
```

Core flow:

```text
User
  |
  v
LLMProvider.chat()
  |
  +-- final text --> return answer
  |
  +-- tool calls --> MCP client --> tool result --> LLMProvider.chat()
```

The full Phase 9 `main.py` can be retained with these changes:

1. Replace direct OpenAI imports with `from llm import create_provider`.
2. Create the provider using `llm = create_provider()`.
3. Pass generic MCP tools to `llm.chat()`.
4. Normalize returned tool calls through `ToolCall`.
5. Limit the loop to `MAX_AGENT_STEPS`.
6. Keep the client-side tool allowlist.

Do not add provider-specific branches to `main.py`.

## 15. Run OpenAI

```powershell
$env:LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="YOUR_KEY"
python phase10_llm_providers\main.py
```

## 16. Run Gemini

```powershell
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="YOUR_KEY"
python phase10_llm_providers\main.py
```

## 17. Run Claude

```powershell
$env:LLM_PROVIDER="claude"
$env:ANTHROPIC_API_KEY="YOUR_KEY"
python phase10_llm_providers\main.py
```

## 18. Run OpenRouter

```powershell
$env:LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="YOUR_KEY"
$env:OPENROUTER_MODEL="MODEL_NAME"
python phase10_llm_providers\main.py
```

## 19. Run Llama

```powershell
ollama list
ollama pull llama3.1:8b
```

Then:

```powershell
$env:LLM_PROVIDER="llama"
$env:OLLAMA_MODEL="llama3.1:8b"
python phase10_llm_providers\main.py
```

## 20. Test Plan

### Test 1 — Simple read

```text
Find the customer named John.
```

Expected tool:

```text
find_customer
```

### Test 2 — Multi-step read

```text
Find John's latest order.
```

Expected approximate sequence:

```text
find_customer -> get_orders
```

### Test 3 — Create

```text
Create a customer named Alice with email alice@example.com.
```

Expected:

```text
create_customer
```

Verify the database afterward.

### Test 4 — Multi-step mutation

```text
Find John's latest order and cancel it.
```

Expected approximate sequence:

```text
find_customer -> get_orders -> cancel_order
```

### Test 5 — Permission handling

Use a read-only context and ask:

```text
Create a customer named Bob.
```

Expected:

```text
create_customer -> permission denied
```

The model must not bypass MCP authorization.

## 21. Provider Comparison

Run the same tests against:

- OpenAI
- Gemini
- Claude
- OpenRouter
- Llama

Record:

```text
Provider:
Model:
Prompt:
Tool calls:
Final answer:
Errors:
```

Measure:

- Tool selection
- Tool arguments
- Tool sequence
- Hallucination
- Error recovery
- Multi-tool reasoning
- Safety behavior
- Latency
- Cost, where applicable

## 22. Security

The LLM is not the security boundary.

Do not rely on a system prompt such as:

```text
Never cancel orders.
```

for authorization.

Use:

```text
LLM
 |
v
MCP Client
 |
v
MCP Server
 |
v
Authorization
 |
+--> ALLOW
+--> DENY
```

The MCP server must enforce permissions.

## 23. Maximum Agent Steps

Always limit the tool loop:

```python
MAX_AGENT_STEPS = 10
```

This prevents an accidental or badly behaving model from creating an unbounded tool loop.

## 24. Logging

Log every model/tool interaction:

```text
[MODEL]
llama3.1:8b

[USER]
Find John's latest order and cancel it.

[TOOL]
find_customer

[ARGS]
{"name": "John"}

[RESULT]
...

[TOOL]
get_orders

[ARGS]
{"customer_id": 12}

[RESULT]
...

[TOOL]
cancel_order

[ARGS]
{"order_id": 88}

[RESULT]
...

[FINAL]
Order 88 has been cancelled.
```

## 25. Completion Checklist

```text
[ ] llm/models.py created
[ ] llm/base.py created
[ ] Generic ToolCall implemented
[ ] Generic LLMResponse implemented
[ ] MCP tools are provider-independent
[ ] OpenAI provider works
[ ] OpenRouter provider works
[ ] Claude provider works
[ ] Gemini provider works
[ ] Ollama provider works
[ ] Llama model can call MCP tools
[ ] Provider factory implemented
[ ] Provider selected through LLM_PROVIDER
[ ] main.py contains no provider SDK imports
[ ] Same MCP server works with all providers
[ ] Multi-step tool calling tested
[ ] Tool arguments tested
[ ] Permission denial tested
[ ] Tool errors tested
[ ] Maximum agent steps implemented
[ ] Tool calls logged
[ ] Results compared between providers
```

## 26. Main Lesson

MCP and the LLM are separate concerns.

```text
LLM
 |
 | decides which tool to call
 v
MCP
 |
 | standardizes tool/context integration
 v
Your application
```

The provider adapters make the different model APIs usable by the same agent.

At the end of Phase 10 you should be able to change:

```powershell
$env:LLM_PROVIDER="openai"
```

to:

```powershell
$env:LLM_PROVIDER="gemini"
```

or:

```powershell
$env:LLM_PROVIDER="claude"
```

or:

```powershell
$env:LLM_PROVIDER="openrouter"
```

or:

```powershell
$env:LLM_PROVIDER="llama"
```

without changing:

```text
server.py
database.py
repository.py
security.py
```

## 27. Next Phase

Phase 11 can move the project toward a real service:

- Streamable HTTP transport
- MCP server as a real service
- Authentication
- Authorization
- Multiple MCP clients
- Docker
- Remote tool discovery
- Production logging
- Health checks
- Timeouts
- Retry handling
