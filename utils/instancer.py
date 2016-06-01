import maya.cmds as mc

def instancer(assetName, transform=False):
    selectedAsset = assetName
    namespace = selectedAsset.split(":")[0]

    newInstance = mc.instance(selectedAsset, name=namespace + ":" + "instance#")[0]

    if transform:
        channels = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        count = 0
        for i in channels:
            mc.setAttr(newInstance + "." + i, transform[count])
            count +=1