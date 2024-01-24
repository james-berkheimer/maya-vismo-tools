#!/usr/bin/env python

##--------------------------------------##
#                                        #
##--------------------------------------##

# Standard library imports
from contextlib import contextmanager
import io
import os.path
import os, shutil, glob
import time
import re
import sys, string
import subprocess

# Third party imports
import maya.cmds as cmds


#####################################################################################################
# Gets
#####################################################################################################
def getRenderCameras():
    # Get all cameras first
    cameras = cmds.ls(type=('camera'), l=True)
    # Let's filter all startup / default cameras
    startup_cameras = [
        camera for camera in cameras
        if cmds.camera(cmds.listRelatives(camera, parent=True)[0],
                       startupCamera=True,
                       q=True)
    ]
    # non-default cameras are easy to find now.
    non_startup_cameras = list(set(cameras) - set(startup_cameras))
    # Let's get their respective transform names, just in-case
    non_startup_cameras_transforms = map(
        lambda x: cmds.listRelatives(x, parent=True)[0], non_startup_cameras)
    return non_startup_cameras_transforms


def getRenderableCam():
    cameras = getRenderCameras()
    for cam in cameras:
        if cmds.getAttr(cam + ".renderable"):
            renderableCam = cam
    return renderableCam


def getDirectory():
    print("----------------- In getDirectory --------------------------")
    directory = os.path.dirname(cmds.file(q=True, sn=True))
    print("----------------- Leaving getDirectory --------------------------")
    return directory


def getFileInfo():
    print("----------------- In getFileInfo --------------------------")
    fileName = cmds.file(q=True, sn=True, shn=True)
    fileInfo = fileName.split("_")
    print("----------------- Leaving getFileInfo --------------------------")
    return fileInfo


def getFileName(noExt=1):
    print("----------------- In getFileName -----------------")
    fileName = os.path.basename(cmds.file(q=True, sceneName=True))
    if noExt == 1:
        fileName = fileName[:-4]
    print("----------------- Leaving getFileName -----------------")
    return (fileName)


def getFileType():
    print("----------------- In filetype --------------------------")
    currentImageFormat = cmds.getAttr('defaultArnoldDriver.ai_translator')
    if currentImageFormat == "exr":
        if cmds.getAttr('defaultArnoldDriver.mergeAOVs') == True:
            filetype = "EXRLAYERED"
        else:
            exrPrecision = cmds.getAttr('defaultArnoldDriver.halfPrecision')
            if exrPrecision == 0:
                filetype = "EXR32"
            else:
                filetype = "EXR16"
    if currentImageFormat == "png":
        pngFormat = cmds.getAttr('defaultArnoldDriver.pngFormat')
        if pngFormat == 0:
            filetype = "PNG08"
        else:
            filetype = "PNG16"
    print("----------------- Leaving fileType --------------------------")
    return filetype


def getFrameRange():
    print("----------------- In getFrameRange --------------------------")
    frameRange = str(int(cmds.playbackOptions(q=1, minTime=1))) + "-" + str(
        int(cmds.playbackOptions(q=1, maxTime=1)))
    print("frames: " + frameRange)
    print("----------------- Leaving getFrameRange --------------------------")
    return frameRange


def getFrameSize():
    print("----------------- In getFrameSize --------------------------")
    renderlayers = cmds.ls(type="renderLayer")
    currentLayer = cmds.editRenderLayerGlobals(query=True, crl=True)
    cmds.editRenderLayerGlobals(crl=currentLayer)
    w = cmds.getAttr("defaultResolution.width")
    h = cmds.getAttr("defaultResolution.height")
    frameSize = str(w) + "x" + str(h)
    print("----------------- Leaving getFrameSize --------------------------")
    return frameSize


def getOBJDirectory():
    currentScene = os.path.abspath(cmds.file(q=True, sn=True))
    pathArray = currentScene.split('\\')
    currentScene = '/'.join(pathArray)
    return currentScene.split('Animation')[0] + 'Animation/objects/OBJ'


def getProjectCode():
    print("----------------- In getProjectCode --------------------------")
    fileInfo = getFileInfo()
    show = fileInfo[0]
    print(
        "----------------- Leaving getProjectCode --------------------------")
    return show


