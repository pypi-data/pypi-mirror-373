"""
 2022 Bjoern Annighoefer
"""

from .serialdomain import SerialDomain

from ..config import Config
from ..command import Cmd, Evt
from ..frame import Frm, FRM_TYPE
from ..error import EOQ_ERROR_RUNTIME

from threading import Lock, Semaphore
#type checking
from typing import Tuple, Callable, List, Any


class Request:
    """A class storing requests as long as a command is running
    """
    def __init__(self, frmId:int):
        self.frmId = frmId
        self.signal = Semaphore(0)
        self.resStr = None #this can be used to transfare back the result to the sync thread
        self.serType = None
        
    def Complete(self, resStr:str, serType:str):
        """Complete the request
        """
        self.resStr = resStr
        self.serType = serType
        self.signal.release() #inform the waiting thread

class RemoteDomainClient(SerialDomain):
    """A domain that forwards commands as frames via some serial interface"""
    def __init__(self, config:Config, name:str="RemoteDomainClient"):
        super().__init__(config)
        self.name = name #used for debugging purposes
        self.frmId = 0
        self.frmIdLock = Lock()
        #request Queue
        self.requestQueue = {} #the list of open requests
        self.requestQueueLock = Lock()
        
    #@Override
    def RawDo(self, cmd:Cmd, sessionId:str=None, readOnly=False):
        cmdStr = self.remoteCmdTxSerializer.SerCmd(cmd)
        (resStr,resSerType) = self.SerRawDo(cmdStr, sessionId, self.remoteCmdTxSerializer.Name(),readOnly)
        res = self._DesCmd(resSerType,resStr)
        return res
    
    #@Override
    def SerRawDo(self, cmdStr:str, sessionId:str=None, serType:str=None, readOnly=False)->Tuple[str,str]:
        #build the frame
        frmId = self.__GetNextFrmId()
        frm = Frm(FRM_TYPE.CMD, frmId, serType, cmdStr, sessionId, readOnly)
        request = Request(frmId)
        #add a new request to the stack
        self.requestQueueLock.acquire()
        self.requestQueue[frmId] = request
        self.requestQueueLock.release()
        #send the request
        frmStr = self.remoteFrmTxSerializer.SerFrm(frm)
        self.SendSerFrm(frmStr)
        #wait for the result
        gotResult = request.signal.acquire(timeout=self.config.commandTimeout)
        #remove the result from the expected ones, because nobody listens anymore.
        self.requestQueueLock.acquire()
        del self.requestQueue[frmId]
        self.requestQueueLock.release()
        #check if we got a result in time
        if(not gotResult):
            raise EOQ_ERROR_RUNTIME("%s: Frm %d: Receive timeout. Disconnected?"%(self.name,frmId))
        resStr = request.resStr
        resSerType = request.serType
        return (resStr,resSerType)
    
    #@Override
    def Observe(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None, sessionId:str=None)->None: #by default register for all events
        """Forward the observe wish to the domain
        """
        super().Observe(callback, context, sessionId)
        frm = Frm(FRM_TYPE.OBS, 0, "NON", "", sessionId)
        frmStr = self.remoteFrmTxSerializer.SerFrm(frm)
        self.SendSerFrm(frmStr)
    
    #@Override    
    def Unobserve(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None, sessionId:str=None)->None:
        frm = Frm(FRM_TYPE.UBS, 0, "NON", "", sessionId)
        frmStr = self.remoteFrmTxSerializer.SerFrm(frm)
        self.SendSerFrm(frmStr)
        super().Unobserve(callback, context, sessionId)
         
    #@Override
    def IsEventDesired(self, evt, sourceSessionId:str, sessionId:str)->bool:
        return (sourceSessionId==sessionId)
    
    def OnSerFrmReceived(self, frmStr:str)->None:
        """Needs to be called if frames were received
        """
        frm = self.remoteFrmRxSerializer.DesFrm(frmStr)
        if(FRM_TYPE.RES == frm.typ):
            try:
                request = self.requestQueue[frm.uid]
                request.Complete(frm.dat, frm.ser)
            except KeyError:
                self.logger.Warn("%s: Skipped unexpected response: %s"%(self.name,frmStr))
        elif(FRM_TYPE.EVT == frm.typ):
            sourceSessionId = frm.sid
            if(self.config.enableRawEvents):    
                self.NotifyObservers(frm.dat, sourceSessionId)
            else:
                try:
                    evtCmd = self._DesCmd(frm.ser,frm.dat) #universal deserialization
                    evts = evtCmd.a
                    self.NotifyObservers(evts,sourceSessionId)
                except Exception as e:
                    self.logger.Error('%s: Event deserialization failed: %s'%(self.name,str(e)))
        else:
            self.logger.Warn("%s: Skipped unexpected frame type: %s"%(self.name,frm.typ))
            
    ### INTERFACE ###
    
    def SendSerFrm(self,frmStr:str)->None:
        """This needs to be overwritten by the implementing domain """
        raise NotImplemented()
    
    ### PRIVATE ###
        
    def __GetNextFrmId(self):
        self.frmIdLock.acquire()
        frmId = self.frmId;
        if(self.frmId < 2^32): #limit frame IDs to 4byte
            self.frmId += 1
        else: #wrap around
            self.frmId = 0
        self.frmIdLock.release()
        return frmId
    
