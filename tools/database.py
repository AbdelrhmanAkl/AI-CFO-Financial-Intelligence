import gzip
import os
import shutil
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


DB_NAME = os.getenv(
    "DATABASE_NAME",
    "financial.db",
)

DB_PATH = DATA_DIR / DB_NAME
GZ_PATH = DATA_DIR / f"{DB_NAME}.gz"


def ensure_database():
    if DB_PATH.exists():
        return

    if not GZ_PATH.exists():
        raise FileNotFoundError(
            f"Database file not found: {DB_PATH}"
        )

    print(f"Extracting database: {GZ_PATH.name}")

    with gzip.open(GZ_PATH, "rb") as source:
        with open(DB_PATH, "wb") as target:
            shutil.copyfileobj(source, target)

    print(f"Database extracted: {DB_PATH}")


def get_connection():
    ensure_database()
    return sqlite3.connect(DB_PATH)


def execute_query(query: str, params=()):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        return columns, rows

    finally:
        connection.close()