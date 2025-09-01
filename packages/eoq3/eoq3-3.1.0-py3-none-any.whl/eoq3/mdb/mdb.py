'''
 Model Database (MDB) Interface

 Bjoern Annighoefer 2021
'''

from .readonlymdb import ReadOnlyMdb

from ..value import VAL, PRM, I64, STR, LST, NON
from ..query import Obj
from ..error import EOQ_ERROR

#type checking
from typing import Tuple, List, Union


class Mdb(ReadOnlyMdb):
    """ Definition of an basic MDB interface.
    
    Defines a CRUD+ interface as being the sole interface for interacting with a model database (MDB) 
    All implementations of an MDB should inherit from this interface.
    
    * Create, read, remove, update, delete
    """
     
    def Create(self, classId:Union[STR,Obj], createArgs:LST=LST([]), target:Obj=NON(), recoveryArgs:LST=LST([])) -> Tuple[Obj,EOQ_ERROR]:
        """ Creates a new element based on a class.
        
        Instantiates a clas as a new element and returns the elements reference.
        
        Args:
            classId: The unique identifier of a class
                EOQ generic class IDs might be used as classID to create, e.g.
                meta-model elements.
            name: (optional) some classes might require providing a name
                This is usually the case for meta-model classes.
            target: (optional) if given, the new element is created as a replacement
                of the target element. This is only possible if the target element
                is from the same mdb, but not valid any more, i.e. it is an 
                element that was deleted before.                
                
        Returns:
            newElem: The element that was created, e.g. the new instance of the class.
            postModificationError: None if successful. 
                Returns instance of EOQ_ERROR, if the call failed after the 
                MDB was modified. In that case a rollback is suggested.
            
        Raises:
            EOQ_ERROR_INVALID_VALUE: The class ID provided is not known 
                and cannot be resolved in a class to be instantiated.
            EOQ_ERROR_INVALID_VALUE: The class to be instantiated requires a 
                name in order to be instantiated.
            EOQ_ERROR_INVALID_VALUE: The name given is has an invalid value or is no string 
                Or can not be used because it is already in use.
            
        Side-effects:
            None
        """
        
        pass
    
