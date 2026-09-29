from datetime import datetime
from typing import Any


def format_number(value: Any, decimals: int = 2) -> str:
    if value is None:
        return "N/A"

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, (int, float)):
        if decimals == 0:
            return f"{value:,.0f}"
        return f"{value:,.{decimals}f}"

    return str(value)


def format_percentage(value: Any, decimals: int = 2) -> str:
    if value is None:
        return "N/A"

    if isinstance(value, (int, float)):
        return f"{value:,.{decimals}f}%"

    return str(value)


def build_sql_section(sql_result: dict[str, Any]) -> str:
    rows = sql_result.get("rows", [])

    if not rows:
        return ""

    row = rows[0]

    transaction_count = row[0] if len(row) > 0 else None
    total_received = row[1] if len(row) > 1 else None
    total_paid = row[2] if len(row) > 2 else None
    average_transaction = row[3] if len(row) > 3 else None
    laundering_count = row[4] if len(row) > 4 else None

    return f"""## Financial Performance

- Transaction count: {format_number(transaction_count, 0)}
- Total amount received: {format_number(total_received)}
- Total amount paid: {format_number(total_paid)}
- Average transaction amount: {format_number(average_transaction)}
- Laundering-tagged transactions: {format_number(laundering_count, 0)}
"""


def build_risk_section(risk_result: dict[str, Any]) -> str:
    if not risk_result:
        return ""

    amount_threshold = risk_result.get("amount_threshold")
    frequency_threshold = risk_result.get("frequency_threshold")
    high_value_transactions = risk_result.get("high_value_transactions")
    high_value_laundering = risk_result.get("high_value_laundering")
    high_value_laundering_rate = risk_result.get(
        "high_value_laundering_rate"
    )
    high_frequency_accounts = risk_result.get("high_frequency_accounts")
    transactions_from_high_frequency_accounts = risk_result.get(
        "transactions_from_high_frequency_accounts"
    )

    return f"""## Risk & Anomaly Analysis

- High-value transaction threshold: {format_number(amount_threshold)}
- Frequency threshold: {format_number(frequency_threshold, 0)}
- High-value transactions: {format_number(high_value_transactions, 0)}
- High-value laundering transactions: {format_number(high_value_laundering, 0)}
- High-value laundering rate: {format_percentage(high_value_laundering_rate)}
- High-frequency accounts: {format_number(high_frequency_accounts, 0)}
- Transactions from high-frequency accounts: {format_number(transactions_from_high_frequency_accounts, 0)}

The risk indicators are analytical signals and are not proof of financial crime.
"""


def build_top_accounts_rows(
    risk_result: dict[str, Any],
) -> str:
    accounts = risk_result.get(
        "top_high_frequency_accounts",
        [],
    )

    if not accounts:
        return ""

    lines = [
        "### Top High-Frequency Accounts",
        "",
        "| Account | Transactions | Frequency Threshold | Laundering Rate |",
        "|---|---:|---:|---:|",
    ]

    for account in accounts:
        if not isinstance(account, (tuple, list)):
            continue

        if len(account) < 4:
            continue

        account_id = account[0]
        transactions = account[1]
        frequency_threshold = account[2]
        laundering_rate = account[3]

        lines.append(
            f"| {account_id} | "
            f"{format_number(transactions, 0)} | "
            f"{format_number(frequency_threshold, 0)} | "
            f"{format_percentage(laundering_rate)} |"
        )

    return "\n".join(lines)


def get_candidate_model_name(candidate: Any) -> str:
    if isinstance(candidate, dict):
        return str(
            candidate.get(
                "model",
                candidate.get(
                    "name",
                    candidate.get(
                        "method",
                        "Unknown",
                    ),
                ),
            )
        )

    if isinstance(candidate, (tuple, list)) and candidate:
        return str(candidate[0])

    return str(candidate)


def get_candidate_value(
    candidate: Any,
    keys: tuple[str, ...],
    index: int | None = None,
) -> Any:
    if isinstance(candidate, dict):
        for key in keys:
            if key in candidate:
                return candidate[key]

    if (
        index is not None
        and isinstance(candidate, (tuple, list))
        and len(candidate) > index
    ):
        return candidate[index]

    return None


