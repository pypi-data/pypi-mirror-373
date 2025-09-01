'''
The interface of the class the does the user verification and access control on element level. 
Different implementations are possible as long as they comply to this interface
This is also the base implementation that does pass all verifications

2022 Bjoern Annighoefer

'''
from ..value import STR, I64, PRM, VAL, NON, LST
from ..query import Obj
from ..mdb import ReadOnlyMdb

from typing import Union

class Verifier:
    def __init__(self):
        self.mdb:ReadOnlyMdb = None
    
    ### INIT AND CLOSE ###
    
    def Init(self, mdb:ReadOnlyMdb)->None:
        '''Initialize the Access controller and tell him the domain he is responsible for
        '''
        self.mdb = mdb
        
    def Deinit(self):
        '''Clean up the access controller
        '''
        pass
    
    ### PRE VERIFICATION ###
    # this functions are called before the data is changed
    
    def CreatePreVerify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        '''Raises an exception if the creation should be stopped
        '''
        pass
    
    def ReadPreVerify(self, target:Obj, featureName:STR, context:Obj=NON(), user:str=None)->None:
        '''Raises an exception if the intended read access should be stopped
        '''
        pass
    
    def UpdatePreVerify(self, target:Obj, featureName:STR, value:PRM, position:I64=I64(0), user:str=None)->None:
        '''Raises an exception if the intended update should be stopped
        '''
        pass
    
    
    def DeletePreVerify(self, target:Obj, user:str=None)->None:
        '''Raises an exception if the intended delete should be stopped
        '''
        pass
    
    ### POST VERIFICATION ###
    # this functions are called after the has changed.
    # if a failure is found here, a rollback of the previous change is necessary
    
    def CreatePostVerify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        '''Raises an exception if the creation needs to be undone.
        '''
        pass
    
#     def ReadPostVerify(self, target:Obj, featureName:STR, context:Obj)->None:
#         '''Raises an exception if the read needs to be undone.
#         '''
#         pass
    
    def UpdatePostVerify(self, target:Obj, featureName:STR, value:PRM, position:I64=I64(0), oldValue:PRM=NON(), user:str=None)->None:
        '''Raises an exception if the update needs to be undone.
        '''
        pass
    
    def DeletePostVerify(self, target:Obj, classId:STR, createArgs:LST, recoveryArgs:LST, user:str=None)->None:
        '''Raises an exception if the deletion needs to be undone.
        '''
        pass
    
    
    ### NOTIFIERS ####
    # Functions that inform the verifier that a certain action took place. 
    # This must not fail or raise exceptions, since all actions have passed pre and post verification beforehand
    
    def CreateNotify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        '''This is a callback informing the access controller that a create took place
        '''
        pass
    
    def ReadNotify(self, target:Obj, featureName:STR, context:Obj, val:VAL, user:str=None)->None:
        '''This is a callback informing the access controller that a read took place
        '''
        pass
    
    def UpdateNotify(self, target:Obj, featureName:STR, value:PRM, position:I64, oldValue:PRM, user:str=None)->None:
        '''This is a callback informing the access controller that an update took place
        '''
        pass
    
    def DeleteNotify(self, target:Obj, classId:STR, createArgs:LST, recoveryArgs:LST, user:str=None)->None:
        '''This is a callback informing the access controller that a deletion took place
        '''
        pass

