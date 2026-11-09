
# ============================================
# SMARTMART AI - MAIN APPLICATION
# ============================================
from html import escape
import streamlit as st

import os

# Load deployed credentials from Streamlit Secrets
# Locally, your existing .env files will still work.

try:

    if "OPENAI_API_KEY" in st.secrets:

        os.environ["OPENAI_API_KEY"] = str(
            st.secrets["OPENAI_API_KEY"]
        )

    if "OPENAI_MODEL" in st.secrets:

        os.environ["OPENAI_MODEL"] = str(
            st.secrets["OPENAI_MODEL"]
        )

except Exception:

    # Local development can continue using .env
    pass

import pandas as pd
import plotly.express as px

from pathlib import Path

# Import existing project modules

from modules.customer_agent import CustomerAgent

from modules.store_agent import StoreAssistantAgent

from modules.product_search import search_products

from modules.route_planner import plan_shopping_route

from modules.policy_rag import generate_grounded_answer

from modules.authentication import (
    register_user,
    authenticate_user,
    get_user_by_id,
    save_shopping_item,
    get_saved_items,
    remove_saved_item,
    record_activity,
    get_activity_history
)

from modules.cart_manager import (
    add_to_cart,
    get_cart,
    update_cart_quantity,
    remove_from_cart,
    clear_cart,
    optimize_cart_for_budget,
    replace_cart_contents
)


# Locate project directory

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

EVALUATION_DIR = BASE_DIR / "evaluation"


# Configure Streamlit

st.set_page_config(
    page_title="SmartMart AI",
    page_icon="🛒",
    layout="wide"
)

# ============================================
# CUSTOM SMARTMART DESIGN
# ============================================

st.markdown("""
<style>

/* Main application background */

.stApp {
    background-color: #F7F5EF;
    color: #26352C;
}

/* Main content spacing */

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Sidebar design */

[data-testid="stSidebar"] {
    background-color: #E4EBDD;
    border-right: 1px solid #D5DFD0;
}

/* Main headings */

h1, h2, h3 {
    color: #244E3B !important;
    font-weight: 700;
}

/* Metric cards */

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E0E7DC;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 3px 12px rgba(36, 78, 59, 0.06);
}

/* Buttons */

.stButton > button,
.stFormSubmitButton > button {
    background-color: #244E3B;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.1rem;
    font-weight: 600;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #386B50;
    color: #FFFFFF;
    border: none;
}

/* Input fields */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    border-radius: 10px;
}

/* Main horizontal navigation */

div[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 8px;
    flex-wrap: wrap;
}

div[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #FFFFFF;
    border: 1px solid #DCE5D8;
    padding: 9px 15px;
    border-radius: 12px;
    transition: all 0.2s ease;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #244E3B;
    border-color: #244E3B;
    color: #FFFFFF;
}

/* Product cards */

.product-card {
    background: #FFFFFF;
    border: 1px solid #E1E8DD;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 16px;
    box-shadow: 0 4px 14px rgba(36, 78, 59, 0.07);
}

.product-visual {
    background: #E4EBDD;
    min-height: 105px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
}

.product-card-body {
    padding: 16px;
}

.product-category {
    color: #63836B;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

.product-name {
    color: #244E3B;
    font-size: 18px;
    font-weight: 700;
    margin-top: 5px;
    min-height: 27px;
}

.product-brand {
    color: #788176;
    font-size: 12px;
    margin-top: 5px;
}

.product-price {
    color: #244E3B;
    font-size: 23px;
    font-weight: 800;
    margin-top: 12px;
}

.product-details {
    color: #687568;
    font-size: 12px;
    margin-top: 8px;
}

.product-stock {
    display: inline-block;
    background: #E4F1E4;
    color: #28623D;
    border-radius: 20px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 700;
}
.hero-banner {
    background: linear-gradient(
        120deg,
        #244E3B 0%,
        #477B5B 100%
    );
    padding: 36px 40px;
    border-radius: 22px;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(36,78,59,0.15);
}

.hero-banner h1 {
    color: #FFFFFF !important;
    font-size: 40px;
    margin: 10px 0;
}

.hero-banner p {
    color: #E5F0E5;
    font-size: 16px;
    margin-bottom: 0;
}

.hero-eyebrow {
    color: #F3D59B;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}

</style>
""", unsafe_allow_html=True)


# ============================================
# PHASE 3: CUSTOMER LOGIN AND REGISTRATION
# ============================================

# Initialise login state

if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

if "is_guest" not in st.session_state:
    st.session_state["is_guest"] = False


# Show authentication page if not logged in

