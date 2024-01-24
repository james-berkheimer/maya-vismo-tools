#!/usr/bin/env python

#------------------------------------------------------------------------------
# VISMO Render Tool v1.0.0, James Berkheimer
#------------------------------------------------------------------------------

# Standard library imports
import os
import sys
import traceback
from functools import partial

# Third party imports
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.mel as mel

version = cmds.about(version=True)
if int(version) < 2019:
    from Qt import QtCore, QtWidgets, QtGui

    ## Checking QT binding for compatibility
    from Qt import __binding__

    if __binding__ in ('PySide2', 'PyQt5'):
        print('Qt5 binding available')
    elif __binding__ in ('PySide', 'PyQt4'):
        print('Qt4 binding available.')
    else:
        print('No Qt binding available.')
else:
    from PySide2 import QtCore, QtWidgets, QtGui

# Local application imports
import vismo.render as render
import vismo.setup as setup
import vismo.tools as tools

print("----------------------------------------------------------------")
print("--------         Running VISMO_MDD_Tool %s        ------------" %
      (version))
print("----------------------------------------------------------------")

# Establishing global icon path
scriptDir = os.path.dirname(os.path.abspath(__file__))
scriptDir = os.path.dirname(scriptDir)
icon_path = scriptDir + "\\icons\\"

# Establishing renderer being used
renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")


def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


class RenderTool_UI(QtWidgets.QMainWindow):
    onClose = QtCore.Signal()

    def __init__(self, parent=_maya_main_window()):
        super(RenderTool_UI, self).__init__(parent)
        self.setGeometry(300, 300, 300, 100)
        self.setWindowTitle('VISMO RenderTool v0.1.0')
        self.resize(240, 310)

        # Setting initial render environment
        setup.setRenderEnvironment()

        self.render_setup_widget = Render_Setup_Tab(self)
        self.render_submit_widget = Render_Submit_Button(self)

        _widget = QtWidgets.QWidget()
        _layout = QtWidgets.QVBoxLayout(_widget)
        _tabs = QtWidgets.QTabWidget()
        _tabs.addTab(self.render_setup_widget, "Render Setup")
        _layout.addWidget(_tabs)
        _layout.addWidget(self.render_submit_widget)
        self.setCentralWidget(_widget)


class Render_Setup_Tab(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Render_Setup_Tab, self).__init__(parent)
        #--------------------------------------------------------------------------
        # Call the group box functions
        #--------------------------------------------------------------------------
        self.renderSetupTab_TopGroupBox()

        #--------------------------------------------------------------------------
        # Set Main layout
        #--------------------------------------------------------------------------
        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addStretch(1)
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topGroupBox, 1, 0)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

    #--------------------------------------------------------------------------
    # Creating Group boxes
    #--------------------------------------------------------------------------
    def renderSetupTab_TopGroupBox(self):
        self.topGroupBox = QtWidgets.QGroupBox()
        spacer = QtWidgets.QLabel("")
        fileType = self.get_fileType()
        yellow_html = "<font color=yellow size=5> <u> </u> {} </font>".format(
            fileType)
        render_filetype_label = QtWidgets.QLabel('File Type:')
        self.render_filetype = QtWidgets.QLabel(yellow_html)
        png08_button = Utl.createButton("&PNG 8-Bit",
                                        partial(self.set_fileType, "PNG08"),
                                        icon_path + "png08.png")
        png16_button = Utl.createButton("&PNG 16-Bit",
                                        partial(self.set_fileType, "PNG16"),
                                        icon_path + "png16.png")
        exr16_button = Utl.createButton("&EXR 16-Bit",
                                        partial(self.set_fileType, "EXR16"),
                                        icon_path + "exr16.png")
        exr32_button = Utl.createButton("&EXR 32-Bit",
                                        partial(self.set_fileType, "EXR32"),
                                        icon_path + "exr32.png")
        exrlayered_button = Utl.createButton(
            "&EXR LAYERED", partial(self.set_fileType, "EXRLAYERED"),
            icon_path + "layeredexr16.png")
        hardware2_button = Utl.createButton(
            "&Hardware 2.0", partial(self.set_fileType, "HARDWARE2"))

        layout_main = QtWidgets.QVBoxLayout()
        layout_filetype = QtWidgets.QHBoxLayout()
        layout_outputCheck_Grid = QtWidgets.QGridLayout()
        layout_filetype.setAlignment(QtCore.Qt.AlignLeft)
        layout_filetype.addWidget(render_filetype_label)
        layout_filetype.addWidget(self.render_filetype)
        layout_filetype_grid = QtWidgets.QGridLayout()
        layout_filetype_grid.addWidget(png08_button, 1, 0)
        layout_filetype_grid.addWidget(png16_button, 1, 1)
        layout_filetype_grid.addWidget(exr16_button, 2, 0)
        layout_filetype_grid.addWidget(exr32_button, 2, 1)
        layout_filetype_grid.addWidget(exrlayered_button, 3, 0)
        layout_filetype_grid.addWidget(hardware2_button, 3, 1)
        layout_main.addLayout(layout_filetype)
        layout_main.addLayout(layout_filetype_grid)
        layout_main.addWidget(spacer)
        layout_main.addLayout(layout_outputCheck_Grid)
        layout_main.setAlignment(QtCore.Qt.AlignTop)
        self.topGroupBox.setLayout(layout_main)

    #--------------------------------------------------------------------------
    # Widget Functions
    #--------------------------------------------------------------------------
    def placeHolder(self, word):
        print("I am holding place")
        print("This is my word: " + word)

    #-------------------------------------------------------------------------------
    # Functions
    #-------------------------------------------------------------------------------
    def get_renderer(self):
        return cmds.getAttr('defaultRenderGlobals.currentRenderer')

    def get_fileType(self):
        fileType = "None"
        if self.get_renderer() == 'arnold':
            imageFormat = cmds.getAttr('defaultArnoldDriver.ai_translator')
            if imageFormat == 'exr':
                exrPrecision = cmds.getAttr(
                    'defaultArnoldDriver.halfPrecision')
                if exrPrecision == 1:
                    fileType = "EXR16"
                else:
                    fileType = "EXR32"
                if cmds.getAttr('defaultArnoldDriver.mergeAOVs') == 1:
                    fileType = "EXRLAYERED"
            if imageFormat == 'png':
                pngFormat = cmds.getAttr('defaultArnoldDriver.pngFormat')
                if pngFormat == 1:
                    fileType = "PNG08"
                else:
                    fileType = "PNG16"
        if self.get_renderer() == 'mayaHardware2':
            fileType = "HARDWARE2"
        return fileType

    def set_fileType(self, filetype):
        self.render_filetype.setText(
            "<font color=yellow size=5> <u> </u> {} </font>".format(filetype))
        setup.setRenderEnvironment(filetype, False)


