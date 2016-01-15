#!/usr/bin/env python3

import sys
import argparse

# Usage: python [thisScript] < input > outputConllFormat
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delimiter', type=str, default='_')
    args = parser.parse_args()
    delimiter = args.delimiter
    stdin_buffer = sys.stdin.readlines()
    transFormToConll(stdin_buffer, delimiter)

def transFormToConll(fileHandle, delimiter):
    for line in fileHandle:
        ll = line.rstrip()
        if not ll.startswith('#'):
            pairs = ll.split(' ')
            for i in range(0, len(pairs)):
                word_pos = pairs[i].split(delimiter)
                if len(word_pos) == 2:
                    print(str(i+1) +  '\t' + word_pos[0] +  '\t' + '_' +  '\t' + word_pos[1] +  '\t' + word_pos[1] +  '\t' + '_'+  '\t' + '_'+  '\t' + '_')
                elif len(word_pos) == 3:
                    if word_pos[2] == '1':
                        print(str(i+1) +  '\t' + word_pos[0] +  '\t' + '_' +  '\t' + word_pos[1] +  '\t' + word_pos[1] +  '\t' + '1'+  '\t' + '_'+  '\t' + '_')
                    else:
                        print(str(i+1) +  '\t' + word_pos[0] +  '\t' + '_' +  '\t' + word_pos[1] +  '\t' + word_pos[1] +  '\t' + '_'+  '\t' + '_'+  '\t' + '_')
                elif len(word_pos) > 3:
                    if word_pos[-1] == '1' or word_pos[-1] == '0':
                        if word_pos[-1] == '1':
                            mergeWord = ''
                            for i in range(0, len(word_pos) - 2):
                                mergeWord += word_pos[i]
                            mergePos = word_pos[-2]
                            print(str(i+1) +  '\t' + mergeWord +  '\t' + '_' +  '\t' + mergePos +  '\t' + mergePos +  '\t' + '1'+  '\t' + '_'+  '\t' + '_')
                        else:
                            mergeWord = ''
                            for i in range(0, len(word_pos) - 2):
                                mergeWord += word_pos[i]
                            mergePos = word_pos[-2]
                            print(str(i+1) +  '\t' + mergeWord +  '\t' + '_' +  '\t' + mergePos +  '\t' + mergePos +  '\t' + '_'+  '\t' + '_'+  '\t' + '_')
                    else:
                        mergeWord = ''
                        for i in range(0, len(word_pos) - 1):
                            mergeWord += word_pos[i]
                        mergePos = word_pos[-1]
                        print(str(i+1) +  '\t' + mergeWord +  '\t' + '_' +  '\t' + mergePos +  '\t' + mergePos +  '\t' + '_'+  '\t' + '_'+  '\t' + '_')
                else:
                    print('err: not splitible in: ' + pairs[i])
            print()

if __name__ == '__main__':
    main()

