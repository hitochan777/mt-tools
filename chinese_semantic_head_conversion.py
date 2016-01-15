#!/usr/bin/python

import sys
import re
import codecs

def main():
#Usage: python [ThisScript] [ModalList] (ID_OFFSET) < InputConllFile > OutputConllFile 

    sys.stdin = codecs.getreader('utf-8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    modalFilePath = sys.argv[1]
    try:
        idOffset = int(sys.argv[2])
    except:
        idOffset = 0
    stdin_buffer = sys.stdin.readlines()
    loadTreebank(modalFilePath, stdin_buffer, idOffset)

def flushBuffer(modalLineNum, wordEntry):
    for modalLine in modalLineNum:
        shiftHead(modalLine, wordEntry)
    for blocks in wordEntry:
        endCtr = 0
        for oneBlock in blocks:
            endCtr += 1
            sys.stdout.write(oneBlock)
            if endCtr < len(blocks):
                sys.stdout.write('\t')
        sys.stdout.write('\n')
    if len(wordEntry) > 0:
        sys.stdout.write('\n')
    del wordEntry[:]
    del modalLineNum[:]

def loadTreebank(modalFilePath, fileHandle, idOffset=0):

    modalFileHandle = codecs.open(modalFilePath, 'rU', 'utf-8')
    
    modalDict = {}
    wordEntry = []
    modalLineNum = []
    _id = idOffset

    for line in modalFileHandle:
        ll = line.rstrip()
        modalDict[ll] = 0

    for line in fileHandle:
        ll = line.rstrip()
        if ll.startswith('#'):
            flushBuffer(modalLineNum, wordEntry) 
            matchobj = re.match(r"#\s*(\d+\.?\d*)", ll, re.M)
            score = 0.0
            if matchobj:
                score = float(matchobj.group(1))
            sys.stdout.write("# ID=%d SCORE=%f\n" % (_id, score))
        elif line=="\n":
            _id += 1
        else:
            block = ll.split('\t')
            #if the word is a modal
            if block[1] in modalDict and block[3] == 'VV':
                modalLineNum.append(int(block[0]))
            wordEntry.append(block)
    flushBuffer(modalLineNum, wordEntry) # flush remaining contents

def shiftHead(modalLine, wordEntry):
    childList = []
    predicateIsFound = False

    for blocks in wordEntry:
        if int(blocks[0]) < modalLine:
            if int(blocks[6]) == modalLine:
                childList.append(int(blocks[0]))
        elif int(blocks[0]) == modalLine:
            head = int(blocks[6])
        else:
            if int(blocks[6]) == modalLine:
#                sys.stderr.write(blocks[3] + '\n')
                if not predicateIsFound and blocks[3] == 'VV':
                    predicateIsFound = True
                    predicateLine = int(blocks[0])
                else:
                    childList.append(int(blocks[0]))

    if predicateIsFound:
#        sys.stderr.write(wordEntry[modalLine - 1][1] + ' ' + wordEntry[modalLine - 1][3] + '\n')
        wordEntry[modalLine - 1][6] = str(predicateLine)
        for childLine in childList:
            wordEntry[childLine - 1][6] = str(predicateLine)
        wordEntry[predicateLine - 1][6] = str(head)



if __name__ == '__main__':
    main()
