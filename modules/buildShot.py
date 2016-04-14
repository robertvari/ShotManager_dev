import maya.cmds as mc
import os

from ..utils import config
from ..utils import jsonReader
from ..utils import findAssetCategory
reload(findAssetCategory)
reload(jsonReader)
reload(config)

groupNames = {"castGroup":"CAST", "setsGroup":"SETS", "camGroup":"CAMERA", "propsGroup":"PROPS"}

def buildShot(shotList, assetList, shotStateCombo):
    # new maya file
    mc.file(new=True, f=True)

    shotState = shotStateCombo.currentText()

    # build group structure
    for key, value in groupNames.iteritems():
        if not mc.objExists(value):
            mc.group(name=value, empty=True)

    # load assets
    getAssets(shotList, assetList, shotState)

    # create shotCamera
    shotNumber = shotList.currentItem().text()
    camName = "shot_" + str(shotNumber)

    shotCam = mc.camera()[0]
    mc.parent(shotCam, groupNames["camGroup"])
    mc.rename(shotCam, camName)

    # set time range
    shotData = getShotData(shotList)
    animStart = shotData["shotRange"].split("-")[0]
    animEnd = shotData["shotRange"].split("-")[1]

    mc.playbackOptions(minTime= animStart)
    mc.playbackOptions(animationStartTime= animStart)
    mc.playbackOptions(maxTime= animEnd)
    mc.playbackOptions(animationEndTime= animEnd)

    mc.select(cl=True)

def addAssetToScene(shotList, assetList, shotStateCombo):
    shotState = shotStateCombo.currentText()
    selectedAsset = getSelectedAsset(assetList)[0]

    if mc.objExists("SETS"):
        if not mc.objExists("*%s*" % selectedAsset):
            # load assets
            getAssets(shotList, assetList, shotState)
        else:
            mc.warning(selectedAsset + " is already loaded into the scene.")
    else:
        mc.warning("First you have to build a shot.")

def getShotData(shotList):
    # get shot data
    shotNumber = shotList.currentItem().text()
    shotRootFolder = config.rootFolder + shotNumber + "/"
    shotDataFile = shotRootFolder + "_shotData/shotData.json"
    shotData = jsonReader.jsonRead(shotDataFile)

    return shotData

def getAssets(shotList, assetList, shotState):
    # get shot data
    shotNumber = shotList.currentItem().text()
    shotRootFolder = config.rootFolder + shotNumber + "/"
    shotDataFile = shotRootFolder + "_shotData/shotData.json"
    shotData = jsonReader.jsonRead(shotDataFile)
    assets = shotData["assets"]

    selectedAssets = getSelectedAsset(assetList)
    if selectedAssets:
        assets = selectedAssets

    for i in assets:
        # handle duplicated reference
        duplicatedAsset = None
        if "{" in i:
            duplicatedAsset = i.replace("{", "").replace("}", "")
            i = i.split("{")[0]

        assetGroup = findAssetCategory.findCategory(i)
        filePath = getAssetpath(i)

        # handle shot versions
        assetLevel = False
        if not shotState == "WIP":
            assetState = filePath.replace("_MASTER", "_MASTER_" + shotState)
            if os.path.isfile(assetState):
                assetLevel = True
                filePath = assetState

        # reference asset
        if duplicatedAsset:
            namespace = duplicatedAsset
            mc.file( filePath, r=True, namespace=namespace, ignoreVersion=True)
        else:
            namespace = filePath.split("/")[-1].split(".")[0]
            namespace = namespace.replace("_MASTER", "")
            if assetLevel:
                namespace = namespace.replace("_" + shotState, "")

            mc.file( filePath, r=True, namespace=namespace, ignoreVersion=True)

        rootGroup = namespace + ":root"
        mc.parent(rootGroup, assetGroup)

    # get assets data if exists
    assetsDataFile = getAssetsData(shotRootFolder, assets)
    if assetsDataFile:
        assetsData = jsonReader.jsonRead(assetsDataFile)
        transformSets(assetsData)

def transformSets(setsData):
    channels = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz"]

    for assetName, value in setsData.iteritems():
        asset = assetName + ":root"
        if "{" in assetName:
            asset = assetName.replace("{", "").replace("}", "") + ":root"

        if mc.objExists(asset):
            count = 0
            for i in channels:
                channelValue = value["transform"][count]
                try:
                    mc.setAttr(asset + i, channelValue)
                    count+=1
                except:
                    print asset + " >>> Error setting values"

def getAssetsData(shotRootFolder, assets):
    assetsDataFile = shotRootFolder + "_shotData/sceneData.json"

    if os.path.isfile(assetsDataFile):
        return assetsDataFile
    else:
        return False

def getSelectedAsset(assetList):
    item = assetList.selectedItems()
    assetList = []
    for i in item:
        asset = i.text(0)
        assetList.append(asset)

    return assetList

def getAssetpath(assetName):
    assetPaths = jsonReader.jsonRead(config.assetPaths)

    for key, value in assetPaths.iteritems():
        subfolders = os.listdir(value)
        if subfolders:
            for i in subfolders:
                if i == assetName:
                    folderPath = value + i + "/"
                    masterFile = assetName + "_MASTER.mb"

                    return folderPath + masterFile