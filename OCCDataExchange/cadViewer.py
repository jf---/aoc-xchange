#!/usr/bin/env python
#
# cadViewer.py
# An embryonic python 3D CAD application with very little functionality.
# Perhaps it could be a starting point for a more elaborate program.
# It may be only useful to facilitate the exploration of pythonOCC syntax.
# The latest  version of this file can be found at:
# https://sites.google.com/site/pythonocc/
#
# Author: Doug Blanding   <dblanding at gmail dot com>
#
# cadViewer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# cadViewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# if not, write to the Free Software Foundation, Inc.
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


from __future__ import absolute_import

import os
import os.path
import sys

import treelib
from OCC import VERSION
from OCC.AIS import AIS_Shape
from OCC.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Geom import Handle_Geom_Plane
from OCC.TopTools import TopTools_ListOfShape
from OCC.TopoDS import topods_Edge, topods_Face

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
from PyQt5 import Qt
from PyQt5.QtCore import QPersistentModelIndex, QModelIndex, pyqtSlot, QPoint, pyqtSignal
from PyQt5.QtWidgets import (QTreeWidget, QMenu, QAbstractItemView, QDockWidget, QLabel, QLineEdit, QMainWindow,
                             QMenuBar, QTreeWidgetItem, QInputDialog, QAction, QApplication, QDesktopWidget,
                             QFileDialog)

from OCCDataExchange.myStepXcafReader import StepXcafImporter

print "OCC version: %s" % VERSION

# 'used_backend' needs to be defined prior to importing qtViewer3D
# if VERSION < "0.16.5":
used_backend = OCC.Display.backend.get_backend()
# elif VERSION == "0.16.5":
#     used_backend = OCC.Display.backend.load_backend()
# else:
#     used_backend = OCC.Display.backend.load_backend()
#     print "OCC Version = %s" % OCC.VERSION

from OCC.Display import qtDisplay
from OCC.Display.backend import get_qt_modules

QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()


# QStringList

class point(object):
    def __init__(self, obj=None):
        self.x = 0
        self.y = 0
        if obj is not None:
            self.set(obj)

    def set(self, obj):
        self.x = obj.x()
        self.y = obj.y()


# Modify qtViewer3d to emit signals
class MyqtViewer3d(qtDisplay.qtViewer3d):
    lmb_pressed = pyqtSignal()

    def mousePressEvent(self, event):
        self.lmb_pressed.emit()
        # print 'LMBPressed signal emitted.'
        self.setFocus()
        self.dragStartPos = point(event.pos())
        self._display.StartRotation(self.dragStartPos.x, self.dragStartPos.y)

    def mouseReleaseEvent(self, event):
        self.lmb_pressed.emit()
        # print 'LMBReleased signal emitted.'
        pt = point(event.pos())
        modifiers = event.modifiers()

        if event.button() == QtCore.Qt.LeftButton:
            pt = point(event.pos())
            if self._select_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._select_area = False
            else:
                # multiple select if shift is pressed
                if modifiers == QtCore.Qt.ShiftModifier:
                    self._display.ShiftSelect(pt.x, pt.y)
                else:
                    # single select otherwise
                    self._display.Select(pt.x, pt.y)
        elif event.button() == QtCore.Qt.RightButton:
            if self._zoom_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.ZoomArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._zoom_area = False


