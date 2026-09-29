from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from typing_extensions import TypedDict

from agents.sql_agent import run_sql_agent
from agents.risk_agent import run_risk_agent
from agents.forecast_agent import run_forecast_agent
from agents.insight_agent import run_insight_agent
from agents.report_agent import run_report_agent
from agents.report_validator import validate_report


# ============================================================
# STATE
# ============================================================

class CFOState(TypedDict, total=False):
    question: str

    selected_agents: list[str]
    executed_agents: list[str]

    sql_result: dict
    risk_result: dict
    forecast_result: dict

    insight_result: str
    report: str

    validation_result: dict
    final_report: str


# ============================================================
# AGENT ORDER
# ============================================================

AGENT_ORDER = [
    "SQL",
    "RISK",
    "FORECAST",
    "INSIGHT",
    "REPORT",
    "VALIDATOR",
]


NODE_MAPPING = {
    "SQL": "sql_agent",
    "RISK": "risk_agent",
    "FORECAST": "forecast_agent",
    "INSIGHT": "insight_agent",
    "REPORT": "report_agent",
    "VALIDATOR": "validator",
}


# ============================================================
# QUESTION CLASSIFICATION
# ============================================================

def classify_question(question: str) -> list[str]:
    """
    Determine which agents are required for the user's request.

    The supervisor is deterministic:
    - no LLM-based routing
    - predictable execution
    - UI reflects the actual workflow
    - unrelated agents are not executed

    Complete financial analysis:
        SQL
        RISK
        FORECAST
        INSIGHT
        REPORT
        VALIDATOR
    """

    question_lower = question.lower().strip()

    # --------------------------------------------------------
    # PERFORMANCE / SQL
    # --------------------------------------------------------

    sql_keywords = [
        "analyze",
        "analysis",
        "financial analysis",
        "financial performance",
        "performance",
        "financial activity",
        "financial overview",
        "revenue",
        "expenses",
        "amount",
        "total",
        "count",
        "database",
        "sql",
        "metrics",
        "metric",
        "key financial metrics",
        "transactions",
        "transaction volume",
        "transaction activity",
    ]

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk_keywords = [
        "risk",
        "risky",
        "suspicious",
        "unusual",
        "anomaly",
        "anomalies",
        "laundering",
        "money laundering",
        "fraud",
        "financial crime",
    ]

    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    forecast_keywords = [
        "forecast",
        "forecasting",
        "predict",
        "prediction",
        "future",
        "next day",
        "next month",
        "next week",
        "expected",
        "trend prediction",
        "trend forecast",
    ]

    # --------------------------------------------------------
    # INSIGHT
    # --------------------------------------------------------

    insight_keywords = [
        "insight",
        "insights",
        "interpret",
        "interpretation",
        "key insight",
        "key insights",
        "business insight",
        "business insights",
        "recommendation",
        "recommendations",
        "management recommendation",
        "management recommendations",
        "action",
        "actions",
        "what should management do",
        "what should we do",
        "decision",
        "decisions",
    ]

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    report_keywords = [
        "report",
        "management report",
        "executive report",
        "financial report",
        "executive summary",
        "management summary",
        "generate a report",
        "generate report",
        "create a report",
        "create report",
        "management report",
    ]

    # --------------------------------------------------------
    # COMPLETE / EXECUTIVE ANALYSIS
    # --------------------------------------------------------

    comprehensive_keywords = [
        "complete analysis",
        "complete financial analysis",
        "comprehensive analysis",
        "comprehensive financial analysis",
        "full analysis",
        "full financial analysis",
        "complete financial review",
        "comprehensive financial review",
        "overall analysis",
        "overall financial analysis",
        "end-to-end analysis",
        "end to end analysis",
        "complete review",
        "full review",
        "management analysis",
        "executive analysis",
        "financial decision analysis",
    ]

    # --------------------------------------------------------
    # INTENT DETECTION
    # --------------------------------------------------------

    sql_requested = any(
        keyword in question_lower
        for keyword in sql_keywords
    )

    risk_requested = any(
        keyword in question_lower
        for keyword in risk_keywords
    )

    forecast_requested = any(
        keyword in question_lower
        for keyword in forecast_keywords
    )

    insight_requested = any(
        keyword in question_lower
        for keyword in insight_keywords
    )

    report_requested = any(
        keyword in question_lower
        for keyword in report_keywords
    )

    comprehensive_requested = any(
        keyword in question_lower
        for keyword in comprehensive_keywords
    )

    # --------------------------------------------------------
    # SPECIAL CASE:
    # COMPLETE FINANCIAL ANALYSIS
    #
    # This is the main executive workflow.
    # --------------------------------------------------------

    if comprehensive_requested:

        return AGENT_ORDER.copy()

    # --------------------------------------------------------
    # MANAGEMENT RECOMMENDATIONS
    #
    # Recommendations require data + insights.
    # --------------------------------------------------------

    if insight_requested and not (
        sql_requested
        or risk_requested
        or forecast_requested
    ):
        sql_requested = True

    # --------------------------------------------------------
    # BUILD SELECTED AGENTS
    # --------------------------------------------------------

    agents = set()

    # --------------------------------------------------------
    # REPORT REQUEST
    #
    # A management report requires the full intelligence
    # pipeline.
    # --------------------------------------------------------

    if report_requested:

        agents.update(
            {
                "SQL",
                "RISK",
                "FORECAST",
                "INSIGHT",
                "REPORT",
                "VALIDATOR",
            }
        )

    else:

        # ----------------------------------------------------
        # PERFORMANCE
        # ----------------------------------------------------

        if sql_requested:
            agents.add("SQL")

        # ----------------------------------------------------
        # RISK
        #
        # Risk depends on SQL/database information.
        # ----------------------------------------------------

        if risk_requested:

            agents.add("SQL")
            agents.add("RISK")

        # ----------------------------------------------------
        # FORECAST
        #
        # Forecast depends on historical transaction data.
        # ----------------------------------------------------

        if forecast_requested:

            agents.add("SQL")
            agents.add("FORECAST")

        # ----------------------------------------------------
        # INSIGHT
        # ----------------------------------------------------

        if insight_requested:

            agents.add("SQL")
            agents.add("INSIGHT")

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    if not agents:
        agents.add("SQL")

    # --------------------------------------------------------
    # DETERMINISTIC ORDER
    # --------------------------------------------------------

    return [
        agent
        for agent in AGENT_ORDER
        if agent in agents
    ]


