#!/usr/bin/env python3

import sys
import fileinput
import re
import argparse

"""
"""

def process(buffer):
    if len(buffer)!=3:
        sys.exit("len(buffer) is not 3")
    if "rejected" in buffer[2]:
        return None
    flen = len(buffer[0].rstrip().split()[1:]) # remove the first word "zh:"
    tags = [None]*flen
    wa = buffer[2].rstrip().split()[1:] # remove the first word "wa:"
    cnt = 0
    for a in wa:
        fa = a.split("-")[0]
        if fa == "":
            continue
        linkTag = re.search(r"\((.*)\)", a).groups()[0]
        li = []
        for f in fa.split(","):
            m = re.search(r"\[(\D*)\]",f)
            wordTag = "TRA" # TRA means a direct translation
            if m is not None:
                f = f[:m.start()]
                wordTag = m.groups()[0]

            if tags[int(f) - 1] is not None:
                raise RuntimeError('a source word is assigned tags twice!')
                sys.exit(1)

            tags[int(f) - 1] = "%s:%s" % (linkTag, wordTag) 
            cnt += 1

    if cnt != flen:
        raise RuntimeError('There are some indices which are not assigned link tags!')
        sys.exit(1)
            
    return " ".join(tags)

if __name__=="__main__":
    buffer = []
    for line in fileinput.input():
        if line.startswith("#") and len(buffer)==3:
            result = process(buffer)
            if result is not None:
                print(result)
 
            buffer = []
        elif not line.startswith("#"):
            buffer.append(line)
 
    if len(buffer)==3:
        if result is not None:
            print(result)