if (
    st.session_state["auth_user"] is None
    and not st.session_state["is_guest"]
):

    st.markdown(
        """
        <div style="text-align:center; padding:25px 0;">
            <h1>🛒 SmartMart AI</h1>
            <p style="color:#718174; font-size:17px;">
                Your smarter shopping experience starts here.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 1.6, 1])

    with center:

        st.container(border=True)

        mode = st.radio(
            "Welcome",
            [
                "Login",
                "Create Account",
                "Continue as Guest"
            ],
            horizontal=True,
            key="authentication_mode"
        )

        st.divider()

        # --------------------------------
        # LOGIN FORM
        # --------------------------------

        if mode == "Login":

            st.subheader("Welcome Back!")

            st.write(
                "Sign in to access your SmartMart account."
            )

            with st.form("customer_login_form"):

                email = st.text_input(
                    "Email Address",
                    placeholder="example@email.com",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                login_button = st.form_submit_button(
                    "Login to SmartMart",
                    type="primary",
                    width="stretch"
                )

            if login_button:

                user = authenticate_user(
                    email,
                    password
                )

                if user is None:

                    st.error(
                        "Incorrect email or password."
                    )

                else:

                    st.session_state["auth_user"] = user

                    st.session_state["is_guest"] = False

                    st.success(
                        f"Welcome back, {user['name']}!"
                    )

                    st.rerun()

        # --------------------------------
        # REGISTRATION FORM
        # --------------------------------

        elif mode == "Create Account":

            st.subheader("Create Your Account")

            st.write(
                "Join SmartMart for personalised shopping."
            )

            with st.form("customer_registration_form"):

                name = st.text_input(
                    "Full Name",
                    key="register_name"
                )

                email = st.text_input(
                    "Email Address",
                    key="register_email"
                )

                password = st.text_input(
                    "Create Password",
                    type="password",
                    help="At least 8 characters",
                    key="register_password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="confirm_password"
                )

                budget = st.number_input(
                    "Shopping Budget (₹)",
                    min_value=1.0,
                    value=1000.0,
                    step=100.0,
                    key="register_budget"
                )

                dietary = st.selectbox(
                    "Dietary Preference",
                    [
                        "No restriction",
                        "vegetarian",
                        "vegan"
                    ],
                    key="register_dietary"
                )

                category = st.selectbox(
                    "Preferred Category",
                    [
                        "All categories",
                        "fruits & vegetables",
                        "dairy",
                        "bakery",
                        "snacks",
                        "beverages",
                        "personal care",
                        "household",
                        "breakfast"
                    ],
                    key="register_category"
                )

                register_button = st.form_submit_button(
                    "Create Account",
                    type="primary",
                    width="stretch"
                )

            if register_button:

                if password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    dietary_value = (
                        ""
                        if dietary == "No restriction"
                        else dietary
                    )

                    category_value = (
                        ""
                        if category == "All categories"
                        else category
                    )

                    success, message, user = register_user(

                        name=name,

                        email=email,

                        password=password,

                        budget=budget,

                        dietary=dietary_value,

                        category=category_value

                    )

                    if success:

                        st.session_state["auth_user"] = user

                        st.session_state["is_guest"] = False

                        st.success(message)

                        st.rerun()

                    else:

                        st.error(message)

        # --------------------------------
        # GUEST LOGIN
        # --------------------------------

        elif mode == "Continue as Guest":

            st.subheader("Explore SmartMart")

            st.write(
                "Try our AI-powered shopping assistant "
                "using simulated customer profiles."
            )

            if st.button(
                "Continue as Guest",
                type="primary",
                width="stretch",
                key="guest_login_button"
            ):

                st.session_state["is_guest"] = True

                st.session_state["auth_user"] = None

                st.rerun()

        st.divider()

        st.caption(
            "SmartMart AI | Intelligent Retail Assistant"
        )

    # Stop the rest of the application until authentication
    st.stop()



# Main title


st.markdown("""
<div class="hero-banner">
    <div class="hero-content">
        <div class="hero-eyebrow">YOUR SMARTER SHOPPING EXPERIENCE</div>
        <h1>🛒 SmartMart AI</h1>
        <p>
            Discover products, get intelligent recommendations,
            and shop smarter with AI.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================
# LOAD PROJECT DATA
# ============================================

@st.cache_data
def load_catalogue():

    products = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    inventory = pd.read_csv(
        DATA_DIR / "inventory.csv"
    )

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

    return catalogue


@st.cache_data
def load_customers():

    return pd.read_csv(
        DATA_DIR / "customer_profiles.csv"
    )


# ============================================
# PRODUCT CARD DESIGN
# ============================================


# ============================================
# PRODUCT CARD DESIGN - UPDATED
# ============================================

CATEGORY_EMOJI = {

    "fruits & vegetables": "🥑",
    "dairy": "🥛",
    "bakery": "🍞",
    "snacks": "🥜",
    "beverages": "🥤",
    "personal care": "🧴",
    "household": "🧹",
    "breakfast": "🥣"

}


def render_product_cards(products, columns_per_row=3):

    if products.empty:

        st.info("No products available.")

        return

    products = products.reset_index(drop=True)

    for start in range(0, len(products), columns_per_row):

        batch = products.iloc[
            start:start + columns_per_row
        ]

        columns = st.columns(columns_per_row)

        for column, (_, row) in zip(
            columns,
            batch.iterrows()
        ):

            category = str(row["category"])

            emoji = CATEGORY_EMOJI.get(
                category.lower(),
                "🛍️"
            )

            with column:

                with st.container(border=True):

                    st.markdown(
                        f"### {emoji} {row['name']}"
                    )

                    st.caption(
                        f"{category} | {row['brand']}"
                    )

                    st.markdown(
                        f"## ₹{float(row['price']):,.0f}"
                    )

                    st.write(
                        f"📍 Section: {row['section']}"
                    )

                    stock = int(row["stock"])

                    if stock > 0:

                        st.success(
                            f"{stock} units available"
                        )

                    else:

                        st.error("Out of stock")



def show_route(route_result):

    st.subheader("🗺️ Recommended Shopping Route")

    st.write(
        " → ".join(route_result["route"])
    )

    st.metric(
        "Total Walking Distance",
        f"{route_result['total_distance']:.1f} metres"
    )

    st.write("Sections to visit:")

    st.write(
        " → ".join(route_result["visit_order"])
    )

    if not route_result["unavailable_products"].empty:

        st.warning("Some requested products are unavailable.")

        st.dataframe(
            route_result["unavailable_products"],
            use_container_width=True
        )

# ============================================
# SIDEBAR AND CUSTOMER PROFILE
# ============================================

st.sidebar.title("🛒 SmartMart AI")

st.sidebar.caption("Navigation Panel")

# Load customer profiles


# ============================================
# CUSTOMER ACCOUNT AND SIDEBAR
# ============================================

if st.session_state["is_guest"]:

    # Guest uses existing demo profiles

    customers = load_customers()

    customer_ids = customers["customer_id"].tolist()

    customer_id = st.sidebar.selectbox(
        "Select Demo Customer",
        customer_ids,
        key="guest_customer_selector"
    )

    customer = CustomerAgent(customer_id)

else:

    # Registered customer uses SQLite profile

    user = st.session_state["auth_user"]

    customer = CustomerAgent(
        user["customer_id"]
    )


# Display customer information

st.sidebar.divider()

st.sidebar.subheader("👤 Customer Information")

st.sidebar.write(
    f"**Name:** {customer.name}"
)

if not st.session_state["is_guest"]:

    st.sidebar.caption(user["email"])

st.sidebar.write(
    f"**Budget:** ₹{customer.budget:.0f}"
)

st.sidebar.write(
    f"**Diet:** {customer.dietary_preference or 'No restriction'}"
)

st.sidebar.write(
    f"**Category:** {customer.preferred_category or 'All categories'}"
)

st.sidebar.divider()


# Logout / exit demo

logout_label = (
    "Exit Demo"
    if st.session_state["is_guest"]
    else "Log Out"
)

if st.sidebar.button(
    logout_label,
    key="customer_logout",
    width="stretch"
):

    st.session_state["auth_user"] = None

    st.session_state["is_guest"] = False

    # Clear previous customer-specific results
    for key in [
        "shopping_result",
        "product_results",
        "route_result",
        "policy_result"
    ]:

        st.session_state.pop(key, None)

    st.rerun()



# ============================================
# MAIN PAGE NAVIGATION
# ============================================

st.markdown(
    "### Explore SmartMart",
)


page = st.radio(
    "Choose a section",
    [
        "Dashboard",
        "AI Shopping Assistant",
        "Product Finder",
        "Store Navigation",
        "Policy Assistant",
        "AI Evaluation",
        "My Shopping",
        "Shopping Cart"
    ],
    format_func=lambda value: {
        "Dashboard": "🏠 Home",
        "AI Shopping Assistant": "🤖 Shopping AI",
        "Product Finder": "🛍️ Products",
        "Store Navigation": "🗺️ Navigation",
        "Policy Assistant": "📚 Policies",
        "AI Evaluation": "📊 Analytics",
        "My Shopping": "🛒 My Shopping",
        "Shopping Cart": "🍓 Shopping Cart"
    }[value],
    horizontal=True,
    key="main_navigation"
)


st.divider()


st.sidebar.divider()

st.sidebar.caption(
    "AI-Based Smart Retail Store Assistant"
)

# ============================================
# PAGE 1: DASHBOARD
# ============================================

if page == "Dashboard":

    catalogue = load_catalogue()

    st.header("Welcome to SmartMart AI!")
    st.write(
        "Your intelligent assistant for a smarter "
        "and more convenient shopping experience."
    )

    catalogue = load_catalogue()

    total_products = len(catalogue)

    available_products = len(
        catalogue[catalogue["stock"] > 0]
    )

    total_stock = int(catalogue["stock"].sum())

    policy_text = (
        DATA_DIR / "store_policies.txt"
    ).read_text(encoding="utf-8")

    total_policies = len(
        [
            item for item in policy_text.split("---")
            if item.strip()
        ]
    )

    # Display store statistics

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Products",
        total_products
    )

    col2.metric(
        "Available Products",
        available_products
    )

    col3.metric(
        "Total Stock",
        total_stock
    )

    col4.metric(
        "Store Policies",
        total_policies
    )

    st.divider()

    st.subheader("Your AI-Powered Retail Features")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            "🔍 Product Discovery\n\n"
            "Search products using filters and budgets."
        )

        st.info(
            "🤖 AI Recommendations\n\n"
            "Find products based on customer preferences."
        )

        st.info(
            "📚 Policy Assistant\n\n"
            "Ask questions about store policies."
        )

    with col2:

        st.info(
            "🗺️ Store Navigation\n\n"
            "Calculate efficient shopping routes."
        )

        st.info(
            "👥 Multi-Agent System\n\n"
            "Coordinate customer and store agents."
        )

        st.info(
            "📊 AI Paradigm Comparison\n\n"
            "Evaluate different AI approaches."
        )

