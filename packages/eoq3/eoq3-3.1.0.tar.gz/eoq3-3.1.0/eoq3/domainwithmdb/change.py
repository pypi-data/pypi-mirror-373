'''
PyEOQ Example: Change.py
----------------------------------------------------------------------------------------
Definition of the record to store local changes in the command runner. 

A change includes precise information about the change in oder to repeat it.
A change includes all information to revert the change.

2022 Bjoern Annighoefer
'''

from ..query import Obj
from ..value import VAL, PRM, BOL, U32, I64, STR, LST

from typing import Union

class Change:
    def __init__(self, postModError:bool=False, timestamp = -1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        self.postModError = postModError
        self.timestamp = timestamp
        self.cid = cid
        self.tid = tid, 
        self.user = user
        self.sessionNumber = sessionNumber
       
        
    def __repr__(self):
        return "%d/%d/%d(%s): %s(%d)"%(self.cid, self.tid, self.postModError, self.timestamp, self.user, self.sessionNumber)
        
class CrtChange(Change):
    def __init__(self, target:Obj, classId:Union[STR,Obj], createArgs:LST \
                 , postModError:bool=False, timestamp = -1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.target = target
        self.classId = classId
        self.createArgs = createArgs
        
    def __repr__(self):
        return super().__repr__()+" CREATE %s %s -> %s"%(self.classId, self.createArgs, self.target)
    
class UpdChange(Change):
    def __init__(self, target:Obj, feature:STR, value:PRM, position:I64, oldValue:PRM, oldOwner:Obj, oldFeature:STR, oldIndex:I64\
                 , postModError:bool=False, timestamp = -1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.target = target
        self.feature = feature
        self.value = value
        self.position = position
        self.oldValue = oldValue
        self.oldOwner = oldOwner
        self.oldFeature = oldFeature
        self.oldIndex = oldIndex
        
    def __repr__(self):
        return super().__repr__()+" UPDATE %s %s %s %s"%(self.target, self.feature, self.value, self.position)
        
class DelChange(Change):
    def __init__(self, target:Obj, classId:Union[STR,Obj], createArgs:LST, recoveryArgs:LST\
                 , postModError:bool=False, timestamp = -1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.target = target
        self.classId = classId
        self.createArgs = createArgs
        self.recoveryArgs = recoveryArgs
        
    def __repr__(self):
        return super().__repr__()+" DELETE %s"%(self.target)
    
    
class ObsChange(Change):
    def __init__(self, evtType:str, evtKey:VAL\
                 , postModError:bool=False, timestamp=-1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.evtType = evtType
        self.evtKey = evtKey
        
    def __repr__(self):
        return super().__repr__()+" OBSERVE %s::%s"%(self.evtType, self.evtKey)
    
class UbsChange(Change):
    def __init__(self, evtType:str, evtKey:VAL, affectedSessionPublicId:str\
                 , postModError:bool=False, timestamp=-1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.evtType = evtType
        self.evtKey = evtKey
        self.affectedSessionPublicId = affectedSessionPublicId #to be stored, because ubs can be caused by other sessions
        
    def __repr__(self):
        return super().__repr__()+" UNOBSERVE %s::%s"%(self.evtType, self.evtKey)
    
class MsgChange(Change):
    def __init__(self, msgKey:STR, msg:STR\
                 , postModError:bool=False, timestamp=-1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.msgKey = msgKey
        self.msg = msg
        
    def __repr__(self):
        return super().__repr__()+" MESSAGE(%s): %s"%(self.msgKey, self.msg)
    
    
class VecChange(Change):
    def __init__(self, target:Obj,  constraint:Obj, isValid:BOL,  error:STR\
                 , postModError:bool=False, timestamp=-1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.target = target
        self.constraint = constraint
        self.isValid = isValid
        self.error = error
        
    def __repr__(self):
        return super().__repr__()+" VERIFICATION CHANGE: %s on %s %s %s"%(self.target, self.constraint, self.isValid, self.error)
    
class WatChange(Change):
    def __init__(self, wid:U32,  result:VAL,  error:STR\
                 , postModError:bool=False, timestamp=-1, cid:int=-1, tid:int=-1, user:str='', sessionNumber:int = -1):
        super().__init__(postModError, timestamp, cid, tid, user, sessionNumber)
        self.wid = wid
        self.result = result
        self.error = error
        
    def __repr__(self):
        return super().__repr__()+" WATCH: %s on %s %s %s"%(self.target, self.constraint, self.isValid, self.error)
