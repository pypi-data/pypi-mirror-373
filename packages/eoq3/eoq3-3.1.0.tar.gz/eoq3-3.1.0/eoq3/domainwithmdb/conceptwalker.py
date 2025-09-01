'''
 conceptwalker.py a class that can walk through the clone path of concepts. 
 This is meant to be inherited by other classes to carry out certain actions.
 
 This file is generated form: conceptwalker.py.mako on 2025-07-16 09:22:09.674781 by calling E:/1_ILS/Projects/2018_EOQ/Groups/PYEOQ/pyeoq/eoq3conceptsgen/generatefromconceptscli.py -i conceptwalker.py.mako -o ../conceptwalker.py.
 
 Bjoern Annighoefer 2023
'''

from ..concepts import CONCEPTS, MXMDB ,MXELEMENT ,MXCONSTRAINT ,M2PRIMITIVES ,M2PACKAGE ,M2MODEL ,M2ENUM ,M2OPTIONOFENUM ,M2CLASS ,M2ATTRIBUTE ,M2ASSOCIATION ,M2COMPOSITION ,M2INHERITANCE ,M1MODEL ,M1OBJECT ,M1FEATURE ,M1ATTRIBUTE ,M1ASSOCIATION ,M1COMPOSITION
from ..value import STR, NON, LST
from ..query import Obj
from ..error import EOQ_ERROR_RUNTIME

from typing import Any


