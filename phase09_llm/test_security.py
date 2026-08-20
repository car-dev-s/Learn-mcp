from security import (
    Permission,
    Role,
    is_allowed,
    require_permission,
    validate_amount,
    validate_customer_name,
    validate_email,
    validate_id,
)


def main() -> None:

    print("Test 1: read-only can read")

    assert is_allowed(
        Role.READ_ONLY,
        Permission.READ_CUSTOMERS,
    )

    print("PASS")


    print("Test 2: read-only cannot create")

    assert not is_allowed(
        Role.READ_ONLY,
        Permission.CREATE_CUSTOMER,
    )

    print("PASS")


    print("Test 3: operator can create")

    assert is_allowed(
        Role.OPERATOR,
        Permission.CREATE_CUSTOMER,
    )

    print("PASS")


    print("Test 4: invalid name")

    try:
        validate_customer_name("")
        assert False
    except ValueError:
        pass

    print("PASS")


    print("Test 5: invalid amount")

    try:
        validate_amount(-10)
        assert False
    except ValueError:
        pass

    print("PASS")


    print("Test 6: invalid ID")

    try:
        validate_id(0, "customer_id")
        assert False
    except ValueError:
        pass

    print("PASS")


    print("Test 7: invalid email")

    try:
        validate_email("invalid")
        assert False
    except ValueError:
        pass

    print("PASS")


    print("All security tests passed.")


if __name__ == "__main__":
    main()