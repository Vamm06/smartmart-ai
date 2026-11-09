
import sqlite3
import pandas as pd

from modules.authentication import DB_FILE

from pathlib import Path


# -------------------------------------------
# STEP 1: LOCATE PRODUCT DATABASE
# -------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"

INVENTORY_FILE = BASE_DIR / "data" / "inventory.csv"


# -------------------------------------------
# STEP 2: CREATE SHOPPING CART TABLE
# -------------------------------------------

def initialize_cart_table():

    with sqlite3.connect(DB_FILE) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (

                customer_id TEXT NOT NULL,

                product_id TEXT NOT NULL,

                quantity INTEGER NOT NULL
                    CHECK(quantity > 0),

                added_at TEXT DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY(customer_id, product_id)

            )
        """)

        connection.commit()


initialize_cart_table()


# -------------------------------------------
# STEP 3: LOAD PRODUCT CATALOGUE
# -------------------------------------------

def load_cart_catalogue():

    products = pd.read_csv(
        PRODUCTS_FILE,
        dtype={"product_id": str}
    )

    inventory = pd.read_csv(
        INVENTORY_FILE,
        dtype={"product_id": str}
    )

    products["product_id"] = (
        products["product_id"]
        .str.strip()
        .str.upper()
    )

    inventory["product_id"] = (
        inventory["product_id"]
        .str.strip()
        .str.upper()
    )

    catalogue = products.merge(
        inventory,
        on="product_id",
        how="left"
    )

    catalogue["stock"] = (
        pd.to_numeric(
            catalogue["stock"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    catalogue["price"] = pd.to_numeric(
        catalogue["price"],
        errors="coerce"
    )

    return catalogue


# -------------------------------------------
# STEP 4: ADD PRODUCT TO CART
# -------------------------------------------

def add_to_cart(customer_id, product_id, quantity=1):

    if not isinstance(quantity, int) or quantity < 1:

        return False, "Quantity must be a positive integer."

    customer_id = str(customer_id).strip().upper()

    product_id = str(product_id).strip().upper()

    catalogue = load_cart_catalogue()

    product = catalogue[
        catalogue["product_id"] == product_id
    ]

    if product.empty:

        return False, "Product not found."

    stock = int(product.iloc[0]["stock"])

    if stock <= 0:

        return False, "Product is out of stock."

    with sqlite3.connect(DB_FILE) as connection:

        current = connection.execute("""

            SELECT quantity

            FROM cart_items

            WHERE customer_id = ?
            AND product_id = ?

        """, (
            customer_id,
            product_id
        )).fetchone()

        current_quantity = (
            current[0] if current else 0
        )

        if current_quantity + quantity > stock:

            return False, (
                f"Only {stock} units are available. "
                f"You already have {current_quantity}."
            )

        connection.execute("""

            INSERT INTO cart_items (
                customer_id,
                product_id,
                quantity
            )

            VALUES (?, ?, ?)

            ON CONFLICT(customer_id, product_id)

            DO UPDATE SET

                quantity = cart_items.quantity
                           + excluded.quantity,

                updated_at = CURRENT_TIMESTAMP

        """, (
            customer_id,
            product_id,
            quantity
        ))

        connection.commit()

    return True, "Product added to cart."


# -------------------------------------------
# STEP 5: GET CUSTOMER CART
# -------------------------------------------

def get_cart(customer_id):

    customer_id = str(customer_id).strip().upper()

    with sqlite3.connect(DB_FILE) as connection:

        cart_items = pd.read_sql_query("""

            SELECT product_id, quantity, added_at

            FROM cart_items

            WHERE customer_id = ?

        """, connection, params=(customer_id,))

    if cart_items.empty:

        return pd.DataFrame(
            columns=[
                "product_id",
                "name",
                "category",
                "price",
                "quantity",
                "stock",
                "section",
                "line_total",
                "available"
            ]
        )

    catalogue = load_cart_catalogue()

    cart = cart_items.merge(
        catalogue,
        on="product_id",
        how="left"
    )

    cart["available"] = (
        cart["stock"].fillna(0).astype(int)
        >= cart["quantity"]
    ) & (
        cart["stock"].fillna(0).astype(int) > 0
    )

    cart["line_total"] = (
        cart["price"] * cart["quantity"]
    )

    return cart


# -------------------------------------------
# STEP 6: UPDATE PRODUCT QUANTITY
# -------------------------------------------

def update_cart_quantity(
    customer_id,
    product_id,
    quantity
):

    if not isinstance(quantity, int) or quantity < 1:

        return False, "Quantity must be at least 1."

    product_id = str(product_id).strip().upper()

    customer_id = str(customer_id).strip().upper()

    catalogue = load_cart_catalogue()

    product = catalogue[
        catalogue["product_id"] == product_id
    ]

    if product.empty:

        return False, "Product not found."

    stock = int(product.iloc[0]["stock"])

    if quantity > stock:

        return False, f"Only {stock} units are available."

    with sqlite3.connect(DB_FILE) as connection:

        cursor = connection.execute("""

            UPDATE cart_items

            SET quantity = ?,

                updated_at = CURRENT_TIMESTAMP

            WHERE customer_id = ?

            AND product_id = ?

        """, (
            quantity,
            customer_id,
            product_id
        ))

        connection.commit()

        if cursor.rowcount == 0:

            return False, "Product is not in this cart."

    return True, "Cart quantity updated."


# -------------------------------------------
# STEP 7: REMOVE PRODUCT FROM CART
# -------------------------------------------

def remove_from_cart(customer_id, product_id):

    with sqlite3.connect(DB_FILE) as connection:

        cursor = connection.execute("""

            DELETE FROM cart_items

            WHERE customer_id = ?

            AND product_id = ?

        """, (
            str(customer_id).strip().upper(),
            str(product_id).strip().upper()
        ))

        connection.commit()

    return cursor.rowcount > 0


# -------------------------------------------
# STEP 8: CLEAR ENTIRE CART
# -------------------------------------------

def clear_cart(customer_id):

    with sqlite3.connect(DB_FILE) as connection:

        connection.execute("""

            DELETE FROM cart_items

            WHERE customer_id = ?

        """, (
            str(customer_id).strip().upper(),
        ))

        connection.commit()


# -------------------------------------------
# STEP 9: REPLACE CART WITH APPROVED ITEMS
# -------------------------------------------

def replace_cart_contents(customer_id, items):

    customer_id = str(customer_id).strip().upper()

    catalogue = load_cart_catalogue()

    stock_lookup = dict(zip(
        catalogue["product_id"],
        catalogue["stock"]
    ))

    validated_items = []

    for _, row in items.iterrows():

        product_id = str(row["product_id"]).strip().upper()

        quantity = int(row["quantity"])

        if quantity < 1 or product_id not in stock_lookup:
            raise ValueError("Invalid product or quantity.")

        if quantity > int(stock_lookup[product_id]):
            raise ValueError(
                f"Insufficient stock for {product_id}."
            )

        validated_items.append(
            (customer_id, product_id, quantity)
        )

    with sqlite3.connect(DB_FILE) as connection:

        connection.execute("BEGIN IMMEDIATE")

        connection.execute("""

            DELETE FROM cart_items

            WHERE customer_id = ?

        """, (customer_id,))

        connection.executemany("""

            INSERT INTO cart_items (
                customer_id,
                product_id,
                quantity
            )

            VALUES (?, ?, ?)

        """, validated_items)

        connection.commit()


# -------------------------------------------
# STEP 10: OPTIMISE CART WITHIN A BUDGET
# -------------------------------------------

def optimize_cart_for_budget(cart, budget):

    budget = float(budget)

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    empty_result = pd.DataFrame(
        columns=[
            "product_id",
            "name",
            "price",
            "quantity",
            "line_total",
            "section"
        ]
    )

    if cart.empty:

        return {
            "items": empty_result,
            "total": 0.0,
            "budget": budget,
            "remaining": budget,
            "units_selected": 0
        }

    # Only consider products that have enough stock
    available = cart[cart["available"]].copy()

    # Expand quantities into individual product units
    units = []

    for _, row in available.iterrows():

        price_cents = int(
            round(float(row["price"]) * 100)
        )

        for _ in range(int(row["quantity"])):

            units.append({
                "product_id": str(row["product_id"]),
                "price_cents": price_cents
            })

    budget_cents = int(round(budget * 100))

    # Dynamic programming:
    # First maximise number of units.
    # If tied, maximise amount spent within budget.
    dp = {
        0: ()
    }

    for index, unit in enumerate(units):

        cost = unit["price_cents"]

        if cost <= 0:
            continue

        for spent, chosen in list(dp.items()):

            new_spent = spent + cost

            if new_spent > budget_cents:
                continue

            candidate = chosen + (index,)

            existing = dp.get(new_spent)

            if (
                existing is None
                or len(candidate) > len(existing)
            ):

                dp[new_spent] = candidate

    best_spent, best_indices = max(

        dp.items(),

        key=lambda item: (
            len(item[1]),
            item[0]
        )

    )

    # Count selected units per product
    selected_counts = {}

    for index in best_indices:

        product_id = units[index]["product_id"]

        selected_counts[product_id] = (
            selected_counts.get(product_id, 0) + 1
        )

    selected_rows = []

    for product_id, quantity in selected_counts.items():

        row = available[
            available["product_id"].astype(str) == product_id
        ].iloc[0]

        selected_rows.append({

            "product_id": product_id,

            "name": row["name"],

            "price": float(row["price"]),

            "quantity": quantity,

            "line_total": (
                float(row["price"]) * quantity
            ),

            "section": row["section"]

        })

    selected_items = pd.DataFrame(selected_rows)

    total = best_spent / 100

    return {

        "items": selected_items,

        "total": total,

        "budget": budget,

        "remaining": round(budget - total, 2),

        "units_selected": len(best_indices)

    }
