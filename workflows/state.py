from typing import TypedDict, Any


class CFOState(TypedDict, total=False):
    user_question: str

    sql_result: dict[str, Any]
    risk_result: dict[str, Any]
    forecast_result: dict[str, Any]

    insight: str
    report: str

    next_agent: str
    error: str