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
            controlName = mc.getAttr(i + ".control")
            if not newCamNodes:
                controlName = assetName + ":" + controlName

            # build constraints
            if "constraint" in i:

                # TODO have ot add constraint source/dest data to all constraint animCurves

                source = mc.getAttr(i + ".source")
                dest = mc.getAttr(i + ".destination")

                constraintNode = mc.parentConstraint(source, dest, maintainOffset=True)[0]

                # add channel to source
                if not mc.objExists(source + ".constraint"):
                    mc.addAttr(source, shortName="constraint", attributeType="double", keyable=True, minValue=0, maxValue=1)

                # connect source channel to constraint weight
                mc.connectAttr(source + ".constraint", constraintNode + "." + source.split(":")[-1]+"W0")

                # add namespace to constraint
                mc.rename(constraintNode, assetName + ":" + constraintNode)

            mc.connectAttr(i + ".output", controlName)