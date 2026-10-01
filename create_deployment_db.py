import sqlite3
import os


SOURCE_DB = "data/financial.db"
TARGET_DB = "data/financial_deployment.db"


if os.path.exists(TARGET_DB):
    os.remove(TARGET_DB)


source = sqlite3.connect(SOURCE_DB)
target = sqlite3.connect(TARGET_DB)


target.execute("""
CREATE TABLE transactions (
    timestamp TEXT,
    from_bank TEXT,
    from_account TEXT,
    to_bank TEXT,
    to_account TEXT,
    amount_received REAL,
    receiving_currency TEXT,
    amount_paid REAL,
    payment_currency TEXT,
    payment_format TEXT,
    is_laundering INTEGER
)
""")


print("Copying deployment transactions...")


target.execute("""
ATTACH DATABASE ? AS source_db
""", (SOURCE_DB,))


target.execute("""
INSERT INTO transactions
SELECT *
FROM source_db.transactions
WHERE is_laundering = 1

   OR from_account IN (
        SELECT from_account
        FROM source_db.transactions
        GROUP BY from_account
        HAVING COUNT(*) > 92
   )

   OR to_account IN (
        SELECT from_account
        FROM source_db.transactions
        WHERE is_laundering = 1
   )
""")


target.commit()


target.execute("""
CREATE INDEX idx_timestamp
ON transactions(timestamp)
""")

target.execute("""
CREATE INDEX idx_from_account
ON transactions(from_account)
""")

target.execute("""
CREATE INDEX idx_to_account
ON transactions(to_account)
""")

target.execute("""
CREATE INDEX idx_laundering
ON transactions(is_laundering)
""")


target.commit()

count = target.execute(
    "SELECT COUNT(*) FROM transactions"
).fetchone()[0]

target.close()
source.close()


print()
print("Deployment DB created successfully.")
print("Transactions:", count)
print(
    "Size:",
    round(os.path.getsize(TARGET_DB) / (1024 ** 2), 2),
    "MB"
)