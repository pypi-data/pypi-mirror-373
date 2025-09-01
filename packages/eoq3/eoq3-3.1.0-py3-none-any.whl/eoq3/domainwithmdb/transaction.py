'''
 Bjoern Annighoefer 2022
 
'''

from .history import History

class Transaction:
    ''' The class to store the transaction information of one domain interaction.
    
    '''
    def __init__(self,tid:int,roc:bool,cid:int):
        self.tid = tid
        self.roc = roc #is read-only command?
        self.session = None
        self.changes = [] #dictionary which collects changes until the transaction is finished
        self.nRealChanges:int = 0 #collects the number of changes reported to the outside
        self.historyStack = [] #there is always one history on the stack
        self.nextHistory = History() #the next history that is put on the stack. Can be used to initialize values before it becomes active
        self.lastHistory = None #remember the last removed history 
        self.isMuted = False
        self.cid = cid #the change ID of the transaction
        
    def StartHistory(self)->History:
        newHistory = self.nextHistory
        self.historyStack.append(newHistory) #add a new history layer
        self.nextHistory = History() #create a new history for the next call
        return newHistory
        
    def StopHistory(self):
        self.lastHistory = self.historyStack.pop() #remove uppermost history
        
    def GetCurrentHistory(self)->History:
        if(0<len(self.historyStack)):
            return self.historyStack[-1]
        else:
            return None
    
    def GetLastHistory(self)->History:
        return self.lastHistory
    
    def GetNextHistory(self)->History:
        return self.nextHistory