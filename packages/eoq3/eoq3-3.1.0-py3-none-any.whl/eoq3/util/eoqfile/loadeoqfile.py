'''
 Bjoern Annighoefer 2024
'''

from ...domain import Domain
from .cmdstream import EoqFileInStream, ToDomainCmdStream


def LoadEoqFile(infile: str, domain: Domain = None, sessionId: str = None, validateBeforeLoad: bool = True) -> None:
    """Loads an EOQ file to a specified domain.

    Args:
        infile (str): Path to the EOQ file to be loaded.
        domain (Domain, optional): The domain to load the EOQ file to. Defaults to None.
        sessionId (str, optional): Session ID for the domain. Defaults to None.
        validateBeforeLoad (bool, optional): Whether to validate the EOQ file before loading. Defaults to True.

    Raises:
        [Exception]: If an error occurs during loading or validation.

    This function loads an EOQ file to a specified domain. If no domain is provided, a default interpreter will be used.
    The EOQ file can be optionally validated before loading.
    """
    fileInStream = EoqFileInStream()
    if(validateBeforeLoad):
        #load the file, before the domain is connected.
        fileInStream.Begin()
        fileInStream.LoadEoqFile(infile)
        fileInStream.Flush()
    #connect the domain and load the file (again)
    fileInStream.Connect(ToDomainCmdStream(domain,sessionId,False,True))
    fileInStream.Begin()
    fileInStream.LoadEoqFile(infile)
    fileInStream.Flush()