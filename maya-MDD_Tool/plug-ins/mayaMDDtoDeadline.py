#!/usr/bin/env python

# Standard library imports
import os
import sys, string
import subprocess

# Third party imports
import maya.api.OpenMaya as om2
import maya.cmds as cmds

print ("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print ("+++++   Loading Deadline MDD Launch Plugin v002   +++++")
print ( "+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print ( "+++++++++++++++++++++++++")
print ( "+++++   Maya 2018   +++++")
print ( "+++++++++++++++++++++++++")

# Establish command name
kPluginCmdName = "deadlinelaunch"

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

#===============================================
# Create command
#===============================================
class Deadline_Launch( om2.MPxCommand ): 
    print ( "+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print ( "+++++   In Deadline_Launch                        +++++")
    print ( "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" )
    def __init__(self):
        ''' Constructor. '''  
        om2.MPxCommand.__init__(self)
        # scriptDir = cmds.pluginInfo("mayaMDDtoDeadline.py", query=True, p=True)
        # scriptDir = os.path.dirname(os.path.dirname(scriptDir))
        scriptDir = "O:\\Assets\\Animation_Share\\VISMO_Tools\\Maya\\2018\\Modules\\mayaMDDTool"
        # scriptDir = "O:\\Users\\jBerkheimer\\Scripts\\Maya\\2018\\Modules\\mayaMDDTool"
        cmdScript = "\\scripts\\mayaCmdLineMddExport.py"
        self.cmdScript_Path = scriptDir + cmdScript
        self.exportPath = "Export Path"
        self.startFrame = "1"
        self.endFrame = "2"
        self.meshListString = ""
        self.setListString = ""
        self.objExport = True 
        self.sceneFileFull = cmds.file( q=True, l=True )[0]   
        if self.sceneFileFull[0] == "":        
            # If scene filename is empty, tell user that they must save the scene file.
            errmsg = "Scene must be saved once before it can be submitted to Deadline"
            self.error_dialog(errMsg)
            sys.extit()        
                
        # Establish Deadline launch commands          
        launch_script = "\\custom\\scripts\\Submission\\\Maya\\VISMO_MayaCommandLineSubmission.py"
        deadlinebin = os.environ['DEADLINE_PATH'].split(os.pathsep)
        deadlinebin = deadlinebin[0]
        deadlinecommand = deadlinebin +  "\\" + "deadlinecommand.exe"
        deadlinecmd = [deadlinecommand, '-getrepositoryroot']      
          
        # Make deadeline launch command 
        self.deadlinecommandbg = deadlinebin +  "\\" + "deadlinecommandbg.exe"        
        print(deadlinebin)
        print(deadlinecommand)
        print(self.deadlinecommandbg)
        os.chdir(deadlinebin)
        p = subprocess.Popen(deadlinecmd, stdout=subprocess.PIPE)
        root = p.stdout.read()
        root = root.rstrip()
        
        # Make path to launch script
        self.launch_script_path = root + launch_script
        
    def parseArgs(self, args):
        ''' 
        The presence of this function is not enforced,
        but helps separate argument parsing code from other
        command code. 
        '''
        # The following MArgParser object allows you to check if specific flags are set.
        argData = om2.MArgParser( self.syntax(), args )          
        
        # Check if each flag is set, and store its value            
        if argData.isFlagSet( 'ep' ):
            self.exportPath = argData.flagArgumentString( 'ep', 0 )
            print ( 'ep' + ': ' + str( self.exportPath ))
            
        if argData.isFlagSet( 'fs' ):
            self.startFrame = argData.flagArgumentString( 'fs', 0 )
            print ( 'fs' + ': ' + str( self.startFrame ))
            
        if argData.isFlagSet( 'fe' ):
            self.endFrame = argData.flagArgumentString( 'fe', 0 )
            print ( 'fe' + ': ' + str( self.endFrame ))
            
        if argData.isFlagSet( 'ml' ):
            self.meshListString = argData.flagArgumentString( 'ml', 0 )
            print ( 'ml' + ': ' + str( self.meshListString ))
            
        if argData.isFlagSet( 'sl' ):
            self.setListString = argData.flagArgumentString( 'sl', 0 )
            print ( 'sl' + ': ' + str( self.setListString ))
            
        if argData.isFlagSet( 'oe' ):
            self.objExport = argData.flagArgumentString( 'oe', 0 )
            print ( 'oe' + ': ' + str( self.objExport ))
            
        
    def doIt(self, args):
        ''' Command's first-time execution. '''
        # Set mayapy executable path
        if cmds.about(version=True) == '2015':
            print ( "Maya 2015")
            executable = "C:\\Program Files\\Autodesk\\Maya2015\\bin\\mayapy.exe"
        elif cmds.about(version=True) == '2016': 
            print ( "Maya 2016")
            executable = "C:\\Program Files\\Autodesk\\Maya2016\\bin\\mayapy.exe"
        elif "2016 Extension 2" in cmds.about(version=True): 
            print ( "Maya 2016.5")
            executable = "C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\mayapy.exe"
        elif cmds.about(version=True) == '2017': 
            print ( "Maya 2017")
            executable = "C:\\Program Files\\Autodesk\\Maya2017\\bin\\mayapy.exe"
        elif cmds.about(version=True) == '2018': 
            print ( "Maya 2018")
            executable = "C:\\Program Files\\Autodesk\\Maya2018\\bin\\mayapy.exe"
            
        # Parse the flags and the arguments
        try:
            # We recommend parsing your arguments first.
            self.parseArgs( args )
        except Exception as e:
            # An exception is thrown here if the argument/flag syntax is wrong.
            print ( e)
            print( '\n----[' + kPluginCmdName + ']---- Invalid flag syntax \n' )          
            return        
            
        # Clear the current selection list to avoid any wrong grouping.
        # om2.MGlobal.clearSelectionList()
             
        # Run functionality
        if self.launch_script_path:            
            launchDeadline = [self.deadlinecommandbg, '-executescript', self.launch_script_path, executable, self.cmdScript_Path, self.sceneFileFull, self.exportPath, self.startFrame, self.endFrame, self.meshListString, self.setListString, self.objExport]
            process = subprocess.Popen(launchDeadline, stdout=subprocess.PIPE)
            process.wait()            
        else:
            scripterrmsg = "The VISMO_MayaCommandLineSubmission.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine,\nthat the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository."
            self.error_dialog( scripterrmsg )
        
    
        
        
#===============================================
# Plug-in Initialization.
#===============================================    
def cmdCreator():
        ''' Return an instance of the command. '''
        return Deadline_Launch()
        
def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''    
    # Create an instance of MSyntax which will contain our command's syntax definition.
    syntax = om2.MSyntax()    
    
    # Add the flags to the MSyntax object
    syntax.addFlag( 'ep', 'exportPath', om2.MSyntax.kString )
    syntax.addFlag( 'fs', 'startFrame', om2.MSyntax.kString )
    syntax.addFlag( 'fe', 'endFrame', om2.MSyntax.kString )
    syntax.addFlag( 'ml', 'meshListString', om2.MSyntax.kString )
    syntax.addFlag( 'sl', 'setListString', om2.MSyntax.kString )
    syntax.addFlag( 'oe', 'objExport', om2.MSyntax.kBoolean )
    return syntax

def initializePlugin( mobject ):
    ''' Initialize the plug-in when Maya loads it. '''
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator, syntaxCreator )
    except:
        sys.stderr.write( 'Failed to register command: ' + kPluginCmdName )
        # raise

def uninitializePlugin( mobject ):
    ''' Uninitialize the plug-in when Maya un-loads it. '''
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( 'Failed to unregister command: ' + kPluginCmdName )
        # raise
        
        
#===============================================
# Sample Usage.
#===============================================
''' 
# Copy the following lines and run them in Maya's Python Script Editor:

import maya.cmds as cmds
cmds.deadlinelaunch()
'''

    
    
    
    
    
    
    