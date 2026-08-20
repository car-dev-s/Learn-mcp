from database import initialize_database
from repository import CustomerRepository


def main() -> None:
    initialize_database()

    repository = CustomerRepository()

    print("Test 1: find_customer")
    customers = repository.find_customer("John")

    print(f"customers:{len(customers)}")

    assert len(customers) == 1
    assert customers[0].name == "John Smith"

    print("PASS")

    print("Test 2: get_customer")
    customer = repository.get_customer(2)

    assert customer is not None
    assert customer.name == "Alice Brown"

    print("PASS")

    print("Test 3: unknown customer")
    customer = repository.get_customer(999)

    assert customer is None

    print("PASS")

    print("Test 4: get_orders")
    orders = repository.get_orders(1)

    assert len(orders) == 3

    print("PASS")

    print("All repository tests passed.")


if __name__ == "__main__":
    main()