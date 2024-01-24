#!/usr/bin/env python

# Standard library imports
import os
import sys
import traceback

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
import mayaOBJExport

# cmds.loadPlugin("VISMO_MDDtoDeadline_v001", quiet=1) # Load all plugins you might need

try:    
    if cmds.pluginInfo("mayaMDDtoDeadline",q=1,loaded=1) == False:
        cmds.loadPlugin("mayaMDDtoDeadline",quiet=1)
        
    if cmds.pluginInfo("mayaMddWriter",q=1,loaded=1) == False:
        cmds.loadPlugin("mayaMddWriter",quiet=1)
        
    if cmds.pluginInfo("MDDExporter.mll",q=1,loaded=1) == False:
        cmds.loadPlugin("MDDExporter.mll",quiet=1)
    print "Plugins loaded"
except:
    print "Plugins not loaded"

print "----------------------------------------------------------------"
print "--------   Running VISMO_MDD_Tool v003 Maya2018     ------------"
print "----------------------------------------------------------------"

def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')

class VISMO_MDD_UI(QtWidgets.QDialog):    
#------------------------#
# PySide UI              #
#------------------------# 
    def __init__(self, parent=_maya_main_window()):
        super(VISMO_MDD_UI, self).__init__(parent)

        self.deadline = False
        self.prefix = 'MDD_'
        self.suffix = ''
        self.startFrame  = cmds.playbackOptions(q=1, minTime=1 )
        self.endFrame = cmds.playbackOptions(q=1, maxTime=1 )
        self.fps = 24
        self.existing_MDD_Sets = cmds.listSets(allSets=1)
        
        
    def create(self):
        self.setWindowTitle("VISMO MDD Export Tool Maya2018")
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.create_controls()
        self.create_layout()
        self.create_connections()
        
    def create_controls(self):
        '''
        Create the widgets for the dialog
        '''             
    ## Make layout items 
        QtWidgets.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        self.frame_range_title = QtWidgets.QLabel('Frame Range')
        self.frame_start_edit = QtWidgets.QLineEdit(str(int(self.startFrame)))
        self.frame_start_edit.setFixedWidth(50)
        self.frame_end_edit = QtWidgets.QLineEdit(str(int(self.endFrame)))
        self.frame_end_edit.setFixedWidth(50)
        #
        self.frame_rate_title = QtWidgets.QLabel('Frame Rate')
        self.fps = self.getMayaFrameRate()
        self.frame_rate_edit = QtWidgets.QLineEdit(str(int(self.fps)))
        self.frame_rate_edit.setFixedWidth(50)
        self.frame_fpsLabel_title = QtWidgets.QLabel('fps')  
        #
        self.mdd_suffix_title = QtWidgets.QLabel('MDD Suffix: ')
        self.mdd_suffix = QtWidgets.QLineEdit("")
        self.mdd_suffix.setText(self.getshotName())
        suffix = self.mdd_suffix.text()
        if suffix == "":
            self.suffix = ""
        else:
            self.suffix = "_" + self.mdd_suffix.text()
        self.mdd_suffix.setFixedWidth(150)
        mdd_suffix_tooltip = ("This is used to put custom text between the mesh name and the version number.\n"
                              "i.e. MeshName_Suffix_Version.mdd")
        self.mdd_suffix.setToolTip(mdd_suffix_tooltip)
        #
        self.obj_export = QtWidgets.QCheckBox("Overwrite full OBJ")
        self.obj_export.setChecked(True)
        obj_export_Tooltip = ("By default this tool overwrites the entire OBJ file.\n"
                              "To only write header data uncheck this box")
        self.obj_export.setToolTip(obj_export_Tooltip)
        #
        self.mdd_scene_version = QtWidgets.QCheckBox("Sync MDD version to Scene version")
        self.mdd_scene_version.setChecked(True)
        mdd_scene_version_Tooltip = ("By default the MDD file will be given the same version of your scene file.\n"
                                     "If your scene has no version, you will be unable to launch the export.\n"
                                     "If there is an existing MDD version, a _rev directory will be made and the old file moved there.\n"
                                     "If unchecked, the tool will automatically version up your MDDs based on the last version in you directory path.")
        self.mdd_scene_version.setToolTip(mdd_scene_version_Tooltip)
        #
        self.versionUp_scene_button = QtWidgets.QPushButton("Version Up Scene")
        #
        self.file_path_Title = QtWidgets.QLabel('Export Path: ')        
        self.file_path_Edit = QtWidgets.QLineEdit(self.getCurrentPath())
        self.file_path_Edit.setFixedWidth(400)
        self.file_open_Button = QtWidgets.QPushButton("Set Path")
        self.file_open_Button.setFixedWidth(100)   
        file_open_Tooltip = ("This path is set by default to find the project's cache directory.\n"
                             "You can manually set a different path.")
        self.file_open_Button.setToolTip(file_open_Tooltip)
        
        #
        self.red_html = "<font color=red size=5> <u> </u> {} </font>".format("v001")
        
        self.maya_mesh_add_Button = QtWidgets.QPushButton("Add Mesh")
        self.maya_mesh_add_Button.setFixedWidth(100)
        self.maya_mesh_add_Button.setFixedHeight(30)
        #
        self.maya_mesh_remove_Button = QtWidgets.QPushButton("Remove Mesh")
        self.maya_mesh_remove_Button.setFixedWidth(100)
        self.maya_mesh_remove_Button.setFixedHeight(30)
        #
        self.maya_set_add_Button = QtWidgets.QPushButton("Add MDD Set")
        self.maya_set_add_Button.setFixedWidth(100)
        self.maya_set_add_Button.setFixedHeight(30)
        #
        self.maya_mesh_clear_Button = QtWidgets.QPushButton("Clear All")
        self.maya_mesh_clear_Button.setFixedWidth(100)
        self.maya_mesh_clear_Button.setFixedHeight(30)
        #
        self.maya_mesh_list_title = QtWidgets.QLabel('Selection Sets')
        self.maya_mesh_list = QtWidgets.QListWidget()
        self.maya_mesh_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        # self.maya_mesh_list.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.maya_mesh_list.setFrameStyle(QtWidgets.QFrame.Box |QtWidgets.QFrame.Plain)
        self.maya_mesh_list.setLineWidth(1)
        
        #
        self.export_button = QtWidgets.QPushButton()
        self.export_button.setFixedHeight(50)
        self.export_button.setStyleSheet("background-color: #9dc38a")
        self.export_button.setText("Export (Local)")
        self.export_button.setStyleSheet("font-size: 14pt")
        #
        self.deadline_button = QtWidgets.QPushButton()
        self.deadline_button.setFixedHeight(50)
        self.deadline_button.setStyleSheet("background-color: #9dc38a")
        self.deadline_button.setText("Export (Deadline)")
        self.deadline_button.setStyleSheet("font-size: 14pt")        
        #
        self.text_log_box = QtWidgets.QTextEdit()
        #
        self.log_box_clear_Button = QtWidgets.QPushButton("Clear Log")
        self.log_box_clear_Button.setFixedHeight(15)
        
        
    def create_layout(self):
        '''
        Create the layouts and add widgets
        '''   
    # Make layouts
        layout_main = QtWidgets.QVBoxLayout()
        layout_frameRange = QtWidgets.QHBoxLayout()
        layout_frameRate = QtWidgets.QHBoxLayout()
        layout_frameInfo = QtWidgets.QVBoxLayout()
        layout_mdd_suffix = QtWidgets.QHBoxLayout()
        layout_OBJ_Export = QtWidgets.QVBoxLayout()
        layout_filePath = QtWidgets.QHBoxLayout()
        layout_mdd_version = QtWidgets.QHBoxLayout()
        layout_filePath_mddName = QtWidgets.QVBoxLayout()
        layout_object_buttons = QtWidgets.QHBoxLayout()
        layout_objects = QtWidgets.QVBoxLayout()
        layout_export_buttons = QtWidgets.QHBoxLayout()
        layout_export = QtWidgets.QVBoxLayout()
        
    # Make Frames
        frame_main = QtWidgets.QFrame()
        frame_frameRange = QtWidgets.QFrame()
        frame_OBJ = QtWidgets.QFrame()
        frame_filePath = QtWidgets.QFrame()
        frame_objectList = QtWidgets.QFrame()
        frame_export = QtWidgets.QFrame()
        
        
    # Set options for Frames
        frame_frameRange.setMinimumWidth(300)
        frame_frameRange.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_OBJ.setMinimumWidth(300)
        frame_OBJ.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_filePath.setMinimumWidth(300)
        frame_filePath.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame_objectList.setMinimumWidth(600)
        frame_objectList.setFrameShape(QtWidgets.QFrame.StyledPanel)        
        frame_export.setMinimumWidth(600)
        frame_export.setFrameShape(QtWidgets.QFrame.StyledPanel)
        
    # Add Widgets
        layout_frameRange.addWidget(self.frame_range_title,0, QtCore.Qt.AlignLeft)
        layout_frameRange.addWidget(self.frame_start_edit, 0, QtCore.Qt.AlignLeft)
        layout_frameRange.addWidget(self.frame_end_edit, 1, QtCore.Qt.AlignLeft)
        #
        layout_frameRate.addWidget(self.frame_rate_title, 0, QtCore.Qt.AlignLeft)
        layout_frameRate.addWidget(self.frame_rate_edit, 0, QtCore.Qt.AlignLeft)
        layout_frameRate.addWidget(self.frame_fpsLabel_title, 1, QtCore.Qt.AlignLeft)
        
        ######################
        layout_mdd_suffix.addWidget(self.mdd_suffix_title, 0, QtCore.Qt.AlignLeft)
        layout_mdd_suffix.addWidget(self.mdd_suffix, 1, QtCore.Qt.AlignLeft)
        
        # layout_OBJ_Export.addLayout(layout_mdd_suffix)
        layout_OBJ_Export.addWidget(self.obj_export)
        # layout_OBJ_Export.addWidget(self.mdd_scene_version)
        #########################
        
        layout_OBJ_Export.addWidget(self.versionUp_scene_button)
        #
        layout_frameInfo.addLayout(layout_frameRange)
        layout_frameInfo.addLayout(layout_frameRate)
        #
        layout_filePath.addWidget(self.file_path_Title)    
        layout_filePath.addWidget(self.file_path_Edit)    
        layout_filePath.addWidget(self.file_open_Button) 
        layout_filePath.setAlignment(QtCore.Qt.AlignCenter)   
        #
        layout_filePath_mddName.addLayout(layout_filePath)
        layout_filePath_mddName.addLayout(layout_mdd_version)
        #
        layout_object_buttons.addWidget(self.maya_mesh_add_Button, 0)
        layout_object_buttons.addWidget(self.maya_mesh_remove_Button, 0)
        layout_object_buttons.addWidget(self.maya_set_add_Button, 0)
        layout_object_buttons.addWidget(self.maya_mesh_clear_Button, 0)
        layout_object_buttons.setAlignment(QtCore.Qt.AlignCenter)
        #
        layout_objects.addLayout(layout_object_buttons)
        layout_objects.addWidget(self.maya_mesh_list)
        #
        layout_export_buttons.addWidget(self.export_button)
        layout_export_buttons.addWidget(self.deadline_button)
        #
        layout_export.addLayout(layout_export_buttons)
        layout_export.addWidget(self.text_log_box)
        layout_export.addWidget(self.log_box_clear_Button)
        
    # Create a QSplitter widget and add the left and right frames into it
        
        splitter1 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter1.addWidget(frame_frameRange)
    # Set the QSplitter to not bein collapsable
        splitter1.setCollapsible(0,False)
        splitter1.setCollapsible(1,False)
        #
        splitter_frameInfo = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter_frameInfo.addWidget(splitter1)
        splitter_frameInfo.addWidget(frame_OBJ)
        splitter_frameInfo.setCollapsible(0,False)
        splitter_frameInfo.setCollapsible(1,False)
        #
        splitter2 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter_frameInfo)        
        splitter2.addWidget(frame_filePath)
        splitter2.addWidget(frame_objectList)
        splitter2.setCollapsible(0,False)
        splitter2.setCollapsible(1,False)
        #
        splitter3 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter3.addWidget(splitter2)
        splitter3.addWidget(frame_export)
        splitter3.setCollapsible(0,False)
        splitter3.setCollapsible(1,False)
    #Add the splitter to the mainLayout
        layout_main.addWidget(splitter3)
        
    #Set the layout for the frames
        frame_main.setLayout(layout_main)
        frame_frameRange.setLayout(layout_frameInfo)
        frame_OBJ.setLayout(layout_OBJ_Export)
        frame_filePath.setLayout(layout_filePath_mddName)
        frame_objectList.setLayout(layout_objects)
        frame_export.setLayout(layout_export)
        
        self.setLayout(layout_main)
        
    def create_connections(self):
        '''
        Create the signal/slot connections
        '''
        self.versionUp_scene_button.clicked.connect(self.versionUp_scene_pressed)
        self.file_open_Button.clicked.connect(self.openFile_button_pressed)
        self.maya_mesh_add_Button.clicked.connect(self.maya_mesh_add_pressed)
        self.maya_mesh_remove_Button.clicked.connect(self.item_remove_pressed)
        self.maya_set_add_Button.clicked.connect(self.add_MDD_set_pressed) #####
        self.maya_mesh_clear_Button.clicked.connect(self.maya_items_clear_pressed)
        self.export_button.clicked.connect(self.export_button_pressed)
        self.deadline_button.clicked.connect(self.deadline_button_pressed)
        self.log_box_clear_Button.clicked.connect(self.logBox_clear_button_pressed)
             
        
    #--------------------------------------------------------------------------
    # SLOTS
    #--------------------------------------------------------------------------
    def versionUp_scene_pressed(self):
        sceneName = cmds.file(q=True, sceneName=True).split('/')[-1]
        scenePath = cmds.file(q=True, sceneName=True).split('/')[:-1]
        scenePath = "/".join(scenePath)
        version = ""
        sceneName = sceneName.split('_')
        for n,i in enumerate(sceneName):
            i = i.split('.')[0]
            if "v0" in i.lower():
                versionNumber = i[1:]
                newVersionNum = int(versionNumber) + 1
                newVersionNum = '%03d' % newVersionNum
                version = "v" + str(newVersionNum)
                sceneName[n] = version                
        sceneName = "_".join(sceneName)
        newScene = scenePath + "/" + sceneName  
        cmds.file(rename=newScene)
        cmds.file( save=True, type='mayaAscii' )
        
    def openFile_button_pressed(self):
        print ("Button Pressed.....setting file path")        
        scenePath = self.getCurrentPath()        
        filePath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder', self.file_path_Edit.text())        
        self.file_path_Edit.setText(filePath)
        self.text_log_box.append("Setting output path to......") 
        self.text_log_box.append("\n-------------------------------------------\n")
        self.text_log_box.append(filePath)
        
    def maya_mesh_add_pressed(self):
        print ("Button Pressed.....Adding mesh")
        selection = self.get_Selected_Meshes()
        for sel in selection:
            isInList = self.checkList(sel)
            if isInList:
                self.text_log_box.append(sel + " is already in export list")
            else:
                self.maya_mesh_list.addItem(sel)
                self.text_log_box.append("Adding maya mesh........" + sel)
        self.text_log_box.append("\n-------------------------------------------\n")
            
    def add_MDD_set_pressed(self):
        setName, ok = QtWidgets.QInputDialog.getText(self, 'Make Selection Set', 'Enter new Set name:', QtWidgets.QLineEdit.Normal, 'New Set')    
        if ok:
            setName = str(setName) + "_SET"
            self.maya_mesh_list.addItem(setName)        
            self.create_MayaSet(setName) 
            self.text_log_box.append("Adding maya selection set........" + setName)  

    def item_remove_pressed(self):
        setItems = self.maya_mesh_list.selectedItems()        
        for i in setItems:
            self.maya_mesh_list.takeItem(self.maya_mesh_list.row(i))
            self.text_log_box.append("Removing maya mesh........" + i.text())
            self.text_log_box.append("\n-------------------------------------------\n")
        
    def maya_items_clear_pressed(self):
        print ("Button Pressed.....Clearing all selection sets")          
        self.maya_mesh_list.clear()   
        self.text_log_box.append("Clearing all export items")  
        self.text_log_box.append("\n-------------------------------------------\n")
        
    def export_button_pressed(self):
        print ("Button Pressed.....Exporting MDDs")
        self.text_log_box.append("Starting MDD exports.......") 
        self.text_log_box.append("\n-------------------------------------------\n")
        self.deadline = False
        # self.launchExportCheck()
        self.launchExport()
        
    def deadline_button_pressed(self):
        print ("Button Pressed....Deadline export button pressed")
        self.text_log_box.append("Starting MDD exports.......") 
        self.text_log_box.append("\n-------------------------------------------\n")
        self.deadline = True
        # self.launchExportCheck()
        self.launchExport()
        
    def logBox_clear_button_pressed(self):
        print ("Button Pressed.....Clearing log box")
        self.text_log_box.clear()        
   
    def checkList(self, mesh):
        items = []
        isInList = False
        for index in xrange(self.maya_mesh_list.count()):
            if mesh == self.maya_mesh_list.item(index).text():
                isInList = True
                
        return isInList
           
