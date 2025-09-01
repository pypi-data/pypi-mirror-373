'''
 2022 Bjoern Annighoefer
'''

from .serialdomain import SerialDomain

from ..config import Config, EOQ_DEFAULT_CONFIG
from ..domain import Domain
from ..command import Cmd, IsReadOnlyCmd, Evt
from ..serializer import DesCmd
from ..error import EOQ_ERROR_INVALID_TYPE


from threading import Thread, Semaphore, Lock, Event
import sys #used to exit threads
from collections import deque
#type checking
from typing import Tuple, List, Callable, Any


class ThreadController():
    ''' A class to store a thread '''
    
    def __init__(self, shallRun:bool):
        self.shallRun = shallRun
        
    def ShallRun(self)->bool:
        return self.shallRun
    
    def Stop(self):
        self.shallRun = False
        
def StopableAcquire(lock:Lock, threadController:ThreadController):
    '''This tries to acquire the lock, but looks from time to time if the thread was canceled.
    '''
    gotLock = False
    while(not gotLock):
        gotLock = lock.acquire(timeout=1.0)
        if(not threadController.ShallRun()):
            sys.exit()


class Promise():
    def __init__(self):
        self.signal = Semaphore(0)
        self.v = None
        
    def Get(self, threadController:ThreadController):
        self.signal.acquire()
        return self.v
    
    def Set(self,v):
        self.v = v
        self.signal.release()


class Job:
    def __init__(self, id:int, cmd:Cmd, sessionId:str, readOnly:bool, nDomains:int, cmdStr:str=None, serType:str=None, serialCmdOnly:bool=False):
        self.id = id
        self.cmd = cmd
        self.sessionId = sessionId
        self.readOnly = readOnly
        self.cmdStr = cmdStr
        self.serType = serType
        self.serialCmdOnly = serialCmdOnly
        self.multiDomainJobSync = Event()
        self.resPromise = Promise()
        self.processedBy = [False for i in range(nDomains)] #domains that started with the job
        self.finishedBy = [False for i in range(nDomains)] #domains that have finished this job
        self.lock = Lock() #a private lock for this job
        self.isFinished = False # is set to true if 
        
    def Result(self):
        return self.resPromise #Warning: this is only a promise. You must wait for it

