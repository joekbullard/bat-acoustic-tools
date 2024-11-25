import ffmpeg
import sqlite3
from pathlib import Path
import logging
import argparse
from utils import find_file, setup_logging

"""
This script:

- Pulls out a list of file names from SQLite database
- The list of files to extract can be customised using SQL query (-s/--sql flag) or use default values
- The default query selects all files that haven't been backed up, aren't from CM and have a class_name of 'None'
- The program iterates over list of file names and searches for each file in specified directory
- When file is found, the file is converted to FLAC using ffmpeg and saved in specified directory
- Original wav file is deleted at the end
"""


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "wav_directory",
        help="Path to root directory containing WAV files, e.g. 'D:\Goblin Combe - Bat Data\2024\Deployments'",
        type=str,
    )

    parser.add_argument(
        "flac_directory",
        help="Path to root directory to store FLAC files, e.g. 'H:\Goblin Combe - Bat Data\2024'",
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
        "-s",
        "--sql",
        help="SQL query used to create list of file names, must return a single field of valid filenames",
        default="select file_name from records where class_name = 'None' and backup = 'no' and location_id <> 'CM'",
        type=str,
    )

    return parser.parse_args()


def create_flac_path(wav_file: Path, flac_root: Path) -> Path:
    """
    Creates a directory structure under `flac_root` based on the WAV file path and
    returns the full path for the corresponding FLAC file.

    Args:
        wav_file (Path): Path to the source WAV file.
        flac_root (Path): Root directory for the FLAC file structure.

    Returns:
        Path: Path to the FLAC file to be created.
    """
    wav_path_parts = wav_file.parts
    deployment_date = wav_path_parts[-4]
    location_id = wav_path_parts[-3]

    flac_dir = flac_root / deployment_date / location_id / "data"
    flac_dir.mkdir(parents=True, exist_ok=True)

    return flac_dir / (wav_file.stem + ".flac")


if __name__ == "__main__":
    setup_logging()
    args = parse_arguments()
    wav_directory = Path(args.wav_directory)
    flac_directory = Path(args.flac_directory)
    db_path = Path(args.db_path)
    sql_query = args.sql

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(sql_query)

        results = cur.fetchall()
        result_count = len(results)

        logging.info(f"{result_count} files to be backed up")

        for count, result in enumerate(results, 1):
            file_name = result[0]

            logging.info(
                f"Backing up file {count} of {result_count} ({round((count/result_count) * 100, 1)}%) - File name: {file_name}"
            )
            wav_file_path = find_file(file_name, wav_directory)

            if wav_file_path is not None:
                backup_path = create_flac_path(wav_file_path, flac_directory)
                try:
                    ffmpeg.input(str(wav_file_path)).output(
                        str(backup_path),
                        audio_bitrate="6144k",
                        acodec="flac",
                        ar=384000,
                        map_metadata=0,
                        loglevel="quiet",
                    ).run()

                    cur2 = conn.cursor()
                    cur2.execute(
                        "update records set backup = 'yes', backup_path = ? where file_name = ?",
                        (str(backup_path), file_name),
                    )
                    logging.info(f"Backup of {file_name} complete - deleting WAV file")

                    if count % 10 == 0:
                        conn.commit()

                    wav_file_path.unlink()

                except ffmpeg._run.Error:
                    logging.error(
                        f"Error converting {file_name} to FLAC, continuing to next file"
                    )
            else:
                logging.info(f"{file_name} not found in {str(wav_directory)}")
