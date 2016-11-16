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

    def getInstrOp(self):
        return self.instrOp

    def addEdgesInAndOut(self, children):
        for child in children:
            self.edgesOut.append(child)
            child[0].addEdgesIn(self)

    def addEdgesIn(self, nodeFrom):
        self.edgesIn.append(nodeFrom)

    def justMeStr(self):
        return str(self.instrNum)

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
        retStr += "(instr: " + str(self.instrNum) + " is " + self.instrOp + " which defines: " + str(self.regDefined) +": ["
        print retStr
        for child in self.edgesOut:
            print ("\t" * (ind + 1)) + "edge weight: " + str(child[1])
            child[0].print_layered(ind + 1)
        retStr = ""
        for i in range(ind):
            retStr += '\t'
        print retStr + "])"


def getDependencyGraph(firstNode):
    instr = 0
    thisInstr = firstNode
    # VR->nodes
    M = {}

    # All actual nodes
    mrStore = None # mr means most recent
    mrOutput = None
    allLoadsAndOuts = []
    farthestNode = None

    while thisInstr != None:
        instr += 1

        VRi = thisInstr.getResVR()
        VRj1 = thisInstr.getUsedVR1()
        VRj2 = thisInstr.getUsedVR2()

        opName = thisInstr.getOpName()

        print "Found instr: "
        print thisInstr.getVirtView()

        if opName == 'output' or opName == 'store' or opName == 'nop':
            thisNode = GraphNode(instr, opName, -1, thisInstr)
        else:
            thisNode = GraphNode(instr, opName, VRi, thisInstr)

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
                if mrStore != None:
                    nodesToConnectTo.append([mrStore, 5])
                allLoadsAndOuts.append(thisNode)
            # If just load, remember it depends on first op's vr
            if opName == 'load':
                nodesToConnectTo.append([M[VRj1], latencies.get(M[VRj1].getInstrOp())])
            # Output needs an edge to most recent output
            if opName == 'output':
                if mrOutput != None:
                    # TODO: If outputs come out mangled, probs need t oset this to 5
                    nodesToConnectTo.append([mrOutput, 1])
                mrOutput = thisNode
            # Store needs an edge to most rec store, as well as all prev load and out
            if opName == 'store':
                if mrStore != None:
                    nodesToConnectTo.append([mrStore, 1])
                mrStore = thisNode

                #nodesToConnectTo += allLoadsAndOuts
                for loadOrOut in allLoadsAndOuts:
                    nodesToConnectTo.append([loadOrOut, 1])

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
            print "Op: " + opName
            #childNodes = [M[VRj1], M[VRj2]]
            #thisNode.addEdgesInAndOut(childNodes)
            thisNode.addEdgesInAndOut([[M[VRj1], latencies.get(M[VRj1].getInstrOp())]])
            thisNode.addEdgesInAndOut([[M[VRj2], latencies.get(M[VRj2].getInstrOp())]])

        # Have to do this at the end in case VRi is used to calc this op
        M[VRi] = thisNode

        farthestNode = thisNode
        thisInstr = thisInstr.getNext()

    return farthestNode

# Gameplan: second pass, give edges a weight (delay(op))
#   possible now b/c we

# Wait no, instructions are read 1->7, so we should always be able to tell what defined what
# Edge weights can be added here as we did in the notes version, just use
# latencies.get(M[VRj...].getOpName())

# probably switch the direction of edges like john suggested

# afterwards, can implement scheduling alg, b/c we have delay(op), and all the things
# an op is waiting on, and can easily (i think?) find the leaves
