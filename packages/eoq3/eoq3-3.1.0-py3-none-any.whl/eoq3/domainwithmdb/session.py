'''
 Bjoern Annighoefer 2022
 
'''

from ..value import LST
from ..query import Obj

from datetime import datetime

from typing import Tuple, Dict

class Session:
    ''' The class to store the session information when interacting with the domain
    
    '''
    def __init__(self, sessionId:str, sessionIdPublic:str, sessionIdSecret:str, sessionNumber:int):
        self.sessionId = sessionId
        self.sessionIdPublic = sessionIdPublic
        self.sessionIdSecret = sessionIdSecret
        self.sessionNumber = sessionNumber
        self.user = None
        self.begin = datetime.now()
        self.isTemp = False
        #initialize event table
        self.observedEventTypes:Dict[str,bool] = {} #the event types to observe -> bool
        self.superobservedEventTypes:Dict[str,bool] = {} #the event types to observe -> bool
        self.observedElements:Dict[Obj,bool] = {} #stores the elements known by the session
        self.watchedQueries:Dict[int,bool] = {} #stores the keys to watched expressions
        self.observedMessageKeys:Dict[str,bool] = {} #stores all message keys to be observed
        
    ### REGULAR OBSERVATION ###
            
    def ObserveEvent(self,evtType:str)->bool:
        '''Starts listening to this type of events
        Returns: is this a new observation?
        '''
        if(evtType in self.observedEventTypes):
            return False #is already observed
        else:
            self.observedEventTypes[evtType] = True
            return True
        
    def UnobserveEvent(self, evtType:str)->bool:           
        if evtType in self.observedEventTypes:
            del self.observedEventTypes[evtType]
            return True
        else:
            return False
            
    def IsEventObserved(self, evtType:str)->bool:
        if evtType in self.observedEventTypes:
            return True
        else:
            return False
        
    ### SUPER OBSERVATION ###
            
    def SuperobserveEvent(self,evtType:str)->bool:
        '''Starts listening to this type of events
        
        '''
        if(evtType in self.superobservedEventTypes):
            return False #is already observed
        else:
            self.superobservedEventTypes[evtType] = True
            return True
        
    def UnSuperobserveEvent(self, evtType:str)->bool:           
        if evtType in self.superobservedEventTypes:
            del self.superobservedEventTypes[evtType]
            return True
        else:
            return False
            
    def IsEventSuperobserved(self, evtType:str)->bool:
        if evtType in self.superobservedEventTypes:
            return True
        else:
            return False
        
    ### ELEMENT OBSERVATION ###
    
    def ObserveElement(self, elem:Obj)->bool:
        '''Add one element to the observed elements 
        and return if this was new.
        '''
        if(elem in self.observedElements):
            return False
        else:
            self.observedElements[elem] = True 
            return True
        
    def UnobserveElement(self, elem:Obj)->bool:
        if(elem in self.observedElements):
            del self.observedElements[elem] 
            return True
        else:
            return False
        
    def ObserveElements(self, elements:LST)->Tuple[bool,LST]:
        '''Add multiple elements to the observed elements 
        and return if at least one was new 
        and return a list of all new elements.
        '''
        newElements = LST([])
        isChanged = False
        for e in elements:
            if(e not in self.observedElements):
                self.observedElements[e] = True
                newElements.append(e)
                isChanged = True
        return isChanged, newElements
    
    def UnobserveElements(self, elements:LST)->Tuple[bool,LST]:
        '''Remove multiple elements from the observed elements 
        and return if at least one was removed
        and return a list of all removed elements.
        '''
        removedElements = LST([])
        isChanged = False
        for e in elements:
            if(e in self.observedElements):
                del self.observedElements[e]
                removedElements.append(e)
                isChanged = True
        return isChanged, removedElements
            
    def IsElementObserved(self, elem:Obj)->bool:
        return (elem in self.observedElements)
    
    def UnobserveAllElements(self)->Tuple[bool,LST]:
        '''Remove all elements from the observed elements 
        and return if at least one was removed
        and return a list of all removed elements.
        '''
        removedElements = LST([e for e in self.observedElements.keys()])
        self.observedElements.clear()
        isChanged = 0<len(removedElements)
        return isChanged, removedElements
    
    ### QUERY OBSERVATION ###
    
    def ObserveQuery(self, watchId:int)->bool:
        if(watchId in self.watchedQueries):
            return False
        else:
            self.watchedQueries[watchId] = True
            return True
        
    def UnobserveQuery(self, watchId:int)->None:
        if(watchId in self.watchedQueries):
            del self.watchedQueries[watchId]
            return True
        else:
            return False
            
    def ClearObservedQueries(self)->None:
        self.watchedQueries = {}
            
    def IsQueryObserved(self, watchId:int)->bool:
        return (watchId in self.watchedQueries)
    
    def GetWatchedQueryIds(self)->list:
        return [wid for wid in self.watchedQueries.keys()]
    
    ### MEASSAGE OBSERVATION ###
    
    def ObserveMessage(self, msgKey:str)->None:
        if(msgKey in self.observedMessageKeys):
            return False
        else:
            self.observedMessageKeys[msgKey] = True
            return True
        
    def UnobserveMessage(self, msgKey:str)->None:
        if(msgKey in self.observedMessageKeys):
            del self.observedMessageKeys[msgKey]
            return True
        else:
            return False
            
    def IsMessageObserved(self, msgKey:str)->bool:
        return (msgKey in self.observedMessageKeys) 
        
    
    
    