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

    def create_customer(
            self,
            name: str,
            email: str,
    ) -> Customer:

        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError("Customer name cannot be empty")

        if not email:
            raise ValueError("Customer email cannot be empty")

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO customers (name, email)
                VALUES (?, ?)
                """,
                (name, email),
            )

            customer_id = cursor.lastrowid

        customer = self.get_customer(customer_id)

        if customer is None:
            raise RuntimeError(
                "Customer was created but could not be retrieved"
            )

        return customer

    def update_customer(
            self,
            customer_id: int,
            name: str,
            email: str,
    ) -> Customer | None:

        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError("Customer name cannot be empty")

        if not email:
            raise ValueError("Customer email cannot be empty")

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE customers
                SET name  = ?,
                    email = ?
                WHERE id = ?
                """,
                (name, email, customer_id),
            )

            if cursor.rowcount == 0:
                return None

        return self.get_customer(customer_id)

    def create_order(
            self,
            customer_id: int,
            product: str,
            amount: float,
    ) -> Order:

        product = product.strip()

        if not product:
            raise ValueError("Product cannot be empty")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        customer = self.get_customer(customer_id)

        if customer is None:
            raise ValueError(
                f"Customer {customer_id} does not exist"
            )

        created_at = datetime.now(timezone.utc).isoformat()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO orders (customer_id,
                                    product,
                                    amount,
                                    status,
                                    created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    product,
                    amount,
                    "PENDING",
                    created_at,
                ),
            )

            order_id = cursor.lastrowid

        order = self.get_order(order_id)

        if order is None:
            raise RuntimeError(
                "Order was created but could not be retrieved"
            )

        return order

    def cancel_order(
            self,
            order_id: int,
    ) -> Order | None:

        order = self.get_order(order_id)

        if order is None:
            return None

        if order.status == "CANCELLED":
            return order

        if order.status == "DELIVERED":
            raise ValueError(
                "A delivered order cannot be cancelled"
            )

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE orders
                SET status = 'CANCELLED'
                WHERE id = ?
                """,
                (order_id,),
            )

        return self.get_order(order_id)

