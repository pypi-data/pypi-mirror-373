'''
 Bjoern Annighoefer 2024
'''

from ...domain import Domain
from ...value import VAL
from ...value import VAL, QRY, STR
from ...query import Qry, IsObj
from ...command import Get
from ...concepts import *
from ...error import EOQ_ERROR_INVALID_TYPE

from typing import Dict, Any

class ResNameGenA():
    ''' Interface to generate unique names for resNames
    '''
    def __init__(self):
        raise NotImplementedError()
        
    def GenResName(self, res:VAL)->str:
        ''' Returns a unique name for a set of results, usually Obj.
        For the same res the same name will be recovered. 
        '''
        raise NotImplementedError()
    
    def InventResName(self)->str:
        ''' Returns a unique name generated out of nothing, but is unique
        '''
        raise NotImplementedError()
    
    
    
class SimpleResNameGen(ResNameGenA):
    ''' Helper to generate readable names for resNames by consecutively enumerating elements.
    '''
    def __init__(self, prefix:str="o"):
        self.prefix = prefix
        self.objCount = 0
        self.objNameLut:Dict[VAL,str] = {}
        
    #@Override
    def GenResName(self, res:VAL)->str:
        resName = None
        if(res in self.objNameLut):
            resName = self.objNameLut[res]
        else:
            resName = self.InventResName()
        self.objNameLut[res] = resName
        return resName
    
    #@Override
    def InventResName(self)->str:
        ''' Returns a unique name generated out of nothing, but is unique
        '''
        resName = "%s%d"%(self.prefix,self.objCount)
        self.objCount += 1
        return resName
    
    


from typing import Hashable, Dict, Any

