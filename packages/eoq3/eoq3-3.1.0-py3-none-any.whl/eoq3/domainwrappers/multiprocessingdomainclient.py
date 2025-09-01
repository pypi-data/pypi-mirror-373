'''
 2022 Bjoern Annighoefer
'''

from .remotedomainclient import RemoteDomainClient
from .queuebasedframecom import QueueBasedFrameCom

from ..config import Config, EOQ_DEFAULT_CONFIG

from multiprocessing import Queue
from threading import Semaphore, Lock


'''
 CLIENT
 
'''

class DO_STRATEGY:
    SYNC = 0
    ASYNC = 1


class ResultWaitInfo:
    def __init__(self,commandId,doStrategy:int,semaphore=None,callback=None):
        self.commandId = commandId
        self.doStrategy = doStrategy
        self.semaphore = semaphore
        self.callback = callback
        self.res = None #this can be used to transfare back the result to the sync thread
    


class MultiprocessingQueueDomainClient(RemoteDomainClient):
    def __init__(self,cmdTxQueue:Queue, cmdRxQueue:Queue, config:Config=EOQ_DEFAULT_CONFIG, name:str="MultiprocessingQueueDomainClient"):
        super().__init__(config,name)
        self.cmdTxQueue = cmdTxQueue
        self.cmdRxQueue = cmdRxQueue
        self.comController = QueueBasedFrameCom(cmdTxQueue, cmdRxQueue, config, self.OnSerFrmReceived)  
        self.lock = Lock()
        self.resSignal = Semaphore(0)
        self.resStr = None
        self.frmId = 0
        self.frmIdLock = Lock()
        self.comController.Start() #last action to make sure not any notifies are called before
    
    #@Override    
    def Close(self):
        self.comController.Stop()
        
    #@Override
    def SendSerFrm(self,frmStr:str)->None:
        """Need to be implemented because it is called within RemoteDomainClient
        """
        self.comController.SendRaw(frmStr)
