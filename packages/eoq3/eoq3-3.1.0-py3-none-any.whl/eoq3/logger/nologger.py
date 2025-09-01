'''
2019 Bjoern Annighoefer
'''

from .logger import Logger, RegisterLogger, DEFAULT_LOGGER_LEVELS

class NoLogger(Logger):
    '''A logger which does nothing
    '''
    def __init__(self, activeLevels:int=DEFAULT_LOGGER_LEVELS.L2_WARNING):
        super().__init__(activeLevels)
        
    #@Override
    def ShallLog(self):
        return False

    #@Override
    def _Log(self, levelName:str, msg:str):
        pass #do nothing

RegisterLogger("NOL",NoLogger,[])
    
    