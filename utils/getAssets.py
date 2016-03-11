import json
import os
import config
reload(config)

def getAssets():
    assetPaths = config.assetPaths
    with open(assetPaths) as data_file:
        scenesData = json.load(data_file)

    assetList = []
    for key, value in scenesData.iteritems():
        subfolders = os.listdir(value)
        if subfolders:
            for i in subfolders:
                assetList.append(i)

    return assetList