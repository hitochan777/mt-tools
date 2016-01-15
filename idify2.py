#!/usr/bin/env python3

import fileinput
import sys

nbestList = []
delimiter = "\t"

with open(sys.argv[1],"r") as f:
    cnt = 1
    for line in f:
        if not line.strip():
            nbestList.append(cnt)
            cnt+=1 
        else:
            splitted = line.split(delimiter, 1)[0]
            if len(splitted) == 1: # when score is not present
                score = 0.0 # some random score
                parse = splitted[0]
            elif len(splitted) == 2:
                score = splitted[0]
                parse = splitted[1] 

            line = "; "+str(cnt)+"\t"+score+"\n"+parse
        if len(sys.argv) >= 3 and int(sys.argv[2]) == 1 :
            cnt += 1

        print(line)
