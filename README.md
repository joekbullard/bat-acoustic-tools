# AWT Bat Data Processing

## Introduction
Toolset to process, analyse and manage bat acoustic sounds files gathered used Wildlife Acoustics SM Mini static detectors. Uses the BatDetect2 library, the outputs (records and annotations) are saved into an SQLite database.

## Table of Contents
- [Key Features](#key-features)
- [Installation Instructions](#installation-instructions)
- [Usage Instructions](#usage-instructions)
- [Dependencies](#dependencies)
- [Examples](#examples)

## Key Features
The repo contains scripts to be used at the command line to process and manage acoustic bat data (WAV files). 

`process_wavs.py` uses BatDetect2 to analyse wav files in a given directory. The analysis outputs are stored in an SQLite database using a 1:N related table schema - `records` for file level information and `annotations` for individual call level information, for more details refer to [BatDetect2](https://github.com/macaodha/batdetect2).

Example `record` output:

| id	| file_name |	location_id | record_time | class_name | recording_night |
|-------|-----------|---------------|-------------|------------|-----------------|
| 15181	| SMU01770-2_20240406_230356.wav | GC01 | 2024-04-06 23:03:56+01:00	|Rhinolophus hipposideros | 06/04/2024 |



`process_wavs.py` handles conversion of WAV files to FLAC to reduce storage footprint. Note that bat acoustic metadata (guano) will be lost through conversion. However, important (timestamp, location) metadata is retained within the SQLite database `records` table. 

`backup_wavs.py` handles backup of WAV file to FLAC format using ffmpeg. The default setting takes all files that are noise and not currently backed up. The script generates a replica folder structure. Conversion to FLAC typically reduces file size by 30-70% when compared to WAV. Flac is lossless so if required, the file can be converted back to WAV for analysis or further processing. Conversion is handled by ffmpeg-python - note you will need to have ffmpeg installed on your machine in order to install the library.

`utils.py` has a number of utilitiy functions that are used across the various other tools

TODO `import_to_agol.py`

## Installation Instructions
1. Ensure you have Python version > 3.8 and <= 3.10 installed.
2. Navigate to folder on your machine where you want to store the repo and clone, e.g. `git clone git@github.com:joekbullard/Bat-Data-Processing.git` 
3. `cd` into repo `cd Bat-Data-Processing`
4. Create and activate a virtual environment:
    `python -m venv venv`
    On linux use `source venv/bin/activate`   
    On Windows use `venv\Scripts\activate`
   
5. With the virtual environment active, install the required packages using the `requirements.txt` file:
    `python -m pip install -r requirements.txt`

## Usage Instructions
To use the script, run the following command:
```bash
python -m bat_acoustic_tools backup -h
```
### Example Usage
```bash
python -m bat_acoustic_tools analyse "D:\Goblin Combe - Bat Data\2024\Deployments\2024-05-28\GC17\Data"
```


## Dependencies
* Python (version > 3.8 and <= 3.10)
* BatDetect2
* guano
* ffmpeg-python (Note system install of ffmpeg required)
