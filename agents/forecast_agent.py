from statistics import mean

from tools.database import execute_query


ALPHA_VALUES = [
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
]

BASELINE_WINDOW = 7
MIN_TRAIN_SIZE = BASELINE_WINDOW

# Diagnostic settings
RECENT_WINDOW = 3
REGIME_CHANGE_THRESHOLD = 0.80


def get_daily_transaction_counts():
    query = """
    SELECT
        substr(timestamp, 1, 10) AS date,
        COUNT(*) AS transaction_count
    FROM transactions
    GROUP BY date
    ORDER BY date
    """

    columns, rows = execute_query(query)

    if not rows:
        raise ValueError(
            "No daily transaction data found."
        )

    return {
        "columns": columns,
        "rows": rows,
    }


def simple_exponential_smoothing(
    values,
    alpha,
):
    if not values:
        raise ValueError(
            "No values provided for forecasting."
        )

    if not 0 < alpha <= 1:
        raise ValueError(
            "Alpha must be greater than 0 and less than or equal to 1."
        )

    level = float(values[0])

    for value in values[1:]:
        level = (
            alpha * float(value)
            + (1 - alpha) * level
        )

    return max(0.0, level)


def calculate_mae(
    actual,
    predicted,
):
    if not actual or not predicted:
        raise ValueError(
            "No values available for MAE calculation."
        )

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    errors = [
        abs(float(a) - float(p))
        for a, p in zip(actual, predicted)
    ]

    return mean(errors)


def backtest_ses(
    values,
    alpha,
    start_index,
):
    if len(values) <= start_index:
        raise ValueError(
            "Not enough observations for SES backtesting."
        )

    actual_values = []
    predicted_values = []

    for test_index in range(
        start_index,
        len(values),
    ):
        train = values[:test_index]

        prediction = simple_exponential_smoothing(
            train,
            alpha,
        )

        actual = values[test_index]

        predicted_values.append(prediction)
        actual_values.append(actual)

    return calculate_mae(
        actual_values,
        predicted_values,
    )


def backtest_moving_average(
    values,
    window=BASELINE_WINDOW,
    start_index=BASELINE_WINDOW,
):
    if len(values) <= start_index:
        raise ValueError(
            "Not enough observations for moving-average backtesting."
        )

    if start_index < window:
        raise ValueError(
            "Start index must be greater than or equal to the moving-average window."
        )

    actual_values = []
    predicted_values = []

    for test_index in range(
        start_index,
        len(values),
    ):
        prediction = mean(
            values[
                test_index - window:test_index
            ]
        )

        actual = values[test_index]

        predicted_values.append(prediction)
        actual_values.append(actual)

    return calculate_mae(
        actual_values,
        predicted_values,
    )


def backtest_naive(
    values,
    start_index=BASELINE_WINDOW,
):
    if len(values) <= start_index:
        raise ValueError(
            "Not enough observations for naive backtesting."
        )

    actual_values = []
    predicted_values = []

    for test_index in range(
        start_index,
        len(values),
    ):
        prediction = values[
            test_index - 1
        ]

        actual = values[test_index]

        predicted_values.append(prediction)
        actual_values.append(actual)

    return calculate_mae(
        actual_values,
        predicted_values,
    )


def find_best_ses_alpha(
    values,
    start_index,
):
    results = []

    for alpha in ALPHA_VALUES:
        mae = backtest_ses(
            values,
            alpha,
            start_index=start_index,
        )

        results.append(
            {
                "alpha": alpha,
                "mae": mae,
            }
        )

    best_result = min(
        results,
        key=lambda item: item["mae"],
    )

    return best_result, results


def calculate_improvement_percentage(
    baseline_mae,
    model_mae,
):
    if baseline_mae == 0:
        return 0.0

    return (
        (baseline_mae - model_mae)
        / baseline_mae
        * 100
    )


