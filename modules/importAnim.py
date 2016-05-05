import maya.cmds as mc
import os
import re
from ..utils import jsonReader
from ..utils import parentConstraint

def importAnim(shotPath, assetName, conSetup=False):
    animFolder = shotPath + "_anim" + "/" + assetName + "/"
    animFile = animFolder + assetName + "_anim.ma"
    constraintsFile = animFolder + assetName + "_constraints.json"

    if "camera" in shotPath:
        animFile = shotPath + assetName + "_anim.ma"

    if os.path.isfile(animFile):
        newCamNodes = []
        constraintsData = None

        if os.path.isfile(constraintsFile):
            constraintsData = jsonReader.jsonRead(constraintsFile)

        if "camera" in shotPath:
            newNodes = mc.file(animFile, i=True, ignoreVersion=True, returnNewNodes=True)

            shotNumber = "_" + assetName.split("shot_")[-1] + "_"

            for i in newNodes:
                importNumber = re.search('_\d\w+_', i)
                importNumber = importNumber.group(0)
                newName = mc.rename(i, i.replace(importNumber, shotNumber))
                newCamNodes.append(newName)
        else:
            newNodes = mc.file(animFile, i=True, ignoreVersion=True, returnNewNodes=True, namespace=assetName, mergeNamespacesOnClash=True)

        if newCamNodes:
            newNodes = newCamNodes

        for i in newNodes:
            inChannel = i.split("_")[-1]
            controlName = i.split("_"+inChannel)[0]

            if mc.objExists(i + ".control"):
                controlName = mc.getAttr(i + ".control")
                inChannel = i.split(controlName)[-1][1::]
                controlName = assetName + ":" + controlName

            if "target_0" in controlName:
                controlName = controlName.replace("_target_0_", ".target[0]")

            mc.connectAttr(i + ".output", controlName + "." + inChannel)