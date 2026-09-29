from tools.database import execute_query


def run_data_quality_agent() -> dict:
    """
    Analyze transaction data quality and detect major
    volume or composition changes across daily observations.
    """

    query = """
    SELECT
        substr(timestamp, 1, 10) AS date,
        COUNT(*) AS transactions,
        COUNT(DISTINCT from_bank) AS from_banks,
        COUNT(DISTINCT to_bank) AS to_banks,
        COUNT(DISTINCT from_account) AS from_accounts,
        COUNT(DISTINCT to_account) AS to_accounts,
        COUNT(DISTINCT receiving_currency) AS receiving_currencies,
        COUNT(DISTINCT payment_currency) AS payment_currencies
    FROM transactions
    GROUP BY substr(timestamp, 1, 10)
    ORDER BY date;
    """

    columns, rows = execute_query(query)

    if not rows:
        raise ValueError("No daily transaction data available.")

    daily_data = [
        dict(zip(columns, row))
        for row in rows
    ]

    warnings = []

    # Detect major transaction-volume changes
    for previous, current in zip(daily_data, daily_data[1:]):
        previous_transactions = previous["transactions"]
        current_transactions = current["transactions"]

        if previous_transactions == 0:
            continue

        change_percentage = (
            (current_transactions - previous_transactions)
            / previous_transactions
        ) * 100

        if abs(change_percentage) >= 50:
            warnings.append({
                "type": "transaction_volume_change",
                "date": current["date"],
                "previous_transactions": previous_transactions,
                "current_transactions": current_transactions,
                "change_percentage": round(change_percentage, 2),
            })

    # Detect major account-coverage changes
    for previous, current in zip(daily_data, daily_data[1:]):
        previous_accounts = previous["from_accounts"]
        current_accounts = current["from_accounts"]

        if previous_accounts == 0:
            continue

        change_percentage = (
            (current_accounts - previous_accounts)
            / previous_accounts
        ) * 100

        if abs(change_percentage) >= 50:
            warnings.append({
                "type": "account_coverage_change",
                "date": current["date"],
                "previous_from_accounts": previous_accounts,
                "current_from_accounts": current_accounts,
                "change_percentage": round(change_percentage, 2),
            })

    status = "WARNING" if warnings else "OK"

    return {
        "status": status,
        "total_days": len(daily_data),
        "daily_data": daily_data,
        "warnings": warnings,
    }