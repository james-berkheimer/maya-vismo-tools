#!/usr/bin/env python

##--------------------------------------##
#                                        # 
##--------------------------------------##

# Standard library imports
import os.path
import os, shutil, glob
import time
import re
import sys, string
import subprocess

# Third party imports
import maya.cmds as cmds

# Local application imports
import vismo.tools as tools

print("In Dev setup.py")

####################################################################################################
# Sets
#####################################################################################################    

def setRenderEnvironment(filetype="EXR16", versionUp=False):     
    print("_____________________ In Dev setArnoldEnvironment _____________________")        
    # Need to establish Maya render environment setup        
    ## Set the images path:
    renderFileName = tools.getRenderFileName(versionUp)
    renderDir = tools.getRenderOutputDir(versionUp)
    cmds.workspace(fr=["images", renderDir])
    cmds.workspace(saveWorkspace=True)
    
    ## Set the File Name Prefix:
    if filetype != "EXRLAYERED":
        prefix = "<RenderLayer>/<RenderPass>/" + renderFileName[:-3] + "_<RenderLayer>_<RenderPass>"
    else:
        prefix = "<RenderLayer>/" + renderFileName[:-3] + "_<RenderLayer>"
    
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", prefix, type='string')
    
    if filetype == "PNG08":
        cmds.setAttr( 'defaultArnoldDriver.ai_translator', 'png', type='string' )
        cmds.setAttr( 'defaultArnoldDriver.pngFormat', 0 )
    if filetype == "PNG16":
        cmds.setAttr( 'defaultArnoldDriver.ai_translator', 'png', type='string' )
        cmds.setAttr( 'defaultArnoldDriver.pngFormat', 1 )
    if filetype == "EXR16":
        cmds.setAttr( 'defaultArnoldDriver.ai_translator', 'exr', type='string' )
        cmds.setAttr( 'defaultArnoldDriver.halfPrecision', 1 )
    if filetype == "EXR32":
        cmds.setAttr( 'defaultArnoldDriver.ai_translator', 'exr', type='string' )
        cmds.setAttr( 'defaultArnoldDriver.halfPrecision', 0 )
    if filetype == "EXRLAYERED":
        cmds.setAttr( 'defaultArnoldDriver.ai_translator', 'exr', type='string' )
        cmds.setAttr( 'defaultArnoldDriver.halfPrecision', 1 )
        cmds.setAttr( 'defaultArnoldDriver.mergeAOVs', 1 )
    if filetype == "HARDWARE2":
        cmds.setAttr( 'defaultRenderGlobals.imageFormat', 40)
        cmds.setAttr( 'defaultRenderGlobals.exrPixelType', 1)
    
    
    ## Set the frame extention format
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    cmds.setAttr("defaultRenderGlobals.animation", 1)
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
    cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
    cmds.setAttr("defaultRenderGlobals.periodInExt", 2)      
        
    ## Possibly set the names of the AOV's        
        
    print("_____________________ Leaving setArnoldEnvironment _____________________")
    
def setPRManEnvironment(versionUp=False):        
    print("_____________________ In setPRManEnvironment _____________________")        
    # Need to establish Maya render environment setup        
    ## Set the images path:
    renderFileName = tools.getRenderFileName(versionUp)
    renderDir = tools.getRenderOutputDir(versionUp)
    
    ## Set the File Name Prefix:
    prefix = "<RenderLayer>/<RenderPass>/" + renderFileName[:-3] + "_<RenderLayer>_<RenderPass>"
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", prefix, type='string')
    
    ## Set the frame extention format
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    cmds.setAttr("defaultRenderGlobals.animation", 1)
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
    cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
    cmds.setAttr("defaultRenderGlobals.periodInExt", 2)
    ## Possibly set the names of the AOV's                
    print("_____________________ Leaving setPRManEnvironment _____________________")


def saveRenderReadyVersion(versionUp = True):        
    print("_____________________ In saveRenderReadyVersion _____________________")
    directory = tools.getDirectory()
    if versionUp == False:
        renderFileName = tools.getRenderFileName(False)
    else:
        renderFileName = tools.getRenderFileName()
    fileExtension = ".mb"
    # fileExtension = tools.getSceneFileExtention()
    renderReady = renderFileName + fileExtension
    saveFile = directory + "/" + renderReady
            
    print("Saving Render Ready file: " + renderReady)
    # Need Maya save code here
    cmds.file( rename=saveFile )
    cmds.file( save=True, type='mayaBinary' )
    cmds.confirmDialog(message='Render Ready Version Saved')
    return saveFile
    print("_____________________ Leaving saveRenderReadyVersion _____________________")
    
def dirMaker(par, num):
    test = par
    dirCheck = os.path.exists(test) 
    print("Dir Check %s" % (num))
    print(dirCheck)
    if not dirCheck:
        print("Creating: " + test)            
        os.makedirs(test)
   
def setBaseRenderDir(versionUp = True):        
    #---------------------------------------------------------------------------------------------
    # This sets the base render directory.  Another method will set each Render Output Directory.
    #---------------------------------------------------------------------------------------------        
    print("_____________________ In setBaseRenderDir _____________________")
    if versionUp == False:
        renderDir = tools.getRenderOutputDir(False)
    else:
         renderDir = tools.getRenderOutputDir()
         
    dirList = []
    dirList.append(renderDir)
    par1 = os.path.dirname(renderDir)
    dirList.append(os.path.dirname(par1))
    print("par1 " + par1)
    par2 = os.path.dirname(par1)
    dirList.append(os.path.dirname(par2))
    print("par2 " + par2)
    par3 = os.path.dirname(par2)
    dirList.append(os.path.dirname(par3))
    print("par3 " + par3)
    par4 = os.path.dirname(par3)
    dirList.append(os.path.dirname(par4))
    print("par4 " + par4)
    par5 = os.path.dirname(par4)
    dirList.append(os.path.dirname(par5))
    print("par5 " + par5)
    par6 = os.path.dirname(par5)
    dirList.append(os.path.dirname(par6))
    print("par6 " + par6)
    par7 = os.path.dirname(par6)
    dirList.append(os.path.dirname(par7))
    print("par7 " + par7)
    par8 = os.path.dirname(par7)
    dirList.append(os.path.dirname(par8))
    print("par8 " + par8)
    
    for d in range(len(dirList)):
        dirMaker(dirList[d], d)
    print("_____________________ Leaving setBaseRenderDir _____________________")       

