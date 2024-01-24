import maya.cmds as cmds

winID = "JamesDoc"
if cmds.window(winID, exists=True):
    cmds.deleteUI(winID)

# Create the first tab UI
tab1Layout = cmds.columnLayout(winID)
cmds.text(" Window 1 ", font='boldLabelFont', bgc=[0.957, 0.808, 0.259])
# Add controls into this Layout
amplitudeSlider = cmds.floatSliderGrp( label='Amplitude', field=True, minValue=-10.0, maxValue=10.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, cw3=(65,75, 100))
sizeSlider = cmds.floatSliderGrp( label='Size', field=True, minValue=-10.0, maxValue=10.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, cw3=(65,75, 100))
cmds.separator()
cmds.floatFieldGrp( numberOfFields=1, label='Time 1', value1=0.3, cw2=(65,75) )
cmds.floatFieldGrp( numberOfFields=1, label='Time 2', value1=0.168, cw2=(65,75) )
cmds.floatFieldGrp( numberOfFields=1, label='Time 3', value1=0.053, cw2=(65,75) )
cmds.separator()
cmds.checkBoxGrp( numberOfCheckBoxes=1, label1='Point Space Local', cw1=(75), cal=(2,'center'))

# Create the second tab UI
cmds.separator( height=20, style='in' )
cmds.text(" Window 2 ", font='boldLabelFont', bgc=[0.957, 0.808, 0.259])
# Add controls into this Layout
amplitudeSlider = cmds.floatSliderGrp( label='Amplitude', field=True, minValue=-10.0, maxValue=10.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, cw3=(65,75, 100))
sizeSlider = cmds.floatSliderGrp( label='Size', field=True, minValue=-10.0, maxValue=10.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, cw3=(65,75, 100))
cmds.separator()
cmds.floatFieldGrp( numberOfFields=1, label='Time 1', value1=0.3, cw2=(65,75) )
cmds.floatFieldGrp( numberOfFields=1, label='Time 2', value1=0.168, cw2=(65,75) )
cmds.floatFieldGrp( numberOfFields=1, label='Time 3', value1=0.053, cw2=(65,75) )
cmds.separator()
cmds.checkBoxGrp( numberOfCheckBoxes=1, label1='Point Space Local', cw1=(75), cal=(2,'center'))
cmds.dockControl(l='Turbolizers', area='right', content=tab1Layout)