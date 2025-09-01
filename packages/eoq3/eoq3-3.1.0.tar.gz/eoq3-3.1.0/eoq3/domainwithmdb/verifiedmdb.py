'''
Access controlled MDB wrapper. Stops if the user is not allowed to do the current action.

 Bjoern Annighoefer 2022
'''

from .session import Session

from ..mdb import Mdb
from ..error import EOQ_ERROR, EOQ_ERROR_UNKNOWN
from ..value import VAL, PRM, I64, STR, NON, LST
from ..query import Obj
from ..verifier import Verifier

#type checking
from typing import Tuple, Union


class VerifiedMdb(Mdb):
    def __init__(self, mdb:Mdb, verifier:Verifier):
        self.__mdb = mdb
        self.verifier = verifier
        self.session = None
        
    def SetSession(self, session:Session):
        '''Before any operation on the mdb, the current session must be set
        '''
        self.session = session
        
    def UnsetSession(self):
        '''Unset the session when the operation is over, to prevent any security breaches
        '''
        self.session = None
        
    def IsAllowedToRead(self, target:Obj, featureName:STR, user:str)->bool:
        ''' Checking read allowance without raising exceptions
        '''
        try:
            self.verifier.ReadPreVerify(target, featureName, NON(), user)
            return True
        except:
            return False
        
    #@Override
    def Create(self, classId:Union[STR,Obj], createArgs:LST=LST([]), target:Obj=NON(), recoveryArgs:LST=LST([]), shallVerify:bool=True, shallNotify=True)->Tuple[Obj,EOQ_ERROR]:
        #pre verification
        if shallVerify: self.verifier.CreatePreVerify(classId, createArgs, target, recoveryArgs, self.session.user)
        #creation
        (res,pmerr) = self.__mdb.Create(classId, createArgs, target, recoveryArgs)
        #post verification
        if(shallVerify and None == pmerr):
            #if operation was successful so far, look for carry out further checking and catch all post modification errors
            try:
                self.verifier.CreatePostVerify(classId, createArgs, res, recoveryArgs, self.session.user)
            except EOQ_ERROR as e:
                pmerr = e #store for later recovery
            except Exception as e:
                pmerr = EOQ_ERROR_UNKNOWN(str(e))
        #notification of successful creation
        if(shallNotify and None == pmerr):
            self.verifier.CreateNotify(classId, createArgs, res, self.session.user)
        return (res,pmerr)
    
    #@Override  
    def Read(self, target:Obj, featureName:STR, context:Obj=NON(), shallVerify:bool=True, shallNotify=True)->VAL:
        if shallVerify: self.verifier.ReadPreVerify(target,featureName,context,self.session.user)
        val = self.__mdb.Read(target,featureName,context)
        if shallVerify:
            val = self.__FilterReturnValue(val)
        #notification of successful read
        if(shallNotify):
            self.verifier.ReadNotify(target, featureName, context, val)
        return val
    
    #@Override
    def Update(self, target:Obj,featureName:STR, value:PRM, position:I64=I64(0), shallVerify:bool=True, shallNotify=True)->Tuple[Obj,Obj,Obj,I64]:
        #pre verification
        if(shallVerify):
            self.verifier.UpdatePreVerify(target, featureName, value, position, self.session.user)
        #actual update
        (oldValue, oldOwner, oldComposition, oldPosition, pmerr) = self.__mdb.Update(target, featureName, value, position)
        #post verification
        if(shallVerify and None == pmerr):
            #if operation was successful so far, look for carry out further checking and catch all post modification errors
            try:
                self.verifier.UpdatePostVerify(target, featureName, value, position, oldValue, self.session.user)
            except EOQ_ERROR as e:
                pmerr = e #store for later recovery
            except Exception as e:
                pmerr = EOQ_ERROR_UNKNOWN(str(e))
        #notification of a successful update
        if(shallNotify and None == pmerr):
            self.verifier.UpdateNotify(target, featureName, value, position, oldValue, self.session.user)
        return (oldValue, oldOwner, oldComposition, oldPosition, pmerr)
            
    
    #@Override
    def Delete(self, target:Obj, shallVerify:bool=True, shallNotify=True)->Tuple[STR,LST,LST]:
        if(shallVerify):
            self.verifier.DeletePreVerify(target, self.session.user)
        (classId, createArgs, recoveryArgs, pmerr) = self.__mdb.Delete(target)
        if(shallVerify and None == pmerr):
            #if operation was successful so far, look for carry out further checking and catch all post modification errors
            try:
                self.verifier.DeletePostVerify(target, classId, createArgs, recoveryArgs, self.session.user)
            except EOQ_ERROR as e:
                pmerr = e #store for later recovery
            except Exception as e:
                pmerr = EOQ_ERROR_UNKNOWN(str(e))
        #notify on successful delete
        if(shallNotify and None == pmerr):
            self.verifier.DeleteNotify(target, classId, createArgs, recoveryArgs, self.session.user)
        return (classId,createArgs,recoveryArgs,pmerr)
        
    #@Override
    def FindElementByIdOrName(self, classNameOrId:STR, context:Obj=NON(), restrictToConcept:STR=NON()) -> LST:
        return LST([c for c in self.__mdb.FindElementByIdOrName(classNameOrId,context,restrictToConcept) if self.IsAllowedToRead(c, NON(), self.session.user)])
    
    ### PRIVATE METHODS ###

    def __FilterReturnValue(self, val:VAL):
        '''Removes all not allowed objects from a list of return values
        '''
        if(LST == type(val)):
            return LST([v for v in val if (not isinstance(v,Obj) or self.IsAllowedToRead(v, NON(), self.session.user))])
        else:
            return val