#------------------------#
# OS Tools               #
#------------------------#  
    def getOBJFiles(self):
        currentDir = QtCore.QDir(self.file_path_Edit.text())
        fileName = "*"
        files = currentDir.entryList([fileName], QtCore.QDir.Files | QtCore.QDir.NoSymLinks)
        mdd_files = []
        obj_files = []
        
        for f in files:
            if ".obj" in f:
                obj_files.append(f)
                
        return obj_files
        
        
#------------------------#
# Maya Tools             #
#------------------------#  
    def create_MayaSet(self, setName):
        objs = self.get_Selected_Meshes()
        cmds.sets(objs, n=setName)
        
    def delete_MayaSet(self, items):
        names = []
        msg = ""
        for i in items:
            if type(i) == 'PySide2.QtWidgets.QListWidgetItem':
                cmds.delete(i.text())
                names.append(i.text())
            else:
                cmds.delete(i)
                names.append(i)
                
        msg = 'Deleting sets: ' + ' '.join([f+',' for f in names])
        return msg
        
    def get_Selected_Meshes(self):
        sel =  cmds.ls(sl=1, objectsOnly=1)
        return sel   
        
    def getCurrentPath(self):
        sceneFile = cmds.file(query=True, sn=True)
        try:
            pathInfo = sceneFile.split("/")
            index = pathInfo.index("Animation") + 1
            pathInfo = pathInfo[:index]
            # pathInfo = pathInfo[:5]
            shot = sceneFile.split("/")[-2]
            newpath = ""
            for i in pathInfo:
                newpath = newpath + i + "/"            
            mddPath = newpath + "cache/MDD/" + shot   
            if os.path.exists(mddPath) == False:
                os.makedirs(mddPath)
            return mddPath
        except:
            cmds.confirmDialog(title='Error', 
                   message='Scene path error.  \nPlease save your scene under an Animation directory', 
                   ma="center") 
            sys.exit() 
        
    def getMayaFrameRate(self):
        frameRate = float(24)
        currentFps = cmds.currentUnit( query=True, time=True )
        if currentFps == 'film':
            frameRate =float(24)
        if currentFps == 'pal':
            frameRate =float(25)        
        if currentFps == 'show':
            frameRate =float(48)        
        if currentFps == 'palf':
            frameRate =float(50)
        if currentFps == 'ntscf':
            frameRate =float(60)        
        if currentFps == 'game':
            frameRate =float(15)    
        return frameRate
        
    def get_exportList(self):
        items = []            
        for index in xrange(self.maya_mesh_list.count()):
            name = self.maya_mesh_list.item(index)
            items.append(name.text())  
        return items
        
    def get_MDD_Path(self):
        scenePath = cmds.file( q=True, l=True )[0]
        
    def getshotName(self):
        shotName = ""
        sceneFile = cmds.file(query=True, sn=True)
        if sceneFile:
            sceneName = sceneFile.split('/')[-1]
            try:
                shotName = sceneName.split('_')[0] + "_" + sceneName.split('_')[1]
            except:
                shotName = sceneName.split('.')[0]
        return shotName
        
    def stripObjName(self, objectName):
        newName = objectName.split(':')
        return newName[0]
        
    def get_scene_name(self):
        return cmds.file(q=True, sceneName=True).split('/')[-1]
    
