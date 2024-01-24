
        # cmds.addAttr(ln="WaveType", at='enum', en="sin:cos")
        # cmds.addAttr(ln="FrequencyMult", at='double', min=-10, max=10, dv=1.0, k=True)
        # cmds.addAttr(ln="Amplitude", at='double', min=-10, max=10, dv=1.0, k=True)
        # cmds.addAttr(ln="Offset", at='double', min=0, max=10, dv=1.0, k=True)
        # cmds.addAttr(ln='WaveValue', at='double', dv=0)
        # expString = 'if ('+ groupName + '.WaveType == 0){\n'
        # expString += groupName + '.WaveValue = sin((time * ' + groupName + '.FrequencyMult) * ' + groupName + '.Amplitude) + ' + groupName + '.Offset;\n}'
        # expString += '\nelse {\n' + groupName + '.WaveValue = cos((time * ' + groupName + '.FrequencyMult) * ' + groupName + '.Amplitude) + ' + groupName + '.Offset;\n}'
        # cmds.expression( s=expString,
        #                  o=groupName,
        #                  n="WaveValue",
        #                  ae=1,
        #                  uc=all )
        # cmds.addAttr(ln='newTime1', at='double', dv=0)
        # expString = (groupName + '.newTime1 = ' + groupName + '.WaveValue * 0.5;')
        # cmds.expression(s=expString, o=groupName, n='newTime1', ae=1, uc=all)
        # cmds.addAttr(ln='newTime2', at='double', dv=0)
        # expString = (groupName + '.newTime2 = ' + groupName + '.WaveValue * 1.5;')
        # cmds.expression(s=expString, o=groupName, n='newTime2', ae=1, uc=all)
        # cmds.addAttr(ln='newTime3', at='double', dv=0)
        # expString = (groupName + '.newTime3 = ' + groupName + '.WaveValue * 2.5;')
        # cmds.expression(s=expString, o=groupName, n='newTime3', ae=1, uc=all)
        
              
        # inTangentTypeString = 'spline'
        # outTangentTypeString = 'spline'
        # loopLength = 30
        # timeMult1 = [0, 0.5, 1]
        # timeMult2 = [0.33, 0.83, 1.33]
        # timeMult3 = [0.67, 1.17, 1.67]
        # self.addTimeAttr(groupName, 'Time1', loopLength, inTangentTypeString, outTangentTypeString, timeMult1)
        # self.addTimeAttr(groupName, 'Time2', loopLength, inTangentTypeString, outTangentTypeString, timeMult2)
        # self.addTimeAttr(groupName, 'Time3', loopLength, inTangentTypeString, outTangentTypeString, timeMult3)
        
        
        
        
        # #####
        # cmds.addAttr(ln='WaveValue', at='double', dv=0)
        # expString = 'if ('+ groupName + '.WaveType == 0){\n'
        # expString += groupName + '.WaveValue = sin(' + groupName + '.radians * ' + groupName + '.Offset);\n}'
        # expString += '\nelse {\n' + groupName + '.WaveValue = cos(' + groupName + '.radians * ' + groupName + '.Offset);\n}'
        # cmds.expression( s=expString,
        #                  o=groupName,
        #                  n="WaveResult",
        #                  ae=1,
        #                  uc=all )
        # #####
        
        
        
        
    # def addTimeAttr(self, groupName, name, loopLength, inTangentTypeString, outTangentTypeString, timeMult):
    #     print ("------------ In addTimeAttr ------------")
    #     loopLengthAdjusted = loopLength * 0.2
    #     time = timeMult[0]
    #     cmds.addAttr(ln=name, at='double', dv=0, k=True)
    #     cmds.setKeyframe(at=name, time=time, value=0, inTangentType=inTangentTypeString, outTangentType=outTangentTypeString)
    #     time = loopLength * timeMult[1]
    #     cmds.setKeyframe(at=name, time=time, value=loopLengthAdjusted, inTangentType=inTangentTypeString, outTangentType=outTangentTypeString)
    #     time = loopLength * timeMult[2]
    #     cmds.setKeyframe(at=name, time=time, value=0, inTangentType=inTangentTypeString, outTangentType=outTangentTypeString)
    #     cmds.setAttr(groupName + "_" + name + ".preInfinity", 3)
    #     cmds.setAttr(groupName + "_" + name + ".postInfinity", 3)
    #     print ("------------ In addTimeAttr ------------")