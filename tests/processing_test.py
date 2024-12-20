import sqlite3
from pathlib import Path
import pytest
from src.bat_acoustic_tools.process_wavs import (
    executemany_query,
    execute_query,
    INSERT_ANNOTATION,
    INSERT_RECORD,
)
from src.bat_acoustic_tools.db.utils import RECORDS, ANNOTATIONS


@pytest.fixture
def temp_db(tmpdir):
    db_path = tmpdir / "test_db.sqlite3"

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(RECORDS)
    cursor.execute(ANNOTATIONS)
    conn.commit()

    yield conn

    conn.close()
    Path(db_path).unlink()


def test_insert_record(temp_db):
    cur = temp_db.cursor()

    record_values = (
        "test_file.wav",
        "GC01",
        "test_serial",
        "2024-08-25 02:00:25+01:00",
        3.1,
        "class_name",
        "2024-08-24",
        "no",
        None,
        None,
        "no",
        None,
        r"D:\Goblin Combe - Bat Data\2024\Deployments\2024-08-06\BW31\Data\SMU12567_20240825_020025.wav",
    )

    record_id = execute_query(temp_db, INSERT_RECORD, record_values)

    cur.execute("SELECT * FROM records WHERE id=?", (1,))
    record = cur.fetchone()
    assert record_id is not None
    assert record[1::] == record_values


def test_insert_annotations(temp_db):
    cur = temp_db.cursor()

    record_values = (
        "test_file.wav",
        "GC01",
        "test_serial",
        "2024-08-25 02:00:25+01:00",
        3.1,
        "class_name",
        "2024-08-24",
        "no",
        None,
        None,
        "no",
        None,
        r"D:\Goblin Combe - Bat Data\2024\Deployments\2024-08-06\BW31\Data\SMU12567_20240825_020025.wav",
    )

    record_id = execute_query(temp_db, INSERT_RECORD, record_values)

    annotations = [
        (record_id, 0.0, 1.0, 16000, 20000, "species", 0.9, 0.8, 1, "event1"),
        (record_id, 1.5, 2.5, 16000, 20000, "species", 0.9, 0.8, 1, "event2"),
    ]

    executemany_query(temp_db, INSERT_ANNOTATION, annotations)

    cur.execute(
        "SELECT record_id, start_time, end_time, low_freq, high_freq, spp_class, class_prob, det_prob, individual, event FROM annotations WHERE record_id=?",
        (record_id,),
    )

    rows = cur.fetchall()
    assert len(rows) == 2
    assert rows == annotations