class TreeList(QTreeWidget):  # With 'drag & drop' ; context menu
    """ Display assembly structure
    """

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.header().setHidden(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.connect(self, SIGNAL("customContextMenuRequested(QPoint)"),
        #              self.contextMenu)
        self.popMenu = QMenu(self)

    @pyqtSlot(QPoint)
    def contextMenu(self, point):
        self.menu = QMenu()
        action = self.popMenu.exec_(self.mapToGlobal(point))

    def dropEvent(self, event):
        if event.source() == self:
            QAbstractItemView.dropEvent(self, event)

    def dropMimeData(self, parent, row, data, action):
        if action == Qt.MoveAction:
            return self.moveSelection(parent, row)
        return False

    def moveSelection(self, parent, position):
        # save the selected items
        selection = [QPersistentModelIndex(i)
                     for i in self.selectedIndexes()]
        parent_index = self.indexFromItem(parent)
        if parent_index in selection:
            return False
        # save the drop location in case it gets moved
        target = self.model().index(position, 0, parent_index).row()
        if target < 0:
            target = position
        # remove the selected items
        taken = []
        for index in reversed(selection):
            item = self.itemFromIndex(QModelIndex(index))
            if item is None or item.parent() is None:
                taken.append(self.takeTopLevelItem(index.row()))
            else:
                taken.append(item.parent().takeChild(index.row()))
        # insert the selected items at their new positions
        while taken:
            if position == -1:
                # append the items if position not specified
                if parent_index.isValid():
                    parent.insertChild(
                        parent.childCount(), taken.pop(0))
                else:
                    self.insertTopLevelItem(
                        self.topLevelItemCount(), taken.pop(0))
            else:
                # insert the items at the specified position
                if parent_index.isValid():
                    parent.insertChild(min(target,
                                           parent.childCount()), taken.pop(0))
                else:
                    self.insertTopLevelItem(min(target,
                                                self.topLevelItemCount()), taken.pop(0))
        return True


class MainWindow(QMainWindow):
    def __init__(self, *args):
        apply(QMainWindow.__init__, (self,) + args)
        self.canva = MyqtViewer3d(self)
        self.setCentralWidget(self.canva)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setWindowTitle("Simple CAD App using pythonOCC-%s ('qt' backend)" % VERSION)
        self.resize(1024, 768)

        # -------------------------------------------------------------------------------
        # tree
        # -------------------------------------------------------------------------------

        self.asyPrtTree = TreeList()  # Assy/Part structure (display)
        itemName = ['/', str(0)]
        self.asyPrtTreeRoot = QTreeWidgetItem(self.asyPrtTree, itemName)  # Root Item in TreeView
        self.asyPrtTree.expandItem(self.asyPrtTreeRoot)
        # self.asyPrtTree.itemChanged.connect(self.asyPrtTreeItemChanged)
        self.itemClicked = None  # TreeView item that has been mouse clicked
        self.tree = treelib.Tree()  # Assy/Part Structure (model)
        self.tree.create_node('/', 0, None, {'a': True, 'l': None, 'c': None, 's': None})  # Root Node in TreeModel

        # -------------------------------------------------------------------------------
        # status bar / line edit
        # -------------------------------------------------------------------------------

        # self.unitsLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.lineEdit = QLineEdit()
        self.lineEditStack = []  # list of user inputs
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.lineEdit)
        status.addPermanentWidget(self.unitsLabel)
        status.showMessage("Ready", 5000)

        # -------------------------------------------------------------------------------
        # bind signals
        # -------------------------------------------------------------------------------

        # self.connect(self, SIGNAL("customContextMenuRequested(QPoint)"),
        #              self.contextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        # self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.appendToStack)

        self.lineEdit.returnPressed.connect(self.appendToStack)

        # I need a SIGNAL that will trigger self.dispatch() so subclass qtViewer3d
        # with myqtViewer3d which will emit a signal when the mouse is clicked.
        # self.connect(self.canva, SIGNAL("LMBReleased"), self.lmbClicked)
        self.canva.lmb_pressed.connect(self.lmbClicked)

        self.asyPrtTree.itemClicked.connect(self.asyPrtTreeItemClicked)

        # -------------------------------------------------------------------------------
        # docking
        # -------------------------------------------------------------------------------

        self.treeDockWidget = QDockWidget("Assy/Part Structure", self)
        self.treeDockWidget.setObjectName("treeDockWidget")
        self.treeDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
                                            Qt.RightDockWidgetArea)
        self.treeDockWidget.setWidget(self.asyPrtTree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.treeDockWidget)

        self.popMenu = QMenu(self)
        self._menus = {}
        self._menu_methods = {}
        if not sys.platform == 'darwin':
            self.menu_bar = self.menuBar()
        else:
            # create a parentless menubar see:
            # http://stackoverflow.com/questions/11375176/qmenubar-and-qmenu-doesnt-show-in-mac-os-x?lq=1
            # noticeable is that the menu ( alas ) is created in the topleft of the screen,
            # just next to the apple icon
            # still does ugly things like showing the "Python" menu in bold
            self.menu_bar = QMenuBar()

        # place the window in the center of the screen, at half the screen size
        self.centerOnScreen()
        self.unitsLabel = QLabel()
        self.unitsLabel.setText("Units: mm ")

        self.currentOp = None  # current operation
        self.activePart = None  # OCCpartObject
        self.activePartUID = 0
        self._assyDict = {}  # k = uid, v = Loc
        self._partDict = {}  # k = uid, v = OCCpartObject
        self._nameDict = {}  # k = uid, v = partName
        self._colorDict = {}  # k = uid, v = part display color
        self._transparencyDict = {}
        self._ancestorDict = {}  # k = uid, v = ancestorUID
        self._currentUID = 0
        self.drawList = []  # list of part uid's to be displayed

    ####  PyQt general & menuBar:

    def centerOnScreen(self):
        '''Centers the window on the screen.'''
        resolution = QDesktopWidget().screenGeometry()
        self.move(
            (resolution.width() / 2) - (self.frameSize().width() / 2),
            (resolution.height() / 2) - (self.frameSize().height() / 2)
        )

    def add_menu(self, menu_name):
        _menu = self.menu_bar.addMenu("&" + menu_name)
        self._menus[menu_name] = _menu

    def add_function_to_menu(self, menu_name, text, _callable):
        assert callable(_callable), 'the function supplied is not callable'
        try:
            _action = QAction(text, self)
            # if not, the "exit" action is now shown...
            # Qt is trying so hard to be native cocoa'ish that its a nuisance
            _action.setMenuRole(QAction.NoRole)
            # self.connect(_action, SIGNAL("triggered()"), _callable)
            _action.triggered.connect(_callable)
            self._menus[menu_name].addAction(_action)
        except KeyError:
            raise ValueError('the menu item %s does not exist' % (menu_name))

    #### 'treeView' related methods:

    @pyqtSlot(QPoint)
    def contextMenu(self, point):
        self.menu = QMenu()
        action = self.popMenu.exec_(self.mapToGlobal(point))

    def getPartsInAssy(self, uid):
        if uid not in self._assyDict.keys():
            print "This node is not an assembly"
        else:
            asyPrtTree = []
            leafNodes = self.tree.leaves(uid)
            for node in leafNodes:
                pid = node.identifier
                if pid in self._partDict.keys():
                    asyPrtTree.append(pid)
            return asyPrtTree

    def asyPrtTreeItemClicked(self, item):  # called whenever treeView item is clicked
        self.itemClicked = item  # store item
        if not self.inSync():  # click may have been on checkmark. Update drawList (if needed)
            self.syncDrawListToChecked()
            self.redraw()

    def checkedToList(self):
        """
        Returns list of checked (part) items in treeView
        """
        dl = []
        for item in self.asyPrtTree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState(0) == 2:
                uid = int(item.text(1))
                if uid in self._partDict.keys():
                    dl.append(uid)
        return dl

    def inSync(self):
        """
        Returns True if checked items are in sync with drawList
        """
        if self.checkedToList() == self.drawList:
            return True
        else:
            return False

    def syncDrawListToChecked(self):
        self.drawList = self.checkedToList()

    def syncCheckedToDrawList(self):
        for item in self.asyPrtTree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            itemUid = int(item.text(1))
            if itemUid in self._partDict:
                if itemUid in self.drawList:
                    item.setCheckState(0, Qt.Checked)
                else:
                    item.setCheckState(0, Qt.Unchecked)

    def setActive(self):  # Set item clicked in treeView Active
        item = self.itemClicked
        if item:
            name = item.text(0)
            uid = int(item.text(1))
            if uid in self._partDict:
                self.activePart = self._partDict[uid]
                self.activePartUID = uid
                sbText = "%s [uid=%i] is now the active part" % (name, uid)
            else:
                sbText = "This is an assembly. Click on a part."
            self.asyPrtTree.clearSelection()
            self.itemClicked = None
            self.statusBar().showMessage(sbText, 5000)

    def setTransparent(self):
        item = self.itemClicked
        if item:
            uid = int(item.text(1))
            if uid:
                self._transparencyDict[uid] = 0.6
                self.redraw()
            self.itemClicked = None

    def setOpaque(self):
        item = self.itemClicked
        if item:
            uid = int(item.text(1))
            if uid:
                self._transparencyDict.pop(uid)
                self.redraw()
            self.itemClicked = None

    def editName(self):  # Edit name of item clicked in treeView
        item = self.itemClicked
        sbText = ''  # status bar text
        if item:
            name = item.text(0)
            uid = int(item.text(1))
            prompt = 'Enter new name for part %s' % name
            newName, OK = QInputDialog.getText(self, 'Input Dialog', prompt, text=name)
            if OK:
                item.setText(0, newName)
                sbText = "Part name changed to %s" % newName
                self._nameDict[uid] = newName
        self.asyPrtTree.clearSelection()
        self.itemClicked = None
        # Todo: update name in treeModel
        self.statusBar().showMessage(sbText, 5000)

    ####  CAD model related methods:

    def printCurrUID(self):
        print self._currentUID

    def getNewPartUID(self, OCCpartObject, name="", ancestor=0, color=None):
        """
        Method for assigning a unique ID (serial number) to a new part generated within the application.
        Using that uid as a key, record the part's info in the various dictionaries.
        The process of modifying a part generally involves doing an operation on an existing 'ancestor' part,
        which is not thrown away, but merely removed form the drawlist.
        """
        if ancestor:
            self.drawList.remove(ancestor)  # Remove ancestor from draw list
            if not name:
                name = self._nameDict[ancestor]  # Keep ancestor name
        if not name:
            name = 'Part'  # Default name
        uid = self._currentUID + 1
        self._currentUID = uid
        # Update dictionaries
        self._partDict[uid] = OCCpartObject
        self._nameDict[uid] = name
        if color:
            c = OCC.Display.OCCViewer.color(color.Red(), color.Green(), color.Blue())
        else:
            c = OCC.Display.OCCViewer.color(.2, .1, .1)  # default color
        self._colorDict[uid] = c
        self._ancestorDict[uid] = ancestor
        # add item to treeView
        itemName = [name, str(uid)]
        item = QTreeWidgetItem(self.asyPrtTreeRoot, itemName)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Checked)
        # add node to treeModel
        self.tree.create_node(name,
                              uid,
                              0,
                              {'a': False, 'l': None, 'c': c, 's': OCCpartObject})
        # Add new uid to draw list and sync w/ treeView
        self.drawList.append(uid)
        self.syncCheckedToDrawList()
        # Make new part active
        self.activePartUID = uid
        self.activePart = OCCpartObject
        return uid

    def appendToStack(self):  # text input stack
        self.lineEditStack.append(unicode(self.lineEdit.text()))
        self.lineEdit.clear()
        if self.currentOp:
            self.dispatch()
        else:
            self.lineEditStack.pop()

    def lmbClicked(self):  # call dispatch() only during a CAD operation.
        if self.currentOp:
            self.dispatch()

    def dispatch(self, currOp=None):
        """
        Allows a CAD operation, initially triggered by a toolbar button,
        to be repeatedly called by user screen picks and text inputs
        until the operation is complete.
        """
        if not currOp:
            currOp = self.currentOp
            initial = False  # called without a parameter
        else:
            self.currentOp = currOp
            initial = True  # called by a triggered button (w/ arg)
        print "%s dispatched" % currOp
        if initial:
            func = "%s(True)" % currOp
        else:
            func = "%s(False)" % currOp
        eval(func)

    def endCurrOp(self):
        self.currentOp = None
        self.canva._display.SetSelectionModeShape()

    def clearStack(self):
        self.lineEditStack = []

    ####  3D display management & (Show / Hide) methods:

    def fitAll(self):
        self.canva._display.FitAll()

    def eraseAll(self):
        context = self.canva._display.Context
        context.RemoveAll()
        win.drawList = []
        self.syncCheckedToDrawList()

    def redraw(self):
        context = self.canva._display.Context
        context.RemoveAll()
        context.SetAutoActivateSelection(False)
        for uid in self.drawList:
            if uid in self._transparencyDict.keys():
                transp = self._transparencyDict[uid]
            else:
                transp = 0
            color = self._colorDict[uid]
            aisShape = AIS_Shape(self._partDict[uid])
            h_aisShape = aisShape.GetHandle()
            context.Display(h_aisShape)
            context.SetColor(h_aisShape, color)
            context.SetTransparency(h_aisShape, transp)
            context.HilightWithColor(h_aisShape, OCC.Quantity.Quantity_NOC_BLACK)
        print 'Redrawing'

    def drawAll(self):
        self.drawList = []
        for k in self._partDict.keys():
            self.drawList.append(k)
        self.syncCheckedToDrawList()
        self.redraw()

    def drawOnlyActivePart(self):
        self.eraseAll()
        uid = self.activePartUID
        self.drawList.append(uid)
        self.canva._display.DisplayShape(self._partDict[uid])
        self.syncCheckedToDrawList()
        self.redraw()

    def drawOnlyPart(self, key):
        self.eraseAll()
        self.drawList.append(key)
        self.syncCheckedToDrawList()
        self.redraw()

    def drawAddPart(self, key):  # Add part to drawList
        self.drawList.append(key)
        self.syncCheckedToDrawList()
        self.redraw()

    def drawHidePart(self, key):  # Remove part from drawList
        if key in self.drawList:
            self.drawList.remove(key)
            self.syncCheckedToDrawList()
            self.redraw()

            ####  Step Load / Save methods:

    def loadStep(self):
        """
        Load a step file and bring it in as a treelib.Tree() structure
        Unpack this structure to:
        1. Populate the various dictionaries: assy, part, name, color and
        2. Build the Part/Assy structure (treeView), and
        3. Paste the loaded tree onto win.tree (treeModel)
        """
        prompt = 'Select STEP file to import'
        fname = QFileDialog.getOpenFileName(None, prompt, './', "STEP files (*.stp *.STP *.step)")
        if not fname:
            print "Load step cancelled"
            return
        fname = str(fname)
        name = os.path.basename(fname).split('.')[0]
        nextUID = self._currentUID
        stepImporter = StepXcafImporter(fname, nextUID)
        tree = stepImporter.tree
        partTreeDict = {}  # uid:asyPrtTreeItem (used temporarily during unpack)
        for uid in tree.expand_tree(mode=self.tree.DEPTH):
            node = tree.get_node(uid)
            name = node.tag
            itemName = [name, str(uid)]
            parentUid = node.bpointer
            if node.data['a']:  # Assembly
                if not parentUid:  # This is the top level item
                    parentItem = self.asyPrtTreeRoot
                else:
                    parentItem = partTreeDict[parentUid]
                item = QTreeWidgetItem(parentItem, itemName)
                item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                self.asyPrtTree.expandItem(item)
                partTreeDict[uid] = item
                Loc = node.data['l']  # Location object
                self._assyDict[uid] = Loc
            else:  # Part
                # add item to asyPrtTree treeView
                if not parentUid:  # This is the top level item
                    parentItem = self.asyPrtTreeRoot
                else:
                    parentItem = partTreeDict[parentUid]
                item = QTreeWidgetItem(parentItem, itemName)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Checked)
                partTreeDict[uid] = item
                color = node.data['c']
                shape = node.data['s']
                # Update dictionaries
                self._partDict[uid] = shape
                self._nameDict[uid] = name
                if color:
                    c = OCC.Display.OCCViewer.color(color.Red(), color.Green(), color.Blue())
                else:
                    c = OCC.Display.OCCViewer.color(.2, .1, .1)  # default color
                self._colorDict[uid] = c
                self.activePartUID = uid  # Set as active part
                self.activePart = shape
                self.drawList.append(uid)  # Add to draw list
        self.tree.paste(0, tree)  # Paste tree onto win.tree root
        klist = self._partDict.keys()
        klist.sort()
        klist.reverse()
        maxUID = klist[0]
        self._currentUID = maxUID
        self.redraw()


