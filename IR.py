'''
Created on Aug 30, 2016

@author: christianburkhartsmeyer
'''

class IRLink(object):
    '''
    Linked list nodes
    '''
    

    def __init__(self, firstCmd, isTable = None):
        if isTable:
            self.table = firstCmd
        else:
            self.table = [None,firstCmd,0,0,0,float('inf'),0,0,0,float('inf'),0,0,0,float('inf'),None]

    #Pretty printing for final form
    #TODO: possible optimization, hashtable strings to ints for matching?
    #TODO: RN pulling ops from SR, for lab1 needs to be VR, for lab2 PR
    #NOTE: for constants, vr and pr never modified, just look at cr for value
    def __str__(self):
        table = self.table
        opName = table[1]
        retStr = opName
        if opName == "nop":
            return retStr
        if opName==("output"):
            return retStr + "\t" + str(table[2])
        elif opName == "loadl":
            return "loadI" + "\t" + str(table[2]) + "\t=>\tr" + str(table[12])
        elif opName == "load":
            return retStr + "\tr" +str(table[4]) + "\t=>\tr" + str(table[12])
        elif opName == "store":
            return retStr + "\tr" +str(table[4]) + "\t=>\tr" + str(table[8])
        #arithop
        else:
            return retStr + "\tr" +str(table[4]) + ",r" + str(table[8]) + "\t=>\tr" + str(table[12])
        
    def getVirtView(self):
        table = self.table
        opName = table[1]
        retStr = opName
        if opName == "nop":
            return retStr
        if opName==("output"):
            return retStr + "\t" + str(table[2])
        elif opName == "loadl":
            return "loadI" + "\t" + str(table[2]) + "\t=>\tr" + str(table[11])
        elif opName == "load":
            return retStr + "\tr" +str(table[3]) + "\t=>\tr" + str(table[11])
        elif opName == "store":
            return retStr + "\tr" +str(table[3]) + "\t=>\tr" + str(table[7])
        #arithop
        else:
            return retStr + "\tr" +str(table[3]) + ",r" + str(table[7]) + "\t=>\tr" + str(table[11])
        
    def getPrev(self):
        return self.table[0]
    def getNext(self):
        return self.table[-1]
    def getTable(self):
        return self.table
    def setNext(self, a):
        self.table[-1] = a
    def setPrev(self, a):
        self.table[0] = a
    