import maya.cmds as mc
from PySide import QtGui, QtCore
import maya.OpenMayaUI as apiUI
import shiboken
import os

from modules import createShot
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

        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        createNew_menu = QtGui.QAction(self)
        editCurrent_menu = QtGui.QAction(self)
        copyCurrent_menu = QtGui.QAction(self)
        deleteShot_menu = QtGui.QAction(self)
        createNew_menu.setText("Create New Shot")
        editCurrent_menu.setText("Edit Current...")
        copyCurrent_menu.setText("Copy Current")
        deleteShot_menu.setText("Delete Shot")
        editManu.addAction(createNew_menu)
        editManu.addAction(editCurrent_menu)
        editManu.addAction(copyCurrent_menu)
        editManu.addAction(deleteShot_menu)
        self.menubar.addAction(editManu.menuAction())

        createNew_menu.triggered.connect(self.openCreateShotWindow)
        # menubar ----------------------------------------------------

        self.gui = GUI(self)
        self.setCentralWidget(self.gui)

    def openCreateShotWindow(self):
        self.createShotWindow = createShot.CreateShotWindow()
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

        shotListView = QtGui.QListView()
        shotsGroupBoxlayout.addWidget(shotListView)

        # contents groupBox
        contentsGroupBox = QtGui.QGroupBox("Contents")
        contentsGroupBoxLayout = QtGui.QVBoxLayout(contentsGroupBox)
        shotDetailsLayout.addWidget(contentsGroupBox)

        contentsTreeView = QtGui.QTreeWidget()
        contentsGroupBoxLayout.addWidget(contentsTreeView)

        # shotblasts groupBox
        shotblastsGroupBox = QtGui.QGroupBox("Shotblasts")
        shotblastsGroupBoxLayout = QtGui.QVBoxLayout(shotblastsGroupBox)
        shotDetailsLayout.addWidget(shotblastsGroupBox)

        shotblastList = QtGui.QListView()
        shotblastsGroupBoxLayout.addWidget(shotblastList)



if mc.window("shotManagerWindow", exists=True):
    mc.deleteUI("shotManagerWindow")

window = ShotManager()
window.show()