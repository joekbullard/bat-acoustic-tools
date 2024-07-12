import os
import sqlite3
from arcgis.gis import GIS
from arcgis.features import Table


db_path = r"D:\Goblin Combe - Bat Data\2024\processing tools\sqlite3.db"

# import user variables - make sure these are configured beforehand
agol_user = os.environ.get('AGOL_USER')
agol_pass = os.environ.get('AGOL_PASS')
agol_url = os.environ.get('AGOL_URL')

gis = GIS(agol_url, agol_user, agol_pass)

# work flow

# get deployments from AGOL and create dict with code, start/end date and globalID
layer_item = gis.content.get('f57426d99cd04797a9d778465824c3b8')

feature_layer = layer_item.tables[0]

features = feature_layer.query().features

deployment_list = []

for feat in features:
    dep_feat = dict(
        
    )
# iterate over records in sqlite database

# for each record, assign to correct globalID

# create new feature and add to feature layer
