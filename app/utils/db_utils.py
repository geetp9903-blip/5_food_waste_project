import sqlite3
import pandas as pd

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "database", "food_waste.db")

def get_db_connection():
    """Establishes a connection to the SQLite database with row factory enabled."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def execute_query(query, params=()):
    """Executes a read query and returns a Pandas DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Database error on read: {e}")
        raise e
    finally:
        conn.close()

def execute_dml(query, params=()):
    """Executes a Data Manipulation Language (DML) statement (INSERT, UPDATE, DELETE)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Database error on write: {e}")
        raise e
    finally:
        conn.close()

def execute_dml_returning_rowcount(query, params=()):
    """Executes a DML statement and returns the number of affected rows."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        print(f"Database error on write (rowcount): {e}")
        raise e
    finally:
        conn.close()
