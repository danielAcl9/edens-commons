import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "eden_commons.db")

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)