def getProjectPhase():
    print("----------------- In getProjectPhase --------------------------")
    path = getDirectory()
    pathInfo = path.split("/")
    for i in pathInfo:
        print("Path Info: " + i)
    tmp = pathInfo[-2]
    phaseInfo = tmp.split("_")
    for j in phaseInfo:
        print("Phase Info: " + j)
    showPhase = phaseInfo[-1]
    print(
        "----------------- Leaving getProjectPhase --------------------------")
    return showPhase

def getRenderer():
    print("----------------- In getRenderer --------------------------")
    return cmds.getAttr("defaultRenderGlobals.currentRenderer")
    print("----------------- Leaving getRenderer --------------------------")

def getRenderFileName(versionUp=True):
    print("----------------- In getRenderFileName --------------------------")
    fileInfo = getFileInfo()
    version = fileInfo[-2]
    versionNumber = version[1:]
    if versionUp == True:
        print("Old Version Number: " + versionNumber)
        versionNumber = int(versionNumber) + 1
        print("New Version Number: " + str(versionNumber))
    print("New version number: " + str(versionNumber))
    print(int(versionNumber))
    version = "%03d" % int(versionNumber)
    version = "v" + str(version)
    print("New version: " + version)
    userInitials = getUserInitials()
    renderReady = fileInfo[0] + "_" + fileInfo[
        1] + "_" + version + "_" + userInitials
    print("Render ready file: " + renderReady)
    print(
        "----------------- Leaving getRenderFileName --------------------------"
    )
    return renderReady


def getRenderLayers():
    print("----------------- In getRenderLayers --------------------------")
    renderLayersTmp = cmds.ls(type="renderLayer")
    currentLayer = cmds.editRenderLayerGlobals(query=True, crl=True)
    currentLayer = currentLayer.replace('rs_', "")
    renderLayers = [currentLayer]
    # Strip rs_ prefix from layer names
    for layer in renderLayersTmp:
        if "defaultRenderLayer" in layer:
            if len(layer) < 18:
                if layer != currentLayer:
                    renderLayers.append(layer)
        else:
            layer = layer.replace('rs_', "")
            if layer != currentLayer:
                renderLayers.append(layer)
    return renderLayers
    print(
        "----------------- Leaving getRenderLayers --------------------------")


def getRenderOutputDir(versionUp=True):
    print("----------------- In getRenderOutputDir --------------------------")
    directory = getDirectory()
    fileInfo = getFileInfo()
    print("Directory: " + directory)
    version = fileInfo[-2]
    print("File version: " + version)
    userInitials = getUserInitials()
    print("userInitials: " + userInitials)
    versionNumber = version[1:]
    if versionUp == True:
        versionNumber = int(versionNumber) + 1
    print("New version number: " + str(versionNumber))
    version = "%03d" % int(versionNumber)
    version = "v" + str(version)
    print("New version: " + version)
    projShotVers = fileInfo[0] + "_" + fileInfo[1] + "_" + version
    print("New Project Shot Version: " + projShotVers)
    directory = directory + "/" + projShotVers
    # directory = directory.replace("scenes", "frames")
    dirList = directory.split('/')
    animIndex = dirList.index("Animation") + 1
    if dirList[animIndex] == "scenes":
        directory = directory.replace("scenes", "frames")
    else:
        dirList[animIndex] = "frames"
        phase = dirList[animIndex + 2]
        framesProj = "MAYA" + "_" + fileInfo[0]
        dirList[animIndex + 1] = framesProj
        directory = '/'.join(dirList)
    print("Directory path: " + directory)
    print(
        "----------------- Leaving getRenderOutputDir --------------------------"
    )
    return directory


def getRenderVersion():
    print("----------------- In getRenderVersion --------------------------")
    fileInfo = getFileInfo()
    version = fileInfo[-2]
    versionNumber = version[1:]
    versionNumber = int(versionNumber) + 1
    print("New version number: " + str(versionNumber))
    version = "%03d" % int(versionNumber)
    version = "v" + str(version)
    print("New version: " + version)
    print(
        "----------------- Leaving getRenderVersion --------------------------"
    )
    return version


def getSceneFileExtention():
    print(
        "----------------- In getSceneFileExtention --------------------------"
    )
    fileInfo = getFileInfo()
    userName = fileInfo[-1]
    extension = "." + userName.split('.')[1]
    return extension
    print(
        "----------------- Leaving getSceneFileExtention --------------------------"
    )


