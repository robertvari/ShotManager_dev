import maya.cmds as mc
import os
import shutil

from ..utils import getShotData
reload(getShotData)

def saveAnimation(shotListView, cameraAnim=False):
    try:
        animRootFolder = getShotData.getShotFolder(shotListView) + "_anim"
    except:
        mc.warning("Select a shot!")
        return

    # get selected asset name
    if not cameraAnim:
        try:
            assetName = mc.ls(sl=True)[0].split(":")[0]
        except:
            mc.warning("Which character you want to save anim for?? hint: Select a controller...")
            return

        # create animation folders for the asset if not exists
        folderPath = animRootFolder + "/" + assetName + "/"

        # collect controls
        controls = getControls(assetName)

        # get constraints

        # get constrained assets

        # get anim layers

        # save animation
        createFolder(folderPath)
        exportAnim(folderPath, controls, assetName)
    else:
        folderPath = animRootFolder + "/camera/"
        createFolder(folderPath)
        camName = "shot_" + shotListView.currentItem().text()
        exportCameraAnim(folderPath, camName)

    print "Animation was saved: " + folderPath,

def exportAnim(folderPath, controls, assetName):
    fileName = folderPath + assetName + "_anim.ma"

    # backup animation
    if os.path.isfile(fileName):
        makeBackup(folderPath, fileName)

    mc.select(cl=True)
    for i in controls:
        mc.select(i, add=True)

    animCurves = []

    setName = assetName + ":character"
    for i in mc.sets(setName, q=True ):
        animCurve = i.replace(".", "_")
        if mc.objExists(animCurve):
            # parent anim curves to root namespace
            animCurves.append(mc.rename(animCurve, animCurve.split(":")[-1]))

    mc.file(fileName, type='mayaAscii', exportSelectedAnim=True, f=True)

    # add namespace to anim curves
    for i in animCurves:
        mc.rename(i, assetName + ":" + i)

def exportCameraAnim(folderPath, camName):
    fileName = folderPath + camName + "_anim.ma"

    # backup animation
    if os.path.isfile(fileName):
        makeBackup(folderPath, fileName)

    mc.select(camName)
    mc.file(fileName, type='mayaAscii', exportSelectedAnim=True, f=True)

def makeBackup(folderPath, fileName):
    masterFilePath = fileName
    BACKUP_PATH = folderPath + "_backup/"
    masterName = fileName.split("/")[-1]

    # create backup folder if not exists
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)

    if os.path.isfile(fileName):
        i = 0
        backupFilename = BACKUP_PATH + "/" + masterName.split(".ma")[0] + "_backup_%s.ma" %i

        i = 0
        while os.path.exists(BACKUP_PATH + "/" + masterName.split(".ma")[0] + "_backup_%i.ma" % i):
            i += 1

        backupName = BACKUP_PATH + "/" + masterName.split(".ma")[0] + "_backup_%i.ma" % i
        shutil.copyfile(masterFilePath, backupName)

def getCamerAnimCurves(assetName):
    return mc.listConnections(assetName)

def getControls(assetName):
    setName = assetName + ":character"

    controls = []
    for i in mc.sets(setName, q=True ):
        controlName = i.split(".")[0]
        if not controlName in controls:
            controls.append(controlName)

    return controls

def createFolder(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)