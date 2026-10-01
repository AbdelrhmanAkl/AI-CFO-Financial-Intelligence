import html

import pandas as pd
import streamlit as st

from workflows.graph import run_cfo


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI CFO | Financial Management System",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "active_view" not in st.session_state:
    st.session_state.active_view = "Overview"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "analysis_question" not in st.session_state:
    st.session_state.analysis_question = ""

if "last_error" not in st.session_state:
    st.session_state.last_error = None


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.block-container {
    max-width: 1400px;
    padding-top: 1.1rem;
    padding-bottom: 1.2rem;
}

[data-testid="stSidebar"] {
    border-right: 1px solid #e7e9ef;
}

[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #e3e5eb;
    background: #ffffff;
    color: #171a21;
    font-weight: 600;
    min-height: 42px;
}

.stButton > button:hover {
    border-color: #6d5dfc;
    color: #5b4de8;
    background: #faf9ff;
}

.stButton > button[kind="primary"] {
    border-color: #6d5dfc;
}

.cfo-brand {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #171a21;
    margin-bottom: 2px;
}

.cfo-subtitle {
    color: #737783;
    font-size: 12px;
    margin-bottom: 18px;
}

.sidebar-label {
    color: #8b8e98;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    margin: 16px 0 7px 2px;
}

.sidebar-status {
    border: 1px solid #e4e6eb;
    background: #fafafa;
    border-radius: 10px;
    padding: 10px 11px;
    margin-bottom: 12px;
}

.sidebar-status-title {
    font-size: 12px;
    font-weight: 700;
    color: #252832;
}

.sidebar-status-sub {
    font-size: 10px;
    color: #8a8d96;
    margin-top: 2px;
}

.nav-title {
    font-size: 11px;
    font-weight: 800;
    color: #92959e;
    letter-spacing: 0.8px;
    margin: 18px 0 7px 2px;
}

.page-kicker {
    color: #777b86;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 3px;
}

.page-title {
    color: #151821;
    font-size: 28px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
}

.page-description {
    color: #737783;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 16px;
}

.hero {
    background: linear-gradient(135deg, #f5f2ff 0%, #faf9ff 100%);
    border: 1px solid #e6e1ff;
    border-radius: 16px;
    padding: 23px 25px;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 28px;
    font-weight: 800;
    color: #181925;
    margin-bottom: 6px;
}

.hero-description {
    color: #666a76;
    font-size: 13px;
    line-height: 1.55;
    max-width: 850px;
}

.section-title {
    font-size: 16px;
    font-weight: 800;
    color: #20232c;
    margin: 17px 0 7px 0;
}

.section-description {
    color: #777b85;
    font-size: 12px;
    margin-bottom: 10px;
}

.card {
    background: #ffffff;
    border: 1px solid #e6e8ed;
    border-radius: 13px;
    padding: 15px;
    margin-bottom: 10px;
}

.kpi-label {
    color: #858994;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.kpi-value {
    color: #171a21;
    font-size: 21px;
    font-weight: 800;
    line-height: 1.15;
    word-break: break-word;
}

.kpi-sub {
    color: #8a8d96;
    font-size: 10px;
    margin-top: 5px;
}

.action-card {
    border: 1px solid #e5e7ec;
    border-radius: 14px;
    background: #ffffff;
    padding: 14px;
    min-height: 88px;
}

.action-icon {
    font-size: 20px;
    margin-bottom: 5px;
}

.action-title {
    color: #1d2028;
    font-size: 13px;
    font-weight: 800;
}

.action-text {
    color: #858892;
    font-size: 10px;
    margin-top: 2px;
}

.badge {
    display: inline-block;
    border-radius: 14px;
    padding: 4px 8px;
    font-size: 9px;
    font-weight: 800;
    margin-right: 4px;
    margin-bottom: 4px;
}

.badge-green {
    background: #edf9f1;
    color: #21844a;
}

.badge-blue {
    background: #eef5ff;
    color: #2864c7;
}

.badge-orange {
    background: #fff5e9;
    color: #b96812;
}

.badge-purple {
    background: #f3f0ff;
    color: #654dd8;
}

.badge-gray {
    background: #f2f3f5;
    color: #727680;
}

.finding {
    border-left: 3px solid #6d5dfc;
    background: #faf9ff;
    border-radius: 0 9px 9px 0;
    padding: 10px 12px;
    margin-bottom: 7px;
    color: #51545e;
    font-size: 11px;
    line-height: 1.5;
}

.insight-card {
    border: 1px solid #e5e1ff;
    border-left: 4px solid #6d5dfc;
    background: #faf9ff;
    border-radius: 10px;
    padding: 13px 15px;
    color: #4f5260;
    font-size: 12px;
    line-height: 1.6;
    margin-bottom: 9px;
}

.report-box {
    border: 1px solid #e4e6eb;
    background: #ffffff;
    border-radius: 13px;
    padding: 19px;
}

.system-card {
    border: 1px solid #e4e6eb;
    border-radius: 13px;
    background: #ffffff;
    padding: 16px;
    min-height: 108px;
    margin-bottom: 10px;
}

.system-name {
    font-size: 13px;
    font-weight: 800;
    color: #22252d;
    margin-bottom: 5px;
}

.system-text {
    font-size: 10px;
    color: #7d808a;
    line-height: 1.45;
}

.workflow-card {
    border: 1px solid #e4e6eb;
    border-radius: 13px;
    background: #ffffff;
    padding: 14px;
    min-height: 82px;
    margin-bottom: 8px;
}

.workflow-name {
    font-size: 12px;
    font-weight: 800;
    color: #22252d;
    margin-bottom: 7px;
}

.context-question {
    color: #454852;
    font-size: 12px;
    line-height: 1.5;
    background: #faf9ff;
    border: 1px solid #e7e3ff;
    border-radius: 10px;
    padding: 11px 13px;
    margin-bottom: 10px;
}

.empty-card {
    border: 1px dashed #d9dce3;
    border-radius: 13px;
    background: #fcfcfd;
    padding: 28px;
    text-align: center;
    color: #858993;
    font-size: 12px;
    margin-top: 8px;
}

.empty-title {
    color: #40434d;
    font-weight: 800;
    margin-bottom: 4px;
}

.cfo-table-wrapper {
    border: 1px solid #e6e8ed;
    border-radius: 12px;
    overflow-x: auto;
    background: #ffffff;
    margin-bottom: 12px;
}

.cfo-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}