# Make Body Functions...

def makeBox():
    name = 'Box'
    myBody = BRepPrimAPI_MakeBox(60, 60, 50).Shape()
    uid = win.getNewPartUID(myBody, name=name)
    win.redraw()


def makeCyl():
    name = 'Cylinder'
    myBody = BRepPrimAPI_MakeCylinder(40, 80).Shape()
    uid = win.getNewPartUID(myBody, name=name)
    win.redraw()


# Make Bottle Stuff...

def face_is_plane(face):
    """
    Returns True if the TopoDS_Shape is a plane, False otherwise
    """
    hs = OCC.BRep.BRep_Tool_Surface(face)
    downcast_result = Handle_Geom_Plane.DownCast(hs)
    # The handle is null if downcast failed or is not possible, that is to say the face is not a plane
    if downcast_result.IsNull():
        return False
    else:
        return True


def geom_plane_from_face(aFace):
    """
    Returns the geometric plane entity from a planar surface
    """
    return Handle_Geom_Plane.DownCast(OCC.BRep.BRep_Tool_Surface(aFace)).GetObject()


# Geometry modification functons...
def shell(initial=True):
    if initial:
        display.selected_shape = None
        display.SetSelectionModeFace()
    statusText = "First select face to remove then specify shell thickness."
    win.statusBar().showMessage(statusText)
    workPart = win.activePart
    wrkPrtUID = win.activePartUID
    aShape = display.GetSelectedShape()
    win.lineEdit.setFocus()
    if len(win.lineEditStack) and aShape:
        text = win.lineEditStack.pop()
    else:
        return
    shellT = float(text)
    aFace = topods_Face(aShape)
    facesToRemove = TopTools_ListOfShape()
    facesToRemove.Append(aFace)
    newPart = BRepOffsetAPI_MakeThickSolid(workPart, facesToRemove, -shellT, 1.e-3).Shape()
    win.getNewPartUID(newPart, ancestor=wrkPrtUID)
    win.statusBar().showMessage('Shell operation complete')
    win.endCurrOp()  # clear current operation
    win.redraw()


