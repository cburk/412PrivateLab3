from heapq import heappush, heappop

latencies = {"store":5, "load":5, "mult":3, "loadl":1, "add":1, "sub":1, "lshift":1, "rshift":1, "output":1}

# TODO: this plan doesn't give a very good output.  For example, if nothing in F1 queue but F0 queue head loses
# to a both, only both gets exec'd on F0 ( when it could be [F0head, bothhead]).  Think about it
# Pop 2 from fBoth, 1 from f1 and f2 each.  rank (could use queue((rank, nodePtr, queuePtr)), then activate
# remaining, return others to their queues
def bestFromEither(restrictedReadies0, restrictedReadies1, bothReadies, startCycle, thisCycle, Active):
    combQueue = []
    print "Picking bests"
    if(len(restrictedReadies0) != 0):
        print "rr 0choice 1: " + str(restrictedReadies0[0][2].instrIR.getVirtView())
        heappush(combQueue, heappop(restrictedReadies0))
    if(len(restrictedReadies1) != 0):
        print "rr1 choice 1: " + str(restrictedReadies1[0][2].instrIR.getVirtView())
        heappush(combQueue, heappop(restrictedReadies1))
    if(len(bothReadies) != 0):
        print "both choice 1: " + str(bothReadies[0][2].instrIR.getVirtView())
        heappush(combQueue, heappop(bothReadies))
    if(len(bothReadies) != 0):
        print "both choice 2: " + str(bothReadies[0][2].instrIR.getVirtView())
        heappush(combQueue, heappop(bothReadies))

    # Choose two to be active
    a1Nop = False
    if(len(combQueue) != 0):
        a1 = heappop(combQueue)
        startCycle[a1[2]] = thisCycle
        Active.append(a1[2])
    else:
        a1Nop = True
        a1 = "NOP"
    a2Nop = False
    if(len(combQueue) != 0):
        a2 = heappop(combQueue)
        startCycle[a2[2]] = thisCycle
        Active.append(a2[2])
    else:
        a2Nop = True
        a2 = "NOP"

    while len(combQueue) != 0:
        backOn = heappop(combQueue)
        oName = backOn[2].getInstrOp()
        if oName == 'mult':
            heappush(restrictedReadies1, backOn)
        elif oName == 'load' or oName == 'store':
            heappush(restrictedReadies0, backOn)
        else:
            heappush(bothReadies, backOn)

    # Put them in the correct order
    if a2Nop and a1Nop:
        return (a1,a2)
    if a2Nop:
        if a1[2].getInstrOp() == 'mult':
            return (a1,a2)
        return [a1,a2]
    if a2[2].getInstrOp() == 'mult':
        return (a1,a2)
    return (a1,a2)

