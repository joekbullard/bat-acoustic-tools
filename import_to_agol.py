import os
import sqlite3
import logging
import sys
from arcgis.gis import GIS
import datetime
from zoneinfo import ZoneInfo
import tempfile
import csv
import uuid


def find_globalid(serial_dict, serial, timestamp):
    # Ensure the serial exists in the dictionary
    if serial not in serial_dict:
        return None

    # Iterate over the list of dictionaries for the given serial number
    for entry in serial_dict[serial]:
        # Convert the start and end dates to datetime objects
        start_date = entry["start_date"]
        end_date = entry["end_date"]

        # Check if the timestamp is within the range
        if start_date <= timestamp <= end_date:
            return entry["globalid"]

    # Return None if no matching entry is found
    return None


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


# import user variables - make sure these are configured beforehand
agol_user = os.environ.get("AGOL_USER")
agol_pass = os.environ.get("AGOL_PASS")
agol_url = os.environ.get("AGOL_URL")
uk_tz = ZoneInfo("Europe/London")

setup_logging()

try:
    logging.info("Connecting to AGOL portal")
    gis = GIS(agol_url, agol_user, agol_pass)
    logging.info("Connection successful")
except Exception as e:
    logging.error(e)
    logging.info("Chgeck credentials, ending script")
    sys.exit()
# work flow

# get deployments from AGOL and create dict with code, start/end date and globalID

logging.info("Downloading deployments table from AGOL portal")
layer_item = gis.content.get("f57426d99cd04797a9d778465824c3b8")
deployment_table = layer_item.tables[0]
passes_table = layer_item.tables[1]
features = deployment_table.query(
    where="end_date IS NOT NULL AND end_date <> ''"
).features
logging.info("Download successful")


logging.info("Generating deployment dictionary")
deployment_dict = {}

for feat in features:
    attributes = feat.attributes
    serial = attributes["serial"]

    start_date = datetime.datetime.fromtimestamp(
        attributes["start_date"] / 1000
    ).replace(tzinfo=uk_tz)
    end_date = datetime.datetime.fromtimestamp(attributes["end_date"] / 1000).replace(
        tzinfo=uk_tz
    )
    globalid = attributes["GlobalID"]

    dep = {"start_date": start_date, "end_date": end_date, "globalid": globalid}

    if serial in deployment_dict:
        deployment_dict[serial].append(dep)
    else:
        deployment_dict[serial] = [dep]

logging.info("Deployment dictionary generated")

with sqlite3.connect("./sqlite3.db") as conn:
    loc_query = "SELECT serial FROM records GROUP BY serial"

    cursor = conn.cursor()

    cursor.execute(loc_query)

    serial_numbers = cursor.fetchall()

    logging.info("Creating features to import")

    features = []

    for serial_number in serial_numbers:
        sn = serial_number[0]
        logging.info(f"{sn}")

        cursor = conn.cursor()

        cursor.execute(
            """
                       SELECT record_time, file_name, duration, recording_night, class_name, location_id  FROM records WHERE serial = ? AND class_name <> 'None'
                       """,
            (sn,),
        )
        records = cursor.fetchall()

        for record in records:
            record_time = datetime.datetime.fromisoformat(record[0])
            file_name = record[1]
            duration = record[2]
            recording_night = record[3]
            class_name = record[4]
            location_id = record[5]
            guid = find_globalid(deployment_dict, sn, record_time)

            record_dict = {
                "deployment_guid": guid,
                "timestamp": record_time.isoformat(),
                "file_name": file_name,
                "duration": duration,
                "recording_night": recording_night,
                "class_name": class_name,
                "location_id": location_id,
            }

            features.append(record_dict)

        logging.info(f"FeatureSet generated for {sn}")

logging.info("Creating temporary csv file")

with tempfile.NamedTemporaryFile(delete=False, newline="", suffix=".csv") as tmp_csv:
    headers = features[0].keys()
    writer = csv.DictWriter(tmp_csv, fieldnames=headers)

    writer.writeheader()
    writer.writerows(features)

    temp_file_name = tmp_csv.name

item_properties = {
    "title": "temp_csv_" + uuid.uuid4().hex[:7],
    "tags": "temp",
    "description": "temp",
    "type": "CSV",
}

logging.info("Uploading CSV file to AGOL Portal")
upload_item = gis.content.add(item_properties, temp_file_name)
logging.info("CSV uploaded")
logging.info("Obtaining analyze parameters for uploaded CSV")
analyze_param = gis.content.analyze(item=upload_item.id)

logging.info("Appending data to Passes table")
fields = [
    "deployment_guid",
    "timestamp",
    "file_name",
    "duration",
    "recording_night",
    "class_name",
    "location_id",
]
result = passes_table.append(
    item_id=upload_item.id,
    upload_format="csv",
    rollback=True,
    append_fields=fields,
    source_info=analyze_param,
)

# if result["addResults"]:
#     logging.info("Bulk insert successful!")
#     for add_result in result["addResults"]:
#         if add_result["success"]:
#             logging.info(f"Added ObjectID: {add_result['objectId']}")
#         else:
#             logging.info(f"Failed to add row: {add_result['error']}")
# else:
#     logging.info("No rows were added.")

logging.info("Complete, tidying up")

logging.info("Deleting CSV from AGOL")
upload_item.delete()

logging.info("Deleting temp file")
os.remove(temp_file_name)
