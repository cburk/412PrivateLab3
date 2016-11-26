'''
Created on Aug 30, 2016

@author: christianburkhartsmeyer
'''
from sys import argv
from frontend.parser import parseFile
from backend.virtualizer import renameVirtRegisters
from IR import IRLink
from backend.allocator import allocatePRS
from depGraphMaker import getDependencyGraph, setRanks
from scheduler import scheduleInstructions

if len(argv) == 2:
    if argv[1] == '-h':
        print """\n
        schedule -h  : lists valid commands
        schedule is nor reguired to process any args after schedule -h

        schedule <file name> : performs instruction scheduling on the iloc file <file name>.
        Produces an equivalent program.  Uses square bracket notation, is not required to parse
        args after schedule <file name>
                   """
    else:
        # Scan and parse file, front end
        firstLast = parseFile(argv[1])
        IRInst1 = firstLast[0]
        IRInstFinal = firstLast[1]
        numLines = firstLast[2]
        maxSRnum = firstLast[3]

        #Renaming to virt registers, fill in live ranges
        renameVirtRegisters(IRInst1, IRInstFinal, numLines, maxSRnum)

        print "After renaming:"
        curInst = IRInst1
        instNum = 1
        while(curInst != None):
            thisTable = curInst.getTable()
            #print "This table: " + str(thisTable)
            print str(instNum) + " : " + curInst.getVirtView()
            curInst = curInst.getNext()
            instNum += 1
            #print "Renaming view over,"


        #print "Max vrn num before: NA"
        maxVRNum = 0
        curInst = IRInst1
        while(curInst != None):
            thisTable = curInst.getTable()
            if thisTable[3] > maxVRNum:
                maxVRNum = thisTable[3]
            if thisTable[7] > maxVRNum:
                maxVRNum = thisTable[7]
            if thisTable[11] > maxVRNum:
                maxVRNum = thisTable[11]
            curInst = curInst.getNext()
            #print "Max vrn num after: " + str(maxVRNum)

        # Keep track of value stored in known vr's
        VRToValue = {}
        for i in range(maxVRNum):
            VRToValue[i] = -1
        ValueToVR = {}
        curInst = IRInst1
        while(curInst != None):
            thisTable = curInst.getTable()
            thisOpName = curInst.getOpName()

            if thisOpName == 'nop':
                # do nothing
                1 + 1
            elif thisOpName == 'loadl':
                VRToValue[curInst.getResVR()] = thisTable[2]
                print 'loadI ' + str(thisTable[2]) + " into " + str(curInst.getResVR())
            elif thisOpName == 'add' or thisOpName == 'sub' or thisOpName == 'mult' or thisOpName == 'lshift' or thisOpName == 'rshift':
                # If the registers used have known values, calc:
                valOneVR = VRToValue[curInst.getUsedVR1()]
                valOtherVR = VRToValue[curInst.getUsedVR2()]
                if valOneVR != -1 and valOtherVR != -1:
                    nameResVR = curInst.getResVR()
                    if thisOpName == 'add':
                        VRToValue[nameResVR] = valOneVR + valOtherVR
                        # TODO: general pattern of how to make these
                        opRes = valOneVR + valOtherVR
                        if opRes in ValueToVR.keys():
                            ValueToVR[opRes].append(nameResVR)
                        else:
                            ValueToVR[opRes] = [nameResVR]
                    if thisOpName == 'sub':
                        VRToValue[nameResVR] = valOneVR - valOtherVR
                    if thisOpName == 'mult':
                        VRToValue[nameResVR] = valOtherVR * valOneVR
                    if thisOpName == 'lshift':
                        VRToValue[nameResVR] = valOneVR << valOtherVR
                    if thisOpName == 'rshift':
                        VRToValue[nameResVR] = valOneVR >> valOtherVR
                    print thisOpName + " sets " + str(nameResVR) + " = " + str(VRToValue[nameResVR])

            curInst = curInst.getNext()



        # Build dependency graph
        no_successors, no_predecessors, instrOrdered = getDependencyGraph(IRInst1, VRToValue, ValueToVR)

        # give every node a rank, using a bfs from the lines w/ no successors
        setRanks(no_predecessors)

        #print "Found " + str(len(no_successors)) + " lines/nodes w/ no successors: "
        #for ns in no_successors:
        #    ns.print_layered(0)

        #print "Found " + str(len(no_predecessors)) + " lines w/ no predecessors: "
        #for np in no_predecessors:
        #    np.print_layered(0)

        fullSched = scheduleInstructions(no_predecessors)

        #print "Scheduling finished"

        for pair in fullSched:
            pairStr = "[" + instrOrdered[pair[0]] + "; " + instrOrdered[pair[1]] + "]"
            print pairStr

            #Perform actual register allocation
        #allocatePRS(inIRForm[0], 8, 4)
        #allocatePRS(IRInst1, maxVRNum + 1, numRegisters)
else:
    print "Malformed arguments: " + str(argv) + ", use 412alloc -h for help"

