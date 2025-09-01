'''
 2019 Bjoern Annighoefer
'''

from ..config import Config

import queue # imported for using queue.Empty exception
from multiprocessing import Queue
from threading import Thread

import traceback



class QueueBasedFrameCom:
    def __init__(self, cmdTxQueu:Queue, cmdRxQueu:Queue,\
                config:Config,\
                rawFrmCallback):
        super().__init__()
        self.cmdTxQueu = cmdTxQueu
        self.cmdRxQueu = cmdRxQueu
        self.rawFrmCallback = rawFrmCallback
        self.config = config
        
    def SendRaw(self,frmStr:str):
        self.cmdTxQueu.put(frmStr)
        
#     def SendEvt(self,frame:Frm):
#         ##print('Sending frame on queue: %d'%(queueNb))
#         frmStr = self.config.remoteSerializer.SerFrm(frame)
#         self.SendEvtRaw(frmStr)
#         
#     def SendEvtRaw(self,frmStr:str):
#         self.evtTxQueue.put(frmStr)
#         #print('%s: event send %d bytes'%(self,len(frmStr)))
        
    def Start(self):
        ##create an event observing thread
        self.shallRun = True
        self.rxThread = Thread(target=self.__RxThread, args=('RxThread',self.cmdRxQueu,self.rawFrmCallback,))
        self.rxThread.start()
 
    def Stop(self):
        self.shallRun = False
        #print('%s: stopped (run %d)'%(self,self.shallRun))
        self.rxThread.join()
        #print('%s: Both threads stopped (run: %d)'%(self,self.shallRun))
        
    def __RxThread(self, name:str, cmdRxQueu, rawCallback):
        while(self.shallRun):
            try:
                frmStr = cmdRxQueu.get(timeout=self.config.threadLoopTimeout)
                #print("%s: frm recieved: %s"%(self,frmStr))
                try:
                    rawCallback(frmStr)
                except Exception as e:
                    print('%s: %s raw callback failed: %s'%(self,name,str(e)))
                    traceback.print_exc()
            except queue.Empty:
                pass #wait for next frame
            except Exception as e:
                print('%s: %s failed: %s'%(self,name,str(e)))
        #thread terminates here
        #print('%s: %s terminated'%(self,name))

        
