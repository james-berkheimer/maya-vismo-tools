#!/usr/bin/env python

# Third party imports
import maya.OpenMaya as om
import maya.OpenMayaFX as omx
import maya.cmds as cmds

# Local application imports
import vismo.tools as tools

class MeshData(object):
    def __init__(self, objectName):
        tools.log("Getting Mesh Data")
        self.objectName = objectName
        self.faceNormalsDict = {}
        self.oldSelection = cmds.ls(selection=True)
        cmds.select(objectName)        
        self.dataDict = {"v":self.getVerts(),
                         "vn":self.getVertNormals(),
                         "vt":self.getVertTextCoord(),
                         "f":self.getFaces(),
                         "g":self.objectName}
        
    def getMeshData(self):
        tools.log("Mesh Data retrival complete")
        return self.dataDict

    def getVerts(self):
        #Verts
        vertexValues = []
        numVerts = cmds.polyEvaluate(vertex=True)
        tools.log("NumVerts : %s" % numVerts)
        vertexValues = [cmds.pointPosition("%s.vtx[%d]" % (self.objectName,i)) for i in range(numVerts)]
        return vertexValues     
     
    def getVertNormals(self):
        #Normals
        vertNormalValues = [] 
        numFaceNormals = 0
        numFaces = cmds.polyEvaluate(face=True)
        tools.log("NumFaces : %s" % numFaces)
        for face in range(numFaces):
            cmds.select("%s.f[%d]" % (self.objectName,face))
            vertexFaces = cmds.polyListComponentConversion(fromFace=True,toVertexFace=True)
            vertexFaces = cmds.filterExpand(vertexFaces,selectionMask=70,expand=True)
            self.faceNormalsDict[("%s.f[%d]" % (self.objectName,face))] = []
            if vertexFaces:
                for vertexFace in vertexFaces:
                    vertNormalValues.append(cmds.polyNormalPerVertex(vertexFace, query=True, xyz=True))
                    numFaceNormals += 1
                    self.faceNormalsDict[("%s.f[%d]" % (self.objectName,face))].append(numFaceNormals)
        return vertNormalValues
        
    def getVertTextCoord(self): 
        #Texture Coordinates
        textureValues = []
        numTexVerts = cmds.polyEvaluate(uvcoord=True)
        textureValues = [cmds.getAttr("%s.uvpt[%d]" % (self.objectName,i)) for i in range(numTexVerts)]
        return textureValues
    
    def getShadingGroupDict(self):
        shadergroupDict = {}
        shapeName = cmds.listRelatives(self.objectName, shapes=True)
        shadingGroups = set(cmds.listConnections(shapeName, t='shadingEngine'))
        for sg in shadingGroups: 
            shadergroupDict[sg] = []
            for s in cmds.sets(sg, q=True):
                if self.objectName in s or cmds.listRelatives(self.objectName, shapes=True)[0] in s:
                    try: 
                        poly = s.split('[')[1].split(']')[0]
                        if ':' in s.split('[')[1].split(']')[0]:
                            for i in range(int(poly.split(':')[0]), int(poly.split(':')[1])+1):
                                shadergroupDict[sg].append(("%s.f[%d]" % (self.objectName,int(i))))
                        else:
                            shadergroupDict[sg].append(("%s.f[%d]" % (self.objectName,int(poly))))
                    except:
                        # This is for mesh items with only 1 material assignment
                        cmds.select(s)
                        for face in range(cmds.polyEvaluate(face=True)):
                            pf = ("%s.f[%d]" % (self.objectName,face))
                            shadergroupDict[sg].append(pf)
        cmds.select(self.oldSelection)
        return shadergroupDict  
     
    def getFaces(self): 
        #Faces
        facesDict = {}
        vertIndexList = []
        vertNormalIndexList = []
        vertTextureIndexList = []
        numFaces = cmds.polyEvaluate(face=True)
        vnIter = 0
        faceValues = []
        sgdict = self.getShadingGroupDict() 
        for sg, pfaces in sgdict.iteritems():
            facesDict[sg] = []
            for pface in pfaces:
                cmds.select(pface)                
            #-- Verts (v)
                faceVertIndicies = cmds.polyInfo(faceToVertex=True)                
                #This is hacky and should be replaced with snazzy regex
                faceVertIndicies =  [int(fv)+1 for fv in faceVertIndicies[0].split(":")[-1].strip().replace("  "," ").replace("  "," ").replace("  "," ").replace(" ",",").split(",")]
                vertIndexList.append(faceVertIndicies)                
            #-- Normals (vn)
                cmds.select(pface)
                try:
                    vertNormalIndexList.append(self.faceNormalsDict[pface])
                except:
                    for face in range(cmds.polyEvaluate(face=True)):
                        pf = ("%s.f[%d]" % (self.objectName,face))
                        vertNormalIndexList.append(self.faceNormalsDict[pf])                
            #-- Texture (vt)
                cmds.select(pface)
                tex = cmds.polyListComponentConversion(fromFace=True,toUV=True)
                tex = cmds.filterExpand(tex,selectionMask=35,expand=True)
                if tex:
                    tex = [int(t.split("map")[-1].strip("[]")) +1 for t in tex]
                    #Order is incorrect, need to get in same order as vertex ordering
                    tmpDict = {}
                    for t in tex:
                        cmds.select("%s.map[%d]" % (self.objectName,t-1))
                        vertFromTex = cmds.polyListComponentConversion(fromUV=True,toVertex=True)
                        tmpDict[int(vertFromTex[0].split("[")[-1].split("]")[0]) + 1] = t
                    orderedTex=[]
                    for v in vertIndexList[-1]:
                        orderedTex.append(tmpDict[v])
                    vertTextureIndexList.append(orderedTex)
                    face = " ".join( ["%d/%d/%d" % (vertIndexList[-1][j], vertTextureIndexList[-1][j], vertNormalIndexList[-1][j]) for j in range( len( vertTextureIndexList[-1] ) ) ] )
                    facesDict[sg].append(face)
        cmds.select(self.oldSelection)
        return facesDict    

    def get_Selection_List(self, *args):        
        #created OpenMaya selectection list
        selected = om.MSelectionList()     
        #get selected items in maya to populate selection list (selected)
        om.MGlobal.getActiveSelectionList(selected)        
        #create global python list so all functions can access it
        global list        
        #populate python list with selection strings from OpenMaya selection list
        list = []
        selected.getSelectionStrings(list)        
        #error handling
        if len(list)==0:
            om.MGlobal.displayError("You don't have anything selected! List set to 'NULL'")
            list.append('NULL')   
            
        return selected
        # Example of use
        # get_Selection_List()
        # print list
