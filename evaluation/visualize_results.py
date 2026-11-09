
from pathlib import Path
import pandas as pd
import plotly.express as px


# -------------------------------------------
# STEP 1: LOCATE RESULTS
# -------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

SUMMARY_FILE = (
    BASE_DIR / "evaluation" / "evaluation_summary.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "evaluation" / "paradigm_comparison.html"
)


# -------------------------------------------
# STEP 2: LOAD SUMMARY
# -------------------------------------------

summary = pd.read_csv(SUMMARY_FILE)


# -------------------------------------------
# STEP 3: CREATE PERFORMANCE CHART
# -------------------------------------------

fig = px.bar(

    summary,

    x="paradigm",

    y="pass_rate_percent",

    color="task",

    barmode="group",

    title="SmartMart AI Paradigm Performance Comparison",

    labels={
        "paradigm": "AI Paradigm",
        "pass_rate_percent": "Pass Rate (%)",
        "task": "Task"
    },

    text="pass_rate_percent"

)

fig.update_layout(

    xaxis_title="AI Paradigm",

    yaxis_title="Pass Rate (%)",

    yaxis_range=[0, 100],

    legend_title="Task",

    template="plotly_white",

    xaxis_tickangle=-20

)


# -------------------------------------------
# STEP 4: SAVE CHART
# -------------------------------------------

fig.write_html(OUTPUT_FILE)

print("Chart generated successfully!")

print("Saved at:", OUTPUT_FILE)
