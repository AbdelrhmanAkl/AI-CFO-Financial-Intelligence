from typing import Any

from .local_llm import llm


def extract_sql_facts(
    sql_result: dict[str, Any]
) -> dict[str, Any]:

    rows = sql_result.get("rows", [])

    if not rows:
        return {}

    row = rows[0]

    return {
        "transaction_count":
            row[0] if len(row) > 0 else None,

        "total_amount_received":
            row[1] if len(row) > 1 else None,

        "total_amount_paid":
            row[2] if len(row) > 2 else None,

        "average_transaction_amount":
            row[3] if len(row) > 3 else None,

        "laundering_transaction_count":
            row[4] if len(row) > 4 else None,
    }


def extract_risk_facts(
    risk_result: dict[str, Any]
) -> dict[str, Any]:

    if not risk_result:
        return {}

    return {
        "high_value_transactions":
            risk_result.get(
                "high_value_transactions"
            ),

        "high_value_laundering":
            risk_result.get(
                "high_value_laundering"
            ),

        "high_value_laundering_rate":
            risk_result.get(
                "high_value_laundering_rate"
            ),

        "high_frequency_accounts":
            risk_result.get(
                "high_frequency_accounts"
            ),

        "transactions_from_high_frequency_accounts":
            risk_result.get(
                "transactions_from_high_frequency_accounts"
            ),
    }


def extract_forecast_facts(
    forecast_result: dict[str, Any]
) -> dict[str, Any]:

    if not forecast_result:
        return {}

    return {
        "selected_model":
            forecast_result.get(
                "selected_model"
            ),

        "forecast_next_day_transactions":
            forecast_result.get(
                "forecast_next_day_transactions"
            ),

        "backtest_mae":
            forecast_result.get(
                "backtest_mae"
            ),

        "improvement_vs_baseline":
            forecast_result.get(
                "improvement_vs_baseline"
            ),

        "baseline_method":
            forecast_result.get(
                "baseline_method"
            ),

        "historical_days":
            forecast_result.get(
                "historical_days",
                [],
            ),

        "total_days":
            forecast_result.get(
                "total_days"
            ),

        "first_date":
            forecast_result.get(
                "first_date"
            ),

        "last_date":
            forecast_result.get(
                "last_date"
            ),

        "last_day_transactions":
            forecast_result.get(
                "last_day_transactions"
            ),

        "forecast_target":
            forecast_result.get(
                "forecast_target"
            ),

        "forecast_warning":
            forecast_result.get(
                "forecast_warning"
            ),

        "recent_3_day_average":
            forecast_result.get(
                "recent_3_day_average"
            ),

        "recent_7_day_average":
            forecast_result.get(
                "recent_7_day_average"
            ),

        "last_day_change_percentage":
            forecast_result.get(
                "last_day_change_percentage"
            ),

        "data_quality_conditions":
            forecast_result.get(
                "data_quality_conditions",
                [],
            ),

        "data_quality_status":
            forecast_result.get(
                "data_quality_status"
            ),
    }


def contains_numeric_content(
    text: str
) -> bool:

    return any(
        character.isdigit()
        for character in text
    )


def generate_llm_insight(
    sql_facts: dict[str, Any],
    risk_facts: dict[str, Any],
    forecast_facts: dict[str, Any],
) -> str:

    prompt = f"""
You are an analytical assistant inside an AI CFO system.

Generate ONE short business observation.

STRICT RULES:

- Do not output ANY digits.
- Do not output ANY numbers.
- Do not output percentages.
- Do not output dates.
- Do not output account IDs.
- Do not calculate metrics.
- Do not make recommendations.
- Do not claim fraud occurred.
- Do not claim money laundering occurred.
- Risk indicators are analytical signals only.
- Do not claim a forecast model is highly reliable.
- Do not use words such as "significantly improved accuracy".
- Do not invent causal explanations.
- Describe only patterns directly supported by the supplied facts.
- If the forecast history is limited, mention that the forecast has limited historical support.
- If recent transaction volume is lower than the preceding observations, this may be described as a recent decline in activity.
- Do not treat a forecast warning as proof of a future outcome.
- Maximum two sentences.

Financial facts:
{sql_facts}

Risk facts:
{risk_facts}

Forecast facts:
{forecast_facts}

Return only the observation.
"""

    try:

        response = llm.invoke(prompt)

        content = getattr(
            response,
            "content",
            "",
        )

        if isinstance(
            content,
            list,
        ):

            content = " ".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )

        content = str(content).strip()

        if not content:
            return ""

        if contains_numeric_content(
            content
        ):
            return ""

        return content

    except Exception:
        return ""


