import re
from decimal import Decimal, InvalidOperation


NUMBER_PATTERN = re.compile(
    r"(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?%?"
)

DATE_PATTERN = re.compile(
    r"\b\d{4}/\d{2}/\d{2}\b"
)

TIMESTAMP_PATTERN = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\b"
)

# Account IDs in the Risk report are identifiers, not numeric metrics.
# Examples:
# 100428660
# 1004286A8
# 1004286F0
ACCOUNT_ID_PATTERN = re.compile(
    r"\b100428[A-Za-z0-9]+\b"
)


def parse_number(value):
    try:
        return Decimal(
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )
    except (InvalidOperation, ValueError):
        return None


def normalize_number(value) -> str:
    number = parse_number(value)

    if number is None:
        raise ValueError(
            f"Invalid numeric value: {value}"
        )

    return format(
        number.normalize(),
        "f",
    )


def numbers_match(
    report_value: str,
    verified_value: str,
) -> bool:

    report_number = parse_number(
        report_value
    )

    verified_number = parse_number(
        verified_value
    )

    if (
        report_number is None
        or verified_number is None
    ):
        return False

    absolute_difference = abs(
        report_number - verified_number
    )

    if absolute_difference <= Decimal("0.01"):
        return True

    if verified_number != 0:
        relative_difference = (
            absolute_difference
            / abs(verified_number)
        )

        if relative_difference <= Decimal("0.000001"):
            return True

    return False


def remove_non_data_numbers(
    text: str,
) -> str:

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Remove generated timestamp.
        stripped = TIMESTAMP_PATTERN.sub(
            "",
            stripped,
        )

        # Remove historical dates.
        stripped = DATE_PATTERN.sub(
            "",
            stripped,
        )

        # Remove Account IDs.
        # They are identifiers and must not participate
        # in numerical integrity validation.
        stripped = ACCOUNT_ID_PATTERN.sub(
            "",
            stripped,
        )

        # Remove Markdown list numbering.
        stripped = re.sub(
            r"^\d+\.\s+",
            "",
            stripped,
        )

        # Remove numeric heading prefixes.
        stripped = re.sub(
            r"^(#{1,6})\s+\d+\.\s+",
            r"\1 ",
            stripped,
        )

        # Prevent "7-day" from being treated as data.
        stripped = re.sub(
            r"\b7-day\b",
            "moving-average",
            stripped,
            flags=re.IGNORECASE,
        )

        cleaned_lines.append(
            stripped
        )

    return "\n".join(
        cleaned_lines
    )


def extract_numbers(
    text: str,
) -> list[str]:

    cleaned_text = remove_non_data_numbers(
        text
    )

    matches = NUMBER_PATTERN.findall(
        cleaned_text
    )

    return [
        normalize_number(value)
        for value in matches
    ]


def add_numeric_value(
    verified: set[str],
    value,
) -> None:

    if isinstance(value, bool):
        return

    if isinstance(
        value,
        (int, float, Decimal),
    ):
        verified.add(
            normalize_number(value)
        )


