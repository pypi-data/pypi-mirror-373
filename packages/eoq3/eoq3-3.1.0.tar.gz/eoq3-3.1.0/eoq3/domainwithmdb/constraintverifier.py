'''
Dealing with the interpretation of constraints and caching the results

2024 Bjoern Annighoefer

'''

from ..value import BOL, STR, LST
from ..query import Obj,Qry
from ..concepts import *
from ..config import Config, EOQ_DEFAULT_CONFIG
from ..serializer import CreateSerializer
from ..error import *
from ..mdb import ReadOnlyMdb

from .qryrunner import QryRunner

from typing import Dict, Union, Tuple

class ConstraintInfo:
    '''An entry in the constraints cache
    '''
    def __init__(self, constraint:Obj):
        self.constraint:Obj = constraint
        self.owner:Obj = None #the parent element of the constraint
        self.query:Qry = None
        self.targets:Dict[Obj,bool] = {} #the list of elements this constraint was evaluated for
        
class ConstraintEvaluationInfo:
    def __init__(self, constraint:Obj, target:Obj):
        self.constraint:Obj = constraint
        self.target:Obj = target #the element the constraint was evaluated for
        self.exception:str = None
        self.isValid = False
        self.evalCounter = 0 #how often was the constraint evaluated
        
class TargetInfo:
    def __init__(self, target:Obj):
        self.target:Obj = target
        self.evaluations:Dict[Obj,ConstraintEvaluationInfo] = {}#relates constraint and result

from ..verifier import Verifier

class ConstraintVerifier(Verifier):
    def __init__(self, config:Config = EOQ_DEFAULT_CONFIG):
        super().__init__()
        self.config = config
        #internals
        self.expressionSerializer = CreateSerializer(self.config.constraintSerializer)
        self.qryrunner = None #need a private qryrunner with full access is set later
        self.constraintsCache:Dict[Obj,ConstraintInfo] = {} #each constraint definition is stored here
        self.targetCache:Dict[Obj,TargetInfo] = {} #a combination of constraint and target forms an evaluation
        
    ### VERIFIER OVERRIDES ###
    #@override
    def Init(self, mdb:ReadOnlyMdb)->None:
        '''Initialize the Access controller and tell him the domain he is responsible for
        '''
        super().Init(mdb)
        self.qryrunner = QryRunner(self.mdb,self.config)
    
    #@override
    def CreatePreVerify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        '''Validate if a constraint contains a valid expression before it enters the mdb
        '''
        if(CONCEPTS.MXCONSTRAINT==classId and 2==len(createArgs)):
            expression = createArgs[1]
            if(STR == type(expression)): #if not STR, this create will fail anyhow
                self.expressionSerializer.DesQry(expression.GetVal()) #raises exception if it fails
    
    #@override
    def CreateNotify(self, classId:Union[STR,Obj], createArgs:LST, target:Obj, recoveryArgs:LST, user:str=None)->None:
        '''If a constraint has entered the mdb, add it to the cache
        '''
        if(CONCEPTS.MXCONSTRAINT==classId):
            # no further check necessary, since everything was validated beforehand
            constraint = target
            owner = createArgs[0]
            expression = createArgs[1]
            # create cache entry
            constraintInfo = ConstraintInfo(constraint)
            constraintInfo.owner = owner
            constraintInfo.query = self.expressionSerializer.DesQry(expression.GetVal())
            self.constraintsCache[constraint] = constraintInfo
                
    def DeleteNotify(self, target:Obj, classId:STR, createArgs:LST, recoveryArgs:LST, user:str=None)->None:
        '''Remove constraints from the cache if deleted
        '''
        # any deletion might cause a target being removed from the cache
        if(target in self.targetCache):
            targetInfo = self.targetCache[target]
            constraintInfo = self.constraintsCache[targetInfo.constraint]
            if(target in constraintInfo.targets):
                del constraintInfo.targets[target]
            del self.targetCache[target]
        # if a constraint itself is removed, remove its info and results
        if(CONCEPTS.MXCONSTRAINT==classId):
            c = target
            if(c in self.constraintsCache):
                constraintsInfo = self.constraintsCache[c]
                for t in constraintsInfo.targets.values():
                    if(t in self.targetCache):
                        targetInfo = self.targetCache[t]
                        if(c in targetInfo.evaluations):
                            del targetInfo.evaluations[c]
            del self.constraintsCache[c]
            
    ### CONSTRAINT METHODS ###
    def EvalConstraint(self, constraint:Obj, target:Obj)->Tuple[bool,str,bool]:
        '''evaluates a constraint for a given target and returns the result
        or raise an exception
        '''
        #get or create the evaluation info 
        constraintInfo = self.constraintsCache[constraint]
        targetInfo = None
        if(target in self.targetCache):
            targetInfo = self.targetCache[target]
        else: #create new target record
            targetInfo = TargetInfo(target)
            self.targetCache[target] = targetInfo
        evaluationInfo = None
        if(constraint in targetInfo.evaluations):
            evaluationInfo = targetInfo.evaluations[constraint]
        else: #create new evaluation record
            evaluationInfo = ConstraintEvaluationInfo(constraint,target)
            targetInfo.evaluations[constraint] = evaluationInfo #1. add to the results per target
            constraintInfo.targets[target] = True #2. add this as a target for the given constraint
        #store old values to obtain the changed text
        oldValid = evaluationInfo.isValid
        oldException = evaluationInfo.exception
        # run the evaluation
        try:
            result = self.qryrunner.EvalOnContextAndScope(target, constraintInfo.query, target, None)
            if(BOL==type(result)):
                evaluationInfo.exception = None
                evaluationInfo.isValid = result.GetVal()
            else:
                evaluationInfo.exception = EoqErrorAsString(EOQ_ERROR_INVALID_VALUE("No boolean result."))
                evaluationInfo.isValid = False
        except Exception as e:
            evaluationInfo.exception = EoqErrorAsString(EOQ_ERROR_RUNTIME("Evaluation failed: %s"%(str(e))))
            evaluationInfo.isValid = False
        #check if validation resulted in an update
        changed = (1>evaluationInfo.evalCounter) or (oldValid != evaluationInfo.isValid) or (oldException != evaluationInfo.exception)
        #increase counter
        evaluationInfo.evalCounter += 1
        #return
        return evaluationInfo.isValid, evaluationInfo.exception, changed
            
            
    
    