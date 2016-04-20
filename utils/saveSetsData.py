import maya.cmds as mc
import os
import json

import config
import jsonReader
reload(jsonReader)
reload(config)

def sceneData(shotListView):
    channels = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
    shotData = {}
    shotPath = getShotpath(shotListView)

    setsGroup = "SETS"

    # get shot data if exists
    if os.path.isfile(shotPath + "sceneData.json"):
        shotData = jsonReader.jsonRead(shotPath + "sceneData.json")

    print shotData

    setChild = mc.listRelatives(setsGroup, children=True)

    for i in setChild:
        mc.select(i, add=True)

    selection = mc.ls(sl=True)

    mc.select(cl=True)

    for item in selection:
        referenceFile = mc.referenceQuery(mc.referenceQuery(item, rfn=True), filename=True)
        assetName = referenceFile.replace("_MASTER.mb", "")
        assetName = assetName.split("/")[-1]
        channelData = []
        for i in channels:
            channelData.append(mc.getAttr(item + "." + i))
            shotData[assetName] = {"transform": channelData, "path":getAssetPath(assetName)}

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