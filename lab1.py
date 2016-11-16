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

#print "Hello world!"

if len(argv) == 3:
    #Check 1
    if argv[1] == "-x":
        #print "No register allocation, filename: " + argv[2]
        firstLast = parseFile(argv[2])
        IRInst1 = firstLast[0]
        IRInstFinal = firstLast[1]
        numLines = firstLast[2]
        maxVRNum = firstLast[3]
        # Traverse over links in IR, comment out
        """
        curInst = IRInst1
        while(curInst != None):
            print curInst
            curInst = curInst.getNext()
        """
            
        #Renaming, live ranges
        renameVirtRegisters(IRInst1, IRInstFinal, numLines, maxVRNum)
        #print "Returned from renaming successfully"
        curInst = IRInst1
        while(curInst != None):
            #print curInst
            curInst = curInst.getNext()
        
        
    #Check 2    
    elif ord(argv[1][0]) >= 48 and ord(argv[1][0]) <= 57:
        numRegisters = int(argv[1])
        if numRegisters > 64 or numRegisters < 3:
            print "Invalid k value (number of registers), found: " + str(numRegisters)
        #print "Actual register allocation, filename: " + argv[2] + ", num registers: " + str(numRegisters)
        
        # Scan and parse file, front end
        firstLast = parseFile(argv[2])
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

        #Set up example from slides
        """
        myIR = [[None,'loadl',128,0,0,float('inf'),0,0,0,0,0,1,0,1,None],
                [None,'load',0,1,0,8, 0,0,0,0, 0,2,0,7,None],
                [None,'loadl',132,0,0,float('inf'),0,0,0,0,0,7,0,3,None],
                [None,'load',0,7,0,float('inf'),0,0,0,0, 0,4,0,6,None],
                [None,'loadl',136,0,0,float('inf'),0,0,0,0,0,6,0,5,None],
                [None,'load',0,6,0,float('inf'),0,0,0,0, 0,5,0,6,None],
                [None,'mult',0,4,0,float('inf'),0,5,0,float('inf'),0,3,0,7,None],
                [None,'add',0,2,0,float('inf'),0,3,0,float('inf'),0,0,0,8,None],
                [None,'store',0,0,0,float('inf'),0,1,0,float('inf'),0,0,0,0,None],]
        
        inIRForm = []
        prev = None
        i = 0
        for table in myIR:
            this = IRLink(table, True)
            this.setPrev(prev)
            if i > 0:
                prev.setNext(this)
            prev = this
            inIRForm.append(this)
            i += 1
        """
        
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

           
        #Perform actual register allocation 
        #allocatePRS(inIRForm[0], 8, 4)
        allocatePRS(IRInst1, maxVRNum + 1, numRegisters)
            
        #print "\n\nEnd allocation, printing new instr set:\n"
        
        #curInst = inIRForm[0]
        curInst = IRInst1
        while(curInst != None):
            print curInst
            curInst = curInst.getNext()
        """
        for newIR in inIRForm:
            print newIR
        """

        
if len(argv) == 2:
    if argv[1] == '-h':
        print """412alloc Help:\nOptions:\n
        412alloc -h    : used to display this help screen
        412alloc -x <filename>    : performs renaming on the iloc block in filename,\nas per code check 1.  Returns an iloc block w/ virtual registers.\nDoes not handle any arguments after -x
        412alloc k <filename>    : performs register allocation w/ k physical registers on the iloc block specified by filename.\nK must be >=3 and <= 64
                   """
    else:
        print "yeah boiiii"
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
        no_successors, no_predecessors = getDependencyGraph(IRInst1)

        # give every node a rank, using a bfs from the lines w/ no successors
        setRanks(no_predecessors)

        print "Found " + str(len(no_successors)) + " lines/nodes w/ no successors: "
        for ns in no_successors:
            ns.print_layered(0)


            #Perform actual register allocation
        #allocatePRS(inIRForm[0], 8, 4)
        #allocatePRS(IRInst1, maxVRNum + 1, numRegisters)



else:
    print "Malformed arguments: " + str(argv) + ", use 412alloc -h for help"

