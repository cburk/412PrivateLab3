class GraphNode(object):
    '''
    Nodes for dependency graph
    '''


    def __init__(self, instrNum):
        self.instrNum = instrNum
        self.edgesIn = []
        self.edgesOut = []

    def addEdgesInAndOut(self, children):
        for child in children:
            self.edgesOut.append(child)
            child.addEdgesIn(self)

    def addEdgesIn(self, nodeFrom):
        self.edgesIn.append(nodeFrom)

    def justMeStr(self):
        return str(self.instrNum)

    def __str__(self):
        retStr = "(" + str(self.instrNum) + " : ["
        if len(self.edgesOut) == 0:
            retStr += "  "
        else:
            for child in self.edgesOut:
                retStr += child.__str__() + " , "
        retStr = retStr[:-2] + "])"
        return retStr

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
        if instr == 6:
            break
        instr += 1

        VRi = thisInstr.getResVR()
        VRj1 = thisInstr.getUsedVR1()
        VRj2 = thisInstr.getUsedVR2()

        opName = thisInstr.getOpName()

        print "Found instr: "
        print thisInstr.getVirtView()

        thisNode = GraphNode(VRi)
        M[VRi] = thisNode

        # No need to add edges
        # TODO: Shouldn't we eliminate nop, probs before here?
        if opName == 'nop' or opName == 'loadl':
            thisInstr = thisInstr.getNext()
            continue
        # Add edges, hard case.  Following slide 12 alg
        elif opName == 'load' or opName == 'store' or opName == 'output':
            nodesToConnectTo = []
            # Load and output need an edge to most recent store
            if opName == 'load' or opName == 'output':
                if mrStore != None:
                    nodesToConnectTo.append(mrStore)
                allLoadsAndOuts.append(thisNode)
            # If just load, remember it depends on first op's vr
            if opName == 'load':
                nodesToConnectTo.append(M[VRj1])
            # Output needs an edge to most recent output
            if opName == 'output':
                if mrOutput != None:
                    nodesToConnectTo.append(mrOutput)
                mrOutput = thisNode
            # Store needs an edge to most rec store, as well as all prev load and out
            if opName == 'store':
                if mrStore != None:
                    nodesToConnectTo.append(mrStore)
                mrStore = thisNode

                nodesToConnectTo += allLoadsAndOuts

                # store uses both of the op vr's
                nodesToConnectTo += [M[VRj1], M[VRj2]]

                print "Nodes we're connecting to: "
                pstr = "["
                for n in nodesToConnectTo:
                    pstr += n.justMeStr() + " "
                print pstr + "]"
                return 1

            thisNode.addEdgesInAndOut(nodesToConnectTo)

        # Arithop case, easy to add edges
        else:
            childNodes = [M[VRj1], M[VRj2]]
            thisNode.addEdgesInAndOut(childNodes)

        farthestNode = thisNode
        thisInstr = thisInstr.getNext()

    return farthestNode