def calculate_recent_statistics(
    values,
):
    if not values:
        raise ValueError(
            "No values available for recent statistics."
        )

    recent_3_days = values[
        -RECENT_WINDOW:
    ]

    recent_7_days = values[
        -BASELINE_WINDOW:
    ]

    recent_3_day_average = mean(
        recent_3_days
    )

    recent_7_day_average = mean(
        recent_7_days
    )

    last_day_value = float(
        values[-1]
    )

    previous_day_value = (
        float(values[-2])
        if len(values) >= 2
        else last_day_value
    )

    if previous_day_value != 0:
        last_day_change_percentage = (
            (
                last_day_value
                - previous_day_value
            )
            / previous_day_value
            * 100
        )
    else:
        last_day_change_percentage = 0.0

    return {
        "recent_3_day_average": round(
            recent_3_day_average,
            2,
        ),
        "recent_7_day_average": round(
            recent_7_day_average,
            2,
        ),
        "last_day_change_percentage": round(
            last_day_change_percentage,
            2,
        ),
    }


def detect_data_quality_conditions(
    values,
):
    conditions = []

    total_days = len(values)

    if total_days < 30:
        conditions.append(
            "Short historical series: fewer than 30 daily observations are available."
        )

    if len(values) >= 2:
        previous_day = float(
            values[-2]
        )

        last_day = float(
            values[-1]
        )

        if previous_day > 0:
            change_ratio = abs(
                last_day - previous_day
            ) / previous_day

            if (
                change_ratio
                >= REGIME_CHANGE_THRESHOLD
            ):
                conditions.append(
                    "Recent transaction volume changed sharply between the last two observations."
                )

    if len(values) >= BASELINE_WINDOW:
        recent_average = mean(
            values[-BASELINE_WINDOW:]
        )

        earlier_values = values[
            :-BASELINE_WINDOW
        ]

        if earlier_values:
            earlier_average = mean(
                earlier_values
            )

            if earlier_average > 0:
                regime_ratio = (
                    recent_average
                    / earlier_average
                )

                if regime_ratio < 0.20:
                    conditions.append(
                        "Recent transaction volume is substantially lower than the earlier historical period."
                    )

                elif regime_ratio > 5.0:
                    conditions.append(
                        "Recent transaction volume is substantially higher than the earlier historical period."
                    )

    if not conditions:
        conditions.append(
            "No major data-quality condition detected."
        )

    return conditions