def build_candidate_model_rows(
    forecast_result: dict[str, Any],
) -> str:
    candidates = forecast_result.get(
        "candidate_models",
        [],
    )

    if not candidates:
        return ""

    lines = [
        "### Candidate Model Comparison",
        "",
        "| Model | MAE | Alpha |",
        "|---|---:|---:|",
    ]

    for candidate in candidates:
        name = get_candidate_model_name(candidate)

        mae = get_candidate_value(
            candidate,
            ("mae", "MAE"),
            index=1,
        )

        alpha = get_candidate_value(
            candidate,
            ("alpha",),
            index=2,
        )

        alpha_text = (
            format_number(alpha, 2)
            if alpha is not None
            else "N/A"
        )

        lines.append(
            f"| {name} | {format_number(mae)} | {alpha_text} |"
        )

    return "\n".join(lines)


def build_forecast_section(
    forecast_result: dict[str, Any],
) -> str:
    if not forecast_result:
        return ""

    selected_model = forecast_result.get("selected_model")

    if not selected_model:
        selected_model = forecast_result.get("method")

    forecast_next_day = forecast_result.get(
        "forecast_next_day_transactions"
    )

    selected_mae = forecast_result.get(
        "backtest_mae"
    )

    baseline_method = forecast_result.get(
        "baseline_method"
    )

    baseline_mae = forecast_result.get(
        "baseline_mae"
    )

    improvement_vs_baseline = forecast_result.get(
        "improvement_vs_baseline"
    )

    naive_baseline_method = forecast_result.get(
        "naive_baseline_method"
    )

    naive_baseline_mae = forecast_result.get(
        "naive_baseline_mae"
    )

    improvement_vs_naive = forecast_result.get(
        "improvement_vs_naive"
    )

    test_observations = forecast_result.get(
        "backtest_test_observations"
    )

    lines = [
        "## Forecast",
        "",
        f"- Selected model: {selected_model or 'N/A'}",
        f"- Backtesting observations: {format_number(test_observations, 0)}",
        f"- Forecast Next-Day Transactions: {format_number(forecast_next_day, 0)}",
        f"- Selected model backtest MAE: {format_number(selected_mae)}",
        f"- Primary baseline method: {baseline_method or 'N/A'}",
        f"- Primary baseline MAE: {format_number(baseline_mae)}",
        f"- Improvement versus primary baseline: "
        f"{format_percentage(improvement_vs_baseline)}",
        f"- Naive baseline method: {naive_baseline_method or 'N/A'}",
        f"- Naive baseline MAE: {format_number(naive_baseline_mae)}",
        f"- Improvement versus naive baseline: "
        f"{format_percentage(improvement_vs_naive)}",
        "",
        "The next-day value is a forecast of transaction count based on "
        "the latest available historical observations.",
        "The backtesting observation count is separate from the forecasted "
        "transaction count.",
        "The forecast is a statistical estimate and should not be treated "
        "as a guaranteed future value.",
        "",
    ]

    return "\n".join(lines)


def build_historical_section(
    forecast_result: dict[str, Any],
) -> str:
    historical_days = forecast_result.get(
        "historical_days",
        [],
    )

    if not historical_days:
        return ""

    lines = [
        "### Historical Daily Observations",
        "",
        "| Date | Transactions |",
        "|---|---:|",
    ]

    for item in historical_days:

        # Current Forecast Agent format:
        # ("2022/09/01", 1114921)
        if isinstance(item, (tuple, list)):
            if len(item) < 2:
                continue

            date = item[0]
            transactions = item[1]

        # Future-compatible dictionary format
        elif isinstance(item, dict):
            date = item.get("date")
            transactions = item.get("transactions")

        else:
            continue

        if date is None or transactions is None:
            continue

        lines.append(
            f"| {date} | {format_number(transactions, 0)} |"
        )

    return "\n".join(lines)


def build_insight_section(
    insight_result: dict[str, Any] | str | None,
) -> str:
    if not insight_result:
        return ""

    if isinstance(insight_result, dict):
        insight = insight_result.get(
            "insight",
            "",
        )
    else:
        insight = str(insight_result)

    insight = str(insight).strip()

    if not insight:
        return ""

    return f"""## AI-Generated Insights

{insight}

The generated observation is grounded in the available agent outputs and is not a substitute for financial or compliance review.
"""


