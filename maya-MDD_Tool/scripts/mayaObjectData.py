#!/usr/bin/env python

# Standard library imports

# Third party imports
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.cmds as cmds

# Local application imports

class MayaObjectData():    
    valList = (1, 0, 0, 0,
               0, 1, 0, 0,
               0, 0, -1, 0,
               0, 0, 0, 1)
    reversMatrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(valList, reversMatrix)
    def __init__(self):
        self.pointCount = 0
        self.res = True
        self.scale = 1.0
        self.step = 1

    def get_Selection_List(self, *args):        
        #created OpenMaya selectection list
        selected = om.MSelectionList()     
        #get selected items in maya to populate selection list (selected)
        om.MGlobal.getActiveSelectionList(selected)        
        #create global python list so all functions can access it
        global slist        
        #populate python list with selection strings from OpenMaya selection list
        slist = []
        selected.getSelectionStrings(slist)        
        #error handling
        if len(slist)==0:
            om.MGlobal.displayError("You don't have anything selected! List set to 'NULL'")
            slist.append('NULL')   
            
        return selected
        # Example of use
        # get_Selection_List()
        # print list

    #################################################

    def getPoints(self, selection, scale):
        poslist = []
        polyPoints = self.polyPoints(selection, scale)
        if polyPoints:
            poslist += polyPoints
        del polyPoints
        return poslist

    #################################################

    def polyPoints(self, selection, scale):
        dagPath = om.MDagPath()
        selIter = om.MItSelectionList(selection, om.MFn.kTransform)
        polyPoints = []
        while not selIter.isDone():
            selIter.getDagPath(dagPath)
            transformMatrix = dagPath.inclusiveMatrix()
            for child in self.shapeGenerator(dagPath, om.MFn.kMesh):
                objIt = om.MItMeshVertex(child)
                while not objIt.isDone():
                    position = objIt.position(om.MSpace.kObject) * (transformMatrix * self.reversMatrix)
                    polyPoints += [position.x*scale, position.y*scale, position.z*scale]
                    objIt.next()
            selIter.next()
        return polyPoints

    #################################################
    
    def shapeGenerator(self, dagPath, fn):
        dagNode = om.MFnDagNode(dagPath)
        for i in range(dagNode.childCount()):
            child = dagNode.child(i)
            if child.apiType() == fn:
                node = om.MFnDependencyNode(child)
                intermediatePlug = om.MPlug(node.findPlug("intermediateObject"))
                if not intermediatePlug.asBool():
                    yield child
                
    ################################################   
        
    def get_Vert_Dict(self, objList, setList):
        object_Vert_Dict = {}
        cmds.select( clear=True )
        if objList[0]:
            for i in objList:
                cmds.select(i, add=True)
                selected = self.get_Selection_List()
                vertexPositionList = self.getPoints(selected, self.scale)
                object_Vert_Dict[i] = vertexPositionList
                cmds.select( clear=True )
                
        if setList[0]:    
            for i in setList:
                cmds.select(i, add=True)
                selected = self.get_Selection_List()
                vertexPositionList = self.getPoints(selected, self.scale)
                object_Vert_Dict[i] = vertexPositionList
                cmds.select( clear=True )
        
        return object_Vert_Dict
    
    def unicodeClear(self, uc):
        new = []
        for i in uc:
            new.append(i.encode("utf-8"))
        uc = new
        return uc

# od = Maya_Object_Data()
# vertDict = od.get_Vert_Dict()

# for k,v in vertDict.items():
#     print k
    # print k, 'corresponds to', v
