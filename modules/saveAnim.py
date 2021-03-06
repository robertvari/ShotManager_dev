import maya.cmds as mc
import maya.mel as mel
import os
import shutil

from ..utils import getShotData
from ..utils import jsonReader
reload(jsonReader)
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

        # get anim layers
        # animLayers = getAnimLayers(controls)

        # save animation
        createFolder(folderPath)
        exportAnim(folderPath, controls, assetName)
    else:
        folderPath = animRootFolder + "/camera/"
        createFolder(folderPath)
        camName = "shot_" + shotListView.currentItem().text()
        exportCameraAnim(folderPath, camName)

    if cameraAnim:
        assetName = "Camera"

    mc.inViewMessage( amg='Animation was saved for <hl>%s</hl>.' %assetName, pos='midCenter', fade=True )

def getAnimLayers(controls):
    animLayers = []
    for control in controls:
        if mc.listConnections(control, type="animLayer"):
            for item in mc.listConnections(control, type="animLayer"):
                if not item in animLayers:
                    animLayers.append(item)

    return animLayers

def exportAnim(folderPath, controls, assetName):

    # backup animation
    fileName = folderPath + assetName + "_anim.ma"
    if os.path.isfile(fileName):
        makeBackup(folderPath, fileName)

    animCurves = []

    setName = assetName + ":character"
    for i in mc.sets(setName, q=True ):
        if mc.listConnections(i, type="animCurve"):
            animCurve = mc.listConnections(i, type="animCurve")[0]

            if mc.objExists(animCurve):
                connectTo = mc.listConnections(animCurve, plugs=True)[0].split(":")[-1]

                # add extra channel for import connection
                if not mc.objExists(animCurve + ".control"): mc.addAttr(animCurve, ln="control", dt="string")

                mc.setAttr(animCurve + ".control", connectTo, type="string")

                # parent anim curves to root namespace
                animCurves.append(mc.rename(animCurve, animCurve.split(":")[-1]))

    mc.select(cl=True)
    for i in controls:
        mc.select(i, add=True)

    mc.file(fileName, type='mayaAscii', exportSelectedAnim=True, f=True)

    # add namespace to anim curves
    for i in animCurves:
        mc.rename(i, assetName + ":" + i)

    # clear selection
    mc.select(cl=True)

def getConstraints(controls):
    constraintList = {}

    constraints = []
    for i in controls:
        if mc.objExists(i + ".constraint"):
            constraints.append(mc.listConnections(i + ".constraint", type="constraint")[0])

    for con in constraints:
        source = mc.parentConstraint(con, q=True, targetList=True)[0]
        dest = mc.listRelatives(con, allParents=True)[0]

        restData = getConstraintRest(con)
        constraintList[con]=[source, dest, restData]

def getConstraintRest(constraint):
    rt = []
    rr = []

    restTranslate = [".targetOffsetTranslateX", ".targetOffsetTranslateY", ".targetOffsetTranslateZ"]
    restRotate = [".targetOffsetRotateX", ".targetOffsetRotateY", ".targetOffsetRotateZ"]

    for i in restTranslate:
        rt.append(mc.getAttr(constraint + ".target[0]" + i))

    for i in restRotate:
        rr.append(mc.getAttr(constraint + ".target[0]" + i))

    constraintRest = {"restTranslate":rt, "restRotate":rr}
    return constraintRest

def exportCameraAnim(folderPath, camName):
    fileName = folderPath + camName + "_anim.ma"

    # backup animation
    if os.path.isfile(fileName):
        makeBackup(folderPath, fileName)

    # write data on camera animCurves
    camAnimCurves = mc.listConnections(camName, type="animCurve")
    for i in camAnimCurves:
        if not mc.objExists(i + ".control"): mc.addAttr(i, ln="control", dt="string")

        connectTo = mc.listConnections(i, plugs=True)[0]
        mc.setAttr(i + ".control", connectTo, type="string")

    mc.select(camName)
    mc.file(fileName, type='mayaAscii', exportSelectedAnim=True, f=True)

def makeBackup(folderPath, fileName):
    masterFilePath = fileName
    BACKUP_PATH = folderPath + "_backup/"
    masterName = fileName.split("/")[-1]

    ext = ".ma"
    if ".json" in fileName:
        ext = ".json"

    # create backup folder if not exists
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)

    if os.path.isfile(fileName):
        i = 0
        backupFilename = BACKUP_PATH + "/" + masterName.split(ext)[0] + ".%s" %i

        i = 0
        while os.path.exists(BACKUP_PATH + "/" + masterName.split(ext)[0] + ".%i" %i):
            i += 1

        backupName = BACKUP_PATH + masterName.split(ext)[0] + ".%i" %i

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