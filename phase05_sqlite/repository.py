from database import get_connection
from models import Customer, Order


class CustomerRepository:

    def find_customer(self, name: str) -> list[Customer]:
        search_text = name.strip()

        if not search_text:
            return []

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, name, email
                FROM customers
                WHERE name LIKE ?
                ORDER BY id
                """,
                (f"%{search_text}%",),
            ).fetchall()

        return [
            Customer(
                id=row["id"],
                name=row["name"],
                email=row["email"],
            )
            for row in rows
        ]

    def get_customer(self, customer_id: int) -> Customer | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, name, email
                FROM customers
                WHERE id = ?
                """,
                (customer_id,),
            ).fetchone()

        if row is None:
            return None

        return Customer(
            id=row["id"],
            name=row["name"],
            email=row["email"],
        )

    def get_orders(self, customer_id: int) -> list[Order]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    customer_id,
                    product,
                    amount,
                    status,
                    created_at
                FROM orders
                WHERE customer_id = ?
                ORDER BY id
                """,
                (customer_id,),
            ).fetchall()

        return [
            Order(
                id=row["id"],
                customer_id=row["customer_id"],
                product=row["product"],
                amount=row["amount"],
                status=row["status"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_order(self, order_id: int) -> Order | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    customer_id,
                    product,
                    amount,
                    status,
                    created_at
                FROM orders
                WHERE id = ?
                """,
                (order_id,),
            ).fetchone()

        if row is None:
            return None

        return Order(
            id=row["id"],
            customer_id=row["customer_id"],
            product=row["product"],
            amount=row["amount"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def get_all_customers(self) -> list[Customer]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, name, email
                FROM customers
                ORDER BY id
                """
            ).fetchall()

        return [
            Customer(
                id=row["id"],
                name=row["name"],
                email=row["email"],
            )
            for row in rows
        ]

