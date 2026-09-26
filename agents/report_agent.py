from datetime import datetime


def run_report_agent(
    sql_result: dict,
    risk_result: dict,
    forecast_result: dict,
    insight_result: str,
) -> str:

    if not insight_result or not insight_result.strip():
        raise ValueError(
            "No Insight Agent results available for report generation."
        )

    sql_rows = sql_result.get("rows", [])
    columns = sql_result.get("columns", [])

    if not sql_rows:
        raise ValueError(
            "No SQL results available for report generation."
        )

    sql_values = dict(
        zip(columns, sql_rows[0])
    )

    required_sql_fields = [
        "transaction_count",
        "total_amount_received",
        "total_amount_paid",
        "average_transaction_amount",
        "laundering_transaction_count",
    ]

    for field in required_sql_fields:
        if field not in sql_values:
            raise ValueError(
                f"Missing SQL field: {field}"
            )

    required_risk_fields = [
        "amount_threshold",
        "high_value_transactions",
        "high_value_laundering",
        "high_value_laundering_rate",
        "high_frequency_accounts",
        "transactions_from_high_frequency_accounts",
    ]

    for field in required_risk_fields:
        if field not in risk_result:
            raise ValueError(
                f"Missing risk field: {field}"
            )

    required_forecast_fields = [
        "selected_model",
        "alpha",
        "backtest_test_observations",
        "backtest_mae",
        "candidate_models",
        "baseline_method",
        "baseline_mae",
        "improvement_vs_baseline",
        "naive_baseline_method",
        "naive_baseline_mae",
        "improvement_vs_naive",
        "forecast_next_day_transactions",
        "historical_days",
    ]

    for field in required_forecast_fields:
        if field not in forecast_result:
            raise ValueError(
                f"Missing forecast field: {field}"
            )

    # ---------------------------------------------------------
    # SQL Results
    # ---------------------------------------------------------

    total_transactions = sql_values[
        "transaction_count"
    ]

    total_amount_received = sql_values[
        "total_amount_received"
    ]

    total_amount_paid = sql_values[
        "total_amount_paid"
    ]

    average_transaction_amount = sql_values[
        "average_transaction_amount"
    ]

    laundering_transaction_count = sql_values[
        "laundering_transaction_count"
    ]

    # ---------------------------------------------------------
    # Risk Results
    # ---------------------------------------------------------

    amount_threshold = risk_result[
        "amount_threshold"
    ]

    high_value_transactions = risk_result[
        "high_value_transactions"
    ]

    high_value_laundering = risk_result[
        "high_value_laundering"
    ]

    high_value_laundering_rate = risk_result[
        "high_value_laundering_rate"
    ]

    high_frequency_accounts = risk_result[
        "high_frequency_accounts"
    ]

    high_frequency_transactions = risk_result[
        "transactions_from_high_frequency_accounts"
    ]

    # ---------------------------------------------------------
    # Forecast Results
    # ---------------------------------------------------------

    selected_model = forecast_result[
        "selected_model"
    ]

    forecast_alpha = forecast_result[
        "alpha"
    ]

    test_observations = forecast_result[
        "backtest_test_observations"
    ]

    forecast_mae = forecast_result[
        "backtest_mae"
    ]

    candidate_models = forecast_result[
        "candidate_models"
    ]

    baseline_method = forecast_result[
        "baseline_method"
    ]

    baseline_mae = forecast_result[
        "baseline_mae"
    ]

    improvement_vs_baseline = forecast_result[
        "improvement_vs_baseline"
    ]

    naive_baseline_method = forecast_result[
        "naive_baseline_method"
    ]

    naive_baseline_mae = forecast_result[
        "naive_baseline_mae"
    ]

    improvement_vs_naive = forecast_result[
        "improvement_vs_naive"
    ]

    forecast_value = forecast_result[
        "forecast_next_day_transactions"
    ]

    historical_days = forecast_result[
        "historical_days"
    ]

    # ---------------------------------------------------------
    # Candidate Model Results
    # ---------------------------------------------------------

    candidate_models_text = "\n".join(
        (
            f"- {model['model']}: "
            f"MAE = {model['mae']}"
            + (
                f", Alpha = {model['alpha']}"
                if model["alpha"] is not None
                else ""
            )
        )
        for model in candidate_models
    )

    # ---------------------------------------------------------
    # Historical Data
    # ---------------------------------------------------------

    historical_text = "\n".join(
        f"- {date}: {count}"
        for date, count in historical_days
    )

    # ---------------------------------------------------------
    # Forecast Interpretation
    # ---------------------------------------------------------

    if selected_model == "Naive Last-Value Forecast":
        forecast_interpretation = (
            "The selected model is the Naive Last-Value Forecast, "
            "which uses the most recent observed transaction volume "
            "as the next-day estimate."
        )

    elif selected_model == "7-Day Moving Average":
        forecast_interpretation = (
            "The selected model is the 7-Day Moving Average, "
            "which estimates the next-day transaction volume "
            "using the average of the most recent seven observations."
        )

    else:
        forecast_interpretation = (
            "The selected model is Simple Exponential Smoothing, "
            "with the alpha parameter selected through backtesting."
        )

    # ---------------------------------------------------------
    # Alpha Information
    # ---------------------------------------------------------

    if forecast_alpha is None:
        alpha_text = "Not applicable"
    else:
        alpha_text = str(forecast_alpha)

    # ---------------------------------------------------------
    # Generated Timestamp
    # ---------------------------------------------------------

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ---------------------------------------------------------
    # Final Report
    # ---------------------------------------------------------

    report = f"""
# AI CFO Financial Intelligence Report

Generated: {generated_at}

## Executive Summary

This report consolidates verified financial performance,
risk indicators, transaction-volume forecasting results,
and AI-generated analytical insights from the financial
transaction dataset.

Risk findings are analytical signals that may require
additional investigation. They should not be interpreted
as proof of fraud or financial crime.

The forecast is a statistical estimate based on historical
transaction observations and should not be treated as a
guaranteed future value.

## Financial Performance

- Total Transactions: {total_transactions}
- Total Amount Received: {total_amount_received}
- Total Amount Paid: {total_amount_paid}
- Average Transaction Amount: {average_transaction_amount}
- Laundering-Tagged Transactions: {laundering_transaction_count}

## Risk & Anomaly Analysis

- High-Value Transaction Threshold: {amount_threshold}
- High-Value Transactions: {high_value_transactions}
- High-Value Laundering Transactions: {high_value_laundering}
- High-Value Laundering Rate (among high-value transactions): {high_value_laundering_rate}%
- High-Frequency Accounts: {high_frequency_accounts}
- Transactions From High-Frequency Accounts: {high_frequency_transactions}

High-value transactions and high-frequency accounts are
analytical risk signals. They are not proof of fraud or
financial crime.

The reported high-value laundering rate is calculated
within the high-value transaction group by the Risk Agent.

The high-value laundering transactions are a subset of the
high-value transaction group.

## Forecast

- Selected Forecasting Model: {selected_model}
- Selected Alpha: {alpha_text}
- Test Observations: {test_observations}
- Forecast Next-Day Transactions: {forecast_value}

{forecast_interpretation}

### Candidate Model Comparison

{candidate_models_text}

### Forecast Validation

- Selected Model MAE: {forecast_mae}
- Primary Baseline Method: {baseline_method}
- Primary Baseline MAE: {baseline_mae}
- Improvement vs Primary Baseline: {improvement_vs_baseline}%
- Naive Reference Method: {naive_baseline_method}
- Naive Reference MAE: {naive_baseline_mae}
- Improvement vs Naive Reference: {improvement_vs_naive}%

The forecasting models are evaluated using walk-forward
backtesting over the available historical observations.

Model selection is based on the lowest backtest MAE among
the evaluated candidate forecasting methods.

The 7-day moving average and Naive Last-Value Forecast are
included as reference methods to provide simple forecasting
benchmarks.

Backtest results describe historical test performance and
do not guarantee future forecasting accuracy.

### Historical Daily Observations

{historical_text}

## AI-Generated Insights

The following section was generated by the Insight Agent
from verified SQL, Risk, and Forecast Agent outputs.

{insight_result}

## Management Actions

1. Review high-value transactions above the configured
   risk threshold.

2. Monitor high-frequency accounts for unusual activity.

3. Review laundering-tagged transactions as part of
   further investigation.

4. Consider recent transaction-volume patterns when using
   the forecast for operational planning.

5. Re-evaluate forecasting performance when additional
   historical data becomes available.

6. Review the selected forecasting model periodically as
   additional historical observations become available.

## Data & Methodology

- SQL-based financial performance analysis
- Rule-based risk and anomaly analysis
- Candidate forecasting model evaluation
- Simple Exponential Smoothing
- 7-day Moving Average
- Naive Last-Value Forecast
- Walk-forward backtesting
- MAE-based model selection
- Insight Agent analysis
- Deterministic report generation
- Synthetic AML transaction dataset
- Numerical values are inserted directly from verified
  agent outputs
- The Report Agent does not generate or calculate
  numerical values
""".strip()

    return report