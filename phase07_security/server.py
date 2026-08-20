import json

from mcp.server.fastmcp import FastMCP

from database import initialize_database
from repository import CustomerRepository

from security import (
    Permission,
    RequestContext,
    Role,
    require_permission,
    validate_amount,
    validate_customer_name,
    validate_email,
    validate_id,
    validate_product,
)

from audit import audit

mcp = FastMCP("customer-mutations-server")

repository = CustomerRepository()

CURRENT_CONTEXT = RequestContext(
    actor="demo-user",
    role=Role.READ_ONLY,
)

# ============================================================
# READ TOOLS
# ============================================================

@mcp.tool()
def find_customer(name: str) -> list[dict]:
    """
    Find customers by partial name.
    """

    try:
        require_permission(
            CURRENT_CONTEXT.role,
            Permission.READ_CUSTOMERS,
        )

        name = validate_customer_name(name)

        customers = repository.find_customer(name)

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="find_customer",
            success=True,
        )

        return [
            {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            }
            for customer in customers
        ]

    except Exception as exc:

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="find_customer",
            success=False,
            details=str(exc),
        )

        raise


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
    """

    try:
        require_permission(
            CURRENT_CONTEXT.role,
            Permission.CREATE_CUSTOMER,
        )

        name = validate_customer_name(name)
        email = validate_email(email)

        customer = repository.create_customer(
            name=name,
            email=email,
        )

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="create_customer",
            success=True,
            details=f"customer_id={customer.id}",
        )

        return {
            "success": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            },
        }

    except Exception as exc:

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="create_customer",
            success=False,
            details=str(exc),
        )

        return {
            "success": False,
            "error": str(exc),
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
    Create an order for a customer.
    """

    try:
        require_permission(
            CURRENT_CONTEXT.role,
            Permission.CREATE_ORDER,
        )

        customer_id = validate_id(
            customer_id,
            "customer_id",
        )

        product = validate_product(product)

        amount = validate_amount(amount)

        order = repository.create_order(
            customer_id=customer_id,
            product=product,
            amount=amount,
        )

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="create_order",
            success=True,
            details=f"order_id={order.id}",
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

    except Exception as exc:

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="create_order",
            success=False,
            details=str(exc),
        )

        return {
            "success": False,
            "error": str(exc),
        }


@mcp.tool()
def cancel_order(order_id: int) -> dict:
    """
    Cancel an order.
    """

    try:
        require_permission(
            CURRENT_CONTEXT.role,
            Permission.CANCEL_ORDER,
        )

        order_id = validate_id(
            order_id,
            "order_id",
        )

        order = repository.cancel_order(order_id)

        if order is None:
            raise ValueError(
                f"Order {order_id} does not exist"
            )

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="cancel_order",
            success=True,
            details=f"order_id={order.id}",
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

    except Exception as exc:

        audit(
            actor=CURRENT_CONTEXT.actor,
            role=CURRENT_CONTEXT.role.value,
            operation="cancel_order",
            success=False,
            details=str(exc),
        )

        return {
            "success": False,
            "error": str(exc),
        }


# ============================================================
# RESOURCES
# ============================================================

@mcp.resource("customers://all")
def get_all_customers() -> str:
    """Return all customers as JSON."""

    require_permission(
        CURRENT_CONTEXT.role,
        Permission.READ_CUSTOMERS,
    )
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

    require_permission(
        CURRENT_CONTEXT.role,
        Permission.READ_CUSTOMERS,
    )
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