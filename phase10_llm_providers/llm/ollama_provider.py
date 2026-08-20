from ollama import AsyncClient

from .base import LLMProvider
from .models import LLMResponse, ToolCall


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        model: str,
        host: str = "http://localhost:11434",
    ) -> None:

        self.client = AsyncClient(
            host=host
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

            if role in {
                "system",
                "user",
            }:

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
                            "content": "",
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": call[
                                            "name"
                                        ],
                                        "arguments": call[
                                            "arguments"
                                        ],
                                    }
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
                        "tool_name": message[
                            "name"
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

        response = await self.client.chat(
            model=self.model,
            messages=self._convert_messages(
                messages
            ),
            tools=self._convert_tools(
                tools
            ),
        )

        message = response.message

        calls = []

        for index, call in enumerate(
            message.tool_calls or []
        ):

            calls.append(
                ToolCall(
                    id=f"ollama-call-{index}",
                    name=call.function.name,
                    arguments=dict(
                        call.function.arguments
                    ),
                )
            )

        return LLMResponse(
            text=message.content or None,
            tool_calls=calls,
        )