# ============================================================
# NEXT NODE
# ============================================================

def get_next_node(
    selected_agents: list[str],
    current_agent: str,
) -> str:

    try:
        current_index = AGENT_ORDER.index(
            current_agent
        )

    except ValueError:
        return "final"

    for agent in AGENT_ORDER[current_index + 1:]:

        if agent in selected_agents:
            return NODE_MAPPING[agent]

    return "final"


# ============================================================
# SUPERVISOR NODE
# ============================================================

def supervisor_node(
    state: CFOState,
) -> Command[
    Literal[
        "sql_agent",
        "risk_agent",
        "forecast_agent",
        "insight_agent",
        "report_agent",
        "validator",
        "final",
    ]
]:

    selected_agents = classify_question(
        state["question"]
    )

    if not selected_agents:
        selected_agents = ["SQL"]

    first_agent = selected_agents[0]

    next_node = NODE_MAPPING.get(
        first_agent,
        "final",
    )

    return Command(
        update={
            "selected_agents": selected_agents,
            "executed_agents": [],
        },
        goto=next_node,
    )


# ============================================================
# SQL AGENT NODE
# ============================================================

def sql_agent_node(
    state: CFOState,
) -> Command[
    Literal[
        "risk_agent",
        "forecast_agent",
        "insight_agent",
        "report_agent",
        "validator",
        "final",
    ]
]:

    result = run_sql_agent(
        state["question"]
    )

    executed_agents = [
        *state.get("executed_agents", []),
        "SQL",
    ]

    next_node = get_next_node(
        selected_agents=state["selected_agents"],
        current_agent="SQL",
    )

    return Command(
        update={
            "sql_result": result,
            "executed_agents": executed_agents,
        },
        goto=next_node,
    )


