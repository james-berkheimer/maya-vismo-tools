#!/usr/bin/env python

# Standard library imports
import sys
import os
import argparse

# Third party imports
import maya.utils as utils
import maya.cmds as cmds
import maya.standalone

# Initialize Maya Command Python
maya.standalone.initialize("Python")

# Load MDD plugin
try:    
    if cmds.pluginInfo("mayaMddWriter",q=1,loaded=1) == False:
        cmds.loadPlugin("mayaMddWriter", quiet=1)
    print "Plugins loaded"
except:
    print "Plugins not loaded"
    
print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++"
print "++++++++   Running MDD Export Commandline ++++++++++"
print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"

#===============================================
# Usage
#===============================================
# mayapy.exe "O:\Assets\Animation_Share\Maya\VISMO_DEV\scripts\VISMO_CmdPlugin_Test_v002.py" -v 2

def main():
        
    mayaScene = ''
    exportPath = ''
    startFrame = ''
    endFrame = ''
    meshListString = ''
    setListString = ''
    objExport = "True" 
    
    # Establish parser
    parser = argparse.ArgumentParser(description='Runs the MDD exporter in Maya standalone')
    
    # Add arguments
    parser.add_argument('--mayaScene', '-ms', action='store', dest='mayaScene', help='This is the Maya scene.' )
    parser.add_argument('--exportPath', '-ep', action='store', dest='exportPath',help='This is the MDD export path.' )
    parser.add_argument('--startFrame', '-fs', action='store', dest='startFrame',help='This is the Start frame.' )
    parser.add_argument('--endFrame', '-fe', action='store', dest='endFrame',help='This is the End frame.' )
    parser.add_argument('--meshListString', '-ml', action='store', dest='meshListString',help='This is the mesh list.' )
    parser.add_argument('--setListString', '-sl', action='store', dest='setListString',help='This is the set list.' )
    parser.add_argument('--objExport', '-oe', action='store', dest='objExport',help='Export new OBJ.' )
    
    # Grab the arguments
    args = parser.parse_args()
    if args.mayaScene:
        mayaScene = args.mayaScene
    if args.exportPath:
        exportPath = args.exportPath
    if args.startFrame:
        startFrame = args.startFrame
    if args.endFrame:
        endFrame = args.endFrame
    if args.meshListString:
        meshListString = args.meshListString
    if args.setListString:
        setListString = args.setListString
    if args.objExport:
        objExport = args.objExport  
    
    # Run functionality
    print "TESTING"
    print mayaScene
    print exportPath
    print startFrame
    print endFrame
    print meshListString
    print setListString
    print objExport
    
    print "ep=" + exportPath + ", " + "fs=" + startFrame + ", " + "fe=" + endFrame + ", " + "ml=" + meshListString + ", " + "sl=" + setListString + ", " + "oe=" + str(objExport)
    
    cmds.file(mayaScene, o=1, f=1)
    # cmds.mddWriter(ep=exportPath, fs=startFrame, fe=endFrame, ml=meshListString, sl=setListString, oe=objExport)
    mayaOBJExport.MayaOBJExport(exportPath, meshListString, setListString, objExportCheck)
    cmds.MDDExport(ep=exportPath, ml=meshListString, sl=setListString)

    print "File Complete"
    maya.standalone.uninitialize()
    os._exit(0)

if __name__ == "__main__":
   main()