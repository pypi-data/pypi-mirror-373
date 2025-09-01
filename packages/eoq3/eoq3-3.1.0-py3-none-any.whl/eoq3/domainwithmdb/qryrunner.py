"""
 Implements a query interpreter.
 2019 Bjoern Annighoefer
"""

from .history import History
from .util import ApplyToAllElements,ApplyToAllElementsInA,ApplyToAllElementsInB,ApplyToAllListsOfElementsInA,ApplyToSimilarElementStrutures,ApplyToSimilarListsOfObjects,IsList,IsListOfObjects,TRM,Determinate,IsNoList

from ..config import Config
from ..logger import GetLoggerInstance
from ..concepts import CONCEPTS, MXMDB, MXELEMENT, MXCONSTRAINT,\
                       M2MODEL, M2PACKAGE, M2ENUM,M2OPTIONOFENUM, M2CLASS, M2ATTRIBUTE, M2ASSOCIATION, M2COMPOSITION, M2INHERITANCE,\
                       M1MODEL, M1OBJECT, M1COMPOSITION, M1ATTRIBUTE, M1ASSOCIATION
from ..value import VAL, PRM, BOL, U32, U64, I32, I64, F32, F64, STR, DAT, NON, LST, QRY, ValidateVal
from ..query import SEG_TYPES, Seg, Qry, Obj, MET_MODES, IDX_MODES, STF_MODES
from ..error import EOQ_ERROR, EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_DOES_NOT_EXIST, EOQ_ERROR_UNSUPPORTED, EOQ_ERROR_UNKNOWN, EOQ_ERROR_RUNTIME
from ..serializer import Serializer, TextSerializer
from ..mdb import Mdb
from ..util.benchmark import Benchmark

import re

from typing import Dict, Any, List

# constants
CONTEXT_LESS_SEGMENTS = {
    SEG_TYPES.OBJ : True,
    SEG_TYPES.HIS : True
    }


# Special type handling regex
class RGX(STR):
    def __init__(self, value:re.Pattern):
        VAL.__init__(self,'RGX')
        self.v = value
    def __repr__(self):
        return str(self.v)
    def Type(self):
        return STR #regex are handled like strings

#terminate operation
def TvX(a,b):
    return a #do nothing