def build_verified_number_set(
    sql_result: dict,
    risk_result: dict,
    forecast_result: dict,
) -> set[str]:

    verified = set()

    # ---------------------------------------------------------
    # SQL numbers
    # ---------------------------------------------------------

    sql_rows = sql_result.get(
        "rows",
        [],
    )

    for row in sql_rows:
        for value in row:
            add_numeric_value(
                verified,
                value,
            )

    # ---------------------------------------------------------
    # Risk numbers
    # ---------------------------------------------------------

    risk_numeric_fields = [
        "amount_threshold",
        "frequency_threshold",
        "high_value_transactions",
        "high_value_laundering",
        "high_value_laundering_rate",
        "high_frequency_accounts",
        "transactions_from_high_frequency_accounts",
    ]

    for field in risk_numeric_fields:
        add_numeric_value(
            verified,
            risk_result.get(field),
        )

    # Account IDs are intentionally NOT added.
    # They are identifiers, not numerical metrics.

    top_accounts = risk_result.get(
        "top_high_frequency_accounts",
        [],
    )

    for account in top_accounts:
        if not isinstance(
            account,
            (list, tuple),
        ):
            continue

        # Expected structure:
        # (
        #     account_id,
        #     transaction_count,
        #     frequency_threshold,
        #     laundering_rate,
        # )

        # Skip account_id at index 0.
        for value in account[1:]:
            add_numeric_value(
                verified,
                value,
            )

    # ---------------------------------------------------------
    # Forecast numbers
    # ---------------------------------------------------------

    forecast_numeric_fields = [
        "alpha",
        "backtest_test_observations",
        "forecast_next_day_transactions",
        "backtest_mae",
        "baseline_mae",
        "naive_baseline_mae",
        "improvement_vs_baseline",
        "improvement_vs_naive",
        "total_days",
        "backtest_test_start_index",
    ]

    for field in forecast_numeric_fields:
        add_numeric_value(
            verified,
            forecast_result.get(field),
        )

    # ---------------------------------------------------------
    # Candidate model numbers
    # ---------------------------------------------------------

    candidate_models = forecast_result.get(
        "candidate_models",
        [],
    )

    for candidate in candidate_models:
        if not isinstance(
            candidate,
            dict,
        ):
            continue

        for field in [
            "mae",
            "alpha",
        ]:
            add_numeric_value(
                verified,
                candidate.get(field),
            )

    # ---------------------------------------------------------
    # SES alpha results
    # ---------------------------------------------------------

    ses_results = forecast_result.get(
        "ses_alpha_results",
        [],
    )

    for result in ses_results:
        if not isinstance(
            result,
            dict,
        ):
            continue

        for field in [
            "alpha",
            "mae",
        ]:
            add_numeric_value(
                verified,
                result.get(field),
            )

    # ---------------------------------------------------------
    # Historical observations
    # ---------------------------------------------------------

    historical_days = forecast_result.get(
        "historical_days",
        [],
    )

    for row in historical_days:
        if isinstance(
            row,
            (list, tuple),
        ):
            for value in row:
                add_numeric_value(
                    verified,
                    value,
                )

    return verified


def validate_required_sections(
    report: str,
    sql_result: dict,
    risk_result: dict,
    forecast_result: dict,
) -> list[str]:

    """
    Validate only the sections corresponding to
    analytical results that actually exist.
    """

    required_sections = [
        "## Executive Summary",
        "## AI-Generated Insights",
        "## Management Actions",
        "## Data & Methodology",
    ]

    if sql_result:
        required_sections.append(
            "## Financial Performance"
        )

    if risk_result:
        required_sections.append(
            "## Risk & Anomaly Analysis"
        )

    if forecast_result:
        required_sections.extend(
            [
                "## Forecast",
                "### Forecast Validation",
            ]
        )

        if forecast_result.get(
            "candidate_models"
        ):
            required_sections.append(
                "### Candidate Model Comparison"
            )

        if forecast_result.get(
            "historical_days"
        ):
            required_sections.append(
                "### Historical Daily Observations"
            )

    missing_sections = []

    for section in required_sections:
        if section not in report:
            missing_sections.append(
                section
            )

    return missing_sections


