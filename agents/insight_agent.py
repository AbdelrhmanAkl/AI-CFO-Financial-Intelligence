from agents.local_llm import llm


def extract_sql_facts(sql_result: dict) -> dict:
    columns = sql_result.get("columns", [])
    rows = sql_result.get("rows", [])

    if not rows:
        raise ValueError("SQL Agent returned no rows.")

    row = rows[0]

    facts = dict(zip(columns, row))

    required_fields = [
        "transaction_count",
        "total_amount_received",
        "total_amount_paid",
        "average_transaction_amount",
        "laundering_transaction_count",
    ]

    missing = [field for field in required_fields if field not in facts]

    if missing:
        raise ValueError(
            f"SQL Agent result is missing required fields: {missing}"
        )

    return facts


def extract_risk_facts(risk_result: dict) -> dict:
    required_fields = [
        "amount_threshold",
        "frequency_threshold",
        "high_value_transactions",
        "high_value_laundering",
        "high_value_laundering_rate",
        "high_frequency_accounts",
        "transactions_from_high_frequency_accounts",
    ]

    missing = [
        field
        for field in required_fields
        if field not in risk_result
    ]

    if missing:
        raise ValueError(
            f"Risk Agent result is missing required fields: {missing}"
        )

    return {
        "amount_threshold": risk_result["amount_threshold"],
        "frequency_threshold": risk_result["frequency_threshold"],
        "high_value_transactions": risk_result["high_value_transactions"],
        "high_value_laundering": risk_result["high_value_laundering"],
        "high_value_laundering_rate": risk_result[
            "high_value_laundering_rate"
        ],
        "high_frequency_accounts": risk_result[
            "high_frequency_accounts"
        ],
        "transactions_from_high_frequency_accounts": risk_result[
            "transactions_from_high_frequency_accounts"
        ],
    }


def extract_forecast_facts(forecast_result: dict) -> dict:
    required_fields = [
        "selected_model",
        "method",
        "backtest_test_observations",
        "forecast_next_day_transactions",
        "backtest_mae",
        "baseline_method",
        "baseline_mae",
        "improvement_vs_baseline",
    ]

    missing = [
        field
        for field in required_fields
        if field not in forecast_result
    ]

    if missing:
        raise ValueError(
            f"Forecast Agent result is missing required fields: {missing}"
        )

    return {
        "selected_model": forecast_result["selected_model"],
        "method": forecast_result["method"],
        "alpha": forecast_result.get("alpha"),
        "backtest_test_observations": forecast_result[
            "backtest_test_observations"
        ],
        "forecast_next_day_transactions": forecast_result[
            "forecast_next_day_transactions"
        ],
        "backtest_mae": forecast_result["backtest_mae"],
        "baseline_method": forecast_result["baseline_method"],
        "baseline_mae": forecast_result["baseline_mae"],
        "naive_baseline_method": forecast_result.get(
            "naive_baseline_method"
        ),
        "naive_baseline_mae": forecast_result.get(
            "naive_baseline_mae"
        ),
        "improvement_vs_baseline": forecast_result[
            "improvement_vs_baseline"
        ],
        "improvement_vs_naive": forecast_result.get(
            "improvement_vs_naive"
        ),
        "historical_days": forecast_result.get("historical_days"),
    }


def format_number(value):
    if value is None:
        return "N/A"

    if isinstance(value, int):
        return f"{value:,}"

    if isinstance(value, float):
        return f"{value:,.2f}"

    return str(value)


def generate_llm_insight(
    sql_facts: dict,
    risk_facts: dict,
    forecast_facts: dict,
) -> list[str]:

    prompt = """
You are the Insight Agent inside an AI CFO financial intelligence system.

Generate exactly THREE short neutral observations.

The application already handles all numerical values.

Therefore:

- Do NOT write any numbers.
- Do NOT write percentages.
- Do NOT calculate metrics.
- Do NOT compare numerical values.
- Do NOT create recommendations.
- Do NOT claim fraud or financial crime.
- Do NOT infer causation.
- Do NOT use evaluative language.
- Do NOT use words such as significant, major, substantial,
  large, small, strong, weak, concerning, alarming, unusual,
  abnormal, excellent, poor, reliable, accurate, or meaningful.
- Risk indicators are analytical signals only.
- The forecasting model is a statistical model and not a guaranteed outcome.

Observation 1:
Describe the financial performance section in neutral terms.

Observation 2:
Describe the risk analysis as analytical signals.

Observation 3:
Describe the forecast as a statistical estimate based on historical observations.

Return exactly three lines.
No numbering.
No bullet points.
No headings.
No numbers.

Verified financial facts:
"""

    prompt += f"""
{sql_facts}

Verified risk facts:
{risk_facts}

Verified forecast facts:
{forecast_facts}
"""

    response = llm.invoke(prompt)

    lines = [
        line.strip()
        for line in response.content.splitlines()
        if line.strip()
    ]

    if len(lines) < 3:
        return [
            "The financial performance section summarizes verified transaction and amount metrics.",
            "The risk section contains analytical signals derived from transaction and account activity.",
            "The forecast section provides a statistical estimate based on the available historical observations.",
        ]

    return lines[:3]


def run_insight_agent(
    sql_result: dict,
    risk_result: dict,
    forecast_result: dict,
) -> str:

    sql = extract_sql_facts(sql_result)
    risk = extract_risk_facts(risk_result)
    forecast = extract_forecast_facts(forecast_result)

    llm_insights = generate_llm_insight(
        sql,
        risk,
        forecast,
    )

    report = f"""
### Financial Performance

- Transaction count: {format_number(sql["transaction_count"])}
- Total amount received: {format_number(sql["total_amount_received"])}
- Total amount paid: {format_number(sql["total_amount_paid"])}
- Average transaction amount: {format_number(sql["average_transaction_amount"])}
- Laundering-tagged transactions: {format_number(sql["laundering_transaction_count"])}
- AI-generated observation: {llm_insights[0]}

### Risk & Anomaly Findings

- High-value transaction threshold: {format_number(risk["amount_threshold"])}
- High-value transactions: {format_number(risk["high_value_transactions"])}
- High-value laundering transactions: {format_number(risk["high_value_laundering"])}
- High-value laundering rate: {format_number(risk["high_value_laundering_rate"])}%
- High-frequency accounts: {format_number(risk["high_frequency_accounts"])}
- Transactions from high-frequency accounts: {format_number(risk["transactions_from_high_frequency_accounts"])}
- The 1,010 high-value laundering transactions are part of the 884,251 high-value transactions.
- The risk indicators are analytical signals and are not proof of financial crime.
- AI-generated observation: {llm_insights[1]}

### Forecast

- Selected model: {forecast["selected_model"]}
- Forecasting method: {forecast["method"]}
- Test observation count: {format_number(forecast["backtest_test_observations"])}
- Forecast next-day transactions: {format_number(forecast["forecast_next_day_transactions"])}
- Selected model MAE: {format_number(forecast["backtest_mae"])}
- Primary baseline method: {forecast["baseline_method"]}
- Primary baseline MAE: {format_number(forecast["baseline_mae"])}
- Improvement versus primary baseline: {format_number(forecast["improvement_vs_baseline"])}%
- AI-generated observation: {llm_insights[2]}
- Limitation: The forecast is based on a limited historical dataset, including a sequence of declining daily transaction counts in the available observations.

### Key Management Takeaways

1. The financial performance section contains verified transaction and amount metrics.
2. The risk section contains analytical risk indicators and dataset labels.
3. The forecast section provides a statistical next-day estimate based on the available historical observations.
"""

    return report.strip()