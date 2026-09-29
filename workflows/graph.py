from langgraph.graph import StateGraph, START, END

from workflows.state import CFOState

from agents.supervisor import run_supervisor
from agents.sql_agent import run_sql_agent
from agents.risk_agent import run_risk_agent
from agents.forecast_agent import run_forecast_agent
from agents.insight_agent import run_insight_agent
from agents.report_agent import run_report_agent


# ============================================================
# HELPERS
# ============================================================

def parse_agents(next_agent: str) -> list[str]:
    """
    Convert the supervisor output into a clean list of agents.

    Example:
        "SQL,RISK,FORECAST"
        ->
        ["SQL", "RISK", "FORECAST"]
    """

    if not next_agent:
        return []

    return [
        agent.strip().upper()
        for agent in next_agent.split(",")
        if agent.strip()
    ]


# ============================================================
# SUPERVISOR NODE
# ============================================================

def supervisor_node(state: CFOState):

    next_agent = run_supervisor(
        state["user_question"]
    )

    return {
        "next_agent": next_agent
    }


# ============================================================
# SQL NODE
# ============================================================

def sql_node(state: CFOState):

    result = run_sql_agent(
        state["user_question"]
    )

    return {
        "sql_result": result
    }


# ============================================================
# RISK NODE
# ============================================================

def risk_node(state: CFOState):

    result = run_risk_agent()

    return {
        "risk_result": result
    }


# ============================================================
# FORECAST NODE
# ============================================================

def forecast_node(state: CFOState):

    result = run_forecast_agent()

    return {
        "forecast_result": result
    }


# ============================================================
# INSIGHT NODE
# ============================================================

def insight_node(state: CFOState):

    result = run_insight_agent(
        sql_result=state.get(
            "sql_result",
            {}
        ),
        risk_result=state.get(
            "risk_result",
            {}
        ),
        forecast_result=state.get(
            "forecast_result",
            {}
        ),
    )

    return {
        "insight": result
    }


# ============================================================
# REPORT NODE
# ============================================================

def report_node(state: CFOState):

    result = run_report_agent(
        sql_result=state.get(
            "sql_result",
            {}
        ),
        risk_result=state.get(
            "risk_result",
            {}
        ),
        forecast_result=state.get(
            "forecast_result",
            {}
        ),
    )

    return {
        "report": result
    }


# ============================================================
# SUPERVISOR ROUTING
# ============================================================

def route_from_supervisor(state: CFOState):

    agents = parse_agents(
        state.get(
            "next_agent",
            ""
        )
    )

    # SQL has the highest priority because
    # Risk and Forecast depend on financial data.
    if "SQL" in agents:
        return "sql"

    if "RISK" in agents:
        return "risk"

    if "FORECAST" in agents:
        return "forecast"

    return "sql"


# ============================================================
# SQL ROUTING
# ============================================================

def route_after_sql(state: CFOState):

    agents = parse_agents(
        state.get(
            "next_agent",
            ""
        )
    )

    # Risk comes after SQL.
    if "RISK" in agents:
        return "risk"

    # Forecast can run after SQL.
    if "FORECAST" in agents:
        return "forecast"

    # If Insight or Report was requested directly,
    # the available financial data is not enough for
    # the complete downstream workflow unless Forecast
    # is also requested.
    return "end"


# ============================================================
# RISK ROUTING
# ============================================================

def route_after_risk(state: CFOState):

    agents = parse_agents(
        state.get(
            "next_agent",
            ""
        )
    )

    # Complete reports require Forecast after Risk.
    if "FORECAST" in agents:
        return "forecast"

    # If the supervisor selected REPORT, the complete
    # workflow must continue through Forecast.
    if "REPORT" in agents:
        return "forecast"

    # If INSIGHT was selected together with Risk,
    # Forecast is required because Insight expects it.
    if "INSIGHT" in agents:
        return "forecast"

    return "end"


# ============================================================
# FORECAST ROUTING
# ============================================================

def route_after_forecast(state: CFOState):

    # Forecast feeds the Insight Agent.
    return "insight"


# ============================================================
# INSIGHT ROUTING
# ============================================================

def route_after_insight(state: CFOState):

    # Insight feeds the Report Agent.
    return "report"


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(CFOState)


# ============================================================
# NODES
# ============================================================

builder.add_node(
    "supervisor",
    supervisor_node
)

builder.add_node(
    "sql",
    sql_node
)

builder.add_node(
    "risk",
    risk_node
)

builder.add_node(
    "forecast",
    forecast_node
)

builder.add_node(
    "insight",
    insight_node
)

builder.add_node(
    "report",
    report_node
)


# ============================================================
# ENTRY
# ============================================================

builder.add_edge(
    START,
    "supervisor"
)


# ============================================================
# SUPERVISOR → FIRST AGENT
# ============================================================

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "sql": "sql",
        "risk": "risk",
        "forecast": "forecast",
    },
)


# ============================================================
# SQL ROUTING
# ============================================================

builder.add_conditional_edges(
    "sql",
    route_after_sql,
    {
        "risk": "risk",
        "forecast": "forecast",
        "end": END,
    },
)


# ============================================================
# RISK ROUTING
# ============================================================

builder.add_conditional_edges(
    "risk",
    route_after_risk,
    {
        "forecast": "forecast",
        "end": END,
    },
)


# ============================================================
# FORECAST → INSIGHT
# ============================================================

builder.add_edge(
    "forecast",
    "insight"
)


# ============================================================
# INSIGHT → REPORT
# ============================================================

builder.add_edge(
    "insight",
    "report"
)


# ============================================================
# REPORT → END
# ============================================================

builder.add_edge(
    "report",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile()


# ============================================================
# PUBLIC API
# ============================================================

def run_cfo(question: str) -> dict:
    """
    Run the complete AI CFO LangGraph workflow.

    Parameters
    ----------
    question : str
        User's financial analysis request.

    Returns
    -------
    dict
        Final LangGraph state.
    """

    if not question or not question.strip():
        raise ValueError(
            "AI CFO question cannot be empty."
        )

    return graph.invoke(
        {
            "user_question": question.strip()
        }
    )