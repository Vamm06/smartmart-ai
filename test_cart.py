
from modules.cart_manager import (
    add_to_cart,
    get_cart,
    update_cart_quantity,
    remove_from_cart,
    optimize_cart_for_budget,
    clear_cart
)

# Use a temporary test customer
customer_id = "CART_TEST_001"

# Start with an empty cart
clear_cart(customer_id)


# TEST 1: ADD PRODUCTS

print("\nTEST 1: ADD PRODUCTS")

print(add_to_cart(customer_id, "P001", 1))

print(add_to_cart(customer_id, "P003", 2))

print(add_to_cart(customer_id, "P004", 1))


# TEST 2: DISPLAY CART

print("\nTEST 2: SHOPPING CART")

cart = get_cart(customer_id)

print(cart.to_string(index=False))

total = cart["line_total"].sum()

print("\nTOTAL:", total)


# TEST 3: UPDATE QUANTITY

print("\nTEST 3: UPDATE QUANTITY")

print(
    update_cart_quantity(
        customer_id,
        "P003",
        1
    )
)

print(get_cart(customer_id).to_string(index=False))


# TEST 4: OPTIMISE BASKET

print("\nTEST 4: BUDGET OPTIMISATION")

cart = get_cart(customer_id)

suggestion = optimize_cart_for_budget(
    cart,
    budget=300
)

print("\nOPTIMISED BASKET")

print(suggestion["items"].to_string(index=False))

print("\nBASKET TOTAL:", suggestion["total"])

print("CUSTOMER BUDGET:", suggestion["budget"])

print("REMAINING:", suggestion["remaining"])


# TEST 5: REMOVE PRODUCT

print("\nTEST 5: REMOVE PRODUCT")

print(
    remove_from_cart(
        customer_id,
        "P004"
    )
)

print(get_cart(customer_id).to_string(index=False))


# CLEAN UP TEST DATA

clear_cart(customer_id)

print("\nALL CART TESTS FINISHED.")
