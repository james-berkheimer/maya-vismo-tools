
# Standard library imports
import struct
from functools import partial
from time import gmtime, strftime
import time, datetime, sys, os, subprocess, shutil, re, getpass, glob
import gc
import platform
import itertools

# Third party imports
import maya.mel as mel
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.cmds as cmds

# Local application imports
import vismo.tools as tools
import mayaObjectData
mod = mayaObjectData.MayaObjectData()

print ( "+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print ( "++++++++   Loading mddWriter Plugin v003   ++++++++++++")
print ( "+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print ( "+++++++++++++++++++++++++")
print ( "+++++   Maya 2018   +++++")
print ( "+++++++++++++++++++++++++")

try:    
    if cmds.pluginInfo("objExport.mll",q=1,loaded=1) == False:
        cmds.loadPlugin("objExport.mll",quiet=1)
    print ( "Plugins loaded")
except:
    print ( "Plugins not loaded")

class MddWriterClass():    
    valList = (1, 0, 0, 0,
               0, 1, 0, 0,
               0, 0, -1, 0,
               0, 0, 0, 1)
    reversMatrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(valList, reversMatrix)

    def __init__(self):
        self.filenames = []
        
    def export(self, exportPath, start, end, meshList, setList, objExportCheck):   
        print ( "\n")
        print ( "------------------------------------------------")
        print ( "----------------- Begin Export -----------------")
        print ( "------------------------------------------------")
        print ( "\n")
        taskStartTime = time.time()
        start = int(start)
        end = int(end)
        res = True
        scale = 1.0
        step = 1
        print ("meshList", meshList)
        vertexPosDict = mod.get_Vert_Dict(meshList, setList)
        self.objExportCheck = objExportCheck
        
        ##########################
        # Open MDD file          #
        ##########################
        mddFiles = self.writeMDD_Instance(exportPath, vertexPosDict)
        
        #first frame
        cmds.currentTime(start, edit=True)
        
        #variables
        fps = float(mel.eval('currentTimeUnitToFPS'))
        print ('FPS:', fps)
        print ( start )
        print ( end )
        numframes = end - start + 1
        print ( numframes )
        rev_dir = "_rev"
        
        ##########################
        #  start write to file   #
        ##########################
        print ("\n")
        print ( "-----------------------------------------------------------")
        print ( "----------------- Start writing MDD files -----------------")
        print ( "-----------------------------------------------------------")
        print ( "\n")
        for mddFile, key in itertools.izip(mddFiles, vertexPosDict):
            numverts = len(vertexPosDict[key])/3
            print ("Write first frame data")             
            # Lets write the first frame data
            mddFile.write(struct.pack(">2i", numframes, numverts))
            mddFile.write(struct.pack(">%di" % numframes, *[frame/fps for frame in xrange(numframes)]))
            mddFile.write(struct.pack(">%df" % (numverts*3), *[v for v in vertexPosDict[key]]))
        
        #write sequence
        amount = 0
        frameRange = (end-start)+1
        cmds.progressWindow(	title='Exporting sequence',
                        progress=amount,
                        status='Finished: 0%',
                        isInterruptable=True ,
                        maxValue = frameRange)
        frame = start
        # while frame < end+1:
        while frame < end:
            if cmds.progressWindow( query=True, isCancelled=True ) :
                break
            cmds.currentTime( frame, edit=True )
            print ('Write cache frame '+str(frame+1))
            vertexPosDict = mod.get_Vert_Dict(meshList, setList)
            for mddFile, key in itertools.izip(mddFiles, vertexPosDict):
                numverts = len(vertexPosDict[key])/3
                if not (numverts*3) == len(vertexPosDict[key]):
                    om.MGlobal.displayError('TOPOLOGY HAS CHANGED!!!')
                    print ('TOPOLOGY HAS CHANGED!!!')
                    res =  False
                    break
                # Write next MDD frame data    
                mddFile.write(struct.pack(">%df" % (numverts*3), *[v for v in vertexPosDict[key]]))
                        
            frame += step
            if cmds.progressWindow( query=True, progress=True ) >= frameRange  :
                break
            amount += 1
            cmds.progressWindow( edit=True, progress=amount, status=('Finished: ' + `amount` + '%' ) )
        cmds.progressWindow(endProgress=1)
        
        #close file
        for mddfile in mddFiles:
            mddFile.close()
        
        cmds.currentTime(start, edit=True)
        seconds = end - start
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print ( "\n")
        print ( "---------------------------------------------------")
        print ( "----------------- Export Complete -----------------")
        print ( "------ Task time %d HR : %02d Min : %02d Sec -----------" % (h, m, s))
        print ( "---------------------------------------------------")
        print ( "\n")
        return res
    
    #################################################
    
    def writeMDD_Instance(self, exportPath, vertexPosDict):
        mddInstances = []
        self.filenames = []
        for item in vertexPosDict:
            meshName = item.replace(":","-")
            meshName = meshName.replace("|","-")
            fileName = self.mddVersionUp(meshName, exportPath)
            self.filenames.append(fileName)
            fullPath = exportPath + "\\" + fileName
            try:                
                self.objExport(item, meshName, exportPath, fullPath, self.objExportCheck)
                print ("Let's create the MDD File name......." + fullPath)
                mddFile = open(fullPath, 'wb')
                mddInstances.append(mddFile)                
            except IOError:
                print ('Error open file ' + fullPath)
                return False
        return mddInstances
        
    #################################################
    
    def getVersion(self, file):
        f1 = file.split(".")[0]
        f2 = f1.split("_")[-1]
        f3 = f2[1:]
        return int(f3)
    
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
   
    def objExport(self, item, meshName, exportPath, mddPath, objExportCheck):
        print ("In objExport")
        print ( "item:", item)
        print ( "meshName:", meshName)
        print ( "exportPath:", exportPath)
        print ( "mddPath:", mddPath)
        print ( 'objExportCheck', objExportCheck)
        print ( 'objExportCheck type', type(objExportCheck))
        objPath = exportPath + "\\" + meshName + '.obj'
        sceneName = cmds.file(q=True, sceneName=True)
        self.writeMetaDataFile(exportPath, meshName, mddPath)
        if objExportCheck == "True":
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
#
#
#
#
#===============================================
# Establish command name
#===============================================
#
#
kPluginCmdName = "mddWriter"
#
#
#===============================================
# Create command
#===============================================

def maya_useNewAPI():
	"""
	The presence of this function tells Maya that the plugin produces, and
	expects to be passed, objects created using the Maya Python API 2.0.
	"""
	pass
	
class MddWriterClassCmd( om2.MPxCommand ):
    
    def __init__(self):
        ''' Constructor. '''
        print ( "===============================================")
        print ( "   In mddWriter   ")
        print ( "==============================================="  )      
        om2.MPxCommand.__init__(self)         
        self.mddwriter = MddWriterClass()        
        # Set default variables        
        self.filePath = ""
        self.startFrame = "1"
        self.endFrame = "2"
        self.meshListString = ""
        self.setListString = ""   
        self.objExport = "True"   
        
    def parseArgs(self, args):
        ''' Parse the command's arguments. ''' 
        print ( "===============================================")
        print ( "   In Parse Args   ")
        print ( "===============================================")
        
        # Create an argument parser object.
        argData = om2.MArgParser( self.syntax(), args )     
        
        # Check if each flag is set, and store its value.
        if argData.isFlagSet( 'ep' ):
            self.filePath = argData.flagArgumentString( 'ep', 0 )
            print ( 'ep' + ': ' + str( self.filePath ))
            
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
        print ( "===============================================")
        print ( "   In Do It   ")
        print ( "===============================================")
        
        # Parse the flags and the arguments
        try:
            self.parseArgs( args )
        except Exception as e:
            # An exception is thrown here if the argument/flag syntax is wrong.
            print( '[' + kPluginCmdName + '] Invalid flag syntax' )
            return
        
        # Run functionality
        meshList = self.meshListString.split(",")
        setList = self.setListString.split(",")        
        self.mddwriter.export(self.filePath, self.startFrame, self.endFrame, meshList, setList, self.objExport)      
#
#
#
#        
#===============================================
# Plug-in Initialization.
#===============================================

def cmdCreator():
    ''' Return an instance of the command. ''' 
    return MddWriterClassCmd()


def syntaxCreator():
    ''' Define the syntax of the command. '''    
    # Create an instance of MSyntax which will contain our command's syntax definition.
    syntax = om2.MSyntax()    
    # Add the flags to the MSyntax object
    syntax.addFlag( 'ep', 'exportpath', om2.MSyntax.kString )
    syntax.addFlag( 'fs', 'framestart', om2.MSyntax.kString )
    syntax.addFlag( 'fe', 'frameend', om2.MSyntax.kString )
    syntax.addFlag( 'ml',  'meshList', om2.MSyntax.kString )
    syntax.addFlag( 'sl', 'setlist', om2.MSyntax.kString )
    syntax.addFlag( 'oe', 'objExport', om2.MSyntax.kString )
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
