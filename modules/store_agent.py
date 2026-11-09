
# -------------------------------------------
# IMPORT EXISTING AI MODULES
# -------------------------------------------

from modules.product_search import search_products

from modules.recommendation import recommend_products

from modules.route_planner import plan_shopping_route

from modules.policy_rag import generate_grounded_answer


# -------------------------------------------
# CREATE STORE ASSISTANT AGENT
# -------------------------------------------

class StoreAssistantAgent:

    def __init__(self):

        self.name = "SmartMart Store Assistant"

        self.tools_used = []

    # ---------------------------------------
    # STEP 1: HANDLE CUSTOMER REQUEST
    # ---------------------------------------

    def handle_request(self, request):

        task = request["task"]

        self.tools_used = []

        # Handle product search
        if task == "search":

            return self.search_tool(request)

        # Handle product recommendations
        elif task == "recommend":

            return self.recommendation_tool(request)

        # Handle complete shopping trip
        elif task == "shopping_trip":

            return self.shopping_trip_tool(request)

        # Handle policy questions
        elif task == "policy":

            return self.policy_tool(request)

        # Handle direct route requests
        elif task == "route":

            return self.route_tool(request)

        else:

            return {
                "status": "error",
                "message": "I cannot handle this request."
            }

    # ---------------------------------------
    # STEP 2: PRODUCT SEARCH TOOL
    # ---------------------------------------

    def search_tool(self, request):

        self.tools_used.append("Product Search")

        result = search_products(
            keyword=request.get("query"),
            category=request.get("category"),
            max_price=request.get("budget"),
            dietary=request.get("dietary")
        )

        return {
            "status": "success",
            "message": "Product search completed.",
            "products": result,
            "steps": self.tools_used.copy()
        }

    # ---------------------------------------
    # STEP 3: RECOMMENDATION TOOL
    # ---------------------------------------

    def recommendation_tool(self, request):

        self.tools_used.append("Recommendation Engine")

        result = recommend_products(

            query=request.get("query"),

            max_price=request.get("budget"),

            category=request.get("category"),

            dietary=request.get("dietary"),

            top_n=5
        )

        return {
            "status": "success",
            "message": "Product recommendations generated.",
            "products": result,
            "steps": self.tools_used.copy()
        }

    # ---------------------------------------
    # STEP 4: COMPLETE SHOPPING TRIP
    # ---------------------------------------

    def shopping_trip_tool(self, request):

        # First, recommend products
        products = self.recommendation_tool(request)

        recommended = products["products"]

        if recommended.empty:

            return {
                "status": "no_products",
                "message": "No suitable products were found.",
                "products": recommended,
                "steps": self.tools_used.copy()
            }

        # Extract recommended product IDs
        product_ids = recommended[
            "product_id"
        ].tolist()

        # Next, calculate the store route
        self.tools_used.append("Store Route Planner")

        route = plan_shopping_route(

            product_ids=product_ids,

            start="Entrance",

            return_to_start=request.get(
                "return_to_start", False
            )
        )

        return {
            "status": "success",
            "message": "Shopping trip planned successfully.",
            "products": recommended,
            "route": route,
            "steps": self.tools_used.copy()
        }

    # ---------------------------------------
    # STEP 5: POLICY ASSISTANT TOOL
    # ---------------------------------------

    def policy_tool(self, request):

        self.tools_used.append("RAG Policy Assistant")

        question = request.get("policy_question")

        if not question:
            question = request.get("query")

        result = generate_grounded_answer(
            question=question
        )

        return {
            "status": "success",
            "message": "Policy question answered.",
            "answer": result["answer"],
            "sources": result["sources"],
            "steps": self.tools_used.copy()
        }

    # ---------------------------------------
    # STEP 6: DIRECT ROUTE TOOL
    # ---------------------------------------

    def route_tool(self, request):

        self.tools_used.append("Store Route Planner")

        route = plan_shopping_route(

            product_ids=request.get("product_ids", []),

            start="Entrance",

            return_to_start=request.get(
                "return_to_start", False
            )
        )

        return {
            "status": "success",
            "message": "Shopping route calculated.",
            "route": route,
            "steps": self.tools_used.copy()
        }

