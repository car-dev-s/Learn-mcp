import asyncio
from pathlib import Path
import json

from llm_client import LLMClient
from mcp_client import (
    MCPClient,
    convert_tools_for_openai,
)


SERVER_PATH = (
    Path(__file__).parent / "server.py"
)


async def main() -> None:

    mcp = MCPClient(
        SERVER_PATH
    )

    llm = LLMClient()

    await mcp.connect()

    try:

        tools = await mcp.list_tools()

        llm_tools = convert_tools_for_openai(
            tools
        )

        print("\nAvailable tools:")

        for tool in llm_tools:
            print(
                "-",
                tool["function"]["name"],
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful customer "
                    "service assistant."
                ),
            }
        ]

        while True:

            user_input = input(
                "\nUser: "
            ).strip()

            if user_input.lower() in {
                "exit",
                "quit",
            }:
                break

            messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            response = await llm.chat(
                messages,
                llm_tools,
            )

            message = (
                response.choices[0].message
            )

            if message.content:
                print(
                    "\nAssistant:",
                    message.content,
                )

            messages.append(
                message.model_dump(
                    exclude_none=True
                )
            )

    finally:

        await mcp.close()


if __name__ == "__main__":
    asyncio.run(main())