# Featured products

    st.divider()

    st.subheader("🌿 Available Picks")

    featured_products = catalogue[
        catalogue["stock"] > 0
    ].sort_values(
        by="stock",
        ascending=False
    ).head(3)

    render_product_cards(
        featured_products,
        columns_per_row=3
    )
    st.divider()

    st.caption(
            "SmartMart is a simulated supermarket "
            "created for an AI-based university project."
        )

# ============================================
# PAGE 2: AI SHOPPING ASSISTANT
# ============================================

if page == "AI Shopping Assistant":

    st.header("🤖 AI Shopping Assistant")

    st.write(
        "Tell SmartMart what you want to buy. "
        "Our assistant will recommend products "
        "and plan your shopping route."
    )

    catalogue = load_catalogue()

    categories = sorted(
        catalogue["category"].dropna().unique().tolist()
    )

    with st.form("shopping_assistant_form"):

        query = st.text_input(
            "What are you looking for?",
            placeholder="Example: healthy snacks rich in protein"
        )

        budget = st.number_input(
            "Your maximum budget (₹)",
            min_value=0.0,
            value=float(customer.budget),
            step=50.0
        )

        category_choice = st.selectbox(
            "Product Category",
            [
                "Use customer preference",
                "All categories"
            ] + categories
        )

        dietary_choice = st.selectbox(
            "Dietary Preference",
            [
                "Use customer preference",
                "No restriction",
                "vegetarian",
                "vegan"
            ]
        )

        return_to_start = st.checkbox(
            "Return to store entrance after shopping"
        )

        submitted = st.form_submit_button(
            "Generate Shopping Plan",
            type="primary"
        )

    if submitted:

        if not query.strip():

            st.warning("Please enter your shopping requirements.")

        else:

            category = (
                None
                if category_choice == "Use customer preference"
                else ""
                if category_choice == "All categories"
                else category_choice
            )

            dietary = (
                None
                if dietary_choice == "Use customer preference"
                else ""
                if dietary_choice == "No restriction"
                else dietary_choice
            )

            request = customer.create_request(

                task="shopping_trip",

                query=query,

                budget=budget,

                category=category,

                dietary=dietary,

                return_to_start=return_to_start

            )

            store = StoreAssistantAgent()

            try:

                with st.spinner(
                    "Searching products and planning your route..."
                ):

                    response = store.handle_request(request)

                customer.receive_response(response)

                st.session_state["shopping_result"] = response

                if response.get("products") is not None:

                    record_activity(

                        customer.customer_id,

                        "shopping_trip",

                        query,

                        response["products"]["product_id"]
                        .astype(str)
                        .tolist()

                    )

            except Exception as error:

                st.error(f"Shopping assistant error: {error}")

    # Display saved result

    if "shopping_result" in st.session_state:

        response = st.session_state["shopping_result"]

        st.divider()

        if response["status"] == "success":

            st.success(response["message"])

            st.subheader("Recommended Products")

            st.dataframe(
                response["products"],
                use_container_width=True,
                hide_index=True
            )

            show_route(response["route"])

            st.subheader("AI Agent Activity")

            for tool in response["steps"]:

                st.write("✅ " + tool)

        else:

            st.warning(response["message"])

