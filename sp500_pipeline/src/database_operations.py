# src/database_operations.py
import sqlite3
from typing import Optional
import pandas as pd
import logging
import os

from . import config

logger = logging.getLogger(__name__)
# BasicConfig for logger is usually set in the main entry point (main_pipeline.py)

def create_connection(db_path: str) -> Optional[sqlite3.Connection]:
    """
    Establishes a connection to the SQLite database specified by db_path.
    Creates the directory for the database file if it doesn't exist.
    """
    conn: Optional[sqlite3.Connection] = None
    try:
        # Ensure the parent directory for the database file exists
        db_dir = os.path.dirname(db_path)
        if db_dir: # Only create if db_path includes a directory
            os.makedirs(db_dir, exist_ok=True)
            
        conn = sqlite3.connect(db_path)
        logger.info(f"Successfully connected to SQLite database: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"SQLite error when connecting to {db_path}: {e}")
        return None
    except OSError as e: # Catch OS errors like permission issues for makedirs
        logger.error(f"OS error when creating directory for {db_path}: {e}")
        return None


def save_data_to_db(df: pd.DataFrame, conn: sqlite3.Connection, table_name: str):
    """
    Saves the provided DataFrame to a specified table in the SQLite database.
    If the table already exists, it will be replaced.
    """
    if df.empty:
        logger.warning(f"DataFrame is empty. No data saved to table '{table_name}'.")
        return

    try:
        # Using 'replace' ensures the table is overwritten if it exists,
        # making the operation idempotent for a given DataFrame.
        # 'index=False' prevents pandas DataFrame index from being written to the table.
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        logger.info(f"Successfully saved {len(df)} rows to table '{table_name}' in the database.")
    except (pd.io.sql.DatabaseError, sqlite3.Error, Exception) as e: # Broader exception catch for to_sql
        logger.error(f"Error saving DataFrame to table '{table_name}': {e}")

# The optional comment about CREATE TABLE is fine as it explains a design choice.