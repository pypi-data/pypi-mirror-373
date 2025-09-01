'''
2019 Bjoern Annighoefer
'''

from .logger import Logger,RegisterLogger, DEFAULT_LOGGER_LEVELS, LOG_LEVELS_NAME_LUT

import os
import logging

class FileLogger(Logger):
    """A logger that logs to a file.
    If split files is desired, each log level has its own file.
    The log files are created in the logDir with the prefix and the log level as name.
    """
    def __init__(self,activeLevels:int=DEFAULT_LOGGER_LEVELS.L2_WARNING,logDir:str='./log',prefix:str='log',splitFiles:bool=False):
        super().__init__(activeLevels)
        self.logDir = logDir
        self.prefix = prefix #the text added as log file name
        self.splitFiles = splitFiles
        #internals
        self.pyLoggers = {}
        #make sure the dir exists
        if(not os.path.isdir(self.logDir)):
            os.makedirs(self.logDir)
        #create loggers
        if(splitFiles):
            # create native python loggers for each level
            for k,v in LOG_LEVELS_NAME_LUT.items():
                if(k & activeLevels):
                    self._InitPyLogger(v,v)
        else:
            # create native python logger
            self._InitPyLogger("all","")

    def _InitPyLogger(self,name,postfix):
        """Initializes a python logger for the given name
        and adds it to the pyLoggers dict.
        """
        logger = logging.getLogger(name)
        logFile = os.path.join(self.logDir, "%s%s.log" % (self.prefix, postfix))
        fh = logging.FileHandler(logFile, 'w')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
        self.pyLoggers[name] = logger

    #@Override         
    def _Log(self,levelName:str,msg:str):
        if(self.splitFiles):
            self.pyLoggers[levelName].info(msg)
        else:
            self.pyLoggers["all"].info(f"[{levelName}] {msg}")


RegisterLogger("FIL",FileLogger,[ "logDir","prefix","splitFiles"])