# ============================================
# PAGE 3: PRODUCT FINDER
# ============================================

if page == "Product Finder":

    st.header("🔍 Product Finder")

    st.write(
        "Search and filter products from the SmartMart catalogue."
    )

    catalogue = load_catalogue()

    categories = sorted(
        catalogue["category"].dropna().unique().tolist()
    )

    with st.form("product_search_form"):

        keyword = st.text_input(
            "Search by product name or keyword"
        )

        category = st.selectbox(
            "Category",
            ["All"] + categories
        )

        apply_budget = st.checkbox(
            "Apply maximum budget",
            value=True
        )

        budget = st.number_input(
            "Maximum Budget (₹)",
            min_value=0.0,
            value=float(customer.budget),
            step=50.0
        )

        dietary = st.selectbox(
            "Dietary Preference",
            [
                "Any",
                "vegetarian",
                "vegan"
            ]
        )

        submitted = st.form_submit_button(
            "Search Products"
        )

    if submitted:

        try:

            with st.spinner("Searching catalogue..."):

                results = search_products(

                    keyword=keyword.strip() or None,

                    category=(
                        None if category == "All"
                        else category
                    ),

                    max_price=(
                        budget if apply_budget else None
                    ),

                    dietary=(
                        None if dietary == "Any"
                        else dietary
                    )

                )

                st.session_state["product_results"] = results
                record_activity(

                    customer.customer_id,

                    "product_search",

                    keyword or "Browse products",

                    results["product_id"].astype(str).tolist()

                )       

        except Exception as error:

            st.error(f"Product search failed: {error}")

    
    if "product_results" in st.session_state:

        results = st.session_state["product_results"]

        st.divider()

        st.subheader("Search Results")

        st.metric(
            "Matching Products",
            len(results)
        )

        if results.empty:

            st.warning("No matching products found.")

        else:

            st.caption(
                f"Showing {len(results)} matching products"
            )

            render_product_cards(
                results,
                columns_per_row=3
            )

            with st.expander("View product data table"):

                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================
