import re

from agents.local_llm import llm
from tools.database import execute_query


SCHEMA = """
Table: transactions

Columns:
- timestamp TEXT
- from_bank TEXT
- from_account TEXT
- to_bank TEXT
- to_account TEXT
- amount_received REAL
- receiving_currency TEXT
- amount_paid REAL
- payment_currency TEXT
- payment_format TEXT
- is_laundering INTEGER
"""


FORBIDDEN_SQL_KEYWORDS = [
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "DROP ",
    "ALTER ",
    "CREATE ",
    "PRAGMA ",
]


def get_dataset_period():
    query = """
    SELECT
        MIN(timestamp) AS min_timestamp,
        MAX(timestamp) AS max_timestamp,
        COUNT(*) AS transaction_count
    FROM transactions
    """

    _, rows = execute_query(query)

    min_timestamp, max_timestamp, transaction_count = rows[0]

    return {
        "min_timestamp": min_timestamp,
        "max_timestamp": max_timestamp,
        "transaction_count": transaction_count,
    }


def normalize_relative_dates(sql: str, dataset_period: dict) -> str:
    latest_timestamp = dataset_period["max_timestamp"]
    latest_date = latest_timestamp[:10]

    previous_date_query = f"""
    SELECT MAX(substr(timestamp, 1, 10))
    FROM transactions
    WHERE substr(timestamp, 1, 10) < '{latest_date}'
    """

    _, rows = execute_query(previous_date_query)

    previous_date = rows[0][0]

    if previous_date is None:
        previous_date = latest_date

    # DATE('now', '-1 day')
    sql = re.sub(
        r"DATE\(\s*'now'\s*,\s*'-1 day'\s*\)",
        f"'{previous_date}'",
        sql,
        flags=re.IGNORECASE,
    )

    # DATE('now')
    sql = re.sub(
        r"DATE\(\s*'now'\s*\)",
        f"'{latest_date}'",
        sql,
        flags=re.IGNORECASE,
    )

    # CURRENT_DATE
    sql = re.sub(
        r"\bCURRENT_DATE\b",
        f"'{latest_date}'",
        sql,
        flags=re.IGNORECASE,
    )

    # CURRENT_TIMESTAMP
    sql = re.sub(
        r"\bCURRENT_TIMESTAMP\b",
        f"'{latest_timestamp}'",
        sql,
        flags=re.IGNORECASE,
    )

    # datetime('now')
    sql = re.sub(
        r"datetime\(\s*'now'\s*\)",
        f"'{latest_timestamp}'",
        sql,
        flags=re.IGNORECASE,
    )

    # Convert YYYY-MM-DD or YYYY-MM-DD HH:MM
    # into the dataset format YYYY/MM/DD HH:MM.
    sql = re.sub(
        r"'(\d{4})-(\d{2})-(\d{2})(\s+\d{2}:\d{2})?'",
        lambda match: (
            f"'{match.group(1)}/{match.group(2)}/{match.group(3)}"
            f"{match.group(4) or ''}'"
        ),
        sql,
    )

    # DATE(timestamp) is unsafe for this dataset format.
    sql = re.sub(
        r"DATE\(\s*timestamp\s*\)",
        "substr(timestamp, 1, 10)",
        sql,
        flags=re.IGNORECASE,
    )

    # Normalize STRFTIME usage.
    sql = re.sub(
        r"strftime\(\s*'([^']+)'\s*,\s*timestamp\s*\)",
        r"strftime('\1', replace(timestamp, '/', '-'))",
        sql,
        flags=re.IGNORECASE,
    )

    return sql


