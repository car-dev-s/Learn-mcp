import json

from mcp.server.fastmcp import FastMCP

from database import initialize_database
from repository import CustomerRepository


mcp = FastMCP("customer-sqlite-server")

repository = CustomerRepository()


# ============================================================
# Tools
# ============================================================

@mcp.tool()
def find_customer(name: str) -> list[dict]:
    """
    Find customers whose name contains the supplied text.
    """

    customers = repository.find_customer(name)

    return [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        }
        for customer in customers
    ]


@mcp.tool()
def get_customer(customer_id: int) -> dict | None:
    """
    Get a customer by ID.
    """

    customer = repository.get_customer(customer_id)

    if customer is None:
        return None

    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
    }


@mcp.tool()
def get_orders(customer_id: int) -> list[dict]:
    """
    Get all orders belonging to a customer.
    """

    orders = repository.get_orders(customer_id)

    return [
        {
            "id": order.id,
            "customer_id": order.customer_id,
            "product": order.product,
            "amount": order.amount,
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]


@mcp.tool()
def get_order(order_id: int) -> dict | None:
    """
    Get an order by ID.
    """

    order = repository.get_order(order_id)

    if order is None:
        return None

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "product": order.product,
        "amount": order.amount,
        "status": order.status,
        "created_at": order.created_at,
    }


# ============================================================
# Resources
# ============================================================

@mcp.resource("customers://all")
def get_all_customers() -> str:
    """
    Return all customers as JSON.
    """

    customers = repository.get_all_customers()

    result = [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        }
        for customer in customers
    ]

    return json.dumps(result, indent=2)


@mcp.resource("customers://{customer_id}")
def get_customer_resource(customer_id: int) -> str:
    """
    Return a customer resource as JSON.
    """

    customer = repository.get_customer(customer_id)

    if customer is None:
        return json.dumps(
            {
                "error": "Customer not found",
                "customer_id": customer_id,
            },
            indent=2,
        )

    result = {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
    }

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    initialize_database()
    mcp.run()