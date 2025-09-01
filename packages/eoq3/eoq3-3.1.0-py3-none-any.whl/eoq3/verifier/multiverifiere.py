'''
This is an verifier implementation that groups multiple verifiers and executes each of their verification and notification functions.

2022 Bjoern Annighoefer

'''


from .verifier import Verifier

from ..value import STR, I64, PRM, VAL, NON, LST
from ..query import Obj
from ..mdb import ReadOnlyMdb

#type checking
from typing import List, Union

class MultiVerifier(Verifier):
    def __init__(self):
        super().__init__()
        self.verifiers:List[Verifier] = []
        
    def AddVerifier(self, v:Verifier)->None:
        self.verifiers.append(v)
        v.Init(self.mdb)
        
    def RemoveVerifier(self, v:Verifier)->None:
        self.verifiers.remove(v)

### INIT AND CLOSE ###
    
    #@Override
    def Init(self, mdb:ReadOnlyMdb)->None:
        super().Init(mdb)
        for v in self.verifiers:
            v.Init(mdb)
    
    #@Override    
    def Deinit(self):
        for v in self.verifiers:
            v.Deinit()
    
    ### PRE VERIFICATION ###
    
    #@Override
    def CreatePreVerify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        for v in self.verifiers:
            v.CreatePreVerify(classId, createArgs, target, recoveryArgs, user)
    
    #@Override
    def ReadPreVerify(self, target:Obj, featureName:STR, context:Obj=NON(), user:str=None)->None:
        for v in self.verifiers:
            v.ReadPreVerify(target, featureName, context, user)
    
    #@Override
    def UpdatePreVerify(self, target:Obj, featureName:STR, value:PRM, position:I64=I64(0), user:str=None)->None:
        for v in self.verifiers:
            v.UpdatePreVerify(target, featureName, value, position, user)
    
    #@Override
    def DeletePreVerify(self, target:Obj, user:str=None)->None:
        for v in self.verifiers:
            v.DeletePreVerify(target, user)
    
    ### POST VERIFICATION ###
    
    #@Override
    def CreatePostVerify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        for v in self.verifiers:
            v.CreatePostVerify(classId, createArgs, target, recoveryArgs, user)
    
    #@Override
    def UpdatePostVerify(self, target:Obj, featureName:STR, value:PRM, position:I64=I64(0), oldValue:PRM=NON(), user:str=None)->None:
        for v in self.verifiers:
            v.UpdatePostVerify(target, featureName, value, position, oldValue, user)
    
    #@Override
    def DeletePostVerify(self, target:Obj, classId:STR, createArgs:LST, recoveryArgs:LST, user:str=None)->None:
        for v in self.verifiers:
            v.DeletePostVerify(target, classId, createArgs, recoveryArgs, user)
    
    
    ### NOTIFIERS ####
    
    #@Override
    def CreateNotify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        for v in self.verifiers:
            v.CreateNotify(classId, createArgs, target, recoveryArgs, user)
    
    #@Override
    def ReadNotify(self, target:Obj, featureName:STR, context:Obj, val:VAL, user:str=None)->None:
        for v in self.verifiers:
            v.ReadNotify(target, featureName, context, val, user)
    
    #@Override
    def UpdateNotify(self, target:Obj, featureName:STR, value:PRM, position:I64, oldValue:PRM, user:str=None)->None:
        for v in self.verifiers:
            v.UpdateNotify(target, featureName, value, position, oldValue, user)
    
    #@Override
    def DeleteNotify(self, target:Obj, classId:STR, createArgs:LST, recoveryArgs:LST, user:str=None)->None:
        for v in self.verifiers:
            v.DeleteNotify(target, classId, createArgs, recoveryArgs, user)