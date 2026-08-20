from openai import AsyncOpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


class LLMClient:

    def __init__(self) -> None:

        self.client = AsyncOpenAI(
            api_key=OPENAI_API_KEY
        )

        self.model = OPENAI_MODEL


    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
    ):

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        return response