'''
Created on Sep 1, 2016

@author: christianburkhartsmeyer
'''

SRToVR = {}
LU = {}
VRName = 0

def update(OPtable, OPnum, index):
    global SRToVR
    global LU
    global VRName
    
    startThisOp = 2 + (OPnum - 1)*4
    
    if SRToVR[OPtable[startThisOp+0]] == -1:
        SRToVR[OPtable[startThisOp+0]] = VRName
        VRName += 1
    OPtable[startThisOp+1] = SRToVR[OPtable[startThisOp+0]]
    OPtable[startThisOp+3] = LU[OPtable[startThisOp+0]]
    LU[OPtable[startThisOp + 0]] = index
    
    #Not sure if I should be doing this here, but just tag them?


def renameVirtRegisters(firstInstruction, lastInstruction, numLines, maxSrcReg):
    global SRToVR
    global LU
    global VRName

    #print "\nFinding live ranges, virtual registers\n"
    
    #Initialize mappings
    for i in range(maxSrcReg + 1):
        SRToVR[i] = -1
        LU[i] = float("inf")
        
    curInstruction = lastInstruction
    #print "Last: " + lastInstruction.__str__()
    #print "First: " + firstInstruction.__str__()
    #print "Cur: " + curInstruction.__str__()
    #print "#: " + maxSrcReg.__str__()
    #print "Max src reg num? " + str(maxSrcReg)
    # Traverse the instruction set in reverse, find LR's and 
    for j in range(numLines):
        i = numLines - (j + 1)
        #print "looking at inst: " + str(i)
        curOpTable = curInstruction.getTable()
        instName = curOpTable[1]
        #print "Instruction: " + instName
        #Update and kill op 3 IF ITS A REGISTER (remember store)
        if instName != 'output' and instName != 'nop' and instName != "store":
            update(curOpTable, 3, i)
            #TODO: Slide 29 hint, does each distinct use have a fresh VR w/ this line?
            SRToVR[curOpTable[10]] = -1
            LU[curOpTable[10]] = float("inf")


        if instName != "loadl" and instName != "nop" and instName != "output":
            update(curOpTable, 1, i) #First op, only update if a register
        if instName != "load" and instName != "loadl" and instName != "nop" and instName != "output":
            update(curOpTable, 2, i) #2nd op, only update if not load/l, 
            
        #print "optable afterwards: " + str(curOpTable)
        #Fetch next line
        curInstruction = curInstruction.getPrev()
        