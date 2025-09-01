'''
 deleter.py recursive delete function for a model tree based on concepts. 
 
 This file is generated form: cloner.py.mako on 2025-07-16 09:22:01.221006 by calling E:/1_ILS/Projects/2018_EOQ/Groups/PYEOQ/pyeoq/eoq3conceptsgen/generatefromconceptscli.py -i cloner.py.mako -o ../cloner.py.
 
 Bjoern Annighoefer 2023
'''

from ..concepts import CONCEPTS, MXMDB ,MXELEMENT ,MXCONSTRAINT ,M2PRIMITIVES ,M2PACKAGE ,M2MODEL ,M2ENUM ,M2OPTIONOFENUM ,M2CLASS ,M2ATTRIBUTE ,M2ASSOCIATION ,M2COMPOSITION ,M2INHERITANCE ,M1MODEL ,M1OBJECT ,M1FEATURE ,M1ATTRIBUTE ,M1ASSOCIATION ,M1COMPOSITION
from ..value import VAL, STR, NON, LST, I64
from ..query import Obj
from ..command import CLO_MODES
from ..error import EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_INVALID_OPERATION

from .conceptwalker import ConceptWalker

from typing import Tuple, Any, Dict, List

class CloneInfo:
    def __init__(self, original:Obj, concept:STR, createArgNames:LST, createArgs:LST):
        self.original:Obj = original
        self.concept:str = concept
        self.createArgNames:LST = createArgNames
        self.createArgs:LST = createArgs
        self.clone = None

class CloneFulRun:
    '''This class is used to maintain global information in one delete call
    '''
    def __init__(self):
        self.elementsToClone:Dict[int,Obj] = {} #a dict sorting elements by order
        self.cloneInfoLut:Dict[Obj,CloneInfo] = {} #a look-up table for clone information