class DomainPool(SerialDomain):
    def __init__(self,domains:List[Domain], shallForwardSerializedCmds:bool=False, config:Config=EOQ_DEFAULT_CONFIG):
        super().__init__(config)
        self.domains = domains
        allSerialDomains = all([isinstance(d,SerialDomain) for d in domains])
        if(shallForwardSerializedCmds and not allSerialDomains):
            raise EOQ_ERROR_INVALID_TYPE("If serial forwarding is enabled, all domains must be SerialDomain.")
        self.shallForwardSerializedCmds = shallForwardSerializedCmds
        self.config = config
        self.nDomains = len(domains)
        self.jobCount = 0
        self.jobs = deque()
        self.jobsSignal = Semaphore(0)
        self.jobsLock = Lock()
        self.allDomainsReadyEvent = Event()
        self.currentJobLock = Lock()
        self.threadController = ThreadController(True)
        self.workers = []
        workerMethod = self.__WorkerThreadSer if self.shallForwardSerializedCmds else self.__WorkerThread
        for i in range(self.nDomains):
            worker = Thread(target=workerMethod, args=(i,))
            self.workers.append(worker)
            worker.start()
        
    def Close(self)->None:
        self.threadController.Stop()
        for w in self.workers:
            w.join()
        for d in self.domains:
            d.Close()
    
    #@Override
    def RawDo(self, cmd:Cmd, sessionId:str=None, readOnly:bool=False)->Cmd:
        #override readOnly, because it is essential for the performance
        readOnly = IsReadOnlyCmd(cmd)
        cmdStr = None
        if(self.shallForwardSerializedCmds):
            cmdStr = self.remoteCmdTxSerializer.SerCmd(cmd)
        job = self.__AddNewJob(cmd, cmdStr, self.remoteCmdTxSerializer.Name(), sessionId, readOnly, False)
        res = job.Result().Get(self.threadController) #blocks until the result is ready
        return res
    
    #@Override
    def SerRawDo(self, cmdStr:str, sessionId:str=None, serType:str=None, readOnly:bool=False)->Tuple[str,str]:
        job = self.__AddNewJob(None, cmdStr, serType, sessionId, readOnly, True)
        res = job.Result().Get(self.threadController) #blocks until the result is ready
        return res
    
    def __AddNewJob(self, cmd:Cmd, cmdStr:str, serType:str, sessionId:str, readOnly=False, serialCmdOnly:bool=False)->Job:
        jobId = self.jobCount
        self.jobCount += 1 #job count is not thread-safe, but currently there is no demand for that.
        job = Job(jobId,cmd,sessionId,readOnly,self.nDomains,cmdStr,serType,serialCmdOnly)
        self.jobsLock.acquire()
        self.jobs.appendleft(job)
        self.jobsLock.release()
        self.jobsSignal.release() #indicate that a new job is waiting
        return job
        
    #@Override
    def IsEventDesired(self, evt, sourceSessionId:str, sessionId:str)->bool:
        return (sourceSessionId==sessionId)
    
    def Observe(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None, sessionId:str=None)->None:
        #Observe only domain 0. This is the masterdomain
        self.domains[0].Observe(callback, context=context, sessionId=sessionId)
        
    def Unobserve(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None, sessionId:str=None)->None:
        self.domains[0].Unobserve(callback, context=context, sessionId=sessionId)
    
    def __WorkerThread(self, n:int):
        domain = self.domains[n] #this is the domain of this thread
        while(self.threadController.ShallRun()):
            job = self.__GetNextJob(n)
            if(None!=job): #job can be None if stopped by shallRun during __GetNextJob
                res = domain.RawDo(job.cmd,job.sessionId,job.readOnly)
                job.lock.acquire()
                job.finishedBy[n] = True
                if(job.readOnly or all(job.finishedBy) ):
                    job.resPromise.Set(res) #notify about results
                    job.isFinished = True
                #in case of multi domain jobs the workers must be synchronized
                if(not job.readOnly):
                    if(job.isFinished): #I was the last worker on this multi domain job, so close it.
                        self.jobsLock.acquire()
                        self.jobs.pop() 
                        self.jobsLock.release()
                        job.lock.release()
                        job.multiDomainJobSync.set()
                    else: # I am not the last one I have to wait
                        job.lock.release()
                        #print("W%d blocked"%(n))
                        job.multiDomainJobSync.wait() 
                #print("W%d: finished job %d"%(n,job.id))
                
    def __WorkerThreadSer(self, n:int):
        domain = self.domains[n] #this is the domain of this thread
        while(self.threadController.ShallRun()):
            job = self.__GetNextJob(n)
            if(None!=job): #job can be None if stopped by shallRun during __GetNextJob
                (resStr,serType) = domain.SerRawDo(job.cmdStr,job.sessionId,job.serType,job.readOnly)
                StopableAcquire(job.lock, self.threadController)
                job.finishedBy[n] = True
                if(job.readOnly or all(job.finishedBy) ):
                    if(job.serialCmdOnly):
                        job.resPromise.Set((resStr,serType))
                    else:
                        res = DesCmd(serType,resStr)
                        job.resPromise.Set(res) #notify about results
                    job.isFinished = True
                #in case of multi domain jobs the workers must be synchronized
                if(not job.readOnly):
                    if(job.isFinished): #I was the last worker on this multi domain job, so close it.
                        StopableAcquire(self.jobsLock, self.threadController)
                        self.jobs.pop() 
                        self.jobsLock.release()
                        job.lock.release()
                        job.multiDomainJobSync.set()
                    else: # I am not the last one I have to wait
                        job.lock.release()
                        #print("W%d blocked"%(n))
                        job.multiDomainJobSync.wait() 
                #print("W%d: finished job %d"%(n,job.id))
            
    def __GetNextJob(self, n:int)->Job:
        job = None
        while(None == job and self.threadController.ShallRun()):
            isNewJob = self.jobsSignal.acquire(timeout=1.0)
            if(isNewJob):
                StopableAcquire(self.jobsLock, self.threadController)
                nextJob = self.jobs[-1]
                #print("W%d: got job %d"%(n,nextJob.id))
                if(nextJob.readOnly):
                    job = nextJob
                    self.jobs.pop()
                else: #this job is for only this  domain
                    job = nextJob
                    StopableAcquire(job.lock, self.threadController)
                    job.processedBy[n] = True #mark as processed by this domain
                    if(not all(job.processedBy)):
                        self.jobsSignal.release() #make it possible for the remaining threads to get this job
                    job.lock.release()
                self.jobsLock.release()
        return job
                               
        
