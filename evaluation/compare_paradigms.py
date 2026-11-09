
from pathlib import Path
import time
import pandas as pd

# Import our existing AI modules
from modules.product_search import search_products

from modules.recommendation import recommend_products

from modules.policy_rag import retrieve_policies

from modules.store_agent import StoreAssistantAgent


# --------------------------------------------------
# STEP 1: FILE LOCATIONS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TEST_FILE = BASE_DIR / "evaluation" / "test_cases.csv"

RESULTS_FILE = (
    BASE_DIR / "evaluation" / "evaluation_results.csv"
)

SUMMARY_FILE = (
    BASE_DIR / "evaluation" / "evaluation_summary.csv"
)


# --------------------------------------------------
# STEP 2: LOAD TEST DATA
# --------------------------------------------------

def load_test_cases():

    if not TEST_FILE.exists():
        raise FileNotFoundError(
            "test_cases.csv was not found."
        )

    return pd.read_csv(TEST_FILE)


def parse_ids(value):

    if pd.isna(value) or not str(value).strip():
        return set()

    return {
        item.strip().upper()
        for item in str(value).split("|")
        if item.strip()
    }


def optional_value(value):

    if pd.isna(value) or str(value).strip() == "":
        return None

    return value


# --------------------------------------------------
# STEP 3: RULE-BASED POLICY SYSTEM
# --------------------------------------------------

def rule_based_policy(question):

    question = question.lower()

    # Receipt-related questions
    if "receipt" in question:
        return "RECEIPT-001"

    # Perishable product questions
    if "perishable" in question:
        return "RETURN-002"

    # Refund questions
    if "refund" in question:
        return "REFUND-001"

    # Combining discounts
    if "discount" in question and (
        "combine" in question or "two" in question
    ):
        return "DISCOUNT-002"

    # Membership discounts
    if "member" in question or "membership" in question:
        return "DISCOUNT-001"

    # Opened product returns
    if (
        "opened" in question
        or "shampoo" in question
    ):
        return "RETURN-001"

    return None


# --------------------------------------------------
# STEP 4: EVALUATE PRODUCT RECOMMENDATIONS
# --------------------------------------------------

def evaluate_product_case(case, results):

    query = case["query"]

    category = optional_value(case["category"])
    dietary = optional_value(case["dietary"])
    budget = optional_value(case["budget"])

    if budget is not None:
        budget = float(budget)

    expected = parse_ids(
        case["expected_product_ids"]
    )

    # Test 1: Rule-based system
    start_time = time.perf_counter()

    rule_result = search_products(
        category=category,
        max_price=budget,
        dietary=dietary
    )

    rule_time = (
        time.perf_counter() - start_time
    ) * 1000

    rule_ids = set(
        rule_result["product_id"]
        .astype(str).str.upper()
    )

    # Test 2: TF-IDF recommendation system
    start_time = time.perf_counter()

    ml_result = recommend_products(
        query=query,
        category=category,
        max_price=budget,
        dietary=dietary,
        top_n=5
    )

    ml_time = (
        time.perf_counter() - start_time
    ) * 1000

    ml_ids = set(
        ml_result["product_id"]
        .astype(str).str.upper()
    )

    # Calculate metrics for both systems
    systems = [
        ("Rule-based AI", rule_ids, rule_time),
        ("TF-IDF Recommendation", ml_ids, ml_time)
    ]

    for name, actual, latency in systems:

        true_positive = len(expected & actual)

        precision = (
            true_positive / len(actual)
            if actual else 0
        )

        recall = (
            true_positive / len(expected)
            if expected else 0
        )

        passed = expected.issubset(actual)

        results.append({

            "case_id": case["case_id"],

            "paradigm": name,

            "task": "Product Recommendation",

            "passed": int(passed),

            "precision": precision,

            "recall": recall,

            "latency_ms": latency,

            "actual_results": "|".join(sorted(actual))

        })


# --------------------------------------------------
# STEP 5: EVALUATE POLICY SYSTEMS
# --------------------------------------------------


