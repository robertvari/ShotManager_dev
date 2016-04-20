import maya.cmds as mc
from PySide import QtGui, QtCore
import maya.OpenMayaUI as apiUI
import shiboken
import os
import json
from functools import partial

from modules import saveAnim
from modules import createShot
from utils import config
from utils import findAssetCategory
from modules import buildShot
from utils import jsonReader
from utils import saveSetsData
reload(saveAnim)
reload(saveSetsData)
reload(jsonReader)
reload(buildShot)
reload(findAssetCategory)
reload(config)
reload(createShot)

def getMayaWindow():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtGui.QWidget)

scriptPath = os.path.dirname(__file__)
version = "0.1"

class ShotManager(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ShotManager, self).__init__(parent=getMayaWindow())
        # self.setSizeGripEnabled(True)
        self.setObjectName("shotManagerWindow")
        self.setWindowTitle("Shot Manager v%s" % version)
        self.resize(1100, 950)

        # menubar ----------------------------------------------------
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 18))

        editManu = QtGui.QMenu(self.menubar)
        editManu.setTitle("Edit")

        saveManu = QtGui.QMenu(self.menubar)
        saveManu.setTitle("Save Data...")

        animationMenu = QtGui.QMenu(self.menubar)
        animationMenu.setTitle("Animation")

        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        createNew_menu = QtGui.QAction(self)
        editCurrent_menu = QtGui.QAction(self)
        copyCurrent_menu = QtGui.QAction(self)
        createNew_menu.setText("Create New Shot")
        editCurrent_menu.setText("Edit Current...")
        copyCurrent_menu.setText("Copy Current")
        editManu.addAction(createNew_menu)
        editManu.addAction(editCurrent_menu)
        editManu.addAction(copyCurrent_menu)
        self.menubar.addAction(editManu.menuAction())
        self.menubar.addAction(saveManu.menuAction())
        self.menubar.addAction(animationMenu.menuAction())

        # save data menu actions
        saveSets_menu = QtGui.QAction(self)
        saveSets_menu.setText("Update SETS Posittion")

        saveManu.addAction(saveSets_menu)

        # animation menu
        saveAnimation_menu = QtGui.QAction(self)
        saveAnimation_menu.setText("Save Animation for selected")
        importAnimation_menu = QtGui.QAction(self)
        importAnimation_menu.setEnabled(False)
        importAnimation_menu.setText("Import Animation for selected")
        animManager_menu = QtGui.QAction(self)
        animManager_menu.setText("Animation Manager")
        animManager_menu.setEnabled(False)
        saveCamera_menu = QtGui.QAction(self)
        saveCamera_menu.setText("Save Camera Animation")
        importCamera_menu = QtGui.QAction(self)
        importCamera_menu.setEnabled(False)
        importCamera_menu.setText("Import Camera Animation")
        animationMenu.addAction(saveAnimation_menu)
        animationMenu.addAction(importAnimation_menu)
        animationMenu.addAction(animManager_menu)
        animationMenu.addSeparator()
        animationMenu.addAction(saveCamera_menu)
        animationMenu.addAction(importCamera_menu)


        createNew_menu.triggered.connect(partial(self.openCreateShotWindow, mode="new"))
        editCurrent_menu.triggered.connect(partial(self.openCreateShotWindow, mode="edit"))
        copyCurrent_menu.triggered.connect(partial(self.openCreateShotWindow, mode="copy"))

        # menubar ----------------------------------------------------

        self.gui = GUI(self)
        self.setCentralWidget(self.gui)

        # save sets data action
        saveSets_menu.triggered.connect(partial(saveSetsData.sceneData, self.gui.shotListView))

        # save animation action
        saveAnimation_menu.triggered.connect(partial(saveAnim.saveAnimation, self.gui.shotListView))
        saveCamera_menu.triggered.connect(partial(saveAnim.saveAnimation, self.gui.shotListView, cameraAnim=True))

    def openCreateShotWindow(self, mode):
        self.createShotWindow = createShot.CreateShotWindow(self.gui.shotListView, self.gui.contentsTreeView, mode)
        self.createShotWindow.show()