def extract_historical_values(
    historical_days: list[Any]
) -> list[float]:

    values = []

    for item in historical_days:

        if isinstance(item, dict):

            value = item.get(
                "transactions"
            )

        elif (
            isinstance(item, (tuple, list))
            and len(item) >= 2
        ):

            value = item[1]

        else:

            continue

        if isinstance(
            value,
            (int, float),
        ):

            values.append(
                float(value)
            )

    return values


def build_fallback_insight(
    sql_facts: dict[str, Any],
    risk_facts: dict[str, Any],
    forecast_facts: dict[str, Any],
) -> str:

    sections = []

    # ---------------------------------------------------------
    # Financial activity
    # ---------------------------------------------------------

    if sql_facts:

        received = sql_facts.get(
            "total_amount_received"
        )

        paid = sql_facts.get(
            "total_amount_paid"
        )

        if (
            isinstance(received, (int, float))
            and isinstance(paid, (int, float))
        ):

            if received > paid:

                sections.append(
                    "Transaction activity shows total incoming value above total outgoing value."
                )

            elif received < paid:

                sections.append(
                    "Transaction activity shows total outgoing value above total incoming value."
                )

            else:

                sections.append(
                    "Incoming and outgoing transaction values are broadly balanced."
                )

    # ---------------------------------------------------------
    # Risk signals
    # ---------------------------------------------------------

    if risk_facts:

        high_value = risk_facts.get(
            "high_value_transactions"
        )

        high_frequency = risk_facts.get(
            "high_frequency_accounts"
        )

        if (
            isinstance(
                high_value,
                (int, float),
            )
            and high_value > 0
        ) or (
            isinstance(
                high_frequency,
                (int, float),
            )
            and high_frequency > 0
        ):

            sections.append(
                "The dataset contains high-value and high-frequency activity signals. These indicators require contextual review and do not by themselves establish financial crime."
            )

    # ---------------------------------------------------------
    # Forecast / recent activity
    # ---------------------------------------------------------

    if forecast_facts:

        historical_days = (
            forecast_facts.get(
                "historical_days",
                [],
            )
        )

        values = extract_historical_values(
            historical_days
        )

        if len(values) >= 2:

            previous_value = values[-2]
            latest_value = values[-1]

            if latest_value < previous_value:

                sections.append(
                    "Recent transaction volume is lower than the immediately preceding observation."
                )

            elif latest_value > previous_value:

                sections.append(
                    "Recent transaction volume is higher than the immediately preceding observation."
                )

            else:

                sections.append(
                    "Recent transaction volume is unchanged relative to the immediately preceding observation."
                )

        # -----------------------------------------------------
        # Forecast data quality warning
        # -----------------------------------------------------

        data_quality_status = (
            forecast_facts.get(
                "data_quality_status"
            )
        )

        if data_quality_status == "WARNING":

            sections.append(
                "The forecast has limited historical support and should be interpreted with caution."
            )

    # ---------------------------------------------------------
    # Final fallback
    # ---------------------------------------------------------

    if not sections:

        return (
            "The available agent outputs do not provide enough evidence for a specific analytical observation."
        )

    return " ".join(
        sections[:3]
    )


def run_insight_agent(
    sql_result: dict[str, Any] | None = None,
    risk_result: dict[str, Any] | None = None,
    forecast_result: dict[str, Any] | None = None,
) -> dict[str, Any]:

    sql_result = (
        sql_result
        or {}
    )

    risk_result = (
        risk_result
        or {}
    )

    forecast_result = (
        forecast_result
        or {}
    )

    sql_facts = extract_sql_facts(
        sql_result
    )

    risk_facts = extract_risk_facts(
        risk_result
    )

    forecast_facts = extract_forecast_facts(
        forecast_result
    )

    insight = generate_llm_insight(
        sql_facts,
        risk_facts,
        forecast_facts,
    )

    if not insight:

        insight = build_fallback_insight(
            sql_facts,
            risk_facts,
            forecast_facts,
        )

    return {
        "insight": insight,

        "sql_facts":
            sql_facts,

        "risk_facts":
            risk_facts,

        "forecast_facts":
            forecast_facts,
    }
