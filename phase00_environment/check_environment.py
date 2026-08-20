import sys

import mcp


def main() -> None:
    print("=" * 50)
    print("MCP Learning Project - Phase 0")
    print("=" * 50)

    print(f"Python version : {sys.version.split()[0]}")
    print(f"Python path    : {sys.executable}")
    print(f"MCP version    : {getattr(mcp, '__version__', 'unknown')}")
    print()
    print("MCP import     : OK")

    print("=" * 50)


if __name__ == "__main__":
    main()