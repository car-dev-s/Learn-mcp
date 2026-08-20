from dataclasses import dataclass
from datetime import datetime


@dataclass
class Customer:
    id: int
    name: str
    email: str


@dataclass
class Order:
    id: int
    customer_id: int
    product: str
    amount: float
    status: str
    created_at: datetime