# PAGE 4: STORE NAVIGATION
# ============================================

if page == "Store Navigation":

    st.header("🗺️ Store Navigation")

    st.write(
        "Select products and find the most efficient "
        "shopping route through SmartMart."
    )

    catalogue = load_catalogue()

    available = catalogue[
        catalogue["stock"] > 0
    ].copy()

    product_names = {

        row["product_id"]:
        f"{row['name']} | ₹{row['price']} | Section {row['section']}"

        for _, row in available.iterrows()

    }

    with st.form("route_form"):

        selected_products = st.multiselect(

            "Select the products you want to collect",

            options=available["product_id"].tolist(),

            format_func=lambda pid: product_names[pid]

        )

        store_map = pd.read_csv(
            DATA_DIR / "store_map.csv"
        )

        locations = sorted(
            set(store_map["location"])
            | set(store_map["connected_to"])
        )

        start_location = st.selectbox(
            "Starting Location",
            locations,
            index=locations.index("Entrance")
            if "Entrance" in locations else 0
        )

        return_to_start = st.checkbox(
            "Return to starting location"
        )

        submitted = st.form_submit_button(
            "Calculate Shopping Route",
            type="primary"
        )

    if submitted:

        if not selected_products:

            st.warning("Please select at least one product.")

        else:

            try:

                with st.spinner("Calculating shortest route..."):

                    result = plan_shopping_route(

                        product_ids=selected_products,

                        start=start_location,

                        return_to_start=return_to_start

                    )

                    st.session_state["route_result"] = result

            except Exception as error:

                st.error(f"Route planning failed: {error}")

    if "route_result" in st.session_state:

        result = st.session_state["route_result"]

        st.divider()

        st.subheader("Your Shopping Route")

        st.success("Route calculated successfully!")

        st.write(
            " → ".join(result["route"])
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Walking Distance",
            f"{result['total_distance']:.1f} metres"
        )

        col2.metric(
            "Product Sections",
            len(result["visit_order"])
        )

        st.write("### Visit Order")

        st.write(
            " → ".join(result["visit_order"])
        )

        st.write("### Product Locations")

        st.dataframe(
            result["available_products"][
                ["name", "price", "section", "stock"]
            ],
            use_container_width=True,
            hide_index=True
        )

        if not result["unavailable_products"].empty:

            st.warning("Some products are out of stock.")

            st.dataframe(
                result["unavailable_products"],
                use_container_width=True,
                hide_index=True
            )

