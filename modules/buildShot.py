import maya.cmds as mc
import os

from ..utils import config
from ..utils import jsonReader
from ..utils import findAssetCategory
from ..utils import getShotData
from ..utils import shotCam
from ..utils import parentConstraint
from ..utils import instancer
import importAnim
reload(instancer)
reload(parentConstraint)
reload(shotCam)
reload(importAnim)
reload(getShotData)
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

    # create shotCamera
    shotNumber = shotList.currentItem().text()
    camName = "shot_" + str(shotNumber)
    camera = shotCam.shotCam(camName, groupNames["camGroup"])

    # import camera anim
    shotRootFolder = config.rootFolder + shotNumber + "/_anim/" + "camera/"
    importAnim.importAnim(shotRootFolder, camera)

    # set viewport to camera
    try:
        mc.modelEditor( "modelPanel4", edit=True, camera=camera )
    except:
        pass

    # load assets
    getAssets(shotList, assetList, shotState)

    # set time range
    shotData = getShotData.getShotData(shotList)
    animStart = shotData["shotRange"].split("-")[0]
    animEnd = shotData["shotRange"].split("-")[1]

    mc.playbackOptions(minTime= animStart)
    mc.playbackOptions(animationStartTime= animStart)
    mc.playbackOptions(maxTime= animEnd)
    mc.playbackOptions(animationEndTime= animEnd)
    mc.currentTime( animStart, edit=True )

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

    # get assets from constraintFile
    constrainedAssets = []
    constrainDataFiles = []
    for i in assets:
        assetsForConstraint = getAssetsForConstraints(shotRootFolder, i)
        if assetsForConstraint:
            for i in assetsForConstraint[0]:
                constrainedAssets.append(i)

            constrainDataFiles.append(assetsForConstraint[1])

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

            # handle .mb to .ma conversion
            if not os.path.isfile(assetState):
                assetState = assetState.replace(".mb", ".ma")

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

            mc.file(filePath, r=True, namespace=namespace, ignoreVersion=True)

        rootGroup = namespace + ":root"
        mc.parent(rootGroup, assetGroup)

    # place static assets
    assetsDataFile = getAssetsData(shotRootFolder, assets)
    if assetsDataFile:
        assetsData = jsonReader.jsonRead(assetsDataFile)
        transformSets(assetsData)

    # setup constraints
    if constrainedAssets:
        setupConstraints(constrainDataFiles)

    # import animation
    for i in assets:
        importAnim.importAnim(shotRootFolder, i)

    mc.inViewMessage( amg='Shot: <hl>%s</hl>.' %shotNumber, pos='midCenter', fade=True )

def getAssetsForConstraints(shotRootFolder, assetName):
    assetAnimFolder = shotRootFolder + "_anim/" + assetName + "/"
    constraintDataFile = assetAnimFolder + assetName + "_constraints.json"

    assets = []

    if os.path.isfile(constraintDataFile):
        constraintData = jsonReader.jsonRead(constraintDataFile)

        for constraint, objects in constraintData.iteritems():
            assets.append(objects[1].split(":")[0])

    if assets:
        return assets, constraintDataFile
    else:
        return False

def setupConstraints(constrainDataFiles):

    for i in constrainDataFiles:
        constrainData = jsonReader.jsonRead(i)

        for constraint, objects in constrainData.iteritems():
            mc.select(objects[0])
            mc.select(objects[1], add=True)

            constrainNode = parentConstraint.parentConstraint()

            # setup constraint restPose
            restData = objects[2]
            rt = restData["restTranslate"]
            rr = restData["restRotate"]

            restTranslate = [".targetOffsetTranslateX", ".targetOffsetTranslateY", ".targetOffsetTranslateZ"]
            restRotate = [".targetOffsetRotateX", ".targetOffsetRotateY", ".targetOffsetRotateZ"]

            counter = 0
            for i in restTranslate:
                mc.setAttr(constrainNode + ".target[0]" + i, rt[counter])
                counter +=1

            counter = 0
            for i in restRotate:
                mc.setAttr(constrainNode + ".target[0]" + i, rr[counter])
                counter +=1

def transformSets(setsData):
    channels = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz"]

    for assetName, value in setsData.iteritems():
        asset = assetName + ":root"
        if "{" in assetName:
            asset = assetName.replace("{", "").replace("}", "") + ":root"

        if mc.objExists(asset):
            count = 0

            # transform referenced asset
            for i in channels:
                channelValue = value["transform"][0][count]
                try:
                    mc.setAttr(asset + i, channelValue)
                    count+=1
                except:
                    print asset + " >>> Error setting values"

            # create instances
            if len(value["transform"]) > 1:
                instanceNumber = len(value["transform"])

                c = 1
                while c < instanceNumber:
                    instancer.instancer(asset, transform=value["transform"][c])
                    c+=1

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

                    if not os.path.isfile(folderPath + masterFile):
                        masterFile = assetName + "_MASTER.ma"

                    return folderPath + masterFile