def validate_consistency(
    report: str,
    sql_result: dict,
    risk_result: dict,
    forecast_result: dict,
) -> list[str]:

    errors = []

    # ---------------------------------------------------------
    # Risk consistency
    # ---------------------------------------------------------

    if risk_result:

        high_value_transactions = risk_result.get(
            "high_value_transactions"
        )

        high_value_laundering = risk_result.get(
            "high_value_laundering"
        )

        if (
            isinstance(
                high_value_transactions,
                (int, float),
            )
            and isinstance(
                high_value_laundering,
                (int, float),
            )
        ):
            if (
                high_value_laundering
                > high_value_transactions
            ):
                errors.append(
                    "High-value laundering transactions cannot exceed high-value transactions."
                )

    # ---------------------------------------------------------
    # Forecast consistency
    # ---------------------------------------------------------

    if forecast_result:

        selected_model = forecast_result.get(
            "selected_model"
        )

        candidate_models = forecast_result.get(
            "candidate_models",
            [],
        )

        candidate_names = []

        for candidate in candidate_models:
            if not isinstance(
                candidate,
                dict,
            ):
                continue

            name = candidate.get(
                "method"
            )

            if name:
                candidate_names.append(
                    name
                )

        if (
            selected_model
            and candidate_names
            and selected_model not in candidate_names
        ):
            errors.append(
                "Selected forecasting model is not present in the candidate model results."
            )

        forecast_value = forecast_result.get(
            "forecast_next_day_transactions"
        )

        if forecast_value is not None:

            report_forecast_pattern = re.search(
                r"Forecast Next-Day Transactions:\s*\*?([0-9,.\-]+)",
                report,
                flags=re.IGNORECASE,
            )

            if report_forecast_pattern:

                report_forecast_value = (
                    report_forecast_pattern.group(1)
                )

                if not numbers_match(
                    report_forecast_value,
                    str(forecast_value),
                ):
                    errors.append(
                        "Report forecast value does not match the Forecast Agent output."
                    )

            else:
                errors.append(
                    "Forecast next-day transaction value is missing from the report."
                )

    # ---------------------------------------------------------
    # SQL consistency
    # ---------------------------------------------------------

    if sql_result:

        sql_rows = sql_result.get(
            "rows",
            [],
        )

        if not sql_rows:
            errors.append(
                "SQL Agent returned no rows."
            )

    return errors


def validate_report(
    report: str,
    sql_result: dict,
    risk_result: dict,
    forecast_result: dict,
) -> dict:

    has_sql = bool(sql_result)
    has_risk = bool(risk_result)
    has_forecast = bool(forecast_result)

    if not (
        has_sql
        or has_risk
        or has_forecast
    ):
        return {
            "valid": False,
            "numerical_integrity": False,
            "section_integrity": False,
            "consistency_integrity": False,
            "invalid_numbers": [],
            "missing_sections": [],
            "consistency_errors": [
                "No analytical agent results were provided."
            ],
            "verified_numbers": [],
        }

    # ---------------------------------------------------------
    # Build verified numerical values
    # ---------------------------------------------------------

    verified_numbers = build_verified_number_set(
        sql_result=sql_result,
        risk_result=risk_result,
        forecast_result=forecast_result,
    )

    # ---------------------------------------------------------
    # Extract numerical values from report
    # ---------------------------------------------------------

    report_numbers = extract_numbers(
        report
    )

    invalid_numbers = []

    for report_number in report_numbers:

        matched = any(
            numbers_match(
                report_number,
                verified_number,
            )
            for verified_number in verified_numbers
        )

        if not matched:
            invalid_numbers.append(
                report_number
            )

    numerical_integrity = (
        len(invalid_numbers) == 0
    )

    # ---------------------------------------------------------
    # Section integrity
    # ---------------------------------------------------------

    missing_sections = validate_required_sections(
        report=report,
        sql_result=sql_result,
        risk_result=risk_result,
        forecast_result=forecast_result,
    )

    section_integrity = (
        len(missing_sections) == 0
    )

    # ---------------------------------------------------------
    # Consistency integrity
    # ---------------------------------------------------------

    consistency_errors = validate_consistency(
        report=report,
        sql_result=sql_result,
        risk_result=risk_result,
        forecast_result=forecast_result,
    )

    consistency_integrity = (
        len(consistency_errors) == 0
    )

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------

    valid = (
        numerical_integrity
        and section_integrity
        and consistency_integrity
    )

    return {
        "valid": valid,
        "numerical_integrity": numerical_integrity,
        "section_integrity": section_integrity,
        "consistency_integrity": consistency_integrity,
        "invalid_numbers": sorted(
            set(invalid_numbers)
        ),
        "missing_sections": missing_sections,
        "consistency_errors": consistency_errors,
        "verified_numbers": sorted(
            verified_numbers
        ),
    }