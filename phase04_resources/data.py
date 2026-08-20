from datetime import datetime, timedelta

from models import Customer, Order


customers = [
    Customer(
        id=1,
        name="John Smith",
        email="john@example.com",
    ),
    Customer(
        id=2,
        name="Alice Brown",
        email="alice@example.com",
    ),
    Customer(
        id=3,
        name="David Cohen",
        email="david@example.com",
    ),
]


now = datetime.now()

orders = [
    Order(
        id=1001,
        customer_id=1,
        product="Laptop",
        amount=1299.99,
        status="DELIVERED",
        created_at=now - timedelta(days=10),
    ),
    Order(
        id=1002,
        customer_id=1,
        product="Keyboard",
        amount=99.99,
        status="SHIPPED",
        created_at=now - timedelta(days=3),
    ),
    Order(
        id=1003,
        customer_id=1,
        product="Mouse",
        amount=49.99,
        status="PENDING",
        created_at=now - timedelta(days=1),
    ),
    Order(
        id=2001,
        customer_id=2,
        product="Monitor",
        amount=499.99,
        status="DELIVERED",
        created_at=now - timedelta(days=7),
    ),
    Order(
        id=3001,
        customer_id=3,
        product="Headphones",
        amount=199.99,
        status="PENDING",
        created_at=now - timedelta(days=2),
    ),
]