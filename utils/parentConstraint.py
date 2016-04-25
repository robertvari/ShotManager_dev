import maya.cmds as mc

def parentConstraint():
    selection = mc.ls(sl=True)

    source = selection[0]
    dest = selection[1] + "_DRIVEN"
    if "_DRIVEN" in selection[1]:
        dest = selection[1]

    constraintNode = mc.parentConstraint(source, dest, maintainOffset=True)[0]

    # add channel to source
    if not mc.objExists(source + ".constraint"):
        mc.addAttr(source, shortName="constraint", attributeType="double", keyable=True, minValue=0, maxValue=1)
        mc.setAttr(source + ".constraint", 1)

    # add new channel to character set
    namespace = source.split(":")[0]
    characterSet = namespace + ":" + "character"
    mc.sets(source + ".constraint", addElement=characterSet)

    # connect source channel to constraint weight
    mc.connectAttr(source + ".constraint", constraintNode + "." + source.split(":")[-1]+"W0")

    mc.select(source)

    print "Constraint created for %s" % source,
    return constraintNode


def deleteConstraint():
    control = mc.ls(sl=True)[0]

    # delete constraint
    mc.delete(mc.listConnections(control)[0])

    # remove channel
    mc.deleteAttr(control + ".constraint")

    print "Constraint was deleted from %s" % control