class FromDomainResNameGen(SimpleResNameGen):
    '''Tries to generate readable names for resNames
    based on the concept type
    '''
    def __init__(self, domain:Domain, sessionId:str, prefix:str="o", segmentSeperator="_"):
        super().__init__(prefix)
        self.domain = domain
        self.sessionId = sessionId
        self.segmentSeperator = segmentSeperator
        #internals
        self.usedNames:Dict[str,bool] = {}
        #concept handler table
        self.resNameHandlers = {}
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2ENUM)] = self.__M2EnumResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)] = self.__M2OptionOfEnumResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2MODEL)] = self.__M2ModelResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2PACKAGE)] = self.__M2ModelResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2CLASS)] = self.__M2ClassResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)] = self.__M2AttributeResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)] = self.__M2AssociationResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2COMPOSITION)] = self.__M2CompositionResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M2INHERITANCE)] = self.__M2InheritanceResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M1MODEL)] = self.__M1ModelResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M1OBJECT)] = self.__M1ObjectResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)] = self.__M1AttributeResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)] = self.__M1AssociationResName
        self.resNameHandlers[GetConceptKeyString(CONCEPTS.M1COMPOSITION)] = self.__M1CompositionResName
        
    #@Override
    def GenResName(self, res:VAL)->str:
        resName = None
        if(IsObj(res)):
            conceptId = self.domain.Do( Get( Qry(res).Pth(STR(MXELEMENT.CONCEPT))),self.sessionId).GetVal()
            try:
                conceptKey = GetConceptKeyString(conceptId)
                handler = self.resNameHandlers[conceptKey]
                name = handler(res)
                resNameRaw = self.segmentSeperator.join([conceptKey.lower(),name if name else ""])
                resName = resNameRaw
                suffix = 1
                while(resName in self.usedNames):
                    suffix += 1
                    resName = "%s%d"%(resNameRaw,suffix) #append count to make name unique
                self.usedNames[resName] = True
                self.objNameLut[res] = resName
            except KeyError:
                resName = super().GenResName(res)
        else:
            raise EOQ_ERROR_INVALID_TYPE("Can only generate resNames from res of type Obj.")
        return resName
        
    ### INTERNALS
        
    def __M2EnumResName(self, target:QRY)->str:
        return self.domain.Do( Get( Qry(target).Pth(STR(M2ENUM.NAME))),self.sessionId).GetVal()
    
    def __M2OptionOfEnumResName(self, target:QRY)->str:
        enumName = self.domain.Do( Get( Qry(target).Pth(STR(M2OPTIONOFENUM.ENUM)).Pth(STR(M2ENUM.NAME))),self.sessionId).GetVal()
        name = self.domain.Do( Get( Qry(target).Pth(STR(M2OPTIONOFENUM.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([enumName,name])

    def __M2ModelResName(self, target:QRY)->str:
        return self.domain.Do( Get( Qry(target).Pth(STR(M2PACKAGE.NAME))),self.sessionId).GetVal()
    
    def __M2PackageResName(self, target:QRY)->str:
        return self.domain.Do( Get( Qry(target).Pth(STR(M2PACKAGE.NAME))),self.sessionId).GetVal()
    
    def __M2ClassResName(self, target:QRY)->str:
        return self.domain.Do( Get( Qry(target).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
    
    def __M2AttributeResName(self, target:QRY)->str:
        className = self.domain.Do( Get( Qry(target).Pth(STR(M2ATTRIBUTE.CLASS)).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
        name = self.domain.Do( Get( Qry(target).Pth(STR(M2ATTRIBUTE.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([className,name])
    
    def __M2AssociationResName(self, target:QRY)->str:
        className = self.domain.Do( Get( Qry(target).Pth(STR(M2ASSOCIATION.SRCCLASS)).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
        name = self.domain.Do( Get( Qry(target).Pth(STR(M2ASSOCIATION.SRCNAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([className,name])
    
    def __M2CompositionResName(self, target:QRY)->str:
        className = self.domain.Do( Get( Qry(target).Pth(STR(M2COMPOSITION.PARENTCLASS)).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
        name = self.domain.Do( Get( Qry(target).Pth(STR(M2COMPOSITION.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([className,name])
    
    def __M2InheritanceResName(self, target:QRY)->str:
        subClassName = self.domain.Do( Get( Qry(target).Pth(STR(M2INHERITANCE.SUBCLASS)).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
        superClassName = self.domain.Do( Get( Qry(target).Pth(STR(M2INHERITANCE.SUPERCLASS)).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([subClassName,superClassName])
    
    def __M1ModelResName(self, target:QRY)->str:
        modelName = self.domain.Do( Get( Qry(target).Pth(STR(M1MODEL.M2MODEL)).Pth(STR(M2PACKAGE.NAME))),self.sessionId).GetVal()
        name = self.domain.Do( Get( Qry(target).Pth(STR(M1MODEL.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([modelName,name])
    
    def __M1ObjectResName(self, target:QRY)->str:
        return super().GenResName(target)
        # className = self.domain.Do( Get( Qry(target).Pth(STR(M1OBJECT.M2CLASS)).Pth(STR(M2CLASS.NAME))),self.sessionId).GetVal()
        # name = self.domain.Do( Get( Qry(target).Pth(STR(M1OBJECT.NAME))),self.sessionId).GetVal()
        # return self.segmentSeperator.join([className,name])
    
    def __M1AttributeResName(self, target:QRY)->str:
        parentName = self.objNameLut[self.domain.Do( Get( Qry(target).Pth(STR(M1ATTRIBUTE.OBJECT))),self.sessionId)]
        className = self.domain.Do( Get( Qry(target).Pth(STR(M1ATTRIBUTE.M2ATTRIBUTE)).Pth(STR(M2ATTRIBUTE.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([parentName[CONCEPT_UNIQUE_LEN+1:],className]) #CONCEPT_UNIQUE_LEN+1 removes the previous prefix
    
    def __M1AssociationResName(self, target:QRY)->str:
        parentName = self.objNameLut[self.domain.Do( Get( Qry(target).Pth(STR(M1ASSOCIATION.SRC))),self.sessionId)]
        className = self.domain.Do( Get( Qry(target).Pth(STR(M1ASSOCIATION.M2ASSOCIATION)).Pth(STR(M2ASSOCIATION.SRCNAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([parentName[CONCEPT_UNIQUE_LEN+1:],className]) #CONCEPT_UNIQUE_LEN+1 removes the previous prefix
    
    def __M1CompositionResName(self, target:QRY)->str:
        parentName = self.objNameLut[self.domain.Do( Get( Qry(target).Pth(STR(M1COMPOSITION.PARENT))),self.sessionId)]
        className = self.domain.Do( Get( Qry(target).Pth(STR(M1COMPOSITION.M2COMPOSITION)).Pth(STR(M2COMPOSITION.NAME))),self.sessionId).GetVal()
        return self.segmentSeperator.join([parentName[CONCEPT_UNIQUE_LEN+1:],className]) #CONCEPT_UNIQUE_LEN+1 removes the previous prefix