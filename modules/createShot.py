from PySide import QtGui, QtCore
import maya.cmds as mc
import json

from ..utils import config
from ..utils import getAssets
from ..utils import findAssetCategory
reload(findAssetCategory)
reload(getAssets)
reload(config)

class CreateShotWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle("Create New Shot")
        self.resize(400, 500)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

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
        shotLocationsCombo = QtGui.QComboBox()
        self.addAssetField = QtGui.QLineEdit()
        self.autoCompletter()
        addAsset_bttn = QtGui.QPushButton("Add")
        addAssetLayout = QtGui.QHBoxLayout()
        addAssetLayout.addWidget(self.addAssetField)
        addAssetLayout.addWidget(addAsset_bttn)
        self.assetsTree = QtGui.QTreeWidget()
        self.shotRangeField = QtGui.QLineEdit()
        createShot_bttn = QtGui.QPushButton("Create Shot")

        createShot_bttn.clicked.connect(self.createShot)

        self.assetsTree.setHeaderHidden(True)

        # add items to layout
        gridlayout.addWidget(shotNumber_lbl, 0,0)
        gridlayout.addWidget(self.shotNumberField, 0,1)
        gridlayout.addWidget(shotRange_lbl, 1,0)
        gridlayout.addWidget(self.shotRangeField, 1,1)
        gridlayout.addWidget(shotLocation_lbl, 2,0)
        gridlayout.addWidget(shotLocationsCombo, 2,1)
        gridlayout.addWidget(addEsset_lbl, 3,0)
        gridlayout.addLayout(addAssetLayout, 3,1)
        gridlayout.addWidget(assets_lbl, 4,0)
        gridlayout.addWidget(self.assetsTree, 4,1)

        mainLayout.addWidget(createShot_bttn)

        # get scenes data and add items into locations combo
        scenesDataFile = config.shotLocationsPath
        with open(scenesDataFile) as data_file:
            scenesData = json.load(data_file)

        locationList = []
        for key, value in scenesData.iteritems():
            locationList.append(key)

        for i in sorted(locationList):
            shotLocationsCombo.addItem(str(i))

        # add assetButton action
        addAsset_bttn.clicked.connect(self.addAsset)

        # add context menu to Assets
        self.assetsTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assetsTree.customContextMenuRequested.connect(self.deleteAssetMenu)

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

        # make shot folders if not exists


        self.close()

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
        completter.setModel(model)
        self.addAssetField.setCompleter(completter)

    def addAsset(self):
        # get the text from addAsset field
        assetName = self.addAssetField.text()

        # clear addAsset field text
        self.addAssetField.setText("")

        # get asset category
        category = findAssetCategory.findCategory(assetName)

        # self.assetsTree.invisibleRootItem()

        # create asset category if not exists
        if not self.assetsTree.findItems( category, QtCore.Qt.MatchContains):
            # add category to TreeView if not there
            root = QtGui.QTreeWidgetItem(self.assetsTree, [category])
            root.setExpanded(True)
            root.setForeground(0,QtGui.QBrush(QtGui.QColor("#ADD8E6")))
            childItem = QtGui.QTreeWidgetItem(root, [assetName])
            childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("#E9967A")))
        else:
            # find category item in list
            root = self.assetsTree.findItems( category, QtCore.Qt.MatchContains)[0]
            childItem = QtGui.QTreeWidgetItem(root, [assetName])
            childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("#E9967A")))