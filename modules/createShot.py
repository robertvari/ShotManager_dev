from PySide import QtGui, QtCore
import json

from ..utils import config
from ..utils import getAssets
reload(getAssets)
reload(config)

class CreateShotWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle("Create New Shot")
        self.resize(400, 500)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        print config.shotLocationsPath

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        gridlayout = QtGui.QGridLayout()
        mainLayout.addLayout(gridlayout)

        # labels
        shotNumber_lbl = QtGui.QLabel("Shot Number:")
        shotLocation_lbl = QtGui.QLabel("Shot Location:")
        addEsset_lbl = QtGui.QLabel("Add Asset:")
        assets_lbl = QtGui.QLabel("Assets:")
        shotRange_lbl = QtGui.QLabel("Shot Range:")

        # items
        shotNumberField = QtGui.QLineEdit()
        shotLocationsCombo = QtGui.QComboBox()
        self.addAssetField = QtGui.QLineEdit()
        self.autoCompletter()
        addAsset_bttn = QtGui.QPushButton("Add")
        addAssetLayout = QtGui.QHBoxLayout()
        addAssetLayout.addWidget(self.addAssetField)
        addAssetLayout.addWidget(addAsset_bttn)
        self.assetsTree = QtGui.QTreeWidget()
        shotRangeField = QtGui.QLineEdit()
        createShot_bttn = QtGui.QPushButton("Create Shot")


        self.assetsTree.headerItem().setText(0, "Assets")

        # add items to layout
        gridlayout.addWidget(shotNumber_lbl, 0,0)
        gridlayout.addWidget(shotNumberField, 0,1)
        gridlayout.addWidget(shotRange_lbl, 1,0)
        gridlayout.addWidget(shotRangeField, 1,1)
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

        # add asset to TreeView if not there
        assetItem = QtGui.QTreeWidgetItem(self.assetsTree)
        self.assetsTree.topLevelItem(0).setText(0, assetName)