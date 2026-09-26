import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "HI-Small_Trans.csv"
DB_FILE = BASE_DIR / "data" / "financial.db"

BATCH_SIZE = 50_000

if DB_FILE.exists():
    DB_FILE.unlink()

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE transactions (
    timestamp TEXT NOT NULL,
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

insert_sql = """
INSERT INTO transactions (
    timestamp,
    from_bank,
    from_account,
    to_bank,
    to_account,
    amount_received,
    receiving_currency,
    amount_paid,
    payment_currency,
    payment_format,
    is_laundering
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

total_rows = 0
batch = []

print(f"Reading: {CSV_FILE}")
print("Building SQLite database...")

with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)

    next(reader)

    for row in reader:
        batch.append((
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            float(row[5]),
            row[6],
            float(row[7]),
            row[8],
            row[9],
            int(row[10])
        ))

        if len(batch) >= BATCH_SIZE:
            cursor.executemany(insert_sql, batch)
            conn.commit()

            total_rows += len(batch)
            batch.clear()

            print(f"Inserted: {total_rows:,} rows")

if batch:
    cursor.executemany(insert_sql, batch)
    conn.commit()
    total_rows += len(batch)

print(f"Inserted: {total_rows:,} rows")

print("Creating indexes...")

cursor.execute("""
CREATE INDEX idx_timestamp
ON transactions(timestamp)
""")

cursor.execute("""
CREATE INDEX idx_from_account
ON transactions(from_account)
""")

cursor.execute("""
CREATE INDEX idx_to_account
ON transactions(to_account)
""")

cursor.execute("""
CREATE INDEX idx_laundering
ON transactions(is_laundering)
""")

conn.commit()

db_rows = cursor.execute(
    "SELECT COUNT(*) FROM transactions"
).fetchone()[0]

conn.close()

print()
print("Database created successfully.")
print(f"Database: {DB_FILE}")
print(f"Rows: {db_rows:,}")