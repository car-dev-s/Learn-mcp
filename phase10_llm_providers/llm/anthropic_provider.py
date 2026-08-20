import json

from anthropic import AsyncAnthropic

from .base import LLMProvider
from .models import LLMResponse, ToolCall


class AnthropicProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:

        self.client = AsyncAnthropic(
            api_key=api_key
        )

        self.model = model

    @staticmethod
    def _convert_tools(
        tools: list[dict],
    ) -> list[dict]:

        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"],
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

            if role == "user":

                result.append(
                    {
                        "role": "user",
                        "content": message.get(
                            "content",
                            "",
                        ),
                    }
                )

            elif role == "assistant":

                if message.get("tool_calls"):

                    content = []

                    for call in message[
                        "tool_calls"
                    ]:

                        content.append(
                            {
                                "type": "tool_use",
                                "id": call["id"],
                                "name": call["name"],
                                "input": call[
                                    "arguments"
                                ],
                            }
                        )

                    result.append(
                        {
                            "role": "assistant",
                            "content": content,
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
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": message[
                                    "tool_call_id"
                                ],
                                "content": message.get(
                                    "content",
                                    "",
                                ),
                            }
                        ],
                    }
                )

        return result

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:

        system = None

        non_system_messages = []

        for message in messages:

            if message["role"] == "system":
                system = message.get(
                    "content",
                    "",
                )
            else:
                non_system_messages.append(
                    message
                )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=self._convert_messages(
                non_system_messages
            ),
            tools=self._convert_tools(
                tools
            ),
        )

        text_parts = []

        calls = []

        for block in response.content:

            if block.type == "text":

                text_parts.append(
                    block.text
                )

            elif block.type == "tool_use":

                calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )

        return LLMResponse(
            text="".join(text_parts) or None,
            tool_calls=calls,
        )