def getShapeNodes(obj):
    howManyShapes = 0
    getShape = maya.cmds.listRelatives(obj, shapes=True)
    if (getShape == None):
        print('ERROR:: getShapeNodes : No Shape Nodes Connected to ' + obj +
              ' /n')
    return (getShape)


def getShotOBJPath():
    objPath = "Animation/objects/OBJ"
    scenePath = os.path.dirname(cmds.file(q=True, sn=True))
    showPath = scenePath.split('Animation', 1)[0]
    return showPath + objPath


def getUserInitials():
    print("----------------- In getUserInitials --------------------------")
    fileInfo = getFileInfo()
    userName = fileInfo[-1]
    userInitials = userName.split('.')[0]
    print(
        "----------------- Leaving getUserInitials --------------------------")
    return userInitials


####################################################################################################
# Checks
#####################################################################################################
def checkImages():
    print("----------------- In checkImages -----------------")
    foundIssue = False
    localImages = []
    print("Checking for local images......")
    fileList = cmds.ls(type='file')
    if fileList:
        for f in fileList:
            # Get the name of the image attached to it
            texture_filename = cmds.getAttr(f + '.fileTextureName')
            if "/" in texture_filename:
                driveLoc = texture_filename[0]
                print("Drive letter: " + driveLoc)
                if driveLoc == "O":
                    print("Legal file location")
                else:
                    print("ISSUE FOUND --------- " + texture_filename)
                    print("Not legal file location")
                    print("\n")
                    foundIssue = True
                    localImages.append(texture_filename)
            print(" ")
    else:
        print("____No Images in Scene____")
    print(foundIssue)
    print("----------------- Leaving checkImages -----------------")


def checkFileName():
    print("----------------- In checkFileName -----------------")
    foundIssue = False
    fileNameIssue = False
    print(0)
    directory = getDirectory()
    print(1)
    saveDir = directory
    directory = directory[3:]
    fileName = getFileName()
    print(2)
    print(fileName)
    # fileName = fileName[:-4]
    underScores = fileName.count("_")
    print("Number of underscores: " + str(underScores))
    if underScores == 3:
        pass
    else:
        print("FOUND --------- " + "Bad File Name")
        print("\n")
        foundIssue = True
    return foundIssue
    print("----------------- Leaving checkFileName -----------------")


def checkForIssues():
    print("----------------- In checkForIssues -----------------")
    foundIssue = False
    foundLocalImage = checkImages()
    foundFileNameIssue = checkFileName()
    # checkRenderRegions()
    if True in {foundLocalImage, foundFileNameIssue}:
        # if foundIssue == True:
        print("!!!!!!! Issues were found !!!!!!!")
        if foundLocalImage:
            cmds.confirmDialog(
                message='   !!ERRORS FOUND!! \n \n Check for local images')
        if foundFileNameIssue == True:
            cmds.confirmDialog(
                message='   !!ERRORS FOUND!! \n \n Check your File Name')
        print("----------------- Leaving checkForIssues -----------------")
        foundIssue = True
    print(" No Issues were found ")
    return foundIssue
    print("----------------- Leaving checkForIssues -----------------")


####################################################################################################
# Utilities
#####################################################################################################
def cleanName(name):
    print("----------------- In cleanName -----------------")
    cleanName = name.replace(" ", "")
    cleanName = re.sub('\(.*?\)', '', cleanName)
    cleanName = cleanName.replace("_", "")
    print("----------------- Leaving cleanName -----------------")
    return cleanName


def cleanReferencedCameras():
    cmds.select(hierarchy=True)
    sel = cmds.ls(selection=True)
    for i in sel:
        try:
            cmds.camera(i, e=True, startupCamera=False)
            print("Deleting: ", i)
            cmds.delete(i)
        except Exception as e:
            print("Not a camera", e)


