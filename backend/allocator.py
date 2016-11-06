from IR import IRLink

'''
Created on Sep 4, 2016

@author: christianburkhartsmeyer
'''

VRToPR = []
PRToVR = []
NextUse = []

VRToLIVal = [] #If VR value last modified by LI, no spill necessary
# and loading again is just a rematerialization

# No memory loc to keep track of where spill vals are, just use 32768 + 16 * VR (ex. VR2 @ 32800)

# Add instructions to store the value previously held in freePR
def spill(spilledVR, freePR, reservedRegister, curInstr):
    global VRToLIVal
    
    #print "Spilling"
    
    # If the last modification to this term was just a LI, no need to save it, we'll get it back w/ an LI
    if VRToLIVal[spilledVR] != -1:
        return
    
    newBlockStart = curInstr.getPrev()
    newBlockStartSpill = IRLink([0,"loadl", 32768 + (16 * spilledVR), 0,0,0,0,0,0,0,0,0,reservedRegister,0,0], True)
    newBlockSaveSpill = IRLink([0,"store", 0,0,freePR,0, 0,0,reservedRegister,0, 0,0,0,0, 0], True)
    # Add to linked list
    newBlockStart.setNext(newBlockStartSpill)
    newBlockStartSpill.setPrev(newBlockStart)
    newBlockStartSpill.setNext(newBlockSaveSpill)
    newBlockSaveSpill.setPrev(newBlockStartSpill)
    newBlockSaveSpill.setNext(curInstr)
    curInstr.setPrev(newBlockSaveSpill)

# Add instructions to load the value for VR VRToLoad into freePR.
def loadFromSpill(VRToLoad, freePR, reservedReg, curInstr):
    global VRToLIVal
    
    #print "Loading from spill for vr: " + str(VRToLoad)
    
    # If this VR was stored as the result of an LI, rematerialize w/ that same LI
    # MAJOR CHANGE: this should have been checking if the VR's val was the result of an LI.  D'o!
    #if VRToLIVal[freePR] != -1:
    if VRToLIVal[VRToLoad] != -1:
        #print "Value being loaded: " + str(VRToLIVal[freePR])
        remat = IRLink([0,"loadl", VRToLIVal[VRToLoad],0,0,0, 0,0,0,0, 0,0,freePR,0, 0], True)
        #Put it back in the linked list
        start = curInstr.getPrev()
        start.setNext(remat)
        remat.setPrev(start)
        remat.setNext(curInstr)
        curInstr.setPrev(remat)
    # Otherwise reload w/ instructions:
    # loadI 327688 + (16 * VRToLoad) => reservedReg
    # load reservedReg => freePR
    else:
        newBlockStart = curInstr.getPrev()
        newBlockStartLoad = IRLink([0,"loadl", 32768 + (16 * VRToLoad),0,0,0, 0,0,0,0, 0,0,reservedReg,0, 0], True)
        newBlockLoad = IRLink([0,"load", 0,0,reservedReg,0, 0,0,0,0, 0,0,freePR,0, 0], True)
        # Rebuild linked list
        newBlockStart.setNext(newBlockStartLoad)
        newBlockStartLoad.setPrev(newBlockStart)
        newBlockStartLoad.setNext(newBlockLoad)
        newBlockLoad.setPrev(newBlockStartLoad)
        newBlockLoad.setNext(curInstr)
        curInstr.setPrev(newBlockLoad)


