from pathlib import Path
import re
import os
import pandas as pd

from dotenv import load_dotenv
from openai import OpenAI


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------------------
# STEP 1: LOCATE POLICY DOCUMENT
# -------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

POLICY_FILE = BASE_DIR / "data" / "store_policies.txt"


# -------------------------------------------
# STEP 2: LOAD POLICY DOCUMENTS
# -------------------------------------------

def load_policies():

    if not POLICY_FILE.exists():
        raise FileNotFoundError(
            "store_policies.txt was not found in the data folder."
        )

    content = POLICY_FILE.read_text(encoding="utf-8")

    # Separate individual policies using ---
    blocks = re.split(
        r"(?m)^\s*---\s*$",
        content
    )

    records = []

    for block in blocks:

        if not block.strip():
            continue

        record = {}

        for line in block.splitlines():

            if ":" in line:

                key, value = line.split(":", 1)

                record[key.strip().lower()] = value.strip()

        required_fields = [
            "policy_id",
            "title",
            "topic",
            "source",
            "text"
        ]

        missing = [
            field for field in required_fields
            if not record.get(field)
        ]

        if missing:
            raise ValueError(
                f"Policy is missing fields: {missing}"
            )

        records.append(record)

    if not records:
        raise ValueError("No policies were found.")

    policies = pd.DataFrame(records)

    # Create searchable text for each policy
    policies["search_text"] = (
        policies["title"] + " " +
        policies["topic"] + " " +
        policies["text"]
    )

    return policies


# -------------------------------------------
# STEP 3: RETRIEVE RELEVANT POLICIES
# -------------------------------------------

def retrieve_policies(
    question,
    top_k=3,
    min_similarity=0.08
):

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a valid question.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    # Load policy database
    policies = load_policies()

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    # Convert policy documents into vectors
    policy_vectors = vectorizer.fit_transform(
        policies["search_text"]
    )

    # Convert customer's question into a vector
    question_vector = vectorizer.transform(
        [question]
    )

    # Calculate similarity
    scores = cosine_similarity(
        question_vector,
        policy_vectors
    ).flatten()

    # Store scores
    policies["similarity_score"] = scores

    # Filter weak matches
    results = policies[
        policies["similarity_score"] >= min_similarity
    ].copy()

    # Rank from highest similarity to lowest
    results = results.sort_values(
        by="similarity_score",
        ascending=False
    )

    return results.head(top_k)

# -------------------------------------------
# STEP 6: GENERATE ANSWERS USING AN LLM
# -------------------------------------------

def generate_grounded_answer(question, top_k=3):

    # Check whether the API key exists
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is missing. "
            "Please check your .env file."
        )

    # Retrieve relevant policy documents
    matches = retrieve_policies(
        question,
        top_k=top_k
    )

    # If no policy is retrieved, do not call the LLM
    if matches.empty:

        return {
            "answer": (
                "I could not find sufficient information "
                "in the store policy documents to answer "
                "your question. Please contact store staff."
            ),
            "sources": []
        }

    # Prepare evidence for the AI model
    evidence = []
    sources = []

    for _, row in matches.iterrows():

        evidence.append(
            f"""
            Policy ID: {row['policy_id']}
            Title: {row['title']}
            Source: {row['source']}
            Policy Text: {row['text']}
            """
        )

        sources.append({
            "policy_id": row["policy_id"],
            "title": row["title"],
            "source": row["source"],
            "similarity": round(
                float(row["similarity_score"]), 3
            )
        })

    evidence_text = "\n\n".join(evidence)

    # Connect to OpenAI
    client = OpenAI()

    # Give the model instructions
    instructions = """
    You are SmartMart's AI Store Policy Assistant.

    Your job is to answer customer questions
    about supermarket policies.

    Follow these rules strictly:

    1. Answer using ONLY the policy evidence
       provided in the input.

    2. Do not invent store rules, refund periods,
       discounts or return conditions.

    3. If the retrieved policies do not directly
       answer the question, clearly say that the
       available policy documents do not provide
       enough information.

    4. Do not use your general knowledge to
       fill gaps in store policies.

    5. Clearly explain relevant conditions
       and exceptions mentioned in the policies.

    6. Use simple, friendly language.

    7. Do not claim that a customer qualifies
       for a refund or return unless the evidence
       supports that conclusion.

    8. Do not pretend that a policy says something
       that it does not say.

    9. Do not invent policy IDs or sources.

    Your goal is to provide accurate,
    evidence-based customer assistance.
    """

    # Generate the answer
    response = client.responses.create(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-6-luna"
        ),
        instructions=instructions,
        input=f"""
        CUSTOMER QUESTION:

        {question}

        RETRIEVED STORE POLICY EVIDENCE:

        {evidence_text}

        Answer the customer's question using
        the policy evidence above.
        """
    )

    answer = response.output_text

    if not answer:
        raise RuntimeError(
            "The AI model returned an empty answer."
        )

    return {
        "answer": answer.strip(),
        "sources": sources
    }


    matches = retrieve_policies(question)

    # Handle questions not covered by our policies
    if matches.empty:

        return {
            "answer": (
                "I could not find a relevant policy in the "
                "available store documents. Please contact "
                "store staff for clarification."
            ),
            "source": "No relevant policy found",
            "retrieved": matches
        }

    # Select the strongest matching policy
    best_match = matches.iloc[0]

    answer = (
        "According to the store policy, "
        + best_match["text"]
    )

    return {
        "answer": answer,
        "source": (
            best_match["source"]
            + " (" + best_match["policy_id"] + ")"
        ),
        "retrieved": matches
    }


# -------------------------------------------
# STEP 5: TEST POLICY ASSISTANT
# -------------------------------------------


# -------------------------------------------
# STEP 7: TEST THE COMPLETE RAG SYSTEM
# -------------------------------------------

if __name__ == "__main__":

    print("\nSMARTMART AI POLICY ASSISTANT")
    print("-----------------------------")

    question = input(
        "\nEnter your policy question: "
    ).strip()

    if not question:
        print("Please enter a question.")

    else:

        try:

            result = generate_grounded_answer(question)

            print("\nAI GENERATED ANSWER")
            print("-------------------")

            print(result["answer"])

            print("\nRETRIEVED POLICY REFERENCES")
            print("---------------------------")

            if result["sources"]:

                for source in result["sources"]:

                    print(
                        f"\nPolicy ID: {source['policy_id']}"
                    )

                    print(
                        f"Title: {source['title']}"
                    )

                    print(
                        f"Source: {source['source']}"
                    )

                    print(
                        f"Similarity: {source['similarity']}"
                    )

            else:

                print("No relevant policy retrieved.")

        except Exception as error:

            print("\nERROR")
            print("-------------------")
            print(error)
