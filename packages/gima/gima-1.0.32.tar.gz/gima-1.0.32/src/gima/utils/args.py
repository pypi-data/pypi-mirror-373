'''
Created on Jul 15, 2025

@author: ahypki
'''

import sys

def getArgString(name, defaultvalue):
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--" + name:
            return sys.argv[i + 1]
    return defaultvalue

def isArgPresent(name):
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--" + name or sys.argv[i] == "-" + name:
            return True
    return False