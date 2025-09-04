'''
Created on Jul 15, 2025

@author: ahypki
'''

import os.path
import re
import subprocess
import sys
import time
# import urllib.request

def firstGroup(s, regex):
    r = re.compile(regex)
    m = r.search(s)
    if m:
        return m.group(1)
    return ""

def isNumber(s):
    return matches(s, '^[\d]+$')

def matches(s, regex):
    r = re.compile(regex)
    m = r.search(s)
    if m:
        return True
    return False