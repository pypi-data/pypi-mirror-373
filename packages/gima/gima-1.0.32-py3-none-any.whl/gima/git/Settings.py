'''
Created on Jul 15, 2025

@author: ahypki
'''

class Settings(object):
    '''
    classdocs
    '''

    MAX_COMMIT_BYTES = 1_000 * 1_000_000 # 1 GB
    
    SEPARATOR_NEXT_REPO = '############################################################'
    PREFIX_LINE = "# "

    def __init__(self, params):
        '''
        Constructor
        '''
        