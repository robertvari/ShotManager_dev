import maya.cmds as mc

def keyToOff():
    controller = mc.ls(sl=True)[0]
    constraint = mc.listConnections(controller + ".constraint", type="constraint")[0]
    currentTime = mc.currentTime( query=True )

    # set key on 1 for controller
    setKeyframe(controller + ".constraint", currentTime-1, value=1)
    setKeyframe(controller + ".constraint", currentTime, value=0)

    # save rest pose on constraint
    mc.parentConstraint(constraint, edit=True, maintainOffset=True)
    constraintChannels = [".restTranslateX", ".restTranslateY", ".restTranslateZ", ".restRotateX", ".restRotateY", ".restRotateZ"]
    for i in constraintChannels:
        value = mc.getAttr(constraint + i)
        setKeyframe(constraint + i, currentTime, value)

def keyToOn():
    controller = mc.ls(sl=True)[0]
    constraint = mc.listConnections(controller + ".constraint", type="constraint")[0]
    currentTime = mc.currentTime( query=True )

    # set key on 1 for controller
    setKeyframe(controller + ".constraint", currentTime-1, value=0)
    setKeyframe(controller + ".constraint", currentTime, value=1)

    # save rest pose on constraint
    mc.parentConstraint(constraint, edit=True, maintainOffset=True)
    constraintChannels = [".restTranslateX", ".restTranslateY", ".restTranslateZ", ".restRotateX", ".restRotateY", ".restRotateZ"]
    for i in constraintChannels:
        value = mc.getAttr(constraint + i)
        setKeyframe(constraint + i, currentTime, value)


def setKeyframe(control, currentTime, value):
    mc.setKeyframe(control, value=value, time=currentTime, inTangentType="clamped", outTangentType="step")