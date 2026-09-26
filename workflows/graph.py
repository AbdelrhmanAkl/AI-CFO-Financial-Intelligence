from langgraph.graph import StateGraph, START, END

from workflows.state import CFOState

from agents.supervisor import run_supervisor
from agents.sql_agent import run_sql_agent
from agents.risk_agent import run_risk_agent
from agents.forecast_agent import run_forecast_agent
from agents.insight_agent import run_insight_agent
from agents.report_agent import run_report_agent


def supervisor_node(state: CFOState):
    next_agent = run_supervisor(
        state["user_question"]
    )

    return {
        "next_agent": next_agent
    }


def sql_node(state: CFOState):
    result = run_sql_agent(
        state["user_question"]
    )

    return {
        "sql_result": result
    }


def risk_node(state: CFOState):
    result = run_risk_agent()

    return {
        "risk_result": result
    }


def forecast_node(state: CFOState):
    result = run_forecast_agent()

    return {
        "forecast_result": result
    }


def insight_node(state: CFOState):
    result = run_insight_agent(
        sql_result=state["sql_result"],
        risk_result=state["risk_result"],
        forecast_result=state["forecast_result"],
    )

    return {
        "insight": result
    }


def report_node(state: CFOState):
    result = run_report_agent(
        sql_result=state["sql_result"],
        risk_result=state["risk_result"],
        forecast_result=state["forecast_result"],
    )

    return {
        "report": result
    }


def route_from_supervisor(state: CFOState):
    agents = state["next_agent"].split(",")

    if "SQL" in agents:
        return "sql"

    if "RISK" in agents:
        return "risk"

    if "FORECAST" in agents:
        return "forecast"

    return "sql"


def route_after_sql(state: CFOState):
    agents = state["next_agent"].split(",")

    if "RISK" in agents:
        return "risk"

    if "FORECAST" in agents:
        return "forecast"

    return "end"


def route_after_risk(state: CFOState):
    agents = state["next_agent"].split(",")

    if "FORECAST" in agents:
        return "forecast"

    return "end"


def route_after_forecast(state: CFOState):
    return "insight"


def route_after_insight(state: CFOState):
    return "report"


builder = StateGraph(CFOState)

# ---------------------------------------------------------
# Nodes
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Entry
# ---------------------------------------------------------

builder.add_edge(
    START,
    "supervisor"
)

# ---------------------------------------------------------
# Supervisor routing
# ---------------------------------------------------------

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "sql": "sql",
        "risk": "risk",
        "forecast": "forecast",
    },
)

# ---------------------------------------------------------
# SQL routing
# ---------------------------------------------------------

builder.add_conditional_edges(
    "sql",
    route_after_sql,
    {
        "risk": "risk",
        "forecast": "forecast",
        "end": END,
    },
)

# ---------------------------------------------------------
# Risk routing
# ---------------------------------------------------------

builder.add_conditional_edges(
    "risk",
    route_after_risk,
    {
        "forecast": "forecast",
        "end": END,
    },
)

# ---------------------------------------------------------
# Forecast → Insight
# ---------------------------------------------------------

builder.add_edge(
    "forecast",
    "insight"
)

# ---------------------------------------------------------
# Insight → Report
# ---------------------------------------------------------

builder.add_conditional_edges(
    "insight",
    route_after_insight,
    {
        "report": "report"
    },
)

# ---------------------------------------------------------
# Report → END
# ---------------------------------------------------------

builder.add_edge(
    "report",
    END
)

# ---------------------------------------------------------
# Compile
# ---------------------------------------------------------

graph = builder.compile()