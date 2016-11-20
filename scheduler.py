from heapq import heappush, heappop

latencies = {"store":5, "load":5, "mult":3, "loadl":1, "add":1, "sub":1, "lshift":1, "rshift":1, "output":1}

# TODO: this plan doesn't give a very good output.  For example, if nothing in F1 queue but F0 queue head loses
# to a both, only both gets exec'd on F0 ( when it could be [F0head, bothhead]).  Think about it
def bestFromEither(restrictedReadies, bothReadies, startCycle, thisCycle, Active):
    fault = 0
    if len(restrictedReadies) == 0:
        topFRestr = None
    else:
        topFRestr = heappop(restrictedReadies)
    if len(bothReadies) == 0:
        topBoth = None
    else:
        topBoth = heappop(bothReadies)

    # if both queues are empty, don't do anything, nothing active this round
    topBothNone = topBoth == None
    topFRestrNone = topFRestr == None
    if topFRestrNone and topBothNone:
        return None

    # Break ties in favor of constrained
    if topBothNone or (not topFRestrNone and topFRestr[1].rank >= topBoth[1].rank):
        startCycle[topFRestr[1]] = thisCycle
        Active.append(topFRestr[1])
        # we're not using the other one, have to push it
        if not topBothNone:
            heappush(bothReadies, topBoth)

        return topFRestr
    else:
        startCycle[topBoth[1]] = thisCycle
        Active.append(topBoth[1])
        # we're not using the other one, have to push it
        if not topFRestrNone:
            heappush(restrictedReadies, topFRestr)

        return topBoth


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
            heappush(readyHeapF0, (instr.rank, instr))
        elif instr.getInstrOp() == "mult":
            heappush(readyHeapF1, (instr.rank, instr))
        else:
            heappush(readyHeapBoth, (instr.rank, instr))


    startCycle = {}

    cycle = 1

    while(len(Active) != 0 or len(readyHeapBoth) != 0 or len(readyHeapF0) != 0 or len(readyHeapF1) != 0):
        # foreach functional unit, start executing the highest priority instr that's ready
        thisCycleF0 = bestFromEither(readyHeapF0, readyHeapBoth, startCycle, cycle, Active)
        thisCycleF1 = bestFromEither(readyHeapF1, readyHeapBoth, startCycle, cycle, Active)

        print "Main Cycle Space: " + str(cycle)
        if thisCycleF0 != None:
            print "F0 new op: " + str(thisCycleF0) + ", instr#: " + str(thisCycleF0[1].instrNum)
        if thisCycleF1 != None:
            print "F1 new op: " + str(thisCycleF1) + ", instr#: " + str(thisCycleF1[1].instrNum)

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
                        if succName == "load" or instr.getInstrOp() == "store":
                            heappush(readyHeapF0, (successorInstr.rank, successorInstr))
                        elif succName == "mult":
                            heappush(readyHeapF1, (successorInstr.rank, successorInstr))
                        else:
                            heappush(readyHeapBoth, (successorInstr.rank, successorInstr))
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
                        if succName == "load" or instr.getInstrOp() == "store":
                            heappush(readyHeapF0, (successorInstr.rank, successorInstr))
                        elif succName == "mult":
                            heappush(readyHeapF1, (successorInstr.rank, successorInstr))
                        else:
                            heappush(readyHeapBoth, (successorInstr.rank, successorInstr))
        # update actives list w/ finished ones
        for act in activesToRemove:
            Active.remove(act)

    # Thought: return value could prob just be startCycle, minimal intuition into which is which
    # alternatively, we could just create as we go along.  Start seems ok for now tho