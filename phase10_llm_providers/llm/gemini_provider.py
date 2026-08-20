import json

from google import genai

from .base import LLMProvider
from .models import LLMResponse, ToolCall


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    @staticmethod
    def _convert_tools(
        tools: list[dict],
    ) -> list[dict]:

        return [
            {
                "type": "function",
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
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

            if role == "system":

                continue

            if role == "user":

                result.append(
                    {
                        "type": "user_input",
                        "content": [
                            {
                                "type": "text",
                                "text": message.get(
                                    "content",
                                    "",
                                ),
                            }
                        ],
                    }
                )

            elif role == "assistant":

                if message.get("tool_calls"):

                    for call in message[
                        "tool_calls"
                    ]:

                        result.append(
                            {
                                "type": "function_call",
                                "id": call["id"],
                                "name": call["name"],
                                "arguments": call[
                                    "arguments"
                                ],
                            }
                        )

                else:

                    result.append(
                        {
                            "type": "model_output",
                            "content": [
                                {
                                    "type": "text",
                                    "text": message.get(
                                        "content",
                                        "",
                                    ),
                                }
                            ],
                        }
                    )

            elif role == "tool":

                result.append(
                    {
                        "type": "function_result",
                        "name": message["name"],
                        "call_id": message[
                            "tool_call_id"
                        ],
                        "result": [
                            {
                                "type": "text",
                                "text": message.get(
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

        system_instruction = None

        for message in messages:

            if message["role"] == "system":

                system_instruction = (
                    message.get(
                        "content",
                        "",
                    )
                )

                break

        interaction = await self.client.aio.interactions.create(
            model=self.model,
            input=self._convert_messages(
                messages
            ),
            tools=self._convert_tools(
                tools
            ),
            system_instruction=system_instruction,
        )

        text_parts = []

        calls = []

        for step in interaction.steps:

            if step.type == "function_call":

                calls.append(
                    ToolCall(
                        id=step.id,
                        name=step.name,
                        arguments=step.arguments,
                    )
                )

            elif step.type == "text":

                text_parts.append(
                    getattr(
                        step,
                        "text",
                        "",
                    )
                )

        return LLMResponse(
            text="".join(text_parts) or None,
            tool_calls=calls,
        )