class ConceptWalker:
    def __init__(self, cmdrunner):
        self.cmdrunner = cmdrunner
        self.walkerHandlers = {}
        self.walkerHandlers["*MXMDB"] = self._WalkMxMdb
        self.walkerHandlers["*MXCONSTRAINT"] = self._WalkMxConstraint
        self.walkerHandlers["*M2PACKAGE"] = self._WalkM2Package
        self.walkerHandlers["*M2MODEL"] = self._WalkM2Model
        self.walkerHandlers["*M2ENUM"] = self._WalkM2Enum
        self.walkerHandlers["*M2OPTIONOFENUM"] = self._WalkM2OptionOfEnum
        self.walkerHandlers["*M2CLASS"] = self._WalkM2Class
        self.walkerHandlers["*M2ATTRIBUTE"] = self._WalkM2Attribute
        self.walkerHandlers["*M2ASSOCIATION"] = self._WalkM2Association
        self.walkerHandlers["*M2COMPOSITION"] = self._WalkM2Composition
        self.walkerHandlers["*M2INHERITANCE"] = self._WalkM2Inheritance
        self.walkerHandlers["*M1MODEL"] = self._WalkM1Model
        self.walkerHandlers["*M1OBJECT"] = self._WalkM1Object
        self.walkerHandlers["*M1ATTRIBUTE"] = self._WalkM1Attribute
        self.walkerHandlers["*M1ASSOCIATION"] = self._WalkM1Association
        self.walkerHandlers["*M1COMPOSITION"] = self._WalkM1Composition

    def Walk(self, tid:int, target:Obj, successor:Obj, maxRecursion:int=-1, data:Any=None)->Any:
        conceptId = self.cmdrunner._MdbRead(tid,target,STR(MXELEMENT.CONCEPT)).GetVal()
        try:
            handler = self.walkerHandlers[conceptId]
            res = handler(tid,target,successor,maxRecursion,data)
        except KeyError:
            raise EOQ_ERROR_RUNTIME("Cannot walk element %s of type %s"%(str(target),conceptId))

    def _WalkMxMdb(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterMxMdb(tid,target,successor,maxRecursion,data)
        self._OnExitMxMdb(tid,target,successor,maxRecursion,data)

    def _WalkMxElement(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterMxElement(tid,target,successor,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # CONSTRAINTS
            constraints = self.cmdrunner._MdbRead(tid,target,STR(MXELEMENT.CONSTRAINTS))
            for e in constraints:
                self._WalkMxConstraint(tid,e,target,maxRecursion-1,data)
        self._OnExitMxElement(tid,target,successor,maxRecursion,data)

    def _WalkMxConstraint(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterMxConstraint(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitMxConstraint(tid,target,successor,maxRecursion,data)

    def _WalkM2Primitives(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Primitives(tid,target,successor,maxRecursion,data)
        self._OnExitM2Primitives(tid,target,successor,maxRecursion,data)

    def _WalkM2Package(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Package(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # SUBPACKAGES
            subpackages = self.cmdrunner._MdbRead(tid,target,STR(M2PACKAGE.SUBPACKAGES))
            for e in subpackages:
                self._WalkM2Package(tid,e,target,maxRecursion-1,data)
            # CLASSES
            classes = self.cmdrunner._MdbRead(tid,target,STR(M2PACKAGE.CLASSES))
            for e in classes:
                self._WalkM2Class(tid,e,target,maxRecursion-1,data)
            # ENUMS
            enums = self.cmdrunner._MdbRead(tid,target,STR(M2PACKAGE.ENUMS))
            for e in enums:
                self._WalkM2Enum(tid,e,target,maxRecursion-1,data)
        self._OnExitM2Package(tid,target,successor,maxRecursion,data)

    def _WalkM2Model(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Model(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkM2Package(tid,target,target,maxRecursion,data)
        self._OnExitM2Model(tid,target,successor,maxRecursion,data)

    def _WalkM2Enum(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Enum(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # OPTIONS
            options = self.cmdrunner._MdbRead(tid,target,STR(M2ENUM.OPTIONS))
            for e in options:
                self._WalkM2OptionOfEnum(tid,e,target,maxRecursion-1,data)
        self._OnExitM2Enum(tid,target,successor,maxRecursion,data)

    def _WalkM2OptionOfEnum(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2OptionOfEnum(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitM2OptionOfEnum(tid,target,successor,maxRecursion,data)

    def _WalkM2Class(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Class(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # MYATTRIBUTES
            myattributes = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYATTRIBUTES))
            for e in myattributes:
                self._WalkM2Attribute(tid,e,target,maxRecursion-1,data)
            # MYSRCASSOCIATIONS
            mysrcassociations = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYSRCASSOCIATIONS))
            for e in mysrcassociations:
                self._WalkM2Association(tid,e,target,maxRecursion-1,data)
            # MYPARENTCOMPOSITIONS
            myparentcompositions = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYPARENTCOMPOSITIONS))
            for e in myparentcompositions:
                self._WalkM2Composition(tid,e,target,maxRecursion-1,data)
            # MYGENERALIZATIONS
            mygeneralizations = self.cmdrunner._MdbRead(tid,target,STR(M2CLASS.MYGENERALIZATIONS))
            for e in mygeneralizations:
                self._WalkM2Inheritance(tid,e,target,maxRecursion-1,data)
        self._OnExitM2Class(tid,target,successor,maxRecursion,data)

    def _WalkM2Attribute(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Attribute(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitM2Attribute(tid,target,successor,maxRecursion,data)

    def _WalkM2Association(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Association(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitM2Association(tid,target,successor,maxRecursion,data)

    def _WalkM2Composition(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Composition(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitM2Composition(tid,target,successor,maxRecursion,data)

    def _WalkM2Inheritance(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM2Inheritance(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitM2Inheritance(tid,target,successor,maxRecursion,data)

    def _WalkM1Model(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM1Model(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # OBJECTS
            objects = self.cmdrunner._MdbRead(tid,target,STR(M1MODEL.OBJECTS))
            for e in objects:
                self._WalkM1Object(tid,e,target,maxRecursion-1,data)
        self._OnExitM1Model(tid,target,successor,maxRecursion,data)

    def _WalkM1Object(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM1Object(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # ATTRIBUTES
            attributes = self.cmdrunner._MdbRead(tid,target,STR(M1OBJECT.ATTRIBUTES))
            for e in attributes:
                self._WalkM1Attribute(tid,e,target,maxRecursion-1,data)
            # SRCASSOCIATIONS
            srcassociations = self.cmdrunner._MdbRead(tid,target,STR(M1OBJECT.SRCASSOCIATIONS))
            for e in srcassociations:
                self._WalkM1Association(tid,e,target,maxRecursion-1,data)
            # PARENTCOMPOSITIONS
            parentcompositions = self.cmdrunner._MdbRead(tid,target,STR(M1OBJECT.PARENTCOMPOSITIONS))
            for e in parentcompositions:
                self._WalkM1Composition(tid,e,target,maxRecursion-1,data)
        self._OnExitM1Object(tid,target,successor,maxRecursion,data)

    def _WalkM1Feature(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM1Feature(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkMxElement(tid,target,target,maxRecursion,data)
        self._OnExitM1Feature(tid,target,successor,maxRecursion,data)

    def _WalkM1Attribute(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM1Attribute(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkM1Feature(tid,target,target,maxRecursion,data)
        self._OnExitM1Attribute(tid,target,successor,maxRecursion,data)

    def _WalkM1Association(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM1Association(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkM1Feature(tid,target,target,maxRecursion,data)
        self._OnExitM1Association(tid,target,successor,maxRecursion,data)

    def _WalkM1Composition(self, tid:int, target:Obj, successor:Obj, maxRecursion:int, data:Any)->Any:
        self._OnEnterM1Composition(tid,target,successor,maxRecursion,data)
        # walk super concepts
        self._WalkM1Feature(tid,target,target,maxRecursion,data)
        if(maxRecursion!=0):
            # walk clone path properties
            # CHILD
            e = self.cmdrunner._MdbRead(tid,target,STR(M1COMPOSITION.CHILD))
            if not e.IsNone(): self.Walk(tid,e,target,maxRecursion-1,data)
        self._OnExitM1Composition(tid,target,successor,maxRecursion,data)


    def _OnEnterMxMdb(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterMxElement(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterMxConstraint(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitMxMdb(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitMxElement(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitMxConstraint(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Primitives(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Package(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Enum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2OptionOfEnum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Class(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM2Inheritance(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Primitives(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Package(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Enum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2OptionOfEnum(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Class(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM2Inheritance(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM1Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM1Object(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM1Feature(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM1Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM1Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnEnterM1Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM1Model(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM1Object(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM1Feature(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM1Attribute(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM1Association(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

    def _OnExitM1Composition(self, tid:int, target:Obj, successor:Obj, recursionLevel:int, data:Any)->Any:
        pass #override to implement dedicated behavior