# ============================================================
# RISK AGENT NODE
# ============================================================

def risk_agent_node(
    state: CFOState,
) -> Command[
    Literal[
        "forecast_agent",
        "insight_agent",
        "report_agent",
        "validator",
        "final",
    ]
]:

    result = run_risk_agent()

    executed_agents = [
        *state.get("executed_agents", []),
        "RISK",
    ]

    next_node = get_next_node(
        selected_agents=state["selected_agents"],
        current_agent="RISK",
    )

    return Command(
        update={
            "risk_result": result,
            "executed_agents": executed_agents,
        },
        goto=next_node,
    )


# ============================================================
# FORECAST AGENT NODE
# ============================================================

def forecast_agent_node(
    state: CFOState,
) -> Command[
    Literal[
        "insight_agent",
        "report_agent",
        "validator",
        "final",
    ]
]:

    result = run_forecast_agent()

    executed_agents = [
        *state.get("executed_agents", []),
        "FORECAST",
    ]

    next_node = get_next_node(
        selected_agents=state["selected_agents"],
        current_agent="FORECAST",
    )

    return Command(
        update={
            "forecast_result": result,
            "executed_agents": executed_agents,
        },
        goto=next_node,
    )


# ============================================================
# INSIGHT AGENT NODE
# ============================================================

def insight_agent_node(
    state: CFOState,
) -> Command[
    Literal[
        "report_agent",
        "validator",
        "final",
    ]
]:

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

    executed_agents = [
        *state.get("executed_agents", []),
        "INSIGHT",
    ]

    next_node = get_next_node(
        selected_agents=state["selected_agents"],
        current_agent="INSIGHT",
    )

    return Command(
        update={
            "insight_result": result,
            "executed_agents": executed_agents,
        },
        goto=next_node,
    )


# ============================================================
# REPORT AGENT NODE
# ============================================================

def report_agent_node(
    state: CFOState,
) -> Command[
    Literal[
        "validator",
        "final",
    ]
]:

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

    executed_agents = [
        *state.get("executed_agents", []),
        "REPORT",
    ]

    next_node = get_next_node(
        selected_agents=state["selected_agents"],
        current_agent="REPORT",
    )

    return Command(
        update={
            "report": report,
            "executed_agents": executed_agents,
        },
        goto=next_node,
    )


# ============================================================
# VALIDATOR NODE
# ============================================================

def validator_node(
    state: CFOState,
) -> Command[
    Literal["final"]
]:

    report = state.get(
        "report",
        "",
    )

    if not report:
        raise ValueError(
            "Validator received an empty report."
        )

    validation_result = validate_report(
        report=report,
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

    if not validation_result.get(
        "valid",
        False,
    ):
        raise ValueError(
            "Report validation failed: "
            f"{validation_result}"
        )

    executed_agents = [
        *state.get("executed_agents", []),
        "VALIDATOR",
    ]

    return Command(
        update={
            "validation_result": validation_result,
            "final_report": report,
            "executed_agents": executed_agents,
        },
        goto="final",
    )


# ============================================================
# FINAL NODE
# ============================================================

def final_node(
    state: CFOState,
) -> CFOState:

    # For workflows that generate a final report,
    # make sure final_report is available.
    if state.get("report") and not state.get("final_report"):
        state["final_report"] = state["report"]

    return state


# ============================================================
# GRAPH
# ============================================================

def build_cfo_graph():

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


# ============================================================
# COMPILED GRAPH
# ============================================================

cfo_graph = build_cfo_graph()


# ============================================================
# PUBLIC API
# ============================================================

def run_cfo(
    question: str,
) -> dict:

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    return cfo_graph.invoke(
        {
            "question": question.strip(),
        }
    )


def run_supervisor(
    question: str,
) -> str:

    selected_agents = classify_question(
        question
    )

    return ",".join(
        selected_agents
    )