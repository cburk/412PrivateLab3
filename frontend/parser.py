from scanner import getNextToken, openFile
from IR import IRLink
'''
Created on Aug 29, 2016

@author: christianburkhartsmeyer
'''
# Symbol codes
ERROR = -1
MEMOP= 0
LOADL= 1
ARITHOP= 2
OUTPUT= 3
NOP= 4 #
CONSTANT= 5
REGISTER= 6
COMMA= 7
INTO= 8
EOF = 9
# For crearting the ir
TOKENSTHISLINE = 0
lineNumber = 0
maxSrcNum = 0


grammaticalSymbols = ["MEMOP", "LOADL", "ARITHOP", "OUTPUT", "NOP", "CONSTANT", "REGISTER", "COMMA", "INTO", "EOF"]

"""
returns false if syntax invalid, true if this line is valid so far, the actual line if it's done
"""
def checkSyntax(thisToken, tokenValue):
    global TOKENSTHISLINE
    global thisLine
    global firstToken
    global maxSrcNum
    
    # Set up a new linked list element if the previous 
    if TOKENSTHISLINE == 0:
        thisLine = IRLink(tokenValue)

    """        
    if thisToken != REGISTER + COMMA:
        ###print "this token: " + grammaticalSymbols[thisToken]
        ###print "Num tokens: " + str(TOKENSTHISLINE)
    """
    if TOKENSTHISLINE == 0:
        if thisToken == CONSTANT or thisToken == REGISTER or thisToken == COMMA or thisToken == INTO:
            return False
        if thisToken == NOP:
            TOKENSTHISLINE = 0
            return thisLine
        firstToken = thisToken
        TOKENSTHISLINE = 1
        return True
    elif TOKENSTHISLINE == 1:
        # 2 token lines
        if firstToken == OUTPUT and thisToken == CONSTANT:
            # Save as ir
            TOKENSTHISLINE = 0
            thisLine.getTable()[2] = tokenValue
            return thisLine
        # 4 token lines
        if firstToken == LOADL and thisToken == CONSTANT:
            TOKENSTHISLINE = 2
            thisLine.getTable()[2] = tokenValue
            return True
        if firstToken == MEMOP and thisToken == REGISTER:
            TOKENSTHISLINE = 2
            if tokenValue > maxSrcNum:
                maxSrcNum = tokenValue
            thisLine.getTable()[2] = tokenValue
            return True
        if firstToken == ARITHOP and thisToken == REGISTER + COMMA:
            TOKENSTHISLINE = 3
            if tokenValue > maxSrcNum:
                maxSrcNum = tokenValue
            thisLine.getTable()[2] = tokenValue
            return True
        # 6 token lines
        if firstToken == ARITHOP and thisToken == REGISTER:
            TOKENSTHISLINE = 2
            if tokenValue > maxSrcNum:
                maxSrcNum = tokenValue
            thisLine.getTable()[2] = tokenValue
            return True
        return False
    elif TOKENSTHISLINE == 2:
        ###print "First token: " + grammaticalSymbols[firstToken]
        if (firstToken == MEMOP or firstToken == LOADL) and thisToken == INTO:
            TOKENSTHISLINE = 3
            return True
        elif thisToken == COMMA:
            TOKENSTHISLINE = 3
            return True
        return False
    elif TOKENSTHISLINE == 3:
        if (firstToken == MEMOP or firstToken == LOADL) and thisToken == REGISTER:
            TOKENSTHISLINE = 0
            if tokenValue > maxSrcNum:
                maxSrcNum = tokenValue
            #If it's load, we don't want to kill OP3, so put it in OP2
            if thisLine.getTable()[1] == "store":
                thisLine.getTable()[6] = tokenValue
            else:
                thisLine.getTable()[10] = tokenValue
            return thisLine
        #Otherwise, make sure it's middle register for arithop
        elif thisToken == REGISTER:
            TOKENSTHISLINE += 1
            if tokenValue > maxSrcNum:
                maxSrcNum = tokenValue
            thisLine.getTable()[6] = tokenValue
            return True
        return False
    elif TOKENSTHISLINE == 4:
        if thisToken == INTO:
            TOKENSTHISLINE += 1
            return True
        return False
    else:
        if thisToken == REGISTER:
            TOKENSTHISLINE = 0
            if tokenValue > maxSrcNum:
                maxSrcNum = tokenValue
            thisLine.getTable()[10] = tokenValue
            return thisLine
        return False
    
"""
Returns ERROR if the file has invalid syntax or an invalid next token,
intermediate value otherwise
"""
def parseFile(filename):
    gottenFirstLine = False
    lastLine = None
    ##print "Tokens this line: " + str(TOKENSTHISLINE)
    myFile = openFile(filename)
    numInsts = 0
    thisToken = MEMOP
    while thisToken != EOF:
        pair = getNextToken(myFile)
        if thisToken == EOF:
            break
        thisToken = pair[0]
        thisValue = pair[1]
        

        # Best token printing b/c reg + comma hack breaks
        """
        if thisToken != REGISTER + COMMA:
            print "Down here, got token: " + grammaticalSymbols[thisToken]
        else:
            print "Comma + register"
        if thisToken == ERROR:
            return ERROR
        """
        
        # Just pass the integer
        result = checkSyntax(thisToken, thisValue)
        if result == False:
            #print "Error, invalid syntax"
            return ERROR
        # If we got back the actual linked list node, i.e. the ir
        if result != True:
            numInsts += 1
            if gottenFirstLine != True:
                gottenFirstLine = True
                firstLine = result
            else:
                lastLine.setNext(result)
            result.setPrev(lastLine)
            lastLine = result
        #elif we're in the middle of the instruction, and there was an => after our last char w/ no spaces
        elif len(pair) == 3:
            checkSyntax(pair[2], -1)
            if result == False:
                return ERROR
        
    
    ##print lastLine.getPrev() == None
     
    #return [firstLine, lastLine, numInsts, numInsts + 3]
    #Above is incorrect, actually needs to return maxSrc
    return [firstLine, lastLine, numInsts, maxSrcNum]
        