@contextmanager
def inplace(filename,
            mode='r',
            buffering=-1,
            encoding=None,
            errors=None,
            newline=None,
            backup_extension=None):
    """Allow for a file to be replaced with new content.

    yields a tuple of (readable, writable) file objects, where writable
    replaces readable.

    If an exception occurs, the old file is restored, removing the
    written data.

    mode should *not* use 'w', 'a' or '+'; only read-only-modes are supported.

    """

    # move existing file to backup, create new file with same permissions
    # borrowed extensively from the fileinput module
    if set(mode).intersection('wa+'):
        raise ValueError('Only read-only file modes can be used')

    backupfilename = filename + (backup_extension or os.extsep + 'bak')
    try:
        os.unlink(backupfilename)
    except os.error:
        pass
    os.rename(filename, backupfilename)
    readable = io.open(backupfilename,
                       mode,
                       buffering=buffering,
                       encoding=encoding,
                       errors=errors,
                       newline=newline)
    try:
        perm = os.fstat(readable.fileno()).st_mode
    except OSError:
        writable = open(filename,
                        'w' + mode.replace('r', ''),
                        buffering=buffering,
                        encoding=encoding,
                        errors=errors,
                        newline=newline)
    else:
        os_mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if hasattr(os, 'O_BINARY'):
            os_mode |= os.O_BINARY
        fd = os.open(filename, os_mode, perm)
        writable = io.open(fd,
                           "w" + mode.replace('r', ''),
                           buffering=buffering,
                           encoding=encoding,
                           errors=errors,
                           newline=newline)
        try:
            if hasattr(os, 'chmod'):
                os.chmod(filename, perm)
        except OSError:
            pass
    try:
        yield readable, writable
    except Exception:
        # move backup back
        try:
            os.unlink(filename)
        except os.error:
            pass
        os.rename(backupfilename, filename)
        raise
    finally:
        readable.close()
        writable.close()
        try:
            os.unlink(backupfilename)
        except os.error:
            pass


def log(message, prefix="Debug", hush=False):
    if not hush:
        print("%s : %s " % (prefix, message))


def exportOBJ():
    try:
        if cmds.pluginInfo("objExport.mll", q=1, loaded=1) == False:
            cmds.loadPlugin("objExport.mll", quiet=1)
    except Exception as e:
        print("Plugins not loaded", e)
    selection = cmds.ls(selection=True)
    showOBJPath = getShotOBJPath()
    cmds.select(clear=True)
    for item in selection:
        cmds.select(item, add=True)
        item = item.replace(":", "-")
        item = item.replace("|", "-")
        objPath = showOBJPath + "/" + item + ".obj"
        print(objPath)
        cmds.file(objPath,
                  op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1",
                  typ="OBJexport",
                  pr=1,
                  es=1,
                  force=1)

    cmds.confirmDialog(message='OBJ saved to:\n' + showOBJPath)


def listMatch(oString, oList):
    newList = [item.lower() for item in oList]
    newString = oString.lower()
    if newString in newList:
        return True
    else:
        return False


def uniqifyList(seq):
    # not order preserving
    set = {}
    map(set.__setitem__, seq, [])
    return set.keys()


def send_mail(send_from,
              send_to,
              subject,
              text,
              files=[],
              server="cybertron02.viscira.local"):
    import smtplib
    import os
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.Utils import COMMASPACE, formatdate
    from email import Encoders
    assert type(send_to) == list
    assert type(files) == list
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    print(msg.as_string())
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment filename="%s"' % os.path.basename(f))
        msg.attach(part)
    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


def saveDebugScene():
    rootDir = "O:/Clients"
    newRootDir = str()
    filename = cmds.file(q=True, sceneName=True)
    currSceneName = os.path.basename(filename)
    currScenePath = os.path.dirname(filename)
    currUser = getUserInitials()
    result = cmds.promptDialog(title='New User Initials',
                               message='Enter Initials:',
                               button=['OK', 'Cancel'],
                               defaultButton='OK',
                               cancelButton='Cancel',
                               dismissString='Cancel')
    if result == 'OK':
        newUserInitials = cmds.promptDialog(query=True, text=True)
    newRootDir = cmds.fileDialog2(startingDirectory="O:/Users/",
                                  dialogStyle=1,
                                  fileMode=3)[0]
    # Make new file name and file path
    print(rootDir)
    print(newRootDir)
    newScenePath = currScenePath.replace(rootDir, newRootDir)
    newSceneName = currSceneName.replace("_" + currUser, "_" + newUserInitials)
    newScenePathFull = newScenePath + "\\" + newSceneName
    # Create new directory structure and copy over file with new name
    print(newScenePath)
    try:
        os.makedirs(newScenePath)
    except Exception as e:
        print("Path exists!", e)
    print(filename)
    print(newScenePathFull)
    try:
        cmds.file(rename=newScenePathFull)
        cmds.file(save=True, type='mayaBinary')
    except Exception as e:
        print("Failed to copy scene file", e)
    print("Debug scene moved to: %s" % (newScenePathFull))