class QryRunner:
    """QueryRunner: Evaluates a query using a mdb.
    Queries are evaluated by sequentially applying segments to the context.
    Query runner will not change the mdb.
    Only the Eval and EvalOnContextAndScope function should be called externally
    """
    def __init__(self, mdb:Mdb, config:Config):
        self.mdb:Mdb = mdb
        self.mdbObj:Obj = None
        self.config:Config = config
        #internals
        self.qrySerializer:Serializer = TextSerializer()
        self.segmentEvaluators = {}
        self.logger = GetLoggerInstance(config)
        #benchmark
        if self.config.enableStatistics:
            self.benchmark = Benchmark()
            allQryTypes = [getattr(SEG_TYPES,k) for k in SEG_TYPES.__dict__ if not k.startswith('_')]
            for t in allQryTypes:
                self.benchmark.InitMessure(t)
        #Segment operators
        self.segmentEvaluators = self.__InitQrySegHandlers()
        #META operators
        self.metEvaluators = self.__InitMetOperationHandlers()
        # init numerical and boolean operation handlers
        self.equEvaluators = self.__InitEquOperationHandlers()
        self.neqEvaluators = self.__InitNeqOperationHandlers()
        self.greEvaluators = self.__InitGreOperationHandlers()
        self.lesEvaluators = self.__InitLesOperationHandlers()
        self.rgxEvaluators = self.__InitRgxOperationHandlers()
        self.addEvaluators = self.__InitAddOperationHandlers()
        self.subEvaluators = self.__InitSubOperationHandlers()
        self.mulEvaluators = self.__InitMulOperationHandlers()
        self.divEvaluators = self.__InitDivOperationHandlers()
        # init list length handler
        self.lenFunctor = lambda a, b: U64(len(a))
        # init list operation handlers
        #cross product operation
        def cspUni(a,b):
            res = LST()
            for e1 in a:
                for e2 in b:
                    res.append(LST([e1,e2]))
            return res
        self.cspEvaluator = cspUni
        #intersection operation
        def itsUni(a,b):
            res = LST()
            #add common elements
            for e1 in a:
                if(e1 in b):
                    res.append(e1)
            return res
        self.itsEvaluator = itsUni
        #set difference operation
        def difUni(a,b):
            res = LST()
            #add common elements
            for e1 in a:
                if(e1 not in b):
                    res.append(e1)
            return res
        self.difEvaluator = difUni
        #union operations
        def uniUni(a,b):
            res = LST()
            #add all unique elements of a
            for e in a:
                if(e in res):
                    continue
                res.append(e)
            #add all unique elements of b
            for e in b:
                if(e in res):
                    continue
                res.append(e)
            return res
        self.uniEvaluator = uniUni
        #concatenate operation
        def conUni(a,b):
            res = []
            res.extend(a)
            res.extend(b)
            return LST(res)
        self.conEvaluator = conUni
        
    def Eval(self, val:VAL, history:History=None) -> VAL:
        context = NON()
        #get an initial context if the first segment requires that 
        if(isinstance(val,Qry) and 0<len(val.v) and val.v[0].seg not in CONTEXT_LESS_SEGMENTS):
            if(None==self.mdbObj):
                # init mdb obj to prevent that this must be re-read
                self.mdbObj = self.mdb.Read(NON(),STR(MXMDB.MDB)) #read non is MXDB
            modelroot = self.mdbObj #the root is allways the MDB
            context = self.mdbObj if modelroot.IsNone() else modelroot
        return self.EvalOnContextAndScope(context,val,context,history)
        
    def EvalOnContextAndScope(self, context:VAL, val:VAL, scope:VAL, history:History) -> VAL:
        if(isinstance(val,Qry)):
            return self.EvalQry(context, val.v, scope, history)
        elif(IsList(val)):
            return self.EvalArr(context,LST([val]),scope,history)
        else:
            return val #its a primitive value, do nothing 
    
    ### SEGMENT EVALUATORS ###

    def EvalSeg(self, context:VAL,seg : Seg, scope:VAL, history:History) -> VAL:
        res = NON()
        segType = seg.seg
        try:
            evalFunction = self.segmentEvaluators[segType] 
        except KeyError as e:
            raise EOQ_ERROR_UNSUPPORTED("Unknown segment type: %s: %s"%(segType,str(e)))
        if self.config.enableStatistics: self.benchmark.Start()
        try:
            v = seg.v 
            res = evalFunction(context,v,scope,history)
        except Exception as e:
            if self.config.enableStatistics: self.benchmark.Stop(segType)
            raise e         
        if self.config.enableStatistics: self.benchmark.Stop(segType)
        return res

    def EvalQry(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        currentContext = scope #each subquery restarts from the current scope
        #newScope = context
        n = 1
        for seg in args:
            if(isinstance(currentContext,TRM)):
                break;
            try:
                currentContext = self.EvalSeg(currentContext,seg,scope,history)
            except EOQ_ERROR as e:
                e.msg = "Segment %d (%s): "%(n,seg.seg) + e.msg
                raise e
            except Exception as e:
                raise EOQ_ERROR_UNKNOWN("Segment %d (%s): %s"%(n,seg.seg,str(e)))
            n+=1
        res = Determinate(currentContext)
        return res
    
    def EvalObj(self, context:VAL, args:list, scope:VAL, history:History) -> VAL :
        objId = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[PRM],'element ID',exact=False)
        #TODO: speed up local processing, by not creating an new object seg element, but by attaching the old one.
        return Obj(objId) # because the argument is unpacked before
    
    def EvalOni(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = NON()
        nameOrId = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[STR],'nameOrId')
        ValidateVal(context,[Obj],'context',False)
        elements = self.mdb.FindElementByIdOrName(nameOrId,context)
        n = len(elements)
        if(0==n):
            raise EOQ_ERROR_DOES_NOT_EXIST("%s is no element name or ID."%(nameOrId))
        if(n>1):
            raise EOQ_ERROR_INVALID_VALUE("%s is not unique"%(nameOrId))
        else:
            res = elements[0]         
        return res
    
    def EvalHis(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        ref = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[I64,STR],'reference')
        if(None != history):
            if(isinstance(ref,I64)):
                return history.GetValueByIndex(ref.GetVal())
            else:
                return history.GetValueByName(ref.GetVal())
        else:
            raise EOQ_ERROR_DOES_NOT_EXIST('No history available. Used his outside a compound command?')
        
    def EvalPth(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        name = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[STR],'name')
        pathFunctor = lambda o: self.mdb.Read(o,name)
        res = ApplyToAllElements(context, pathFunctor)
        return res
    
    def EvalCls(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = NON()
        name = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[STR],'name')
        classes = self.mdb.FindElementByIdOrName(name,NON(),STR(CONCEPTS.M2CLASS))
        nClasses = len(classes)
        if(nClasses>0):
            if(nClasses>1):
                self.logger.Warn('Class name %s is not unique. Use class ID instead.'%(name))
            res = LST()
            clsFunctor = lambda a,b: self.mdb.Read(b,STR(M2CLASS.MYINSTANCES),a)
            for c in classes:
                res += LST(ApplyToAllElementsInA(context,c,clsFunctor))
        else:
            raise EOQ_ERROR_DOES_NOT_EXIST("No known class with name %s."%(name))
        return res

    def EvalIno(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = NON()
        name = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[STR],'name')
        classes = self.mdb.FindElementByIdOrName(name,NON(),STR(CONCEPTS.M2CLASS))
        nClasses = len(classes)
        if(nClasses>0):
            if(nClasses>1):
                self.logger.Warn('Class name %s is not unique. Use class ID instead.'%(name))
            res = LST()
            inoFunctor = lambda a,b: self.mdb.Read(b,STR(M2CLASS.INSTANCES),a)
            for c in classes:
                res += LST(ApplyToAllElementsInA(context,c,inoFunctor))
        else:
            raise EOQ_ERROR_DOES_NOT_EXIST("No known class with name %s."%(name))
        return res

    def EvalNot(self, context:VAL, args:VAL, scope:VAL, history:History) -> VAL:
        notFunctor = lambda o: BOL(False) if o.IsTrue() else BOL(True)
        res = ApplyToAllElements(context, notFunctor)
        return res
    
    def EvalTrm(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        #Define select functors
        def TrmOperator(a,b,c):
            res = None
            if(isinstance(a,TRM)): #termination already happened
                res = a
            elif(b): #condition is true
                res = TRM(c)
            else:
                res = a #return value as is
            return res
        
        def TrmElemVsElemFunc(a,b,c):
            return LST([TrmOperator(a[i],b[i],c) for i in range(len(b))])

        def TrmElemVsStructFunc(a,b,c):
            raise EOQ_ERROR_RUNTIME("Error applying termination: Argument of termination condition must be of lower depth than the context, but got %s{%s,%s}="%(a,b,c))
        
        def TrmStructVsElemFunc(a,b,c): 
            return LST([TrmOperator(a[i],b[i],c) for i in range(len(b))])
        #Begin of function
        nArgs = len(args)
        condquery = None
        default = None
        #is custom condition given?
        if(nArgs>0):
            condquery = ValidateVal(args[0],[VAL],'condition',False)
        else:
            condquery = Qry().Equ(NON()) #special default case
        #is custom default given?
        if(nArgs>1):
            default = self.EvalOnContextAndScope(context,args[1],context,history)
        else:
            default = NON()
        condition = self.EvalOnContextAndScope(context,condquery,context,history)
        # default = self.EvalOnContextAndScope(context,args[1],context,history)
        res = ApplyToSimilarListsOfObjects(LST([context]),LST([condition]),TrmElemVsElemFunc,TrmElemVsStructFunc,TrmStructVsElemFunc,default)
        return res[0] #return the first element because context and condition packed in lists above
    
    def EvalQrf(self, context:VAL, args:VAL, scope:VAL, history:History) -> VAL:
               
        def qrfFunctor(a:Obj):
            if(isinstance(a,Obj)):
                #reverse the path through concepts to this element
                pathFromParent = []
                currentElement = a
                currentConcept = self.mdb.Read(currentElement,STR(MXELEMENT.CONCEPT)).GetVal()
                while(currentConcept != CONCEPTS.MXMDB):
                    parent = None
                    feature = None
                    index = None
                    # MX layer
                    if(currentConcept==CONCEPTS.MXCONSTRAINT):
                        parent = self.mdb.Read(currentElement,STR(MXCONSTRAINT.ELEMENT))
                        feature = STR(MXELEMENT.CONSTRAINTS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    # M2 layer
                    elif(currentConcept==CONCEPTS.M2MODEL):
                        (parent,perr) = self.mdb.Create(STR(CONCEPTS.MXMDB))
                        feature = STR(MXMDB.M2MODELS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2PACKAGE):
                        parent = self.mdb.Read(currentElement,STR(M2PACKAGE.SUPERPACKAGE))
                        feature = STR(M2PACKAGE.SUBPACKAGES)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2ENUM):
                        parent = self.mdb.Read(currentElement,STR(M2ENUM.PACKAGE))
                        feature = STR(M2PACKAGE.ENUMS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2OPTIONOFENUM):
                        parent = self.mdb.Read(currentElement,STR(M2OPTIONOFENUM.ENUM))
                        feature = STR(M2ENUM.OPTIONS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2CLASS):
                        parent = self.mdb.Read(currentElement,STR(M2CLASS.PACKAGE))
                        feature = STR(M2PACKAGE.CLASSES)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2ATTRIBUTE):
                        parent = self.mdb.Read(currentElement,STR(M2ATTRIBUTE.CLASS))
                        feature = STR(M2CLASS.MYATTRIBUTES)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2ASSOCIATION):
                        parent = self.mdb.Read(currentElement,STR(M2ASSOCIATION.SRCCLASS))
                        feature = STR(M2CLASS.MYSRCASSOCIATIONS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2COMPOSITION):
                        parent = self.mdb.Read(currentElement,STR(M2COMPOSITION.PARENTCLASS))
                        feature = STR(M2CLASS.MYPARENTCOMPOSITIONS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M2INHERITANCE):
                        parent = self.mdb.Read(currentElement,STR(M2INHERITANCE.SUBCLASS))
                        feature = STR(M2CLASS.GENERALIZATIONS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    # M1 layer
                    elif(currentConcept==CONCEPTS.M1MODEL):
                        (parent,perr) = self.mdb.Create(STR(CONCEPTS.MXMDB))
                        feature = STR(MXMDB.M1MODELS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M1OBJECT):
                        parent = self.mdb.Read(currentElement,STR(M1OBJECT.MODEL))
                        feature = STR(M1MODEL.OBJECTS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M1ATTRIBUTE):
                        parent = self.mdb.Read(currentElement,STR(M1ATTRIBUTE.OBJECT))
                        feature = STR(M1OBJECT.ATTRIBUTES)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M1ASSOCIATION):
                        parent = self.mdb.Read(currentElement,STR(M1ASSOCIATION.SRC))
                        feature = STR(M1OBJECT.SRCASSOCIATIONS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    elif(currentConcept==CONCEPTS.M1COMPOSITION):
                        parent = self.mdb.Read(currentElement,STR(M1COMPOSITION.PARENT))
                        feature = STR(M1OBJECT.PARENTCOMPOSITIONS)
                        index = I64(self.mdb.Read(parent,feature).index(currentElement)) #low performance
                    #prepare next round
                    pathFromParent.append((parent,feature,index))
                    currentElement = parent
                    currentConcept = self.mdb.Read(currentElement,STR(MXELEMENT.CONCEPT)).GetVal()
                #build the path in reverse order
                val = Qry()
                for segment in reversed(pathFromParent):
                    f = segment[1]
                    i = segment[2]
                    if(None == i):
                        val.Pth(f)
                    else:
                        val.Pth(f).Idx(i)
            else:
                EOQ_ERROR_INVALID_TYPE("Qrf only requires context of type OBJ.")
            return val
            
        res = ApplyToAllElements(context, qrfFunctor)
        return res
    
    def EvalStf(self, context:VAL, args:VAL, scope:VAL, history:History) -> VAL:
        nArgs = len(args)
        mode = None
        if(nArgs>0):
            mode = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[STR],'mode').GetVal()
        else:
            mode = STR(STF_MODES.ELM)  # default
        res = NON()
        if(STF_MODES.ELM==mode):
            stfFunctor = lambda o: STR(self.qrySerializer.SerVal(o))
            res = ApplyToAllElements(context, stfFunctor)
        elif(STF_MODES.LST==mode):
            if(LST!=type(context)):
                raise EOQ_ERROR_INVALID_TYPE("Only LST can be input for stringify in mode LST.")
            res = LST([STR(self.qrySerializer.SerVal(o)) for o in context])
        elif(STF_MODES.FUL==mode):
            res = STR(self.qrySerializer.Ser(context))
        else:
            raise EOQ_ERROR_INVALID_VALUE("Unknown mode: %s"%(mode)) 
        return res
    
    def EvalSlf(self, context:VAL, args:VAL, scope:VAL, history:History) -> VAL:
        return context
    
    def EvalTry(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        def tryFunctor(a,b):
            res = NON()
            query = b[0]
            default = b[1]
            history = b[2]
            try:
                res = self.EvalOnContextAndScope(a,query,a,history)
            except:
                res = self.EvalOnContextAndScope(a,default,a,history)
            return res
        nArgs = len(args)
        query = ValidateVal(args[0],[VAL],'tryStatement',False) #do not evaluate here but element-wise inside try
        default = None
        #is custom default given?
        if (nArgs > 1):
            default = ValidateVal(args[1],[VAL],'exceptStatement',False)
        else:
            default = NON()

        res = ApplyToAllElementsInA(context,(query,default,history),tryFunctor)
        
        return res
    
    def EvalIdx(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = NON()
        if(not IsList(context)):
            raise EOQ_ERROR_INVALID_TYPE("Can only select from LST but got: %s"%(context))
        nArgs = len(args)
        if(1 == nArgs):
            n = self.EvalOnContextAndScope(context,args[0],context,history)
            if(isinstance(n, I64)):
                try:
                    idxFunctor = lambda a,b: a[b.GetVal()]
                    res = ApplyToAllListsOfElementsInA(context,n,idxFunctor)
                except IndexError:
                    raise EOQ_ERROR_DOES_NOT_EXIST('Index %d is out of bounds.'%(n.GetVal()))
            elif(isinstance(n, STR)):
                if(STR(IDX_MODES.ASC)==n): #sort ascending
                    ascFunctor = lambda a,b: LST(sorted(a))
                    res = ApplyToAllListsOfElementsInA(context,None,ascFunctor)
                elif(STR(IDX_MODES.DSC)==n): #sort descending
                    dscFunctor = lambda a,b: LST(sorted(a,reverse=True))
                    res = ApplyToAllListsOfElementsInA(context,None,dscFunctor)
                elif(STR(IDX_MODES.FLT)==n): #flatten
                    if(IsList(context)):
                        res = LST()
                        self.__Flatten(context,res)
                    else:
                        res = context
                elif(STR(IDX_MODES.LEN)==n): #calc size
                    res = ApplyToAllListsOfElementsInA(context,NON(),self.lenFunctor)
                else:
                    raise EOQ_ERROR_UNSUPPORTED("Unknown keyword: %s"%(n))
            else:
                raise EOQ_ERROR_INVALID_TYPE("Argument must be STR or I64, but got %s."%(type(n).__name__))
        elif(3 == nArgs):
            n = [self.EvalOnContextAndScope(context,args[0],context,history),
                 self.EvalOnContextAndScope(context,args[1],context,history),
                 self.EvalOnContextAndScope(context,args[2],context,history)]
            if(isinstance(n[0], I64) and isinstance(n[1], I64) and isinstance(n[2], I64)):
                rngFunctor = lambda a,b: a[b[0].GetVal():b[1].GetVal():b[2].GetVal()]
                try:
                    res = ApplyToAllListsOfElementsInA(context,n,rngFunctor)
                except IndexError:
                    raise EOQ_ERROR_DOES_NOT_EXIST('Index range %s is out of bounds.'%(n))
            else:
                raise EOQ_ERROR_INVALID_TYPE("Argument must be I64[3] but got: %s"%(type(n).__name__))
        else:
            raise EOQ_ERROR_INVALID_TYPE("Argument must be I64[3] or STR but got: %s" % (args))
        return res
    
    def EvalSel(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = LST
        #Define select functors
        def SelListVsListFunc(a,b,c):
            if(len(a)!=len(b)):
                raise EOQ_ERROR_INVALID_VALUE("Selector length %d does not match context length %d."%(len(b),len(a)))
            return LST([a[i] for i in range(len(b)) if b[i].IsTrue()])
        def SelListVsStructFunc(a,b,c):
            raise EOQ_ERROR_INVALID_VALUE("Error applying selector: Argument of selector must be of lower depth than the context, but got %s{%s"%(a,b))
        def SelStructVsListFunc(a,b,c): 
            return LST([a[i] for i in range(len(b)) if b[i].IsTrue()]) # is the same since 
        # Input check 
        if(IsNoList(context)): 
            raise EOQ_ERROR_INVALID_VALUE("Select only works on lists or lists of list, but got %s"%(str(context)))
        #Start Select evaluation        
        # selector changes the context
        if(0==len(context)):
            res = LST() #The result of an empty array is always an empty array. This saves time and prevents wrong interpretations of select queries that reduce the array length, e.g. any
        else:
            select = self.EvalOnContextAndScope(context,args[0],context,history)
            res = ApplyToSimilarListsOfObjects(context,select,SelListVsListFunc,SelListVsStructFunc,SelStructVsListFunc)
        return res
    
    def EvalArr(self, context:VAL, args:list, scope:VAL, history:History) -> VAL: 
        res = LST([self.EvalOnContextAndScope(context,a,context,history) for a in args[0]])
        return res
    
    def EvalZip(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        def ZipListVsListFunc(a,b,c):
            return a+LST([b])
        def ZipListVsStructFunc(a,b,c):
            return a+LST([b])
        def ZipStructVsListFunc(a,b,c):
            return LST([ApplyToAllListsOfElementsInA(a[i],b[i],lambda a,b: a+LST([b])) for i in range(len(b))])
        #works only for lists as context
        if(not IsList(context)):
            raise EOQ_ERROR_INVALID_TYPE("Can only apply ZIP for LST but got: %s"%(context))
        #prepare the results structure according to the context
        res = ApplyToAllElementsInA(context,NON(),lambda a,b: LST([]))
        #get the individual results
        if(0 < len(res)): #only add elements if the list is not empty, because the following code misbehaves for empty list inputs
            for a in args[0]:
                ar = self.EvalOnContextAndScope(context,a,context,history)
                #merge the individual result in the result structure derived from the context
                res = ApplyToSimilarListsOfObjects(res,ar,ZipListVsListFunc,ZipListVsStructFunc,ZipStructVsListFunc)
        return res
    
    
    def EvalAny(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        #local functor
        def anyFunctor(a,b):
            if(IsList(b)):
                for e in b:
                    if(e in a):
                        return BOL(True)
            else:
                return BOL(b in a)
            return BOL(False)
        
        #method start
        if(not IsList(context)):
            raise EOQ_ERROR_INVALID_TYPE("Can only apply ANY for LST but got: %s"%(context))
        select = self.EvalOnContextAndScope(context,args[0],context,history)
        if(IsList(select) and not IsListOfObjects(select)):
            raise EOQ_ERROR_INVALID_TYPE("Argument must be VAL or a LST of VAL but got: %s"%(select))
        res = ApplyToAllListsOfElementsInA(context,select,anyFunctor)
        return res
    
    def EvalAll(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        #local functor
        def allFunctor(a,b):
            foundMembers = 0
            if(IsList(b)):
                for e in b:
                    if(e in a):
                        foundMembers +=1
                return BOL(len(b)==foundMembers)
            else:
                return BOL(b in a)
            return BOL(False)
        
        #method start
        if(not IsList(context)):
            raise EOQ_ERROR_INVALID_TYPE("Can only apply ALL for LST but got: %s"%(context))
        select = self.EvalOnContextAndScope(context,args[0],context,history)
        if(IsList(select) and not IsListOfObjects(select)):
            raise EOQ_ERROR_INVALID_TYPE("Argument must be VAL or a LST of VAL but got: %s"%(select))
        res = ApplyToAllListsOfElementsInA(context,select,allFunctor)
        return res
    
    def EvalMet(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = None
        try: 
            name = ValidateVal(args[0],[STR],'name').GetVal()
            metEvaluator = self.metEvaluators[name]
            res = metEvaluator(context,args,scope,history)
        except KeyError as e:
            raise EOQ_ERROR_UNSUPPORTED("Unknown META segment type: %s: %s"%(name,str(e)))
        return res
    
    ### META EVALUATORS ###
   
    def EvalMetCls(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.__DeprecatedWarning("@%s is deprecated, please use %s instead."%(MET_MODES.CLS,M1OBJECT.M2CLASS))
        clsFunctor = lambda a,b: self.mdb.Read(a,STR(M1OBJECT.M2CLASS))
        res = ApplyToAllElementsInA(context,NON(),clsFunctor)
        return res
    
    def EvalMetCln(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.__DeprecatedWarning("DEPRECATED: @%s is deprecated, please use %s/%s instead."%(MET_MODES.CLN,M1OBJECT.M2CLASS,M2CLASS.NAME))
        clnFunctor = lambda a,b: self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.NAME))
        res = ApplyToAllElementsInA(context,NON(),clnFunctor)
        return res
    
    def EvalMetLen(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        if(not IsList(context)):
            raise EOQ_ERROR_INVALID_TYPE("SIZE only works for lists, but got: %s" %(context))
        res = ApplyToAllListsOfElementsInA(context,NON(),self.lenFunctor)
        return res
    
    def EvalMetPar(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        #self.__DeprecatedWarning("DEPRECATED: @%s is deprecated, please use %s/%s instead."%(MET_MODES.PAR,M1OBJECT.CHILDCOMPOSITION,M1COMPOSITION.PARENT))
        def parFunctor(a,b):
            parent = NON()
            parentCompo = self.mdb.Read(a,STR(M1OBJECT.CHILDCOMPOSITION))
            if(parentCompo):
                parent = self.mdb.Read(parentCompo,STR(M1COMPOSITION.PARENT))
            return parent
        res = ApplyToAllElementsInA(context,NON(),parFunctor)
        return res
    
    def EvalMetAlp(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        """All parents
        """
        def alpFunctor(a,b): 
            allParents = []
            parentCompo = self.mdb.Read(a,STR(M1OBJECT.CHILDCOMPOSITION))
            while parentCompo:
                parent = self.mdb.Read(parentCompo,STR(M1COMPOSITION.PARENT))
                allParents.append(parent)
                parentCompo = self.mdb.Read(parent,STR(M1OBJECT.CHILDCOMPOSITION))
            return LST(reversed(allParents))
        res = ApplyToAllElementsInA(context,NON(),alpFunctor)
        return res

    def EvalMetAlc(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        """All children
        """
        def alcFunctor(a,b):
            concept = self.mdb.Read(a, STR(MXELEMENT.CONCEPT))
            if (CONCEPTS.M1OBJECT != concept.GetVal()):
                raise EOQ_ERROR_INVALID_VALUE("%s: context be M1OBJECT, but is %s" % (MET_MODES.ALC, str(a)))
            return LST(self._AllCHildrenRaw(a))
        res = ApplyToAllElementsInA(context,NON(),alcFunctor)
        return res

    def _AllCHildrenRaw(self,target:Obj)->List[Obj]:
        """Returns all children of target in a flat list.
        """
        res = []
        for m1compo in self.mdb.Read(target,STR(M1OBJECT.PARENTCOMPOSITIONS)):
            child = self.mdb.Read(m1compo,STR(M1COMPOSITION.CHILD))
            subchildren = self._AllCHildrenRaw(child)
            res += [child] + [c for c in subchildren]
        return res
    
    def EvalMetAso(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        """Associates
        Optionally associated can be filtered as being children or a root object
        """
        def asoFunctor(a,b): 
            return LST([self.mdb.Read(x,STR(M1ASSOCIATION.SRC)) for x in self.mdb.Read(a,STR(M1OBJECT.DSTASSOCIATIONS))])
        root = NON()
        if(1<len(args)):
            rootArg = self.EvalOnContextAndScope(context,args[1],context,history)
            root = ValidateVal(rootArg, [Obj], 'args')
            concept = self.mdb.Read(root, STR(MXELEMENT.CONCEPT))
            if (CONCEPTS.M1OBJECT != concept.GetVal()):
                raise EOQ_ERROR_INVALID_VALUE("%s: second arg must be M1OBJECT, but is %s" % (MET_MODES.ASO,str(root)))
        res = ApplyToAllElementsInA(context,root,asoFunctor)
        if(not root.IsNone()):
            rootChildren = self._AllCHildrenRaw(root)
            res = LST([a for a in res if a in rootChildren or a == root])
        return res
    
    def EvalMetIdx(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CFT,M1OBJECT.CHILDCOMPOSITION,M1COMPOSITION.POS))
        def idxFunctor(a,b): 
            cc = self.mdb.Read(a,STR(M1OBJECT.CHILDCOMPOSITION))
            return self.mdb.Read(cc,STR(M1COMPOSITION.POS)) if not cc.IsNone() else NON()
        res = ApplyToAllElementsInA(context,NON(),idxFunctor)
        return res
    
    def EvalMetCft(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CFT,M1OBJECT.CHILDCOMPOSITION,M1COMPOSITION.M2COMPOSITION))
        def cftFunctor(a,b): 
            cc = self.mdb.Read(a,STR(M1OBJECT.CHILDCOMPOSITION))
            return self.mdb.Read(cc,STR(M1COMPOSITION.M2COMPOSITION)) if not cc.IsNone() else NON()
        res = ApplyToAllElementsInA(context,NON(),cftFunctor)
        return res
    
    def EvalMetFea(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/[%s,%s,%s] instead.'%(MET_MODES.FEA,M1OBJECT.M2CLASS,M2CLASS.ATTRIBUTES,M2CLASS.SRCASSOCIATIONS,M2CLASS.PARENTCOMPOSITIONS))
        feaFunctor = lambda a,b:    self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.ATTRIBUTES))+\
                                    self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.SRCASSOCIATIONS))+\
                                    self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.PARENTCOMPOSITIONS))
        res = ApplyToAllElementsInA(context,NON(),feaFunctor)
        return res
    
    def EvalMetFen(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/[%s,%s,%s] instead.'%(MET_MODES.FEN,M1OBJECT.M2CLASS,M2CLASS.ATTRIBUTES,M2CLASS.SRCASSOCIATIONS,M2CLASS.PARENTCOMPOSITIONS))
        fenFunctor = lambda a,b:    LST([self.mdb.Read(x,STR(M2ATTRIBUTE.NAME)) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.ATTRIBUTES))])+\
                                    LST([self.mdb.Read(x,STR(M2ASSOCIATION.DSTNAME)) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.SRCASSOCIATIONS))])+\
                                    LST([self.mdb.Read(x,STR(M2COMPOSITION.NAME)) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.PARENTCOMPOSITIONS))])
        res = ApplyToAllElementsInA(context,None,fenFunctor)
        return res
    
    def EvalMetFev(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/[%s,%s,%s] instead.'%(MET_MODES.FEV,M1OBJECT.M2CLASS,M2CLASS.ATTRIBUTES,M2CLASS.SRCASSOCIATIONS,M2CLASS.PARENTCOMPOSITIONS))
        fevFunctor = lambda a,b:    LST([self.mdb.Read(a,self.mdb.Read(x,STR(M2ATTRIBUTE.NAME))) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.ATTRIBUTES))])+\
                                    LST([self.mdb.Read(a,self.mdb.Read(x,STR(M2ASSOCIATION.DSTNAME))) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.SRCASSOCIATIONS))])+\
                                    LST([self.mdb.Read(a,self.mdb.Read(x,STR(M2COMPOSITION.NAME))) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.PARENTCOMPOSITIONS))])
        res = ApplyToAllElementsInA(context,NON(),fevFunctor)
        return res
    
    def EvalMetAtt(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s instead.'%(MET_MODES.ATT,M1OBJECT.M2CLASS,M2CLASS.ATTRIBUTES))
        attFunctor = lambda a,b: self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.ATTRIBUTES))
        res = ApplyToAllElementsInA(context,None,attFunctor)
        return res
    
    def EvalMetAtn(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s/%s instead.'%(MET_MODES.ATN,M1OBJECT.M2CLASS,M2CLASS.ATTRIBUTES,M2ATTRIBUTE.NAME))
        atnFunctor = lambda a,b: LST([self.mdb.Read(x,STR(M2ATTRIBUTE.NAME)) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.ATTRIBUTES))])
        res = ApplyToAllElementsInA(context,NON(),atnFunctor)
        return res
    
    def EvalMetAtv(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s instead.'%(MET_MODES.ATV,M1OBJECT.M2CLASS,M2CLASS.ATTRIBUTES))
        atvFunctor = lambda a,b: LST([self.mdb.Read(a,self.mdb.Read(x,STR(M2ATTRIBUTE.NAME))) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.ATTRIBUTES))])
        res = ApplyToAllElementsInA(context,NON(),atvFunctor)
        return res
    
    def EvalMetRef(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s instead.'%(MET_MODES.REF,M1OBJECT.M2CLASS,M2CLASS.SRCASSOCIATIONS))
        refFunctor = lambda a,b: self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.SRCASSOCIATIONS))
        res = ApplyToAllElementsInA(context,NON(),refFunctor)
        return res
    
    def EvalMetRen(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s/%s instead.'%(MET_MODES.ATV,M1OBJECT.M2CLASS,M2CLASS.SRCASSOCIATIONS,M2ASSOCIATION.DSTNAME))
        renFunctor = lambda a,b: LST([self.mdb.Read(x,STR(M2ASSOCIATION.DSTNAME)) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.SRCASSOCIATIONS))])
        res = ApplyToAllElementsInA(context,NON(),renFunctor)
        return res
    
    def EvalMetRev(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s instead.'%(MET_MODES.REV,M1OBJECT.M2CLASS,M2CLASS.SRCASSOCIATIONS))
        revFunctor = lambda a,b: LST([self.mdb.Read(a,self.mdb.Read(x,STR(M2ASSOCIATION.DSTNAME))) for x in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.SRCASSOCIATIONS))])
        res = ApplyToAllElementsInA(context,NON(),revFunctor)
        return res
    
    def EvalMetCnt(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s instead.'%(MET_MODES.CNT,M1OBJECT.M2CLASS,M2CLASS.PARENTCOMPOSITIONS))
        cntFunctor = lambda a,b: self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.PARENTCOMPOSITIONS))
        res = ApplyToAllElementsInA(context,NON(),cntFunctor)
        return res
    
    def EvalMetCnn(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CNN,M2CLASS.PARENTCOMPOSITIONS,M2COMPOSITION.NAME))
        cnnFunctor = lambda a,b : LST([self.mdb.Read(c,STR(M2COMPOSITION.NAME)) for c in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.PARENTCOMPOSITIONS))])
        res = ApplyToAllElementsInA(context,NON(),cnnFunctor)
        return res
    
    def EvalMetCnv(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s/%s instead.'%(MET_MODES.CNV,M1OBJECT.M2CLASS,M2CLASS.PARENTCOMPOSITIONS))
        cnvFunctor = lambda a,b: LST([self.mdb.Read(a,self.mdb.Read(c,STR(M2COMPOSITION.NAME))) for c in self.mdb.Read(self.mdb.Read(a,STR(M1OBJECT.M2CLASS)),STR(M2CLASS.PARENTCOMPOSITIONS))])
        res = ApplyToAllElementsInA(context,NON(),cnvFunctor)
        return res
    
    def EvalMetPac(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use /%s instead.'%(MET_MODES.CNT,M2CLASS.PACKAGE))
        pacFunctor = lambda a,b: self.mdb.Read(a,STR(M2CLASS.PACKAGE))
        res = ApplyToAllElementsInA(context,NON(),pacFunctor)
        return res
    
    def EvalMetSty(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CNT,M2CLASS.MYGENERALIZATIONS,M2INHERITANCE.SUPERCLASS))
        styFunctor = lambda a,b: LST([self.mdb.Read(x,STR(M2INHERITANCE.SUPERCLASS)) for x in self.mdb.Read(a,STR(M2CLASS.MYGENERALIZATIONS))])
        res = ApplyToAllElementsInA(context,NON(),styFunctor)
        return res
    
    def EvalMetAls(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CNT,M2CLASS.GENERALIZATIONS,M2INHERITANCE.SUPERCLASS))
        alsFunctor = lambda a,b: LST([self.mdb.Read(x,STR(M2INHERITANCE.SUPERCLASS)) for x in self.mdb.Read(a,STR(M2CLASS.GENERALIZATIONS))])
        res = ApplyToAllElementsInA(context,NON(),alsFunctor)
        return res
    
    def EvalMetImp(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CNT,M2CLASS.SPECIALIZATIONS,M2INHERITANCE.SUBCLASS))
        impFunctor = lambda a,b: LST([self.mdb.Read(x,STR(M2INHERITANCE.SUBCLASS)) for x in self.mdb.Read(a,STR(M2CLASS.SPECIALIZATIONS))])
        res = ApplyToAllElementsInA(context,NON(),impFunctor)
        return res
    
    def EvalMetAli(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s/%s instead.'%(MET_MODES.CNT,M2CLASS.SPECIALIZATIONS,M2INHERITANCE.SUBCLASS))
        aliFunctor = lambda a,b: LST([self.mdb.Read(x,STR(M2INHERITANCE.SUBCLASS)) for x in self.mdb.Read(a,STR(M2CLASS.SPECIALIZATIONS))])
        res = ApplyToAllElementsInA(context,NON(),aliFunctor)
        return res
    
    def EvalMetMmo(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        self.logger.Warn('DEPRECATED: @%s is deprecated, please use %s.%s instead.'%(MET_MODES.MMO,CONCEPTS.MXMDB,MXMDB.M2MODELS))
        (mdb,perr) = self.mdb.Create(STR(CONCEPTS.MXMDB))
        res = self.mdb.Read(mdb,STR(MXMDB.M2MODELS)) 
        return res
    
    def EvalMetIff(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        metaArgs = ValidateVal(args[1], [LST], 'args')
        condition = self.EvalOnContextAndScope(context,metaArgs[0],context,history)
        res = NON()
        if(condition.IsTrue()):
            res = self.EvalOnContextAndScope(context,metaArgs[1],context,history)
        else:
            res = self.EvalOnContextAndScope(context,metaArgs[2],context,history)
        return res
    
    '''
        LOGICAL AND MATH OPERATORS
    '''
    
    def EvalEqu(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.EQU, self.equEvaluators,history)
        return res
    
    def EvalEqa(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        #local functor
        def eqaFunctor(a,b):
            return BOL(a in b)
        #method start
        select = self.EvalOnContextAndScope(context,args[0],context,history)
        if(not IsListOfObjects(select)):
            raise EOQ_ERROR_INVALID_TYPE("Argument must be a list of elements but got: %s"%(select))
        res = ApplyToAllElementsInA(context,select,eqaFunctor)
        return res
    
    def EvalNeq(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.NEQ, self.neqEvaluators,history)
        return res
    
    def EvalLes(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.LES, self.lesEvaluators,history)
        return res
    
    def EvalGre(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.GRE, self.greEvaluators,history)
        return res
    
    def EvalRgx(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        regex = ValidateVal(self.EvalOnContextAndScope(context,args[0],context,history),[STR],'regex')
        if(not isinstance(regex,STR)):
            raise EOQ_ERROR_INVALID_TYPE("Argument must be STR, but got %s."%(args))
        pattern = None
        try:
            pattern = RGX(re.compile(regex.GetVal()))
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("%s is no valid regular expression: %s"%(regex,str(e)))
        res = self.__EvalElementOperation(context, pattern, scope, SEG_TYPES.RGX, self.rgxEvaluators,history)
        return res
    
    def EvalAdd(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.ADD, self.addEvaluators,history)
        return res
    
    def EvalSub(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.SUB, self.subEvaluators,history)
        return res
    
    def EvalMul(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.MUL, self.mulEvaluators,history)
        return res
    
    def EvalDiv(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalElementOperation(context, args[0], scope, SEG_TYPES.DIV, self.divEvaluators,history)
        return res
    
    
    def EvalCsp(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalListOfElementsOperation(context, args[0], scope, SEG_TYPES.CSP, self.cspEvaluator,history)
        return res
    
    def EvalIts(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalListOfElementsOperation(context, args[0], scope, SEG_TYPES.ITS, self.itsEvaluator,history)
        return res
    
    def EvalDif(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalListOfElementsOperation(context, args[0], scope, SEG_TYPES.ITS, self.difEvaluator,history)
        return res
    
    def EvalUni(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalListOfElementsOperation(context, args[0], scope, SEG_TYPES.UNI, self.uniEvaluator,history)
        return res
    
    def EvalCon(self, context:VAL, args:list, scope:VAL, history:History) -> VAL:
        res = self.__EvalListOfElementsOperation(context, args[0], scope, SEG_TYPES.CON, self.conEvaluator,history)
        return res
    
    '''
        PRIVATE METHODS
    '''
   
    def __EvalElementOperation(self, context:VAL, args:list, scope:VAL, operator, opEvaluators, history:History) -> VAL:  
        res = None
        #Define operators
        def opEqualListsFunc(a,b,c):
            return self.__ApplyOperator(a,b,opEvaluators)
        def opOnlyOp1ListFunc(a,b,c):
            op1Functor = lambda o1,o2: self.__ApplyOperator(o1,o2,opEvaluators)
            return ApplyToAllElementsInB(a,b,op1Functor)
        def opOnlyOp2ListFunc(a,b,c):
            op2Functor = lambda o1,o2: self.__ApplyOperator(o1,o2,opEvaluators)
            return ApplyToAllElementsInA(a,b,op2Functor)
    
        op1 = context
        op2 = self.EvalOnContextAndScope(context,args,scope,history)
        
        try:
            res = ApplyToSimilarElementStrutures(op1, op2, opEqualListsFunc, opOnlyOp1ListFunc, opOnlyOp2ListFunc)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Failed to evaluate %s. Context and arguments must be single elements or arrays of same type and size, but got %s %s %s: %s"%(operator,op1,operator,op2,str(e)))
        return res

    def __EvalListOfElementsOperation(self, context:VAL, args:list, scope:VAL, operator, opEvaluator, history:History) -> VAL:  
        res = None
        #Define operators
        def opEqualListsFunc(a,b,c):
            return opEvaluator(a,b)
        def opOnlyOp1ListFunc(a,b,c):
            return ApplyToAllElementsInB(a,b,opEvaluator)
        def opOnlyOp2ListFunc(a,b,c):
            return ApplyToAllElementsInA(a,b,opEvaluator)
    
        op1 = context
        op2 = self.EvalOnContextAndScope(context,args,scope,history)
        
        try:
            res = ApplyToSimilarListsOfObjects(op1, op2, opEqualListsFunc, opOnlyOp1ListFunc, opOnlyOp2ListFunc)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Failed to evaluate %s. Context and arguments must be single elements or arrays of same type and size, but got %s %s %s: %s"%(operator,op1,operator,op2,str(e)))
        return res
                
    def __ApplyOperator(self,a,b,operatorHandlers):
        aType = a.Type()
        bType = b.Type()
        try:
            handler = operatorHandlers[(aType,bType)]
            if(None == handler):
                raise EOQ_ERROR_INVALID_TYPE('Unsupported operation for types %s and %s.'%(aType,bType))
            return handler(a,b)
        except KeyError:
            raise EOQ_ERROR_INVALID_TYPE('Unsupported operation for types %s and %s.'%(aType,bType))
        
    def __Flatten(self,src : VAL,target : LST) -> LST:
        for x in src:
            if(IsList(x)):
                self.__Flatten(x, target)
            else: 
                target.append(x)
        
    def __InitQrySegHandlers(self):
        handlerTable = {}
        handlerTable[SEG_TYPES.OBJ] = self.EvalObj
        handlerTable[SEG_TYPES.ONI] = self.EvalOni
        handlerTable[SEG_TYPES.HIS] = self.EvalHis
        
        handlerTable[SEG_TYPES.PTH] = self.EvalPth
        handlerTable[SEG_TYPES.CLS] = self.EvalCls
        handlerTable[SEG_TYPES.INO] = self.EvalIno
        handlerTable[SEG_TYPES.MET] = self.EvalMet
        handlerTable[SEG_TYPES.NOT] = self.EvalNot
        handlerTable[SEG_TYPES.TRM] = self.EvalTrm
        handlerTable[SEG_TYPES.TRY] = self.EvalTry
        
        handlerTable[SEG_TYPES.QRF] = self.EvalQrf
        handlerTable[SEG_TYPES.STF] = self.EvalStf
        handlerTable[SEG_TYPES.SLF] = self.EvalSlf
        
        handlerTable[SEG_TYPES.IDX] = self.EvalIdx
        handlerTable[SEG_TYPES.SEL] = self.EvalSel
        handlerTable[SEG_TYPES.ARR] = self.EvalArr
        handlerTable[SEG_TYPES.ZIP] = self.EvalZip
        
        handlerTable[SEG_TYPES.ANY] = self.EvalAny
        handlerTable[SEG_TYPES.ALL] = self.EvalAll
        
        handlerTable[SEG_TYPES.EQU] = self.EvalEqu
        handlerTable[SEG_TYPES.EQA] = self.EvalEqa
        handlerTable[SEG_TYPES.NEQ] = self.EvalNeq
        handlerTable[SEG_TYPES.LES] = self.EvalLes
        handlerTable[SEG_TYPES.GRE] = self.EvalGre
        handlerTable[SEG_TYPES.RGX] = self.EvalRgx
        
        handlerTable[SEG_TYPES.ADD] = self.EvalAdd
        handlerTable[SEG_TYPES.SUB] = self.EvalSub
        handlerTable[SEG_TYPES.MUL] = self.EvalMul
        handlerTable[SEG_TYPES.DIV] = self.EvalDiv
        
        #synonyms for boolean operations
        handlerTable[SEG_TYPES.ORR] = self.EvalAdd
        handlerTable[SEG_TYPES.XOR] = self.EvalSub
        handlerTable[SEG_TYPES.AND] = self.EvalMul
        handlerTable[SEG_TYPES.NAD] = self.EvalDiv
        
        handlerTable[SEG_TYPES.CSP] = self.EvalCsp
        handlerTable[SEG_TYPES.ITS] = self.EvalIts
        handlerTable[SEG_TYPES.DIF] = self.EvalDif
        handlerTable[SEG_TYPES.UNI] = self.EvalUni
        handlerTable[SEG_TYPES.CON] = self.EvalCon
        return handlerTable
        
    def __InitMetOperationHandlers(self):
        handlerTable = {}
        handlerTable[MET_MODES.CLS] = self.EvalMetCls
        handlerTable[MET_MODES.CLN] = self.EvalMetCln
        handlerTable[MET_MODES.LEN] = self.EvalMetLen
        handlerTable[MET_MODES.PAR] = self.EvalMetPar
        handlerTable[MET_MODES.CON] = self.EvalMetPar #container is the same as parent
        handlerTable[MET_MODES.ALP] = self.EvalMetAlp
        handlerTable[MET_MODES.ASO] = self.EvalMetAso
        handlerTable[MET_MODES.ALC] = self.EvalMetAlc
        handlerTable[MET_MODES.IDX] = self.EvalMetIdx
        handlerTable[MET_MODES.CFT] = self.EvalMetCft
        handlerTable[MET_MODES.FEA] = self.EvalMetFea
        handlerTable[MET_MODES.FEN] = self.EvalMetFen
        handlerTable[MET_MODES.FEV] = self.EvalMetFev
        handlerTable[MET_MODES.ATT] = self.EvalMetAtt
        handlerTable[MET_MODES.ATN] = self.EvalMetAtn
        handlerTable[MET_MODES.ATV] = self.EvalMetAtv
        handlerTable[MET_MODES.REF] = self.EvalMetRef
        handlerTable[MET_MODES.REN] = self.EvalMetRen
        handlerTable[MET_MODES.REV] = self.EvalMetRev
        handlerTable[MET_MODES.CNT] = self.EvalMetCnt
        handlerTable[MET_MODES.CNN] = self.EvalMetCnn
        handlerTable[MET_MODES.CNV] = self.EvalMetCnv
        #class meta operators
        handlerTable[MET_MODES.PAC] = self.EvalMetPac
        handlerTable[MET_MODES.STY] = self.EvalMetSty
        handlerTable[MET_MODES.ALS] = self.EvalMetAls
        handlerTable[MET_MODES.IMP] = self.EvalMetImp
        handlerTable[MET_MODES.ALI] = self.EvalMetAli
        handlerTable[MET_MODES.MMO] = self.EvalMetMmo
        #control flow operators
        handlerTable[MET_MODES.IFF] = self.EvalMetIff
        return handlerTable
    
    
    def __InitOpHandlerEnt(self,aType,bolHandler,\
                           u32Handler,u64Handler,\
                           i32Handler,i64Handler,\
                           f32Handler,f64Handler,\
                           strHandler,datHandler,\
                           qryHandler,\
                           nonHandler,trmHandler):
        return {(aType,BOL):bolHandler,
                (aType,U32):u32Handler,
                (aType,U64):u64Handler,
                (aType,I32):i32Handler,
                (aType,I64):i64Handler,
                (aType,F32):f32Handler,
                (aType,F64):f64Handler,
                (aType,STR):strHandler,
                (aType,DAT):datHandler,
                (aType,QRY):qryHandler,
                (aType,NON):nonHandler,
                (aType,TRM):trmHandler}
            
        
    def __InitEquOperationHandlers(self):
        handlerTable = {}
        #handler functors
        XvX = lambda a,b: BOL(a==b) #any combination
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, XvX , None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, XvX , XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, XvX , None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
    
    def __InitNeqOperationHandlers(self):
        handlerTable = {}
        #handler functors
        XvX = lambda a,b: BOL(a!=b) #any combination
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, XvX , None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, XvX , XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
    
    def __InitGreOperationHandlers(self):
        handlerTable = {}
        #handler functors
        XvX = lambda a,b: BOL(a>b) #any combination
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, XvX , None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, XvX , None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
    
    def __InitLesOperationHandlers(self):
        handlerTable = {}
        #handler functors
        XvX = lambda a,b: BOL(a<b) #any combination
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, XvX , None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, XvX , None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
        
    def __InitRgxOperationHandlers(self):
        handlerTable = {}
        #handler functors
        XvS = lambda a,b: BOL(True) if(b.GetVal().search(a.GetVal())) else BOL(False) #only string can be the second argument. 
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvS , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
    
    def __InitAddOperationHandlers(self):
        handlerTable = {}
        #handler functors STR > BOL > DBL > FLO > INT > OBJ > NON
        XvX = lambda a,b: a+b #only for numeric types, i.e. INT, FLO, DBL
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, XvX , None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
    
    def __InitSubOperationHandlers(self):
        handlerTable = {}
        #handler functors STR > BOL > DBL > FLO > INT > OBJ > NON
        XvX = lambda a,b: a-b #only for numeric types, i.e. INT, FLO, DBL
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, XvX , None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable

       
    def __InitMulOperationHandlers(self):
        handlerTable = {}
        #handler functors STR > BOL > DBL > FLO > INT > OBJ > NON
        XvX = lambda a,b: a*b #only for numeric types, i.e. INT, FLO, DBL
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
        
    def __InitDivOperationHandlers(self):
        handlerTable = {}
        #handler functors STR > BOL > DBL > FLO > INT > OBJ > NON
        XvX = lambda a,b: a/b #only for numeric types, i.e. INT, FLO, DBL
        # create a handler entry and compatibility list for every primitive type combination.
        # None indicates incompatible operations      
        #                                           first operator type        , BOL , INT , FLO , DBL , STR , OBJ , NON , TRM
                # first operator type                            BOL , U32 , U64 , I32 , I64 , F32 , F64 , STR , DAT , QRY , NON , TRM
        handlerTable.update(self.__InitOpHandlerEnt(BOL, XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , XvX , None))
        handlerTable.update(self.__InitOpHandlerEnt(U32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(U64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(I64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F32, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(F64, None, XvX , XvX , XvX , XvX , XvX , XvX , None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(STR, None, None, None, None, None, None, None, XvX , None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(DAT, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(QRY, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(NON, None, None, None, None, None, None, None, None, None, None, None, None))
        handlerTable.update(self.__InitOpHandlerEnt(TRM, TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX , TvX )) 
        return handlerTable
    
    def __DeprecatedWarning(self, message:str):
        self.logger.Warn("%s is deprecated. Consider replacement."%(message))
                
        
                