.cfo-table th {
    background: #f7f7fa;
    color: #555965;
    font-weight: 800;
    padding: 9px 11px;
    text-align: left;
    border-bottom: 1px solid #e6e8ed;
    white-space: nowrap;
}

.cfo-table td {
    color: #50535d;
    padding: 9px 11px;
    border-bottom: 1px solid #f0f1f4;
    white-space: nowrap;
}

.cfo-table tr:last-child td {
    border-bottom: none;
}

.footer {
    text-align: center;
    color: #9699a2;
    font-size: 10px;
    padding: 20px 0 4px 0;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def safe_number(value, default=None):
    try:
        if value is None:
            return default

        number = float(value)

        if pd.isna(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def format_number(value, decimals=2):
    number = safe_number(value)

    if number is None:
        return "—"

    if decimals:
        return f"{number:,.{decimals}f}"

    return f"{number:,.0f}"


def compact_number(value):
    number = safe_number(value)

    if number is None:
        return "—"

    absolute = abs(number)

    if absolute >= 1_000_000_000_000:
        return f"{number / 1_000_000_000_000:.2f}T"

    if absolute >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"

    if absolute >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"

    if absolute >= 1_000:
        return f"{number / 1_000:.2f}K"

    return f"{number:,.0f}"


def safe_text(value):
    return html.escape(str(value)) if value is not None else ""


# ============================================================
# RESULT ACCESS
# ============================================================

def result_dict(result, key):
    if not isinstance(result, dict):
        return {}

    value = result.get(key)

    return value if isinstance(value, dict) else {}


def get_sql_result(result):
    return result_dict(result, "sql_result")


def get_risk_result(result):
    return result_dict(result, "risk_result")


def get_forecast_result(result):
    return result_dict(result, "forecast_result")


def get_validation(result):
    if not isinstance(result, dict):
        return {}

    # Current LangGraph state uses "validation".
    value = result.get("validation")

    if isinstance(value, dict):
        return value

    # Backward compatibility.
    value = result.get("validation_result")

    if isinstance(value, dict):
        return value

    if isinstance(value, bool):
        return {"valid": value}

    return {}


def normalize_report(report):
    if report is None:
        return ""

    if isinstance(report, str):
        return report.strip()

    if isinstance(report, dict):
        for key in [
            "report",
            "content",
            "text",
            "message",
            "insight",
        ]:
            value = report.get(key)

            if value:
                return str(value).strip()

    return str(report).strip()


def get_report(result):
    if not isinstance(result, dict):
        return ""

    for key in [
        "report",
        "final_report",
        "management_report",
    ]:
        value = result.get(key)

        if value:
            return normalize_report(value)

    return ""


def get_insight(result):
    if not isinstance(result, dict):
        return ""

    for key in [
        "insight",
        "final_insight",
        "insight_result",
        "business_insight",
        "business_insights",
    ]:
        value = result.get(key)

        if value:
            return normalize_report(value)

    return ""


# ============================================================
# AGENT STATE
# ============================================================

def normalize_agent_name(agent_name):
    if agent_name is None:
        return ""

    name = str(agent_name).strip().upper()

    aliases = {
        "SQL_AGENT": "SQL",
        "SQL": "SQL",

        "RISK_AGENT": "RISK",
        "RISK": "RISK",

        "FORECAST_AGENT": "FORECAST",
        "FORECAST": "FORECAST",

        "INSIGHT_AGENT": "INSIGHT",
        "INSIGHT": "INSIGHT",

        "REPORT_AGENT": "REPORT",
        "REPORT": "REPORT",

        "REPORT_VALIDATOR": "VALIDATOR",
        "REPORT VALIDATOR": "VALIDATOR",
        "VALIDATOR": "VALIDATOR",
    }

    return aliases.get(name, name)


def normalize_agent_list(agents):
    if isinstance(agents, str):
        agents = agents.split(",")

    if not isinstance(agents, list):
        return []

    normalized = []

    for agent in agents:
        name = normalize_agent_name(agent)

        if name and name not in normalized:
            normalized.append(name)

    return normalized


def get_selected_agents(result):
    """
    Read Supervisor routing information.

    The current graph stores the Supervisor output
    in the "next_agent" state field.
    """

    if not isinstance(result, dict):
        return []

    next_agent = result.get("next_agent", "")

    return normalize_agent_list(next_agent)


def get_executed_agents(result):
    """
    Infer executed agents from the current CFOState.

    This keeps the UI compatible with the current graph
    without requiring extra execution-tracking fields.
    """

    if not isinstance(result, dict):
        return []

    executed = []

    if result.get("sql_result"):
        executed.append("SQL")

    if result.get("risk_result"):
        executed.append("RISK")

    if result.get("forecast_result"):
        executed.append("FORECAST")

    if result.get("insight"):
        executed.append("INSIGHT")

    if result.get("report"):
        executed.append("REPORT")

    if result.get("validation"):
        executed.append("VALIDATOR")

    return executed


def agent_executed(result, agent):
    return normalize_agent_name(agent) in get_executed_agents(result)


def agent_selected(result, agent):
    return normalize_agent_name(agent) in get_selected_agents(result)


def agent_state(result, agent):
    agent = normalize_agent_name(agent)

    if agent_executed(result, agent):
        return "Completed"

    if agent_selected(result, agent):
        return "Selected"

    return "Not used"


# ============================================================
# SQL METRICS
# ============================================================

def normalize_column_name(column):
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def find_metric(columns, aliases):
    normalized_columns = {
        normalize_column_name(column): column
        for column in columns
    }

    for alias in aliases:
        normalized_alias = normalize_column_name(alias)

        if normalized_alias in normalized_columns:
            return normalized_columns[normalized_alias]

    return None


def extract_financial_metrics(result):
    sql_result = get_sql_result(result)

    if not sql_result:
        return {}

    columns = sql_result.get("columns", [])
    rows = sql_result.get("rows", [])

    if not isinstance(columns, list) or not columns:
        return {}

    if not isinstance(rows, list) or not rows:
        return {}

    first_row = rows[0]

    if not isinstance(first_row, (list, tuple)):
        return {}

    raw_metrics = dict(zip(columns, first_row))

    aliases = {
        "transactions": [
            "transaction_count",
            "total_transactions",
            "transactions",
        ],
        "received": [
            "total_amount_received",
            "total_received",
            "received_amount",
            "money_received",
        ],
        "paid": [
            "total_amount_paid",
            "total_paid",
            "paid_amount",
            "money_paid",
        ],
        "average": [
            "average_transaction_amount",
            "avg_transaction_amount",
            "average_amount",
            "avg_amount",
        ],
        "laundering": [
            "laundering_transaction_count",
            "laundering_count",
            "total_laundering",
            "laundering_transactions",
            "laundering_tagged",
        ],
    }

    metrics = {}

    for metric_name, metric_aliases in aliases.items():
        key = find_metric(columns, metric_aliases)

        metrics[metric_name] = (
            safe_number(raw_metrics.get(key))
            if key
            else None
        )

    return metrics


# ============================================================
# RISK / FORECAST METRICS
# ============================================================

def extract_risk_metrics(result):
    risk = get_risk_result(result)

    return {
        "threshold": risk.get("amount_threshold"),
        "frequency_threshold": risk.get("frequency_threshold"),
        "high_value": risk.get("high_value_transactions"),
        "high_value_laundering": risk.get(
            "high_value_laundering"
        ),
        "rate": risk.get(
            "high_value_laundering_rate"
        ),
        "high_frequency_accounts": risk.get(
            "high_frequency_accounts"
        ),
        "transactions_from_frequency": risk.get(
            "transactions_from_high_frequency_accounts"
        ),
        "top_accounts": risk.get(
            "top_high_frequency_accounts",
            [],
        ),
    }


def extract_forecast_metrics(result):
    forecast = get_forecast_result(result)

    return {
        "model": forecast.get("selected_model")
        or forecast.get("method"),

        "forecast": forecast.get(
            "forecast_next_day_transactions"
        ),

        "mae": forecast.get(
            "backtest_mae"
        ),

        "observations": forecast.get(
            "backtest_test_observations"
        ),

        "baseline_method": forecast.get(
            "baseline_method"
        ),

        "baseline_mae": forecast.get(
            "baseline_mae"
        ),

        "improvement": forecast.get(
            "improvement_vs_baseline"
        ),

        "recent_3_day_average": forecast.get(
            "recent_3_day_average"
        ),

        "recent_7_day_average": forecast.get(
            "recent_7_day_average"
        ),

        "last_day_change_percentage": forecast.get(
            "last_day_change_percentage"
        ),

        "data_quality_status": forecast.get(
            "data_quality_status"
        ),

        "forecast_warning": forecast.get(
            "forecast_warning"
        ),

        "data_quality_conditions": forecast.get(
            "data_quality_conditions",
            [],
        ),

        "candidate_models": forecast.get(
            "candidate_models",
            [],
        ),

        "historical_days": forecast.get(
            "historical_days",
            [],
        ),
    }


# ============================================================
# RENDER HELPERS
# ============================================================

def render_section(title, description=None):
    st.markdown(
        f'<div class="section-title">{safe_text(title)}</div>',
        unsafe_allow_html=True,
    )

    if description:
        st.markdown(
            f'<div class="section-description">'
            f'{safe_text(description)}'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_kpi(label, value, sub=None):
    sub_html = ""

    if sub:
        sub_html = (
            f'<div class="kpi-sub">'
            f'{safe_text(sub)}'
            f'</div>'
        )

    st.markdown(
        '<div class="card">'
        f'<div class="kpi-label">{safe_text(label)}</div>'
        f'<div class="kpi-value">{safe_text(value)}</div>'
        f'{sub_html}'
        '</div>',
        unsafe_allow_html=True,
    )


def render_empty(title, message):
    st.markdown(
        '<div class="empty-card">'
        f'<div class="empty-title">{safe_text(title)}</div>'
        f'{safe_text(message)}'
        '</div>',
        unsafe_allow_html=True,
    )


def render_dataframe(dataframe):
    if dataframe is None or dataframe.empty:
        return

    display_df = dataframe.copy()

    html_table = display_df.to_html(
        index=False,
        escape=True,
        classes="cfo-table",
        border=0,
    )

    st.markdown(
        f'<div class="cfo-table-wrapper">'
        f'{html_table}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# ANALYSIS CONTEXT
# ============================================================

def render_analysis_context(result):
    if not isinstance(result, dict):
        return

    question = (
        result.get("question")
        or result.get("user_question")
        or ""
    )

    selected = get_selected_agents(result)
    executed = get_executed_agents(result)

    if question:
        st.markdown(
            '<div class="context-question">'
            '<strong>Analysis Query</strong><br>'
            f'{safe_text(question)}'
            '</div>',
            unsafe_allow_html=True,
        )

    if selected:
        render_section(
            "Agent Selection",
            "Agents selected by the Supervisor for this analysis.",
        )

        badges = []

        for agent in selected:
            completed = agent in executed

            badge_class = (
                "badge-green"
                if completed
                else "badge-blue"
            )

            state = (
                "Completed"
                if completed
                else "Selected"
            )

            badges.append(
                f'<span class="badge {badge_class}">'
                f'{safe_text(agent)} · {state}'
                '</span>'
            )

        st.markdown(
            "".join(badges),
            unsafe_allow_html=True,
        )


# ============================================================
# FINANCIAL OVERVIEW
# ============================================================

def render_financial_overview(result):
    metrics = extract_financial_metrics(result)

    if not metrics:
        render_empty(
            "Financial overview unavailable",
            "No structured financial summary was returned by the SQL Agent.",
        )
        return

    render_section(
        "Financial Overview",
        "Core financial activity calculated from the underlying transaction database.",
    )

    cols = st.columns(5)

    with cols[0]:
        render_kpi(
            "Transactions",
            format_number(
                metrics.get("transactions"),
                0,
            ),
        )

    with cols[1]:
        render_kpi(
            "Money Received",
            compact_number(
                metrics.get("received")
            ),
        )

    with cols[2]:
        render_kpi(
            "Money Paid",
            compact_number(
                metrics.get("paid")
            ),
        )

    with cols[3]:
        render_kpi(
            "Average Transaction",
            compact_number(
                metrics.get("average")
            ),
        )

    with cols[4]:
        render_kpi(
            "Laundering Tagged",
            format_number(
                metrics.get("laundering"),
                0,
            ),
        )


# ============================================================
# KEY FINDINGS
# ============================================================

def render_key_findings(result):
    executed = set(
        get_executed_agents(result)
    )

    findings = []

    if "RISK" in executed:
        risk = extract_risk_metrics(result)

        high_value = safe_number(
            risk.get("high_value")
        )

        high_value_laundering = safe_number(
            risk.get("high_value_laundering")
        )

        rate = safe_number(
            risk.get("rate")
        )

        if high_value is not None:
            findings.append(
                f"{format_number(high_value, 0)} "
                "high-value transactions were identified "
                "using the analytical amount threshold."
            )

        if high_value_laundering is not None:
            findings.append(
                f"{format_number(high_value_laundering, 0)} "
                "high-value transactions were "
                "laundering-tagged."
            )

        if rate is not None:
            findings.append(
                "The laundering-tagged rate within the "
                f"high-value group is {rate:.2f}%."
            )

    if "FORECAST" in executed:
        forecast = extract_forecast_metrics(result)

        forecast_value = safe_number(
            forecast.get("forecast")
        )

        if forecast_value is not None:
            findings.append(
                "The selected forecasting method estimates "
                f"{format_number(forecast_value, 0)} "
                "transactions for the next observation."
            )

    if not findings:
        return

    render_section(
        "Key Findings",
        "Important observations extracted from the agents that were executed.",
    )

    for finding in findings:
        st.markdown(
            f'<div class="finding">'
            f'{safe_text(finding)}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# INSIGHTS
# ============================================================

def render_insight(result):
    insight = get_insight(result)

    if not insight:
        return

    render_section(
        "AI Insights",
        "Business observations produced by the Insight Agent.",
    )

    safe_insight = safe_text(
        insight
    ).replace("\n", "<br>")

    st.markdown(
        '<div class="insight-card">'
        f'{safe_insight}'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# RISK VIEW
# ============================================================

def render_risk_summary(result):
    risk = extract_risk_metrics(result)

    values = [
        risk.get(key)
        for key in [
            "threshold",
            "frequency_threshold",
            "high_value",
            "high_value_laundering",
            "rate",
            "high_frequency_accounts",
            "transactions_from_frequency",
        ]
    ]

    if not any(
        value is not None
        for value in values
    ):
        render_empty(
            "Risk analysis unavailable",
            "No risk indicators were returned for this analysis.",
        )
        return

    render_section(
        "Risk & Anomaly Analysis",
        "Analytical indicators derived from transaction amount and account-frequency patterns.",
    )

    cols = st.columns(4)

    with cols[0]:
        render_kpi(
            "High-Value Transactions",
            format_number(
                risk.get("high_value"),
                0,
            ),
        )

    with cols[1]:
        render_kpi(
            "High-Value Laundering",
            format_number(
                risk.get("high_value_laundering"),
                0,
            ),
        )

    with cols[2]:
        rate = safe_number(
            risk.get("rate")
        )

        render_kpi(
            "High-Value Laundering Rate",
            (
                f"{rate:.2f}%"
                if rate is not None
                else "—"
            ),
        )

    with cols[3]:
        render_kpi(
            "High-Frequency Accounts",
            format_number(
                risk.get(
                    "high_frequency_accounts"
                ),
                0,
            ),
        )

    cols2 = st.columns(3)

    with cols2[0]:
        render_kpi(
            "Amount Threshold",
            format_number(
                risk.get("threshold"),
                2,
            ),
        )

    with cols2[1]:
        render_kpi(
            "Frequency Threshold",
            format_number(
                risk.get(
                    "frequency_threshold"
                ),
                0,
            ),
        )

    with cols2[2]:
        render_kpi(
            "Transactions From High-Frequency Accounts",
            format_number(
                risk.get(
                    "transactions_from_frequency"
                ),
                0,
            ),
        )

    st.info(
        "Risk indicators are analytical signals and do not "
        "establish fraud or financial crime."
    )

    top_accounts = risk.get(
        "top_accounts"
    )

    if (
        not isinstance(
            top_accounts,
            list,
        )
        or not top_accounts
    ):
        return

    render_section(
        "Top High-Frequency Accounts",
        "Accounts with the highest transaction activity among the identified high-frequency group.",
    )

    rows = []

    for account in top_accounts:
        if (
            not isinstance(
                account,
                (list, tuple),
            )
            or len(account) < 4
        ):
            continue

        transactions = safe_number(
            account[1]
        )

        laundering = safe_number(
            account[2]
        )

        laundering_rate = safe_number(
            account[3]
        )

        rows.append(
            {
                "Account": str(
                    account[0]
                ),
                "Transactions": (
                    f"{transactions:,.0f}"
                    if transactions is not None
                    else "—"
                ),
                "Laundering Tagged": (
                    f"{laundering:,.0f}"
                    if laundering is not None
                    else "—"
                ),
                "Laundering Rate": (
                    f"{laundering_rate:.2f}%"
                    if laundering_rate is not None
                    else "—"
                ),
            }
        )

    if rows:
        render_dataframe(
            pd.DataFrame(rows)
        )


# ============================================================
# FORECAST VIEW
# ============================================================

def build_historical_dataframe(
    historical_days
):
    rows = []

    if not isinstance(
        historical_days,
        list,
    ):
        return pd.DataFrame()

    for item in historical_days:
        date_value = None
        count_value = None

        if isinstance(item, dict):
            date_value = (
                item.get("date")
                or item.get("day")
                or item.get("timestamp")
            )

            count_value = item.get(
                "transactions"
            )

            if count_value is None:
                count_value = item.get(
                    "transaction_count"
                )

            if count_value is None:
                count_value = item.get(
                    "count"
                )

        elif (
            isinstance(
                item,
                (list, tuple),
            )
            and len(item) >= 2
        ):
            date_value = item[0]
            count_value = item[1]

        numeric_count = safe_number(
            count_value
        )

        if (
            date_value is not None
            and numeric_count is not None
        ):
            parsed_date = pd.to_datetime(
                date_value,
                errors="coerce",
            )

            if pd.notna(parsed_date):
                rows.append(
                    {
                        "Date": parsed_date,
                        "Transactions": numeric_count,
                    }
                )

    if not rows:
        return pd.DataFrame()

    dataframe = pd.DataFrame(rows)

    return (
        dataframe
        .drop_duplicates(
            subset=["Date"]
        )
        .sort_values("Date")
        .reset_index(drop=True)
    )


def render_forecast(result):
    forecast = extract_forecast_metrics(
        result
    )

    values = [
        value
        for key, value in forecast.items()
        if key not in [
            "candidate_models",
            "historical_days",
        ]
    ]

    if not any(
        value is not None
        for value in values
    ):
        render_empty(
            "Forecast unavailable",
            "No forecasting result was returned for this analysis.",
        )
        return

    render_section(
        "Forecast",
        "Transaction-count forecasting based on historical daily observations.",
    )

    cols = st.columns(4)

    with cols[0]:
        render_kpi(
            "Selected Model",
            str(
                forecast.get("model")
                or "—"
            ),
        )

    with cols[1]:
        render_kpi(
            "Next-Day Transactions",
            format_number(
                forecast.get("forecast"),
                0,
            ),
        )

    with cols[2]:
        render_kpi(
            "Backtesting MAE",
            format_number(
                forecast.get("mae"),
                2,
            ),
        )

    with cols[3]:
        render_kpi(
            "Backtesting Observations",
            format_number(
                forecast.get(
                    "observations"
                ),
                0,
            ),
        )

    st.info(
        "The forecast is a statistical estimate based on "
        "historical transaction observations and is not "
        "a guaranteed future value."
    )

    forecast_warning = forecast.get(
        "forecast_warning"
    )

    data_quality_status = forecast.get(
        "data_quality_status"
    )

    if forecast_warning:
        if (
            str(
                data_quality_status
                or ""
            ).upper()
            == "WARNING"
        ):
            st.warning(
                str(forecast_warning)
            )
        else:
            st.caption(
                str(forecast_warning)
            )

    conditions = forecast.get(
        "data_quality_conditions",
        [],
    )

    if (
        isinstance(
            conditions,
            list,
        )
        and conditions
    ):
        render_section(
            "Forecast Data Quality",
            "Conditions reported by the Forecast Agent for the available history.",
        )

        for condition in conditions:
            st.markdown(
                f'<div class="finding">'
                f'{safe_text(condition)}'
                f'</div>',
                unsafe_allow_html=True,
            )

    baseline_method = forecast.get(
        "baseline_method"
    )

    baseline_mae = safe_number(
        forecast.get(
            "baseline_mae"
        )
    )

    improvement = safe_number(
        forecast.get(
            "improvement"
        )
    )

    if (
        baseline_method
        and baseline_mae is not None
    ):
        text = (
            f"Primary baseline: {baseline_method} "
            f"with MAE {baseline_mae:,.2f}"
        )

        if improvement is not None:
            text += (
                f" · MAE difference versus baseline: "
                f"{improvement:.2f}%"
            )

        st.caption(
            text + "."
        )

    recent_3 = safe_number(
        forecast.get(
            "recent_3_day_average"
        )
    )

    recent_7 = safe_number(
        forecast.get(
            "recent_7_day_average"
        )
    )

    last_change = safe_number(
        forecast.get(
            "last_day_change_percentage"
        )
    )

    if any(
        value is not None
        for value in [
            recent_3,
            recent_7,
            last_change,
        ]
    ):
        recent_cols = st.columns(3)

        with recent_cols[0]:
            render_kpi(
                "Recent 3-Day Average",
                format_number(
                    recent_3,
                    2,
                ),
            )

        with recent_cols[1]:
            render_kpi(
                "Recent 7-Day Average",
                format_number(
                    recent_7,
                    2,
                ),
            )

        with recent_cols[2]:
            render_kpi(
                "Last-Day Change",
                (
                    f"{last_change:.2f}%"
                    if last_change is not None
                    else "—"
                ),
            )

    candidate_models = forecast.get(
        "candidate_models"
    )

    if (
        isinstance(
            candidate_models,
            list,
        )
        and candidate_models
    ):
        render_section(
            "Candidate Model Comparison",
            "Models evaluated during the forecasting workflow.",
        )

        rows = []

        for item in candidate_models:
            if not isinstance(
                item,
                dict,
            ):
                continue

            row = {}

            for key, value in item.items():
                clean_key = (
                    str(key)
                    .replace("_", " ")
                    .title()
                )

                numeric_value = safe_number(
                    value
                )

                if numeric_value is not None:
                    if "mae" in str(
                        key
                    ).lower():
                        row[clean_key] = (
                            f"{numeric_value:,.2f}"
                        )

                    elif "alpha" in str(
                        key
                    ).lower():
                        row[clean_key] = (
                            f"{numeric_value:.4f}"
                        )

                    else:
                        row[clean_key] = (
                            f"{numeric_value:,.2f}"
                        )

                elif (
                    value is None
                    or str(value).lower()
                    == "nan"
                ):
                    row[clean_key] = "N/A"

                else:
                    row[clean_key] = value

            rows.append(row)

        if rows:
            render_dataframe(
                pd.DataFrame(rows)
            )

    historical_df = build_historical_dataframe(
        forecast.get(
            "historical_days"
        )
    )

    if not historical_df.empty:
        render_section(
            "Transaction Volume Trend",
            "Daily transaction counts used by the forecasting workflow.",
        )

        st.line_chart(
            historical_df,
            x="Date",
            y="Transactions",
            use_container_width=True,
        )

        render_section(
            "Historical Daily Observations",
            "Exact daily observations returned by the Forecast Agent.",
        )

        display_df = historical_df.copy()

        display_df["Date"] = (
            display_df["Date"]
            .dt.strftime("%Y-%m-%d")
        )

        display_df["Transactions"] = (
            display_df["Transactions"]
            .map(
                lambda x: f"{x:,.0f}"
            )
        )

        render_dataframe(
            display_df
        )


# ============================================================
# WORKFLOW
# ============================================================

def render_process(result):
    executed = get_executed_agents(
        result
    )

    selected = get_selected_agents(
        result
    )

    active_agents = []

    for agent in selected + executed:
        if agent not in active_agents:
            active_agents.append(agent)

    if not active_agents:
        return

    render_section(
        "AI CFO Workflow",
        "Execution status of the financial intelligence components.",
    )

    agents = [
        ("SQL", "SQL Agent"),
        ("RISK", "Risk Agent"),
        ("FORECAST", "Forecast Agent"),
        ("INSIGHT", "Insight Agent"),
        ("REPORT", "Report Agent"),
        ("VALIDATOR", "Report Validator"),
    ]

    visible_agents = [
        item
        for item in agents
        if item[0] in active_agents
    ]

    if not visible_agents:
        return

    cols = st.columns(
        min(
            3,
            len(visible_agents),
        )
    )

    for index, (
        agent_key,
        label,
    ) in enumerate(
        visible_agents
    ):
        state = agent_state(
            result,
            agent_key,
        )

        if state == "Completed":
            badge = "badge-green"

        elif state == "Selected":
            badge = "badge-blue"

        else:
            badge = "badge-gray"

        content = (
            '<div class="workflow-card">'
            f'<div class="workflow-name">'
            f'{safe_text(label)}'
            f'</div>'
            f'<span class="badge {badge}">'
            f'{safe_text(state)}'
            f'</span>'
            '</div>'
        )

        with cols[
            index % len(cols)
        ]:
            st.markdown(
                content,
                unsafe_allow_html=True,
            )


# ============================================================
# VALIDATION
# ============================================================

def render_validation(result):
    validation = get_validation(
        result
    )

    if not validation:
        return

    valid = validation.get(
        "valid"
    )

    if valid is True:
        st.success(
            "Report validation passed."
        )

    elif valid is False:
        st.warning(
            "Report validation returned warnings or errors."
        )

    numerical_integrity = validation.get(
        "numerical_integrity"
    )

    section_integrity = validation.get(
        "section_integrity"
    )

    consistency_integrity = validation.get(
        "consistency_integrity"
    )

    render_section(
        "Report Validation",
        "Automated integrity checks performed against the analytical agent outputs.",
    )

    validation_cols = st.columns(4)

    with validation_cols[0]:
        render_kpi(
            "Overall",
            "PASSED"
            if valid is True
            else "FAILED"
            if valid is False
            else "—",
        )

    with validation_cols[1]:
        render_kpi(
            "Numerical Integrity",
            "PASSED"
            if numerical_integrity is True
            else "FAILED"
            if numerical_integrity is False
            else "—",
        )

    with validation_cols[2]:
        render_kpi(
            "Section Integrity",
            "PASSED"
            if section_integrity is True
            else "FAILED"
            if section_integrity is False
            else "—",
        )

    with validation_cols[3]:
        render_kpi(
            "Consistency",
            "PASSED"
            if consistency_integrity is True
            else "FAILED"
            if consistency_integrity is False
            else "—",
        )

    invalid_numbers = (
        validation.get(
            "invalid_numbers"
        )
        or []
    )

    missing_sections = (
        validation.get(
            "missing_sections"
        )
        or []
    )

    consistency_errors = (
        validation.get(
            "consistency_errors"
        )
        or []
    )

    if invalid_numbers:
        render_section(
            "Invalid Numbers"
        )

        for number in invalid_numbers:
            st.markdown(
                f'<div class="finding">'
                f'{safe_text(number)}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if missing_sections:
        render_section(
            "Missing Sections"
        )

        for section in missing_sections:
            st.markdown(
                f'<div class="finding">'
                f'{safe_text(section)}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if consistency_errors:
        render_section(
            "Consistency Errors"
        )

        for error in consistency_errors:
            st.markdown(
                f'<div class="finding">'
                f'{safe_text(error)}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# REPORT
# ============================================================

def render_report(result):
    report = get_report(
        result
    )

    if not report:
        render_empty(
            "No management report available",
            "Run a complete management-report analysis to generate one.",
        )
        return

    render_section(
        "Management Report",
        "Generated from the available SQL, risk, forecast, and insight outputs.",
    )

    st.markdown(
        '<div class="report-box">',
        unsafe_allow_html=True,
    )

    st.markdown(
        report
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        label="Download Management Report",
        data=report,
        file_name="ai_cfo_management_report.md",
        mime="text/markdown",
        use_container_width=False,
    )


# ============================================================
# QUESTION INPUT
# ============================================================

def render_question_box():
    render_section(
        "Need Something Specific?",
        "Ask a question about the financial data.",
    )

    return st.text_area(
        "Ask a specific question",
        key="analysis_question",
        placeholder=(
            "Example: Give me a complete financial analysis "
            "including performance, risk, forecast, and "
            "management recommendations."
        ),
        height=90,
        label_visibility="visible",
    )


# ============================================================
# ANALYSIS
# ============================================================

def run_analysis(question):
    with st.spinner(
        "Running AI CFO analysis..."
    ):
        return run_cfo(
            question
        )


def reset_analysis():
    st.session_state.analysis_result = None
    st.session_state.analysis_question = ""
    st.session_state.active_view = "Overview"
    st.session_state.last_error = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="cfo-brand">◆ AI CFO</div>'
        '<div class="cfo-subtitle">'
        'Financial Management System'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-label">'
        'SYSTEM STATUS'
        '</div>'
        '<div class="sidebar-status">'
        '<div class="sidebar-status-title">'
        '<span style="color:#31a354;">●</span> '
        'Application Ready'
        '</div>'
        '<div class="sidebar-status-sub">'
        'v1.0 · Internal build'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-title">'
        'WORKSPACE'
        '</div>',
        unsafe_allow_html=True,
    )

    views = [
        "Overview",
        "Analytics",
        "Risk",
        "Forecast",
        "Reports",
        "System",
    ]

    for view in views:
        if st.button(
            view,
            key=f"nav_{view}",
            use_container_width=True,
        ):
            st.session_state.active_view = view
            st.rerun()

    st.markdown(
        "---"
    )

    st.button(
        "New Analysis",
        key="new_analysis",
        use_container_width=True,
        on_click=reset_analysis,
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="page-kicker">'
    'AI CFO / Workspace'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# OVERVIEW
# ============================================================

if (
    st.session_state.active_view
    == "Overview"
):
    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">'
        'Financial Intelligence'
        '</div>'
        '<div class="hero-description">'
        'Understand financial activity, monitor transaction risk, '
        'forecast upcoming activity, and create management reports '
        'from one simple workspace.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    render_section(
        "What do you want to check?",
        "Choose an area to analyze.",
    )

    col1, col2, col3, col4 = st.columns(4)

    quick_question = None

    with col1:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">▣</div>'
            '<div class="action-title">Performance</div>'
            '<div class="action-text">'
            'View financial activity'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Analyze Performance",
            key="quick_performance",
            use_container_width=True,
        ):
            quick_question = (
                "Analyze the overall financial "
                "performance and summarize the "
                "key financial metrics."
            )

    with col2:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">◈</div>'
            '<div class="action-title">Risk</div>'
            '<div class="action-text">'
            'Check transaction risk'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Analyze Risk",
            key="quick_risk",
            use_container_width=True,
        ):
            quick_question = (
                "Analyze transaction risk and identify "
                "the main risk indicators."
            )

    with col3:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">◇</div>'
            '<div class="action-title">Forecast</div>'
            '<div class="action-text">'
            'See expected activity'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Run Forecast",
            key="quick_forecast",
            use_container_width=True,
        ):
            quick_question = (
                "Forecast the next transaction activity "
                "and evaluate the forecasting performance."
            )

    with col4:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">▤</div>'
            '<div class="action-title">Report</div>'
            '<div class="action-text">'
            'Create management report'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Generate Report",
            key="quick_report",
            use_container_width=True,
        ):
            quick_question = (
                "Generate a complete executive financial "
                "report covering financial performance, "
                "transaction risk, forecast, key insights, "
                "management recommendations, and report validation."
            )

    question = render_question_box()

    analyze_clicked = st.button(
        "Run Analysis",
        key="run_analysis",
        type="primary",
        use_container_width=True,
    )

    selected_question = quick_question

    if (
        selected_question is None
        and analyze_clicked
    ):
        if not question.strip():
            st.warning(
                "Enter a question or choose one "
                "of the analysis areas above."
            )
        else:
            selected_question = (
                question.strip()
            )

    if selected_question:
        try:
            result = run_analysis(
                selected_question
            )

            st.session_state.analysis_result = (
                result
            )

            st.session_state.last_error = None
            st.session_state.active_view = (
                "Overview"
            )

            st.rerun()

        except Exception as error:
            st.session_state.last_error = (
                str(error)
            )

            st.error(
                f"Analysis failed: {error}"
            )

    result = (
        st.session_state.analysis_result
    )

    if result is None:
        render_empty(
            "Start with an area above",
            "Choose Performance, Risk, Forecast, or Report to begin.",
        )

    else:
        render_analysis_context(
            result
        )

        executed_agents = set(
            get_executed_agents(
                result
            )
        )

        if "SQL" in executed_agents:
            render_financial_overview(
                result
            )

        if executed_agents.intersection(
            {
                "RISK",
                "FORECAST",
            }
        ):
            render_key_findings(
                result
            )

        if "INSIGHT" in executed_agents:
            render_insight(
                result
            )

        if "RISK" in executed_agents:
            render_risk_summary(
                result
            )

        if "FORECAST" in executed_agents:
            render_forecast(
                result
            )

        if "REPORT" in executed_agents:
            render_report(
                result
            )

        if "VALIDATOR" in executed_agents:
            render_validation(
                result
            )

        render_process(
            result
        )


# ============================================================
# ANALYTICS
# ============================================================

elif (
    st.session_state.active_view
    == "Analytics"
):
    st.markdown(
        '<div class="page-title">'
        'Analytics'
        '</div>'
        '<div class="page-description">'
        'Financial activity returned by the SQL analysis workflow.'
        '</div>',
        unsafe_allow_html=True,
    )

    result = (
        st.session_state.analysis_result
    )

    if result is None:
        render_empty(
            "No analysis available",
            "Run an analysis from Overview first.",
        )

    elif not agent_executed(
        result,
        "SQL",
    ):
        render_empty(
            "SQL analysis was not executed",
            "Run a Performance, Risk, Forecast, or Report analysis first.",
        )

    else:
        render_analysis_context(
            result
        )

        render_financial_overview(
            result
        )

        sql_result = get_sql_result(
            result
        )

        rows = sql_result.get(
            "rows",
            [],
        )

        columns = sql_result.get(
            "columns",
            [],
        )

        if rows:
            render_section(
                "SQL Analysis Result",
                "Raw structured output returned by the SQL Agent.",
            )

            try:
                dataframe = (
                    pd.DataFrame(
                        rows,
                        columns=columns,
                    )
                    if columns
                    else pd.DataFrame(
                        rows
                    )
                )

                render_dataframe(
                    dataframe
                )

            except Exception:
                st.write(
                    rows
                )

        else:
            render_empty(
                "No SQL rows returned",
                "The SQL Agent did not return tabular rows for this analysis.",
            )

        render_process(
            result
        )


# ============================================================
# RISK
# ============================================================

elif (
    st.session_state.active_view
    == "Risk"
):
    st.markdown(
        '<div class="page-title">'
        'Risk Analysis'
        '</div>'
        '<div class="page-description">'
        'Transaction risk and anomaly indicators generated '
        'from the financial dataset.'
        '</div>',
        unsafe_allow_html=True,
    )

    result = (
        st.session_state.analysis_result
    )

    if result is None:
        render_empty(
            "No risk analysis available",
            "Run a Risk analysis from Overview first.",
        )

    elif not agent_executed(
        result,
        "RISK",
    ):
        render_empty(
            "Risk Agent was not executed",
            "Run a Risk analysis from Overview first.",
        )

    else:
        render_analysis_context(
            result
        )

        if agent_executed(
            result,
            "SQL",
        ):
            render_financial_overview(
                result
            )

        render_key_findings(
            result
        )

        render_risk_summary(
            result
        )

        render_process(
            result
        )


# ============================================================
# FORECAST
# ============================================================

elif (
    st.session_state.active_view
    == "Forecast"
):
    st.markdown(
        '<div class="page-title">'
        'Forecast'
        '</div>'
        '<div class="page-description">'
        'Historical transaction activity and next-observation '
        'transaction-count forecasting.'
        '</div>',
        unsafe_allow_html=True,
    )

    result = (
        st.session_state.analysis_result
    )

    if result is None:
        render_empty(
            "No forecast available",
            "Run a Forecast analysis from Overview first.",
        )

    elif not agent_executed(
        result,
        "FORECAST",
    ):
        render_empty(
            "Forecast Agent was not executed",
            "Run a Forecast analysis from Overview first.",
        )

    else:
        render_analysis_context(
            result
        )

        if agent_executed(
            result,
            "SQL",
        ):
            render_financial_overview(
                result
            )

        render_key_findings(
            result
        )

        render_forecast(
            result
        )

        render_process(
            result
        )


# ============================================================
# REPORTS
# ============================================================

elif (
    st.session_state.active_view
    == "Reports"
):
    st.markdown(
        '<div class="page-title">'
        'Management Reports'
        '</div>'
        '<div class="page-description">'
        'Consolidated financial intelligence generated by '
        'the AI CFO workflow.'
        '</div>',
        unsafe_allow_html=True,
    )

    result = (
        st.session_state.analysis_result
    )

    if result is None:
        render_empty(
            "No report available",
            "Generate a management report from Overview first.",
        )

    elif not agent_executed(
        result,
        "REPORT",
    ):
        render_empty(
            "Report Agent was not executed",
            "Use Generate Report or request a complete executive analysis.",
        )

    else:
        render_analysis_context(
            result
        )

        if agent_executed(
            result,
            "SQL",
        ):
            render_financial_overview(
                result
            )

        if agent_executed(
            result,
            "INSIGHT",
        ):
            render_insight(
                result
            )

        if agent_executed(
            result,
            "RISK",
        ):
            render_risk_summary(
                result
            )

        if agent_executed(
            result,
            "FORECAST",
        ):
            render_forecast(
                result
            )

        render_report(
            result
        )

        if agent_executed(
            result,
            "VALIDATOR",
        ):
            render_validation(
                result
            )

        render_process(
            result
        )


# ============================================================
# SYSTEM
# ============================================================

elif (
    st.session_state.active_view
    == "System"
):
    st.markdown(
        '<div class="page-title">'
        'System'
        '</div>'
        '<div class="page-description">'
        'AI CFO architecture and technology stack.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_section(
        "Architecture"
    )

    architecture = [
        (
            "Supervisor",
            "Classifies the user request and selects the required agents.",
        ),
        (
            "SQL Agent",
            "Retrieves structured financial metrics from SQLite.",
        ),
        (
            "Risk Agent",
            "Identifies amount and account-frequency risk signals.",
        ),
        (
            "Forecast Agent",
            "Compares forecasting methods using historical activity.",
        ),
        (
            "Insight Agent",
            "Transforms analytical outputs into business observations.",
        ),
        (
            "Report Agent",
            "Creates the consolidated management report.",
        ),
        (
            "Report Validator",
            "Checks report consistency against analytical outputs.",
        ),
    ]

    cols = st.columns(3)

    for index, (
        name,
        description,
    ) in enumerate(
        architecture
    ):
        with cols[
            index % 3
        ]:
            st.markdown(
                '<div class="system-card">'
                f'<div class="system-name">'
                f'{safe_text(name)}'
                f'</div>'
                f'<div class="system-text">'
                f'{safe_text(description)}'
                f'</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    render_section(
        "Technology"
    )

    st.markdown(
        '<span class="badge badge-purple">LangGraph</span>'
        '<span class="badge badge-blue">LangChain</span>'
        '<span class="badge badge-green">SQLite</span>'
        '<span class="badge badge-orange">Ollama</span>'
        '<span class="badge badge-purple">Qwen</span>'
        '<span class="badge badge-blue">Streamlit</span>',
        unsafe_allow_html=True,
    )

    render_section(
        "Execution Model"
    )

    st.markdown(
        '<div class="card">'
        '<span class="badge badge-blue">'
        'User Question'
        '</span>'
        ' → '
        '<span class="badge badge-purple">'
        'Supervisor'
        '</span>'
        ' → '
        '<span class="badge badge-green">'
        'SQL'
        '</span>'
        ' → '
        '<span class="badge badge-orange">'
        'Risk'
        '</span>'
        ' → '
        '<span class="badge badge-purple">'
        'Forecast'
        '</span>'
        ' → '
        '<span class="badge badge-blue">'
        'Insight'
        '</span>'
        ' → '
        '<span class="badge badge-green">'
        'Report'
        '</span>'
        ' → '
        '<span class="badge badge-orange">'
        'Validator'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Agents are selected according to the user request; "
        "not every agent runs for every analysis."
    )

    render_section(
        "Available Agents"
    )

    st.markdown(
        '<div class="card">'
        '<span class="badge badge-green">SQL</span>'
        '<span class="badge badge-orange">RISK</span>'
        '<span class="badge badge-purple">FORECAST</span>'
        '<span class="badge badge-blue">INSIGHT</span>'
        '<span class="badge badge-green">REPORT</span>'
        '<span class="badge badge-orange">VALIDATOR</span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'AI CFO · Financial Management System · Internal Build v1.0'
    '</div>',
    unsafe_allow_html=True,
)
