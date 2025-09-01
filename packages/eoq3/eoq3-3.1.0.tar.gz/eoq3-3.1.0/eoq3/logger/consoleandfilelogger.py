'''
2019 Bjoern Annighoefer
'''
from .logger import DEFAULT_LOGGER_LEVELS,RegisterLogger
from .compoundlogger import CompoundLogger
from .consolelogger import ConsoleLogger
from .filelogger import FileLogger

import os
import logging

class ConsoleAndFileLogger(CompoundLogger):
    """A logger that outputs every thing to the console and dedicated files for each active log level
    """
    def __init__(self,activeLevels:int=DEFAULT_LOGGER_LEVELS.L2_WARNING,logDir='./log',prefix=''):
        super().__init__(activeLevels)
        self.logDir = logDir
        self.AddLogger(ConsoleLogger(activeLevels))
        self.AddLogger(FileLogger(activeLevels,logDir,prefix))

RegisterLogger("CFL",ConsoleAndFileLogger,[ "logDir","prefix"])