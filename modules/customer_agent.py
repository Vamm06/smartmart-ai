
from pathlib import Path
import pandas as pd
from modules.authentication import get_user_by_id

# -------------------------------------------
# STEP 1: LOCATE CUSTOMER DATABASE
# -------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CUSTOMER_FILE = BASE_DIR / "data" / "customer_profiles.csv"


# -------------------------------------------
# STEP 2: CREATE CUSTOMER AGENT
# -------------------------------------------

class CustomerAgent:

    
    def __init__(self, customer_id):

        customer_id = str(customer_id).strip().upper()

     # First check the registered customer database
        registered_profile = get_user_by_id(customer_id)

        if registered_profile is not None:

            profile = registered_profile

        else:

        # Otherwise load an existing demo customer
            customers = pd.read_csv(CUSTOMER_FILE)

            customers["customer_id"] = (
                customers["customer_id"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            matching_customer = customers[
                customers["customer_id"] == customer_id
            ]

            if matching_customer.empty:

                raise ValueError("Customer not found.")

            profile = matching_customer.iloc[0].to_dict()

    # Store customer information
        self.customer_id = str(profile["customer_id"])

        self.name = str(profile["name"])

        self.budget = float(profile["budget"])

        dietary = profile.get("dietary_preference", "")

        self.dietary_preference = (
            "" if pd.isna(dietary) else str(dietary)
        )

        category = profile.get("preferred_category", "")

        self.preferred_category = (
            "" if pd.isna(category) else str(category)
        )

    # Customer shopping state
        self.shopping_list = []

        self.last_response = None


    # ---------------------------------------
    # STEP 3: DISPLAY CUSTOMER INFORMATION
    # ---------------------------------------

    def display_profile(self):

        print("\nCUSTOMER PROFILE")
        print("----------------")

        print("Customer ID:", self.customer_id)
        print("Name:", self.name)
        print("Budget: ₹", self.budget)
        print("Dietary Preference:", self.dietary_preference)
        print("Preferred Category:", self.preferred_category)

    # ---------------------------------------
    # STEP 4: CREATE A REQUEST
    # ---------------------------------------

    def create_request(
        self,
        task,
        query=None,
        category=None,
        budget=None,
        dietary=None,
        product_ids=None,
        policy_question=None,
        return_to_start=False
    ):

        request = {

            "customer_id": self.customer_id,

            "customer_name": self.name,

            "task": task,

            "query": query,

            "budget": (
                self.budget if budget is None else budget
            ),

            "category": (
                self.preferred_category
                if category is None else category
            ),

            "dietary": (
                self.dietary_preference
                if dietary is None else dietary
            ),

            "product_ids": product_ids or [],

            "policy_question": policy_question,

            "return_to_start": return_to_start

        }

        return request

    # ---------------------------------------
    # STEP 5: RECEIVE STORE RESPONSE
    # ---------------------------------------

    def receive_response(self, response):

        self.last_response = response

        if "products" in response:
            products = response["products"]

            if not products.empty:
                self.shopping_list = (
                    products["product_id"].tolist()
                )

        print("\nCUSTOMER AGENT")
        print("--------------")
        print("Response received from Store Assistant.")

