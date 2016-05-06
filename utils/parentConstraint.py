import maya.cmds as mc

def parentConstraint():
    selection = mc.ls(sl=True)

    source = selection[0]
    dest = selection[1] + "_DRIVEN"
    if "_DRIVEN" in selection[1]:
        dest = selection[1]

    namespace = source.split(":")[0]

    constraintNode = mc.parentConstraint(source, dest, maintainOffset=True)[0]

    # add constraint to source's namespace
    constraintNode = mc.rename(constraintNode, namespace + ":" + constraintNode)

    # add channel to source
    if not mc.objExists(source + ".constraint"):
        mc.addAttr(source, shortName="constraint", attributeType="double", keyable=True, minValue=0, maxValue=1)
        mc.setAttr(source + ".constraint", 1)

        # create animCurve for saving constraint data
        mc.setKeyframe(source + ".constraint")

        # save constraint data on anim curve
        animCurve = mc.listConnections(source + ".constraint", type="animCurve")[0]
        if not mc.objExists(animCurve + ".source"): mc.addAttr(animCurve, ln="source", dt="string")
        mc.setAttr(animCurve + ".source", source, type="string")
        if not mc.objExists(animCurve + ".destination"): mc.addAttr(animCurve, ln="destination", dt="string")
        mc.setAttr(animCurve + ".destination", dest, type="string")

    # add new channel to character set
    characterSet = namespace + ":" + "character"
    mc.sets(source + ".constraint", addElement=characterSet)

    constraintChannelsToCharacterSet = [".restTranslateX", ".restTranslateY", ".restTranslateZ", ".restRotateX", ".restRotateY", ".restRotateZ",
                                        ".target[0].targetOffsetTranslateX", ".target[0].targetOffsetTranslateY", ".target[0].targetOffsetTranslateZ",
                                        ".target[0].targetOffsetRotateX", ".target[0].targetOffsetRotateY", ".target[0].targetOffsetRotateZ"]

    for i in constraintChannelsToCharacterSet:
        mc.sets(constraintNode + i, addElement=characterSet)

        # key constraint channels for saving data
        mc.setKeyframe(constraintNode + i)

    # connect source channel to constraint weight
    mc.connectAttr(source + ".constraint", constraintNode + "." + source.split(":")[-1]+"W0")

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

    # delete constraint
    mc.delete(mc.listConnections(control)[0])

    # remove channel
    mc.deleteAttr(control + ".constraint")

    print "Constraint was deleted from %s" % control