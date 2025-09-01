'''
2019 Bjoern Annighoefer
'''

from ..error import EOQ_ERROR_INVALID_VALUE
from ..config import Config
# external imports
import traceback
# type annotations
from typing import List,Callable,Type,Dict

class LOG_LEVEL_NAMES:
    ERROR =  "error"
    WARN =   "warning"
    INFO =   "info"
    DEBUG =  "debug"

class LOG_LEVELS_NUM:
    ERROR =  int(1)
    WARN =   int(2)
    INFO =   int(4)
    DEBUG =  int(8)

LOG_LEVELS_NAME_LUT:Dict[int,str] = {
    LOG_LEVELS_NUM.ERROR: LOG_LEVEL_NAMES.ERROR,
    LOG_LEVELS_NUM.WARN: LOG_LEVEL_NAMES.WARN,
    LOG_LEVELS_NUM.INFO: LOG_LEVEL_NAMES.INFO,
    LOG_LEVELS_NUM.DEBUG: LOG_LEVEL_NAMES.DEBUG,
}

class DEFAULT_LOGGER_LEVELS:
    L0_SILENT  = int(0)
    L1_ERROR   = LOG_LEVELS_NUM.ERROR
    L2_WARNING = LOG_LEVELS_NUM.ERROR | LOG_LEVELS_NUM.WARN
    L3_INFO    = LOG_LEVELS_NUM.ERROR | LOG_LEVELS_NUM.WARN | LOG_LEVELS_NUM.INFO
    L4_DEBUG   = LOG_LEVELS_NUM.ERROR | LOG_LEVELS_NUM.WARN | LOG_LEVELS_NUM.INFO | LOG_LEVELS_NUM.DEBUG

class Logger:
    """Base class for all loggers.
    Provides the interface for logging specific log levels, i.e. Debug, Info, Warn, Error.
    Provides the interface for passivatable logging, i.e. PDebug, PInfo, PWarn, PError.
    Each inheriting logger implementation must implement the _Log method.
    """
    def __init__(self, activeLevels:int=DEFAULT_LOGGER_LEVELS.L2_WARNING):
        self.activeLevels = activeLevels
        
    def ShallLog(self):
        return True
    
    def Log(self, level:int, msg:str):
        if(level & self.activeLevels and self.ShallLog()):
            self._Log(LOG_LEVELS_NAME_LUT[level],msg)
    
    #simple log functions
    
    def Debug(self, msg:str):
        self.Log(LOG_LEVELS_NUM.DEBUG, msg)
    
    def Info(self, msg:str):
        self.Log(LOG_LEVELS_NUM.INFO, msg)
        
    def Warn(self, msg:str):
        self.Log(LOG_LEVELS_NUM.WARN, msg)
        
    def Error(self, msg:str):
        self.Log(LOG_LEVELS_NUM.ERROR, msg)
        
    #passive log functions
    
    def PLog(self, level:int, msgFactory:Callable[[],str]):
        """Passivatable log. Is supposed to have higher waste less
        performance if not used, because msgFactory is only evaluated if
        log level is active"""
        if(level & self.activeLevels and self.ShallLog()):
            try:
                levelName = LOG_LEVELS_NAME_LUT[level]
                self._Log(levelName,msgFactory())
            except Exception as e:
                traceback.print_exc()
                self._Log(LOG_LEVEL_NAMES.ERROR,'ERROR while logging: %s'%str(e))
                
    def PDebug(self,msgFactory:Callable[[],str]):
        self.PLog(LOG_LEVELS_NUM.DEBUG, msgFactory)
        
    def PInfo(self,msgFactory:Callable[[],str]):
        self.PLog(LOG_LEVELS_NUM.INFO, msgFactory)
        
    def PWarn(self,msgFactory:Callable[[],str]):
        self.PLog(LOG_LEVELS_NUM.WARN, msgFactory)
    
    def PError(self,msgFactory:Callable[[],str]):
        self.PLog(LOG_LEVELS_NUM.ERROR, msgFactory)
    

    #the following must be overwritten to produce the output
    def _Log(self, levelName:str, msg:str):
        raise NotImplementedError('_Log must be implemented by inheriting class.')

### LOGGER IMPLEMENTATIONS ###
class LoggerInfo:
    def __init__(self, name:str, loggerClass:Type[Logger], initArgNames:List[str]):
        self.name = name
        self.loggerClass = loggerClass
        self.initArgNames = initArgNames

LOGGER_REGISTRY:Dict[str,LoggerInfo] = {} # a registry for for current logger implementations

def RegisterLogger(name:str, loggerClass:Type[Logger], initArgNames:List[str]):
    LOGGER_REGISTRY[name] = LoggerInfo(name, loggerClass, initArgNames)

### LOGGER INSTANCES ###
# Keep registry for logger instances, to reduce resource usage
LOGGER_INSTANCE_REGISTRY:Dict[str,Logger] = {} # a registry for for current logger instances

def LoggerIdString(config:Config)->str:
    '''Returns a string identifying the logger instance
    '''
    loggerIdStr = '%s%s%s'%(config.logger,config.activeLogLevels,config.loggerInitArgs)
    return loggerIdStr

def GetLoggerInstance(config:Config)->Logger:
    '''Returns a logger instance based on the config settings
    '''
    loggerIdStr = LoggerIdString(config)
    try:
        return LOGGER_INSTANCE_REGISTRY[loggerIdStr]
    except KeyError:
        #create a new logger instance
        loggerInfo = LOGGER_REGISTRY[config.logger]
        if(len(loggerInfo.initArgNames) < len(config.loggerInitArgs)):
            raise EOQ_ERROR_INVALID_VALUE('Expecting only %d arguments for logger %s, but got %d'%(len(loggerInfo.initArgNames),config.logger,len(config.loggerInitArgs)))
        for argName in loggerInfo.initArgNames:
            if(not argName in config.loggerInitArgs):
                raise EOQ_ERROR_INVALID_VALUE('Logger argument %s is missing in config'%(argName))
        loggerInstance = loggerInfo.loggerClass(config.activeLogLevels,**config.loggerInitArgs)
        LOGGER_INSTANCE_REGISTRY[loggerIdStr] = loggerInstance
        return loggerInstance

        