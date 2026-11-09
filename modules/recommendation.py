
from pathlib import Path
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# STEP 1: LOAD PRODUCT AND INVENTORY DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
INVENTORY_FILE = BASE_DIR / "data" / "inventory.csv"


def load_catalogue():

    products = pd.read_csv(PRODUCTS_FILE)
    inventory = pd.read_csv(INVENTORY_FILE)

    catalogue = products.merge(
        inventory,
        on="product_id",
        how="left"
    )

    catalogue["stock"] = (
        pd.to_numeric(catalogue["stock"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    # Combine product information into searchable text
    text_columns = [
        "name",
        "category",
        "brand",
        "description",
        "dietary_tags"
    ]

    for column in text_columns:
        catalogue[column] = (
            catalogue[column].fillna("").astype(str)
        )

    catalogue["search_text"] = catalogue[
        text_columns
    ].agg(" ".join, axis=1)

    return catalogue


# --------------------------------------------------
# STEP 2: BUILD PRODUCT RECOMMENDATION ENGINE
# --------------------------------------------------

def recommend_products(
    query,
    max_price=None,
    category=None,
    dietary=None,
    top_n=5,
    min_similarity=0.10
):

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Please enter a valid search query.")

    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    # Load product information
    catalogue = load_catalogue()

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    # Convert product descriptions into vectors
    product_vectors = vectorizer.fit_transform(
        catalogue["search_text"]
    )

    # Convert customer query into a vector
    query_vector = vectorizer.transform([query])

    # Compare customer query with products
    similarity_scores = cosine_similarity(
        query_vector,
        product_vectors
    ).flatten()

    # Add similarity scores to catalogue
    catalogue["similarity_score"] = similarity_scores

    # --------------------------------------------------
    # STEP 3: APPLY CUSTOMER PREFERENCES
    # --------------------------------------------------

    result = catalogue.copy()

    # Budget filtering
    if max_price is not None:
        result = result[
            result["price"] <= max_price
        ]

    # Category filtering
    if category:
        result = result[
            result["category"].str.contains(
                category,
                case=False,
                na=False,
                regex=False
            )
        ]

    # Dietary preference filtering
    if dietary:
        result = result[
            result["dietary_tags"].str.contains(
                dietary,
                case=False,
                na=False,
                regex=False
            )
        ]

    # Remove unavailable products
    result = result[
        result["stock"] > 0
    ]

    # Remove products with very low relevance
    result = result[
        result["similarity_score"] >= min_similarity
    ]

    # --------------------------------------------------
    # STEP 4: RANK PRODUCTS
    # --------------------------------------------------

    result = result.sort_values(
        by="similarity_score",
        ascending=False
    )

    # Display useful information
    result = result[
        [
            "product_id",
            "name",
            "category",
            "price",
            "brand",
            "stock",
            "section",
            "similarity_score"
        ]
    ]

    result = result.head(top_n).copy()

    result["similarity_score"] = (
        result["similarity_score"].round(3)
    )

    return result


# --------------------------------------------------
# STEP 5: TEST THE RECOMMENDATION ENGINE
# --------------------------------------------------

if __name__ == "__main__":

    recommendations = recommend_products(
    query="healthy breakfast",
    max_price=200,
    category="breakfast",
    top_n=5
)

    print("\nAI PRODUCT RECOMMENDATIONS")
    print("--------------------------")

    if recommendations.empty:
        print("No suitable products found.")

    else:
        print(recommendations.to_string(index=False))
