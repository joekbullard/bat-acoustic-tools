import logging
import time
import sqlite3
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


def create_schema(dbpath: str = "./sqlite3.db") -> None:
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
            record_night DATE,
            duration FLOAT,
            class_name TEXT
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