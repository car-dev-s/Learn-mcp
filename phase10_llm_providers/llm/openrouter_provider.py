import json

from openai import AsyncOpenAI

from .base import LLMProvider
from .models import LLMResponse, ToolCall


class OpenRouterProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:

        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        self.model = model

    @staticmethod
    def _convert_tools(
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

    @staticmethod
    def _convert_messages(
        messages: list[dict],
    ) -> list[dict]:

        result = []

        for message in messages:

            role = message["role"]

            if role in {"system", "user"}:

                result.append(
                    {
                        "role": role,
                        "content": message.get(
                            "content",
                            "",
                        ),
                    }
                )

            elif role == "assistant":

                if message.get("tool_calls"):

                    result.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": call["id"],
                                    "type": "function",
                                    "function": {
                                        "name": call["name"],
                                        "arguments": json.dumps(
                                            call["arguments"]
                                        ),
                                    },
                                }
                                for call in message[
                                    "tool_calls"
                                ]
                            ],
                        }
                    )

                else:

                    result.append(
                        {
                            "role": "assistant",
                            "content": message.get(
                                "content",
                                "",
                            ),
                        }
                    )

            elif role == "tool":

                result.append(
                    {
                        "role": "tool",
                        "tool_call_id": message[
                            "tool_call_id"
                        ],
                        "content": message.get(
                            "content",
                            "",
                        ),
                    }
                )

        return result

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:

        response = (
            await self.client.chat.completions.create(
                model=self.model,
                messages=self._convert_messages(
                    messages
                ),
                tools=self._convert_tools(
                    tools
                ),
                tool_choice="auto",
                max_tokens=2600
            )
        )

        message = response.choices[0].message

        calls = []

        for call in message.tool_calls or []:

            calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=json.loads(
                        call.function.arguments
                    ),
                )
            )

        return LLMResponse(
            text=message.content,
            tool_calls=calls,
        )