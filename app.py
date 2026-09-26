import pandas as pd
import streamlit as st

from workflows.graph import graph


st.set_page_config(
    page_title="AI CFO",
    page_icon="AI",
    layout="wide",
)


st.title("AI CFO")
st.caption("Financial Intelligence & Risk System")

st.divider()


question = st.text_area(
    "Ask your financial question",
    placeholder=(
        "Analyze our financial performance, "
        "identify unusual transactions, and "
        "forecast tomorrow transaction volume."
    ),
    height=120,
)


run_analysis = st.button(
    "Run Financial Analysis",
    type="primary",
    use_container_width=True,
)


if run_analysis:

    if not question.strip():
        st.warning("Please enter a financial question.")
        st.stop()

    initial_state = {
        "user_question": question,
        "sql_result": {},
        "risk_result": {},
        "forecast_result": {},
        "insight": "",
        "report": "",
    }

    try:

        with st.spinner(
            "AI CFO is analyzing the financial data..."
        ):
            result = graph.invoke(initial_state)

    except Exception as e:

        st.error(
            "The financial analysis could not be completed."
        )

        with st.expander("Technical Details"):
            st.exception(e)

        st.stop()

    st.success("Analysis completed successfully.")

    st.divider()

    # =========================================================
    # Agent Execution
    # =========================================================

    st.subheader("Agent Execution")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "SQL Agent",
            "Completed" if result.get("sql_result") else "Not Run",
        )

    with col2:
        st.metric(
            "Risk Agent",
            "Completed" if result.get("risk_result") else "Not Run",
        )

    with col3:
        st.metric(
            "Forecast Agent",
            "Completed"
            if result.get("forecast_result")
            else "Not Run",
        )

    with col4:
        st.metric(
            "Insight Agent",
            "Completed" if result.get("insight") else "Not Run",
        )

    with col5:
        st.metric(
            "Report Agent",
            "Completed" if result.get("report") else "Not Run",
        )

    st.divider()

    sql_result = result.get("sql_result", {})
    risk_result = result.get("risk_result", {})
    forecast_result = result.get("forecast_result", {})

    # =========================================================
    # Financial Performance
    # =========================================================

    st.subheader("Financial Performance")

    sql_rows = sql_result.get("rows", [])
    sql_columns = sql_result.get("columns", [])

    if sql_rows:

        sql_values = dict(
            zip(sql_columns, sql_rows[0])
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Transactions",
                f"{sql_values.get('transaction_count', 0):,}",
            )

        with col2:
            st.metric(
                "Amount Received",
                f"{sql_values.get('total_amount_received', 0):,.2f}",
            )

        with col3:
            st.metric(
                "Amount Paid",
                f"{sql_values.get('total_amount_paid', 0):,.2f}",
            )

        with col4:
            st.metric(
                "Laundering Tagged",
                f"{sql_values.get('laundering_transaction_count', 0):,}",
            )

    else:

        st.info(
            "No financial performance data was returned."
        )

    st.divider()

    # =========================================================
    # Risk & Anomaly Analysis
    # =========================================================

    st.subheader("Risk & Anomaly Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "High-Value Transactions",
            f"{risk_result.get('high_value_transactions', 0):,}",
        )

    with col2:
        st.metric(
            "High-Value Laundering",
            f"{risk_result.get('high_value_laundering', 0):,}",
        )

    with col3:
        st.metric(
            "High-Value Laundering Rate",
            f"{risk_result.get('high_value_laundering_rate', 0)}%",
        )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "High-Frequency Accounts",
            f"{risk_result.get('high_frequency_accounts', 0):,}",
        )

    with col2:
        st.metric(
            "Transactions From High-Frequency Accounts",
            f"{risk_result.get('transactions_from_high_frequency_accounts', 0):,}",
        )

    st.divider()

    # =========================================================
    # Transaction Forecast
    # =========================================================

    st.subheader("Transaction Forecast")

    forecast_method = forecast_result.get(
        "method",
        "N/A",
    )

    forecast_alpha = forecast_result.get(
        "alpha",
        "N/A",
    )

    model_mae = forecast_result.get(
        "backtest_mae",
        0,
    )

    baseline_method = forecast_result.get(
        "baseline_method",
        "N/A",
    )

    baseline_mae = forecast_result.get(
        "baseline_mae",
        0,
    )

    improvement = forecast_result.get(
        "improvement_percentage",
        0,
    )

    next_day_forecast = forecast_result.get(
        "forecast_next_day_transactions",
        0,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Method",
            forecast_method,
        )

    with col2:
        st.metric(
            "Alpha",
            forecast_alpha,
        )

    with col3:
        st.metric(
            "Next-Day Forecast",
            f"{next_day_forecast:,.2f}",
        )

    with col4:
        st.metric(
            "MAE Improvement",
            f"{improvement:.2f}%",
        )

    st.markdown("#### Forecast Validation")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Model Backtest MAE",
            f"{model_mae:,.2f}",
        )

    with col2:
        st.metric(
            f"{baseline_method} MAE",
            f"{baseline_mae:,.2f}",
        )

    if baseline_mae:

        st.success(
            f"The selected forecasting model reduced "
            f"backtest MAE by {improvement:.2f}% "
            f"compared with the {baseline_method} baseline."
        )

    st.caption(
        "Validation is based on walk-forward backtesting "
        "over the available historical observations. "
        "Improved historical error does not guarantee "
        "future forecasting accuracy."
    )

    # =========================================================
    # Transaction Volume Trend
    # =========================================================

    st.subheader("Transaction Volume Trend")

    historical_days = forecast_result.get(
        "historical_days",
        [],
    )

    if historical_days:

        chart_data = pd.DataFrame(
            historical_days,
            columns=[
                "Date",
                "Transactions",
            ],
        )

        chart_data["Date"] = pd.to_datetime(
            chart_data["Date"]
        )

        chart_data["Date"] = chart_data["Date"].dt.strftime(
            "%b %d"
        )

        chart_data["Forecast"] = pd.NA

        if next_day_forecast is not None:

            last_date = pd.to_datetime(
                historical_days[-1][0]
            )

            forecast_date = (
                last_date
                + pd.Timedelta(days=1)
            ).strftime("%b %d")

            forecast_row = pd.DataFrame(
                [
                    {
                        "Date": forecast_date,
                        "Transactions": pd.NA,
                        "Forecast": next_day_forecast,
                    }
                ]
            )

            chart_data = pd.concat(
                [
                    chart_data,
                    forecast_row,
                ],
                ignore_index=True,
            )

        chart_data = chart_data.set_index(
            "Date"
        )

        chart_data["Transactions"] = pd.to_numeric(
            chart_data["Transactions"],
            errors="coerce",
        )

        chart_data["Forecast"] = pd.to_numeric(
            chart_data["Forecast"],
            errors="coerce",
        )

        st.line_chart(
            chart_data,
            use_container_width=True,
        )

        st.caption(
            "Historical transaction volume and the "
            "next-day forecast generated by the "
            "Forecast Agent."
        )

    else:

        st.info(
            "No historical transaction data available."
        )

    st.divider()

    # =========================================================
    # AI Insight
    # =========================================================

    st.subheader("AI Insight")

    insight = result.get(
        "insight",
        "",
    )

    if insight:

        st.markdown(insight)

    else:

        st.info(
            "No insight was generated."
        )

    st.divider()

    # =========================================================
    # Financial Intelligence Report
    # =========================================================

    st.subheader(
        "Financial Intelligence Report"
    )

    report = result.get(
        "report",
        "",
    )

    if report:

        st.markdown(report)

        st.download_button(
            "Download Report",
            data=report,
            file_name="ai_cfo_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    else:

        st.warning(
            "No report was generated."
        )
