'''
 2019 Bjoern Annighoefer
'''

from ..config import Config
from ..logger import GetLoggerInstance

from ..value import VAL, PRM, BOL, U32, U64, I64, STR, LST, NON, ValidateVal, ValidateValAndCast, InitValOrNon
from ..query import Qry, Obj
from ..command import CMD_TYPES, DEL_MODES, EVT_TYPES, EVT_KEYS, Cmd, Cmp, Err, Res, Evt, CrtEvt, UpdEvt, DelEvt, MsgEvt, VecEvt, WatEvt
from ..error import EOQ_ERROR, EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_RUNTIME, EOQ_ERROR_UNSUPPORTED, EOQ_ERROR_ACCESS_DENIED, EOQ_ERROR_UNKNOWN, EOQ_ERROR_INVALID_OPERATION, EOQ_ERROR_CODES
from ..mdb import Mdb
from ..serializer import Serializer, TextSerializer, CreateSerializer
from ..util import Observable, GenerateSessionId
from ..concepts import CONCEPTS, MXELEMENT, M2CLASS, M2ATTRIBUTE, M2ASSOCIATION, M2COMPOSITION, M2INHERITANCE,\
                       M1MODEL, M1OBJECT, M1ATTRIBUTE, M1ASSOCIATION, M1COMPOSITION,\
                       IsConcept, NormalizeFeatureName 
from ..accesscontroller import AccessController
from ..util import Benchmark, SESSION_ID_LENGTH
from ..verifier import MultiVerifier

from .verifiedmdb import VerifiedMdb
from .constraintverifier import ConstraintVerifier
from .transaction import Transaction
from .session import Session
from .history import History
from .change import Change, CrtChange, UpdChange, DelChange, ObsChange, UbsChange, MsgChange, VecChange, WatChange
from .qryrunner import QryRunner
from .cloner import Cloner
from .deleter import Deleter
from .querywatcher import QueryWatcher
from .util import IsListOfObjects, IsList, IsNoList

from datetime import datetime
from threading import Thread, Event
import traceback

#type checking
from typing import Tuple, Dict, List
from pyecore.ecore import EModelElement


SESSION_SECRET_LEN = 10 #the part of the session id that is the secret

