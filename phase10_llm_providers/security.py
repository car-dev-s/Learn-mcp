from enum import Enum
from dataclasses import dataclass


class Role(str, Enum):
    READ_ONLY = "read_only"
    OPERATOR = "operator"
    ADMIN = "admin"


class Permission(str, Enum):
    READ_CUSTOMERS = "read_customers"
    CREATE_CUSTOMER = "create_customer"
    UPDATE_CUSTOMER = "update_customer"
    CREATE_ORDER = "create_order"
    CANCEL_ORDER = "cancel_order"


ROLE_PERMISSIONS = {
    Role.READ_ONLY: {
        Permission.READ_CUSTOMERS,
    },

    Role.OPERATOR: {
        Permission.READ_CUSTOMERS,
        Permission.CREATE_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
        Permission.CREATE_ORDER,
        Permission.CANCEL_ORDER,
    },

    Role.ADMIN: {
        Permission.READ_CUSTOMERS,
        Permission.CREATE_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
        Permission.CREATE_ORDER,
        Permission.CANCEL_ORDER,
    },
}


def is_allowed(
    role: Role,
    permission: Permission,
) -> bool:

    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(
    role: Role,
    permission: Permission,
) -> None:

    if not is_allowed(role, permission):
        raise PermissionError(
            f"Role '{role.value}' is not allowed "
            f"to perform '{permission.value}'"
        )

def validate_customer_name(name: str) -> str:
    name = name.strip()

    if not name:
        raise ValueError("Customer name cannot be empty")

    if len(name) > 100:
        raise ValueError(
            "Customer name cannot exceed 100 characters"
        )

    return name


def validate_email(email: str) -> str:
    email = email.strip().lower()

    if not email:
        raise ValueError("Email cannot be empty")

    if len(email) > 254:
        raise ValueError(
            "Email cannot exceed 254 characters"
        )

    if "@" not in email:
        raise ValueError("Invalid email address")

    return email


def validate_product(product: str) -> str:
    product = product.strip()

    if not product:
        raise ValueError("Product cannot be empty")

    if len(product) > 200:
        raise ValueError(
            "Product cannot exceed 200 characters"
        )

    return product


def validate_amount(amount: float) -> float:
    if amount <= 0:
        raise ValueError(
            "Amount must be greater than zero"
        )

    if amount > 1_000_000:
        raise ValueError(
            "Amount exceeds allowed maximum"
        )

    return amount


def validate_id(value: int, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(
            f"{field_name} must be an integer"
        )

    if value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero"
        )

    return value


@dataclass(frozen=True)
class RequestContext:
    actor: str
    role: Role