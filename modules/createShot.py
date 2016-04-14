# This window creates and edits existing shots

from PySide import QtGui, QtCore
import maya.cmds as mc
import json
import os

from ..utils import config
from ..utils import getAssets
from ..utils import findAssetCategory
from ..utils import jsonReader
reload(jsonReader)
reload(findAssetCategory)
reload(getAssets)
reload(config)

class CreateShotWindow(QtGui.QDialog):
    def __init__(self, shotListView, contentsTreeView, mode):
        QtGui.QDialog.__init__(self)
        self.mode = mode
        self.contentsTreeView = contentsTreeView
        self.setWindowTitle("Create New Shot")
        self.resize(400, 500)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        self.shotListView = shotListView

        gridlayout = QtGui.QGridLayout()
        mainLayout.addLayout(gridlayout)

        # labels
        shotNumber_lbl = QtGui.QLabel("Shot Number:")
        shotLocation_lbl = QtGui.QLabel("Shot Location:")
        addEsset_lbl = QtGui.QLabel("Add Asset:")
        assets_lbl = QtGui.QLabel("Assets:")
        assets_lbl.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        shotRange_lbl = QtGui.QLabel("Shot Range:")

        # items
        self.shotNumberField = QtGui.QLineEdit()
        self.shotLocationsCombo = QtGui.QComboBox()
        self.addAssetField = QtGui.QLineEdit()
        self.autoCompletter()
        addAsset_bttn = QtGui.QPushButton("Add")
        addAssetLayout = QtGui.QHBoxLayout()
        addAssetLayout.addWidget(self.addAssetField)
        addAssetLayout.addWidget(addAsset_bttn)
        self.assetsTree = QtGui.QTreeWidget()
        self.fontSize(10, self.assetsTree)
        self.shotRangeField = QtGui.QLineEdit()
        self.createShot_bttn = QtGui.QPushButton("Create Shot")

        self.createShot_bttn.clicked.connect(self.createShot)

        self.assetsTree.setHeaderHidden(True)

        # add items to layout
        gridlayout.addWidget(shotNumber_lbl, 0,0)
        gridlayout.addWidget(self.shotNumberField, 0,1)
        gridlayout.addWidget(shotRange_lbl, 1,0)
        gridlayout.addWidget(self.shotRangeField, 1,1)
        gridlayout.addWidget(shotLocation_lbl, 2,0)
        gridlayout.addWidget(self.shotLocationsCombo, 2,1)
        gridlayout.addWidget(addEsset_lbl, 3,0)
        gridlayout.addLayout(addAssetLayout, 3,1)
        gridlayout.addWidget(assets_lbl, 4,0)
        gridlayout.addWidget(self.assetsTree, 4,1)

        mainLayout.addWidget(self.createShot_bttn)

        # get scenes data and add items into locations combo
        scenesDataFile = config.shotLocationsPath
        with open(scenesDataFile) as data_file:
            scenesData = json.load(data_file)

        locationList = []
        for key, value in scenesData.iteritems():
            locationList.append(key)

        for i in sorted(locationList):
            self.shotLocationsCombo.addItem(str(i))

        # add assetButton action
        addAsset_bttn.clicked.connect(self.addAsset)

        # add context menu to Assets
        self.assetsTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assetsTree.customContextMenuRequested.connect(self.deleteAssetMenu)

        if mode == "edit":
            self.editShotMode()

    def refreshContentList(self):
        pass

    def editShotMode(self):
        self.setWindowTitle("Edit Current Shot")
        shotNumber = str(self.shotListView.currentItem().text())
        self.shotNumberField.setText(shotNumber)
        self.shotNumberField.setEnabled(False)

        # get shot range
        shotRootFolder = config.rootFolder + shotNumber + "/"
        shotDataFile = shotRootFolder + "_shotData/shotData.json"
        shotData = jsonReader.jsonRead(shotDataFile)
        assets = shotData["assets"]
        shotRange = shotData["shotRange"]
        location = shotData["location"]

        self.shotRangeField.setText(shotRange)
        index = self.shotLocationsCombo.findText(location)
        self.shotLocationsCombo.setCurrentIndex(index)

        for i in assets:
            self.fillUpAssetList(i, self.assetsTree)

        # edit button
        self.createShot_bttn.setText("Edit Current Shot")

    def createShot(self):
        # check required fields
        if not self.shotNumberField.text():
            mc.warning("Give a shot number.")
            return

        if not self.shotRangeField.text():
            mc.warning("Give a shot range.")
            return

        if self.assetsTree.topLevelItemCount() == 0:
            mc.warning("Add items to your shot.")
            return

        shotRootFolder = config.rootFolder
        shotFolder = shotRootFolder + str(self.shotNumberField.text())
        if self.mode == "new":
            # make shot folders if not exists
            if not os.path.exists(shotFolder):
                os.makedirs(shotFolder)

            # create subfolders
            subfolderList = ["_anim", "_shotData", "_shotblast"]

            for i in subfolderList:
                if not os.path.exists(shotFolder + "/" + i):
                    os.makedirs(shotFolder + "/" + i)

        # write out json data with shot info
        self.saveJson(shotFolder + "/_shotData/")

        # add shot number to shot list view
        if self.mode == "new":
            self.shotListView.addItem(str(self.shotNumberField.text()))


        self.close()

    def fontSize(self, size, widget):
        font = QtGui.QFont()
        font.setPointSize(size)
        widget.setFont(font)

    def saveJson(self, path):
        shotData = {}

        shotData["shotNumber"] = str(self.shotNumberField.text())
        shotData["shotRange"] = str(self.shotRangeField.text())
        shotData["location"] = str(self.shotLocationsCombo.currentText())

        assetList = []
        ignoreList = ["CAST", "SETS", "PROPS"]
        for item in self.assetsTree.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
            if not item.text(0) in ignoreList:
                assetList.append(item.text(0))

        shotData["assets"] = assetList


        # refresh contentsTreeView
        if self.mode == "edit":
            self.contentsTreeView.clear()
            for i in shotData["assets"]:
                self.fillUpAssetList(i, self.contentsTreeView)

        # write out json file
        filename = path + "shotData.json"
        jsonData = json.dumps(shotData, indent=4)
        fd = open(filename, 'w')
        fd.write(jsonData)
        fd.close()

    def deleteAssetMenu(self, point):
        menu = QtGui.QMenu()

        deleteAssetMenu = menu.addAction("Remove Asset")

        # connect menu actions
        deleteAssetMenu.triggered.connect(self.deleteAssetAction)

        # show menu
        menu.exec_(self.assetsTree.mapToGlobal(point))

    def deleteAssetAction(self):
        for item in self.assetsTree.selectedItems():
            (item.parent() or root).removeChild(item)

    def autoCompletter(self):
        assets = getAssets.getAssets()
        model = QtGui.QStringListModel()
        model.setStringList(assets)

        completter = QtGui.QCompleter()
        completter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completter.setModel(model)
        self.addAssetField.setCompleter(completter)

    def addAsset(self):
        # get the text from addAsset field
        assetName = self.addAssetField.text()

        # clear addAsset field text
        self.addAssetField.setText("")

        self.fillUpAssetList(assetName, self.assetsTree)

    def fillUpAssetList(self, assetName, treeView):
        # get asset category
        category = findAssetCategory.findCategory(assetName)

        # create asset category if not exists
        if not treeView.findItems( category, QtCore.Qt.MatchContains):
            # add category to TreeView if not there
            root = QtGui.QTreeWidgetItem(treeView, [category])
            root.setExpanded(True)
            root.setForeground(0,QtGui.QBrush(QtGui.QColor("#ADD8E6")))
            childItem = QtGui.QTreeWidgetItem(root, [assetName])
            childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("#E9967A")))
        else:
            # find category item in list
            root = treeView.findItems( category, QtCore.Qt.MatchContains)[0]
            childItem = QtGui.QTreeWidgetItem(root, [assetName])
            childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("#E9967A")))