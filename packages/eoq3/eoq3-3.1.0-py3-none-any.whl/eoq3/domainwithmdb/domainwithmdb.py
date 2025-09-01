'''
 2019 Bjoern Annighoefer
'''

from .cmdrunner import CmdRunner   

from ..config import Config, EOQ_DEFAULT_CONFIG
from ..logger import GetLoggerInstance
from ..command import Cmd, Evt
from ..domain import Domain

from ..mdb import Mdb
from ..accesscontroller import AccessController, NoAccessController
 
from threading import Lock
#type checking
from typing import Callable, List, Any

class DomainWithMdb(Domain):
    def __init__(self, mdb:Mdb, accessController:AccessController=NoAccessController(), config:Config=EOQ_DEFAULT_CONFIG):
        super().__init__()
        self.mdb = mdb
        self.accessController = accessController
        self.config = config
        self.logger = GetLoggerInstance(config)
        #internals 
        self.threadSafeLock = Lock()
        self.cmdRunner = CmdRunner(mdb, accessController, config)
        #init the access controller        
        
        
    def RawDo(self, cmd:Cmd, sessionId=None, readOnly=False):
        self.threadSafeLock.acquire()
        #self.logger.PassivatableLog(LogLevels.INFO,lambda : "cmd: %s"%(self.serializer.serialize(cmd)))
        res = self.cmdRunner.Exec(cmd,sessionId,readOnly)
        self.threadSafeLock.release()
        return res
    
    #Override the event provide methods since the sole event provider shall be the cmd runner
    #@Override
    def Observe(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None, sessionId:str=None)->None: #by default register for all events
        self.threadSafeLock.acquire()
        self.cmdRunner.Observe(callback,context,sessionId)
        self.threadSafeLock.release()
    
    #@Override    
    def Unobserve(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None, sessionId:str=None)->None:
        self.threadSafeLock.acquire()
        self.cmdRunner.Unobserve(callback,context,sessionId)
        self.threadSafeLock.release()
        
    def Close(self):
        self.cmdRunner.Close()
        #benchmark:
        if self.config.enableStatistics:
            self.cmdRunner.benchmark.SaveToFile('CmdBenchmark.csv')
            self.logger.Info("Command benchmark saved to CmdBenchmark.csv")
            self.cmdRunner.qryRunner.benchmark.SaveToFile('QryBenchmark.csv')
            self.logger.Info("Query segment benchmark saved to QryBenchmark.csv")
        
        
 
        