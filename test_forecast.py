from statistics import mean
from tools.database import execute_query

query = """
SELECT
    substr(timestamp, 1, 10) AS date,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY date
ORDER BY date
"""

_, rows = execute_query(query)

values = [row[1] for row in rows]

actual = []
predicted = []

for i in range(7, len(values)):
    prediction = mean(values[i-7:i])
    predicted.append(prediction)
    actual.append(values[i])

mae = mean(
    abs(a - p)
    for a, p in zip(actual, predicted)
)

next_day = mean(values[-7:])

print("METHOD: 7-day Moving Average")
print("TEST POINTS:", len(actual))
print("BACKTEST MAE:", round(mae, 2))
print("NEXT-DAY BASELINE FORECAST:", round(next_day, 2))
