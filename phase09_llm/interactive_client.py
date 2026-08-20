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

            tools = await session.list_tools()

            print("\nConnected to MCP server.")
            print("\nAvailable tools:")

            for tool in tools.tools:
                print(f"  {tool.name}")

            while True:

                print("\nCommands:")
                print("1. Find customer")
                print("2. Get customer")
                print("3. Create customer")
                print("4. Create order")
                print("5. Cancel order")
                print("6. Exit")

                choice = input("\nChoose: ").strip()

                if choice == "1":

                    name = input(
                        "Customer name: "
                    )

                    result = await session.call_tool(
                        "find_customer",
                        {
                            "name": name,
                        },
                    )

                    print(result)

                elif choice == "2":

                    customer_id = int(
                        input("Customer ID: ")
                    )

                    result = await session.call_tool(
                        "get_customer",
                        {
                            "customer_id": customer_id,
                        },
                    )

                    print(result)

                elif choice == "3":

                    name = input("Name: ")
                    email = input("Email: ")

                    result = await session.call_tool(
                        "create_customer",
                        {
                            "name": name,
                            "email": email,
                        },
                    )

                    print(result)

                elif choice == "4":

                    customer_id = int(
                        input("Customer ID: ")
                    )

                    product = input(
                        "Product: "
                    )

                    amount = float(
                        input("Amount: ")
                    )

                    result = await session.call_tool(
                        "create_order",
                        {
                            "customer_id": customer_id,
                            "product": product,
                            "amount": amount,
                        },
                    )

                    print(result)

                elif choice == "5":

                    order_id = int(
                        input("Order ID: ")
                    )

                    result = await session.call_tool(
                        "cancel_order",
                        {
                            "order_id": order_id,
                        },
                    )

                    print(result)

                elif choice == "6":

                    print("Goodbye.")
                    break

                else:

                    print("Unknown command.")


if __name__ == "__main__":
    asyncio.run(main())