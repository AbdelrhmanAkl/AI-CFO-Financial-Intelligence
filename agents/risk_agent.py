from tools.database import execute_query


AMOUNT_THRESHOLD = 30590.62
FREQUENCY_THRESHOLD = 92


def run_risk_agent():
    high_value_query = f"""
    SELECT
        COUNT(*) AS transaction_count,
        SUM(is_laundering) AS laundering_count,
        ROUND(
            SUM(is_laundering) * 100.0 / COUNT(*),
            4
        ) AS laundering_rate
    FROM transactions
    WHERE amount_received > {AMOUNT_THRESHOLD}
    """

    _, high_value_rows = execute_query(high_value_query)
    high_value = high_value_rows[0]

    high_frequency_query = f"""
    SELECT
        COUNT(*) AS high_frequency_accounts,
        SUM(transaction_count) AS transactions_from_high_frequency_accounts
    FROM (
        SELECT
            from_account,
            COUNT(*) AS transaction_count
        FROM transactions
        GROUP BY from_account
        HAVING COUNT(*) > {FREQUENCY_THRESHOLD}
    )
    """

    _, high_frequency_rows = execute_query(high_frequency_query)
    high_frequency = high_frequency_rows[0]

    top_accounts_query = f"""
    SELECT
        from_account,
        COUNT(*) AS transaction_count,
        SUM(is_laundering) AS laundering_count,
        ROUND(
            SUM(is_laundering) * 100.0 / COUNT(*),
            4
        ) AS laundering_rate
    FROM transactions
    GROUP BY from_account
    HAVING COUNT(*) > {FREQUENCY_THRESHOLD}
    ORDER BY transaction_count DESC
    LIMIT 10
    """

    _, top_accounts = execute_query(top_accounts_query)

    return {
        "amount_threshold": AMOUNT_THRESHOLD,
        "frequency_threshold": FREQUENCY_THRESHOLD,
        "high_value_transactions": high_value[0],
        "high_value_laundering": high_value[1],
        "high_value_laundering_rate": high_value[2],
        "high_frequency_accounts": high_frequency[0],
        "transactions_from_high_frequency_accounts": high_frequency[1],
        "top_high_frequency_accounts": top_accounts,
    }