class Render_Submit_Button(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Render_Submit_Button, self).__init__(parent)
        #--------------------------------------------------------------------------
        # Create Submit Layout Widgets
        #--------------------------------------------------------------------------
        submitRender_button = Utl.createButton("&Submit Render",
                                               self.submitRender,
                                               icon_path + "images.png",
                                               QtCore.QSize(50, 50))
        submitRender_button.setFixedHeight(50)
        #--------------------------------------------------------------------------
        # Set Main layout
        #--------------------------------------------------------------------------
        mainButtonLayout = QtWidgets.QVBoxLayout()
        mainButtonLayout.addWidget(submitRender_button, 1)
        self.setLayout(mainButtonLayout)

    #-------------------------------------------------------------------------------
    # Submit Render
    #-------------------------------------------------------------------------------
    def submitRender(self):
        ################## Run sanity checks #######################
        filetype = tools.getFileType()
        if tools.checkForIssues() == False:
            # set up the dialog
            userResponse = cmds.confirmDialog(
                title='Render',
                message='Do you want to render a new version?',
                button=['Yes', 'No', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
            print(userResponse)
            Utl.createDirs(userResponse, filetype)


class Utl(object):
    def __init__(self, parent=None):
        super(Utl, self).__init__(parent)

    #--------------------------------------------------------------------------
    # Creating GUI Functions
    #--------------------------------------------------------------------------

    @staticmethod
    def createButton(text,
                     command,
                     icon="",
                     iconSize=QtCore.QSize(24, 24),
                     isCheckable=False):
        button = QtWidgets.QPushButton(text)
        if icon:
            button.setIcon(QtGui.QIcon(icon))
            button.setIconSize(iconSize)
        if isCheckable:
            button.setCheckable()
        button.clicked.connect(command)
        return button

    @staticmethod
    def createDirs(userResponse, filetype):
        if userResponse == 'Yes':
            print("Render Type: " + filetype)
            setup.setRenderEnvironment(filetype, True)
            setup.setBaseRenderDir()
            sceneFileFull = setup.saveRenderReadyVersion()
            render.launchDeadline(sceneFileFull)

        if userResponse == 'No':
            print("No: Not running render setup")
            print(
                "##################################################################################################################################################"
            )
            print(
                "##################################################################################################################################################"
            )
            print("\n")

            sceneFileFull = cmds.file(q=True, sceneName=True)
            render.launchDeadline(sceneFileFull)

        else:
            pass


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


def runUI():
    print("Hi")
    #if __name__ == "__main__":
    print("Trying to run UI")
    # Development workaround for PySide winEvent error (in Maya 2014)
    # Make sure the UI is deleted before recreating
    try:
        ui.close()
    except:
        pass

    # Create minimal UI object
    ui = RenderTool_UI()
    #ui.resize(300, 300)

    # Delete the UI if errors occur to avoid causing winEvent
    # and event errors (in Maya 2014)
    try:
        print("......................................................")
        ui.create()
        ui.show()
        ui.activateWindow()
        ui.raise_()

    except:
        ui.deleteLater()
