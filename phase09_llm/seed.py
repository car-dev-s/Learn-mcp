from database import get_connection, initialize_database


CUSTOMERS = [
    (1, "John Smith", "john@example.com"),
    (2, "Alice Brown", "alice@example.com"),
    (3, "David Cohen", "david@example.com"),
]


ORDERS = [
    (1001, 1, "Laptop", 1299.99, "DELIVERED", "2026-07-30T10:00:00"),
    (1002, 1, "Keyboard", 99.99, "SHIPPED", "2026-08-06T10:00:00"),
    (1003, 1, "Mouse", 49.99, "PENDING", "2026-08-08T10:00:00"),
    (2001, 2, "Monitor", 499.99, "DELIVERED", "2026-08-02T10:00:00"),
    (3001, 3, "Headphones", 199.99, "PENDING", "2026-08-07T10:00:00"),
]


def seed_database() -> None:
    initialize_database()

    with get_connection() as connection:

        connection.executemany(
            """
            INSERT OR IGNORE INTO customers (
                id,
                name,
                email
            )
            VALUES (?, ?, ?)
            """,
            CUSTOMERS,
        )

        connection.executemany(
            """
            INSERT OR IGNORE INTO orders (
                id,
                customer_id,
                product,
                amount,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ORDERS,
        )


if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully.")