def run_forecast_agent():

    daily_data = get_daily_transaction_counts()

    rows = daily_data["rows"]

    if len(rows) <= MIN_TRAIN_SIZE:
        raise ValueError(
            "Not enough historical observations for forecasting."
        )

    # ---------------------------------------------------------
    # Prepare daily transaction series
    # ---------------------------------------------------------

    dates = [
        str(row[0])
        for row in rows
    ]

    values = [
        float(row[1])
        for row in rows
    ]

    test_start_index = BASELINE_WINDOW

    test_observations = (
        len(values) - test_start_index
    )

    # ---------------------------------------------------------
    # Historical data diagnostics
    # ---------------------------------------------------------

    recent_statistics = (
        calculate_recent_statistics(
            values
        )
    )

    data_quality_conditions = (
        detect_data_quality_conditions(
            values
        )
    )

    # ---------------------------------------------------------
    # Candidate 1: Simple Exponential Smoothing
    # ---------------------------------------------------------

    best_ses_result, alpha_results = (
        find_best_ses_alpha(
            values,
            start_index=test_start_index,
        )
    )

    best_ses_alpha = (
        best_ses_result["alpha"]
    )

    ses_mae = (
        best_ses_result["mae"]
    )

    # ---------------------------------------------------------
    # Candidate 2: 7-Day Moving Average
    # ---------------------------------------------------------

    moving_average_mae = (
        backtest_moving_average(
            values,
            window=BASELINE_WINDOW,
            start_index=test_start_index,
        )
    )

    # ---------------------------------------------------------
    # Candidate 3: Naive Last-Value Forecast
    # ---------------------------------------------------------

    naive_mae = (
        backtest_naive(
            values,
            start_index=test_start_index,
        )
    )

    # ---------------------------------------------------------
    # Compare candidate models
    # ---------------------------------------------------------

    candidate_models = [
        {
            "model": "Simple Exponential Smoothing",
            "mae": ses_mae,
            "alpha": best_ses_alpha,
        },
        {
            "model": "7-Day Moving Average",
            "mae": moving_average_mae,
            "alpha": None,
        },
        {
            "model": "Naive Last-Value Forecast",
            "mae": naive_mae,
            "alpha": None,
        },
    ]

    selected_model = min(
        candidate_models,
        key=lambda item: item["mae"],
    )

    selected_model_name = (
        selected_model["model"]
    )

    selected_mae = (
        selected_model["mae"]
    )

    selected_alpha = (
        selected_model["alpha"]
    )

    # ---------------------------------------------------------
    # Generate next-day transaction-count forecast
    # ---------------------------------------------------------

    if selected_model_name == (
        "Simple Exponential Smoothing"
    ):
        next_day_forecast = (
            simple_exponential_smoothing(
                values,
                selected_alpha,
            )
        )

    elif selected_model_name == (
        "7-Day Moving Average"
    ):
        next_day_forecast = mean(
            values[-BASELINE_WINDOW:]
        )

    else:
        next_day_forecast = float(
            values[-1]
        )

    # ---------------------------------------------------------
    # Compare selected model against 7-day baseline
    # ---------------------------------------------------------

    improvement_vs_moving_average = (
        calculate_improvement_percentage(
            moving_average_mae,
            selected_mae,
        )
    )

    # ---------------------------------------------------------
    # Compare selected model against naive baseline
    # ---------------------------------------------------------

    improvement_vs_naive = (
        calculate_improvement_percentage(
            naive_mae,
            selected_mae,
        )
    )

    # ---------------------------------------------------------
    # Forecast interpretation
    # ---------------------------------------------------------

    forecast_warning = (
        "Forecast is based on a short historical series "
        "and should be interpreted as a statistical "
        "transaction-count estimate rather than a guaranteed value."
    )

    if len(values) < 30:
        forecast_warning = (
            "Forecast is based on only "
            f"{len(values)} daily observations. "
            "The limited history and recent change in transaction "
            "volume may reduce forecast stability."
        )

    # ---------------------------------------------------------
    # Return verified forecasting results
    # ---------------------------------------------------------

    return {
        "method": selected_model_name,

        "selected_model": selected_model_name,

        "alpha": selected_alpha,

        "total_days": len(values),

        "first_date": dates[0],

        "last_date": dates[-1],

        "last_day_transactions": round(
            values[-1],
            2,
        ),

        "historical_days": rows,

        # -----------------------------------------------------
        # Backtesting
        # -----------------------------------------------------

        "backtest_test_start_index": (
            test_start_index
        ),

        "backtest_test_observations": (
            test_observations
        ),

        "backtest_mae": round(
            selected_mae,
            2,
        ),

        # -----------------------------------------------------
        # Candidate models
        # -----------------------------------------------------

        "candidate_models": [
            {
                "model": model["model"],
                "mae": round(
                    model["mae"],
                    2,
                ),
                "alpha": model["alpha"],
            }
            for model in candidate_models
        ],

        "ses_alpha_results": [
            {
                "alpha": result["alpha"],
                "mae": round(
                    result["mae"],
                    2,
                ),
            }
            for result in alpha_results
        ],

        # -----------------------------------------------------
        # Baselines
        # -----------------------------------------------------

        "baseline_method": (
            "7-Day Moving Average"
        ),

        "baseline_mae": round(
            moving_average_mae,
            2,
        ),

        "improvement_vs_baseline": round(
            improvement_vs_moving_average,
            2,
        ),

        "naive_baseline_method": (
            "Naive Last-Value Forecast"
        ),

        "naive_baseline_mae": round(
            naive_mae,
            2,
        ),

        "improvement_vs_naive": round(
            improvement_vs_naive,
            2,
        ),

        # -----------------------------------------------------
        # Forecast
        # -----------------------------------------------------

        "forecast_next_day_transactions": round(
            next_day_forecast,
            2,
        ),

        "forecast_target": (
            "Next-Day Transaction Count"
        ),

        "forecast_warning": (
            forecast_warning
        ),

        # -----------------------------------------------------
        # Recent activity diagnostics
        # -----------------------------------------------------

        "recent_3_day_average": (
            recent_statistics[
                "recent_3_day_average"
            ]
        ),

        "recent_7_day_average": (
            recent_statistics[
                "recent_7_day_average"
            ]
        ),

        "last_day_change_percentage": (
            recent_statistics[
                "last_day_change_percentage"
            ]
        ),

        # -----------------------------------------------------
        # Data quality diagnostics
        # -----------------------------------------------------

        "data_quality_conditions": (
            data_quality_conditions
        ),

        "data_quality_status": (
            "WARNING"
            if not (
                len(data_quality_conditions) == 1
                and data_quality_conditions[0]
                == "No major data-quality condition detected."
            )
            else "OK"
        ),
    }