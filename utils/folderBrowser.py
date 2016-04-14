from PySide import QtCore, QtGui

class FolderBrowser():
    def __init__(self, rootFolder, parentLayout, filter, model=False):

        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(rootFolder)

        if filter == "folders": self.model.setFilter(QtCore.QDir.NoDotAndDotDot|QtCore.QDir.AllDirs)

        # create treeView
        self.treeView = QtGui.QTreeView()

        if model:
            self.treeView.setModel(self.model)
            self.treeView.setRootIndex(self.model.index(rootFolder))
            self.treeView.setColumnWidth(0, 300)

        for i in range(1,3):self.treeView.hideColumn(i)

        self.setFontSize(self.treeView, 10)

        # add treeView to layout
        parentLayout.addWidget(self.treeView)

    def setFontSize(self, qItem, size):
        font = QtGui.QFont()
        font.setPointSize(size)
        qItem.setFont(font)