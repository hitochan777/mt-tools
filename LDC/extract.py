#!/usr/bin/env python3

import sys
import fileinput
import re
import argparse

"""
    this script extracts words and word alignment simultaneously from the file where the format follows the files in this directory whose extension is 'wa'
"""

def process(buffer):
    if len(buffer)!=3:
        sys.exit("len(buffer) is not 3")
    if "rejected" in buffer[2]:
        return []
    fchars = buffer[0].rstrip().split()[1:] # remove the first word "zh:"
    ewords = buffer[1].rstrip().split()[1:] # remove the first word "en:"
    wa = buffer[2].rstrip().split()[1:] # remove the first word "wa:"
    fwords = []
    align = []
    infos = [] # infos = [([2,3,4],[2,3]),...]
    for a in wa:
        fa = a.split("-")[0]
        if fa == "":
            continue
        ea = a.split("-")[1]
        tmp = []
        for al in ea.split(","):
            if not al[0].isdigit():
                continue
            m = re.search(r"\D",al)
            if m != None:
                al = int(al[:m.start()])
            tmp.append(int(al))
        ea = tmp
        prev = -1
        li = []
        for f in fa.split(","):
            m = re.search(r"\D",f)
            if m != None:
                f = f[:m.start()]
            if prev != -1 and prev + 1 != int(f):
                infos.append((li,ea)) 
                li = [int(f)]
            else:
                li.append(int(f))
            prev = int(f)
        if len(li)>0:
            infos.append((li,ea))
    infos.sort()
    wpos = 0
    for info in infos: 
        fwords.append("".join(fchars[info[0][0]-1:info[0][-1]]))
        for a in info[1]:
            align.append((wpos,a-1))
        wpos += 1
    return (align, fwords, ewords)

def writeToFile(bundle, align, source, target):
    if len(bundle)==0:
        return 
    for a in bundle[0]:
        align.write("%d-%d " % (a[0],a[1]))
    align.write("\n")
    for w in bundle[1]:
        source.write(w+" ")
    source.write("\n")
    for w in bundle[2]:
        target.write(w+" ")
    target.write("\n")
    return 

if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="./extract.py")
    parser.add_argument("--align",required=True,help="output file for alignment")
    parser.add_argument("--source",required=True,help="output file for source language")
    parser.add_argument("--target",required=True,help="output file for target language")
    parser.add_argument("--input",required=True,help="input file")
    args = parser.parse_args()
    with open(args.align,"w") as a, open(args.source,"w") as s, open(args.target,"w") as t, open(args.input,"r") as i:
        buffer = []
        for line in i:
            if line.startswith("#") and len(buffer)==3:
                writeToFile(process(buffer),a,s,t)
                buffer = []
            elif not line.startswith("#"):
                buffer.append(line)
        if len(buffer)==3:
            writeToFile(process(buffer),a,s,t)
        
