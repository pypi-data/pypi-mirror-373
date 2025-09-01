'''
2019 Bjoern Annighoefer
'''

from .logger import Logger,RegisterLogger,DEFAULT_LOGGER_LEVELS

class CompoundLogger(Logger):
    """A logger forwarding the log messages to multiple child loggers.
    Use AddLogger and RemoveLogger to manage the list of loggers.
    """
    def __init__(self,activeLevels:int=DEFAULT_LOGGER_LEVELS.L2_WARNING):
        super().__init__(activeLevels)
        self.loggers = []

    #@Override
    def _Log(self,levelName:str,msg:str):
        for logger in self.loggers:
            logger.Log(levelName,msg)

    def AddLogger(self,logger:Logger):
        """Add a logger to the list of loggers
        """
        self.loggers.append(logger)

    def RemoveLogger(self,logger:Logger):
        """Remove a logger from the list of loggers
        """
        self.loggers.remove(logger)

RegisterLogger("CPL",CompoundLogger,[])