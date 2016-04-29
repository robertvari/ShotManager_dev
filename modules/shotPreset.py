import maya.cmds as mc
import os
from PySide import QtGui, QtCore
from functools import partial
from ..utils import getShotData
from ..utils import jsonReader
reload(getShotData)
reload(jsonReader)

def saveSelection(mainWindow, assetListView, parentMenu, shotListView):
    if not assetListView.selectedItems():
        mc.warning("Select few assets.")
        return

    result = mc.promptDialog(
                title='Selection',
                message='Enter Preset Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

    if result == 'OK':
        text = mc.promptDialog(query=True, text=True)
        try:
            presetsFile = getShotData.getShotFolder(shotListView) + "_shotData/presets.json"
        except:
            mc.warning("Select a shot.")
            return

        # add new item to parent menu
        addMenuItem(mainWindow, parentMenu, text, presetsFile, assetListView)

        # save selection data to file (network)
        preset = {text:getSelectedAsset(assetListView)}

        if not os.path.isfile(presetsFile):
            jsonReader.jsonWrite(preset, presetsFile)
        else:
            presetData = jsonReader.jsonRead(presetsFile)
            presetData[text] = getSelectedAsset(assetListView)

            jsonReader.jsonWrite(presetData, presetsFile)

        print "Selection was stored in %s \n" %presetsFile,

def addMenuItem(mainWindow, parentMenu, text, presetsFile, assetListView):
    newMenuItem = QtGui.QAction(mainWindow)
    newMenuItem.setText(text)
    parentMenu.addAction(newMenuItem)

    newMenuItem.triggered.connect(partial(presetAction, text, presetsFile, assetListView))

def presetAction(text, presetsFile, assetListView):
    presetsFile = jsonReader.jsonRead(presetsFile)
    assetListView.clearSelection()

    for presetName, value in presetsFile.iteritems():
        if text == presetName:
            assetList = value
            for i in assetList:
                itemInList = assetListView.findItems( i, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)[0]
                assetListView.setItemSelected(itemInList, 1)

def getSelectedAsset(assetList):
    item = assetList.selectedItems()
    assetList = []
    for i in item:
        asset = i.text(0)
        assetList.append(asset)

    return assetList