# ============================================
# PAGE 5: POLICY ASSISTANT
# ============================================

if page == "Policy Assistant":

    st.header("📚 AI Store Policy Assistant")

    st.write(
        "Ask questions about product returns, refunds, "
        "discounts and other SmartMart policies."
    )

    with st.form("policy_form"):

        question = st.text_area(
            "Enter your question",

            placeholder=(
                "Example: Can I return an opened product?"
            )
        )

        submitted = st.form_submit_button(
            "Ask AI Assistant",
            type="primary"
        )

    if submitted:

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            try:

                with st.spinner(
                    "Retrieving policies and generating an answer..."
                ):

                    result = generate_grounded_answer(
                        question
                    )

                    st.session_state["policy_result"] = result
                    record_activity(

                        customer.customer_id,

                        "policy_question",

                        question,

                        []

                    )

            except Exception as error:

                st.error(f"Policy assistant error: {error}")

    if "policy_result" in st.session_state:

        result = st.session_state["policy_result"]

        st.divider()

        st.subheader("AI Generated Answer")

        st.success(result["answer"])

        st.subheader("Retrieved Policy References")

        if result["sources"]:

            for source in result["sources"]:

                with st.expander(
                    source["title"]
                ):

                    st.write(
                        "**Policy ID:**",
                        source["policy_id"]
                    )

                    st.write(
                        "**Source:**",
                        source["source"]
                    )

                    st.write(
                        "**Retrieval Similarity:**",
                        source["similarity"]
                    )

        else:

            st.info(
                "No supporting policy documents were retrieved."
            )

        st.caption(
            "Answers are generated using the simulated "
            "SmartMart policy documents."
        )

# ============================================
# PAGE 6: AI EVALUATION
# ============================================

if page == "AI Evaluation":

    st.header("📊 AI Paradigm Comparison")

    st.write(
        "Compare the performance of different AI approaches "
        "implemented in SmartMart."
    )

    SUMMARY_FILE = (
        EVALUATION_DIR / "evaluation_summary.csv"
    )

    RESULTS_FILE = (
        EVALUATION_DIR / "evaluation_results.csv"
    )

    if SUMMARY_FILE.exists():

        summary = pd.read_csv(SUMMARY_FILE)

        st.subheader("Performance Summary")

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("AI Paradigm Performance")

        fig = px.bar(

            summary,

            x="paradigm",

            y="pass_rate_percent",

            color="task",

            barmode="group",

            text="pass_rate_percent",

            title="AI Paradigm Pass Rate Comparison",

            labels={
                "paradigm": "AI Paradigm",
                "pass_rate_percent": "Pass Rate (%)",
                "task": "Evaluation Task"
            }

        )

        fig.update_layout(

            yaxis_range=[0, 100],

            template="plotly_white",

            xaxis_tickangle=-20

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning(
            "Evaluation results not found. "
            "Run the Module 6 evaluation first."
        )

    if RESULTS_FILE.exists():

        st.divider()

        st.subheader("Detailed Test Results")

        results = pd.read_csv(RESULTS_FILE)

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )

    REVIEW_FILE = (
        EVALUATION_DIR / "manual_review.csv"
    )

    if REVIEW_FILE.exists():

        st.divider()

        st.subheader("Manual LLM Answer Evaluation")

        review = pd.read_csv(REVIEW_FILE)

        st.write(
            "Use this worksheet to record manual factuality "
            "and groundedness assessments."
        )

        st.dataframe(
            review,
            use_container_width=True,
            hide_index=True
        )

# ============================================
# PAGE 7: MY SHOPPING
# ============================================

