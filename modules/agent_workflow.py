
# -------------------------------------------
# IMPORT BOTH AGENTS
# -------------------------------------------

from modules.customer_agent import CustomerAgent

from modules.store_agent import StoreAssistantAgent


# -------------------------------------------
# STEP 1: DISPLAY STORE RESPONSE
# -------------------------------------------

def display_response(response):

    print("\nSTORE ASSISTANT RESPONSE")
    print("========================")

    print(response["message"])

    # Display products
    if "products" in response:

        products = response["products"]

        print("\nRECOMMENDED PRODUCTS")
        print("--------------------")

        if products.empty:
            print("No suitable products found.")

        else:
            print(products.to_string(index=False))

    # Display route
    if "route" in response:

        route = response["route"]

        print("\nSHOPPING ROUTE")
        print("--------------")

        print(" -> ".join(route["route"]))

        print(
            "Total walking distance:",
            route["total_distance"],
            "metres"
        )

    # Display policy answer
    if "answer" in response:

        print("\nPOLICY ANSWER")
        print("-------------")

        print(response["answer"])

        print("\nPOLICY SOURCES")

        for source in response["sources"]:

            print(
                source["policy_id"],
                "-",
                source["source"]
            )

    # Display tool usage
    print("\nTOOLS USED")
    print("----------")

    for tool in response.get("steps", []):

        print("->", tool)


# -------------------------------------------
# STEP 2: START MULTI-AGENT SIMULATION
# -------------------------------------------

if __name__ == "__main__":

    # Create customer agent
    customer = CustomerAgent("C001")

    # Create store assistant agent
    store = StoreAssistantAgent()

    # Display customer information
    customer.display_profile()

    # Customer creates a shopping request
    request = customer.create_request(
    task="shopping_trip",
    query="healthy snacks rich in protein"
)
    print("\nCUSTOMER REQUEST")
    print("----------------")

    print(request["query"])

    print("\nCUSTOMER AGENT")
    print("Sending request to Store Assistant...")

    # Store assistant receives the request
    response = store.handle_request(request)

    # Customer receives the response
    customer.receive_response(response)

    # Display final result
    display_response(response)

    # Display updated customer shopping list
    print("\nUPDATED CUSTOMER SHOPPING LIST")
    print("------------------------------")

    print(customer.shopping_list)
