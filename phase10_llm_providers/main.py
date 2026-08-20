import asyncio
from pathlib import Path

from llm import create_provider
from pmcp.client import MCPClient


SERVER_PATH = (
    Path(__file__).parent / "server.py"
)


ALLOWED_TOOLS = {
    "find_customer",
    "get_customer",
    "get_orders",
    "get_order",
    "create_customer",
    "update_customer",
    "create_order",
    "cancel_order",
}


SYSTEM_PROMPT = """
You are a helpful customer service assistant.

You have access to tools for managing customers
and orders.

Rules:

- Use tools when customer or order data is required.
- Never invent customer or order information.
- Never claim an operation succeeded unless the
  tool confirms it.
- Respect errors returned by tools.
- Ask for missing information when necessary.
"""


async def run_agent(
    user_input: str,
    messages: list[dict],
    llm,
    mcp: MCPClient,
    tools: list[dict],
) -> str:

    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    while True:

        response = await llm.chat(
            messages,
            tools,
        )

        # ----------------------------------------------
        # Final answer
        # ----------------------------------------------

        if not response.tool_calls:

            text = response.text or ""

            messages.append(
                {
                    "role": "assistant",
                    "content": text,
                }
            )

            return text

        # ----------------------------------------------
        # Add normalized assistant tool calls
        # to conversation history
        # ----------------------------------------------

        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": call.id,
                        "name": call.name,
                        "arguments": call.arguments,
                    }
                    for call in response.tool_calls
                ],
            }
        )

        # ----------------------------------------------
        # Execute tools
        # ----------------------------------------------

        for call in response.tool_calls:

            print(
                f"\n[Tool requested: {call.name}]"
            )

            print(
                f"[Arguments: {call.arguments}]"
            )

            # ------------------------------------------
            # Client-side allowlist
            # ------------------------------------------

            if call.name not in ALLOWED_TOOLS:

                result = (
                    f"Tool '{call.name}' "
                    f"is not allowed."
                )

            else:

                try:

                    mcp_result = await mcp.call_tool(
                        call.name,
                        call.arguments,
                    )

                    result = str(
                        mcp_result
                    )

                except Exception as exc:

                    result = (
                        f"Tool '{call.name}' "
                        f"failed: {exc}"
                    )

            print(
                f"[Tool result: {result}]"
            )

            # ------------------------------------------
            # Return result to the LLM
            # ------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )


async def main() -> None:

    print(
        "Starting Phase 10..."
    )

    # ----------------------------------------------
    # Create provider
    # ----------------------------------------------

    llm = create_provider()

    # ----------------------------------------------
    # Create MCP client
    # ----------------------------------------------

    a_mcp = MCPClient(
        SERVER_PATH
    )

    await a_mcp.connect()

    try:

        print(
            "Connected to MCP server."
        )

        # ------------------------------------------
        # Discover MCP tools
        # ------------------------------------------

        tools = await a_mcp.list_tools()

        generic_tools = a_mcp.convert_tools(
            tools
        )

        print(
            "\nAvailable MCP tools:"
        )

        for tool in generic_tools:

            print(
                f"  - {tool['name']}"
            )

        # ------------------------------------------
        # Conversation
        # ------------------------------------------

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        print(
            "\nAgent ready."
        )

        print(
            "Type 'exit' or 'quit' to stop."
        )

        # ------------------------------------------
        # Chat loop
        # ------------------------------------------

        while True:

            try:

                user_input = input(
                    "\nUser: "
                ).strip()

            except (
                EOFError,
                KeyboardInterrupt,
            ):

                print(
                    "\nGoodbye."
                )

                break

            if not user_input:
                continue

            if user_input.lower() in {
                "exit",
                "quit",
            }:

                print(
                    "Goodbye."
                )

                break

            try:

                answer = await run_agent(
                    user_input=user_input,
                    messages=messages,
                    llm=llm,
                    mcp=a_mcp,
                    tools=generic_tools,
                )

                print(
                    f"\nAssistant: {answer}"
                )

            except Exception as exc:

                print(
                    f"\nAgent error: {exc}"
                )

    finally:

        await a_mcp.close()

        print(
            "\nMCP connection closed."
        )


if __name__ == "__main__":
    asyncio.run(main())