if page == "My Shopping":

    st.header("🛒 My Shopping")

    st.write(
        "Manage your saved products and view "
        "your personal shopping activity."
    )

    catalogue = load_catalogue()

    customer_id = customer.customer_id

    # ----------------------------------------
    # TAB NAVIGATION
    # ----------------------------------------

    tab1, tab2 = st.tabs([
        "❤️ Saved Products",
        "🕒 Shopping History"
    ])

    # ========================================
    # TAB 1: SAVED PRODUCTS
    # ========================================

    with tab1:

        st.subheader("Your Saved Shopping List")

        available = catalogue.copy()

        # Select product to save
        product_options = {
            str(row["product_id"]):
            f"{row['name']} - ₹{row['price']}"

            for _, row in available.iterrows()
        }

        with st.form("save_product_form"):

            selected_id = st.selectbox(

                "Choose a product to save",

                options=list(product_options.keys()),

                format_func=lambda pid: product_options[pid],

                key="saved_product_selector"

            )

            add_button = st.form_submit_button(
                "❤️ Save Product",
                type="primary"
            )

        if add_button:

            saved = save_shopping_item(
                customer_id,
                selected_id
            )

            if saved:

                st.success("Product added to your saved list!")

            else:

                st.info("This product is already saved.")

        st.divider()

        # Retrieve saved products
        saved_items = get_saved_items(customer_id)

        saved_ids = [
            item["product_id"]
            for item in saved_items
        ]

        saved_products = catalogue[
            catalogue["product_id"]
            .astype(str)
            .isin(saved_ids)
        ]

        st.metric(
            "Saved Products",
            len(saved_products)
        )

        if saved_products.empty:

            st.info(
                "Your shopping list is empty. "
                "Start saving your favourite products!"
            )

        else:

            render_product_cards(
                saved_products,
                columns_per_row=3
            )

            st.subheader("Remove a Saved Product")

            remove_id = st.selectbox(

                "Choose product to remove",

                options=saved_ids,

                format_func=lambda pid: product_options.get(
                    pid,
                    pid
                ),

                key="remove_saved_product"

            )

            if st.button(
                "Remove from List",
                key="remove_saved_button"
            ):

                remove_saved_item(
                    customer_id,
                    remove_id
                )

                st.success("Product removed.")

                st.rerun()

    # ========================================
    # TAB 2: SHOPPING HISTORY
    # ========================================

    with tab2:

        st.subheader("Your Recent Activity")

        history = get_activity_history(
            customer_id,
            limit=20
        )

        if history:

            history_df = pd.DataFrame(history)

            history_df["product_ids"] = (
                history_df["product_ids"]
                .apply(
                    lambda ids: ", ".join(ids)
                    if ids else "None"
                )
            )

            history_df = history_df.rename(
                columns={
                    "activity_type": "Activity",
                    "query": "Customer Request",
                    "product_ids": "Products",
                    "created_at": "Date and Time"
                }
            )

            st.dataframe(

                history_df[
                    [
                        "Activity",
                        "Customer Request",
                        "Products",
                        "Date and Time"
                    ]
                ],

                use_container_width=True,

                hide_index=True

            )

        else:

            st.info(
                "No shopping activity has been recorded yet."
            )

# ============================================
# PAGE: SHOPPING CART
# ============================================