class Cloner(ConceptWalker):
    def __init__(self, cmdrunner, logger):
        super().__init__(cmdrunner)
        self.logger = logger
        #createArgs get handlers
        self.handlers = {}
        self.handlers[CONCEPTS.MXCONSTRAINT] = (self.__GetCreateArgsMxConstraint,self.__CopyBasePropertiesMxConstraint)
        self.handlers[CONCEPTS.M2PACKAGE] = (self.__GetCreateArgsM2Package,self.__CopyBasePropertiesM2Package)
        self.handlers[CONCEPTS.M2MODEL] = (self.__GetCreateArgsM2Model,self.__CopyBasePropertiesM2Model)
        self.handlers[CONCEPTS.M2ENUM] = (self.__GetCreateArgsM2Enum,self.__CopyBasePropertiesM2Enum)
        self.handlers[CONCEPTS.M2OPTIONOFENUM] = (self.__GetCreateArgsM2OptionOfEnum,self.__CopyBasePropertiesM2OptionOfEnum)
        self.handlers[CONCEPTS.M2CLASS] = (self.__GetCreateArgsM2Class,self.__CopyBasePropertiesM2Class)
        self.handlers[CONCEPTS.M2ATTRIBUTE] = (self.__GetCreateArgsM2Attribute,self.__CopyBasePropertiesM2Attribute)
        self.handlers[CONCEPTS.M2ASSOCIATION] = (self.__GetCreateArgsM2Association,self.__CopyBasePropertiesM2Association)
        self.handlers[CONCEPTS.M2COMPOSITION] = (self.__GetCreateArgsM2Composition,self.__CopyBasePropertiesM2Composition)
        self.handlers[CONCEPTS.M2INHERITANCE] = (self.__GetCreateArgsM2Inheritance,self.__CopyBasePropertiesM2Inheritance)
        self.handlers[CONCEPTS.M1MODEL] = (self.__GetCreateArgsM1Model,self.__CopyBasePropertiesM1Model)
        self.handlers[CONCEPTS.M1OBJECT] = (self.__GetCreateArgsM1Object,self.__CopyBasePropertiesM1Object)
        self.handlers[CONCEPTS.M1ATTRIBUTE] = (self.__GetCreateArgsM1Attribute,self.__CopyBasePropertiesM1Attribute)
        self.handlers[CONCEPTS.M1ASSOCIATION] = (self.__GetCreateArgsM1Association,self.__CopyBasePropertiesM1Association)
        self.handlers[CONCEPTS.M1COMPOSITION] = (self.__GetCreateArgsM1Composition,self.__CopyBasePropertiesM1Composition)

    def Clone(self, original:Obj, mode:STR, createArgOverrides:LST, tid:int)->Obj:
        ''' Clones an element according to the given mode and create arg overrides
        This is the main entry point into the function
        '''
        concept = self.__CheckCanClone(tid, original)
        self.__ValidateCreateArgOverrides(createArgOverrides)
        clone = NON()
        if(CLO_MODES.MIN==mode):
            clone = self.__CloneMinimum(tid, original,concept,createArgOverrides)
        elif(CLO_MODES.BAS==mode):
            clone = self.__CloneBase(tid, original,concept,createArgOverrides)
        elif(CLO_MODES.FUL==mode):
            clone = self.__CloneFull(tid, original,concept,createArgOverrides)
        return clone
    
    # CLONE MODE IMPLEMENTASIONS
    
    def __CheckCanClone(self, tid:int, original:Obj)->str:
        concept = self.cmdrunner._MdbRead(tid,original,STR(MXELEMENT.CONCEPT))
        if( concept not in self.handlers):
            raise EOQ_ERROR_INVALID_OPERATION("Cannot clone %s"%(concept))
        return concept.GetVal()
        
    def __CloneMinimum(self, tid:int, original:Obj, concept:str, createArgOverrides:LST)->Obj:
        '''Implements clone mode MIN
        '''
        (createArgNames,createArgs) = self.__GetCreateInfo(tid,original,concept)
        cloneCreateArgs = self.__OverrideCreateArgs(concept,createArgNames,createArgs,createArgOverrides)
        clone = self.cmdrunner._MdbCreate(tid,STR(concept),cloneCreateArgs)
        return clone
    
    def __CloneBase(self, tid:int, original:Obj, concept:str, createArgOverrides:LST)->Obj:
        clone = self.__CloneMinimum(tid,original,concept,createArgOverrides)
        copyBasePropertiesHandler = self.handlers[concept][1] # No try necessary, because checked before 
        copyBasePropertiesHandler(tid,original,clone)
        return clone
    
    def __CloneFull(self, tid:int, original:Obj, concept:str, createArgOverrides:LST)->Obj:
        clone = NON()
        cloneRun = CloneFulRun()
        # 1 collect all elements to be cloned
        self.Walk(tid,original,None,-1,cloneRun)
        # 2 arrange elements such that they can be cloned in that order without 
        # violating dependencies and remove the root element, which was already cloned.
        conflictfreeCloneChain = [e for k,e in sorted(cloneRun.elementsToClone.items())]
        # 4 cloning elements from the elementsToClone is straight forward
        for o in conflictfreeCloneChain:
            originalInfo = cloneRun.cloneInfoLut[o]
            internalOverrides = self.__CreateArgOverrides(originalInfo,cloneRun.cloneInfoLut)
            if(o == original):
                self.__UpdateCreateArgOverwrites(internalOverrides,createArgOverrides)
                clone = self.__CloneBase(tid,original,concept,internalOverrides)
                cloneRun.cloneInfoLut[original].clone = clone
            else:
                originalInfo.clone = self.__CloneBase(tid,o,originalInfo.concept,internalOverrides)
        return clone
    
    # AUXILLIARY METHODS
    
    def __UpdateCreateArgOverwrites(self,updatedOverwrites:LST, newOverwrites:LST):
        nNewOverwrites = len(newOverwrites)
        nUpdatedOverwrites = len(updatedOverwrites)
        for i in range(0,nNewOverwrites,2):
            matchFound = False
            for j in range(0,nUpdatedOverwrites,2):
                if(updatedOverwrites[j] == newOverwrites[i]):
                    updatedOverwrites[j+1] = newOverwrites[i+1]
                    matchFound = True
                    break
            if(not matchFound): 
                #no match was found add the values
                updatedOverwrites.append(newOverwrites[i])
                updatedOverwrites.append(newOverwrites[i+1])
    
    def __MdbUpdate(self, tid:int, target:Obj, featureName:STR, value:VAL, pos:I64):
        self.cmdrunner._MdbUpdate(tid,target,featureName,value,pos)
            
    def __ValidateCreateArgOverrides(self, createArgOverrides:LST)->bool:
        nOverrides = len(createArgOverrides)
        if(0 != nOverrides % 2):
            raise EOQ_ERROR_INVALID_VALUE("Number of entries in createArgOverrides must be even.")
        for i in range(0,nOverrides,2):
            if(STR != type(createArgOverrides[i])):
                raise EOQ_ERROR_INVALID_TYPE("createArgOverrides[%d] must be string."%(i))
        return True
    
    def __GetCreateInfo(self, tid:int, original:Obj, concept:str)->Tuple[STR,List[STR],List[VAL]]:
        ''' Figures out the concept type and then calls the specific 
        function to return the create arg names and values for this concept type
        '''
        createArgsGetHandler = self.handlers[concept][0] #cannot fail, because concept was checked before
        (createArgNames,createArgs) = createArgsGetHandler(tid,original)
        return (createArgNames,createArgs)
    
    def __OverrideCreateArgs(self, concept:STR, createArgNames:List[STR], createArgs:List[VAL], createArgOverrides:LST)->LST:
        ''' This replaces values in an createArgs list 
        according to a given createArgOverrites list.
        It returns the new createArgs with the replaced values
        '''
        updatedCreateArgs = list(createArgs)
        for i in range(0,len(createArgOverrides),2):
            overrideName = createArgOverrides[i]
            try:
                j = createArgNames.index(overrideName)
                updatedCreateArgs[j] = createArgOverrides[i+1]
            except ValueError:
                raise EOQ_ERROR_INVALID_VALUE("%s is no create arg of %s."%(overrideName,concept))
        return LST(updatedCreateArgs)
    
    def __CreateArgOverrides(self, originalInfo:CloneInfo, cloneInfoLut:Dict[Obj,CloneInfo])->LST:
        '''Creates the createArgOverrides list from all elements cloned so far
        '''
        createArgOverrides = LST([])
        for i in range(len(originalInfo.createArgNames)):
            o = originalInfo.createArgs[i]
            if(isinstance(o,Obj)):
                try:
                    c = cloneInfoLut[o].clone
                    createArgOverrides.append(originalInfo.createArgNames[i])
                    createArgOverrides.append(c)
                except KeyError:
                    pass # no need to replace this argument, it has no clone
        return createArgOverrides;

    # ## CONCEPT WALKER SPECIALIZATION

    #@override
    def _OnEnterMxConstraint(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsMxConstraint(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.MXCONSTRAINT,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Package(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Package(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2PACKAGE,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Model(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2MODEL,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Enum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Enum(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2ENUM,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2OptionOfEnum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2OptionOfEnum(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2OPTIONOFENUM,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Class(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Class(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2CLASS,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Attribute(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2ATTRIBUTE,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Association(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2ASSOCIATION,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Composition(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2COMPOSITION,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM2Inheritance(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM2Inheritance(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M2INHERITANCE,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM1Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM1Model(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M1MODEL,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM1Object(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM1Object(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M1OBJECT,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM1Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM1Attribute(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M1ATTRIBUTE,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM1Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM1Association(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M1ASSOCIATION,createArgNames,createArgs)
            data.elementsToClone[order] = target
    #@override
    def _OnEnterM1Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        '''Collections all concepts (not super concepts) to build a causal chain for cloning
        '''
        if(target != successor and target not in data.cloneInfoLut):
            #only return elements if this is not a super concept walk
            (createArgNames,createArgs) = self.__GetCreateArgsM1Composition(tid,target)
            order = target.v[0] #TODO: implement official method for order
            data.cloneInfoLut[target] = CloneInfo(target,CONCEPTS.M1COMPOSITION,createArgNames,createArgs)
            data.elementsToClone[order] = target
    # ## GET CREATE ARG HANDLERS

    def __GetCreateArgsMxConstraint(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pElement = self.cmdrunner._MdbRead(tid,original,STR(MXCONSTRAINT.ELEMENT))
        pExpression = self.cmdrunner._MdbRead(tid,original,STR(MXCONSTRAINT.EXPRESSION))
        createArgNames = [STR(MXCONSTRAINT.ELEMENT), STR(MXCONSTRAINT.EXPRESSION)]
        createArgs = [pElement, pExpression]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Package(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2PACKAGE.NAME))
        pSuperpackage = self.cmdrunner._MdbRead(tid,original,STR(M2PACKAGE.SUPERPACKAGE))
        createArgNames = [STR(M2PACKAGE.NAME), STR(M2PACKAGE.SUPERPACKAGE)]
        createArgs = [pName, pSuperpackage]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Model(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2PACKAGE.NAME))
        createArgNames = [STR(M2PACKAGE.NAME)]
        createArgs = [pName]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Enum(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2ENUM.NAME))
        pPackage = self.cmdrunner._MdbRead(tid,original,STR(M2ENUM.PACKAGE))
        createArgNames = [STR(M2ENUM.NAME), STR(M2ENUM.PACKAGE)]
        createArgs = [pName, pPackage]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2OptionOfEnum(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2OPTIONOFENUM.NAME))
        pValue = self.cmdrunner._MdbRead(tid,original,STR(M2OPTIONOFENUM.VALUE))
        pEnum = self.cmdrunner._MdbRead(tid,original,STR(M2OPTIONOFENUM.ENUM))
        createArgNames = [STR(M2OPTIONOFENUM.NAME), STR(M2OPTIONOFENUM.VALUE), STR(M2OPTIONOFENUM.ENUM)]
        createArgs = [pName, pValue, pEnum]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Class(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2CLASS.NAME))
        pIsabstract = self.cmdrunner._MdbRead(tid,original,STR(M2CLASS.ISABSTRACT))
        pPackage = self.cmdrunner._MdbRead(tid,original,STR(M2CLASS.PACKAGE))
        createArgNames = [STR(M2CLASS.NAME), STR(M2CLASS.ISABSTRACT), STR(M2CLASS.PACKAGE)]
        createArgs = [pName, pIsabstract, pPackage]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Attribute(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2ATTRIBUTE.NAME))
        pClass = self.cmdrunner._MdbRead(tid,original,STR(M2ATTRIBUTE.CLASS))
        pPrimtype = self.cmdrunner._MdbRead(tid,original,STR(M2ATTRIBUTE.PRIMTYPE))
        pMul = self.cmdrunner._MdbRead(tid,original,STR(M2ATTRIBUTE.MUL))
        pUnit = self.cmdrunner._MdbRead(tid,original,STR(M2ATTRIBUTE.UNIT))
        pEnum = self.cmdrunner._MdbRead(tid,original,STR(M2ATTRIBUTE.ENUM))
        createArgNames = [STR(M2ATTRIBUTE.NAME), STR(M2ATTRIBUTE.CLASS), STR(M2ATTRIBUTE.PRIMTYPE), STR(M2ATTRIBUTE.MUL), STR(M2ATTRIBUTE.UNIT), STR(M2ATTRIBUTE.ENUM)]
        createArgs = [pName, pClass, pPrimtype, pMul, pUnit, pEnum]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Association(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pSrcname = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.SRCNAME))
        pSrcclass = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.SRCCLASS))
        pSrcmul = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.SRCMUL))
        pDstname = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.DSTNAME))
        pDstclass = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.DSTCLASS))
        pDstmul = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.DSTMUL))
        pAnydst = self.cmdrunner._MdbRead(tid,original,STR(M2ASSOCIATION.ANYDST))
        createArgNames = [STR(M2ASSOCIATION.SRCNAME), STR(M2ASSOCIATION.SRCCLASS), STR(M2ASSOCIATION.SRCMUL), STR(M2ASSOCIATION.DSTNAME), STR(M2ASSOCIATION.DSTCLASS), STR(M2ASSOCIATION.DSTMUL), STR(M2ASSOCIATION.ANYDST)]
        createArgs = [pSrcname, pSrcclass, pSrcmul, pDstname, pDstclass, pDstmul, pAnydst]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Composition(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pName = self.cmdrunner._MdbRead(tid,original,STR(M2COMPOSITION.NAME))
        pParentclass = self.cmdrunner._MdbRead(tid,original,STR(M2COMPOSITION.PARENTCLASS))
        pChildclass = self.cmdrunner._MdbRead(tid,original,STR(M2COMPOSITION.CHILDCLASS))
        pMulchild = self.cmdrunner._MdbRead(tid,original,STR(M2COMPOSITION.MULCHILD))
        pAnychild = self.cmdrunner._MdbRead(tid,original,STR(M2COMPOSITION.ANYCHILD))
        createArgNames = [STR(M2COMPOSITION.NAME), STR(M2COMPOSITION.PARENTCLASS), STR(M2COMPOSITION.CHILDCLASS), STR(M2COMPOSITION.MULCHILD), STR(M2COMPOSITION.ANYCHILD)]
        createArgs = [pName, pParentclass, pChildclass, pMulchild, pAnychild]
        return (createArgNames,createArgs)

    def __GetCreateArgsM2Inheritance(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pSubclass = self.cmdrunner._MdbRead(tid,original,STR(M2INHERITANCE.SUBCLASS))
        pSuperclass = self.cmdrunner._MdbRead(tid,original,STR(M2INHERITANCE.SUPERCLASS))
        createArgNames = [STR(M2INHERITANCE.SUBCLASS), STR(M2INHERITANCE.SUPERCLASS)]
        createArgs = [pSubclass, pSuperclass]
        return (createArgNames,createArgs)

    def __GetCreateArgsM1Model(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pM2Model = self.cmdrunner._MdbRead(tid,original,STR(M1MODEL.M2MODEL))
        pName = self.cmdrunner._MdbRead(tid,original,STR(M1MODEL.NAME))
        createArgNames = [STR(M1MODEL.M2MODEL), STR(M1MODEL.NAME)]
        createArgs = [pM2Model, pName]
        return (createArgNames,createArgs)

    def __GetCreateArgsM1Object(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pM2Class = self.cmdrunner._MdbRead(tid,original,STR(M1OBJECT.M2CLASS))
        pModel = self.cmdrunner._MdbRead(tid,original,STR(M1OBJECT.MODEL))
        pName = self.cmdrunner._MdbRead(tid,original,STR(M1OBJECT.NAME))
        createArgNames = [STR(M1OBJECT.M2CLASS), STR(M1OBJECT.MODEL), STR(M1OBJECT.NAME)]
        createArgs = [pM2Class, pModel, pName]
        return (createArgNames,createArgs)

    def __GetCreateArgsM1Attribute(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pM2Attribute = self.cmdrunner._MdbRead(tid,original,STR(M1ATTRIBUTE.M2ATTRIBUTE))
        pObject = self.cmdrunner._MdbRead(tid,original,STR(M1ATTRIBUTE.OBJECT))
        pValue = self.cmdrunner._MdbRead(tid,original,STR(M1ATTRIBUTE.VALUE))
        createArgNames = [STR(M1ATTRIBUTE.M2ATTRIBUTE), STR(M1ATTRIBUTE.OBJECT), STR(M1ATTRIBUTE.VALUE)]
        createArgs = [pM2Attribute, pObject, pValue]
        return (createArgNames,createArgs)

    def __GetCreateArgsM1Association(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pM2Association = self.cmdrunner._MdbRead(tid,original,STR(M1ASSOCIATION.M2ASSOCIATION))
        pSrc = self.cmdrunner._MdbRead(tid,original,STR(M1ASSOCIATION.SRC))
        pDst = self.cmdrunner._MdbRead(tid,original,STR(M1ASSOCIATION.DST))
        createArgNames = [STR(M1ASSOCIATION.M2ASSOCIATION), STR(M1ASSOCIATION.SRC), STR(M1ASSOCIATION.DST)]
        createArgs = [pM2Association, pSrc, pDst]
        return (createArgNames,createArgs)

    def __GetCreateArgsM1Composition(self, tid:int, original:Obj)->Tuple[List[STR],List[VAL]]:
        pM2Composition = self.cmdrunner._MdbRead(tid,original,STR(M1COMPOSITION.M2COMPOSITION))
        pParent = self.cmdrunner._MdbRead(tid,original,STR(M1COMPOSITION.PARENT))
        pChild = self.cmdrunner._MdbRead(tid,original,STR(M1COMPOSITION.CHILD))
        createArgNames = [STR(M1COMPOSITION.M2COMPOSITION), STR(M1COMPOSITION.PARENT), STR(M1COMPOSITION.CHILD)]
        createArgs = [pM2Composition, pParent, pChild]
        return (createArgNames,createArgs)

    # ## COPY BASE PROPERTIES HANDELRS

    def __CopyBasePropertiesMxElement(self, tid:int, original:Obj, clone:Obj):
        documentation = self.cmdrunner._MdbRead(tid,original,STR(MXELEMENT.DOCUMENTATION))
        if(not documentation.IsNone()):
            self.__MdbUpdate(tid,clone,STR(MXELEMENT.DOCUMENTATION),documentation,I64(0))
        owner = self.cmdrunner._MdbRead(tid,original,STR(MXELEMENT.OWNER))
        if(not owner.IsNone()):
            self.__MdbUpdate(tid,clone,STR(MXELEMENT.OWNER),owner,I64(0))
        group = self.cmdrunner._MdbRead(tid,original,STR(MXELEMENT.GROUP))
        if(not group.IsNone()):
            self.__MdbUpdate(tid,clone,STR(MXELEMENT.GROUP),group,I64(0))
        permissions = self.cmdrunner._MdbRead(tid,original,STR(MXELEMENT.PERMISSIONS))
        for v in permissions:
            self.__MdbUpdate(tid,clone,STR(MXELEMENT.PERMISSIONS),permissions,I64(-1))

    def __CopyBasePropertiesMxConstraint(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Package(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Model(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesM2Package(tid,original,clone)

    def __CopyBasePropertiesM2Enum(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2OptionOfEnum(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Class(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Attribute(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Association(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Composition(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM2Inheritance(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM1Model(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM1Object(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM1Feature(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesMxElement(tid,original,clone)

    def __CopyBasePropertiesM1Attribute(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesM1Feature(tid,original,clone)

    def __CopyBasePropertiesM1Association(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesM1Feature(tid,original,clone)

    def __CopyBasePropertiesM1Composition(self, tid:int, original:Obj, clone:Obj):
        self.__CopyBasePropertiesM1Feature(tid,original,clone)

