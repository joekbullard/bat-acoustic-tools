import logging
from pathlib import Path


def find_file(file_name: str, directory: Path)  -> Path | None:
    """
    Recursively searches for a file within a given directory and its subdirectories.

    Args:
        file_name (str): The name of the file to search for.
        directory (Path): The root directory to start the search.

    Returns:
        Path | None: The `Path` object of the first matching file found, or `None` if no match is found.
    """
    for file_path in directory.rglob(file_name):  # Search recursively
        return file_path  # Return the first match
    return None  # File not found

def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )