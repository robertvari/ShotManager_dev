import os
import json
import config
reload(config)

def findCategory(assetName):
    assetPaths = config.assetPaths

    with open(assetPaths) as data_file:
        scenesData = json.load(data_file)

    for key, value in scenesData.iteritems():
        subfolders = os.listdir(value)

        if assetName in subfolders:
            if "CAST" in value: category = "CAST"
            if "SETS" in value: category = "SETS"
            if "PROPS" in value: category = "PROPS"

    return category