#------------------------#
# RUN MDD EXPORT         #
#------------------------#
    def launchExport(self, *args):        
        objExportCheck = self.obj_export.isChecked()
        startFrame = self.frame_start_edit.text()
        endFrame = self.frame_end_edit.text()
        frameRate = self.frame_rate_edit.text()
        exportPath =  self.file_path_Edit.text()
        if os.path.exists(exportPath ):
            exportList = self.get_exportList()
            if exportList:    
                setList = []
                meshList = []
                for item in exportList:
                    if "_SET" in item:                    
                        setList.append(str(item))
                    else:
                        meshList.append(str(item))   
                cmds.select( clear=True )
                ## Export MDD files
                for item in exportList:  
                    print ("The MDD is....." + item)
                    cmds.select(item, ne=True, add=True)
                    self.text_log_box.append("Exporting MDD for: " + item)
                cmds.select( clear=True )                
                #===============================================
                # Calling Command plugin
                #===============================================            
                meshListString = ",".join(meshList)
                setListString = ",".join(setList)
                print "meshListString: ", meshListString
                print "setListString: ", setListString
                sceneversion = self.mdd_scene_version.isChecked()                
                # Send export to Deadline or run locally
                if self.deadline == True:
                    print self.deadline
                    print "TO DEADLINE"
                    print "cmds.deadlinelaunch(ep=" + exportPath + ", fs=" + startFrame + ", fe=" + endFrame + ", ml=" + meshListString + ", sl=" + setListString + ", oe=" + str(objExportCheck) + ")"
                    cmds.deadlinelaunch(ep=exportPath, fs=startFrame, fe=endFrame, ml=meshListString, sl=setListString, oe=objExportCheck)
                else:
                    print "TO LOCAL"
                    mayaOBJExport.MayaOBJExport(exportPath, meshListString, setListString, objExportCheck)
                    cmds.MDDExport(ep=exportPath, ml=meshListString, sl=setListString)
                    # cmds.mddWriter(ep=exportPath, fs=startFrame, fe=endFrame, ml=meshListString, sl=setListString, oe=objExportCheck)
                    
                
                #####################################################################
                
                self.text_log_box.append("\n-------------------------------------------\n")
                self.text_log_box.append("\n-------------------------------------------\n")
                self.text_log_box.append("Export files to........" + exportPath)
            else:
                self.text_log_box.append("!!!----Nothing to export----!!!")
                self.text_log_box.append("\n-------------------------------------------\n")
        else:
            self.text_log_box.append("!!!----File path: " + exportPath + " does not exist----!!!")
            self.text_log_box.append("\n-------------------------------------------\n")

########################

def runUI():
    #if __name__ == "__main__":
    print "Trying to run UI"
    # Development workaround for PySide winEvent error (in Maya 2014)
    # Make sure the UI is deleted before recreating
    try:
        ui.close()
    except:
        pass      

    # Create minimal UI object
    ui = VISMO_MDD_UI()
   
    # Delete the UI if errors occur to avoid causing winEvent
    # and event errors (in Maya 2014)
    try:
        print "......................................................"
        ui.create()
        ui.show()
        ui.activateWindow()
        ui.raise_()
       
    except:
        ui.deleteLater()