'''
A class managing watched expressions

2024 Bjoern Annighoefer
'''

from .qryrunner import QryRunner
from .change import WatChange

from ..value import VAL, U32, STR, NON, InitValOrNon
from ..query import Qry
from ..error import EOQ_ERROR_DOES_NOT_EXIST, EOQ_ERROR_RUNTIME, EoqErrorAsString
from ..config import Config
from ..serializer import CreateSerializer

from typing import Dict, Tuple, List


class WatchedQuery:
    def __init__(self, wid:int, queryStr:str, query:Qry):
        self.wid = wid
        self.queryStr = queryStr
        self.query = query
        self.watchers:Dict[str,bool] = {} #list of all observers. If the list is empty the query can be removed from the watchlist
        
        
class WatchEvaluationRecord:
    def __init__(self, wid:int):
        self.wid = wid #the id of the query to watch
        self.resultHash = None
        self.errorStr = None #the exception text
        self.evalCounter = 0 #how often was the constraint evaluated
        
class Watcher:
    '''Information on somebody observing a query
    '''
    def __init__(self,sessionId:str):
        self.sessionId = sessionId
        self.watchedQueries:Dict[int,WatchEvaluationRecord] = {}
        


class QueryWatcher:
    '''A class managing watched expressions
    '''
    def __init__(self,qryRunner:QryRunner,config:Config):
        self.qryRunner = qryRunner
        #internals
        self.expressionSerializer = CreateSerializer(config.constraintSerializer)
        self.currentWatchId = 0
        self.allWatchedQueries:Dict[int,WatchedQuery] = {} #watch ID for each unique query
        self.watchers:Dict[str,Watcher] = {} #each watcher is stored with the queries he watches and information about the latest evaluation
        self.superWatchers:Dict[str,Watcher] = {} #super watchers just observe every observed query as well
         
    def WatchQuery(self, queryStr:str, sessionId:str)->int:
        # see if the querry is already known or create a new one
        watchedQuery = next((x for x in self.allWatchedQueries.values() if x.queryStr == queryStr), None)
        if(None == watchedQuery): #create a new entry with new wid
            query = self.expressionSerializer.DesQry(queryStr) #use the same serializer as for constraints
            wid = self.currentWatchId
            watchedQuery = WatchedQuery(wid,queryStr,query)
            self.currentWatchId += 1
            self.allWatchedQueries[wid] = watchedQuery
            self.__AddWatchedQueryToSuperwatchers(wid)
        watchedQuery.watchers[sessionId] = True
        # add the query to the session
        self.__AddWatchedQueryToSession(watchedQuery.wid,sessionId)
        return watchedQuery.wid
    
    def WatchQueryById(self,wid:int,sessionId:str)->None:
        # look if a this wid has attached a query
        if(wid in self.allWatchedQueries):
            watchedQuery = self.allWatchedQueries[wid]
            watchedQuery.watchers[sessionId] = True
        else:
            raise EOQ_ERROR_DOES_NOT_EXIST('Unknown watch ID: %d'%(wid))
        # add the query to the session
        self.__AddWatchedQueryToSession(watchedQuery.wid,sessionId)
    
    def UnwatchQuery(self, queryStr:str, sessionId:str)->int:
        watchedQuery = next((x for x in self.allWatchedQueries.values() if x.queryStr == queryStr), None)
        if(watchedQuery):
            wid = watchedQuery.wid
            if(sessionId in watchedQuery.watchers):
                del watchedQuery.watchers[sessionId]
            self.__RemoveWatchedQueryIfNotWatchedAnyMore(watchedQuery)
            self.__RemoveWatchedQueryFromSession(wid,sessionId)
            return watchedQuery.wid
        else:
            raise EOQ_ERROR_DOES_NOT_EXIST('Unknown query: %s'%(queryStr))
                
    def UnwatchQueryById(self,wid:int,sessionId:str)->int:
        if(wid in self.allWatchedQueries):
            watchedQuery = self.allWatchedQueries[wid]
            if(sessionId in watchedQuery.watchers):
                del watchedQuery.watchers[sessionId]
            self.__RemoveWatchedQueryIfNotWatchedAnyMore(watchedQuery)
            self.__RemoveWatchedQueryFromSession(wid,sessionId)
            return wid
        else:
            raise EOQ_ERROR_DOES_NOT_EXIST('Unknown watch ID: %d'%(wid))
    
    def SuperWatch(self, sessionId:str)->None:
        if(not sessionId in self.superWatchers):
            superWatcher = Watcher(sessionId)
            #evaluate all queries for the superwatcher once
            for w in self.allWatchedQueries:
                superWatcher.watchedQueries[w.wid] = self.__InitEvalRecord(w.wid)
            #add the new superwatcher
            self.superWatchers[sessionId] = superWatcher
                
        
    def SuperUnwatch(self, sessionId:str)->None:
        if(sessionId in self.superWatchers):
            del self.superWatchers[sessionId]
            
    def GetAllWatcherSessionIds(self)->List[str]:
        allWatchingSessions = {w.sessionId:True for w in self.watchers.values()}
        for s in self.superWatchers.values():
            allWatchingSessions[s.sessionId] = True
        return list(allWatchingSessions.keys())
        
    def GetAllWatchChangesForSession(self, sessionId:str)->List[WatChange]:
        '''Evaluates all watched queries for a given sessionId
        WARNING: make sure that the corresponding session is set for the qryrunner,
        before this function is called
        '''
        changes = []
        if(sessionId in self.superWatchers):
            w = self.superWatchers[sessionId]
            changes = self.__GetAllChangesForWatcher(w)
        elif(sessionId in self.watchers): #only evaluate individual watches i not a superwatcher anyway. This prevents any duplicated evaluation
            w = self.watchers[sessionId]
            changes = self.__GetAllChangesForWatcher(w)
        return changes
    
    ### Internals functions
    def __AddWatchedQueryToSession(self,wid:int,sessionId:str)->None:
        watcher = None
        if(sessionId in self.watchers):
            watcher = self.watchers[sessionId]
        else:
            watcher = Watcher(sessionId)
            self.watchers[sessionId] = watcher
        if(not wid in watcher.watchedQueries):
            watcher.watchedQueries[wid] = self.__InitEvalRecord(wid)
            
    def __RemoveWatchedQueryFromSession(self,wid:int,sessionId:str):
        if(sessionId in self.watchers):
            watcher = self.watchers[sessionId]
            if(wid in watcher.watchedQueries):
                del watcher.watchedQueries[wid]
            
    def __EvalWatchedQuery(self, evaluationRecord:WatchEvaluationRecord)->Tuple[VAL,bool]:
        result = NON()
        changed = False
        watchedQuery = self.allWatchedQueries[evaluationRecord.wid] #this is not checked, because the function is only called internally
        try:
            result = self.qryRunner.Eval(watchedQuery.query, None)
            resultHash = result.__hash__()
            changed = (None != evaluationRecord.errorStr or resultHash != evaluationRecord.resultHash)
            evaluationRecord.resultHash = resultHash
            evaluationRecord.errorStr = None #remove the error string, such that the next error will be recognized as change
            evaluationRecord.evalCounter += 1
        except Exception as e:
            errorStr = EoqErrorAsString(EOQ_ERROR_RUNTIME("Evaluation failed: %s"%(str(e))))
            changed = (errorStr != evaluationRecord.errorStr)
            evaluationRecord.errorStr = errorStr
        return result, changed
    
    def __InitEvalRecord(self, wid:int)->WatchEvaluationRecord:
        ''' Initializes the Evaluation record
        WARNING: make sure this happens in the session belonging to the watcher!
        '''
        newRecord = WatchEvaluationRecord(wid)
        #the first time a new evaluation needs to be triggered
        self.__EvalWatchedQuery(newRecord)
        return newRecord
    
    def __RemoveWatchedQueryIfNotWatchedAnyMore(self, watchedQuery:WatchedQuery)->None:
        '''Removes a watchedQuery completely if no watcher watches it explicitly anymore
        '''
        if(0 == len(watchedQuery.watchers)):
            self.__RemoveDeletedWatchedQueryFromSuperwatchers(watchedQuery.wid)
            del self.allWatchedQueries[watchedQuery.wid]
    
    def __AddWatchedQueryToSuperwatchers(self, wid:int)->None:
        '''Removes a deleted watched query from all superwatchers
        A deleted watched query is one not watched explicitly by a non super watcher any more.
        '''
        for s in self.superWatchers.values():
            if(not wid in s.watchedQueries):
                s.watchedQueries[wid] = self.__InitEvalRecord(wid)
    
    def __RemoveDeletedWatchedQueryFromSuperwatchers(self, wid:int)->None:
        '''Removes a deleted watched query from all superwatchers
        A deleted watched query is one not watched explicitly by a non super watcher any more.
        '''
        for s in self.superWatchers.values():
            if(wid in s.watchedQueries):
                del s.watchedQueries[wid]
                
    def __GetAllChangesForWatcher(self, watcher:Watcher)->List[WatChange]:
        ''' Evaluates all queries for a single watcher and returns a WatchEvent for each changed result
        WARNING: make sure the qryrunners session is changed to the watcher beforehand.
        '''
        changes = []
        for wid,evaluationRecord in watcher.watchedQueries.items():
            result, changed = self.__EvalWatchedQuery(evaluationRecord)
            if(changed):
                change = WatChange(U32(wid),result,InitValOrNon(evaluationRecord.errorStr, STR))
                changes.append(change)
        return changes
        
            