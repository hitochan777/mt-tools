#!/usr/bin/env python3
import sys
import argparse
from bisect import *
from itertools import accumulate
from collections import defaultdict

def overwrite(sline, tline):
    cutIndices = [0]
    result = []
    cur = 0
    sraw = "".join(sline.split(" "))
    traw = "".join(tline.split(" "))

    assert len(sraw) == len(traw), "The numer of characters in source and target line are different!"

    for word in sline.split(" "):
        cur +=  len(word)
        cutIndices.append(cur)
        
    for i in range(1,len(cutIndices)):
        result.append(traw[cutIndices[i-1]:cutIndices[i]])

    return " ".join(result)
        
def containsAscii(s):
    try:
        for c in s:
            if ord(c) < 128:
                return True     
    except:
        return False

    return False

def findIndices(li, condition):
    return [index for index, elem in enumerate(li) if condition(elem)]


def recover(sline, tline):
    """
    Recover half width words segmentation of tline in sline
    """
    sline = overwrite(sline, tline)
    swords = sline.split(" ") 
    swords_tmp = [swords[0]]
    for index in range(1, len(swords)):
        if containsAscii(swords_tmp[-1][-1]) and containsAscii(swords[index][0]):
            swords_tmp.append(swords_tmp.pop() + swords[index])
        else:
            swords_tmp.append(swords[index]) 

    swords = swords_tmp
    twords = tline.split(" ")
    # print(swords)
    # print(twords)
    endList = list(accumulate(map(lambda x: len(x), swords)))
    twcnt = 0
    cutIndices = defaultdict(list)
    result = []
    for tp in range(len(twords)):
        if containsAscii(twords[tp]):
            index = bisect_left(endList, twcnt)
            if index > 0:
                cutIndices[index].append(twcnt - endList[index - 1])
            else:
                cutIndices[index].append(twcnt)

        twcnt += len(twords[tp])

    for index, token in enumerate(swords):
        if index in cutIndices: 
            start = 0
            for cutIndex in cutIndices[index]: # we know that cutIndices[index] is sorted from the beginning
                word = token[start:cutIndex]
                indices = findIndices(word, lambda x: not containsAscii(x)) # Actually indices will always be **singular list**
                if len(indices) == 0 or indices[0] == 0:
                    result.append(word)

                else:
                    result.append(word[0:indices[0]])
                    result.append(word[indices[0]:])
                    # print(result)

                start = cutIndex

            if start != len(token):
                word = token[start:]
                indices = findIndices(word, lambda x: not containsAscii(x)) # Actually indices will always be **singular list**
                if len(indices) == 0 or indices[0] == 0:
                    result.append(word)
                else:
                    result.append(word[:indices[0]])
                    result.append(word[indices[0]:])
        
        else:
            result.append(token)

    # print(result)
    return " ".join(result).strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Recover half width words segmentation of file2 in file1')
    parser.add_argument('source', type=str,  help='source file')
    parser.add_argument('target', type=str,  help='target file')
    args = parser.parse_args()
    
    with open(args.source, "r") as source, open(args.target, "r") as target:
        while True:
            sline = source.readline().strip()
            tline = target.readline().strip()
            if sline=="" or tline=="":
                 break

            print(recover(sline, tline))