"""
Slide 16 alg (from primer?), not textbook
"""
def scheduleInstructions(no_preds):
    Active = []

    readyHeapF1 = []
    readyHeapBoth = []
    readyHeapF0 = []

    # thought: three ready queues, one for possibles only in f0, one for
    # possibles only in f1, and 1 for all that could go in either.
    # get top from each, if equal break ties for those restricted to only
    # one functional unit
    for instr in no_preds:
        instr.notOnQueue = False
        if instr.getInstrOp() == "load" or instr.getInstrOp == "store":
            heappush(readyHeapF0, (instr.rank, 1, instr))
        elif instr.getInstrOp() == "mult":
            heappush(readyHeapF1, (instr.rank, 1, instr))
        else:
            heappush(readyHeapBoth, (instr.rank, 0, instr))


    startCycle = {}

    cycle = 1
    fullSchedule = []

    while(len(Active) != 0 or len(readyHeapBoth) != 0 or len(readyHeapF0) != 0 or len(readyHeapF1) != 0):
        # foreach functional unit, start executing the highest priority instr that's ready
        [thisCycleF0, thisCycleF1] = bestFromEither(readyHeapF0, readyHeapF1, readyHeapBoth, startCycle, cycle, Active)


        thisIter = []
        #print "Main Cycle Space: " + str(cycle)
        if thisCycleF0 != "NOP":
            #print "F0 new op: " + str(thisCycleF0) + ", instr#: " + str(thisCycleF0[2].instrNum)
            thisIter.append(thisCycleF0[2].instrNum)
        else:
            #print "F0 new op: NOP"
            thisIter.append(0)
        if thisCycleF1 != "NOP":
            #print "F1 new op: " + str(thisCycleF1) + ", instr#: " + str(thisCycleF1[2].instrNum)
            thisIter.append(thisCycleF1[2].instrNum)
        else:
            #print "F1 new op: NOP"
            thisIter.append(0)
        fullSchedule.append(thisIter)

        cycle += 1

        activesToRemove = []
        # check if this round made any new instructions ready
        for activeOp in Active:
            #print "Active op: " + str(activeOp.instrNum)
            #print str(latencies.get('loadl'))
            # if this op is done
            if startCycle.get(activeOp) + latencies.get(activeOp.getInstrOp()) <= cycle:
                #Active.remove(activeOp)
                activesToRemove.append(activeOp)

                for successorEdge in activeOp.getSuccessors():
                    #print "Found successor in cycle " + str(cycle)
                    #print successorEdge[0].instrNum
                    successorInstr = successorEdge[0]
                    # compare node pointer AND edge weight, b/c some might have weight=1 for serialization
                    successorInstr.notWaitingOn(activeOp, latencies.get(activeOp.getInstrOp()))
                    # If active's completion made any successors ready, note that
                    if len(successorInstr.getPredecessors()) == 0 and successorInstr.notOnQueue:
                        #print "Pushing instruction: " + str(successorInstr.instrNum)
                        successorInstr.notOnQueue = False
                        # choose which ready queue to put it in based on opName
                        succName = successorInstr.getInstrOp()
                        print "Succname: " + succName
                        # Change: pretty sure should be checking succName
                        #if succName == "load" or instr.getInstrOp() == "store":
                        if succName == "load" or succName == "store":
                            heappush(readyHeapF0, (successorInstr.rank, 1, successorInstr))
                        elif succName == "mult":
                            heappush(readyHeapF1, (successorInstr.rank, 1, successorInstr))
                        else:
                            print "bothpush B"
                            heappush(readyHeapBoth, (successorInstr.rank, 0, successorInstr))
                    else:
                        # TODO: For debugging, remove
                        #print "Num still waiting on: " + str(len(successorInstr.getPredecessors()))
                        a = 1 + 1

            # if other ops are waiting for this for serialization reasons
            elif (activeOp.getInstrOp() == 'load' or activeOp.getInstrOp() == 'store') and startCycle.get(activeOp) == cycle - 1:
                # Don't remove from active, b/c it'd still be running

                for successorEdge in activeOp.getSuccessors():
                    successorInstr = successorEdge[0]
                    # compare node pointer AND edge weight, b/c some might have weight=1 for serialization
                    successorInstr.notWaitingOn(activeOp, 1)
                    # If active's completion made any successors ready, note that
                    if len(successorInstr.getPredecessors()) == 0 and successorInstr.notOnQueue:
                        successorInstr.notOnQueue = False
                        # choose which ready queue to put it in based on opName
                        succName = successorInstr.getInstrOp()
                        print "Succname: " + str(succName)
                        if succName == "load" or succName == "store":
                            heappush(readyHeapF0, (successorInstr.rank, 1, successorInstr))
                        elif succName == "mult":
                            heappush(readyHeapF1, (successorInstr.rank, 1, successorInstr))
                        else:
                            print "bothpush A"
                            heappush(readyHeapBoth, (successorInstr.rank, 0, successorInstr))
        # update actives list w/ finished ones
        for act in activesToRemove:
            Active.remove(act)

    return fullSchedule

    # Thought: return value could prob just be startCycle, minimal intuition into which is which
    # alternatively, we could just create as we go along.  Start seems ok for now tho