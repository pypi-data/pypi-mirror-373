'''
2019 Bjoern Annighoefer
'''

from .logger import Logger,RegisterLogger,DEFAULT_LOGGER_LEVELS

class ConsoleLogger(Logger):
    """A logger printing to the console
    """
    def __init__(self,activeLevels:int=DEFAULT_LOGGER_LEVELS.L2_WARNING):
        super().__init__(activeLevels)

    #@Override         
    def _Log(self,levelName:str,msg:str):
        print("%s: %s"%(levelName,msg))

RegisterLogger("COL",ConsoleLogger,[])