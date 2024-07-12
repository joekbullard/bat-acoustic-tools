import sqlite3
import argparse
import logging
import sys
import time
from batdetect2 import api
from db.utils import create_schema, table_exists, record_exists
from typing import Optional, Tuple
from guano import GuanoFile
from pathlib import Path

"""
Process wav directory using BatDetect2
DO NOT RUN THIS FROM D Drive, it will be painfully slow
Instead copy to SSD directory and run there
"""

INSERT_ANNOTATION = """
                    INSERT INTO annotations(record_id, start_time, end_time, low_freq, high_freq, spp_class, class_prob, det_prob, individual, event)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

INSERT_RECORD = """INSERT INTO records(file_name, location_id, serial, record_time, duration, class_name)
                    VALUES(?, ?, ?, ?, ?, ?)"""


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "directory", help="Path to directory containing WAV files", type=str
    )

    parser.add_argument(
        "location_id",
        help="Alphanumeric detector code, e.g GC01, refer to AGOL featurelayer",
        type=str,
    )

    parser.add_argument(
        "-d",
        "--db_path",
        help="Path to output sqlite3 database, defaults to sqlite3.db",
        default="./sqlite3.db",
        type=str,
    )

    parser.add_argument(
        "-t",
        "--threshold",
        help="Detection threshold - a value from 0 to 1, defaults to 0.5",
        default=0.5,
        type=float,
    )
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_arguments()
    wav_directory = args.directory
    location_id = args.location_id
    db_path = args.db_path
    threshold = args.threshold

    conf = api.get_config(
        detection_threshold=threshold,
        chunk_size=5,
        target_samp_rate=384000,
        min_freq_hz=16000,
    )

    audio_files = api.list_audio_files(wav_directory)

    audio_array_length = len(audio_files)

    if audio_array_length == 0:
        logging.error("WAV directory is empty, exiting script")
        sys.exit()

    if not table_exists(db_path):
        logging.info("No database schema identified, creating new schema")
        create_schema()
    else:
        logging.info("Database schema exists")

    with sqlite3.connect(db_path) as conn:
        conn.commit()

        for count, f in enumerate(audio_files, start=1):
            logging.info(f"Processing file {count} of {audio_array_length}")

            file_path = Path(f)

            if record_exists(conn, file_path.name):
                logging.info("Record already exists in database, moving to next record")
                continue

            guano_file = GuanoFile(f)
            processed = api.process_file(f, config=conf)

            record = processed["pred_dict"]

            record_values = (
                record["id"],
                location_id,
                guano_file["Serial"],
                guano_file["Timestamp"],
                record["duration"],
                record["class_name"],
            )

            last_row_id = execute_query(conn, INSERT_RECORD, record_values)

            if len(record["annotation"]) > 0:
                rows = [
                    (
                        last_row_id,
                        annotation["start_time"],
                        annotation["end_time"],
                        annotation["low_freq"],
                        annotation["high_freq"],
                        annotation["class"],
                        annotation["class_prob"],
                        annotation["det_prob"],
                        annotation["individual"],
                        annotation["event"],
                    )
                    for annotation in record["annotation"]
                ]

                executemany_query(conn, INSERT_ANNOTATION, rows)

            conn.commit()


if __name__ == "__main__":
    main()
