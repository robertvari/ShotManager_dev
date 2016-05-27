import maya.cmds as mc
import os
import re
from ..utils import jsonReader
from ..utils import parentConstraint

def importAnim(shotPath, assetName, conSetup=False, backupAnim=False):
    animFolder = shotPath + "_anim" + "/" + assetName + "/"
    animFile = animFolder + assetName + "_anim.ma"

    if backupAnim:
        # clean animation curves
        animCurves = mc.ls(assetName + ":*", type="animCurve")
        for i in animCurves:
            mc.delete(i)

    if backupAnim:
        animFile = backupAnim

    if "camera" in shotPath:
        animFile = shotPath + assetName + "_anim.ma"

    print animFile

    if os.path.isfile(animFile):
        newCamNodes = []

        if "camera" in animFolder:
            # clear cam animation before import
            shotName = shotPath.split("/")[-2]
            camName = "shot_"+shotName

            animCurves = mc.ls(camName + "*", type="animCurve")
            for i in animCurves:
                if mc.objExists(i):
                    mc.delete(i)

            newNodes = mc.file(animFile, i=True, ignoreVersion=True, returnNewNodes=True)

            shotNumber = "_" + assetName.split("shot_")[-1] + "_"

            for i in newNodes:
                if not backupAnim:
                    importNumber = re.search('_\d\w+_', i)
                    importNumber = importNumber.group(0)
                    newName = mc.rename(i, i.replace(importNumber, shotNumber))
                    newCamNodes.append(newName)
                else:
                    newCamNodes.append(i)
        else:
            newNodes = mc.file(animFile, i=True, ignoreVersion=True, returnNewNodes=True, namespace=assetName, mergeNamespacesOnClash=True)

        # build constraints
        for i in newNodes:
            if mc.objExists(i + ".source"):
                source = mc.getAttr(i + ".source")
                dest = mc.getAttr(i + ".destination")

                parentConstraint.parentConstraint(nodes=[source, dest])

        for i in newNodes:
            controlName = mc.getAttr(i + ".control")
            if not newCamNodes:
                controlName = assetName + ":" + controlName
            else:
                if not backupAnim:
                    controlName = assetName + "." + controlName.split(".")[-1]
                else:
                    controlName = mc.getAttr(i + ".control")

            mc.connectAttr(i + ".output", controlName, f=True)