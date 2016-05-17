import maya.cmds as mc
import maya.mel as mel

def parentConstraint(nodes=False):
    selection = mc.ls(sl=True)

    if not nodes:
        source = selection[0]
        dest = selection[1] + "_DRIVEN"
        if "_DRIVEN" in selection[1]:
            dest = selection[1]
    else:
        source = nodes[0]
        dest = nodes[1]
        if "_DRIVEN" in nodes[1]:
            dest = nodes[1]

    namespace = source.split(":")[0]

    constraintNode = mc.parentConstraint(source, dest, name=namespace + ":" + dest.split(":")[-1] + "_constraint", maintainOffset=True)[0]

    # add channel to source
    counter = 0
    channelName = dest.split(":")[-1]

    targetList = mc.parentConstraint(constraintNode, q=True, targetList=True)

    while counter+1 < len(targetList):
        counter += 1

    constraintChannel = channelName + str(counter)

    if not mc.objExists(source + "." + constraintChannel):
        mc.addAttr(source, shortName=constraintChannel, attributeType="double", keyable=True, minValue=0, maxValue=1)
        mc.setAttr(source + "." + constraintChannel, 1)

        # set channel to 0 if not the first one
        if counter > 0:
            mc.setAttr(source + "." + constraintChannel, 0)

        # create animCurve for saving constraint data
        mc.setKeyframe(source + "." + constraintChannel)

        # save constraint data on anim curve
        animCurve = mc.listConnections(source + "." + constraintChannel, type="animCurve")[0]
        if not mc.objExists(animCurve + ".source"): mc.addAttr(animCurve, ln="source", dt="string")
        mc.setAttr(animCurve + ".source", source, type="string")
        if not mc.objExists(animCurve + ".destination"): mc.addAttr(animCurve, ln="destination", dt="string")
        mc.setAttr(animCurve + ".destination", dest, type="string")

    # add new channel to character set
    characterSet = namespace + ":" + "character"
    mc.sets(source + "." + constraintChannel, addElement=characterSet)

    constraintChannelsToCharacterSet = [".restTranslateX", ".restTranslateY", ".restTranslateZ", ".restRotateX", ".restRotateY", ".restRotateZ",
                                        ".target[%i].targetOffsetTranslateX" %counter, ".target[%i].targetOffsetTranslateY" %counter, ".target[%i].targetOffsetTranslateZ" %counter,
                                        ".target[%i].targetOffsetRotateX" %counter, ".target[%i].targetOffsetRotateY" %counter, ".target[%i].targetOffsetRotateZ" %counter,]

    for i in constraintChannelsToCharacterSet:
        mc.sets(constraintNode + i, addElement=characterSet)

        # key constraint channels for saving data
        mc.setKeyframe(constraintNode + i)

    # connect source channel to constraint weight
    mc.connectAttr(source + "." + constraintChannel, constraintNode + "." + source.split(":")[-1]+"W%i" %counter)

    # write data on constraint anim curves for importing animations
    animCurvesOnConstraint = mc.listConnections(constraintNode, type="animCurve")

    for i in animCurvesOnConstraint:
        animCurveNode = i
        controller = constraintNode
        targetChannel = mc.listConnections(animCurveNode, plugs=True)[0].split(":")[-1]
        if not mc.objExists(animCurveNode + ".control"): mc.addAttr(animCurveNode, ln="control", dt="string")
        mc.setAttr(animCurveNode + ".control", targetChannel, type="string")

    mc.select(source)

    return constraintNode

def deleteConstraint():
    control = mc.ls(sl=True)[0]

    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')	#fetch maya's main channelbox
    attrs = mc.channelBox(channelBox, q=True, sma=True)

    if attrs:
        # delete constraint
        try:
            constraintNode = mc.listConnections(control + "." + attrs[0], type="constraint")[0]
            if constraintNode:
                mc.delete(constraintNode)
        except:
            pass

        # remove channel
        mc.deleteAttr(control + "." + attrs[0])
    else:
        mc.warning("Please select constraint channel.")