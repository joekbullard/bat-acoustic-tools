import logging
import time
import sqlite3
from pathlib import Path
from typing import Optional, Tuple


def table_exists(dbpath: str = "./sqlite3.db") -> bool:
    with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
            """,
            ("records",),
        )

        exists = cur.fetchone() is not None

        return exists


def create_schema(dbpath: str) -> None:
    with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            file_name TEXT UNIQUE,
            location_id TEXT,
            serial TEXT,
            record_time TIMESTAMP,
            duration FLOAT,
            class_name TEXT,
            recording_night DATE,
            validated TEXT,
            id_correct TEXT,
            comments TEXT,
            backup TEXT,
            backup_path TEXT,
            record_path TEXT   
            )"""
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY,
            record_id INTEGER,
            start_time FLOAT,
            end_time FLOAT,
            low_freq INTEGER,
            high_freq INTEGER,
            spp_class TEXT,
            class_prob FLOAT,
            det_prob FLOAT,
            individual INTEGER,
            event TEXT,
            FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
            )"""
        )

        conn.commit()


def record_exists(conn: sqlite3.Connection, record_id: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        "select exists (select file_name from records where file_name = ?)",
        (record_id,),
    )
    exists = cur.fetchone()[0]

    return exists


def executemany_query(
    connection: sqlite3.Connection, query: str, params: Optional[Tuple] = None
) -> None:
    """
    This is a recursive function that works around issues with SQLite locking of database.
    """
    cur = connection.cursor()
    try:
        cur.executemany(query, params)
        connection.commit()
    except sqlite3.OperationalError as e:
        # Handle potential lock issues
        connection.rollback()
        logging.error(f"SQLite Operational Error: {e}. Retrying in 100ms...")
        time.sleep(0.1)
        executemany_query(connection, query, params)
    finally:
        cur.close()


def execute_query(
    connection: sqlite3.Connection, query: str, params: Optional[Tuple] = None
) -> Optional[int]:
    """
    Execute a SQL query on the provided SQLite database connection.

    Parameters:
    - connection (sqlite3.Connection): A SQLite database connection obtained using sqlite3.connect().
    - query (str): The SQL query to execute.
    - params (tuple, optional): Parameters to substitute into the query if it is a parameterized query.
                                 Default is None.

    Returns:
    - None

    Notes:
    - This function executes the provided SQL query on the given SQLite database connection.
    - If the query is a parameterized query, the params argument should be provided as a tuple
      containing the parameter values.
    - The function retries the query execution in case of an sqlite3.OperationalError, which may
      indicate a locking issue. It waits for a short duration (0.1 seconds by default) before
      retrying the operation.
    - The function may raise exceptions other than sqlite3.OperationalError if there are other issues
      with the query execution, such as syntax errors or integrity constraints violations.
    - It is the caller's responsibility to handle any exceptions raised by this function.

    Example:
    ```
    connection = sqlite3.connect("example.db")
    query = "INSERT INTO my_table (column1, column2) VALUES (?, ?)"
    params = ("value1", "value2")
    execute_query(connection, query, params)
    ```
    """
    cur = connection.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        connection.commit()

        if query.strip().lower().startswith("insert"):
            return cur.lastrowid
        else:
            return None
    except sqlite3.OperationalError as e:
        # Handle potential lock issues
        connection.rollback()
        logging.error(f"SQLite Operational Error: {e}. Retrying in 100ms...")
        time.sleep(0.1)
        execute_query(connection, query, params)
    finally:
        cur.close()


def is_valid_sqlite_file(sqlitedb_path: Path) -> bool:
    if sqlitedb_path.exists():
        try:
            # Attempt to connect to the SQLite database
            with sqlite3.connect(sqlitedb_path) as conn:
                # Try a simple query to verify if it's a valid SQLite file
                conn.execute("SELECT 1;")
            return True
        except sqlite3.DatabaseError:
            return False
    return False