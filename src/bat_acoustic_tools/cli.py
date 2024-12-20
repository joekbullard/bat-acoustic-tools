# TODO This should be the entrypoint for the app to be used through comnand line like `process_wav ...`
import typer
from pathlib import Path
from typing_extensions import Annotated, Optional
from bat_acoustic_tools import process_wavs, backup_wavs

app = typer.Typer(help="Manage bat bioacoustic wav files")


@app.command("analyse")
def process_wav_cli(
    directory: Annotated[
        Optional[Path],
        typer.Argument(
            help="Path to directory containing WAV files",
            exists=True,
            resolve_path=True,
        ),
    ],
    db_path: Annotated[
        Optional[Path],
        typer.Option(
            "--db-path",
            "-d",
            help="Path to output sqlite3 database, defaults to sqlite3.db",
            exists=True,
            resolve_path=True,
        ),
    ] = Path.cwd() / "sqlite3.db",
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            min=0,
            max=1,
            help="BatDetect2 Detection threshold, a value from 0 to 1, defaults to 0.5",
        ),
    ] = 0.5,
):
    process_wavs.main(wav_directory=directory, db_path=db_path, threshold=threshold)


@app.command('backup')
def backup_wavs_cli(
    wav_directory: Annotated[
        Optional[Path],
        typer.Argument(
            help=r"Path to root directory containing WAV files, e.g. 'D:\Goblin Combe - Bat Data\2024\Deployments'",
            exists=True,
            resolve_path=True,
        ),
    ],
    backup_directory: Annotated[
        Optional[Path],
        typer.Argument(
            help=r"Path to root directory to store FLAC files, e.g. 'H:\Goblin Combe - Bat Data\2024'",
            exists=True,
            resolve_path=True
        )
    ],
    db_path: Annotated[
        Optional[Path],
        typer.Option(
            "--db-path",
            "-d",
            help="Path to output sqlite3 database, defaults to sqlite3.db",
            exists=True,
            resolve_path=True,
        ),
    ] = Path.cwd() / "sqlite3.db",
    sql: Annotated[
        str,
        typer.Option(
            "--sql",
            "-s",
            help="SQL query used to create list of file names, must return file_name and record_path fields", 
        )
    ] = "select file_name, record_path from records where class_name = 'None' and backup = 'no' and record_path not NULL"
): 
    backup_wavs.main(wav_directory=wav_directory, flac_directory=backup_directory, db_path=db_path, sql_query=sql)
    

if __name__ == "__main__":
    app()