def clean_sql(sql: str) -> str:
    sql = sql.strip()

    sql = re.sub(
        r"```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"```\s*",
        "",
        sql,
    )

    return sql.strip()


def validate_sql(sql: str):
    normalized = sql.strip().upper()

    if not (
        normalized.startswith("SELECT")
        or normalized.startswith("WITH")
    ):
        raise ValueError(
            "Only SELECT and WITH queries are allowed."
        )

    if any(
        keyword in normalized
        for keyword in FORBIDDEN_SQL_KEYWORDS
    ):
        raise ValueError(
            "Unsafe SQL query detected."
        )


def generate_sql(question: str) -> str:
    dataset_period = get_dataset_period()

    prompt = f"""
You are a SQL analyst working with a historical financial
transaction database.

DATABASE SCHEMA:

{SCHEMA}

DATASET INFORMATION:

- Earliest transaction:
  {dataset_period["min_timestamp"]}

- Latest transaction:
  {dataset_period["max_timestamp"]}

- Total transactions:
  {dataset_period["transaction_count"]}


DATASET RULES:

1. This is historical data.

2. Timestamp format:
   YYYY/MM/DD HH:MM

3. Never assume today's date exists.

4. Never use:
   DATE('now')
   CURRENT_DATE
   CURRENT_TIMESTAMP
   datetime('now')

5. If recent/latest data is requested,
   use the latest available dataset date.

6. Latest available timestamp:
   {dataset_period["max_timestamp"]}

7. Latest available date:
   {dataset_period["max_timestamp"][:10]}

8. Never use DATE(timestamp).

9. Extract dates using:
   substr(timestamp, 1, 10)

10. For STRFTIME use:
    strftime('%Y-%m-%d', replace(timestamp, '/', '-'))

11. Timestamp filters must use:
    YYYY/MM/DD HH:MM

12. Never invent dates outside the dataset.

13. If no date filter is required,
    do not add one.


FINANCIAL PERFORMANCE:

If the user asks for financial performance,
financial analysis, overview, or summary,
generate an aggregate query.

For a general financial performance request,
ALWAYS return exactly these five aliases:

transaction_count
total_amount_received
total_amount_paid
average_transaction_amount
laundering_transaction_count

Use this exact query structure:

SELECT
    COUNT(*) AS transaction_count,
    SUM(amount_received) AS total_amount_received,
    SUM(amount_paid) AS total_amount_paid,
    AVG(amount_paid) AS average_transaction_amount,
    SUM(
        CASE
            WHEN is_laundering = 1 THEN 1
            ELSE 0
        END
    ) AS laundering_transaction_count
FROM transactions;

Do not rename these aliases.

Do not omit these five metrics for a
general financial performance request.

For other questions, return only the
metrics relevant to the question.


SQL GENERATION RULES:

- Generate ONE SQLite query.
- Only SELECT or WITH.
- Never use INSERT.
- Never use UPDATE.
- Never use DELETE.
- Never use DROP.
- Never use ALTER.
- Never use CREATE.
- Never use PRAGMA.

IMPORTANT:

- Do not use UNION unless absolutely necessary.
- If UNION is used, every SELECT must return
  exactly the same number of columns.
- Prefer a single SELECT query whenever possible.
- Do not return individual rows unless explicitly requested.
- Do not invent columns.
- Do not invent dates.
- Do not invent metrics.


OUTPUT RULE:

Return ONLY the SQL query.

No markdown.
No code fences.
No explanation.


USER QUESTION:

{question}
"""

    response = llm.invoke(prompt)

    sql = clean_sql(response.content)

    sql = normalize_relative_dates(
        sql,
        dataset_period,
    )

    return sql.strip()


def generate_retry_sql(
    question: str,
    failed_sql: str,
    error_message: str,
) -> str:

    prompt = f"""
You are a SQL debugging agent.

You are working with this SQLite table:

{SCHEMA}

USER QUESTION:

{question}

FAILED SQL:

{failed_sql}

SQLITE ERROR:

{error_message}


Generate ONE corrected SQLite query.

RULES:

- SELECT or WITH only.
- Read-only query.
- No INSERT.
- No UPDATE.
- No DELETE.
- No DROP.
- No ALTER.
- No CREATE.
- No PRAGMA.
- Prefer a single SELECT.
- Do not use UNION unless necessary.
- If UNION is used, every SELECT must have exactly
  the same number of columns.
- Do not invent columns.
- Do not invent dates.

For a general financial performance question,
use exactly these aliases:

transaction_count
total_amount_received
total_amount_paid
average_transaction_amount
laundering_transaction_count

Use:

SELECT
    COUNT(*) AS transaction_count,
    SUM(amount_received) AS total_amount_received,
    SUM(amount_paid) AS total_amount_paid,
    AVG(amount_paid) AS average_transaction_amount,
    SUM(
        CASE
            WHEN is_laundering = 1 THEN 1
            ELSE 0
        END
    ) AS laundering_transaction_count
FROM transactions;

Return ONLY SQL.
No markdown.
No explanation.
"""

    response = llm.invoke(prompt)

    return clean_sql(response.content)


def run_sql_agent(question: str):
    sql = generate_sql(question)

    validate_sql(sql)

    try:
        columns, rows = execute_query(sql)

    except Exception as first_error:

        retry_sql = generate_retry_sql(
            question=question,
            failed_sql=sql,
            error_message=str(first_error),
        )

        dataset_period = get_dataset_period()

        retry_sql = normalize_relative_dates(
            retry_sql,
            dataset_period,
        )

        validate_sql(retry_sql)

        columns, rows = execute_query(retry_sql)

        sql = retry_sql

    return {
        "question": question,
        "sql": sql,
        "columns": columns,
        "rows": rows,
    }
