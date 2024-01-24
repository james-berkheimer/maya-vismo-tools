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
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.cmds as cmds

# Local application imports
import vismo.tools as tools

# Establish Deadline launch commands
launch_script = "\\custom\\scripts\\Submission\\Maya\\VISMO_MayaRenderSubmission.py"
# launch_script = "\\custom\\scripts\\Submission\\Maya\\DEV_MayaRenderSubmission.py"
deadlinebin = os.environ['DEADLINE_PATH'].split(os.pathsep)
deadlinebin = deadlinebin[0]
deadlinecommand = deadlinebin + "\\" + "deadlinecommand.exe"
deadlinecmd = [deadlinecommand, '-getrepositoryroot']

# Make deadeline launch command
deadlinecommandbg = deadlinebin + "\\" + "deadlinecommandbg.exe"
print(deadlinebin)
print(deadlinecommand)
print(deadlinecommandbg)

# Make path to launch script
launch_script_path = os.getenv('DEADLINE_REPOSITORY') + launch_script

####################################################################################################
# Run Renders
#####################################################################################################


def launchDeadline(sceneFileFull=""):
    print(
        "********************************** In launchDeadline **********************************"
    )
    print(
        "***************************************************************************************"
    )
    print(
        "***************************************************************************************"
    )
    if sceneFileFull[0] == "":
        # If scene filename is empty, tell user that they must save the scene file.
        errmsg = "Scene must be saved once before it can be submitted to Deadline"
        # error_dialog(errMsg)
        sys.extit()
    fileTypeBox = tools.getFileType()
    fileTypeBox = fileTypeBox.upper()
    frameRange = tools.getFrameRange()
    mayaVersion = cmds.about(version=True)
    sceneVersion = tools.getRenderVersion()
    projectPath = cmds.workspace(q=True, rd=True)
    projectCode = tools.getProjectCode()
    projectPhase = tools.getProjectPhase()
    frameSize = tools.getFrameSize()
    renderer = tools.getRenderer()
    cameraNames = tools.getRenderCameras()
    renderableCam = tools.getRenderableCam()
    oldIndex = list(cameraNames).index(renderableCam)
    try:
        list(cameraNames).pop(oldIndex)
    except:
        print("No items to pop")
    list(cameraNames).insert(0, renderableCam)
    renderLayers = tools.getRenderLayers()

    # This turns a list of strings into a single string, separating items with commas
    cameraNamesString = ",".join(list(cameraNames))
    renderLayersString = ",".join(renderLayers)

    outputArguments = []
    outputArgumentsString = ""
    outputPath = cmds.workspace(fre="images")
    print("This is the output path for Deadline: " + outputPath)

    print("================ DEBUG ================")
    print("Script: " + launch_script_path)
    print("sceneFileFull: " + sceneFileFull)
    print("frameRange: " + frameRange)
    print("mayaVersion: " + str(mayaVersion))
    print("projectCode: " + projectCode)
    print("projectPhase: " + projectPhase)
    print("frameSize: " + frameSize)
    print("renderer: " + renderer)
    print("fileTypeBox: " + fileTypeBox)
    print("cameraNamesString: " + cameraNamesString)
    print("renderLayersString: " + renderLayersString)
    print("outputPath: " + outputPath)
    print("sceneVersion: " + sceneVersion)
    print("projectPath:  " + projectPath)

    print("============== START =================")

    if launch_script_path:
        launchDeadline = [
            deadlinecommandbg, '-executescript', launch_script_path,
            str(sceneFileFull),
            str(frameRange),
            str(outputPath),
            str(fileTypeBox),
            str(projectCode),
            str(projectPhase),
            str(mayaVersion),
            str(frameSize),
            str(projectPath),
            str(cameraNamesString),
            str(renderLayersString),            
            str(renderer)
        ]
        print("Launch Command: ")
        print(launchDeadline)
        
        print("============== RUNNING POPEN =================")
        process = subprocess.Popen(launchDeadline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("stdout: ")
        print(stdout)
        print("stdout: :")
        print(stderr)
        
        print("============== FINISHED =================")     
        

    else:
        scripterrmsg = "The VISMO_MayaRenderSubmission.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine,\nthat the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository."
        # error_dialog(scripterrmsg)
        print (scripterrmsg)

    print(
        "********************************** Leaving launchDeadline **********************************"
    )
