
from pathlib import Path
import os
import time
import pandas as pd

from dotenv import load_dotenv
from openai import OpenAI


# Locate project files
BASE_DIR = Path(__file__).resolve().parent.parent

TEST_FILE = BASE_DIR / "evaluation" / "test_cases.csv"

OUTPUT_FILE = (
    BASE_DIR / "evaluation" / "standalone_llm_answers.csv"
)

# Load API settings
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

if not api_key or not model:
    raise RuntimeError(
        "Check OPENAI_API_KEY and OPENAI_MODEL in .env"
    )

client = OpenAI(api_key=api_key)


# Load only policy questions
cases = pd.read_csv(TEST_FILE)

cases = cases[cases["task"] == "policy"]

results = []

instructions = """
You are a general customer-service assistant.

You do not have access to SmartMart's internal
policy documents or private store database.

Do not invent store-specific policies.

If you cannot verify a store-specific rule,
clearly explain that you do not have enough
information to confirm it.

You may explain general concepts, but distinguish
them from verified SmartMart policies.
"""


# Generate answers without retrieval
for _, case in cases.iterrows():

    question = case["query"]

    start = time.perf_counter()

    response = client.responses.create(

        model=model,

        instructions=instructions,

        input=question

    )

    latency = (
        time.perf_counter() - start
    ) * 1000

    answer = response.output_text or ""

    results.append({

        "case_id": case["case_id"],

        "question": question,

        "expected_policy_id": case["expected_policy_id"],

        "standalone_answer": answer,

        "latency_ms": round(latency, 2)

    })

    print("\nQUESTION:", question)

    print("\nSTANDALONE LLM ANSWER:")

    print(answer)


# Save answers
pd.DataFrame(results).to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nStandalone LLM evaluation completed.")

print("Results saved at:", OUTPUT_FILE)
