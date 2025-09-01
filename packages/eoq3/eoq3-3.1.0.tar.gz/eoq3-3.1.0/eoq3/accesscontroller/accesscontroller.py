'''
The interface of the class the does the user verification and access control on element level. 
Different implementations are possible as long as they comply to this interface

2022 Bjoern Annighoefer

'''

from ..verifier import Verifier

class AccessController(Verifier):
    def __init__(self):
        super().__init__()
    
    ### INITIAL ACCESS ###
    
    def AuthenticateUser(self, user:str, password:str)->bool:
        '''Returns true if user and password are valid
        '''
        raise NotImplemented()
    
    ### OBSERVATION ACCESS GUARDS ###
    
    def IsAllowedToObserve(self, user:str, eventType:str)->bool:
        raise NotImplemented()
    
    def IsAllowedToSuperobserve(self, user:str, eventType:str)->bool:
        raise NotImplemented()
    
    ### All other methods are inherited from Verifier ###
