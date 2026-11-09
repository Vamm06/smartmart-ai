
from modules.authentication import (
    save_shopping_item,
    get_saved_items,
    remove_saved_item,
    record_activity,
    get_activity_history
)


customer_id = "C001"

# Test saving an item
saved = save_shopping_item(
    customer_id,
    "P003"
)

print("SAVE TEST:", saved)

# Test duplicate protection
duplicate = save_shopping_item(
    customer_id,
    "P003"
)

print("DUPLICATE TEST:", duplicate)

# Test retrieving saved products
items = get_saved_items(customer_id)

print("\nSAVED ITEMS:")
print(items)

# Test activity history
record_activity(
    customer_id,
    "product_search",
    "healthy snacks",
    ["P003", "P009"]
)

history = get_activity_history(customer_id)

print("\nCUSTOMER ACTIVITY:")
print(history)

# Test removing item
removed = remove_saved_item(
    customer_id,
    "P003"
)

print("\nREMOVE TEST:", removed)

# Confirm removal
print(
    "ITEMS AFTER REMOVAL:",
    get_saved_items(customer_id)
)