'''
 Cmd Runner
'''   
class CmdRunner(Observable):
    def __init__(self, mdb:Mdb, accessController:AccessController, config:Config):
        super().__init__()
        self.__mdb = mdb
        self.accessController = accessController
        self.config = config
        self.logger = GetLoggerInstance(config)
        self.logSerializer  = CreateSerializer(config.logSerializer)
        #initialize constraint verification
        self.constraintVerifier = ConstraintVerifier(self.config)
        #initialize the verification of the mdb
        self.verifier = MultiVerifier()
        self.verifier.Init(mdb)
        self.verifier.AddVerifier(self.accessController)
        self.verifier.AddVerifier(self.constraintVerifier)
        #wrap the mdb to make sure it is access verified
        self.mdb = VerifiedMdb(mdb,self.verifier)
        #internals
        self.cmdSerializer:Serializer = TextSerializer() #this is used for SCC
        #initialize internals
        self.latestTransactionId = 0
        self.sessionCount = 0
        self.transactions:Dict[int,Transaction] = {}
        #sessions
        self.sessions:Dict[str,Session] = {} #dict containing sessions keys and related session informations
        #changes
        self.earliestChangeId = 1
        self.latestChangeId = 1 # must start at 1 because otherwise -1 is created, which is an invalid change
        self.changes:Dict[int,Change] = {}
        #auxiliary modules
        self.qryRunner = QryRunner(self.mdb,self.config)
        self.deleter = Deleter(self,self.logger)
        self.cloner = Cloner(self,self.logger)
        self.queryWatcher = QueryWatcher(self.qryRunner,self.config) 
        #init command evaluators functor table
        self.cmdEvaluators = {}
        self.cmdEvaluators[CMD_TYPES.GET] = self.ExecGet
        self.cmdEvaluators[CMD_TYPES.UPD] = self.ExecUpd
        self.cmdEvaluators[CMD_TYPES.DEL] = self.ExecDel
        self.cmdEvaluators[CMD_TYPES.SET] = self.ExecSet
        self.cmdEvaluators[CMD_TYPES.ADD] = self.ExecAdd
        self.cmdEvaluators[CMD_TYPES.REM] = self.ExecRem
        self.cmdEvaluators[CMD_TYPES.MOV] = self.ExecMov
        self.cmdEvaluators[CMD_TYPES.CLO] = self.ExecClo
        self.cmdEvaluators[CMD_TYPES.CRT] = self.ExecCrt
        self.cmdEvaluators[CMD_TYPES.STS] = self.ExecSts
        self.cmdEvaluators[CMD_TYPES.HEL] = self.ExecHel
        self.cmdEvaluators[CMD_TYPES.SES] = self.ExecSes
        self.cmdEvaluators[CMD_TYPES.GBY] = self.ExecGby
        self.cmdEvaluators[CMD_TYPES.CHG] = self.ExecChg
        self.cmdEvaluators[CMD_TYPES.OBS] = self.ExecObs
        self.cmdEvaluators[CMD_TYPES.UBS] = self.ExecUbs
        self.cmdEvaluators[CMD_TYPES.MSG] = self.ExecMsg
        self.cmdEvaluators[CMD_TYPES.SCC] = self.ExecScc
        self.cmdEvaluators[CMD_TYPES.VER] = self.ExecVer
        self.cmdEvaluators[CMD_TYPES.GAC] = self.ExecGac
        self.cmdEvaluators[CMD_TYPES.CMP] = self.ExecCmp
        #init read only command (roc) functor evaluator table
        self.rocEvaluators = {}
        self.rocEvaluators[CMD_TYPES.GET] = self.ExecGet
        self.rocEvaluators[CMD_TYPES.CMP] = self.ExecCmp
        
        #custom commands
        self.customCommands = {}
    
        #create annonymous session
        anoSessionId = GenerateSessionId()
        (anoSessionIdPublic,anoSessionIdSecret) = self.__SplitSessionId(anoSessionId)
        self.annonymousSession = self.__CreateNewSession(anoSessionId,anoSessionIdPublic,anoSessionIdSecret)
            
        #benchmark
        if(self.config.enableStatistics):
            self.benchmark = Benchmark()
            allCMD_TYPES = [getattr(CMD_TYPES,k) for k in CMD_TYPES.__dict__ if not k.startswith('_')]
            for t in allCMD_TYPES:
                self.benchmark.InitMessure(t)
                
        if(self.config.evtNotifyAsync):
            #event notification thread
            self.notifyObserverSignal = Event()
            self.shallRun:bool = True
            self.evtNotificationThread:Thread = Thread(target=self.__EventNotificationLoop)
            self.evtNotificationThread.start()

        # merge / diff
        self.oldRoot = None
        self.newRoot = None
        self.postponedMergeReferences = []
        self.diffcommands = []
        self.mDummies = 1
        
    def Close(self):
        self.accessController.Deinit()
        if(self.config.evtNotifyAsync):
            self.shallRun = False
            self.evtNotificationThread.join()
        
    ### DIRECT MDB ACCESS
    # can also be called from the outside if the transaction id is known and valid
    
    def _MdbRead(self, tid:int, target:Obj,featureName:STR, context:Obj=NON()):
        res = self.mdb.Read(target,featureName,context)
        return res
    
    def _MdbCreate(self, tid:int, classId:STR, createArgs:LST=LST([]), target:Obj=NON(), recoveryArgs:LST=LST([])):
        (newElem,pmerr) = self.mdb.Create(classId,createArgs,target,recoveryArgs)
        isPostModError = None != pmerr
        change = CrtChange(newElem,classId,createArgs,isPostModError)
        self.__AddLocalChange(tid,change,True,True)
        if(isPostModError):
            raise pmerr
        return newElem
        
    def _MdbUpdate(self, tid:int, target:Obj, featureName:STR, value:PRM, position:I64=I64(0)):
        (oldVal,oldOwner,oldFeature,oldIndex,pmerr) = self.mdb.Update(target,featureName,value,position)
        isPostModError = None != pmerr
        change = UpdChange(target,featureName,value,position,oldVal,oldOwner,oldFeature,oldIndex,isPostModError) 
        self.__AddLocalChange(tid,change,True,True)
        if(isPostModError):
            raise pmerr
        
    def _MdbDelete(self, tid:int, target:Obj)->Tuple[STR,LST,LST]:
        (classId,createArgs,recoveryArgs,pmerr) = self.mdb.Delete(target)
        isPostModError = None != pmerr
        #create the del change itself
        change = DelChange(target,classId,createArgs,recoveryArgs,isPostModError) 
        self.__AddLocalChange(tid,change,True,True)
        #make sure deleted elements are not observed anymore. This prevents memory leaks. This must happen after the DelChange, because otherwise the change is not send
        self.__UnobserveDeletedElementForAllSessions(tid,target)
        if(isPostModError):
            raise pmerr
        return (classId,createArgs,recoveryArgs)
    
    def _MdbFindElementByNameOrId(self, tid:int, nameOrId:STR, context:Obj=NON(), restrictToConcept:STR=NON()) -> LST:
        res = self.mdb.FindElementByIdOrName(nameOrId, context, restrictToConcept)
        return res
        
    ### COMMAND HANDLERS
    
    def Exec(self, cmd:Cmd, sessionId:str=None, readOnly:bool=False) -> Cmd:
        res = None
        #determine the next transaction ID
        self.latestTransactionId+=1
        tid = self.latestTransactionId
        #run the transaction
        try:
            transaction = self.__StartTransaction(tid,sessionId,readOnly)
            val = self.ExecOnTransaction(cmd,tid,readOnly)
            history = self.__GetTransaction(tid).GetLastHistory()
            if(None!=history):
                (resNames,resNameIndicies) = history.GetValueNamesAndIndicies()
                res = Res(I64(tid),I64(transaction.cid),val,resNames,resNameIndicies)
            else:
                res = Res(I64(tid),I64(transaction.cid),val)
        except EOQ_ERROR as e:
            self.logger.Error("%d: %s"%(e.code,e.msg))
            if self.config.printExpectedExceptionTraces: 
                print("Expected exception trace (Exec):") 
                traceback.print_exc()
            res = Err(e.code,e.msg,e.trace)
        except Exception as e: 
            self.logger.Error("%d: %s"%(EOQ_ERROR_CODES.UNKNOWN,str(e)))
            if self.config.printUnexpectedExceptionTraces: 
                print("Unexpected exception trace (Exec):") 
                traceback.print_exc()
            res = Err(EOQ_ERROR_CODES.UNKNOWN,str(e))
        self.__EndTransaction(res,tid)
        return res
    
    def ExecOnTransaction(self, cmd:Cmd, tid:int, readOnly:bool) -> VAL:
        self.logger.PDebug(lambda : 'Transaction: %d: %s'%(tid,self.logSerializer.SerCmd(cmd)))
        cmdId = cmd.cmd
        val = NON()
        #1. find the routine to evaluate the comand type
        evaluator = None
        try:
            if(readOnly):
                evaluator = self.rocEvaluators[cmdId]
            else:
                evaluator = self.cmdEvaluators[cmdId]
        except KeyError: #it is no built-in command. Maybe a custom command?
            try:
                customCmd = self.customCommands[cmdId]
                evaluator = lambda a,t : self.ExecCus(customCmd,a,t)
            except KeyError:
                raise EOQ_ERROR_UNSUPPORTED("Unknown command type: %s."%(cmdId))
        #2. execute the command and catch potential errors
        if self.config.enableStatistics: self.benchmark.Start()
        try:
            val = evaluator(cmd.a,tid)
        except Exception as e: 
            if self.config.enableStatistics: self.benchmark.Stop(cmdId)
            raise e #forward exception
        if self.config.enableStatistics: self.benchmark.Stop(cmdId)
        #3. return the results
        self.logger.PDebug(lambda: 'Result: %d: %s'%(tid,self.logSerializer.SerVal(val)))
        return val
    
    def ExecCmp(self, args:list, tid:int) -> LST:
        transaction = self.__GetTransaction(tid)
        history = transaction.StartHistory()
        val = []
        n = 0;
        for cmd in args:
            n = n+1;
            try:
                v = self.ExecOnTransaction(cmd, tid, transaction.roc)
                history.AddValue(v,cmd.m,cmd.r)
                if(not cmd.m):
                    val.append(v)
            except EOQ_ERROR as e:
                transaction.StopHistory()
                e.msg = "Subcommand %d (%s): "%(n,cmd.cmd) + e.msg
                raise e
            except Exception as e:
                transaction.StopHistory()
                raise EOQ_ERROR_UNKNOWN("Subcommand %d (%s): %s"%(n,cmd.cmd,str(e)))
        transaction.StopHistory()
        return LST(val)
            
    def ExecGet(self,args,tid:int) -> VAL:
        target = ValidateVal(args[0],[VAL],False)
        history = self.__GetHistory(tid)
        val = self.qryRunner.Eval(target,history)
        return val
    
    def __GetConceptAndFeatureTypeForM1Object(self, tid:int, target:Obj, featureName:STR)->Tuple[STR,Obj]:
        '''Retrieves the concept type and feature element of an M1 object and given feature name
        '''
        normFeatureName = NormalizeFeatureName(featureName.GetVal())
        concept = self._MdbRead(tid, target, STR(MXELEMENT.CONCEPT), NON())
        if(CONCEPTS.M1OBJECT != concept.GetVal()):
            raise EOQ_ERROR_INVALID_OPERATION("%s is no M1OBJECT. Non-native features can only be resolved for M1OBJECTS."%(str(target)))
        clazz = self._MdbRead(tid, target, STR(M1OBJECT.M2CLASS), NON())
        features = self._MdbFindElementByNameOrId(tid,STR(normFeatureName),clazz,NON())
        nFeatures = len(features)
        if(0==nFeatures):
            raise EOQ_ERROR_INVALID_VALUE("%s is no known feature of %s."%(normFeatureName,str(target)))
        elif(1<nFeatures):
            raise EOQ_ERROR_INVALID_VALUE("%s is not unique for %s."%(normFeatureName,str(target))) #this should never happen
        feature = features[0]
        featureConcept = self._MdbRead(tid, feature, STR(MXELEMENT.CONCEPT), NON())
        return (featureConcept,feature)
    
    def __MultiElementModificationHandler(self, tid:int, target:VAL, feature:VAL, value:VAL, position:I64, updateWrapper) -> VAL:
        #set the value(s) depending on the multiplicity of the arguments
        if(IsNoList(target)): # e.g. #20
            if(IsNoList(feature)):
                if(IsNoList(value)):
                    updateWrapper(tid,target,feature,value,position)
                elif(IsList(value)):
                    for v in value:
                        updateWrapper(tid,target,feature,v,position)
                else:
                    raise EOQ_ERROR_INVALID_VALUE('Value must be single value or list of values, but got: %s:'%(value)) 
            elif(IsListOfObjects(feature)):
                if(IsNoList(value)):
                    for f in feature:
                        updateWrapper(tid,target,f,value,position)
                elif(IsListOfObjects(value) and len(value) == len(feature)):
                    for i in range(len(feature)):
                        if(IsNoList(value[i])):
                            updateWrapper(tid,target,feature[i],value[i],position)
                        elif(IsListOfObjects(value[i])):
                            for v in value[i]:
                                updateWrapper(tid,target,feature[i],v,position)
                        else:
                            raise EOQ_ERROR_INVALID_VALUE('For multiple features the value must be a list of list of objects for each feature, but entry %d is %s.'%(i,value[i]))
                else:
                    raise EOQ_ERROR_INVALID_VALUE('Value must be single value or list of list of values with outer list having a length equal to the number of features, but got: %s:'%(value)) 
            else:
                raise EOQ_ERROR_INVALID_VALUE('Feature must be single object or list of objects but got: %s:'%(feature)) 
        elif(IsListOfObjects(target)): # e.g. [#20,#22,#23]
            if(IsNoList(feature)):
                if(IsNoList(value)):
                    for t in target:
                        updateWrapper(tid,t,feature,value,position)
                elif(IsList(value) and len(value) == len(target)):
                    for j in range(len(target)):
                        if(IsListOfObjects(value[j])):
                            for i in range(len(value[j])):
                                updateWrapper(tid,target[j],feature,value[j][i],position)
                        else:
                            updateWrapper(tid,target[j],feature,value[j],position) #TODO is that OK
                            #raise EOQ_ERROR_INVALID_VALUE('For multiple targets the value must be a list of list of objects for each target, but entry %d is %s.'%(j,value[j]))
                else:
                    raise EOQ_ERROR_INVALID_VALUE('Value must be single value or list of values with equal length of the number of targets, but got: %s:'%(value)) 
            elif(IsListOfObjects(feature)):
                if(IsNoList(value)):
                    for t in target:
                        for f in feature:
                            updateWrapper(tid,t,f,value,position)
                elif(IsListOfObjects(value) and len(value) == len(feature)):
                    for t in target:
                        for i in range(len(feature)):
                            updateWrapper(tid,t,feature[i],value[i],position)
                elif(IsList(value) and len(value) == len(target)):
                    for j in range(len(target)):
                        if(IsListOfObjects(value[j]) and len(value[j]) == len(feature)):
                            for i in range(len(feature)):
                                updateWrapper(tid,target[j],feature[i],value[j][i],position)
                        elif(IsList(value[j]) and len(value[j]) == len(feature)):
                            for i in range(len(feature)):
                                if(IsList(value[j][i])):
                                    for v in value[j][i]:
                                        updateWrapper(tid,target[j],feature[i],v,position)
                                else:
                                    raise EOQ_ERROR_INVALID_VALUE('For multiple targets, multiple features and multiple values value must list equal to targets containing a list equal to features containing a list of values, but got %s for target %d and feature %d.'%(value[j][i],j,i)) 
                        else:
                            raise EOQ_ERROR_INVALID_VALUE('For multiple targets and multiple features the value for each entry must have the same length as the number of features. Expected %d entries for target %d, but got %s.'%(len(feature),j,value[j]))
                else:
                    raise EOQ_ERROR_INVALID_VALUE('Value must be single value or list of list of list of values with outer list having a length equal to the number of targets and the middle list with a length equal to the number of features, but got: %s:'%(value)) 
            else:
                raise EOQ_ERROR_INVALID_VALUE('Feature must be single object or list of objects but got: %s:'%(feature)) 
        else: 
            raise EOQ_ERROR_INVALID_VALUE('Target must be single object or list of objects but got: %s:'%(target))
    
    
    def __UpdUpdateWrapper(self, tid:int, target:Obj, featureName:STR, value:PRM, position:I64) -> None:
        self._MdbUpdate(tid, target, featureName, value, position)
        
    def __SetUpdateWrapper(self, tid:int, target:Obj, featureName:STR, value:PRM, position:I64) -> None:
        if(IsConcept(featureName.GetVal())):
            self._MdbUpdate(tid, target, featureName, value, position)
        else:
            (concept,feature) = self.__GetConceptAndFeatureTypeForM1Object(tid,target,featureName)
            if(CONCEPTS.M2ATTRIBUTE == concept):
                #check whether the attribute does already exist
                attrInstance = self._MdbRead(tid, target, STR(M1OBJECT.FEATUREINSTANCES+featureName.GetVal()))
                if(0<len(attrInstance)):
                    self._MdbUpdate(tid, attrInstance[0], STR(M1ATTRIBUTE.VALUE), value)
                else:
                    self._MdbCreate(tid, STR(CONCEPTS.M1ATTRIBUTE), LST([feature,target,value]))
            elif(CONCEPTS.M2ASSOCIATION == concept):
                self._MdbCreate(tid, STR(CONCEPTS.M1ASSOCIATION), LST([feature,target,value]))
            elif(CONCEPTS.M2COMPOSITION == concept):
                self._MdbCreate(tid, STR(CONCEPTS.M1COMPOSITION), LST([feature,target,value]))
            else:
                raise EOQ_ERROR_RUNTIME("Do not know how to add for feature %s for concept type %s."%(featureName,concept))
        
    def __AddUpdateWrapper(self, tid:int, target:Obj, featureName:STR, value:PRM, position:I64) -> None:
        if(IsConcept(featureName.GetVal())):
            self._MdbUpdate(tid, target, featureName, value, position)
        else:
            (concept,feature) = self.__GetConceptAndFeatureTypeForM1Object(tid,target,featureName)
            if(CONCEPTS.M2ATTRIBUTE == concept):
                self._MdbCreate(tid, STR(CONCEPTS.M1ATTRIBUTE), LST([feature,target,value]))
            elif(CONCEPTS.M2ASSOCIATION == concept):
                self._MdbCreate(tid, STR(CONCEPTS.M1ASSOCIATION), LST([feature,target,value]))
            elif(CONCEPTS.M2COMPOSITION == concept):
                self._MdbCreate(tid, STR(CONCEPTS.M1COMPOSITION), LST([feature,target,value]))
            else:
                raise EOQ_ERROR_RUNTIME("Do not know how to add for feature %s for concept type %s."%(featureName,concept))
        
    def __RemUpdateWrapper(self, tid:int, target:Obj, featureName:STR, value:PRM, position:I64) -> None:
        #position is never used, because it is determined from the value
        if(IsConcept(featureName.GetVal())):
            position = I64(self.mdb.Read(target,featureName).index(value))
            self._MdbUpdate(tid,target, featureName, NON(), position)
        else:
            (concept,feature) = self.__GetConceptAndFeatureTypeForM1Object(tid,target,featureName)
            self._MdbDelete(tid,feature)
    
    def ExecUpd(self, args:list, tid:int) -> LST:
        #eval all arguments
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj,LST],'target')
        feature = ValidateVal(self.qryRunner.Eval(args[1],history),[STR,LST],'feature')
        value = ValidateVal(self.qryRunner.Eval(args[2],history),[VAL],'value',False)
        position = ValidateValAndCast(self.qryRunner.Eval(args[3],history),[I64],'position')
        # delegate to multi element modification
        self.__MultiElementModificationHandler(tid, target, feature, value, position, self.__UpdUpdateWrapper)
        val = LST([target,feature,position,value])
        return val
    
   
    
    def _Delete(self, target:Obj, mode:STR, tid:int)->Tuple[STR,LST,LST]:
        res = None
        if(DEL_MODES.BAS == mode):
            res = self._MdbDelete(tid,target)
        elif(DEL_MODES.AUT == mode):
            res = self.deleter.DeleteAuto(target, tid)
        elif(DEL_MODES.FUL == mode):
            res = self.deleter.DeleteFull(target, tid)
        else:
            EOQ_ERROR_INVALID_VALUE('Mode %s is not valid:'%(mode))
        return res
            
            
    def ExecDel(self, args:list, tid:int) -> LST:
        #eval all arguments
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj,LST],'target')
        mode = ValidateValAndCast(self.qryRunner.Eval(args[1],history),[STR],'mode')
        res = LST([])
        if(IsListOfObjects(target)):
            for t in target:
                (conceptId,createArgs,recoveryArgs) = self._Delete(t, mode, tid)
                res.append(LST([conceptId,createArgs,recoveryArgs]))
        elif(isinstance(target,Qry)):
            (conceptId,createArgs,recoveryArgs) = self._Delete(target, mode, tid)
            res = LST([conceptId,createArgs,recoveryArgs])
        else:
            raise EOQ_ERROR_INVALID_VALUE('Target must be single object or list of objects but got: %s:'%(target))
        
        return res    
    
    
    def ExecSet(self, args:list, tid:int) -> LST:
        #eval all arguments
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj,LST],'target')
        feature = ValidateVal(self.qryRunner.Eval(args[1],history),[STR,LST],'feature')
        value = self.qryRunner.Eval(args[2],history)
        # delelgate to multi element modification
        self.__MultiElementModificationHandler(tid, target, feature, value, I64(0), self.__SetUpdateWrapper)
        val = LST([target,feature,value])
        return val
    

    def ExecAdd(self, args:list, tid:int) -> LST:
        #eval all arguments
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj,LST],'target')
        feature = ValidateVal(self.qryRunner.Eval(args[1],history),[STR,LST],'feature')
        value = self.qryRunner.Eval(args[2],history)
        # delelgate to multi element modification
        self.__MultiElementModificationHandler(tid, target, feature, value, I64(-1), self.__AddUpdateWrapper)
        val = LST([target,feature,value])
        return val
    
    def ExecRem(self, args:list, tid:int) -> LST:
        # DEPRICATED
        self.__DeprecatedWarning("REM")
        #eval all arguments
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj,LST],'target')
        feature = ValidateVal(self.qryRunner.Eval(args[1],history),[STR,LST],'feature')
        value = ValidateVal(self.qryRunner.Eval(args[2],history),[VAL],'value',False)
        # delelgate to multi element modification
        self.__MultiElementModificationHandler(tid, target, feature, value, NON(), self.__RemUpdateWrapper)
        val = LST([target,feature,value])
        return val
    
    def __MovUpdateWrapper(self, target:Obj, feature:STR, value:PRM, position:U64 ,tid:int) -> None:
        # TODO
        parent = self.mdb.Read(value,STR(M1OBJECT.PARENT))
        featureName = self.mdb.Read(parent[1],STR(M2COMPOSITION.NAME))
        self._MdbUpdate(tid,parent[0], featureName, value, -(I64(position)+I64(2)))
    
    def ExecMov(self, args:list, tid:int) -> LST:
        # DEPRICATED
        self.__DeprecatedWarning("MOV")
        #eval all arguments
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj,LST],'target')
        newIndex = ValidateValAndCast(self.qryRunner.Eval(args[1],history),[U64],'newIndex')
        
        #set the value(s) depending on the multiplicity of the arguments
        if(IsNoList(target)): # e.g. #20
            self.__MovUpdateWrapper(NON(),NON(),target,newIndex,tid)
        elif(IsListOfObjects(target)): # e.g. [#20,#22,#23]
            for t in target:
                self.__MovUpdateWrapper(NON(),NON(),t,newIndex,tid)
        else:
            raise EOQ_ERROR_INVALID_VALUE('Target must Obj or LST of Obj but got: %s:'%(target))
        
        val = LST([target,newIndex])
        return val
    
    
    def ExecClo(self, args:list, tid:int) -> VAL:
        #res = None  
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[Obj],'target')
        mode = ValidateValAndCast(self.qryRunner.Eval(args[1],history),[STR],'mode')
        createArgOverrides = ValidateValAndCast(self.qryRunner.Eval(args[2],history),[LST],'createArgOverrides')
        val = self.cloner.Clone(target,mode,createArgOverrides,tid)
        return val
    
    
    def ExecCrt(self, args:list, tid:int) -> VAL:
        res = NON()  
        history = self.__GetHistory(tid)
        classId = ValidateVal(self.qryRunner.Eval(args[0],history),[STR,Obj],'classId')
        n = ValidateValAndCast(self.qryRunner.Eval(args[1],history),[U32],"n").GetVal()
        createArgs = ValidateValAndCast(self.qryRunner.Eval(args[2],history),[NON,LST],"createArgs")
        target = ValidateValAndCast(self.qryRunner.Eval(args[3],history),[NON,Obj,LST],"target")
        recoveryArgs = ValidateValAndCast(self.qryRunner.Eval(args[4],history),[NON,LST],"createArgs")
        if n == 1:
            res = self._MdbCreate(tid,classId, createArgs, target, recoveryArgs)
        elif(IsListOfObjects(createArgs)):
            res = LST()
            for i in range(n):
                elem = self._MdbCreate(tid, classId, createArgs) #cannot use recovery here
                res.append(elem)
        elif(LST==type(createArgs) and n==len(createArgs)): #n > U32(1)
            res = LST()
            for i in range(n):
                elem = self._MdbCreate(tid, classId, createArgs[i]) #cannot use recovery here
                res.append(elem)
        elif(LST==type(createArgs) and 0==len(createArgs)): #n > U32(1)
            res = LST()
            for i in range(n):
                elem = self._MdbCreate(tid, classId) #cannot use recovery here
                res.append(elem)
        else:
            raise EOQ_ERROR_INVALID_VALUE("There must be exactly as many individual createArgs arrays as the number of elements to be created.")
        return res
    
    def ExecHel(self, args:list, tid:int) -> STR:
        transaction = self.__GetTransaction(tid)
        user = ValidateValAndCast(args[0],[STR],'user').GetVal()
        password = ValidateValAndCast(args[1],[STR],'password').GetVal()
        #prepare a new session
        #sessionId = None
        #check identification
        if(self.annonymousSession == transaction.session):
            raise EOQ_ERROR_ACCESS_DENIED('Cannot login on anonymous session. Please provide session ID.')
        if(self.accessController.AuthenticateUser(user, password)):
            session = transaction.session
            session.user = user
        else:
            raise EOQ_ERROR_ACCESS_DENIED('Identification failed.')
        val = BOL(True)
        return val
    
    def ExecSes(self, args:list, tid:int):
        transaction = self.__GetTransaction(tid)
        sessionId = ValidateValAndCast(args[0],[STR],'sessionId').GetVal() 
        (sessionIdPublic,sessionIdSecret) = self.__SplitSessionId(sessionId)
        try:
            session = self.sessions[sessionIdPublic]
            if(sessionIdSecret != session.sessionIdSecret):
                raise EOQ_ERROR_INVALID_VALUE('Unknown session %s'%(sessionId))
            transaction.session = session
            self.mdb.SetSession(session)
        except KeyError:
            raise EOQ_ERROR_INVALID_VALUE('Unknown session %s'%(sessionId))
        val = BOL(True)
        return val
    
    def ExecGby(self, args:list, tid:int) -> BOL:
        transaction = self.__GetTransaction(tid)
        session = transaction.session
        if(self.annonymousSession == session):
            raise EOQ_ERROR_ACCESS_DENIED("Unknown session.")
        session = self.sessions[session.sessionIdPublic]
        self.sessions.pop(session.sessionIdPublic) #delete the session
        transaction.session = None #remove any eventual remaining reference to the session
        val = BOL(True)
        return val
    
    def ExecSts(self, args:list, tid:int) -> U64:
        val = U64(self.latestChangeId-1) #latest the latest change is one below the indication
        return val
    
    def ExecChg(self, args:list, tid:int) -> LST:
        history = self.__GetHistory(tid)
        changeId = ValidateValAndCast(self.qryRunner.Eval(args[0],history),[U64],'changeId').GetVal()
        n = ValidateValAndCast(self.qryRunner.Eval(args[1],history),[U64],'n').GetVal()
        #sanity check
        if(n<0):
            raise EOQ_ERROR_INVALID_VALUE("Index must be greater or equal zero, but got: %d"%(n))
        val = NON()
        if(changeId<self.earliestChangeId):
            if(n==0 or changeId+n >= self.latestChangeId): 
                val = LST([self.__ChangeToChangeRecord(self.changes[i]) for i in range(self.earliestChangeId,self.latestChangeId)])
            elif(changeId+n >= self.earliestChangeId):
                val = LST([self.__ChangeToChangeRecord(self.changes[i]) for i in range(self.earliestChangeId,changeId+n)])
            else: 
                val = LST()
        elif(changeId >= self.latestChangeId):
            val = LST()
        else: #is a valid change id
            if(n==0 or changeId+n >= self.latestChangeId):
                val = LST([self.__ChangeToChangeRecord(self.changes[i]) for i in range(changeId,self.latestChangeId)])
            else:
                val = LST([self.__ChangeToChangeRecord(self.changes[i]) for i in range(changeId,changeId+n)])
        return val
    
    def ExecObs(self, args:list, tid:int) -> BOL: 
        transaction = self.__GetTransaction(tid)
        history = transaction.GetCurrentHistory()
        evtType = ValidateValAndCast(self.qryRunner.Eval(args[0],history),[STR],'evtType').GetVal() #everything must be string
        evtKeyUnchecked = self.qryRunner.Eval(args[1],history)
        #check is session is known
        if(not transaction.session):
            raise EOQ_ERROR_RUNTIME('Must specify session when observing events.')
        session = transaction.session
        (evtKeyChecked, val, isChanged) = self.__Obs(evtType, evtKeyUnchecked, history, session)
        #add to changes for making this undoable
        if(isChanged):
            self.__AddLocalChange(tid, ObsChange(evtType,evtKeyChecked),False,False)
        #return always true 
        return val
    
    def __Obs(self, evtType:str, evtKeyUnchecked:VAL, history:History, session:Session)->(VAL,VAL,bool):
        val = BOL(True)
        evtKey = evtKeyUnchecked
        isChanged = False
        #decide based on the event type what to do
        if(EVT_TYPES.ELM == evtType):
            evtKey = ValidateValAndCast(self.qryRunner.Eval(evtKeyUnchecked,history),[LST,Obj],'evtKey')
            if(isinstance(evtKey,Obj)):
                isChanged = session.ObserveElement(evtKey)
            elif(LST == type(evtKey)):
                if(IsListOfObjects(evtKey)):
                    isChanged, evtKey = session.ObserveElements(evtKey)
                else:
                    raise EOQ_ERROR_INVALID_VALUE("Multiple elements to be observed must be given as a flat list of objects.")
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        elif(EVT_TYPES.CRT == evtType or\
             EVT_TYPES.UPD == evtType or\
             EVT_TYPES.DEL == evtType or\
             EVT_TYPES.VEC == evtType):
            evtKey = ValidateValAndCast(self.qryRunner.Eval(evtKeyUnchecked,history),[STR,NON],'evtKey')
            if(evtKey.IsNone()):
                isChanged = session.ObserveEvent(evtType)
            elif(STR == type(evtKey) and EVT_KEYS.ALL == evtKey.GetVal()):
                if(self.accessController.IsAllowedToSuperobserve(session.user, evtType)):
                    isChanged = session.SuperobserveEvent(evtType)
                else:
                    raise EOQ_ERROR_ACCESS_DENIED('Not allowed to superobserve %s'%(evtType))
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        elif(EVT_TYPES.WAT == evtType):
            evtKey = ValidateValAndCast(evtKeyUnchecked,[STR,U32,NON],'evtKey')
            if(evtKey.IsNone()): #enable observation
                isChanged = session.ObserveEvent(evtType)
            elif(U32 == type(evtKey)):
                wid = evtKey.GetVal()
                self.queryWatcher.WatchQueryById(wid, session.sessionIdPublic)
                isChanged = session.ObserveQuery(wid)
            elif(STR == type(evtKey)):
                if(EVT_KEYS.ALL == evtKey.GetVal()): #enable superobservation
                    if(self.accessController.IsAllowedToSuperobserve(session.user, evtType)):
                        self.queryWatcher.SuperWatch(session.sessionIdPublic)
                        isChanged = session.SuperobserveEvent(evtType)
                    else:
                        raise EOQ_ERROR_ACCESS_DENIED('Not allowed to superobserve %s'%(evtType))
                else: #watch a normal query
                    if(self.accessController.IsAllowedToObserve(session.user, evtType)):
                        wid = self.queryWatcher.WatchQuery(evtKey.GetVal(), session.sessionIdPublic)
                        isChanged = session.ObserveQuery(wid)
                        val = U32(wid) #return watch id
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        elif(EVT_TYPES.MSG == evtType):
            evtKey = ValidateValAndCast(self.qryRunner.Eval(evtKeyUnchecked,history),[STR,NON],'evtKey')
            if(evtKey.IsNone()): #enable MSG observation
                isChanged = session.ObserveEvent(evtType)
            elif(STR == type(evtKey) and EVT_KEYS.ALL == evtKey.GetVal()): #enable super observation
                if(self.accessController.IsAllowedToSuperobserve(session.user, evtType)):
                    isChanged = session.SuperobserveEvent(evtType)
                else:
                    raise EOQ_ERROR_ACCESS_DENIED('Not allowed to superobserve %s'%(evtType))
            elif(STR == type(evtKey)): #set the event key and observe
                isChanged = session.ObserveMessage(evtKey)
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        else:
            raise EOQ_ERROR_UNSUPPORTED('Unknown event type: %s'%(evtType)) 
        return (evtKey,val,isChanged)
    
    def ExecUbs(self, args:list, tid:int) -> BOL: 
        transaction = self.__GetTransaction(tid)
        history = transaction.GetCurrentHistory()
        evtType = ValidateValAndCast(self.qryRunner.Eval(args[0],history),[STR],'evtType').GetVal() #everything must be string
        evtKeyUnchecked = args[1]
        #check is session is known
        if(not transaction.session):
            raise EOQ_ERROR_RUNTIME('Must specify session when unobserving events.')
        session = transaction.session
        (evtKey,val,isChanged) = self.__Ubs(evtType, evtKeyUnchecked, history, session)
        #add to changes for making this undoable
        if(isChanged):
            self.__AddLocalChange(tid, UbsChange(evtType,evtKey,session.sessionIdPublic),False,False)
        return val
    
    def __Ubs(self, evtType:str, evtKeyUnchecked:VAL, history:History, session:Session)->(VAL,VAL,bool):
        val = BOL(True)
        evtKey = evtKeyUnchecked
        isChanged = False
        #decide based on the event type what to do
        if(EVT_TYPES.ELM == evtType):
            evtKey = ValidateValAndCast(self.qryRunner.Eval(evtKeyUnchecked,history),[LST,NON,Obj],'evtKey')  #Obj must be last in row, because it has no construction check
            if(isinstance(evtKey,Obj)):
                isChanged = session.UnobserveElement(evtKey)
            elif(LST == type(evtKey)):
                if(IsListOfObjects(evtKey)):
                    isChanged, evtKey = session.UnobserveElements(evtKey)
                else:
                    raise EOQ_ERROR_INVALID_VALUE("Multiple objects to be observed must be given as a flat list of objects.")
            elif(evtKey.IsNone()):
                isChanged, evtKey = session.UnobserveAllElements()
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        elif(EVT_TYPES.CRT == evtType or\
            EVT_TYPES.UPD == evtType or\
             EVT_TYPES.DEL == evtType or\
             EVT_TYPES.VEC == evtType):
            evtKey = ValidateValAndCast(self.qryRunner.Eval(evtKeyUnchecked,history),[STR,NON],'evtKey')
            if(evtKey.IsNone()):
                isChanged = session.UnobserveEvent(evtType)
            elif(STR == type(evtKey) and EVT_KEYS.ALL == evtKey.GetVal()):
                isChanged = session.UnSuperobserveEvent(evtType)
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        elif(EVT_TYPES.WAT == evtType):
            evtKey = ValidateValAndCast(evtKeyUnchecked,[STR,U32,NON],'evtKey')
            if(evtKey.IsNone()): #enable observation
                isChanged = session.UnobserveEvent(evtType)
            elif(U32 == type(evtKey)):
                wid = evtKey.GetVal()
                self.queryWatcher.UnwatchQueryById(wid,session.sessionIdPublic)
                isChanged = session.UnobserveQuery(wid)
            elif(STR == type(evtKey)):
                if(EVT_KEYS.ALL == evtKey.GetVal()): #enable superobservation
                    self.queryWatcher.SuperUnwatch(session.sessionIdPublic)
                    isChanged = session.UnSuperobserveEvent(evtType)
                else:
                    wid = self.queryWatcher.UnwatchQuery(evtKey.GetVal(),session.sessionIdPublic)
                    if(0 <= wid): #otherwise the query was never watched
                        isChanged = session.UnobserveQuery(wid)
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        elif(EVT_TYPES.MSG == evtType):
            evtKey = ValidateValAndCast(self.qryRunner.Eval(evtKeyUnchecked,history),[STR,NON],'evtKey')
            if(evtKey.IsNone()): #enable MSG observation
                isChanged = session.UnobserveEvent(evtType)
            elif(STR == type(evtKey) and EVT_KEYS.ALL == evtKey.GetVal()): #enable super observation
                isChanged = session.UnSuperobserveEvent(evtType)
            elif(STR == type(evtKey)): #set the event key and observe
                isChanged = session.UnobserveMessage(evtKey)
            else:
                raise EOQ_ERROR_INVALID_VALUE("Unexpected event key: %s"%(evtKey))
        else:
            raise EOQ_ERROR_UNSUPPORTED('Unknown event type: %s'%(evtType)) 
        return (evtKey,val,isChanged)
    
    def ExecMsg(self, args:list, tid:int) -> BOL: 
        transaction = self.__GetTransaction(tid)
        history = transaction.GetCurrentHistory()
        msgKey = ValidateValAndCast(self.qryRunner.Eval(args[0],history),[STR],'msgKey') # must be string
        msg = ValidateValAndCast(self.qryRunner.Eval(args[1],history),[STR],'msg') # must be string
        self.__SendMessage(msgKey, msg, tid) #mark message for being sent
        val = BOL(True)
        return val
    
    def ExecScc(self, args:list, tid:int) -> BOL: 
        cmdId = ValidateValAndCast(args[0],[STR],'cmdId').GetVal() #everything must be string
        cmdStr = ValidateValAndCast(args[1],[STR, NON],'cmdStr').GetVal() #everything must be string
        #validate cmd form
        if(3 != len(cmdId) or (cmdId.upper() != cmdId)):
            raise EOQ_ERROR_INVALID_VALUE("cmdId must be 3 letter caps.")
        #see if the cmdId does already exist
        if(cmdId in self.cmdEvaluators):
            raise EOQ_ERROR_INVALID_VALUE("%s is reserved. Cannot set."%(cmdId))
        #try parsing the cmdStr in a command
        if(None == cmdStr): #remove the custom command
            if(cmdId in self.customCommands):
                del self.customCommands[cmdId]
        else: #register a new custom command
            try:
                cmd = self.cmdSerializer.DesCmd(cmdStr)
                #make sure the custom command is a compound command, because otherwise the history does not work
                if(not isinstance(cmd,Cmp)):
                    cmd = Cmp().Append(cmd)
                #check for recursions
                self.__PreventRecursion(cmd,cmdId)
                self.customCommands[cmdId] = cmd
            except Exception as e:
                raise EOQ_ERROR_INVALID_VALUE("Parsing cmdStr failed: %s"%(str(e)))
        val = BOL(True)
        return val

    def ExecVer(self, args:list, tid:int): 
        ''' Evaluates all constraints for a given target
        Returns:
        - [[constraint:Obj, isValid:BOL, exception:STR, changed:BOL],[...],...]
        '''
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[LST,Obj],'target')
        evaluationChangedEvents = []
        if(isinstance(target,Obj)):
            res = self.__VerifiyAllConstraintsForTarget(target)
            self.__GenerateVerificationChangeEvents(target,res,tid)
        else:
            if(not IsListOfObjects(target)):
                raise EOQ_ERROR_INVALID_VALUE("Requires Obj or LST<Obj>.")
            res = LST([])
            for t in target:
                r = self.__VerifiyAllConstraintsForTarget(t)
                self.__GenerateVerificationChangeEvents(t,r,tid)
                res.append(r)
        return res
    
    def __VerifiyAllConstraintsForTarget(self, target:Obj)->LST:
        allConstraints = self.__GetAllConstraintsRaw(target)
        # evaluate all applicable constraints
        verificationRecords = LST([])
        for c in allConstraints:
            valid,exception,changed = self.constraintVerifier.EvalConstraint(c, target)
            verificationRecords.append( LST([c,BOL(valid),STR(exception) if str==type(exception) else NON(),BOL(changed)]) )
        return verificationRecords
    
    def __GenerateVerificationChangeEvents(self, target:Obj, verificationRecords:LST,tid:int)->None:
        for r in verificationRecords:
            if(r[3].GetVal()==True): # is changed
                self.__AddLocalChange(tid, VecChange(target,r[0],r[1],r[2]),False,True)

    def ExecGac(self, args:list, tid:int): 
        ''' Retrieves all constraints applicable for a given target
        Returns:
        - [constraint1:Obj, ...]
        '''
        res = NON()
        history = self.__GetHistory(tid)
        target = ValidateVal(self.qryRunner.Eval(args[0],history),[LST,Obj],'target')
        if(isinstance(target,Obj)):
            res = LST(self.__GetAllConstraintsRaw(target))
        else:
            if(not IsListOfObjects(target)):
                raise EOQ_ERROR_INVALID_VALUE("Requires Obj or LST<Obj>.")
            res = LST([ LST(self.__GetAllConstraintsRaw(o)) for o in target])
        return res
        


    def __GetAllConstraintsRaw(self, target:Obj)->List[Obj]:
        '''Get all constraints applicable for the target.
        retrieve any inherited constraints, this is special for each concept type
        '''
        allConstraints = []
        concept = self.mdb.Read(target,STR(MXELEMENT.CONCEPT)).GetVal()
        # Currently no constraints applicable to M2 are defined
        # Constraints on M1 level are either direct of inherited from M1
        if(CONCEPTS.M1MODEL==concept):
            ownConstraints = self.mdb.Read(target,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += ownConstraints.GetVal()
            #check the m2model
            m2Model = self.mdb.Read(target,STR(M1MODEL.M2MODEL))
            inheritConstraints = self.mdb.Read(m2Model,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += inheritConstraints.GetVal()
        elif(CONCEPTS.M1OBJECT==concept):
            ownConstraints = self.mdb.Read(target,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += ownConstraints.GetVal()
            clazz = self.mdb.Read(target,STR(M1OBJECT.M2CLASS))
            classConstraints = self.mdb.Read(clazz,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += classConstraints.GetVal()
            #check all superclasses
            generalizations = self.mdb.Read(clazz,STR(M2CLASS.GENERALIZATIONS))
            for g in generalizations:
                clazz = self.mdb.Read(g,STR(M2INHERITANCE.SUPERCLASS))
                classConstraints = self.mdb.Read(clazz,STR(MXELEMENT.CONSTRAINTS))
                allConstraints += classConstraints.GetVal()
        elif(CONCEPTS.M1ATTRIBUTE==concept):
            ownConstraints = self.mdb.Read(target,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += ownConstraints.GetVal()
            m2Definition = self.mdb.Read(target,STR(M1ATTRIBUTE.M2ATTRIBUTE))
            inheritConstraints = self.mdb.Read(m2Definition,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += inheritConstraints.GetVal()
        elif(CONCEPTS.M1ASSOCIATION==concept):
            ownConstraints = self.mdb.Read(target,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += ownConstraints.GetVal()
            m2Definition = self.mdb.Read(target,STR(M1ASSOCIATION.M2ASSOCIATION))
            inheritConstraints = self.mdb.Read(m2Definition,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += inheritConstraints.GetVal()
        elif(CONCEPTS.M1COMPOSITION==concept):
            ownConstraints = self.mdb.Read(target,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += ownConstraints.GetVal()
            m2Definition = self.mdb.Read(target,STR(M1COMPOSITION.M2COMPOSITION))
            inheritConstraints = self.mdb.Read(m2Definition,STR(MXELEMENT.CONSTRAINTS))
            allConstraints += inheritConstraints.GetVal()
        return allConstraints
    
    def ExecCus(self, cmd:Cmd, args:list, tid:int) -> BOL: 
        ''' Executes a custom command registered externally
        '''
        transaction = self.__GetTransaction(tid)
        history = transaction.GetCurrentHistory()
        #resolve the arguments
        argVal = [self.qryRunner.Eval(a,history) for a in args]
        #add the argument values to the history of the command execution
        localHistory = transaction.GetNextHistory()
        for a in argVal:
            localHistory.AddValue(a,True)
        #execute the command
        val = self.ExecOnTransaction(cmd, tid, transaction.roc)
        return val
        
        
    
    #@Override
    def IsEventDesired(self, evt, sourceSessionId:str, sessionId:str)->bool:
        #extend decision based on the session
        if(sessionId):
            sessionIdPublic = self.__GetSessionIdPublic(sessionId)
            if(sessionIdPublic in self.sessions):
                session = self.sessions[sessionIdPublic]
                evtType = evt.a[0].GetVal()
                evtArgs = evt.a[1]
                #strategy = session.GetObservationStrategy(evtType)
                isObserved = session.IsEventObserved(evtType)
                isSuperobserved = session.IsEventSuperobserved(evtType) and self.accessController.IsAllowedToSuperobserve(session.user, evtType) #recheck if the rights have not changed
                if(not isObserved and not isSuperobserved):
                    return False #quick exit if event type is not desired
                #decide based on the event type what to do
                elif(EVT_TYPES.CRT == evtType):
                    elem = evtArgs[1] #the new object
                    createArgs = evtArgs[3]
                    if(sourceSessionId == sessionId):
                        return False #do not receive self induced changes
                    elif(isObserved):
                        #event selection for create depends on the create args
                        createArgObj = [e for e in createArgs if isinstance(e,Obj)]
                        #make sure that at least one object in the create args is observed
                        anyCreateArgObserved = any([session.IsElementObserved(e) for e in createArgObj])
                        allCreateArgsAllowed = all([self.mdb.IsAllowedToRead(e, NON(), session.user) for e in createArgObj]) 
                        return anyCreateArgObserved and allCreateArgsAllowed
                    elif(isSuperobserved):
                        return self.mdb.IsAllowedToRead(elem, NON(), session.user) 
                elif(EVT_TYPES.UPD == evtType):
                    elem = evtArgs[1] #the target
                    featureName = evtArgs[2]
                    value = evtArgs[3]
                    if(sourceSessionId == sessionId):
                        return False #do not receive self induced changes
                    elif(isObserved):
                        return session.IsElementObserved(elem) and\
                               self.mdb.IsAllowedToRead(elem, featureName, session.user) and\
                             (value.IsNone() or not isinstance(value,Obj) or self.mdb.IsAllowedToRead(value, NON(), session.user))
                    elif(isSuperobserved):
                        return self.mdb.IsAllowedToRead(elem, NON(), session.user) 
                elif(EVT_TYPES.DEL == evtType):
                    elem = evtArgs[1] #the target
                    if(sourceSessionId == sessionId):
                        return False #do not receive self induced changes
                    elif(isObserved):
                        return session.IsElementObserved(elem) and\
                               self.mdb.IsAllowedToRead(elem, NON(), session.user) 
                    elif(isSuperobserved):
                        return self.mdb.IsAllowedToRead(elem, NON(), session.user)
                elif(EVT_TYPES.VEC == evtType):
                    elem = evtArgs[0] #the target
                    const = evtArgs[1] #the constraint
                    if(sourceSessionId == sessionId):
                        return False #do not receive self induced changes
                    elif(isObserved):
                        return session.IsElementObserved(elem) and\
                               self.mdb.IsAllowedToRead(elem, NON(), session.user) and\
                               self.mdb.IsAllowedToRead(const, NON(), session.user)  
                    elif(isSuperobserved):
                        return self.mdb.IsAllowedToRead(elem, NON(), session.user) and\
                               self.mdb.IsAllowedToRead(const, NON(), session.user)   
                elif(EVT_TYPES.WAT == evtType):
                    if(sourceSessionId == sessionId): #each watcher only receives his private watch events
                        return True
                elif(EVT_TYPES.MSG == evtType):
                    if(sourceSessionId == sessionId):
                        return False #do not receive self induced messages
                    elif(isObserved):
                        msgKey = evtArgs[0].GetVal()
                        return session.IsMessageObserved(msgKey) 
                    elif(isSuperobserved):
                        return True
                    
        return False #without session ID and by default no events are received
        
    '''
    PRIVATE METHODS
    '''
    
    def __StartTransaction(self, tid:int, sessionId:str, readOnly:bool) -> Transaction:
        self.logger.Debug('Transaction %d started.'%(tid))
        transaction = Transaction(tid,readOnly,self.latestChangeId-1) #the current change is the latest-1.
        self.transactions[tid] = transaction
        session = self.__InitSession(transaction, sessionId)
        self.mdb.SetSession(session)
        return transaction
    
    def __EndTransaction(self, res:Cmd, tid:int) -> None:
        '''WARNING: __EndTransaction is not allowed to raise exceptions, because this will hold the domain forever
        '''
        try:
            transactionSucess = False #is set to true later
            #remove the current transaction from the stack
            transaction = self.transactions.pop(tid)
            #obtain the changes done during the transaction
            transactionChanges = transaction.changes
            #transactionSessionId = self.__MergeSessionId(transaction.session.sessionIdPublic, transaction.session.sessionIdSecret)
            if(res.cmd == CMD_TYPES.ERR):
                code = res.a[0]
                reason = res.a[1]
                self.logger.Warn('Transaction %d failed: %s: %s'%(tid,code,reason))
                nChanges = len(transactionChanges)
                if(0<nChanges):
                    self.logger.Warn('Transaction %d: Rolling back %d changes.'%(tid,nChanges))
                    self.__RollbackChanges(transactionChanges, transaction)
            else:
                #persist changes
                if(0<len(transactionChanges)):
                    self.__PersistChanges(transactionChanges,transaction.session)
                transactionSucess = True        
            #release the access controlled MDB
            self.mdb.UnsetSession()
            #POST PROCESSING: watched queries and events, but only if transaction succeeded
            if(transactionSucess):
                self.__UpdateWatchedQueriesAndCreateEvents()
                self.ReleasePostponedNotifications()
                self.__TriggerEventNotification()
            else: #transaction failed
                self.ClearPostponedNotifications();
            self.logger.Debug('Transaction %d ended.'%(tid))
        except Exception as e:
            #can not raise any error here, can only log a message.
            self.logger.Error("End transaction failed: %s"%(str(e)))
            
    def __UpdateWatchedQueriesAndCreateEvents(self)->None:
        '''Update any watched query for each watcher and release watch events.
        WARNING: this must be called after the main transaction is over, because this 
        function will toggle between all watching sessions.
        '''
        allWatchingSessions = self.queryWatcher.GetAllWatcherSessionIds()
        for s in allWatchingSessions:
            if(s in self.sessions):
                watcherSession = self.sessions[s]
                self.mdb.SetSession(watcherSession)
                watchChanges = self.queryWatcher.GetAllWatchChangesForSession(s)
                self.mdb.UnsetSession()
                watcherSessionId = watcherSession.sessionId
                for chg in watchChanges:
                    evt = self.__ChangeToEvent(chg)
                    self.PostponeObserverNotification([evt], watcherSessionId)
    
        
    def __GetTransaction(self, tid:int) -> Transaction:
        transaction = None
        try:
            transaction = self.transactions[tid]
        except KeyError:
            raise EOQ_ERROR_RUNTIME("Invalid transaction id %d"%tid)
        return transaction
    
    def __InitSession(self, transaction:Transaction, sessionId:str) -> Session:
        session = None
        if(None == sessionId):
            session = self.annonymousSession
        else:
            (sessionIdPublic, sessionIdSecret) = self.__SplitSessionId(sessionId)
            try:
                session = self.sessions[sessionIdPublic]
                if(session.sessionIdSecret != sessionIdSecret):
                    raise EOQ_ERROR_ACCESS_DENIED("Cannot use foreign session.")
            except KeyError:
                #if not existing, create a new one
                session = self.__CreateNewSession(sessionId, sessionIdPublic, sessionIdSecret)
        #set the current transaction to the session
        transaction.session = session
        return session
    
    def __SplitSessionId(self, sessionId:str)->Tuple[str,str]:
        if(SESSION_ID_LENGTH != len(sessionId)):
            raise EOQ_ERROR_INVALID_VALUE("Invalid session ID")
        sessionIdPublic = self.__GetSessionIdPublic(sessionId)
        sessionIdSecret = self.__GetSessionIdSecret(sessionId)
        return (sessionIdPublic,sessionIdSecret)
    
    def __GetSessionIdPublic(self, sessionId:str)->str:
        '''returns only the public part of the session ID
        '''
        return sessionId[SESSION_SECRET_LEN:]
    
    def __GetSessionIdSecret(self, sessionId:str)->str:
        '''returns only the secret part of the session ID
        '''
        return sessionId[:SESSION_SECRET_LEN]
    
    def __MergeSessionId(self, sessionIdPublic:str, sessionIdSecret:str)->str:
        ''' Composes public and secret part of a session id to the
        full session id
        ''' 
        return sessionIdSecret+sessionIdPublic
    
    def __CreateNewSession(self, sessionId:str, sessionIdPublic:str, sessionIdSecret:str, inheritSession:Session=None, isTemp:bool=False) -> Session:
        self.sessionCount += 1
        sessionNumber = self.sessionCount
        session = Session(sessionId, sessionIdPublic, sessionIdSecret, sessionNumber)
        session.isTemp = isTemp
        if(inheritSession):
            session.user = inheritSession.user #inherit the user and access rights
        self.sessions[sessionIdPublic] = session
        return session
        
    def __GetHistory(self, tid:int) -> History:
        return self.__GetTransaction(tid).GetCurrentHistory()

        
    def __AddLocalChange(self, tid:int, chg:Change, increasesChangeId:bool, isEvent:bool) -> None:
        '''Remembers every change done with in a transaction.
    
        Changes are stored to revert it in case of failures.
        Changes are only persisted if no failure occurs until the (compound) command is complete.
        
        '''
        transaction = self.__GetTransaction(tid)
        cid = self.latestChangeId + transaction.nRealChanges
        chg.timestamp = datetime.now()
        chg.cid = cid
        chg.tid = tid
        chg.user =  transaction.session.user
        chg.sessionNumber = transaction.session.sessionNumber
        #store the change in the transactions local change list
        self.__GetTransaction(tid).changes.append(chg)
        transaction.cid = cid #remember the changes in the transaction
        if(increasesChangeId):
            #calculate what the change ID will be if the change is persisted
            transaction.nRealChanges += 1
        if(isEvent):
            evt = self.__ChangeToEvent(chg)
            self.PostponeObserverNotification([evt], transaction.session.sessionId)
        
    def __PersistChanges(self, changes:list, session:Session) -> None:
        #notify observers on changes
        for chg in changes:
            #persist any model changes
            if(isinstance(chg,(CrtChange,UpdChange,DelChange))): #this are only the real changes
                #if the maximum of saved changes is exceeded begin deleting entries
                if(self.latestChangeId - self.earliestChangeId > self.config.cmdMaxChanges):
                    self.changes.pop(self.earliestChangeId)
                    self.earliestChangeId +=1
                #add each change of the current transaction to the change list
                self.changes[self.latestChangeId] = chg
                if(self.latestChangeId!=chg.cid):
                    #Should never go here
                    raise EOQ_ERROR_RUNTIME('Inconsistency in change detected list.')
                self.latestChangeId+=1
                #log the changes if logging is enabled
            else:
                pass #nothing to do, this will only result in an event
            self.logger.Debug('Change: %s'%(chg))
        
    def __ChangeToEvent(self,chg : Change) -> Evt:
        if(isinstance(chg,CrtChange)):
            return CrtEvt(U64(chg.cid),chg.target,chg.classId,chg.createArgs,InitValOrNon(chg.user,STR))
        elif(isinstance(chg,UpdChange)):
            return UpdEvt(U64(chg.cid),chg.target,chg.feature,chg.value,chg.position,InitValOrNon(chg.user,STR))
        elif(isinstance(chg,DelChange)):
            return DelEvt(U64(chg.cid),chg.target,chg.classId,chg.createArgs,InitValOrNon(chg.user,STR))
        elif(isinstance(chg,MsgChange)):
            return MsgEvt(chg.msgKey,chg.msg)
        elif(isinstance(chg,VecChange)):
            return VecEvt(chg.target,chg.constraint,chg.isValid,chg.error)
        elif(isinstance(chg,WatChange)):
            return WatEvt(chg.wid,chg.result,chg.error)
        else: #should never go here
            raise EOQ_ERROR_RUNTIME('Experienced unexpected change type: %s'%(type(chg).__name__))
            
    def __ChangeToChangeRecord(self, chg:Change) -> LST:
        if(isinstance(chg,CrtChange)):
            return LST([STR(EVT_TYPES.CRT),U64(chg.cid),chg.target,chg.classId,chg.createArgs,InitValOrNon(chg.user,STR)])
        elif(isinstance(chg,UpdChange)):
            return LST([STR(EVT_TYPES.UPD),U64(chg.cid),chg.target,chg.feature,chg.value,chg.position,InitValOrNon(chg.user,STR)])
        elif(isinstance(chg,DelChange)):
            return LST([STR(EVT_TYPES.DEL),U64(chg.cid),chg.target,InitValOrNon(chg.user,STR)])
        else: #should never go here
            raise EOQ_ERROR_RUNTIME('Experienced unexpected change type: %s'%(type(chg).__name__))
        
    def __RollbackChanges(self, changes:list, transaction:Transaction)->None:
        #revert local changes for multicommand transactions
        try:
            for chg in reversed(changes):
                self.logger.Warn("ROLLBACK: %s "%(chg))
                if(isinstance(chg,CrtChange)):
                    self.__RollbackCrt(chg)
                elif(isinstance(chg,UpdChange)):
                    self.__RollbackUpd(chg)
                elif(isinstance(chg,DelChange)):
                    self.__RollbackDel(chg)
                elif(isinstance(chg,ObsChange)):
                    self.__RollbackObs(chg,transaction)
                elif(isinstance(chg,UbsChange)):
                    self.__RollbackUbs(chg,transaction)
                else: #should never go here
                    pass # nothing to do for other changes
        except Exception as e:
            self.logger.Error("Error during rollback: %s"%(str(e)))  
            if self.config.printUnexpectedExceptionTraces:
                print("Unexpected exception trace (__RollbackChanges):") 
                traceback.print_exc()
            
    def __RollbackCrt(self, chg:CrtChange):
        self.mdb.Delete(chg.target,False,not chg.postModError) #use unprotected mdb to make sure that rollback does not fail
            
    def __RollbackUpd(self, chg:UpdChange)->None:
        position = chg.position
        #reset the old value
        if(chg.value.IsNone()):
            if(position >= 0):
                position = -(position+I64(2)) #if a value was deleted, it must be re-added here
        self.mdb.Update(chg.target,chg.feature,chg.oldValue,position,False,not chg.postModError)
        #rebuild the old values containment if it was existing before
        if(chg.oldOwner):
            oldFeatureName = self.mdb.Read(chg.oldFeature,STR(M2COMPOSITION.NAME),NON(),False,not chg.postModError)
            self.mdb.Update(chg.oldOwner,oldFeatureName,chg.value,-(chg.oldIndex+I64(2)),False,not chg.postModError)
            
    def __RollbackDel(self, chg:DelChange)->None:
        (elem,pmerr) = self.mdb.Create(chg.classId,chg.createArgs,chg.target,chg.recoveryArgs) #restore the element with its old ID
                
    def __RollbackObs(self, chg:ObsChange, transaction:Transaction)->None:
        evtType = chg.evtType
        evtKey = chg.evtKey
        history = None
        session = transaction.session
        self.__Ubs(evtType, evtKey, history, session)
        
    def __RollbackUbs(self, chg:ObsChange, transaction:Transaction)->None:
        evtType = chg.evtType
        evtKey = chg.evtKey
        history = None
        if(chg.affectedSessionPublicId in self.sessions):
            affectedSession = self.sessions[chg.affectedSessionPublicId]
            self.__Obs(evtType, evtKey, history, affectedSession)
    
    def __PreventRecursion(self,cmd,cmdId):
        if(cmd.cmd == cmdId):
            raise EOQ_ERROR_INVALID_VALUE('No recursion allowed.')
        elif(cmd.cmd == CMD_TYPES.CMP): #compound command?
            for c in cmd.a:
                self.__PreventRecursion(c, cmdId)
                
    def __SendMessage(self, msgKey:STR, msg:STR, tid:int)->None:
        '''Sends a message to observers. 
        The message is not directly send but put to the event stack and send 
        when the transaction is over
        '''
        if(self.config.cmdMaxMsgKeyLength<len(msgKey)):
            raise EOQ_ERROR_INVALID_VALUE('Message key has more than %d chars'%(self.config.cmdMaxMsgKeyLength))
        if(self.config.cmdMaxMsgLength<len(msg)):
            raise EOQ_ERROR_INVALID_VALUE('Message has more than %d chars: %s'%(self.config.cmdMaxMsgLength,msg))
        change = MsgChange(msgKey, msg)
        self.__AddLocalChange(tid,change,False,True)
        
    def __UnobserveDeletedElementForAllSessions(self, tid:int, deletedElement:Obj)->None:
        '''Creates UbsChange events for all sessions
        '''
        for session in self.sessions.values():
            isChanged = session.UnobserveElement(deletedElement)
            if(isChanged):
                change = UbsChange(EVT_TYPES.ELM,deletedElement,session.sessionIdPublic)
                self.__AddLocalChange(tid,change,False,False)
        
    def __DeprecatedWarning(self, message:str):
        self.logger.Warn("%s is deprecated. Consider replacement."%(message))
        
        
    ### EVENT NOTIFICATION ###
    def __TriggerEventNotification(self):
        '''Triggers that queued and released are sent to their observers. 
        This either happens synchronous or asynchronous
        '''
        if(self.config.evtNotifyAsync):
            self.notifyObserverSignal.set()
        else:
            self.SendQueuedAndReleasedNotifications()
    
    def __EventNotificationLoop(self)->None:
        while(self.shallRun):
            hasNewEvents = self.notifyObserverSignal.wait(timeout=self.config.threadLoopTimeout)
            #hasNewEvents = self.evtSemaphore.acquire(timeout=self.config.threadLoopTimeout)
            if(hasNewEvents):
                self.SendQueuedAndReleasedNotifications()
                self.notifyObserverSignal.clear()
        #finally make sure no events get lost
        self.SendQueuedAndReleasedNotifications()
        
