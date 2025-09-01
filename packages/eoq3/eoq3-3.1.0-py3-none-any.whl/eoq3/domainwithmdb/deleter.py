'''
 deleter.py recursive delete function for a model tree based on concepts. 
 
 This file is generated form: deleter.py.mako on 2025-07-16 09:22:16.214051 by calling E:/1_ILS/Projects/2018_EOQ/Groups/PYEOQ/pyeoq/eoq3conceptsgen/generatefromconceptscli.py -i deleter.py.mako -o ../deleter.py.
 
 Bjoern Annighoefer 2023
'''

from ..concepts import CONCEPTS, MXMDB ,MXELEMENT ,MXCONSTRAINT ,M2PRIMITIVES ,M2PACKAGE ,M2MODEL ,M2ENUM ,M2OPTIONOFENUM ,M2CLASS ,M2ATTRIBUTE ,M2ASSOCIATION ,M2COMPOSITION ,M2INHERITANCE ,M1MODEL ,M1OBJECT ,M1FEATURE ,M1ATTRIBUTE ,M1ASSOCIATION ,M1COMPOSITION
from ..value import VAL, STR, NON, LST, I64
from ..query import Obj
from ..error import EOQ_ERROR_RUNTIME
from .util import IsList

from .conceptwalker import ConceptWalker

from typing import Tuple, Any, Dict, List

class DeleterRun:
    '''This class is used to maintain global information in one delete call
    '''
    def __init__(self):
        self.deletedElements:Dict[Obj,bool] = {} # the delete path in the model is not circle free and cannot be circle free, so need this to trac deleted elements
        self.deleteChain:List[Obj] = [] #the order in which objects are deleted at the end
        self.result:Tuple[STR,LST,LST] = (NON(),LST([]),LST([])) #the return value of the last delete command
 

class Deleter(ConceptWalker):
    def __init__(self,cmdrunner,logger):
        super().__init__(cmdrunner)
        self.logger = logger
        
    def DeleteAuto(self, target, tid)->Tuple[STR,LST,LST]:
        '''Delete target and its delete path properties.
        '''
        deleterRun = DeleterRun()
        # use walk to collect objects to delete and order, but do not delete, because that would change the struture during walk
        # moreover unset any attribute to enable deletion afterwards
        self.Walk(tid,target,NON(),1,deleterRun)
        #when walk is finished, elements can be deleted
        for e in deleterRun.deleteChain:
            deleterRun.result = self.cmdrunner._MdbDelete(tid,e)
        return deleterRun.result
        
    def DeleteFull(self, target:Obj, tid:int)->Tuple[STR,LST,LST]:
        '''Delete target and its delete path properties recursively
        '''
        deleterRun = DeleterRun()
        # use walk to collect objects to delete and order, but do not delete, because that would change the struture during walk
        # moreover unset any attribute to enable deletion afterwards
        self.Walk(tid,target,NON(),-1,deleterRun)
        #when walk is finished, elements can be deleted
        for e in deleterRun.deleteChain:
            deleterRun.result = self.cmdrunner._MdbDelete(tid,e)
        return deleterRun.result
    
    def __MdbDelete(self, tid:int, target:Obj, deleterRun:DeleterRun)->None:
        if(target not in deleterRun.deletedElements):
            deleterRun.result = self.cmdrunner._MdbDelete(tid,target)
            deleterRun.deletedElements[target] = True
            
    def __MarkForDeletion(self, tid:int, target:Obj, deleterRun:DeleterRun)->None:
        if(target not in deleterRun.deletedElements):
            deleterRun.deleteChain.append(target)
            deleterRun.deletedElements[target] = True
    
    def __MdbUpdate(self, tid:int, target:Obj, featureName:STR, value:VAL, pos:I64):
            self.cmdrunner._MdbUpdate(tid,target,featureName,value,pos)

    #@override
    def _OnExitMxMdb(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        # M2MODELS
        elements = self.cmdrunner._MdbRead(tid,target,STR(MXMDB.M2MODELS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MarkForDeletion(tid,e,data)
        # M1MODELS
        elements = self.cmdrunner._MdbRead(tid,target,STR(MXMDB.M1MODELS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MarkForDeletion(tid,e,data)
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitMxElement(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        # DOCUMENTATION
        e = self.cmdrunner._MdbRead(tid,target,STR(MXELEMENT.DOCUMENTATION))
        if(not e.IsNone()): i=0; self.__MdbUpdate(tid,target,STR(MXELEMENT.DOCUMENTATION),NON(),i)
        # OWNER
        e = self.cmdrunner._MdbRead(tid,target,STR(MXELEMENT.OWNER))
        if(not e.IsNone()): i=0; self.__MdbUpdate(tid,target,STR(MXELEMENT.OWNER),NON(),i)
        # GROUP
        e = self.cmdrunner._MdbRead(tid,target,STR(MXELEMENT.GROUP))
        if(not e.IsNone()): i=0; self.__MdbUpdate(tid,target,STR(MXELEMENT.GROUP),NON(),i)
        # PERMISSIONS
        elements = self.cmdrunner._MdbRead(tid,target,STR(MXELEMENT.PERMISSIONS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MdbUpdate(tid,target,STR(MXELEMENT.PERMISSIONS),NON(),i)
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitMxConstraint(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Primitives(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Package(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Enum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2OptionOfEnum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Class(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        # MYDSTASSOCIATIONS
        elements = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYDSTASSOCIATIONS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MarkForDeletion(tid,e,data)
        # MYCHILDCOMPOSITIONS
        elements = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYCHILDCOMPOSITIONS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MarkForDeletion(tid,e,data)
        # MYSPECIALIZATIONS
        elements = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYSPECIALIZATIONS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MarkForDeletion(tid,e,data)
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM2Inheritance(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM1Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM1Object(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        # DSTASSOCIATIONS
        elements = self.cmdrunner._MdbRead(tid,target,STR(M1OBJECT.DSTASSOCIATIONS))
        nElements = len(elements)
        if(0<nElements):
            for i in range(nElements-1,-1,-1):
                e = elements[i]
                self.__MarkForDeletion(tid,e,data)
        # CHILDCOMPOSITION
        e = self.cmdrunner._MdbRead(tid,target,STR(M1OBJECT.CHILDCOMPOSITION))
        if(not e.IsNone()): i=0; self.__MarkForDeletion(tid,e,data)
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM1Feature(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM1Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM1Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

    #@override
    def _OnExitM1Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any):
        if(successor!=target): #prevent the delete call for super
            self.__MarkForDeletion(tid,target,data)

