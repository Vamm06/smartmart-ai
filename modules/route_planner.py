from pathlib import Path
import pandas as pd
import networkx as nx


# -------------------------------------------
# STEP 1: LOCATE OUR DATA FILES
# -------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"
INVENTORY_FILE = BASE_DIR / "data" / "inventory.csv"
MAP_FILE = BASE_DIR / "data" / "store_map.csv"


# -------------------------------------------
# STEP 2: CREATE THE STORE GRAPH
# -------------------------------------------

def load_store_graph():

    store_map = pd.read_csv(MAP_FILE)

    required_columns = {
        "location",
        "connected_to",
        "distance"
    }

    if not required_columns.issubset(store_map.columns):
        raise ValueError("Store map is missing required columns.")

    graph = nx.Graph()

    for _, row in store_map.iterrows():

        location = str(row["location"]).strip()
        connected_to = str(row["connected_to"]).strip()
        distance = float(row["distance"])

        if (
            not location
            or not connected_to
            or not pd.notna(distance)
            or distance < 0
        ):
            raise ValueError("Invalid store map connection.")

        graph.add_edge(
            location,
            connected_to,
            weight=distance
        )

    return graph


# -------------------------------------------
# STEP 3: LOAD PRODUCTS AND INVENTORY
# -------------------------------------------

def load_products():

    products = pd.read_csv(PRODUCTS_FILE)
    inventory = pd.read_csv(INVENTORY_FILE)

    products["product_id"] = (
        products["product_id"].astype(str).str.strip().str.upper()
    )

    inventory["product_id"] = (
        inventory["product_id"].astype(str).str.strip().str.upper()
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


# -------------------------------------------
# STEP 4: PLAN THE SHOPPING ROUTE
# -------------------------------------------

def plan_shopping_route(
    product_ids,
    start="Entrance",
    return_to_start=False
):

    if not product_ids:
        raise ValueError("Please select at least one product.")

    product_ids = list(dict.fromkeys(
        str(pid).strip().upper() for pid in product_ids
    ))

    catalogue = load_products()

    # Find the requested products
    missing_ids = [
        pid for pid in product_ids
        if pid not in set(catalogue["product_id"])
    ]

    if missing_ids:
        raise ValueError(f"Unknown product IDs: {missing_ids}")

    selected = catalogue[
        catalogue["product_id"].isin(product_ids)
    ].copy()

    # Separate available and unavailable products
    available = selected[
        selected["stock"] > 0
    ].copy()

    unavailable = selected[
        selected["stock"] <= 0
    ].copy()

    if available.empty:
        raise ValueError("All requested products are out of stock.")

    # Identify product locations
    available["section"] = (
        available["section"].fillna("").astype(str).str.strip()
    )

    if (available["section"] == "").any():
        raise ValueError("A product has no store section assigned.")

    # Remove duplicate sections
    stops = list(dict.fromkeys(available["section"].tolist()))

    # Load store graph
    graph = load_store_graph()

    if start not in graph:
        raise ValueError(f"Starting location {start} does not exist.")

    missing_sections = [
        section for section in stops
        if section not in graph
    ]

    if missing_sections:
        raise ValueError(
            f"Store map has no locations for: {missing_sections}"
        )

    # ---------------------------------------
    # NEAREST-NEIGHBOUR ROUTE PLANNING
    # ---------------------------------------

    remaining = stops.copy()

    current = start

    route = [start]
    visit_order = []

    # If the customer starts at a requested section
    if current in remaining:
        remaining.remove(current)
        visit_order.append(current)

    while remaining:

        # Calculate shortest distances from current location
        distances, paths = nx.single_source_dijkstra(
            graph,
            source=current,
            weight="weight"
        )

        # Find reachable unvisited sections
        reachable = [
            section for section in remaining
            if section in distances
        ]

        if not reachable:
            raise nx.NetworkXNoPath(
                "Some product locations are disconnected."
            )

        # Select the nearest section
        next_stop = min(
            reachable,
            key=lambda section: distances[section]
        )

        # Get the shortest path to that section
        shortest_leg = paths[next_stop]

        # Add every location in that path
        for location in shortest_leg[1:]:

            route.append(location)

            # Collect any requested products in sections
            # encountered along the way
            if location in remaining:
                remaining.remove(location)
                visit_order.append(location)

        current = next_stop

    # ---------------------------------------
    # OPTIONAL: RETURN TO ENTRANCE
    # ---------------------------------------

    if return_to_start and current != start:

        return_path = nx.shortest_path(
            graph,
            source=current,
            target=start,
            weight="weight"
        )

        route.extend(return_path[1:])

    # ---------------------------------------
    # CALCULATE TOTAL WALKING DISTANCE
    # ---------------------------------------

    total_distance = sum(
        graph[u][v]["weight"]
        for u, v in zip(route, route[1:])
    )

    return {
        "available_products": available,
        "unavailable_products": unavailable,
        "route": route,
        "visit_order": visit_order,
        "total_distance": total_distance
    }


# -------------------------------------------
# STEP 5: TEST THE ROUTE PLANNER
# -------------------------------------------

def display_route_plan(plan):

    print("\nAVAILABLE PRODUCTS")
    print("------------------")

    print(
        plan["available_products"][
            ["product_id", "name", "section", "stock"]
        ].to_string(index=False)
    )

    if not plan["unavailable_products"].empty:

        print("\nOUT OF STOCK PRODUCTS")
        print("---------------------")

        print(
            plan["unavailable_products"][
                ["product_id", "name"]
            ].to_string(index=False)
        )

    print("\nPRODUCT SECTION ORDER")
    print("---------------------")

    print(" -> ".join(plan["visit_order"]))

    print("\nSHOPPING ROUTE")
    print("--------------")

    print(" -> ".join(plan["route"]))

    print(
        f"\nTOTAL WALKING DISTANCE: "
        f"{plan['total_distance']:.1f} metres"
    )


if __name__ == "__main__":

    customer_products = ["P001", "P004"]

    result = plan_shopping_route(
        product_ids=customer_products,
        start="Entrance",
        return_to_start=False
    )

    display_route_plan(result)
