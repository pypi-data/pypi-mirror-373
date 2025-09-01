"""
 2019 Bjoern Annighoefer
"""

from .remotedomainbasea import RemoteDomainBaseA

from ..config import Config
#type checking
from typing import Tuple

class SerialDomain(RemoteDomainBaseA):
    """A domain that supports processing serialized commands directly,
    which is often better performing in multi-computer environments
    """
    def __init__(self, config:Config):
        super().__init__(config)
        
    def SerRawDo(self, cmdStr:str, sessionId:str=None, serType:str=None, readOnly:bool=False)->Tuple[str,str]:
        """Direct processing of serialized commands
        Args:
        - cmdStr: The serialized command
        - sessionId: the session under which this command is processed
        - serType: [3 letter str] the name of the serializer

        Returns:
        - resStr: The serialized results
        - serType: [3 letter str] The serializer name used for the results
        """
        raise NotImplemented()

    def Close(self):
        pass #is to be called if the domain closes down
    
                    
    
        
        