def allocatePRS(firstInstr, numVRs, numPRs):
    global VRToPR
    global PRToVR
    global NextUse
    
    global VRToLIVal
    
    # TODO: Should i subtract one from numPR's for spilling?
    # Temporary soln:
    if numVRs > numPRs:
        numPRs -= 1
        reservedReg = numPRs
        #print "Num used PRs: " + str(numPRs) + " , w/ reserved Reg: " + str(reservedReg)
    
    VRToPR = [-1] * numVRs
    PRToVR = [-1] * (numPRs + 1) # +1 b/c 1 reserved
    NextUse = [-1] * (numPRs + 1)
    
    VRToLIVal = [-1] * (numVRs + 1)
    
    commentsOn = False
    curInstr = firstInstr
    j = 0
    while True:
        #print "Inst: " + str(j)
        j += 1
        
        thisTable = curInstr.getTable()
        if commentsOn:
            print "Instr: " + str(j) + " is: " + str(thisTable)
            print "PR's: " + str(PRToVR)
        PROP1 = -1
        PROP2 = -1
        
        #Handle OP1, only memop and arithop have r1
        #print " = loadl? " + str(thisTable[1])
        if thisTable[1] != "nop" and thisTable[1] != "output" and thisTable[1] != "loadl" :
            op1VR = thisTable[3]
            op1NextUse = thisTable[5]
            #See if there's a free PR
            freePR = -1
            for i in range(numPRs):
                # If this vr is in a reg, use that one
                if PRToVR[i] == op1VR:
                    freePR = i
                    break
            # If our VR isn't already stored in a PR, search for a free one
            if freePR == -1:
                for i in range(numPRs):
                    if PRToVR[i] == -1:
                        freePR = i
                        loadFromSpill(op1VR, i, reservedReg, curInstr)
                        break

            # If there wasn't, spill the one with the furthest next use
            if freePR == -1:
                farthestPR = 0
                usedAt = NextUse[0]
                for i in range(numPRs - 1):
                    # TODO: Should I choose which to spill arbitrarily when equal?  Slides
                    if NextUse[1 + i] > usedAt:
                        farthestPR = 1 + i
                        usedAt = NextUse[1 + i]
                spilledVR = PRToVR[farthestPR]
                if commentsOn:
                    print "Had to spill for op 1, spilling PR: " + str(farthestPR) + " , which is VR: " + str(spilledVR) + ", which is next used at: " + str(usedAt)
                # TODO: Spill and load op val from mem
                freePR = farthestPR
                VRToPR[spilledVR] = -1
                spill(spilledVR, freePR, reservedReg, curInstr)
                loadFromSpill(op1VR, freePR, reservedReg, curInstr)
                #VRToLIVal remains unchanged, loaded from loadI now if was prev, and vv
            
            PRToVR[freePR] = op1VR
            NextUse[freePR] = op1NextUse
            PROP1 = freePR
            
            if commentsOn:
                print "OP 1, vr: " + str(op1VR) + " in pr: " + str(freePR)
                            
            # Keep track of 
            thisTable[4] = freePR

        #Handle OP2
        # Arithops and store, since op2 is a use, not a definition
        if thisTable[1] == "add" or thisTable[1] == "sub" or thisTable[1] == "mult" or thisTable[1] == "lshift" or thisTable[1] == "rshift" or thisTable[1] == "store": 
            op2VR = thisTable[7]
            op2NextUse = thisTable[9]
            
            #See if there's a free PR
            freePR = -1
            for i in range(numPRs):
                # If this vr is in a reg, use that one
                if PRToVR[i] == op2VR:
                    freePR = i
                    break
            # If our VR isn't already stored in a PR, search for a free one
            if freePR == -1:
                for i in range(numPRs):
                    if PRToVR[i] == -1:
                        freePR = i
                        loadFromSpill(op2VR, i, reservedReg, curInstr)
                        break

            # If there wasn't, spill the one with the furthest next use THAT ISNT'T USED IN OP 1
            if freePR == -1:
                farthestPR = 0
                usedAt = -10
                for i in range(numPRs):
                    # TODO: Should I choose which to spill arbitrarily when equal?  Slides
                    # TODO2: Think I might have resolved this ^.  But should we
                    # Be checking if we're past the current instruction for NextUse?
                    if NextUse[i] > usedAt and PRToVR[i] != op1VR:
                        farthestPR = i
                        usedAt = NextUse[i]
                spilledVR = PRToVR[farthestPR]
                if commentsOn:
                    print "Had to spill for OP2, spilling PR: " + str(farthestPR) + " , which is VR: " + str(spilledVR) + ", which is next used at: " + str(usedAt)
                # TODO: Spill and load OP2 val
                freePR = farthestPR
                VRToPR[spilledVR] = -1
                spill(spilledVR, freePR, reservedReg, curInstr)
                loadFromSpill(op2VR, freePR, reservedReg, curInstr)
                #VRToLIVal remains unchanged, loaded from loadI now if was prev, and vv
                
            PRToVR[freePR] = op2VR
            NextUse[freePR] = op2NextUse
            PROP2 = freePR

            if commentsOn:
                print "OP 2, vr: " + str(op2VR) + " in pr: " + str(freePR)
                        
            # Keep track of in IR
            thisTable[8] = freePR
            
        # Free PR's for 1/2 if NextUse is INFINITY
        if PROP1 != -1 and op1NextUse == float("inf"):
            if commentsOn:
                print "OP 1 inf next use, virt:"  + str(op1VR)
            VRToPR[op1VR] = -1
            PRToVR[PROP1] = -1
            VRToLIVal[op1VR] = -1
            NextUse[PROP1] = float("inf")
        
        if PROP2 != -1 and op2NextUse == float("inf"):
            if commentsOn:
                print "OP 2 inf next use, virt: " + str(op2VR)
            VRToPR[op2VR] = -1
            PRToVR[PROP2] = -1
            VRToLIVal[op2VR] = -1
            NextUse[PROP2] = float("inf")
            
        #Handle OP3
        if thisTable[1] != "output" and thisTable[1] != "nop" and thisTable[1] != "store":
            op3VR = thisTable[11]
            op3NextUse = thisTable[13]
                
            #print "Op 3: " + str(op3VR)
            #print thisTable
            
            #See if there's a free PR
            freePR = -1
            #print str(numPRs)
            for i in range(numPRs):
                if PRToVR[i] == -1:
                    freePR = i
                    break

            # If there wasn't, spill the one with the furthest next use
            # TODO: Do we need to 
            if freePR == -1:
                farthestPR = 0
                usedAt = NextUse[0]
                for i in range(numPRs - 1):
                    # TODO: Should I choose which to spill arbitrarily when equal?  Slides
                    if NextUse[1 + i] > usedAt:
                        farthestPR = 1 + i
                        usedAt = NextUse[1 + i]
                spilledVR = PRToVR[farthestPR]
                if commentsOn:
                    print "Had to spill for OP3, spilling PR: " + str(farthestPR) + " , which is VR: " + str(spilledVR) + ", which is next used at: " + str(usedAt)

                # TODO: If we had to spill, save vr's val to memory
                freePR = farthestPR
                VRToPR[spilledVR] = -1
                
                #Need to save old val to memory, addr determined by spilledVR
                # Looks like:
                # loadL 32768 + (16 * spilledVR) => reservedReg
                # store freePR => reservedReg
                spill(spilledVR, freePR, reservedReg, curInstr)
                            
            PRToVR[freePR] = op3VR
            NextUse[freePR] = op3NextUse
            
            # If OP3 PR set w/ loadI, note in array
            if thisTable[1] == 'loadl':
                #print "Setting vr2li for vr: " + str(op3VR) + " as: " + str(thisTable[2])
                VRToLIVal[op3VR] = thisTable[2]
            else:
                VRToLIVal[op3VR] = -1
            
            if commentsOn:
                print "OP 3, vr: " + str(op3VR) + " in pr: " + str(freePR)
            
            # Keep track of in IR
            thisTable[12] = freePR
            
        if commentsOn:
            print "Table: " + str(thisTable)
            print "PR's: " + str(PRToVR)
            print "VR to LI Vals: " + str(VRToLIVal)
        
        nextInst = curInstr.getNext()
        if nextInst == None:
            break
        else:
            curInstr = curInstr.getNext()
    """
    for eachInstr:
        if OP1 used in instruction:
            if OP1 needs register:
                get one
            # If it's dead, free it
            if OP1.NU == INF:
                reset
            
        if OP2...
        
        if OP3...
    
    """
    
    return 0