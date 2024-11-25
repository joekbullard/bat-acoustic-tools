# AWT Bat Data Processing

## Introduction
Toolset to process, analyse and manage bat acoustic sounds files gathered used Wildlife Acoustics SM Mini static detectors. Uses the BatDetect2 library, the outputs (records and annotations) are saved into an SQLite database.

## Table of Contents
- [Key Features](#key-features)
- [Installation Instructions](#installation-instructions)
- [Usage Instructions](#usage-instructions)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Examples](#examples)

## Key Features
The repo contains scripts to be used at the command line to process and manage acoustic bat data (WAV files). 

`process_wavs` uses BatDetect2 to analyse wav files in a given directory. The analysis outputs are stored in an SQLite database using a 1:N related table schema - `records` for file level information and `annotations` for individual call level information, for more details refer to [BatDetect2](https://github.com/macaodha/batdetect2).

`wav_to_flac` handles conversion of WAV files to FLAC to reduce storage footprint. Note that bat acoustic metadata (guano) will be lost through conversion. However, important (timestamp, location) metadata is retained within the SQLite database `records` table. Conversion to FLAC typically reduces file size by 30-70% when compared to WAV. Flac is lossless so if required, the file can be converted back to WAV for analysis or further processing. Conversion is handled by ffmpeg-python - note you will need to have ffmpeg installed on your machine in order to install the library.

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
python process_wavs.py "path/to/directory"
```
### Example Usage
```bash
python process_wavs.py "D:\Goblin Combe - Bat Data\2024\Deployments\2024-05-28\GC17\Data"
```

## Dependencies
* Python (version > 3.8 and <= 3.10)
* BatDetect2
* guano