class GUI(QtGui.QWidget):
    def __init__(self, parent):
        super(GUI, self).__init__(parent)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        mainGridlayout = QtGui.QGridLayout()
        mainLayout.addLayout(mainGridlayout)

        shotslayout = QtGui.QVBoxLayout()
        shotDetailsLayout = QtGui.QVBoxLayout()
        mainGridlayout.addLayout(shotslayout, 0,0)
        mainGridlayout.addLayout(shotDetailsLayout, 0,1)

        # shots groupBox
        shotsGroupBox = QtGui.QGroupBox("Shots")
        shotsGroupBoxlayout = QtGui.QVBoxLayout(shotsGroupBox)
        shotslayout.addWidget(shotsGroupBox)

        shotFilter_line = QtGui.QLineEdit()
        shotFilter_line.setPlaceholderText("Filter shots by name...")
        shotsGroupBoxlayout.addWidget(shotFilter_line)

        self.shotListView = QtGui.QListWidget()
        self.fontSize(11, self.shotListView)
        shotsGroupBoxlayout.addWidget(self.shotListView)

        # shot states
        shotStates = ["WIP", "LEVEL_1", "LEVEL_2", "LEVEL_3"]
        shotStateGridLayout = QtGui.QGridLayout()
        shotState_lbl = QtGui.QLabel("Shot Version:")
        shotState_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.shotStateCombo = QtGui.QComboBox()
        for i in shotStates: self.shotStateCombo.addItem(i)
        shotStateGridLayout.addWidget(shotState_lbl, 0,0)
        shotStateGridLayout.addWidget(self.shotStateCombo, 0,1)
        shotsGroupBoxlayout.addLayout(shotStateGridLayout)

        buildShot_bttn = QtGui.QPushButton("Build Shot")
        addAsset_bttn = QtGui.QPushButton("Add Asset to Current Scene")
        shotsGroupBoxlayout.addWidget(buildShot_bttn)
        shotsGroupBoxlayout.addWidget(addAsset_bttn)

        self.fillUpShotList()
        self.shotListView.itemClicked.connect(self.fillUpContents)

        # contents groupBox
        contentsGroupBox = QtGui.QGroupBox("Contents")
        contentsGroupBoxLayout = QtGui.QVBoxLayout(contentsGroupBox)
        shotDetailsLayout.addWidget(contentsGroupBox)

        self.contentsTreeView = QtGui.QTreeWidget()
        self.contentsTreeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.contentsTreeView.setHeaderHidden(True)
        contentsGroupBoxLayout.addWidget(self.contentsTreeView)
        self.fontSize(10, self.contentsTreeView)

        # shotblasts groupBox
        shotblastsGroupBox = QtGui.QGroupBox("Shotblasts")
        shotblastsGroupBoxLayout = QtGui.QVBoxLayout(shotblastsGroupBox)
        shotDetailsLayout.addWidget(shotblastsGroupBox)

        self.shotblastList = QtGui.QTreeView()
        self.shotblastList.doubleClicked.connect(self.openShotblast)
        self.fontSize(11, self.shotblastList)
        shotblastsGroupBoxLayout.addWidget(self.shotblastList)

        # build shot action
        buildShot_bttn.clicked.connect(partial(buildShot.buildShot, self.shotListView, self.contentsTreeView, self.shotStateCombo))
        addAsset_bttn.clicked.connect(partial(buildShot.addAssetToScene, self.shotListView, self.contentsTreeView, self.shotStateCombo))

    def openShotblast(self):
        index = self.shotblastList.selectedIndexes()[0]
        filename = self.model.filePath(index)
        os.system("start "+filename)

    def fontSize(self, size, widget):
        font = QtGui.QFont()
        font.setPointSize(size)
        widget.setFont(font)

    def fillUpShotList(self):
        # get shot list from shot folder
        shotRootFolder = config.rootFolder

        shotList = os.listdir(shotRootFolder)

        for i in shotList:
            self.shotListView.addItem(i)

    def fillUpShotblastsList(self):
        rootFolder = config.rootFolder + self.shotListView.currentItem().text() + "/_shotblast"
        filters = ["*.mov"]
        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(rootFolder)
        self.model.setNameFilterDisables(False)
        self.model.setNameFilters(filters)

        self.shotblastList.setModel(self.model)
        self.shotblastList.setRootIndex(self.model.index(rootFolder))
        self.model.setFilter(QtCore.QDir.Files)

        self.shotblastList.setColumnWidth(0, 200)

        self.shotblastList.hideColumn(2)

    def fillUpContents(self):
        # clear contentView
        self.contentsTreeView.clear()

        # get shot number
        shotName = self.shotListView.currentItem().text()

        # get content data
        shotDataFile = config.rootFolder + shotName + "/_shotData/shotData.json"

        data = jsonReader.jsonRead(shotDataFile)

        assets = data["assets"]

        for i in assets:
            assetName = i
            category = findAssetCategory.findCategory(assetName)

            # create asset category if not exists
            if not self.contentsTreeView.findItems( category, QtCore.Qt.MatchContains):
                # add category to TreeView if not there
                root = QtGui.QTreeWidgetItem(self.contentsTreeView, [category])
                root.setExpanded(True)
                root.setForeground(0,QtGui.QBrush(QtGui.QColor("#ADD8E6")))
                childItem = QtGui.QTreeWidgetItem(root, [assetName])
                childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("#E9967A")))
            else:
                # find category item in list
                root = self.contentsTreeView.findItems( category, QtCore.Qt.MatchContains)[0]
                childItem = QtGui.QTreeWidgetItem(root, [assetName])
                childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("#E9967A")))

        # refresh shotblast list view
        self.fillUpShotblastsList()


if mc.window("shotManagerWindow", exists=True):
    mc.deleteUI("shotManagerWindow")

window = ShotManager()
window.show()