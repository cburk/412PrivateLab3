'''
Created on Aug 30, 2016

@author: christianburkhartsmeyer
'''
from sys import argv
from frontend.parser import parseFile
from backend.virtualizer import renameVirtRegisters
from IR import IRLink
from backend.allocator import allocatePRS

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
        """
        Theirs:
loadI 0        => r0    //  => vr30  <remat>
    loadI 4        => r1    //  => vr22  <remat>
    load r0        => r2    // vr30 => vr18
    add r0, r1    => r0    // vr30, vr22 => vr29
    load r0        => r3    // vr29 => vr19
    add r0, r1    => r0    // vr29, vr22 => vr28
    loadI 32768    => r4    // spilling pr3 (vr19)
    store r3    => r4    // spilling pr3 (vr19)
    load r0        => r3    // vr28 => vr16
    add r0, r1    => r0    // vr28, vr22 => vr27
    loadI 32772    => r4    // spilling pr3 (vr16)
    store r3    => r4    // spilling pr3 (vr16)
    load r0        => r3    // vr27 => vr17
    add r0, r1    => r0    // vr27, vr22 => vr26
    loadI 32776    => r4    // spilling pr3 (vr17)
    store r3    => r4    // spilling pr3 (vr17)
    load r0        => r3    // vr26 => vr14
    add r0, r1    => r0    // vr26, vr22 => vr25
    #Checkpoint 1, seems fine up to here
    loadI 32780    => r4    // spilling pr3 (vr14)
    store r3    => r4    // spilling pr3 (vr14)
    load r0        => r3    // vr25 => vr15
    add r0, r1    => r0    // vr25, vr22 => vr24
    loadI 32784    => r4    // spilling pr3 (vr15)
    store r3    => r4    // spilling pr3 (vr15)
    load r0        => r3    // vr24 => vr12
    add r0, r1    => r0    // vr24, vr22 => vr23
    loadI 32788    => r4    // spilling pr3 (vr12)
    store r3    => r4    // spilling pr3 (vr12)
    load r0        => r3    // vr23 => vr13
    add r0, r1    => r0    // vr23, vr22 => vr21
    //Check 2
    load r0        => r1    // vr21 => vr10
    loadI 32792    => r4    // spilling pr1 (vr10)
    store r1    => r4    // spilling pr1 (vr10)
    loadI 4        => r1    // rematerialized
    add r0, r1    => r0    // vr21, vr22 => vr20
    load r0        => r0    // vr20 => vr11
    loadI 32768    => r1    // restoring vr19 => pr1
    load r1        => r1    // restoring vr19 => pr1
    add r2, r1    => r2    // vr18, vr19 => vr8
    loadI 32772    => r1    // restoring vr16 => pr1
    load r1        => r1    // restoring vr16 => pr1
    loadI 32796    => r4    // spilling pr2 (vr8)
    store r2    => r4    // spilling pr2 (vr8)
    loadI 32776    => r2    // restoring vr17 => pr2
    load r2        => r2    // restoring vr17 => pr2
    add r1, r2    => r1    // vr16, vr17 => vr9
    loadI 32780    => r2    // restoring vr14 => pr2
    load r2        => r2    // restoring vr14 => pr2
    loadI 32800    => r4    // spilling pr1 (vr9)
    store r1    => r4    // spilling pr1 (vr9)
    loadI 32784    => r1    // restoring vr15 => pr1
    load r1        => r1    // restoring vr15 => pr1
    add r2, r1    => r2    // vr14, vr15 => vr6
    loadI 32788    => r1    // restoring vr12 => pr1
    load r1        => r1    // restoring vr12 => pr1
    add r1, r3    => r1    // vr12, vr13 => vr7
    loadI 32792    => r3    // restoring vr10 => pr3
    load r3        => r3    // restoring vr10 => pr3
    add r3, r0    => r3    // vr10, vr11 => vr5
    loadI 32796    => r0    // restoring vr8 => pr0
    load r0        => r0    // restoring vr8 => pr0
    loadI 32804    => r4    // spilling pr3 (vr5)
    store r3    => r4    // spilling pr3 (vr5)
    loadI 32800    => r3    // restoring vr9 => pr3
    load r3        => r3    // restoring vr9 => pr3
    add r0, r3    => r0    // vr8, vr9 => vr4
    add r2, r1    => r2    // vr6, vr7 => vr3
    loadI 32804    => r1    // restoring vr5 => pr1
    load r1        => r1    // restoring vr5 => pr1
    add r0, r1    => r0    // vr4, vr5 => vr2
    add r0, r2    => r0    // vr2, vr3 => vr1
    loadI 0        => r1    //  => vr0  <remat>
    store r0    => r1    // vr1 => vr0
    output 0        // 

//

OURS:
    

        
        """
        
        
elif len(argv) == 2 and argv[1] == '-h':
    print """412alloc Help:\nOptions:\n
    412alloc -h    : used to display this help screen
    412alloc -x <filename>    : performs renaming on the iloc block in filename,\nas per code check 1.  Returns an iloc block w/ virtual registers.\nDoes not handle any arguments after -x
    412alloc k <filename>    : performs register allocation w/ k physical registers on the iloc block specified by filename.\nK must be >=3 and <= 64
               """
else:
    print "Malformed arguments: " + str(argv) + ", use 412alloc -h for help"