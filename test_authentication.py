
from modules.authentication import (
    register_user,
    authenticate_user,
    get_user_by_id
)


# Create a test customer

success, message, user = register_user(

    name="Test Customer",

    email="testcustomer@example.com",

    password="SmartMart123",

    budget=1000,

    dietary="vegetarian",

    category="snacks"

)

print(message)


if success:

    print("\nREGISTERED CUSTOMER")

    print(user)

    # Test login

    logged_in_user = authenticate_user(

        "testcustomer@example.com",

        "SmartMart123"

    )

    print("\nLOGIN TEST")

    print(logged_in_user)

    # Test incorrect password

    wrong_login = authenticate_user(

        "testcustomer@example.com",

        "WrongPassword"

    )

    print("\nINCORRECT PASSWORD TEST")

    print(wrong_login)

    # Fetch profile

    profile = get_user_by_id(
        user["customer_id"]
    )

    print("\nCUSTOMER PROFILE")

    print(profile)

else:

    print("Registration test could not run.")
