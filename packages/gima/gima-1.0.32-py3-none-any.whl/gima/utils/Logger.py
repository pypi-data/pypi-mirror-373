'''
Created on Jul 10, 2025

@author: ahypki
'''
from rich.console import Console

console = Console()

class Logger:
    BLUE = '[blue]'#'\033[94m'
    BLUE_END = '[/blue]'
    GREEN = '[green]'#'\033[92m'
    GREEN_END = '[/green]'
    RED = '[red]'#'\033[91m'
    RED_END = '[/red]'
    WARNING = '[yellow]'#'\033[93m'
    WARNING_END = '[/yellow]'
    FAIL = RED#'\033[91m'
    FAIL_END = RED_END
    # ENDC = '\033[0m'
    
    DEBUG = False
    INFO = True
    
    def blue(s):  # @NoSelf
        return Logger.BLUE + s + Logger.BLUE_END
    
    def logDebug(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        if Logger.DEBUG:
            console.print(("DEBUG " if printLogLevel else '') 
                  + str(msg), 
                  end = ('\n' if printNewLine else ''))
    
    def logInfo(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        if Logger.INFO:
            console.print(("INFO  " if printLogLevel else '') 
                  + str(msg), 
                  end = ('\n' if printNewLine else ''))
        
    def logWarn(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        console.print(("WARN  " if printLogLevel else '') 
              + str(Logger.WARNING + msg + Logger.WARNING_END), 
              end = ('\n' if printNewLine else ''))
    
    def logError(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        console.print(("ERROR " if printLogLevel else '') 
              + str(msg), 
              end = ('\n' if printNewLine else ''))
