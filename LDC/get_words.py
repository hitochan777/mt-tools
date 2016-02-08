#!/usr/bin/env python3

import fileinput

for line in fileinput.input():
    words = map(lambda x: x.split("_")[0], line.strip().split(" "))
    print(" ".join(words))