def build_management_actions(
    sql_result: dict[str, Any],
    risk_result: dict[str, Any],
    forecast_result: dict[str, Any],
) -> str:
    actions = []

    if risk_result:
        actions.append(
            "- Review high-value and high-frequency activity using the available analytical risk indicators."
        )
        actions.append(
            "- Prioritize high-frequency accounts for contextual review rather than treating the indicators as proof of financial crime."
        )

    if forecast_result:
        actions.append(
            "- Monitor actual transaction volume against the forecast over subsequent observations."
        )
        if forecast_result.get("data_quality_status") == "WARNING":
            actions.append(
                "- Extend the historical transaction series before relying on the forecast for operational planning."
            )

    if sql_result:
        actions.append(
            "- Continue monitoring the core financial performance metrics over time."
        )

    if not actions:
        return ""

    return (
        "## Management Actions\n\n"
        + "\n".join(actions)
    )


def build_methodology_section() -> str:
    return """## Data & Methodology

- Financial performance metrics were calculated from the SQL Agent database query.
- Risk indicators were calculated from transaction amount and account-frequency patterns.
- Risk indicators are analytical signals and do not establish fraud or financial crime.
- Forecasting compares candidate statistical models using historical transaction observations.
- Forecast accuracy is evaluated using Mean Absolute Error (MAE) on the available backtesting window.
- The backtesting observation count is separate from the next-day transaction-count forecast.
- Forecast results should not be interpreted as guaranteed future outcomes.
"""


def run_report_agent(
    sql_result: dict[str, Any],
    risk_result: dict[str, Any],
    forecast_result: dict[str, Any],
    insight_result: dict[str, Any] | str | None = None,
) -> str:

    sections = []

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    sections.append(
        f"""# AI CFO Financial Intelligence Report

Generated: {generated_at}
"""
    )

    summary_lines = [
        "## Executive Summary",
        "",
    ]

    if sql_result:
        summary_lines.append(
            "- Financial performance metrics are available from the SQL Agent."
        )

    if risk_result:
        summary_lines.append(
            "- Risk and anomaly indicators are available from the Risk Agent."
        )

    if forecast_result:
        forecast_value = forecast_result.get(
            "forecast_next_day_transactions"
        )

        selected_model = forecast_result.get(
            "selected_model",
            forecast_result.get("method"),
        )

        if forecast_value is not None:
            summary_lines.append(
                f"- The Forecast Agent selected "
                f"'{selected_model or 'N/A'}' and produced a "
                f"next-day transaction-count forecast of "
                f"{format_number(forecast_value)}."
            )
        else:
            summary_lines.append(
                "- Transaction-volume forecasting is available from the Forecast Agent."
            )

    sections.append(
        "\n".join(summary_lines)
    )

    if sql_result:
        sections.append(
            build_sql_section(sql_result)
        )

    if risk_result:
        sections.append(
            build_risk_section(risk_result)
        )

        top_accounts = build_top_accounts_rows(
            risk_result
        )

        if top_accounts:
            sections.append(
                top_accounts
            )

    if forecast_result:
        sections.append(
            build_forecast_section(
                forecast_result
            )
        )

        candidate_models = build_candidate_model_rows(
            forecast_result
        )

        if candidate_models:
            sections.append(
                candidate_models
            )

        sections.append(
            """### Forecast Validation

The selected model was evaluated using a historical backtesting window. Mean Absolute Error (MAE) is the average absolute difference between predicted and observed transaction counts in that evaluation window. The number of backtesting observations is separate from the next-day transaction-count forecast.
"""
        )

        historical = build_historical_section(
            forecast_result
        )

        if historical:
            sections.append(
                historical
            )

    if insight_result:
        sections.append(
            build_insight_section(
                insight_result
            )
        )

    management_actions = build_management_actions(
        sql_result,
        risk_result,
        forecast_result,
    )

    if management_actions:
        sections.append(
            management_actions
        )

    sections.append(
        build_methodology_section()
    )

    sections.append(
        """---

**AI CFO** — Financial Decision Intelligence System  
Multi-Agent Analytics • Risk Intelligence • Forecasting
"""
    )

    return "\n\n".join(
        section.strip()
        for section in sections
        if section and section.strip()
    )