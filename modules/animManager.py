from PySide import QtGui, QtCore
import maya.cmds as mc
import os
import time
from functools import partial

from ..utils import getShotData
import importAnim
reload(importAnim)

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

        masterAnim_bttn = QtGui.QPushButton("Load Master Animation")
        animationsGroupBoxLayout.addWidget(masterAnim_bttn)

        gridLayout.addWidget(assetsGroupbox, 0,0)
        gridLayout.addWidget(animationsGroupBox, 0,1)

        # add header text to animationTreeView
        self.animationList.headerItem().setText(0, "File")
        self.animationList.headerItem().setText(1, "Date")
        self.animationList.header().resizeSection(0,200)

        # get animated assets
        self.listAnimatedAssets()

        self.assetList.itemClicked.connect(self.loadAnimFiles)

        # doubleclick event for animList
        self.animationList.doubleClicked.connect(partial(self.importAnimation, False))

        # load master animation
        masterAnim_bttn.clicked.connect(partial(self.importAnimation, True))

    def importAnimation(self, masterAnim, *args):
        shotPath = getShotData.getShotFolder(self.shotListView)
        assetName = self.assetList.currentItem().text()
        backupAnimPath = shotPath + "_anim/" + assetName + "/_backup/" + self.animationList.currentItem().text(0)

        # clean anim curves from scene
        self.cleanAnimCurves(assetName)

        # import animation from backup
        if masterAnim:
            if "camera" in assetName:
                backupAnimPath = shotPath + "_anim/" + assetName + "/shot_" + shotPath.split("/")[-2] + "_anim.ma"
                importAnim.importAnim(shotPath, assetName, backupAnim=backupAnimPath)
            else:
                importAnim.importAnim(shotPath, assetName)
        else:
            importAnim.importAnim(shotPath, assetName, backupAnim=backupAnimPath)

    def cleanAnimCurves(self, assetName):
        animCurves = mc.ls(assetName + ":*", type="animCurve")
        for i in animCurves:
            mc.delete(i)

    def listAnimatedAssets(self, ):
        animationFolder = getShotData.getShotFolder(self.shotListView) + "_anim"

        for i in os.listdir(animationFolder):
            self.assetList.addItem(i)

    def loadAnimFiles(self):
        self.animationList.setSortingEnabled(False)

        # clear contentView
        self.animationList.clear()

        # get anim folder
        animationFolder = getShotData.getShotFolder(self.shotListView) + "_anim"
        assetFolder = animationFolder + "/" + self.assetList.currentItem().text() + "/"
        backupFolder = assetFolder + "_backup/"


        if os.path.exists(backupFolder):
            counter = 0
            for i in os.listdir(backupFolder):
                fileInfo = self.getFileInfo(backupFolder, i)

                item = QtGui.QTreeWidgetItem(self.animationList)
                self.animationList.topLevelItem(counter).setText(0, i)
                self.animationList.topLevelItem(counter).setText(1, fileInfo)

                counter +=1

        self.animationList.setSortingEnabled(True)
        self.animationList.sortByColumn(1, QtCore.Qt.SortOrder(0))

    def getFileInfo(self, folder, file):
        fileTime = time.strftime('%Y/%m/%d %H:%m:%S', time.gmtime(os.path.getmtime(folder + file)))

        return fileTime