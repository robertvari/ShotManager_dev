import maya.cmds as mc
import os
import jsonReader
import config

def getShotFolder(shotListView):
    shotNumber = shotListView.currentItem().text()
    shotRootFolder = config.rootFolder + shotNumber + "/"

    return shotRootFolder

def getShotData(shotListView):
    # get shot data
    shotNumber = shotListView.currentItem().text()
    shotRootFolder = config.rootFolder + shotNumber + "/"
    shotDataFile = shotRootFolder + "_shotData/shotData.json"
    shotData = jsonReader.jsonRead(shotDataFile)

    return shotData