from PySide import QtGui, QtCore
import maya.cmds as mc
import os

from ..utils import getShotData


class AnimationManager(QtGui.QDialog):
    def __init__(self, shotListView):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle("Animation Manager")
        self.resize(700, 500)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.shotListView = shotListView

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        gridLayout = QtGui.QGridLayout()
        mainLayout.addLayout(gridLayout)

        assetFilterFiels = QtGui.QLineEdit()
        assetFilterFiels.setPlaceholderText("Filter Assets...")
        assetsGroupbox = QtGui.QGroupBox("Assets")
        assetsGroupboxLayout = QtGui.QVBoxLayout(assetsGroupbox)
        animationsGroupBox = QtGui.QGroupBox("Stored Animations")
        animationsGroupBoxLayout = QtGui.QVBoxLayout(animationsGroupBox)

        self.assetList = QtGui.QListWidget()
        assetsGroupboxLayout.addWidget(assetFilterFiels)
        assetsGroupboxLayout.addWidget(self.assetList)

        self.animationList = QtGui.QTreeWidget()
        animationsGroupBoxLayout.addWidget(self.animationList)

        gridLayout.addWidget(assetsGroupbox, 0,0)
        gridLayout.addWidget(animationsGroupBox, 0,1)

        # add header text to animationTreeView
        self.animationList.headerItem().setText(0, "File")
        self.animationList.headerItem().setText(1, "Date")
        self.animationList.headerItem().setText(2, "User")

        # get animated assets
        self.listAnimatedAssets()


        self.assetList.itemClicked.connect(self.loadAnimFiles)

    def listAnimatedAssets(self, ):
        animationFolder = getShotData.getShotFolder(self.shotListView) + "_anim"

        for i in os.listdir(animationFolder):
            self.assetList.addItem(i)

    def loadAnimFiles(self):
        # clear contentView
        self.animationList.clear()

        # get anim folder
        animationFolder = getShotData.getShotFolder(self.shotListView) + "_anim"
        assetFolder = animationFolder + "/" + self.assetList.currentItem().text() + "/"
        backupFolder = assetFolder + "_backup/"

        if os.path.exists(backupFolder):
            for i in os.listdir(backupFolder):
                print i