import maya.cmds as mc
import os
import json

import config
import jsonReader
reload(jsonReader)
reload(config)

def sceneData(shotListView):
    channels = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
    shotPath = getShotpath(shotListView)
    setsGroup = "SETS"


    # get shot data if exists
    if os.path.isfile(shotPath + "sceneData.json"):
        shotData = jsonReader.jsonRead(shotPath + "sceneData.json")

    setChild = mc.listRelatives(setsGroup, children=True)

    for item in setChild:
        if not "instance" in item:
            assetName = item.split(":")[0]
            transformData = []
            data = []
            for i in channels:
                data.append(mc.getAttr(item + "." + i))
            transformData.append(data)

            shotData[assetName] = {"transform": transformData}
        else:
            assetName = item.split(":")[0]
            transformData = shotData[assetName]["transform"]

            data = []
            for i in channels:
                data.append(mc.getAttr(item + "." + i))
            transformData.append(data)

            shotData[assetName] = {"transform": transformData}

    # write out data
    if not os.path.exists(shotPath):
        os.makedirs(shotPath)

    filename = shotPath + "sceneData.json"
    jsonData = json.dumps(shotData, indent=4)
    fd = open(filename, 'w')
    fd.write(jsonData)
    fd.close()

    print "sceneData.json was saved to %s" %shotPath,

def getShotpath(shotListView):
    shotName = shotListView.currentItem().text()
    shotsRootFolder =config.rootFolder
    shotPath = shotsRootFolder + shotName + "/_shotData/"

    return shotPath

def getAssetPath(assetName):
    fbxLibPath = "s:/projects/SnowQueen/lib/_fbx/SETS/"
    return fbxLibPath + assetName + ".fbx"