#     def Read(self, target:Obj, featureName:STR, context:Obj=NON()) -> VAL:
#         """ Returns the value of a feature.
#         
#         Returns the value or values of an attribute, an association or a composition. 
#         The value can be a single value in case the length of the feature is 1.
#         Otherwise a list of values will be returned.
#         
#         Args:
#             target: The element the feature belongs to.
#             featureName: The name of the feature of which the value shall be returned.
#                 Generic feature names might be used
#             context: (optional) if given some feature names are only evaluated 
#                 below the context element, e.g. finding all class instances 
#             
#         Returns:
#             val: The value of the feature.
#             
#         Raises:
#             EOQ_ERROR_INVALID_VALUE: The target is no (known) element.
#             EOQ_ERROR_INVALID_VALUE: The element does not have a feature with the given name 
#                 or it is not readable.
#             
#         Side-effects:
#             None
#         """
#         
#         pass
    
    def Update(self, target:Obj, featureName:STR, value:PRM, position:I64=I64(0)) -> Tuple[Obj,Obj,Obj,I64,EOQ_ERROR]:
        """ Sets or inserts a value of an element's attribute, association or composition
        
        Update is the universal tool to make changes in a model database. 
        It changes the content of a attribute, association or composition (called feature).
        
        If an value is given, this value is stored at the given position of the feature. 
        If this position already has a value, that value is replaced by the new one. 
        For compositions this will change the parent of the replaced element. 
        Likewise, it changes the parent of the new value.
        
        If None is given as the value, the current value at the given position is removed from the feature. 
        Features can not contain empty positions, therefore, the subsequent elements will 
        decrease by one in their position.
        
        The return value contains everything to undo the update. 
        Except information provided in the arguments during the call.
        
        Args:
            target: The target element of the update operation. 
                Obj(0) can be used for root operations
            featureName: The name of the feature of the target to update.
                The feature name can be a generic feature ID.
            value: value == None -> The current value at the given position is removed. 
                The subsequent elements move one position forward.
                value != None -> The current value at the given position is replaced by 
                the given value. 
            position: (optional, default = 0) Legal range [-<feature len>-2, ..., <feature len>+1]
                The position where the value shall be stored or removed. 
                Position must be positive and below the length of the feature or -1.
                If -1 is given the value is added after the last element in the feature.
                Higher negative position indicates insertion. 
                Examples: 
                    - BEFORE    --> update(... x, position) --> AFTER
                    - [1,2,3,4,5] --> upd(...,x, 0) --> [x,2,3,4,5]
                    - [1,2,3,4,5] --> upd(...,x, 2) --> [1,2,x,4,5]
                    - [1,2,3,4,5] --> upd(...,x, 5) --> [1,2,3,4,5,x]
                    - [1,2,3,4,5] --> upd(...,x, 6) --> ERROR
                    - [1,2,3,4,5] --> upd(...,x,-1) --> [1,2,3,4,5,x]
                    - [1,2,3,4,5] --> upd(...,x,-2) --> [x,1,2,3,4,5]
                    - [1,2,3,4,5] --> upd(...,x,-4) --> [1,2,x,3,4,5]
                    - [1,2,3,4,5] --> upd(...,x,-6) --> [1,2,3,4,x,5]
                    - [1,2,3,4,5] --> upd(...,x,-7) --> [1,2,3,4,5,x]
                    - [1,2,3,4,5] --> upd(...,x,-8) --> ERROR
                
        Returns:
            oldValue: The previous element or primitive value at position 
            oldOwner: The parent of value before update.
                (only in case value is an element, the feature is a composition and 
                value had a parent before, is None otherwise) 
            oldComposition: The name of the composition value was inside before the update.
                (only in case value is an element, the feature is a composition and 
                value had a parent before, is None otherwise) 
            oldPosition: The position of the element in an composition before the update.
                (only in case value is an element, the feature is a composition and 
                value had a parent before, is None otherwise) 
            postModificationError: None if successful. 
                Returns instance of EOQ_ERROR, if the call failed after the 
                MDB was modified. In that case a rollback is suggested.
            
        Raises:
            ...
            
        Side-effects:
            Parent change of old value:  (only replace of element values in compositions)
                In case of composition the parent of the old value at the position is removed
            Parent change of new value: (only if new value is an element and add to a composition)
                In case of a composition the parent of the new value is now the target
            Position change of elements > position: (insert only)
                In case of insert (negative position) the position of values after the inserted 
                value are increased by one.
        
        """
        
        pass
    
    
    def Delete(self, target:Obj) -> Tuple[STR,List[STR],List[VAL],EOQ_ERROR]: #modi for delete: complete, element only
        """ Deletes an object. 
        
        Only elements can be deleted that do not have a parent and
        that are not referenced by any other element any more.
        Any child of the deleted element does become an orphan.
        
        Args:
            target: The element to be deleted.
        
        Returns:
            classId: The classId of the deleted element 
            featureNames: All feature names of the deleted element. 
                this includes all attributes, association and composition 
                names of this and all super classes. This can be used 
                to fully restore the element if creating a new one.
            featureValues: All feature values of the deleted element
                this includes the values of all attributes, associations,
                and composition. The values are in the same order as 
                the feature names. This can be used to restore the element.
            postModificationError: None if successful. 
                Returns instance of EOQ_ERROR, if the call failed after the 
                MDB was modified. In that case a rollback is suggested.
                
        Side-effects:
            All children become orphans.
            
            Target is no valid object identifier any more, but might be used 
            for restoring the element in Create()
        """
        pass
    
    def FindElementByIdOrName(self, nameOrId:STR, context:Obj=NON(), restrictToConcept:STR=NON()) -> LST:
        ''' Returns all elements that match the given name or string id.
        
        In case an ID is provided a maximum of one class is returned, because IDs are unique.
        
        Args:
            nameOrId: The *NAME or *STRID value of an element if existent. 
                STRID will maks any name if existent, i.e. if STR ID is found, 
                no NAME is searched
            context: If set element are only used in this context. Only valid for names.
            restrictToConcept: If set, only concepts of this kind are returned, with matching ID are returned.
        
        Returns:
            classes: A list of classes matching the id or name. If no class is found, the list is empty.
        '''
        pass
    
    def Close(self):
        ''' CLoses the MDB gracefully
        
        '''
        pass

