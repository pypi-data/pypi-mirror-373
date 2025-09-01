'''
 2019 Bjoern Annighoefer
'''

from ..value import VAL,LST
from ..error import EoqErrorFactory,EOQ_ERROR_RUNTIME
from ..util.observable import Observable
from ..command import CMD_TYPES, Cmd, Res, Err
#type checking
from typing import Union

class Domain(Observable):
    def __init__(self):
        super().__init__()
    
    def Do(self, cmd:Cmd, sessionId:str=None, asDict:bool=False,
           readOnly=False)->VAL:
        """Execute a command and return the result.
        cmd: Cmd - The command to execute.
        sessionId: str - (optional) The session ID of the session used as a context for the command.
          None if the command is not linked to a session.
        asDict: bool - (optional) If True, the result is returned as a dictionary, for all commands that specify resNames. If False, commands result is returned natively.
        readOnly: bool - (optional) Indicates that the command has read-only effect on the domain, which helps to optimize the execution.
        """
        res = self.RawDo(cmd,sessionId,readOnly)
        if(CMD_TYPES.RES == res.cmd):
            val =  res.a[2]
            if(asDict):
                if(isinstance(res.a[3],LST) and 0<len(res.a[3])):
                    valDct = {}
                    valNames = res.a[3]
                    valNameIndices = res.a[4]
                    for i in range(len(valNames)):
                        valDct[valNames[i].GetVal()] = val[valNameIndices[i]]
                    return valDct
                else:
                    raise EOQ_ERROR_RUNTIME("There are no value names in result. Cannot use asDict.")
            else: #return as list
                return val #the third entry is the value
        elif(CMD_TYPES.ERR == res.cmd):
            error = EoqErrorFactory(res.a[0].GetVal(), res.a[1].GetVal(), res.a[2].GetVal())
            raise error
        else:
            raise EOQ_ERROR_RUNTIME("Unexpected result type: %s"%(res.cmd))
        
    def RawDo(self, cmd:Cmd, sessionId:str=None, readOnly:bool=False)->Union[Res,Err]:
        '''Do function without converting the results back into the value
        '''
        raise NotImplemented()
        
    def DoAsync(self, cmd:Cmd, callbackSuccess:callable, callbackError:callable, sessionId:str=None, asDict:bool=False):
        raise NotImplemented()
            
    
    def Close(self):
        pass #is to be called if the domain closes down
    
                    
    
        
        