def evaluate_policy_case(case, results):

    question = case["query"]

    expected_value = optional_value(
        case["expected_policy_id"]
    )

    expected = (
        str(expected_value).strip().upper()
        if expected_value is not None
        else None
    )

    # Rule-based policy system
    start_time = time.perf_counter()

    rule_policy = rule_based_policy(question)

    rule_time = (
        time.perf_counter() - start_time
    ) * 1000

    rule_passed = (
        rule_policy == expected
        if expected is not None
        else rule_policy is None
    )

    results.append({

        "case_id": case["case_id"],

        "paradigm": "Rule-based AI",

        "task": "Policy Question",

        "passed": int(rule_passed),

        "precision": None,

        "recall": None,

        "latency_ms": rule_time,

        "actual_results": rule_policy or "No match"

    })

    # RAG policy retrieval
    start_time = time.perf_counter()

    rag_result = retrieve_policies(
        question,
        top_k=3
    )

    rag_time = (
        time.perf_counter() - start_time
    ) * 1000

    retrieved_ids = set(
        rag_result["policy_id"]
        .astype(str).str.upper()
    )

    rag_passed = (
        expected in retrieved_ids
        if expected is not None
        else rag_result.empty
    )

    results.append({

        "case_id": case["case_id"],

        "paradigm": "RAG Retrieval",

        "task": "Policy Question",

        "passed": int(rag_passed),

        "precision": None,

        "recall": None,

        "latency_ms": rag_time,

        "actual_results": "|".join(
            sorted(retrieved_ids)
        ) if retrieved_ids else "No match"

    })


# --------------------------------------------------
# STEP 6: EVALUATE AGENTIC WORKFLOW
# --------------------------------------------------

def evaluate_agent_case(case, results):

    store_agent = StoreAssistantAgent()

    request = {

        "task": "shopping_trip",

        "query": case["query"],

        "category": optional_value(
            case["category"]
        ),

        "budget": float(case["budget"]),

        "dietary": optional_value(
            case["dietary"]
        ),

        "return_to_start": False

    }

    expected = parse_ids(
        case["expected_product_ids"]
    )

    start_time = time.perf_counter()

    response = store_agent.handle_request(request)

    latency = (
        time.perf_counter() - start_time
    ) * 1000

    actual = set()

    if "products" in response:

        actual = set(
            response["products"]["product_id"]
            .astype(str).str.upper()
        )

    route_exists = (
        "route" in response
        and bool(response["route"].get("route"))
    )

    passed = (
        response.get("status") == "success"
        and expected.issubset(actual)
        and route_exists
    )

    details = (
        "Products: " + "|".join(sorted(actual))
        + "; Tools: "
        + "|".join(response.get("steps", []))
    )

    results.append({

        "case_id": case["case_id"],

        "paradigm": "Tool-Using Agent Workflow",

        "task": "Shopping Task",

        "passed": int(passed),

        "precision": None,

        "recall": None,

        "latency_ms": latency,

        "actual_results": details

    })


# --------------------------------------------------
# STEP 7: RUN ALL TESTS
# --------------------------------------------------

def run_evaluation():

    test_cases = load_test_cases()

    results = []

    for _, case in test_cases.iterrows():

        task = case["task"]

        if task == "product":

            evaluate_product_case(case, results)

        elif task == "policy":

            evaluate_policy_case(case, results)

        elif task == "agent_shopping":

            evaluate_agent_case(case, results)

    return pd.DataFrame(results)


# --------------------------------------------------
# STEP 8: CREATE COMPARISON SUMMARY
# --------------------------------------------------

def create_summary(results):

    summary = (
        results.groupby(
            ["paradigm", "task"],
            as_index=False
        )
        .agg(
            test_cases=("case_id", "count"),

            passed_tests=("passed", "sum"),

            pass_rate=("passed", "mean"),

            average_latency_ms=("latency_ms", "mean")
        )
    )

    summary["pass_rate_percent"] = (
        summary["pass_rate"] * 100
    ).round(2)

    summary["average_latency_ms"] = (
        summary["average_latency_ms"].round(2)
    )

    return summary


# --------------------------------------------------
# STEP 9: DISPLAY AND SAVE RESULTS
# --------------------------------------------------

if __name__ == "__main__":

    print("\nSMARTMART AI PARADIGM EVALUATION")
    print("================================")

    results = run_evaluation()

    summary = create_summary(results)

    # Save detailed test results
    results.to_csv(
        RESULTS_FILE,
        index=False
    )

    # Save comparison summary
    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    print("\nDETAILED RESULTS")
    print("----------------")

    print(results.to_string(index=False))

    print("\nPARADIGM COMPARISON")
    print("-------------------")

    print(summary.to_string(index=False))

    print("\nFILES GENERATED")
    print("----------------")

    print(RESULTS_FILE)
    print(SUMMARY_FILE)

    print("\nEvaluation completed successfully!")
