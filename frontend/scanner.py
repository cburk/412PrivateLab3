'''
Created on Aug 24, 2016

@author: christianburkhartsmeyer
'''

#Grammatical categories
MEMOP= 0
LOADL= 1
ARITHOP= 2
OUTPUT= 3
NOP= 4
CONSTANT= 5
REGISTER= 6
COMMA= 7
INTO= 8
EOF = 9

grammaticalSymbols = ["MEMOP", "LOADL", "ARITHOP", "OUTPUT", "NOP", "CONSTANT", "REGISTER", "COMMA", "INTO"]

def openFile(fileName):
    return open(fileName, 'r')
    
def getNextToken(myFile):
    thisChar = 'asdf'
    while(thisChar):
        
        thisChar = myFile.read(1)
        if thisChar == ' ' or thisChar == '\n' or thisChar == '    ' or thisChar == '' or thisChar == '\t':
            #print "Found whitespace"
            continue
       
        #Otherwise, try to figure out what grammatical category;
        #printf("found char : %c", thisChar);
        

        #INTO path
        elif thisChar == '=':
            thisChar = myFile.read(1)
            if thisChar == '>':
                return [INTO, ''];
            else:
                print "Wrong symbol0"; return -1;
        #OUTPUT path
        elif thisChar == 'o':
            thisChar = myFile.read(1)
            if thisChar == 'u':
                thisChar = myFile.read(1)
                if thisChar == 't':
                    thisChar = myFile.read(1)
                    if thisChar == 'p':
                        thisChar = myFile.read(1)
                        if thisChar == 'u':
                            thisChar = myFile.read(1)
                            if thisChar == 't':
                                return [OUTPUT, 'output']
                            else:
                                print "Wrong symbol1"; return -1;
                        else:
                            print "Wrong symbol1"; return -1;
                    else:
                        print "Wrong symbol1"; return -1;
                else:
                    print "Wrong symbol1"; return -1;
            else:
                print "Wrong symbol1"; return -1;
        #NOP path
        elif thisChar == 'n':
            thisChar = myFile.read(1)
            if thisChar == 'o':
                thisChar = myFile.read(1)
                if thisChar == 'p':
                    return [NOP, 'nop']
                else:
                    print "Wrong symbol2"; return -1;
            else:
                print "Wrong symbol2"; return -1;
        #ADD path
        elif thisChar == 'a':
            thisChar = myFile.read(1)
            if thisChar == 'd':
                thisChar = myFile.read(1)
                if thisChar == 'd':
                    return [ARITHOP, 'add']
                else:
                    print "Wrong symbol3"; return -1;
            else:
                print "Wrong symbol3"; return -1;
        #MULT path
        elif thisChar == 'm':
            thisChar = myFile.read(1)
            if thisChar == 'u':
                thisChar = myFile.read(1)
                if thisChar == 'l':
                    thisChar = myFile.read(1)
                    if thisChar == 't':
                        return [ARITHOP, 'mult']
                    else:
                        print "Wrong symbol4"; return -1;
                else:
                    print "Wrong symbol4"; return -1;
            else:
                print "Wrong symbol4"; return -1;
        #RSHIFT/Register/Comma paths
        elif thisChar == 'r':
            thisChar = myFile.read(1)
            if thisChar == 's':
                thisChar = myFile.read(1)
                if thisChar == 'h':
                    thisChar = myFile.read(1)
                    if thisChar == 'i':
                        thisChar = myFile.read(1)
                        if thisChar == 'f':
                            thisChar = myFile.read(1)
                            if thisChar == 't':
                                return [ARITHOP, 'rshift']
                            else:
                                print "Wrong symbol5"; return -1;
                        else:
                            print "Wrong symbol5"; return -1;
                    else:
                        print "Wrong symbol5"; return -1;
                else:
                    print "Wrong symbol5"; return -1;
            #Register path
            elif ord(thisChar) >= 48 and ord(thisChar) <= 57:
                thisNum = int(thisChar)
                thisChar = myFile.read(1)
                while(ord(thisChar) >= 48 and ord(thisChar) <= 57):
                    thisNum = 10 * thisNum + int(thisChar)
                    thisChar = myFile.read(1)
                #print "Scanner found register: r" + str(thisNum)
                #print "Also found next char: " + thisChar
                #Hacky workaround,necessary b/c we've already read this char
                if thisChar == ',':
                    return [COMMA + REGISTER, thisNum]
                #Have to add this in case there's the => after a reg or constant grumble grumble
                if thisChar == '=':
                    thisChar = myFile.read(1)
                    if thisChar == '>':
                        return [REGISTER, thisNum, INTO]
                # If people use spaces like good coders
                return [REGISTER, thisNum]
            else:
                print "Wrong symbol5"; return -1;
                    
        #LOAD/LOADL paths
        elif thisChar == 'l':
            thisChar = myFile.read(1)
            if thisChar == 'o':
                thisChar = myFile.read(1)
                if thisChar == 'a':
                    thisChar = myFile.read(1)
                    if thisChar == 'd':
                        thisChar = myFile.read(1)
                        if thisChar == 'I':                            
                            return [LOADL, 'loadl']
                        else: #TODO: go back one byte or make sure it's valid?
                            return [MEMOP, 'load']
                    else:
                        print "Wrong symbol6"; return -1;
                else:
                    print "Wrong symbol6"; return -1;
            elif thisChar == 's':
                thisChar = myFile.read(1)
                if thisChar == 'h':
                    thisChar = myFile.read(1)
                    if thisChar == 'i':
                        thisChar = myFile.read(1)
                        if thisChar == 'f':
                            thisChar = myFile.read(1)
                            if thisChar == 't':
                                return [ARITHOP, 'lshift']
                            else:
                                print "Wrong symbol5"; return -1;
                        else:
                            print "Wrong symbol5"; return -1;
                    else:
                        print "Wrong symbol5"; return -1;
                else:
                    print "Wrong symbol5"; return -1;
            else:
                print "Wrong symbol6"; return -1;
            
        #STORE/SUB paths
        elif thisChar == 's':
            thisChar = myFile.read(1)
            if thisChar == 'u':
                thisChar = myFile.read(1)
                if thisChar == 'b':
                    return [ARITHOP, 'sub']
                else:
                    print "Wrong symbol7"; return -1;
            elif thisChar == 't':
                thisChar = myFile.read(1)
                if thisChar == 'o':
                    thisChar = myFile.read(1)
                    if thisChar == 'r':
                        thisChar = myFile.read(1)
                        if thisChar == 'e':
                            return [MEMOP, 'store']
                        else:
                            print "Wrong symbol7"; return -1;
                    else:
                        print "Wrong symbol7"; return -1;
                else:
                    print "Wrong symbol7"; return -1;
            else:
                print "Wrong symbol7"; return -1;
        #Constant path
        elif(len(thisChar) != 0 and ord(thisChar) >= 48 and ord(thisChar) <= 57):
            #print "Found char: " + thisChar + " w/ ord: " + str(ord(thisChar))
            thisNum = int(thisChar)
            thisChar = myFile.read(1)
            #print "Found char: " + thisChar + " w/ ord: " + str(ord(thisChar))
            while(len(thisChar) != 0 and ord(thisChar) >= 48 and ord(thisChar) <= 57):
                thisNum = 10 * thisNum + int(thisChar)
                thisChar = myFile.read(1)
            # In case peopel don't use spaces between const=>
            if thisChar == '=':
                thisChar = myFile.read(1)
                if thisChar == '>':
                    return [CONSTANT, thisNum, INTO] # Admittedly a queue would've been more elegant
            #print "Scanner found constant: " + str(thisNum)
            return [CONSTANT, thisNum]
        # Comma path
        elif thisChar == ',':
            return [COMMA, ',']
        #Comment path
        elif thisChar == '/':
            thisChar = myFile.read(1)
            if thisChar == '/':
                while thisChar != '\n':
                    thisChar = myFile.read(1)
            else:
                print "Unexpected character '/'"
        else:
            print "Unknown character: " + thisChar
            return -1
                                
    return [EOF, ""]
