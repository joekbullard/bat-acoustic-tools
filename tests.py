import unittest
import sqlite3
import tempfile
import os
from wav_to_sqlite import executemany_query, execute_query, create_timestamp, INSERT_ANNOTATION, INSERT_RECORD

class TestDatabaseFunctions(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary file-based SQLite database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        
        # Create tables
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            file_name TEXT UNIQUE,
            location_id TEXT,
            serial TEXT,
            record_time TIMESTAMP,
            duration FLOAT,
            class_name TEXT
            )"""
        )
        self.cur.execute(
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
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_timestamp(self):
        filename = "SMU01770_20220514_123456.wav"
        expected_timestamp = "2022-05-14 12:34:56"
        self.assertEqual(create_timestamp(filename), expected_timestamp)

    def test_execute_query(self):
        record_values = (
            "test_file.wav",
            "GC01",
            "test_serial",
            "2022-05-14 12:34:56",
            60.0,
            "class_name"
        )
        record_id = execute_query(self.conn, INSERT_RECORD, record_values)
        self.assertIsNotNone(record_id)
        
        self.cur.execute("SELECT * FROM records WHERE id=?", (record_id,))
        record = self.cur.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record[1], "test_file.wav")

    def test_executemany_query(self):
        record_values = (
            "test_file.wav",
            "GC01",
            "test_serial",
            "2022-05-14 12:34:56",
            60.0,
            "class_name"
        )
        record_id = execute_query(self.conn, INSERT_RECORD, record_values)
        
        annotations = [
            (record_id, 0.0, 1.0, 16000, 20000, "species", 0.9, 0.8, 1, "event1"),
            (record_id, 1.0, 2.0, 16000, 20000, "species", 0.9, 0.8, 1, "event2")
        ]
        executemany_query(self.conn, INSERT_ANNOTATION, annotations)
        
        self.cur.execute("SELECT * FROM annotations WHERE record_id=?", (record_id,))
        rows = self.cur.fetchall()
        self.assertEqual(len(rows), 2)

if __name__ == "__main__":
    unittest.main()
