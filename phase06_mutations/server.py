import json

from mcp.server.fastmcp import FastMCP

from database import initialize_database
from repository import CustomerRepository


mcp = FastMCP("customer-mutations-server")

repository = CustomerRepository()


# ============================================================
# READ TOOLS
# ============================================================

@mcp.tool()
def find_customer(name: str) -> list[dict]:
    """Find customers by partial name."""

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
    """Get a customer by ID."""

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
    """Get all orders for a customer."""

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
    """Get an order by ID."""

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
# WRITE TOOLS
# ============================================================

@mcp.tool()
def create_customer(
    name: str,
    email: str,
) -> dict:
    """
    Create a new customer.

    Email addresses must be unique.
    """

    try:
        customer = repository.create_customer(
            name=name,
            email=email,
        )

        return {
            "success": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            },
        }

    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": "Unable to create customer",
            "details": str(exc),
        }


@mcp.tool()
def update_customer(
    customer_id: int,
    name: str,
    email: str,
) -> dict:
    """
    Update an existing customer.
    """

    try:
        customer = repository.update_customer(
            customer_id=customer_id,
            name=name,
            email=email,
        )

        if customer is None:
            return {
                "success": False,
                "error": "Customer not found",
                "customer_id": customer_id,
            }

        return {
            "success": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            },
        }

    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except Exception:
        return {
            "success": False,
            "error": "Unable to update customer",
        }


@mcp.tool()
def create_order(
    customer_id: int,
    product: str,
    amount: float,
) -> dict:
    """
    Create a new order for an existing customer.
    """

    try:
        order = repository.create_order(
            customer_id=customer_id,
            product=product,
            amount=amount,
        )

        return {
            "success": True,
            "order": {
                "id": order.id,
                "customer_id": order.customer_id,
                "product": order.product,
                "amount": order.amount,
                "status": order.status,
                "created_at": order.created_at,
            },
        }

    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except Exception:
        return {
            "success": False,
            "error": "Unable to create order",
        }


@mcp.tool()
def cancel_order(order_id: int) -> dict:
    """
    Cancel an existing order.

    Delivered orders cannot be cancelled.
    """

    try:
        order = repository.cancel_order(order_id)

        if order is None:
            return {
                "success": False,
                "error": "Order not found",
                "order_id": order_id,
            }

        return {
            "success": True,
            "order": {
                "id": order.id,
                "customer_id": order.customer_id,
                "product": order.product,
                "amount": order.amount,
                "status": order.status,
                "created_at": order.created_at,
            },
        }

    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except Exception:
        return {
            "success": False,
            "error": "Unable to cancel order",
        }


# ============================================================
# RESOURCES
# ============================================================

@mcp.resource("customers://all")
def get_all_customers() -> str:
    """Return all customers as JSON."""

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
    """Return a customer resource as JSON."""

    customer = repository.get_customer(customer_id)

    if customer is None:
        return json.dumps(
            {
                "error": "Customer not found",
                "customer_id": customer_id,
            },
            indent=2,
        )

    return json.dumps(
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        },
        indent=2,
    )


if __name__ == "__main__":
    initialize_database()
    mcp.run()