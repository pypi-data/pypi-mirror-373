'''
 2019 Bjoern Annighoefer
'''

'''
    Server
'''

from .remotedomainserver import RemoteDomainServer
from .queuebasedframecom import QueueBasedFrameCom

from ..config import Config
from ..domain import Domain

from multiprocessing import Queue


class MultiprocessingQueueDomainHost(RemoteDomainServer):
    def __init__(self,cmdTxQueue:Queue, cmdRxQueue:Queue, domain:Domain, shallForwardSerializedCmds:bool, config:Config):
        super().__init__(domain,shallForwardSerializedCmds,config)
        #internals
        self.shallRun = True
        self.comController = QueueBasedFrameCom(cmdTxQueue,cmdRxQueue,config,self.OnSerFrmReceived)
        self.comController.Start() #last action to make sure not any notifies are called before
        
    #@Override
    def SendSerFrm(self, frmStr:str, sessionId:str)->None:
        '''Needs to be overwritten by the implementation
        '''
        self.comController.SendRaw(frmStr)
           
    def Stop(self)->None:
        self.comController.Stop()
        
    
        