def fillet(initial=True):
    if initial:
        display.selected_shape = None
        display.selected_shapes = None
        display.SetSelectionModeEdge()
    statusText = "Select edge(or shift-select edges) to fillet then enter fillet radius."
    win.statusBar().showMessage(statusText)
    win.lineEdit.setFocus()
    workPart = win.activePart
    wrkPrtUID = win.activePartUID
    aShape = display.GetSelectedShape()  # single edge selected
    shapes = display.GetSelectedShapes()  # multiple edges selected
    edges = []
    if shapes:  # multiple selection
        for shape in shapes:
            anEdge = topods_Edge(shape)
            edges.append(anEdge)
    elif aShape:  # single selection
        anEdge = topods_Edge(aShape)
        edges.append(anEdge)
    if edges and len(win.lineEditStack):
        text = win.lineEditStack.pop()
        filletR = float(text)
        mkFillet = BRepFilletAPI_MakeFillet(workPart)
        for edge in edges:
            mkFillet.Add(filletR, edge)
        newPart = mkFillet.Shape()
        win.getNewPartUID(newPart, ancestor=wrkPrtUID)
        win.statusBar().showMessage('Fillet operation complete')
        win.endCurrOp()  # clear current operation
        win.redraw()


####  Info & Utility functions:

def printActPart():
    uid = win.activePartUID
    if uid:
        name = win._nameDict[uid]
        print "%s [uid=%i]" % (name, int(uid))
    else:
        print None


