from pathlib import Path
import pandas as pd

# Locate the data files
BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
INVENTORY_FILE = BASE_DIR / "data" / "inventory.csv"


# Function to load products and inventory
def load_catalogue():

    products = pd.read_csv(PRODUCTS_FILE)
    inventory = pd.read_csv(INVENTORY_FILE)

    # Combine both datasets using product ID
    catalogue = products.merge(
        inventory,
        on="product_id",
        how="left"
    )

    # Treat missing stock as zero
    catalogue["stock"] = catalogue["stock"].fillna(0)

    catalogue["stock"] = catalogue["stock"].astype(int)

    return catalogue


# Function to search products
def search_products(
    keyword=None,
    category=None,
    max_price=None,
    dietary=None,
    in_stock_only=True
):

    catalogue = load_catalogue()

    result = catalogue.copy()

    # Filter by keyword
    if keyword:
        searchable = (
            result["name"].fillna("") + " " +
            result["brand"].fillna("") + " " +
            result["description"].fillna("")
        )

        result = result[
            searchable.str.contains(
                keyword,
                case=False,
                regex=False
            )
        ]

    # Filter by category
    if category:
        result = result[
            result["category"].str.contains(
                category,
                case=False,
                na=False,
                regex=False
            )
        ]

    # Filter by maximum budget
    if max_price is not None:
        result = result[
            result["price"] <= max_price
        ]

    # Filter by dietary preference
    if dietary:
        result = result[
            result["dietary_tags"].fillna("").str.contains(
                dietary,
                case=False,
                regex=False
            )
        ]

    # Remove out-of-stock products
    if in_stock_only:
        result = result[
            result["stock"] > 0
        ]

    # Select useful columns for display
    result = result[
        [
            "product_id",
            "name",
            "category",
            "price",
            "brand",
            "stock",
            "section"
        ]
    ]

    return result.sort_values("price")


# Test the product discovery module
if __name__ == "__main__":

    products = search_products(
    category="dairy"
)

    print("\nAVAILABLE PRODUCTS")
    print("------------------")

    if products.empty:
        print("No matching products found.")

    else:
        print(products.to_string(index=False))