if page == "Shopping Cart":

    st.header("🛒 Your Shopping Cart")

    st.write(
        "Manage your products, control your spending "
        "and optimise your shopping basket."
    )

    customer_id = customer.customer_id

    catalogue = load_catalogue()

    available_products = catalogue[
        catalogue["stock"] > 0
    ].copy()

    # ----------------------------------------
    # ADD PRODUCTS
    # ----------------------------------------

    st.subheader("Add Products to Cart")

    product_labels = {

        str(row["product_id"]):
        f"{row['name']} | ₹{row['price']} | "
        f"{row['stock']} available"

        for _, row in available_products.iterrows()

    }

    if available_products.empty:

        st.warning("No products are currently available.")

    else:

        with st.form("add_to_cart_form"):

            selected_product = st.selectbox(

                "Select Product",

                options=list(product_labels.keys()),

                format_func=lambda pid: product_labels[pid],

                key="cart_product_selector"

            )

            quantity = st.number_input(

                "Quantity",

                min_value=1,

                max_value=100,

                value=1,

                step=1,

                key="cart_add_quantity"

            )

            add_button = st.form_submit_button(

                "🛒 Add to Cart",

                type="primary"

            )

        if add_button:

            success, message = add_to_cart(

                customer_id,

                selected_product,

                int(quantity)

            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)

    st.divider()

    # ----------------------------------------
    # DISPLAY CART
    # ----------------------------------------

    st.subheader("Your Cart Items")

    cart = get_cart(customer_id)

    if cart.empty:

        st.info(
            "Your shopping cart is empty. "
            "Add some products to get started!"
        )

    else:

        # Calculate total
        cart_total = float(
            cart["line_total"].fillna(0).sum()
        )

        budget = float(customer.budget)

        all_available = bool(
            cart["available"].all()
        )

        # Cart statistics
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Cart Products",
            len(cart)
        )

        col2.metric(
            "Basket Total",
            f"₹{cart_total:.2f}"
        )

        col3.metric(
            "Your Budget",
            f"₹{budget:.2f}"
        )

        # Display cart table
        display_columns = [

            "product_id",
            "name",
            "price",
            "quantity",
            "line_total",
            "section",
            "stock",
            "available"

        ]

        st.dataframe(

            cart[display_columns],

            use_container_width=True,

            hide_index=True

        )

        # ------------------------------------
        # UPDATE PRODUCT QUANTITY
        # ------------------------------------

        st.subheader("Update Cart Quantity")

        cart_product_ids = (
            cart["product_id"].astype(str).tolist()
        )

        selected_cart_product = st.selectbox(

            "Select Product to Update",

            options=cart_product_ids,

            format_func=lambda pid: product_labels.get(
                pid,
                pid
            ),

            key="cart_update_selector"

        )

        current_row = cart[
            cart["product_id"].astype(str)
            == selected_cart_product
        ].iloc[0]

        new_quantity = st.number_input(

            "New Quantity",

            min_value=1,

            max_value=max(
                1,
                int(current_row["stock"])
            ),

            value=int(current_row["quantity"]),

            key="cart_updated_quantity"

        )

        if st.button(
            "Update Quantity",
            key="update_cart_button"
        ):

            success, message = update_cart_quantity(

                customer_id,

                selected_cart_product,

                int(new_quantity)

            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)

        # ------------------------------------
        # REMOVE AND CLEAR ITEMS
        # ------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🗑️ Remove Selected Product",
                key="remove_cart_item"
            ):

                removed = remove_from_cart(

                    customer_id,

                    selected_cart_product

                )

                if removed:

                    st.success("Product removed.")

                    st.rerun()

        with col2:

            if st.button(
                "Clear Entire Cart",
                key="clear_entire_cart"
            ):

                clear_cart(customer_id)

                st.success("Your cart has been cleared.")

                st.rerun()

        st.divider()

        # ------------------------------------
        # BUDGET CHECK
        # ------------------------------------

        st.subheader("💰 Budget Analysis")

        if budget > 0:

            budget_usage = cart_total / budget

            st.progress(
                min(budget_usage, 1.0)
            )

            if not all_available:

                st.warning(
                    "Some cart products do not have sufficient "
                    "available stock. Remove or adjust them."
                )

            if cart_total <= budget and all_available:

                st.success(
                    f"Your basket fits within your budget! "
                    f"You have ₹{budget - cart_total:.2f} remaining."
                )

            else:

                st.warning(
                    f"Your cart exceeds your budget or contains "
                    f"unavailable products. Basket total: "
                    f"₹{cart_total:.2f}, Budget: ₹{budget:.2f}."
                )

                # --------------------------------
                # OPTIMISE BASKET
                # --------------------------------

                st.subheader(
                    "✨ Optimise Your Shopping Basket"
                )

                suggestion = optimize_cart_for_budget(

                    cart,

                    budget

                )

                if suggestion["items"].empty:

                    st.info(
                        "No available product units fit "
                        "within your current budget."
                    )

                else:

                    st.write(
                        "Here is a suggested selection "
                        "that fits your budget."
                    )

                    st.dataframe(

                        suggestion["items"],

                        use_container_width=True,

                        hide_index=True

                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Optimised Total",
                        f"₹{suggestion['total']:.2f}"
                    )

                    col2.metric(
                        "Remaining Budget",
                        f"₹{suggestion['remaining']:.2f}"
                    )

                    col3.metric(
                        "Units Selected",
                        suggestion["units_selected"]
                    )

                    if st.button(
                        "Apply Optimised Basket",
                        type="primary",
                        key="apply_optimized_cart"
                    ):

                        try:

                            replace_cart_contents(

                                customer_id,

                                suggestion["items"]

                            )

                            st.success(
                                "Optimised basket applied!"
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Could not update basket: {error}"
                            )

        # ------------------------------------
        # PLAN FINAL SHOPPING ROUTE
        # ------------------------------------

        st.divider()

        st.subheader("🗺️ Shopping Route")

        if all_available and cart_total <= budget:

            if st.button(
                "Calculate Route for My Cart",
                type="primary",
                key="cart_route_button"
            ):

                product_ids = (
                    cart["product_id"].astype(str).tolist()
                )

                try:

                    route_result = plan_shopping_route(

                        product_ids=product_ids,

                        start="Entrance",

                        return_to_start=False

                    )

                    st.session_state["cart_route_result"] = (
                        route_result
                    )

                except Exception as error:

                    st.error(
                        f"Route calculation failed: {error}"
                    )

        else:

            st.info(
                "Bring your basket within budget and "
                "ensure all products are available to "
                "calculate your final shopping route."
            )

        if "cart_route_result" in st.session_state:

            show_route(
                st.session_state["cart_route_result"]
            )