def printNameDict():
    print win._nameDict


def printPartDict():
    print win._partDict


def printCurrOp():
    print win.currentOp


def printDrawList():
    print win.drawList


def printInSync():
    print win.inSync()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.add_menu('File')
    win.add_function_to_menu('File', "Load STEP", win.loadStep)
    win.add_menu('Make Bodies')
    win.add_function_to_menu('Make Bodies', "Box", makeBox)
    win.add_function_to_menu('Make Bodies', "Cylinder", makeCyl)
    win.add_menu('modify Active Part')
    win.add_function_to_menu('modify Active Part', "Shell", lambda k='shell': win.dispatch(k))
    win.add_function_to_menu('modify Active Part', "fillet", lambda k='fillet': win.dispatch(k))
    win.add_menu('info')
    win.add_function_to_menu('info', "print current UID", win.printCurrUID)
    win.add_function_to_menu('info', "print active part", printActPart)
    win.add_function_to_menu('info', "print partDict", printPartDict)
    win.add_function_to_menu('info', "print nameDict", printNameDict)
    win.add_function_to_menu('info', "print current op", printCurrOp)
    win.add_function_to_menu('info', "print drawList", printDrawList)
    win.add_function_to_menu('info', "Clear Stack", win.clearStack)
    win.add_function_to_menu('info', "End current op", win.endCurrOp)
    win.add_function_to_menu('info', "Checked inSync w/ DL?", printInSync)

    win.popMenu.addAction('Fit All', win.fitAll)
    win.popMenu.addAction('Redraw', win.redraw)
    win.popMenu.addAction('Hide All', win.eraseAll)
    win.popMenu.addAction('Draw All', win.drawAll)
    win.popMenu.addAction('Draw Only Active Part', win.drawOnlyActivePart)

    win.asyPrtTree.popMenu.addAction('Set Active', win.setActive)
    win.asyPrtTree.popMenu.addAction('Make Transparent', win.setTransparent)
    win.asyPrtTree.popMenu.addAction('Make Opaque', win.setOpaque)
    win.asyPrtTree.popMenu.addAction('Edit Name', win.editName)
    win.show()
    win.canva.InitDriver()
    display = win.canva._display
    win.raise_()  # bring the app to the top
    app.exec_()
