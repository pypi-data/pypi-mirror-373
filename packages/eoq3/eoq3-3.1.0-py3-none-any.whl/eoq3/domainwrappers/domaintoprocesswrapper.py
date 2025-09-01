'''
A class that starts a domain in a separate process.

2022 Bjoern Annighoefer
'''

from .multiprocessingdomainclient import MultiprocessingQueueDomainClient
from .multiprocessingdomainhost import MultiprocessingQueueDomainHost

from ..config import Config, EOQ_DEFAULT_CONFIG
from ..error import EOQ_ERROR_RUNTIME

from multiprocessing import Queue, Process
from threading import Thread
import queue

#type checking
from typing import Dict,Any

class PROCESS_ADMIN_COMMANDS:
    STOP = 'STOP'
    CONFIRM = 'CONFIRM'
    SEPERATOR = ' '

def DomainProcess(domainFactory:callable, domainFactoryArgs:Any, shallForwardSerializedCmds:bool, cmdTxQueue:Queue, cmdRxQueue:Queue, adminQueueTx:Queue, adminQueueRx:Queue, hostConfig:Config):
    #print("DomainProcess started")
    domain = domainFactory(domainFactoryArgs)
    server = MultiprocessingQueueDomainHost(cmdTxQueue,cmdRxQueue,domain,shallForwardSerializedCmds,hostConfig)
    #print("DomainProcess server ready.")
    #confirm that the domain in the process was created successfully
    adminQueueRx.put(PROCESS_ADMIN_COMMANDS.CONFIRM)
    #enter command loop
    shallRun = True
    while(shallRun):
        commandStr = adminQueueTx.get()
        commandFrags = commandStr.split(PROCESS_ADMIN_COMMANDS.SEPERATOR)
        command = commandFrags[0]
        if(PROCESS_ADMIN_COMMANDS.STOP == command):
            shallRun = False
            adminQueueRx.put(PROCESS_ADMIN_COMMANDS.CONFIRM)
    server.Stop()
    domain.Close()


class DomainToProcessWrapper(MultiprocessingQueueDomainClient):
    def __init__(self, domainFactory:callable, domainFactoryArgs:Any=None, shallForwardSerializedCmds:bool=False, config:Config=EOQ_DEFAULT_CONFIG):
        '''
        Args:
        domainFactory: a function that returns an instance of the domain
        '''
        super().__init__(Queue(), Queue(), config)
        self.adminQueueTx = Queue()
        self.adminQueueRx = Queue()
        
        if(config.processLessMode): #in debug mode no process is created, but the server executed in the same Process
            # in the following rx and tx queues for commands and events are mirrored to establish the communication
            self.clientProcess = Thread(name="Domain Worker (Thread)", target=DomainProcess, args=(domainFactory,domainFactoryArgs,shallForwardSerializedCmds,self.cmdRxQueue,self.cmdTxQueue,self.adminQueueTx,self.adminQueueRx,config,))
        else:
            self.clientProcess = Process(name="Domain Worker (Process)", target=DomainProcess, args=(domainFactory,domainFactoryArgs,shallForwardSerializedCmds,self.cmdRxQueue,self.cmdTxQueue,self.adminQueueTx,self.adminQueueRx,config,))
            self.clientProcess.daemon = True #quit this if the hosting process closes
        self.clientProcess.start()
        #wait on the confirmation that the server really started
        try:
            confirm = self.adminQueueRx.get(timeout=config.connectTimeout)
            if(PROCESS_ADMIN_COMMANDS.CONFIRM != confirm):
                raise EOQ_ERROR_RUNTIME('Failed to init domain process.')
        except queue.Empty:
            raise EOQ_ERROR_RUNTIME('Failed to init domain process.')
        
    #@Override
    def Close(self):
        self.__IssueAdminCommand(PROCESS_ADMIN_COMMANDS.STOP)
        self.clientProcess.join()
        super().Close()
            
        
    def __IssueAdminCommand(self,command:str,args:list=[]):
        commandStr = PROCESS_ADMIN_COMMANDS.SEPERATOR.join([command]+args)
        self.adminQueueTx.put(commandStr)
        confirm = self.adminQueueRx.get()
        if(PROCESS_ADMIN_COMMANDS.CONFIRM != confirm):
            raise EOQ_ERROR_RUNTIME('Communication with domain process failed.')
        
    