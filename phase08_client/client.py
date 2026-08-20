import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).parent / "server.py"


async def main() -> None:

    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(
        server_parameters
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            print("Connected to MCP server")

            # ----------------------------------------
            # Discover tools
            # ----------------------------------------

            tools = await session.list_tools()

            print("\nAvailable tools:")

            for tool in tools.tools:
                # print("\n----------------")
                # print("Name:", tool.name)
                # print("Description:", tool.description)
                # print("Input schema:")
                # print(tool.inputSchema)
                print(
                    f"- {tool.name}: "
                    f"{tool.description}"
                )

            # ----------------------------------------
            # Call a tool
            # ----------------------------------------

            result = await session.call_tool(
                "find_customer",
                {
                    "name": "John",
                },
            )

            print("\nfind_customer result:")
            print(result)

            result = await session.call_tool(
                "create_customer",
                {
                    "name": "MCP Client User",
                    "email": "mcp-client@example.com",
                },
            )

            print(result)

            resources = await session.list_resources()

            print("\nAvailable resources:")

            for resource in resources.resources:
                print(
                    f"- {resource.uri}"
                )

            result = await session.read_resource(
                "customers://all"
            )

            print("\nResource:")
            print(result)



if __name__ == "__main__":
    asyncio.run(main())