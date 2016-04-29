import maya.cmds as mc

def shotCam(camName, parentGroup):
    shotCam = mc.camera()[0]
    mc.parent(shotCam, parentGroup)
    shotCam = mc.rename(shotCam, camName)

    # setup camera gate
    camShape = mc.listRelatives(shotCam, shapes=True)[0]
    mc.setAttr(camShape + ".displayGateMask", 1)
    mc.setAttr(camShape + ".displayResolution", 1)
    mc.setAttr(camShape + ".overscan", 1.2)

    # setup clippingPlane
    mc.setAttr(camShape + ".nearClipPlane", 5)
    mc.setAttr(camShape + ".farClipPlane", 5000)

    # add extra channel
    mc.addAttr(shotCam, shortName="focalLength", attributeType="double", minValue=2.5, keyable=True)
    mc.setAttr(shotCam + ".focalLength", 35)
    mc.connectAttr(shotCam + ".focalLength", camShape + ".focalLength")

    # lock channels
    channelLock = [".sx", ".sy", ".sz", ".v"]
    for i in channelLock:
        mc.setAttr(shotCam + i, lock=True)

    mc.setAttr(camShape + ".focalLength", lock=True)


    return shotCam