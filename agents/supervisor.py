from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from typing_extensions import TypedDict

from agents.local_llm import llm
from agents.sql_agent import run_sql_agent
from agents.risk_agent import run_risk_agent
from agents.forecast_agent import run_forecast_agent
from agents.insight_agent import run_insight_agent
from agents.report_agent import run_report_agent
from agents.report_validator import validate_report


class CFOState(TypedDict, total=False):
    question: str

    selected_agents: list[str]

    sql_result: dict
    risk_result: dict
    forecast_result: dict

    insight_result: str
    report: str

    validation_result: dict
    final_report: str


def classify_question(question: str) -> list[str]:
    """
    Determine which analytical agents are relevant
    to the user's question.
    """

    prompt = f"""
You are the supervisor of a financial intelligence multi-agent system.

Available agents:

SQL:
- database queries
- financial performance statistics
- totals
- counts
- transaction analysis

RISK:
- anomaly detection
- suspicious transactions
- risk analysis
- laundering analysis

FORECAST:
- forecasting
- prediction
- future transaction volume
- trend prediction

Return ONLY a comma-separated list containing zero or more of:

SQL
RISK
FORECAST

Do not return explanations.

User question:
{question}
"""

    response = llm.invoke(prompt)

    agents = {
        agent.strip().upper()
        for agent in response.content.split(",")
    }

    valid_agents = {
        "SQL",
        "RISK",
        "FORECAST",
    }

    agents = agents.intersection(valid_agents)

    question_lower = question.lower()

    sql_keywords = [
        "analyze",
        "analysis",
        "financial performance",
        "performance",
        "transactions",
        "revenue",
        "expenses",
        "amount",
        "total",
        "count",
        "database",
    ]

    risk_keywords = [
        "risk",
        "risky",
        "suspicious",
        "unusual",
        "anomaly",
        "anomalies",
        "laundering",
        "fraud",
    ]

    forecast_keywords = [
        "forecast",
        "predict",
        "prediction",
        "future",
        "next day",
        "next month",
        "expected",
    ]

    if any(
        keyword in question_lower
        for keyword in sql_keywords
    ):
        agents.add("SQL")

    if any(
        keyword in question_lower
        for keyword in risk_keywords
    ):
        agents.add("RISK")

    if any(
        keyword in question_lower
        for keyword in forecast_keywords
    ):
        agents.add("FORECAST")

    if not agents:
        agents.add("SQL")

    return [
        agent
        for agent in [
            "SQL",
            "RISK",
            "FORECAST",
        ]
        if agent in agents
    ]


def supervisor_node(
    state: CFOState,
) -> Command[
    Literal["sql_agent"]
]:
    """
    Determine the user's analytical intent and
    start the complete financial intelligence pipeline.

    The selected agents are stored as metadata.
    The full analytical pipeline is still executed because
    Insight, Report, and Validator require all upstream results.
    """

    selected_agents = classify_question(
        state["question"]
    )

    if not selected_agents:
        selected_agents = ["SQL"]

    return Command(
        update={
            "selected_agents": selected_agents,
        },
        goto="sql_agent",
    )


def sql_agent_node(
    state: CFOState,
) -> Command[
    Literal["risk_agent"]
]:
    """
    Execute the SQL Agent.

    SQL is always the first analytical stage because
    the financial report requires verified database results.
    """

    result = run_sql_agent(
        state["question"]
    )

    return Command(
        update={
            "sql_result": result,
        },
        goto="risk_agent",
    )


def risk_agent_node(
    state: CFOState,
) -> Command[
    Literal["forecast_agent"]
]:
    """
    Execute the Risk Agent.
    """

    result = run_risk_agent()

    return Command(
        update={
            "risk_result": result,
        },
        goto="forecast_agent",
    )


def forecast_agent_node(
    state: CFOState,
) -> Command[
    Literal["insight_agent"]
]:
    """
    Execute the Forecast Agent.
    """

    result = run_forecast_agent()

    return Command(
        update={
            "forecast_result": result,
        },
        goto="insight_agent",
    )


def insight_agent_node(
    state: CFOState,
) -> Command[
    Literal["report_agent"]
]:
    """
    Generate AI-assisted analytical insights
    using verified outputs from SQL, Risk, and Forecast agents.
    """

    sql_result = state.get(
        "sql_result",
        {},
    )

    risk_result = state.get(
        "risk_result",
        {},
    )

    forecast_result = state.get(
        "forecast_result",
        {},
    )

    result = run_insight_agent(
        sql_result,
        risk_result,
        forecast_result,
    )

    return Command(
        update={
            "insight_result": result,
        },
        goto="report_agent",
    )


def report_agent_node(
    state: CFOState,
) -> Command[
    Literal["validator"]
]:
    """
    Generate the deterministic financial intelligence report.
    """

    report = run_report_agent(
        sql_result=state.get(
            "sql_result",
            {},
        ),
        risk_result=state.get(
            "risk_result",
            {},
        ),
        forecast_result=state.get(
            "forecast_result",
            {},
        ),
        insight_result=state.get(
            "insight_result",
            "",
        ),
    )

    return Command(
        update={
            "report": report,
        },
        goto="validator",
    )


def validator_node(
    state: CFOState,
) -> Command[
    Literal["final"]
]:
    """
    Validate the generated report before returning it.

    The Validator is the final quality gate.
    """

    validation_result = validate_report(
        report=state["report"],
        sql_result=state.get(
            "sql_result",
            {},
        ),
        risk_result=state.get(
            "risk_result",
            {},
        ),
        forecast_result=state.get(
            "forecast_result",
            {},
        ),
    )

    if not validation_result["valid"]:
        raise ValueError(
            "Report validation failed: "
            f"{validation_result}"
        )

    return Command(
        update={
            "validation_result": validation_result,
            "final_report": state["report"],
        },
        goto="final",
    )


def final_node(
    state: CFOState,
) -> CFOState:
    """
    Return the final validated state.
    """

    return state


def build_cfo_graph():
    """
    Build and compile the complete AI CFO LangGraph.
    """

    graph = StateGraph(CFOState)

    graph.add_node(
        "supervisor",
        supervisor_node,
    )

    graph.add_node(
        "sql_agent",
        sql_agent_node,
    )

    graph.add_node(
        "risk_agent",
        risk_agent_node,
    )

    graph.add_node(
        "forecast_agent",
        forecast_agent_node,
    )

    graph.add_node(
        "insight_agent",
        insight_agent_node,
    )

    graph.add_node(
        "report_agent",
        report_agent_node,
    )

    graph.add_node(
        "validator",
        validator_node,
    )

    graph.add_node(
        "final",
        final_node,
    )

    graph.add_edge(
        START,
        "supervisor",
    )

    graph.add_edge(
        "final",
        END,
    )

    return graph.compile()


cfo_graph = build_cfo_graph()


def run_cfo(
    question: str,
) -> dict:
    """
    Run the complete AI CFO workflow.
    """

    return cfo_graph.invoke(
        {
            "question": question,
        }
    )


def run_supervisor(
    question: str,
) -> str:
    """
    Backward-compatible supervisor interface.

    Returns the agents selected by the Supervisor
    without executing the complete CFO pipeline.
    """

    selected_agents = classify_question(
        question
    )

    return ",".join(
        selected_agents
    )