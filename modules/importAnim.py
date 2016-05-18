import maya.cmds as mc
import os
import re
from ..utils import jsonReader
from ..utils import parentConstraint

def importAnim(shotPath, assetName, conSetup=False):
    animFolder = shotPath + "_anim" + "/" + assetName + "/"
    animFile = animFolder + assetName + "_anim.ma"
    # constraintsFile = animFolder + assetName + "_constraints.json"

    if "camera" in shotPath:
        animFile = shotPath + assetName + "_anim.ma"

    if os.path.isfile(animFile):
        newCamNodes = []

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

            mc.connectAttr(i + ".output", controlName, f=True)