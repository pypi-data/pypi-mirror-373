'''
Created on Jul 15, 2025

@author: ahypki
'''
from gima.utils.Logger import Logger
import subprocess
from gima.utils.regex import firstGroup


def linux_cmd(cmd, workingDir = None, printImmediatelly = False):
    if printImmediatelly:
        Logger.logDebug("linux cmd: " + cmd);
    result = []
    proc = subprocess.run(cmd, cwd = workingDir, shell = True, capture_output=True, text=True).stdout
    # print(proc)
    for line in proc.splitlines():
        strLine = line.rstrip()
        result.append(strLine)
        if printImmediatelly:
            print(strLine)
    return result