import maya.cmds as cmds

print("mmTurbulizeSingle_v001 2017\n")
print("Turbulizes meshes, nurbs surfaces and curves and lattices only.\n\n")

def makeTexDeformer(dimension):
    print ("------------ In makeTexDeformer ------------")
    cmds.select(transformNamesArray[0])
    print ("texDefName:", texDefName + "\n")    
    texDefNameDimension = texDefName + dimension
    print ("texDefNameDimension:", texDefNameDimension + "\n")
    cmds.textureDeformer(name=texDefNameDimension, 
                         envelope=1,
                         strength=1,
                         offset=0,
                         vectorStrength=[1,0,0],
                         vectorOffset=[0,0,0],
                         vectorSpace='World',
                         direction='Vector',
                         pointSpace='Local',
                         exclusive='')
    if dimension == 'X':
        cmds.setAttr(texDefNameDimension + ".vectorStrength", 1, 0, 0)
    if dimension == 'Y':
        cmds.setAttr(texDefNameDimension + ".vectorStrength", 0, 1, 0)
    if dimension == 'Z':
        cmds.setAttr(texDefNameDimension + ".vectorStrength", 0, 0, 1)
    cmds.parent(texDefHandleName, groupName)
    cmds.select(texDefHandleName)
    cmds.rename(texDefNameDimension + "Handle0")
    cmds.connectAttr(groupAmplitudeAttr, texDefNameDimension + ".envelope")
    cmds.connectAttr(noiseNode + ".outColor", texDefNameDimension + ".texture")
    cmds.connectAttr(groupName + ".pointSpaceLocal", texDefNameDimension+".pointSpace")
    
    for i in transformNamesArray:
        print ("transformName:", i +"\n")
        cmds.select(i)
        cmds.deformer(texDefNameDimension, e=True, g=i)
    cmds.select(groupName)
    print ("------------ Out makeTexDeformer ------------")
                         

# get list of selected objects filtered by type
print ("get list of selected objects filtered by type")
types = ['nurbsCurve', 'nurbsSurface', 'mesh', 'lattice', 'particle', 'nParticle']
shapeNamesArray = cmds.ls(sl=True, dag=True, lf=True, type=types)

if len(shapeNamesArray) == 0:
    cmds.error("No meshes, nurbs surfaces, curves or lattices selected!")

# get the transform(s); deformers get added via the transform node.
print ("get the transform(s); deformers get added via the transform node.")
transformNamesArray = cmds.listRelatives(shapeNamesArray, p=True)
print ("transformNamesArray: ", transformNamesArray)
print("\n")
cmds.select(clear=True)

texDefName = "turbTextureDeformer"
texDefHandleName = "textureDeformerHandle1"
groupName = "turbulizeGroup0"

# Make grouyp and get name, as if it's an existing name it will get an incremental number added.
print ("Make grouyp and get name, as if it's an existing name it will get an incremental number added.")
cmds.group(empty=True, name=groupName)
groupName = newNameArray = cmds.ls(sl=True)[0]

# Add attributes to group
print ("Add attributes to group")
cmds.addAttr(ln="amplitude", at='double', min=0, max=10, dv=1, k=True)
groupAmplitudeAttr = groupName + ".amplitude"
#---
cmds.addAttr(ln="size", at='double', min=0, max=10, dv=1, k=True)
groupPlacementSizeAttr = groupName + ".size"
#---
cmds.addAttr(ln="time", at='double', dv=1, k=True)
groupTimeAttr = groupName + ".time"

# Set keyframes
print ("Set keyframes")
cmds.setKeyframe(at="time", t=0, v=0, itt='spline', ott='spline')
cmds.setKeyframe(at="time", t=1, v=0.01, itt='spline', ott='spline')
cmds.setAttr(groupName + "_time.preInfinity", 1)
cmds.setAttr(groupName + "_time.postInfinity", 1)

cmds.addAttr(ln="pointSpaceLocal", at='bool')
cmds.setAttr(groupName + ".pointSpaceLocal", 1)

# make the noise texture and set its attributes
print ("make the noise texture and set its attributes")
noiseNode = "texDefVolNoise0"
cmds.shadingNode('volumeNoise', n=noiseNode, at=True)
cmds.setAttr(noiseNode + ".ratio", 0.6)
cmds.setAttr(noiseNode + ".colorOffset", -0.5, -0.5, -0.5, type='double3')
cmds.setAttr(noiseNode + ".frequency", 4)
cmds.setAttr(noiseNode + ".noiseType", 0)
cmds.connectAttr(groupTimeAttr, noiseNode + ".time")

# Create placement node.
print ("Create placement node.")
placementNode = noiseNode + "_3dPlacement"
cmds.shadingNode('place3dTexture', n=placementNode, au=True, at=True)
cmds.connectAttr(placementNode + ".worldInverseMatrix", noiseNode + ".placementMatrix")
cmds.setAttr(placementNode + ".inheritsTransform", 0)
cmds.parent(placementNode, groupName)
cmds.connectAttr(groupPlacementSizeAttr, placementNode + ".scaleX")
cmds.connectAttr(groupPlacementSizeAttr, placementNode + ".scaleY")
cmds.connectAttr(groupPlacementSizeAttr, placementNode + ".scaleZ")

# connect object(s) to deformer.
print ("connect object(s) to deformer.")
makeTexDeformer('X')
makeTexDeformer('Y')
makeTexDeformer('Z')


                       
                         
                         


