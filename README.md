
# 🛒 SmartMart AI – AI-Based Smart Retail Store Assistant

SmartMart AI is an intelligent retail assistant developed as a university AI/ML project.

It combines product discovery, content-based recommendations, graph-based store navigation, Retrieval-Augmented Generation (RAG), multi-agent workflows and budget-aware shopping.

## Features

### 1. Product Discovery
- Product search and filtering
- Category and budget filtering
- Inventory availability checks

### 2. AI Product Recommendations
- TF-IDF text vectorisation
- Cosine similarity
- Content-based product ranking

### 3. Store Navigation
- Graph-based store representation
- Dijkstra's shortest-path algorithm
- Multi-product route planning

### 4. Store Policy Assistant
- Retrieval-Augmented Generation
- TF-IDF policy retrieval
- Generative AI responses grounded in store documents
- Policy source references

### 5. Multi-Agent System
- Customer Agent
- Store Assistant Agent
- Tool selection and coordination
- Integration of existing AI modules

### 6. AI Paradigm Evaluation
- Rule-based AI
- TF-IDF recommendation
- RAG retrieval
- Tool-using agent workflow
- Evaluation metrics and visualisations

### 7. Customer Account System
- Customer registration and login
- Salted password hashing
- SQLite customer profiles
- Saved shopping lists and activity history

### 8. Shopping Cart
- Add, update and remove products
- Total basket calculation
- Budget optimisation using dynamic programming
- Shopping route calculation

## Technology Stack

- Python
- Streamlit
- Pandas
- Scikit-learn
- NetworkX
- Plotly
- SQLite
- OpenAI API

## Project Structure

```text
smart-retail-assistant/
├── app.py
├── requirements.txt
├── data/
├── modules/
├── evaluation/
├── .streamlit/
├── .gitignore
└── README.md
```

## Run Locally

1. Clone this repository.

2. Create a virtual environment:

```bash
python3 -m venv .venv
```

3. Activate the environment:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=your_configured_model
```

6. Start the application:

```bash
streamlit run app.py
```

## Data and Privacy

SmartMart uses simulated supermarket products, prices, inventory,
customer profiles, store locations and policy documents.

Do not enter real customer information into the demonstration application.

API credentials and local database files should not be committed
to the public repository.

## Project Purpose

This project demonstrates the use of different AI paradigms
in a simulated retail environment, combining traditional
algorithms, information retrieval, generative AI and
tool-using agent workflows.
