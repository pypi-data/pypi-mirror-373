'''
2022 Bjoern Annighoefer

'''
from .accesscontroller import AccessController

class NoAccessController(AccessController):
    ''' Simple implementation that will do no access checking and no user management. 
    Everybody can do everything
    '''
    def __init__(self):
        super().__init__()
    
    ### INITIAL ACCESS ###
    
    def AuthenticateUser(self, user:str, password:str)->bool:
        return True
    
    ### OBSERVATION ###
    
    def IsAllowedToObserve(self, user:str, eventType:str)->bool:
        return True
    
    def IsAllowedToSuperobserve(self, user:str, eventType:str)->bool:
        return True
