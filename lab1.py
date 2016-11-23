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

        #print "After renaming:"
        curInst = IRInst1
        while(curInst != None):
            thisTable = curInst.getTable()
            #print "This table: " + str(thisTable)
            curInst = curInst.getNext()
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

        # Build dependency graph
        no_successors, no_predecessors, instrOrdered = getDependencyGraph(IRInst1)

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

