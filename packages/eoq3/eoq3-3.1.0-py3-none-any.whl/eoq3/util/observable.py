'''

2022 Bjoern Annighoefer
'''

from ..command import Evt

import traceback
from threading import Lock
#type checking
from typing import Callable, Any, List

class ObserverInfo:
    def __init__(self, callback:Callable[[List[Evt],Any,object],None], context:Any, sessionId:str):
        self.callback = callback #the callback function of the event listener
        self.context = context #a unique identifier or None
        self.sessionId = sessionId #set if this observer is linked to a session
        self.queuedEvts = [] #events for this observer postponed for sending
        self.evts = [] #events for this observer marked for sending
        
'''
    EventProvider
'''
class Observable:
    def __init__(self):
        self.observers = {} # callback -> event
        self.observerQueueMutex = Lock()
        
    def Observe(self, callback:Callable[[List[Evt],Any,object],None], context:Any=None,
                sessionId:str=None)->None: #by default register for all events
        """Register a callback function, which is invoked when an event is received.
          callback: Callable[[List[Evt],Any,object],None] - The callback function that
            is invoked when an event is received. The first argument is a list of events,
            the second argument is the context, the third argument is the domain.
          context: Any - A unique context that helps the callback to identify the specific
            Observe registration. Context must be hashable.
          sessionId: str - The session ID of the session that wants to observe events.
            This session must have registered for the desired events before using OBS commands.
        """
        observerInfo = ObserverInfo(callback,context,sessionId)
        self.observerQueueMutex.acquire()
        try:
            self.observers[(callback,context,sessionId)] = observerInfo
        finally:
            self.observerQueueMutex.release()
        
    def Unobserve(self, callback:Callable[[List[Evt],Any,object],None],context:Any=None, sessionId:str=None)->None:
        self.observerQueueMutex.acquire()
        try:
            self.observers.pop((callback,context,sessionId))
        finally:
            self.observerQueueMutex.release()


    '''
        INTERNAL EVENT PROCESSING
    '''

    def IsEventDesired(self, evt:Evt, sourceSessionId:str, sessionId:str)->bool:
        return True
        
    def NotifyObservers(self, evts:List[Evt], sourceSessionId:str)->None: #sends multiple events   
        #print("%s notifying %d observers"%(self,len(self.observers)))
        newEvts = evts.copy() #make a copy to ensure that the list is not changed outside when the event notification loop runs. 
        self.observerQueueMutex.acquire()
        for o in self.observers.values():
            filteredEvts = [e for e in newEvts if self.IsEventDesired(e,sourceSessionId,o.sessionId)]
            try:
                if(0<len(filteredEvts)):
                    o.callback(filteredEvts,o.context,self)
                    #print("%s called"%(o.callback))
            except:
                print("EvtProvider: Warning observer callback failed:")
                traceback.print_exc()
        self.observerQueueMutex.release()
            
    def PostponeObserverNotification(self, evts:List[Evt], sourceSessionId:str)->None: 
        ''' Prepare events for being send to the observers but do not send them right away, 
        but wait for being released.
        
        '''
        newEvts = evts.copy() #make a copy to ensure that the list is not changed outside when the event notification loop runs. 
        self.observerQueueMutex.acquire()
        #print("%s: Postponing %d events: %s"%(self, len(newEvts),[e.a[0] for e in newEvts] ))
        for o in self.observers.values():
            filteredEvts = [e for e in newEvts if self.IsEventDesired(e,sourceSessionId,o.sessionId)]
            if(0<len(filteredEvts)):
                #print("%s: Queuing %d events for %s"%(self, len(filteredEvts),o.sessionId))
                o.queuedEvts.append(filteredEvts)
        self.observerQueueMutex.release()      
        
    def ClearPostponedNotifications(self):
        '''Clears the stored notifications without sending them
        '''
        self.observerQueueMutex.acquire()
        for o in self.observers.values():
            o.queuedEvts.clear()
        self.observerQueueMutex.release()
        
    def ReleasePostponedNotifications(self):
        '''Moves all queued events to the sending queues
        '''
        self.observerQueueMutex.acquire()
        for o in self.observers.values():
            o.evts += o.queuedEvts
            o.queuedEvts.clear()
        self.observerQueueMutex.release()
        
        
    def SendQueuedAndReleasedNotifications(self):
        ''' Sends out all events that have been queued
        '''
        self.observerQueueMutex.acquire()
        for o in self.observers.values():
            for filteredEvts in o.evts:
                try:
                    #print("%s gets %d events:"%(str(o.sessionId), len(filteredEvts) ))
                    o.callback(filteredEvts,o.context,self)
                    #print("%s sending %s"%(str(o.context), str(filteredEvts) ))
                except Exception as e:
                    print("EvtProvider: Warning observer callback failed: %s"%(str(e)))
                    traceback.print_exc()
            o.evts.clear()
        self.observerQueueMutex.release()
        