import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_NAME = os.getenv(
    "DATABASE_NAME",
    "financial.db",
)

DB_PATH = BASE_DIR / "data" / DB_NAME


def get_connection():
    return sqlite3.connect(DB_PATH)


def execute_query(query: str, params=()):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return columns, rows

    finally:
        connection.close()