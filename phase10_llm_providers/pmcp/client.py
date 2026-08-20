import sys
from pathlib import Path

from mcp import (
    ClientSession,
    StdioServerParameters,
)
from mcp.client.stdio import stdio_client


class MCPClient:

    def __init__(
        self,
        server_path: Path,
    ) -> None:

        self.server_path = server_path

        self._stdio_context = None
        self._session_context = None

        self.session = None


    async def connect(self) -> None:

        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(self.server_path)],
        )

        self._stdio_context = stdio_client(
            parameters
        )

        read, write = await self._stdio_context.__aenter__()

        self._session_context = ClientSession(
            read,
            write,
        )

        self.session = (
            await self._session_context.__aenter__()
        )

        await self.session.initialize()


    async def close(self) -> None:

        if self._session_context:
            await self._session_context.__aexit__(
                None,
                None,
                None,
            )

        if self._stdio_context:
            await self._stdio_context.__aexit__(
                None,
                None,
                None,
            )


    async def list_tools(self):

        return await self.session.list_tools()


    async def call_tool(
        self,
        name: str,
        arguments: dict,
    ):

        return await self.session.call_tool(
            name,
            arguments,
        )

    def convert_tools(self,tools) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
            for tool in tools.tools
        ]

def get_tools(
    tools,
) -> list[dict]:

    result = []

    for tool in tools.tools:

        result.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
        )

    return result

