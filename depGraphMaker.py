latencies = {"store":5, "load":5, "mult":3, "loadl":1, "add":1, "sub":1, "lshift":1, "rshift":1, "output":1}

class GraphNode(object):
    '''
    Nodes for dependency graph
    '''


    def __init__(self, instrNum, instrOp, regDefined, instrIR):
        self.instrNum = instrNum
        self.instrOp = instrOp
        self.regDefined = regDefined;
        self.instrIR = instrIR; # Just so we know what's being defined, etc.
        self.edgesIn = []
        self.edgesOut = []
        # As per John's answer to Implementing a priority function
        self.rank = latencies[instrOp]
        self.rankCalculated = False
        # Keep this instr from getting set twice
        self.notOnQueue = True
        self.startInstr = -1 # Right now, only for stores

    def notWaitingOn(self, op, timePassed):
        removingInd = -1
        ind = 0
        # TODO: Probably have to test equality here pretty thoroughly
        for predEdge in self.edgesOut:
            if predEdge[0]== op and predEdge[1] == timePassed:
                removingInd = ind
                break
            ind += 1
        if removingInd != -1:
            del self.edgesOut[removingInd]

    def getInstrOp(self):
        return self.instrOp

    def addEdgesInAndOut(self, children):
        for child in children:
            self.edgesOut.append(child)
            child[0].addEdgesIn([self, child[1]])

    def addEdgesIn(self, nodeFrom):
        self.edgesIn.append(nodeFrom)

    def justMeStr(self):
        return str(self.instrNum)

    def getSuccessors(self):
        return self.edgesIn
    def getPredecessors(self):
        return self.edgesOut

    def __str__(self):
        retStr = "(" + str(self.instrNum) + " : \n["
        if len(self.edgesOut) == 0:
            retStr += "  "
        else:
            for child in self.edgesOut:
                retStr += child.__str__() + " , "
        retStr = retStr[:-2] + "])"
        return retStr

    def print_layered(self, ind):
        retStr = ""
        for i in range(ind):
            retStr += '\t'
        retStr += "(instr: " + str(self.instrNum) + " is " + self.instrOp + " which defines: " + str(self.regDefined) + " Rank<" + str(self.rank) + ">: ["
        print retStr
        for child in self.edgesOut:
            print ("\t" * (ind + 1)) + "edge weight: " + str(child[1])
            child[0].print_layered(ind + 1)
        retStr = ""
        for i in range(ind):
            retStr += '\t'
        print retStr + "])"


