import sqlite3
import os
import logging
import argparse
from pathlib import Path
from db.utils import is_valid_sqlite_file


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("db_query", help="Enter SQL query", type=str)

    parser.add_argument(
        "target_directory", help="Path to directory containing WAV files", type=str
    )

    parser.add_argument(
        "-d",
        "--db_path",
        help="Path to output sqlite3 database, defaults to sqlite3.db",
        default="./sqlite3.db",
        type=str,
    )

    return parser.parse_args()


def main():
    setup_logging()
    args = parse_arguments()
    db_query = args.db_query
    target_dir = Path(args.target_directory)
    db_path = Path(args.db_path)

    try:
        # Attempt to parse the SQL query using sqlite3's internal parser
        sqlite3.complete_statement(db_query)

        if is_valid_sqlite_file(sqlitedb_path=db_path):
            logging.info("Connection made to sqlite3 database")
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row

                cursor = conn.cursor()
                cursor.execute(db_query)
                records = cursor.fetchall()

                if len(records) > 0:
                    logging.info(f"Query returned {len(records)} records")

                    target_dir.mkdir(parents=True, exist_ok=True)

                    for record in records:
                        record_dict = dict(record)

                        file_name = record_dict["file_name"]
                        data_dir_path = Path("D:\Clapton Moor - Bat Data\CM")

                        for file in data_dir_path.rglob(file_name):
                            target_path = target_dir / file_name

                            try:
                                # Convert Path objects to strings for os.symlink
                                os.link(str(file), str(target_path))
                                logging.info(
                                    f"Created hardlink: {target_path} -> {file}"
                                )
                            except FileExistsError:
                                logging.error(f"Symlink already exists: {target_path}")
                            except OSError as e:
                                logging.error(
                                    f"Error creating hardlink for {file}: {e}"
                                )

                else:
                    logging.info("Query returned no values, exiting script")

        else:
            logging.warning("Invalid sqlite.db path")

    except sqlite3.DatabaseError as e:
        # If a DatabaseError is caught, the query is invalid
        logging.error("Invalid SQL query")
        raise argparse.ArgumentTypeError(f"Invalid SQL query: {e}")


if __name__ == "__main__":
    main()
