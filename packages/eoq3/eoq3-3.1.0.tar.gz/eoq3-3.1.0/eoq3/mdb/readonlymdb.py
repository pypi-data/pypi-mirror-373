'''
 Model Database (MDB) Interface

 Bjoern Annighoefer 2021
'''

from ..value import VAL, STR, NON
from ..query import Obj


class ReadOnlyMdb:
    """ Definition of an read only MDB interface.
    """
     
    def Read(self, target:Obj, featureName:STR, context:Obj=NON()) -> VAL:
        """ Returns the value of a feature.
        
        Returns the value or values of an attribute, an association or a composition. 
        The value can be a single value in case the length of the feature is 1.
        Otherwise a list of values will be returned.
        
        Args:
            target: The element the feature belongs to.
            featureName: The name of the feature of which the value shall be returned.
                Generic feature names might be used
            context: (optional) if given some feature names are only evaluated 
                below the context element, e.g. finding all class instances 
            
        Returns:
            val: The value of the feature.
            
        Raises:
            EOQ_ERROR_INVALID_VALUE: The target is no (known) element.
            EOQ_ERROR_INVALID_VALUE: The element does not have a feature with the given name 
                or it is not readable.
            
        Side-effects:
            None
        """
        
        pass

