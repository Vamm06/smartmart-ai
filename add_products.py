"""Safely expand the SmartMart demo catalogue by 110 products.

Place this file in the project root (beside app.py), then run:
    python add_products.py

The script appends products to data/products.csv and matching stock rows to
 data/inventory.csv. Existing rows are preserved and rerunning is safe.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PRODUCTS_FILE = DATA_DIR / "products.csv"
INVENTORY_FILE = DATA_DIR / "inventory.csv"
MAP_FILE = DATA_DIR / "store_map.csv"

# Each item is: (product name, price in INR, factual search description)
GROUPS = [
    {
        "category": "Fruits & Vegetables", "section": "A1",
        "brand": "FarmFresh", "tags": "vegetarian|vegan",
        "items": [
            ("Red Apples", 140, "Fresh crisp red apples, whole fruit, suitable for snacks and breakfast."),
            ("Bananas", 60, "Fresh ripe bananas, naturally sweet fruit for breakfast and smoothies."),
            ("Sweet Oranges", 90, "Juicy oranges, fresh citrus fruit and a source of vitamin C."),
            ("Alphonso Mangoes", 180, "Sweet seasonal mangoes, fresh fruit for snacks and desserts."),
            ("Seedless Grapes", 110, "Fresh seedless grapes, bite-sized fruit for snacks and lunch boxes."),
            ("Watermelon", 55, "Fresh watermelon, hydrating fruit with a mild sweet taste."),
            ("Papaya", 50, "Ripe papaya, fresh fruit commonly served at breakfast."),
            ("Pomegranate", 130, "Fresh pomegranate with edible seeds, suitable for salads and snacks."),
            ("Fresh Spinach", 35, "Leafy green spinach for cooking, salads and vegetable dishes."),
            ("Farm Tomatoes", 40, "Fresh tomatoes for salads, sauces, curries and everyday cooking."),
            ("Potatoes", 35, "Fresh potatoes, versatile vegetables for roasting and everyday meals."),
            ("Red Onions", 45, "Fresh red onions for cooking, salads and savoury dishes."),
            ("Cucumbers", 30, "Fresh cucumbers for salads, sandwiches and snacks."),
            ("Carrots", 50, "Fresh carrots, crunchy vegetables for salads, cooking and snacks."),
            ("Broccoli", 75, "Fresh broccoli florets for steaming, stir-fry and healthy meals."),
        ],
    },
    {
        "category": "Dairy", "section": "C1",
        "brand": "FreshFarm", "tags": "vegetarian",
        "items": [
            ("Greek Yogurt", าม if False else 120, "Plain Greek yogurt, creamy dairy food suitable for breakfast and snacks."),
            ("Plain Curd", 55, "Plain set curd made from milk, suitable as a side or snack."),
            ("Salted Butter", 58, "Salted dairy butter for toast, baking and cooking."),
            ("Cheddar Cheese Slices", 145, "Cheddar cheese slices for sandwiches, burgers and snacks."),
            ("Paneer Cubes", 125, "Fresh paneer cubes, vegetarian dairy protein for curries and stir-fries."),
            ("Plain Buttermilk", 25, "Chilled dairy buttermilk drink, lightly seasoned and refreshing."),
            ("Toned Milk", 32, "Toned cow milk for tea, coffee, cereal and everyday use."),
            ("Full Cream Milk", 38, "Full cream cow milk for beverages, desserts and cooking."),
            ("Cow Ghee", 180, "Clarified butter made from milk, used for cooking and traditional meals."),
            ("Mozzarella Cheese", 165, "Mozzarella cheese for pizza, sandwiches and baked dishes."),
            ("Fresh Cream", 75, "Dairy cream for sauces, soups, desserts and cooking."),
            ("Mango Lassi", 45, "Mango flavoured yogurt drink, chilled dairy beverage."),
            ("Strawberry Yogurt", 35, "Strawberry flavoured dairy yogurt in an individual cup."),
            ("Cheese Spread", 95, "Creamy cheese spread for bread, crackers and sandwiches."),
            ("Unsalted Butter", 62, "Unsalted dairy butter for baking, toast and cooking."),
        ],
    },
    {
        "category": "Bakery", "section": "C2",
        "brand": "DailyBake", "tags": "vegetarian",
        "items": [
            ("Multigrain Bread", 65, "Multigrain sliced bread for toast and sandwiches."),
            ("Brown Bread", 50, "Whole wheat brown bread loaf for everyday sandwiches and toast."),
            ("Dinner Pav", 35, "Soft bakery pav rolls for savoury meals and sandwiches."),
            ("Burger Buns", 45, "Soft burger buns for homemade veggie burgers and sandwiches."),
            ("Butter Croissant", 55, "Flaky bakery croissant made with butter, suitable for breakfast."),
            ("Blueberry Muffin", 60, "Sweet blueberry bakery muffin for breakfast or an afternoon snack."),
            ("Chocolate Muffin", 55, "Chocolate flavoured bakery muffin, individually portioned."),
            ("Garlic Bread", 85, "Garlic seasoned bread for toasting and serving with meals."),
            ("Whole Wheat Pita", 70, "Whole wheat pita bread for wraps, fillings and dips."),
            ("Pizza Base", 50, "Ready-to-top bakery pizza base for homemade pizza."),
            ("Cinnamon Roll", 65, "Sweet cinnamon bakery roll for breakfast or dessert."),
            ("Plain Bagels", 75, "Plain bakery bagels for breakfast sandwiches and toast."),
            ("Multigrain Rusk", 55, "Crunchy multigrain rusks for tea-time snacks."),
            ("Jeera Biscuits", 40, "Cumin flavoured savoury bakery biscuits for tea-time."),
            ("Fruit Bun", 45, "Soft bakery bun with dried fruit pieces, suitable for a snack."),
        ],
    },
    {
        "category": "Snacks", "section": "A2",
        "brand": "DailyBite", "tags": "vegetarian|vegan",
        "items": [
            ("Roasted Peanuts", 75, "Roasted peanuts, crunchy plant-based snack containing protein."),
            ("Masala Makhana", 95, "Roasted fox nuts seasoned with spices, a crunchy vegetarian snack."),
            ("Trail Mix", 160, "Mixed nuts and seeds for a convenient snack with plant protein."),
            ("Peanut Protein Bar", 85, "Peanut-based snack bar with plant ingredients; check pack for nutrition details."),
            ("Roasted Soy Nuts", 110, "Crunchy roasted soybeans, a plant-based snack containing protein."),
            ("Pumpkin Seeds", 140, "Edible pumpkin seeds for snacking, salads and breakfast bowls."),
            ("Sunflower Seeds", 95, "Sunflower kernels for snacks, salads and cereal toppings."),
            ("Baked Chickpea Chips", 70, "Baked chickpea-based crisps, a savoury plant-based snack."),
            ("Salted Popcorn", 45, "Ready-to-eat salted popcorn for a light savoury snack."),
            ("Granola Bar", 65, "Oat and grain snack bar for breakfast or between-meal snacking."),
            ("Seedless Dates", 130, "Seedless dates, naturally sweet dried fruit for snacks and recipes."),
            ("Black Raisins", 85, "Dried black raisins for snacking, baking and breakfast bowls."),
            ("Roasted Cashews", 190, "Roasted cashew nuts, crunchy snack and source of plant protein."),
            ("Pistachios", 210, "Pistachio nuts for snacking and adding to desserts."),
            ("Brown Rice Cakes", 80, "Crisp brown rice cakes for light snacks and toppings."),
            ("Baked Potato Chips", 55, "Baked potato crisps with a lightly salted savoury flavour."),
            ("Gujarati Khakhra", 60, "Thin roasted wheat khakhra, a crunchy savoury snack."),
            ("Puffed Rice Mixture", 50, "Puffed rice savoury mixture with spices for tea-time snacking."),
            ("Soy Protein Crisps", 125, "Crunchy soy-based crisps, a plant-based snack containing protein."),
            ("Roasted Chana Jor", 65, "Spiced flattened roasted chickpeas, a crunchy plant-based protein snack."),
        ],
    },
    {
        "category": "Beverages", "section": "D1",
        "brand": "FreshSip", "tags": "vegetarian|vegan",
        "items": [
            ("Coconut Water", 55, "Packaged coconut water drink, served chilled."),
            ("Green Tea Bags", 120, "Green tea bags for preparing a warm unsweetened tea beverage."),
            ("Black Tea", 95, "Black tea leaves for brewing a hot tea beverage."),
            ("Instant Coffee", 150, "Instant coffee granules for preparing hot or iced coffee."),
            ("Lemonade", 45, "Ready-to-drink lemon beverage with a refreshing citrus flavour."),
            ("Apple Juice", 110, "Packaged apple juice beverage, best served chilled."),
            ("Mixed Fruit Juice", 125, "Mixed fruit juice drink for a chilled beverage."),
            ("Sparkling Water", 65, "Carbonated plain water, served chilled as a beverage."),
            ("Iced Tea", 50, "Ready-to-drink lemon iced tea beverage."),
            ("Mango Drink", 40, "Mango flavoured fruit beverage, served chilled."),
            ("Oat Drink", 135, "Plant-based oat beverage for cereal, smoothies and coffee."),
            ("Almond Drink", 145, "Plant-based almond beverage for cereal, smoothies and coffee."),
        ],
    },
    {
        "category": "Personal Care", "section": "B1",
        "brand": "CleanCare", "tags": "not_applicable",
        "items": [
            ("Hand Wash", 95, "Liquid hand wash for everyday hand hygiene."),
            ("Fluoride Toothpaste", 75, "Toothpaste for routine tooth cleaning and oral hygiene."),
            ("Soft Toothbrush", 35, "Soft-bristle toothbrush for daily oral care."),
            ("Gentle Face Wash", 145, "Gentle facial cleanser for daily face washing."),
            ("Daily Moisturizer", 180, "Face and body moisturizer for everyday skin care."),
            ("SPF Sunscreen", 240, "Broad-spectrum sunscreen for sun protection; follow label directions."),
            ("Hair Conditioner", 160, "Rinse-off hair conditioner for regular hair care."),
            ("Body Lotion", 155, "Body lotion for everyday skin moisturising."),
            ("Bathing Soap", 40, "Bathing soap bar for everyday personal cleansing."),
            ("Roll-On Deodorant", 125, "Roll-on deodorant for everyday personal care."),
            ("Coconut Hair Oil", 110, "Coconut-based hair oil for hair care and conditioning."),
            ("Aloe Face Gel", 135, "Aloe-based face gel for a lightweight skin-care routine."),
            ("Sanitary Pads", 95, "Pack of sanitary pads for menstrual hygiene."),
        ],
    },
    {
        "category": "Household", "section": "D2",
        "brand": "HomePlus", "tags": "not_applicable",
        "items": [
            ("Laundry Detergent", 210, "Laundry detergent powder for washing clothes."),
            ("Dishwashing Liquid", 85, "Liquid dishwashing cleaner for utensils and cookware."),
            ("Toilet Cleaner", 95, "Household toilet cleaning liquid; follow product label directions."),
            ("Facial Tissue Box", 65, "Paper facial tissues for everyday household use."),
            ("Garbage Bags", 75, "Household garbage bags for collecting and disposing of waste."),
            ("Paper Towels", 90, "Absorbent paper towels for kitchen and household cleaning."),
            ("Kitchen Scrubbers", 35, "Scouring scrubbers for cleaning kitchen utensils."),
            ("Surface Cleaner", 120, "Multi-surface household cleaning liquid."),
            ("Fabric Softener", 145, "Laundry fabric softener for washing clothes."),
            ("Air Freshener", 130, "Room air freshener for household spaces."),
        ],
    },
    {
        "category": "Breakfast", "section": "A1",
        "brand": "MorningMill", "tags": "vegetarian|vegan",
        "items": [
            ("Corn Flakes", 135, "Corn flakes breakfast cereal, commonly served with milk or plant drink."),
            ("Fruit Muesli", 190, "Muesli breakfast cereal with grains and dried fruit."),
            ("Crunchy Peanut Butter", 175, "Peanut butter spread for toast, sandwiches and breakfast bowls."),
            ("Natural Honey", 160, "Honey sweetener for toast, cereal and breakfast recipes."),
            ("Mixed Fruit Jam", 95, "Fruit jam spread for bread, toast and breakfast."),
            ("Poha", 60, "Flattened rice for preparing a traditional savoury breakfast."),
            ("Instant Upma Mix", 75, "Ready-to-cook savoury semolina breakfast mix."),
            ("Ragi Flour", 80, "Finger millet flour for porridge, dosa and breakfast recipes."),
            ("Chia Seeds", 145, "Chia seeds for overnight oats, smoothies and breakfast bowls."),
            ("Quinoa Flakes", 185, "Quinoa flakes for preparing a warm cereal or breakfast porridge."),
        ],
    },
]


def main():
    if not PRODUCTS_FILE.exists() or not INVENTORY_FILE.exists():
        raise FileNotFoundError(
            "Could not find data/products.csv or data/inventory.csv. "
            "Place this script in the project root beside app.py."
        )
    if not MAP_FILE.exists():
        raise FileNotFoundError("Could not find data/store_map.csv.")

    products = pd.read_csv(PRODUCTS_FILE)
    inventory = pd.read_csv(INVENTORY_FILE)
    store_map = pd.read_csv(MAP_FILE)

    required_product_columns = [
        "product_id", "name", "category", "price", "brand",
        "description", "dietary_tags", "section"
    ]
    required_inventory_columns = ["product_id", "stock"]
    required_map_columns = ["location", "connected_to", "distance"]

    for col in required_product_columns:
        if col not in products.columns:
            raise ValueError(f"products.csv is missing column: {col}")
    for col in required_inventory_columns:
        if col not in inventory.columns:
            raise ValueError(f"inventory.csv is missing column: {col}")
    for col in required_map_columns:
        if col not in store_map.columns:
            raise ValueError(f"store_map.csv is missing column: {col}")

    planned_count = sum(len(group["items"]) for group in GROUPS)
    if planned_count != 110:
        raise ValueError(f"Expected 110 new products; catalogue defines {planned_count}.")

    # Confirm all assigned sections already exist in the route-planning graph.
    graph_locations = set(store_map["location"].astype(str).str.strip())
    graph_locations.update(store_map["connected_to"].astype(str).str.strip())
    assigned_sections = {group["section"] for group in GROUPS}
    missing_sections = assigned_sections - graph_locations
    if missing_sections:
        raise ValueError(
            "These product sections are missing from store_map.csv: "
            + ", ".join(sorted(missing_sections))
        )

    new_rows = []
    product_number = 11
    stock_rows = []

    for group in GROUPS:
        for item_index, (name, price, description) in enumerate(group["items"]):
            product_id = f"P{product_number:03d}"
            product_number += 1
            new_rows.append({
                "product_id": product_id,
                "name": name,
                "category": group["category"],
                "price": price,
                "brand": group["brand"],
                "description": description,
                "dietary_tags": group["tags"],
                "section": group["section"],
            })
            # Deterministic positive stock between 8 and 50 units.
            stock_rows.append({
                "product_id": product_id,
                "stock": 8 + ((product_number * 7 + item_index) % 43),
            })

    new_products = pd.DataFrame(new_rows)
    new_stock = pd.DataFrame(stock_rows)

    existing_product_ids = set(products["product_id"].astype(str).str.upper())
    product_additions = new_products[
        ~new_products["product_id"].isin(existing_product_ids)
    ].copy()

    existing_inventory_ids = set(inventory["product_id"].astype(str).str.upper())
    stock_additions = new_stock[
        ~new_stock["product_id"].isin(existing_inventory_ids)
    ].copy()

    # Validate before writing.
    if not product_additions.empty:
        products = pd.concat([products, product_additions], ignore_index=True)
    if not stock_additions.empty:
        inventory = pd.concat([inventory, stock_additions], ignore_index=True)

    if products["product_id"].astype(str).str.upper().duplicated().any():
        raise ValueError("Duplicate product IDs detected after update; no files written.")
    if inventory["product_id"].astype(str).str.upper().duplicated().any():
        raise ValueError("Duplicate inventory IDs detected after update; no files written.")

    # Every catalogue product must have an inventory row for the app's merge.
    missing_inventory = set(products["product_id"].astype(str).str.upper()) - set(
        inventory["product_id"].astype(str).str.upper()
    )
    if missing_inventory:
        raise ValueError(
            "Some products have no inventory rows: "
            + ", ".join(sorted(missing_inventory))
        )

    products.to_csv(PRODUCTS_FILE, index=False)
    inventory.to_csv(INVENTORY_FILE, index=False)

    print("SmartMart catalogue expansion completed.")
    print(f"New products added: {len(product_additions)}")
    print(f"New inventory rows added: {len(stock_additions)}")
    print(f"Total products now: {len(products)}")
    print(f"Total inventory rows now: {len(inventory)}")
    print("Sections validated:", ", ".join(sorted(assigned_sections)))
    print("Product file:", PRODUCTS_FILE)
    print("Inventory file:", INVENTORY_FILE)
    if len(product_additions) == 0:
        print("No new products were needed; the script appears to have already run.")


if __name__ == "__main__":
    main()
