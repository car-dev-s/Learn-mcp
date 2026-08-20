from mcp.server.fastmcp import FastMCP


mcp = FastMCP("hello-server")


@mcp.tool()
def hello(name: str) -> str:
    """Return a greeting for the supplied name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()