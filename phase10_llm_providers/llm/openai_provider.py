import json

from openai import AsyncOpenAI

from .base import LLMProvider
from .models import LLMResponse, ToolCall


class OpenAIProvider(LLMProvider):

    def __init__(
            self,
            api_key: str,
            model: str,
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key
        )

        self.model = model

    async def chat(
            self,
            messages: list[dict],
            tools: list[dict],
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        tool_calls = []

        for call in message.tool_calls or []:
            arguments = json.loads(
                call.function.arguments
            )

            tool_calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=arguments,
                )
            )

        return LLMResponse(
            text=message.content,
            tool_calls=tool_calls,
        )

    def convert_tools(
            tools: list[dict],
    ) -> list[dict]:
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