def getDependencyGraph(firstNode, VRToValue, ValueToVR):
    instr = 0
    thisInstr = firstNode
    # VR->nodes
    M = {}

    # All actual nodes
    mrStores = [] # mr means most recent
    mrOutput = None
    allLoadsAndOuts = []
    farthestNode = None
    allNodes = []

    instrOrdered = ["nop"]

    while thisInstr != None:
        instr += 1

        VRi = thisInstr.getResVR()
        VRj1 = thisInstr.getUsedVR1()
        VRj2 = thisInstr.getUsedVR2()

        opName = thisInstr.getOpName()

        #print "Found instr: "
        #print thisInstr.getVirtView()
        instrOrdered.append(thisInstr.getVirtView())

        if opName == 'output' or opName == 'store' or opName == 'nop':
            thisNode = GraphNode(instr, opName, -1, thisInstr)
        else:
            thisNode = GraphNode(instr, opName, VRi, thisInstr)
        allNodes.append(thisNode)

        thisNode.startInstr = instr

        # No need to add edges
        # TODO: Shouldn't we eliminate nop, probs before here?
        if opName == 'nop' or opName == 'loadl':
            # do nothing
            a = 1
        # Add edges, hard case.  Following slide 12 alg
        elif opName == 'load' or opName == 'store' or opName == 'output':
            nodesToConnectTo = []
            # Load and output need an edge to most recent store
            if opName == 'load' or opName == 'output':
                #if mrStore != None:
                # Probably need to check the last few stores, or all stores still live
                if opName == 'load':
                    for mrStore in mrStores:
                        lastStoreAt = VRToValue[mrStore.instrIR.getTable()[7]]
                        if lastStoreAt == VRToValue[VRj1] or lastStoreAt == -1:
                            nodesToConnectTo.append([mrStore, 5])
                #Similar for output
                else:
                    print "Setting store edges for outputs"
                    for mrStore in mrStores:
                        lastStoreAt = VRToValue[mrStore.instrIR.getTable()[7]]
                        if lastStoreAt == thisInstr.getUsedConst1() or lastStoreAt == -1:
                            print "Needed to add edge b/c store to " + str(thisInstr.getUsedConst1()) + " = " + str(lastStoreAt) + " (vr" + str(mrStore.instrIR.getTable()[7]) + ")"
                            nodesToConnectTo.append([mrStore, 5])
                allLoadsAndOuts.append(thisNode)
            # If just load, remember it depends on first op's vr
            if opName == 'load':
                nodesToConnectTo.append([M[VRj1], latencies.get(M[VRj1].getInstrOp())])
            # Output needs an edge to most recent output
            if opName == 'output':
                if mrOutput != None:
                    nodesToConnectTo.append([mrOutput, 1])
                mrOutput = thisNode
            # Store needs an edge to most rec store, as well as all prev load and out
            if opName == 'store':
                #if len(mrStores) != 0:
                #    nodesToConnectTo.append([mrStores[-1], 1])
                # TODO: May be necessary to say if lastStore == <our value> or lastStore = -1, b/c then it could be anything
                for mrStore in mrStores:
                    lastStoreAt = VRToValue[mrStore.instrIR.getTable()[7]]
                    if lastStoreAt == VRToValue[VRj2] or lastStoreAt == -1:
                        print "Storing to same store (" + str(lastStoreAt) + ")"
                        print "Edge required for instr: " + thisInstr.getVirtView()
                        nodesToConnectTo.append([mrStore, 1])


                #mrStore = thisNode
                mrStores.append(thisNode)

                #nodesToConnectTo += allLoadsAndOuts
                for loadOrOut in allLoadsAndOuts:
                    nodesToConnectTo.append([loadOrOut, 1])

                """
                Should be trimming, seems to make worse/incorrect
                """

                # store uses both of the op vr's
                #nodesToConnectTo += [M[VRj1], M[VRj2]]
                nodesToConnectTo.append([M[VRj1], latencies.get(M[VRj1].getInstrOp())])
                nodesToConnectTo.append([M[VRj2], latencies.get(M[VRj2].getInstrOp())])

                #print "Nodes we're connecting to: "
                #pstr = "["
                #for n in nodesToConnectTo:
                #    pstr += n.justMeStr() + " "
                #print pstr + "]"

            thisNode.addEdgesInAndOut(nodesToConnectTo)

        # Arithop case, easy to add edges
        else:
            #print "Op: " + opName
            #childNodes = [M[VRj1], M[VRj2]]
            #thisNode.addEdgesInAndOut(childNodes)
            thisNode.addEdgesInAndOut([[M[VRj1], latencies.get(M[VRj1].getInstrOp())]])
            thisNode.addEdgesInAndOut([[M[VRj2], latencies.get(M[VRj2].getInstrOp())]])

        # Have to do this at the end in case VRi is used to calc this op
        # Q: What if no VRi?
        if opName != "store" and opName != "nop" and opName != "output":
            M[VRi] = thisNode

        # Trim MRStores if they're done executing
        # Todo: Thought: don't actually use this instr#, b/c it's not necessarily when it'll be scheduled
        #for mrStore in mrStores:
        #    if mrStore.startInstr <= instr - 5:
        #        mrStores.remove(mrStore)

        farthestNode = thisNode
        thisInstr = thisInstr.getNext()

    #return farthestNode
    # Now, make a pass over instructions, collect those w/ no successors
    noSuccs = []
    noPreds = []
    for line in allNodes:
        if len(line.getSuccessors()) == 0:
            noSuccs.append(line)
        if len(line.getPredecessors()) == 0:
            noPreds.append(line)

    return noSuccs, noPreds, instrOrdered

# Gameplan: second pass, give edges a weight (delay(op))
#   possible now b/c we

# Wait no, instructions are read 1->7, so we should always be able to tell what defined what
# Edge weights can be added here as we did in the notes version, just use
# latencies.get(M[VRj...].getOpName())

# probably switch the direction of edges like john suggested

# afterwards, can implement scheduling alg, b/c we have delay(op), and all the things
# an op is waiting on, and can easily (i think?) find the leaves

# Starting w/ the nodes w/ no predecessors, set rank(node)=
# "own latency to the max rank among its successors", using a dfs to calculate
# its successors ranks
def setRanks(thisLayerNodes):
    for line in thisLayerNodes:
        # keeps us from recalculating ranks
        if line.rankCalculated:
            continue

        succs = line.getSuccessors()
        # base case, rank is just it's latency, or original rank
        if len(succs) == 0:
            line.rankCalculated = True
            continue
        # otherwise, rank is max amongst its successors
        # TODO: This might calculate the rank of a node many times over, is this avoidable?
        # Thought is we could set a flag, but even then that doesn't seem very efficient
        # May be worth revisiting

        # also nodes passed in, successors are edges
        succsNodes = []
        for edge in succs:
            succsNodes.append(edge[0])
        #setRanks(succs)
        setRanks(succsNodes)

        maxRank = -1
        maxLine = None
        #for succ in succs:
        for succ in succsNodes:
            if succ.rank > maxRank:
                maxRank = succ.rank

        line.rank += maxRank
        line.rankCalculated = True