# AWT Bat Data Processing

## Introduction
AWT Bat Data Processing scans a directory and processes WAV files recorded from static bat detectors using the BatDetect2 library. The outputs (records and annotations) are saved into an SQLite database.

## Table of Contents
- [Key Features](#key-features)
- [Installation Instructions](#installation-instructions)
- [Usage Instructions](#usage-instructions)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Examples](#examples)

## Key Features
- **Feature 1**: Given path to WAV directory, iterates over WAV files and processes each file in turn.
- **Feature 2**: Output is stored in SQLite3 database.
- **Feature 3**: Database and schema will be created if it doesn't exist.

## Installation Instructions
1. Ensure you have Python version > 3.8 and <= 3.10 installed.
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```
3. Install the required packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage Instructions
To use the script, run the following command:
```bash
python wav_to_sqlite.py "path/to/directory"
```
### Example Usage
```bash
python wav_to_sqlite.py "D:\Goblin Combe - Bat Data\2024\Deployments\2024-05-28\GC17\Data"
```

## Dependencies
* Python (version > 3.8 and <= 3.10)
* BatDetect2
* guano
