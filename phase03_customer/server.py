from mcp.server.fastmcp import FastMCP

from data import customers, orders


mcp = FastMCP("customer-server")


@mcp.tool()
def find_customer(name: str) -> list[dict]:
    """
    Find customers whose name contains the supplied text.

    The search is case-insensitive.
    Returns an empty list when no customers match.
    """

    search_text = name.strip().lower()

    if not search_text:
        return []

    matches = [
        customer
        for customer in customers
        if search_text in customer.name.lower()
    ]

    return [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        }
        for customer in matches
    ]


@mcp.tool()
def get_customer(customer_id: int) -> dict | None:
    """
    Get a customer by its ID.

    Returns null when the customer does not exist.
    """

    for customer in customers:
        if customer.id == customer_id:
            return {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            }

    return None


@mcp.tool()
def get_orders(customer_id: int) -> list[dict]:
    """
    Get all orders belonging to a customer.

    Returns an empty list when the customer has no orders.
    """

    customer_orders = [
        order
        for order in orders
        if order.customer_id == customer_id
    ]

    return [
        {
            "id": order.id,
            "customer_id": order.customer_id,
            "product": order.product,
            "amount": order.amount,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
        }
        for order in customer_orders
    ]


@mcp.tool()
def get_order(order_id: int) -> dict | None:
    """
    Get an order by its ID.

    Returns null when the order does not exist.
    """

    for order in orders:
        if order.id == order_id:
            return {
                "id": order.id,
                "customer_id": order.customer_id,
                "product": order.product,
                "amount": order.amount,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
            }

    return None


if __name__ == "__main__":
    mcp.run()