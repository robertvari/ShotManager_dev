import maya.cmds as mc
import maya.mel as mel

def keyToOff():
    controller = mc.ls(sl=True)[0]

    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')	#fetch maya's main channelbox
    attrs = mc.channelBox(channelBox, q=True, sma=True)

    if attrs:
        channel = controller + "." + attrs[0]
        constraint = mc.listConnections(channel, type="constraint")[0]
        currentTime = mc.currentTime( query=True )

        # set key on 1 for controller
        setKeyframe(channel, currentTime-1, value=1)
        setKeyframe(channel, currentTime, value=0)

        # save rest pose on constraint
        mc.parentConstraint(controller, constraint, edit=True, maintainOffset=True)
        constraintChannels = mc.listConnections(constraint, type="animCurve")
        for i in constraintChannels:
            value = mc.getAttr(mc.listConnections(i, plugs=True)[0])
            setKeyframe(mc.listConnections(i, plugs=True)[0], currentTime, value)
    else:
        mc.warning("Select constrain channel!")

def keyToOn():
    controller = mc.ls(sl=True)[0]

    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')	#fetch maya's main channelbox
    attrs = mc.channelBox(channelBox, q=True, sma=True)

    if attrs:
        channel = controller + "." + attrs[0]
        constraint = mc.listConnections(channel, type="constraint")[0]
        currentTime = mc.currentTime( query=True )

        # save rest pose on constraint
        # mc.currentTime(currentTime-1)
        constraintChannels = mc.listConnections(constraint, type="animCurve")
        mc.parentConstraint(controller, constraint, edit=True, maintainOffset=True)
        for i in constraintChannels:
            value = mc.getAttr(mc.listConnections(i, plugs=True)[0])
            setKeyframe(mc.listConnections(i, plugs=True)[0], currentTime, value)

        # set key on 1 for controller
        setKeyframe(channel, currentTime-1, value=0)
        setKeyframe(channel, currentTime, value=1)

        # mc.currentTime( currentTime )
    else:
        mc.warning("Select constrain channel!")


def setKeyframe(control, currentTime, value):
    mc.setKeyframe(control, value=value, time=currentTime, inTangentType="clamped", outTangentType="step")