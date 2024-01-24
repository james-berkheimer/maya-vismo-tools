#!/usr/bin/env python

# Standard library imports
import os
import glob

# Third party imports
import maya.cmds as cmds

try:    
    if cmds.pluginInfo("objExport.mll",q=1,loaded=1) == False:
        cmds.loadPlugin("objExport.mll",quiet=1)
    print "Plugins loaded"
except:
    print "Plugins not loaded"

class MayaOBJExport():
    def __init__(self, exportPath, meshListString, setListString, objExportCheck):
        print "\n"
        print "------------------------------------------------"
        print "----------------- Begin Export -----------------"
        print "------------------------------------------------"
        print "\n"
        self.objExportCheck = objExportCheck
        meshList = meshListString.split(",")
        setList = setListString.split(",")
        exportList = meshList + setList
            
        #first frame
        cmds.currentTime(1, edit=True)        
        for item in exportList:
            if item:
                meshName = item.replace(":","-")
                meshName = meshName.replace("|","-")
                fileName = self.mddVersionUp(meshName, exportPath)
                fullPath = exportPath + "\\" + fileName
                try:                
                    self.export(item, meshName, exportPath, fullPath, self.objExportCheck)
                except IOError:
                    print ('Error open file ' + fullPath)
    
    def mddVersionUp(self, meshName, exportPath):
        os.chdir(exportPath)
        mddfiles = glob.glob("*.mdd")
        mddfilesFiltered = [k for k in mddfiles if meshName in k]
        if len(mddfilesFiltered) != 0:
            latestFile = sorted(mddfilesFiltered)[-1]
            latestVersionNum = latestFile.split('_')[-1].split('.')[0][1:]
            newVersionNum = str(int(latestVersionNum) + 1)
            padding = ''
            if len(newVersionNum) == 1:
                padding = '00'
            if len(newVersionNum) == 2:
                padding = '0'
            return meshName + '_v' + padding + newVersionNum + '.mdd'
        else:
            return meshName + '_v001.mdd'
   
    def export(self, item, meshName, exportPath, mddPath, objExportCheck):
        print "In objExport"
        print "item:", item
        print "meshName:", meshName
        print "exportPath:", exportPath
        print "mddPath:", mddPath
        print 'objExportCheck', objExportCheck
        print 'objExportCheck type', type(objExportCheck)
        objPath = exportPath + "/" + meshName + '.obj'
        print "objPath: " + objPath
        sceneName = cmds.file(q=True, sceneName=True)
        self.writeMetaDataFile(exportPath, meshName, mddPath)
        if objExportCheck == True:
            cmds.select(item, add=True)
            optionsString = "groups=1;ptgroups=1;materials=0;smoothing=1;normals=1;"
            print ("Let's create the OBJ File name......." + objPath)
            cmds.file(objPath,typ="OBJexport",op=optionsString,pr=1,es=1,force=1)
            cmds.select( clear=True )
        # clean mtl files
        print ("-------------", "Cleaning up mtl files.")
        os.chdir(exportPath)
        if glob.glob("*.mtl"):
            for file in glob.glob("*.mtl"):
                print ("++++++++++++++", file)
                os.remove(exportPath + "\\" + file)
        
    def writeMetaDataFile(self, exportPath, meshName, mddPath):
        sceneName = cmds.file(q=True, sceneName=True)
        metaDataPath = exportPath + "\\" + meshName + ".vismo"
        # Open file for writing
        mddFile = open(metaDataPath, 'w')
        mddFile.write("SCENE: " + sceneName +"\r\n")
        mddFile.write("\r\n")
        mddFile.write("SCALE: " + self.getSceneScale() +"\r\n")
        mddFile.write("\r\n")
        mddFile.write("MDD: " + mddPath +"\r\n")
        mddFile.close()
                
    def getSceneScale(self):        
        scale = cmds.currentUnit( query=True, linear=True )
        if scale == 'mm':
            return "millimeters"
        if scale == 'cm':
            return "centimeters"
        if scale == 'm':
            return "meters"
        if scale == 'km':
            return "kilometers"
        if scale == 'in':
            return "inches"
        if scale == 'ft':
            return "feet"
        if scale == 'yd':
            return "tards"
        if scale == 'ni':
            return "miles"