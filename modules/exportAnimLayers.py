import maya.cmds as mc

def getAnimLayers(controler):
    mc.select(cl=True)

    # get anim layers
    animLayerNodes = []
    connections = mc.listConnections(controler, type="animLayer")
    for i in connections:
        if not i in animLayerNodes:
            animLayerNodes.append(i)

    # export anim layers
    for i in animLayerNodes:
        collectAnimLayerNodes(i)

    # save selected
    mc.file("D:/maya_tmp/animation.ma", type="mayaAscii", exportSelected=True, channels=False, constructionHistory=False, expressions=False, constraints=False, f=True)

def collectAnimLayerNodes(animLayerNode):
    mc.animLayer(animLayerNode, edit=True, writeBlendnodeDestinations=True)
    layerCurves = mc.animLayer(animLayerNode, q=True, animCurves=True)
    layerBlendNodes = mc.animLayer(animLayerNode, q=True, blendNodes=True)

    for i in layerBlendNodes:
        animCurveOnLayerNode = mc.listConnections(i, type="animCurve")
        if animCurveOnLayerNode:
            for curveNode in animCurveOnLayerNode:
                if not curveNode in layerCurves:
                    layerCurves.append(curveNode)

    mc.select(animLayerNode, add=True, noExpand=True)

    for curve in layerCurves:
        mc.select(curve, add=True)

    for blendNode in layerBlendNodes:
        mc.select(blendNode, add=True)

getAnimLayers("AMA_MagicWand:wand_CTRL")