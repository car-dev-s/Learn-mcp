import asyncio
import json
from pathlib import Path

from llm_client import LLMClient
from mcp_client import MCPClient, convert_tools_for_openai


SERVER_PATH = Path(__file__).parent / "server.py"

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

You have access to tools for managing customers and orders.

Rules:
- Use tools when the user's request requires customer or order data.
- Never invent customer or order information.
- Never claim an operation succeeded unless the tool confirms it.
- Respect errors returned by the tools.
- Ask the user for missing information when necessary.
"""


async def run_agent(
    user_input: str,
    messages: list[dict],
    llm: LLMClient,
    mcp: MCPClient,
    llm_tools: list[dict],
) -> str:

    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    while True:

        # --------------------------------------------------
        # Ask the LLM what to do
        # --------------------------------------------------

        response = await llm.chat(
            messages,
            llm_tools,
        )

        message = response.choices[0].message

        # --------------------------------------------------
        # No tool call -> final answer
        # --------------------------------------------------

        if not message.tool_calls:

            assistant_text = message.content or ""

            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_text,
                }
            )

            return assistant_text

        # --------------------------------------------------
        # Store assistant's tool-call message
        # --------------------------------------------------

        messages.append(
            message.model_dump(
                exclude_none=True
            )
        )

        # --------------------------------------------------
        # Execute every requested tool
        # --------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            # ----------------------------------------------
            # Security: client-side allowlist
            # ----------------------------------------------

            if tool_name not in ALLOWED_TOOLS:

                error_message = (
                    f"Tool '{tool_name}' "
                    f"is not allowed."
                )

                print(
                    f"\n[BLOCKED TOOL: {tool_name}]"
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": error_message,
                    }
                )

                continue

            # ----------------------------------------------
            # Parse arguments
            # ----------------------------------------------

            try:

                arguments = json.loads(
                    tool_call.function.arguments
                )

            except json.JSONDecodeError as exc:

                error_message = (
                    "Invalid JSON arguments "
                    f"for tool '{tool_name}': {exc}"
                )

                print(
                    f"\n[INVALID TOOL ARGUMENTS]"
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": error_message,
                    }
                )

                continue

            # ----------------------------------------------
            # Log tool call
            # ----------------------------------------------

            print(
                f"\n[LLM requested tool: {tool_name}]"
            )

            print(
                f"[Arguments: {arguments}]"
            )

            # ----------------------------------------------
            # Execute MCP tool
            # ----------------------------------------------

            try:

                result = await mcp.call_tool(
                    tool_name,
                    arguments,
                )

                print(
                    f"[MCP result: {result}]"
                )

                tool_result = str(result)

            except Exception as exc:

                print(
                    f"[MCP tool error: {exc}]"
                )

                tool_result = (
                    f"Tool '{tool_name}' failed: "
                    f"{exc}"
                )

            # ----------------------------------------------
            # Send result back to LLM
            # ----------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

        # --------------------------------------------------
        # Loop again.
        #
        # The LLM now receives the tool results and can:
        #
        #   1. call another tool
        #   2. produce the final answer
        #
        # --------------------------------------------------


async def main() -> None:

    print("Starting Phase 9 MCP + LLM client...")

    # ------------------------------------------------------
    # Create MCP client
    # ------------------------------------------------------

    mcp = MCPClient(
        SERVER_PATH
    )

    # ------------------------------------------------------
    # Create LLM client
    # ------------------------------------------------------

    llm = LLMClient()

    # ------------------------------------------------------
    # Connect to MCP server
    # ------------------------------------------------------

    await mcp.connect()

    try:

        print("Connected to MCP server.")

        # --------------------------------------------------
        # Discover MCP tools
        # --------------------------------------------------

        tools = await mcp.list_tools()

        print("\nMCP tools:")

        for tool in tools.tools:

            print(
                f"  - {tool.name}"
            )

        # --------------------------------------------------
        # Convert MCP tools to OpenAI format
        # --------------------------------------------------

        llm_tools = convert_tools_for_openai(
            tools
        )

        # --------------------------------------------------
        # Conversation history
        # --------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        print(
            "\nPhase 9 agent ready."
        )

        print(
            "Type 'exit' or 'quit' to stop."
        )

        # --------------------------------------------------
        # Interactive loop
        # --------------------------------------------------

        while True:

            try:

                user_input = input(
                    "\nUser: "
                ).strip()

            except (EOFError, KeyboardInterrupt):

                print("\nGoodbye.")

                break

            if not user_input:
                continue

            if user_input.lower() in {
                "exit",
                "quit",
            }:

                print("Goodbye.")

                break

            # ------------------------------------------------
            # Run agent
            # ------------------------------------------------

            try:

                answer = await run_agent(
                    user_input=user_input,
                    messages=messages,
                    llm=llm,
                    mcp=mcp,
                    llm_tools=llm_tools,
                )

                print(
                    f"\nAssistant: {answer}"
                )

            except Exception as exc:

                print(
                    f"\nAgent error: {exc}"
                )

    finally:

        # --------------------------------------------------
        # Always close MCP connection
        # --------------------------------------------------

        await mcp.close()

        print(
            "\nMCP connection closed."
        )


if __name__ == "__main__":
    asyncio.run(main())