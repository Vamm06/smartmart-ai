import json
import sqlite3
import hashlib
import secrets
import hmac
import uuid

from pathlib import Path


# -------------------------------------------
# STEP 1: DATABASE LOCATION
# -------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "data" / "smartmart_users.db"


# -------------------------------------------
# STEP 2: INITIALISE DATABASE
# -------------------------------------------

def initialize_database():

    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with sqlite3.connect(DB_FILE) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (

                customer_id TEXT PRIMARY KEY,

                name TEXT NOT NULL,

                email TEXT NOT NULL UNIQUE COLLATE NOCASE,

                password_hash TEXT NOT NULL,

                salt TEXT NOT NULL,

                budget REAL NOT NULL,

                dietary_preference TEXT NOT NULL,

                preferred_category TEXT NOT NULL

            )
        """)

        connection.commit()


# -------------------------------------------
# STEP 3: HASH PASSWORD
# -------------------------------------------

def hash_password(password, salt):

    return hashlib.pbkdf2_hmac(

        "sha256",

        password.encode("utf-8"),

        salt,

        600000,

        dklen=32

    )


# -------------------------------------------
# STEP 4: REGISTER CUSTOMER
# -------------------------------------------

def register_user(
    name,
    email,
    password,
    budget,
    dietary,
    category
):

    name = name.strip()
    email = email.strip().lower()

    if not name:
        return False, "Please enter your name.", None

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address.", None

    if len(password) < 8:
        return False, "Password must contain at least 8 characters.", None

    if budget <= 0:
        return False, "Budget must be greater than zero.", None

    customer_id = "U" + uuid.uuid4().hex[:8].upper()

    salt = secrets.token_bytes(16)

    password_hash = hash_password(
        password,
        salt
    )

    try:

        with sqlite3.connect(DB_FILE) as connection:

            connection.execute("""

                INSERT INTO users (

                    customer_id,
                    name,
                    email,
                    password_hash,
                    salt,
                    budget,
                    dietary_preference,
                    preferred_category

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            """, (

                customer_id,
                name,
                email,
                password_hash.hex(),
                salt.hex(),
                float(budget),
                dietary,
                category

            ))

            connection.commit()

        return True, "Account created successfully!", {
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "budget": float(budget),
            "dietary_preference": dietary,
            "preferred_category": category
        }

    except sqlite3.IntegrityError:

        return False, "This email is already registered.", None


# -------------------------------------------
# STEP 5: CUSTOMER LOGIN
# -------------------------------------------

def authenticate_user(email, password):

    email = email.strip().lower()

    with sqlite3.connect(DB_FILE) as connection:

        connection.row_factory = sqlite3.Row

        user = connection.execute("""

            SELECT * FROM users
            WHERE email = ? COLLATE NOCASE

        """, (email,)).fetchone()

    if user is None:
        return None

    salt = bytes.fromhex(user["salt"])

    entered_hash = hash_password(
        password,
        salt
    )

    stored_hash = bytes.fromhex(
        user["password_hash"]
    )

    if not hmac.compare_digest(
        entered_hash,
        stored_hash
    ):
        return None

    return {

        "customer_id": user["customer_id"],

        "name": user["name"],

        "email": user["email"],

        "budget": float(user["budget"]),

        "dietary_preference": user["dietary_preference"],

        "preferred_category": user["preferred_category"]

    }


# -------------------------------------------
# STEP 6: FETCH CUSTOMER PROFILE
# -------------------------------------------

def get_user_by_id(customer_id):

    with sqlite3.connect(DB_FILE) as connection:

        connection.row_factory = sqlite3.Row

        user = connection.execute("""

            SELECT
                customer_id,
                name,
                email,
                budget,
                dietary_preference,
                preferred_category

            FROM users

            WHERE customer_id = ?

        """, (customer_id,)).fetchone()

    if user is None:
        return None

    return dict(user)


# Create database when this module is imported
initialize_database()


# ============================================
# CUSTOMER PERSONALISATION DATABASE
# ============================================

def initialize_customer_data_tables():

    with sqlite3.connect(DB_FILE) as connection:

        # Saved shopping list
        connection.execute("""
            CREATE TABLE IF NOT EXISTS saved_items (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                customer_id TEXT NOT NULL,

                product_id TEXT NOT NULL,

                added_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(customer_id, product_id)

            )
        """)

        # Customer activity history
        connection.execute("""
            CREATE TABLE IF NOT EXISTS activity_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                customer_id TEXT NOT NULL,

                activity_type TEXT NOT NULL,

                query TEXT,

                product_ids TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP

            )
        """)

        connection.commit()


# Create tables automatically
initialize_customer_data_tables()


# ============================================
# SAVE PRODUCT TO CUSTOMER SHOPPING LIST
# ============================================

def save_shopping_item(customer_id, product_id):

    with sqlite3.connect(DB_FILE) as connection:

        cursor = connection.execute("""

            INSERT OR IGNORE INTO saved_items (

                customer_id,
                product_id

            )

            VALUES (?, ?)

        """, (
            customer_id,
            product_id
        ))

        connection.commit()

        return cursor.rowcount > 0


# ============================================
# GET CUSTOMER SAVED ITEMS
# ============================================

def get_saved_items(customer_id):

    with sqlite3.connect(DB_FILE) as connection:

        connection.row_factory = sqlite3.Row

        rows = connection.execute("""

            SELECT product_id, added_at

            FROM saved_items

            WHERE customer_id = ?

            ORDER BY added_at DESC

        """, (customer_id,)).fetchall()

    return [dict(row) for row in rows]


# ============================================
# REMOVE SAVED PRODUCT
# ============================================

def remove_saved_item(customer_id, product_id):

    with sqlite3.connect(DB_FILE) as connection:

        cursor = connection.execute("""

            DELETE FROM saved_items

            WHERE customer_id = ?
            AND product_id = ?

        """, (
            customer_id,
            product_id
        ))

        connection.commit()

        return cursor.rowcount > 0


# ============================================
# RECORD CUSTOMER ACTIVITY
# ============================================

def record_activity(
    customer_id,
    activity_type,
    query="",
    product_ids=None
):

    if product_ids is None:
        product_ids = []

    products_json = json.dumps(
        [str(pid) for pid in product_ids]
    )

    with sqlite3.connect(DB_FILE) as connection:

        connection.execute("""

            INSERT INTO activity_history (

                customer_id,
                activity_type,
                query,
                product_ids

            )

            VALUES (?, ?, ?, ?)

        """, (
            customer_id,
            activity_type,
            query,
            products_json
        ))

        connection.commit()


# ============================================
# FETCH CUSTOMER ACTIVITY HISTORY
# ============================================

def get_activity_history(customer_id, limit=20):

    with sqlite3.connect(DB_FILE) as connection:

        connection.row_factory = sqlite3.Row

        rows = connection.execute("""

            SELECT
                activity_type,
                query,
                product_ids,
                created_at

            FROM activity_history

            WHERE customer_id = ?

            ORDER BY id DESC

            LIMIT ?

        """, (
            customer_id,
            limit
        )).fetchall()

    history = []

    for row in rows:

        record = dict(row)

        record["product_ids"] = json.loads(
            record["product_ids"]
        )

        history.append(record)

    return history
