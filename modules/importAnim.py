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

        # create constraints and channels based on constraintsData
        if constraintsData:
            constraintSetup(constraintsData)

        for i in newNodes:
            inChannel = i.split("_")[-1]
            controlName = i.split("_"+inChannel)[0]
            mc.connectAttr(i + ".output", controlName + "." + inChannel)

def constraintSetup(constraintsData):
    # setup for constraints
    for constraint, objects in constraintsData.iteritems():
        mc.addAttr(objects[0], shortName="constraint", attributeType="double", keyable=True, minValue=0, maxValue=1)