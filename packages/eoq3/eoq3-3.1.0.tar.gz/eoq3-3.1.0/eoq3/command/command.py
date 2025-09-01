"""
 Defines all command types of EOQ3.
 2019 Bjoern Annighoefer
"""

from ..value import VAL, PRM, BOL, U32, U64, STR, I64, LST, NON, EncVal
from ..query import Obj
from ..error import EOQ_ERROR_RUNTIME
#type checking
from typing import Dict, List, Any, Type, Union
from abc import ABC

CMD_SEP = '\n'
CMD_ARG_SEP = ' '

class CMD_TYPES:
    """ All commands 3-letter identifiers.
    """
    #basic CRUD commands
    CRT = 'CRT'  # create
    RED = 'RED' #read cmd
    UPD = 'UPD' #update cmd
    DEL = 'DEL'  # delete cmd
    # high level commands
    GET = 'GET'  # get cmd
    SET = 'SET' #set cmd value (M1 only)
    ADD = 'ADD' #add cmd value (M1 only)
    REM = 'REM' #remove cmd value (M1 only)
    MOV = 'MOV' #move cmd cmd (M1 only)
    CLO = 'CLO' #clone source target mode
    QRF = 'QRF' #querify
    #maintenance related commands
    HEL = 'HEL' #hello
    GBY = 'GBY' #goodbye
    SES = 'SES' #session
    STS = 'STS' #status
    CHG = 'CHG' #changes
    OBS = 'OBS' #observe
    UBS = 'UBS' #unobserve
    MSG = 'MSG' #send message to observers
    # extensions
    SCC = 'SCC' #set custom command
    UCC = 'UCC' #unset custom command
    CUS = 'CUS' #invoke custom command.
    # Verification related commands
    VER = 'VER' #verify model element against constraint 
    GAC = 'GAC' #get all applicable constraints for target
    #Result
    RES = 'RES' #result
    ERR = 'ERR' #error
    #Event
    EVT = 'EVT' #event
    #Compound commands
    CMP = 'CMP' #compound

class DEL_MODES:
    BAS = 'BAS' #base: delete the element itself. Does only work for elements not contained and not referenced
    AUT = 'AUT' #auto: delete the element itself. All containment's and references are removed beforehand
    FUL = 'FUL' #all: delete element and all children recursively

class CLO_MODES:
    MIN = 'MIN' #minimum: clone only concept and create args
    BAS = 'BAS' #base: clone concept and all updatable all properties
    FUL = 'FUL' #full: clone all elements in the clone path recursively
    
class EVT_TYPES:
    ELM = 'ELM' # element (this is not a real event, but used to make objects observed)
    CRT = 'CRT' # create
    UPD = 'UPD' # update
    DEL = 'DEL' # delete
    MSG = 'MSG' # message
    WAT = 'WAT' # watch event (not implemented)
    VEC = 'VEC' # verification change
    
class EVT_KEYS:
    ALL = '*' # watch all events
    
### COMMAND BASE CLASS ###    
    
class Cmd(ABC):
    def __init__(self,t:str, mute:bool=False, resName:str=None):
        self.cmd:str                = t
        self.a:List[Union[Cmd,VAL]] = []
        self.r:str                  = resName #result name
        self.m:bool                 = mute #mute the output
        
    def __eq__(self,other:Any)->bool:
        if(isinstance(other,Cmd)):
            if(self.cmd!=other.cmd or \
               self.m != other.m or \
               self.r != other.r): 
                return False
            n = len(self.a)
            m = len(other.a)
            if(n!=m):
                return False
            for i in range(n):
                if(self.a[i]!=other.a[i]):
                    return False
            return True #return true if all arguments are the same
        else:
            False 
        
    def __repr__(self)->str:
        cmdStr = ("-" if self.m else "")+str(self.cmd)
        if(len(self.a) > 0):
            cmdStr += CMD_ARG_SEP + CMD_ARG_SEP.join([str(arg) for arg in self.a])
        if(None!=self.r):
            cmdStr += " -> $"+self.r
        return cmdStr
    
    
### COMMAND REGISTRY ###

class CmdInfo:
    def __init__(self,cmdId:str, minArgs:int, maxArgs:int, description:str, clazz:Type[Cmd], unpackArgs:bool=True, optDefVals:List[Any]=[]):
        self.cmdId = cmdId
        self.minArgs = minArgs
        self.maxArgs = maxArgs
        self.description = description
        self.clazz = clazz
        self.unpackArgs = unpackArgs
        self.optArgs:int = maxArgs-minArgs
        self.optDefVals = optDefVals
        
        
EOQ_COMMAND_REGISTRY:Dict[str,CmdInfo] = {}
    

def RegisterCmdType(cmdId:str, minArgs:int, maxArgs:int, description:str, clazz:Type[Cmd], unpackArgs:bool=True, optDefVals:List[Any]=[]):
    EOQ_COMMAND_REGISTRY[cmdId] = CmdInfo(cmdId,minArgs,maxArgs,description,clazz,unpackArgs,optDefVals)
    
def CmdFactory(cmdId:str, args:List[Any], mute:bool=False, resName:str=None):
    try: 
        cmdInfo = EOQ_COMMAND_REGISTRY[cmdId]
        nArgs = len(args)
        if(nArgs < cmdInfo.minArgs or (cmdInfo.maxArgs > 0 and cmdInfo.maxArgs < nArgs)):
            raise EOQ_ERROR_RUNTIME('%s requires between %d and %d arguments, but got %d'%(cmdId,cmdInfo.minArgs,cmdInfo.maxArgs,nArgs))
        if(cmdInfo.unpackArgs):
            return cmdInfo.clazz(*args,mute=mute,resName=resName) #create a new instance
        else:
            return cmdInfo.clazz(args,mute=mute,resName=resName) #create a new instance
    except KeyError:
        return Cus(cmdId,args,mute=mute,resName=resName)
    
def GetCmdInfo(cmdId:str)->CmdInfo:
    if(cmdId in EOQ_COMMAND_REGISTRY):
        return EOQ_COMMAND_REGISTRY[cmdId]
    else:
        return None

class PrmCmd(Cmd,ABC): 
    '''Primitive command a base class for primitive commands, which fixes the argument type 
    '''
    def __init__(self,t:str, args:List[Any], mute:bool=False, resName:str=None):
        super().__init__(t, mute, resName)
        self.a:List[VAL] = [EncVal(a) for a in args]
    
### BASIC COMMANDS ###

class Red(PrmCmd):
    def __init__(self, target:Any, featureName:Any, context:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.GET, [target, featureName, context],mute,resName)
RegisterCmdType(CMD_TYPES.RED,1,1,'CRUD Read',Red,True)
        
class Get(PrmCmd):
    def __init__(self, target:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.GET, [target],mute,resName)     
RegisterCmdType(CMD_TYPES.GET,1,1,'Retrieve values',Get,True)
        
class Upd(PrmCmd):
    def __init__(self, target:Any, feature:Any, value:Any, position:Any=0,mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.UPD, [target,feature,value,I64(position)],mute,resName)
RegisterCmdType(CMD_TYPES.UPD,3,4,'Change, add or delete the value of a feature.',Upd,True,[-10]) #-10 = hack to prevent argument stripping 
        
class Del(PrmCmd):
    def __init__(self, target:Any, mode:Any=DEL_MODES.BAS,mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.DEL, [target,mode],mute,resName)
RegisterCmdType(CMD_TYPES.DEL,1,2,'Delete an element.',Del,True,[DEL_MODES.BAS]) 
        
class Set(PrmCmd):
    def __init__(self, target:Any, feature:Any, value:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.SET, [target,feature,value],mute,resName)
RegisterCmdType(CMD_TYPES.SET,3,3,'Set a feature.',Set,True) 
        
class Add(PrmCmd):
    def __init__(self, target:Any, feature:Any, value:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.ADD, [target,feature,value],mute,resName)
RegisterCmdType(CMD_TYPES.ADD,3,3,'Add values to a multi-value feature.',Add,True) 
        
class Rem(PrmCmd):
    def __init__(self, target:Any, feature:Any, value:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.REM, [target,feature,value],mute,resName)
RegisterCmdType(CMD_TYPES.REM,3,3,'Remove a value from a feature.',Rem,True) 
        
class Mov(PrmCmd):
    def __init__(self, target:Any, newIndex:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.MOV, [target,newIndex],mute,resName)
RegisterCmdType(CMD_TYPES.MOV,2,2,'Remove a value from a feature.',Mov,True) 
        
class Clo(PrmCmd):
    def __init__(self, target:Any, mode:Any=STR(CLO_MODES.MIN), createArgOverrides:Any=LST([]), mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.CLO,[target,mode,createArgOverrides],mute,resName)
RegisterCmdType(CMD_TYPES.CLO,1,3,'Clone an element.',Clo,True,[CLO_MODES.MIN,[]]) 
          
class Crt(PrmCmd):
    def __init__(self, classId:Any, n:Any=U32(1), createArgs:Any=LST([]), target:Any=NON(), recoveryArgs:Any=LST([]),mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.CRT,[classId,U32(n),createArgs,target,recoveryArgs],mute,resName)
RegisterCmdType(CMD_TYPES.CRT,2,5,'Create element by class ID (name or Obj).',Crt,True,[[],None,[]])
        
### DOMAIN RELATED COMMANDS
        
class Hel(PrmCmd):
    def __init__(self, user:Any, password:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.HEL, [user, password],mute,resName)
RegisterCmdType(CMD_TYPES.HEL,2,2,'Log into the domain. The login persists for the actual session id.',Hel,True) 
        
class Ses(PrmCmd):
    def __init__(self, sessionId:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.SES, [sessionId],mute,resName)
RegisterCmdType(CMD_TYPES.SES,1,1,'Set the session id for the current transaction. Only makes sense in a compound command.',Ses,True) 
        
class Gby(PrmCmd):
    def __init__(self, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.GBY, [],mute,resName)
RegisterCmdType(CMD_TYPES.GBY,0,0,'Log off the given session.',Gby,True) 
        
class Sts(PrmCmd):
    def __init__(self, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.STS, [],mute,resName)
RegisterCmdType(CMD_TYPES.STS,0,0,'Status returns the latest change ID.',Sts,True) 
        
class Chg(PrmCmd):
    def __init__(self, latestChangeId:Any, n:Any, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.CHG,[latestChangeId,n],mute,resName)
RegisterCmdType(CMD_TYPES.CHG,2,2,'Retrieve change records.',Chg,True) 
        
class Obs(PrmCmd):
    def __init__(self, eventType:Any, eventKey:Any=None, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.OBS, [eventType,eventKey],mute,resName)
RegisterCmdType(CMD_TYPES.OBS,1,2,'Start observing events for the current session.',Obs,True,[None]) 
        
class Ubs(PrmCmd):
    def __init__(self, eventType:Any, eventKey:Any=None, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.UBS, [eventType,eventKey],mute,resName)
RegisterCmdType(CMD_TYPES.UBS,1,2,'Stop observing events for the current session.',Ubs,True,[None]) 

class Msg(PrmCmd):
    def __init__(self, msgKey:Any, msg:Any, mute:bool=True,resName : str = None):
        super().__init__(CMD_TYPES.MSG, [msgKey,msg],mute,resName)
RegisterCmdType(CMD_TYPES.MSG,2,2,'Sending a message to observers.',Msg,True) 


### CONSTRAINT RELATED COMMANDS ###

class Ver(PrmCmd):
    def __init__(self, target:Any, mute: bool=False,resName : str = None):
        super().__init__(CMD_TYPES.VER, [target],mute,resName)
RegisterCmdType(CMD_TYPES.VER,1,1,'Verify',Ver,True)

class Gac(PrmCmd):
    def __init__(self, target:Any, mute: bool=False,resName : str = None):
        super().__init__(CMD_TYPES.GAC, [target],mute,resName)
RegisterCmdType(CMD_TYPES.GAC,1,1,'Get all constraints',Gac,True)
        
        
### RESULT COMMAND ###

class Res(PrmCmd):
    def __init__(self, tid:Any, cid:Any, val:Any, resNames:LST=LST([]),resNameIndizies:LST=LST([]),mute: bool=False,resName : str = None):
        super().__init__(CMD_TYPES.RES, [U64(tid),U64(cid),val,resNames,resNameIndizies],mute,resName)
RegisterCmdType(CMD_TYPES.RES,3,5,'Result',Res,True,[LST([]),LST([])])
        
class Err(PrmCmd):
    def __init__(self, code:int,msg:Any='', debug:Any='',mute: bool=False, resName:str=None):
        super().__init__(CMD_TYPES.ERR, [U32(code),STR(msg),STR(debug)],mute,resName)
RegisterCmdType(CMD_TYPES.ERR,1,3,'Error result',Err,True,['','']) 
        
        
### EVENT COMMANDS ###

class Evt(PrmCmd):
    def __init__(self, eventType:STR, data:LST, mute:bool=False, resName:str=None):
        super().__init__(CMD_TYPES.EVT, [eventType, data])
RegisterCmdType(CMD_TYPES.EVT,2,2,'Event',Evt,True)
        
class UpdEvt(Evt):
    def __init__(self, cid:U64, target:Obj, feature:STR, value:PRM, position:I64, user:STR):
        super().__init__(STR(EVT_TYPES.UPD),LST([cid,target,feature,value,position,user]))
        
class CrtEvt(Evt):
    def __init__(self, cid:U64, target:Obj, classId:Union[STR,Obj], createArgs:LST, user:STR):
        super().__init__(STR(EVT_TYPES.CRT),LST([cid,target,classId,createArgs,user]))
        
class DelEvt(Evt):
    def __init__(self, cid:U64, target:Obj, classId:Union[STR,Obj], createArgs:LST, user:STR):
        super().__init__(STR(EVT_TYPES.DEL),LST([cid,target,classId,createArgs,user]))
        
class MsgEvt(Evt):
    def __init__(self, msgKey:STR, msg:STR):
        super().__init__(STR(EVT_TYPES.MSG),LST([msgKey, msg]))
        
class WatEvt(Evt):
    def __init__(self, wid:U32, result:VAL, error:STR):
        super().__init__(STR(EVT_TYPES.WAT),LST([wid, result, error]))
        
class VecEvt(Evt):
    def __init__(self, target:Obj,  constraint:Obj, isValid:BOL,  error:STR):
        super().__init__(STR(EVT_TYPES.VEC),LST([target,constraint,isValid,error]))
        
        
### CUSTOM COMMAND ###

class Scc(PrmCmd):
    def __init__(self, cmdId:Any, cmdStr:Any, mute:bool=False, resName:str = None):
        super().__init__(CMD_TYPES.SCC, [cmdId,cmdStr],mute,resName)
RegisterCmdType(CMD_TYPES.SCC,2,2,'Set custom command',Scc,True)

class Ucc(PrmCmd):
    def __init__(self, cmdId:Any, mute:bool=False, resName:str = None):
        super().__init__(CMD_TYPES.SCC, [cmdId],mute,resName)
RegisterCmdType(CMD_TYPES.UCC,1,1,'Unset custom command',Ucc,True)

class Cus(PrmCmd):
    def __init__(self, cmdId:Any, args:List[any], mute:bool=False, resName:str=None):
        super().__init__(cmdId, args, mute, resName)
#RegisterCmdType(CMD_TYPES.CUS,1,1,'Custom command',Cus,True) 
    
        

### COMPOUND COMMAND ###

class Cmp(Cmd):
    def __init__(self, cmds:List[Cmd]=None ,mute: bool=False, resName:str=None):
        super().__init__(CMD_TYPES.CMP,mute,resName)
        self.a:Cmd = []
        if(None != cmds):
            self.a = [c for c in cmds if isinstance(c,Cmd)]

    def Red(self, target:Any, featureName:Any, context:Any, mute:bool=False, resName:str=None):
        self.a.append(Red(target,featureName,context,mute,resName))
        return self
        
    def Get(self, target:Any, mute:bool=False, resName:str=None):
        self.a.append(Get(target,mute,resName))
        return self
    
    def Upd(self, target:Any, feature:Any, value:Any, position:Any=0, mute:bool=False, resName:str=None):
        self.a.append(Upd(target,feature,value,position,mute,resName))
        return self
    
    def Del(self, target:Any, mode:Any=DEL_MODES.BAS, mute:bool=False, resName:str=None):
        self.a.append(Del(target,mode,mute,resName))
        return self
    
    def Set(self, target:Any, feature:Any, value:Any, mute:bool=False, resName:str=None):
        self.a.append(Set(target,feature,value,mute,resName))
        return self
    
    def Add(self, target:Any, feature:Any, value:Any, mute:bool=False, resName:str=None):
        self.a.append(Add(target,feature,value,mute,resName))
        return self
    
    def Rem(self, target:Any, feature:Any, value:Any, mute:bool=False, resName:str=None):
        self.a.append(Rem(target,feature,value,mute,resName))
        return self
    
    def Mov(self, target:Any, newIndex:Any, mute:bool=False, resName:str=None):
        self.a.append(Mov(target,newIndex,mute,resName))
        return self
    
    def Clo(self, target:Any, mode:Any=STR(CLO_MODES.MIN), createArgOverrides:Any=LST([]), mute:bool=False, resName:str=None):
        self.a.append(Clo(target,mode,createArgOverrides,mute,resName))
        return self
    
    def Crt(self, classId:Any, n:Any=U32(1), createArgs:Any=LST([]), target:Any=NON(), recoveryArgs:Any=LST([]), mute:bool=False, resName:str=None):
        self.a.append(Crt(classId,n,createArgs,target,recoveryArgs,mute,resName))
        return self
    
    def Hel(self, user:Any, password:Any, mute:bool=False, resName:str=None):
        self.a.append(Hel(user,password,mute,resName))
        return self
    
    def Ses(self, sessionId:Any, mute:bool=False, resName:str=None):
        self.a.append(Ses(sessionId,mute,resName))
        return self
    
    def Gby(self, mute:bool=False, resName:str=None):
        self.a.append(Gby(mute,resName))
        return self
    
    def Sts(self, mute:bool=False, resName:str=None):
        self.a.append(Sts(mute,resName))
        return self
    
    def Chg(self, changeId:Any, n:Any, mute:bool=False, resName:str=None):
        self.a.append(Chg(changeId,n,mute,resName))
        return self
    
    def Obs(self, eventType:Any, eventKey:Any=None, mute:bool=False, resName:str=None):
        self.a.append(Obs(eventType,eventKey,mute,resName))
        return self
    
    def Ubs(self, eventType:Any, eventKey:Any=None, mute:bool=False, resName:str=None):
        self.a.append(Ubs(eventType,eventKey,mute,resName))
        return self

    def Ver(self, target:Any):
        self.a.append(Ver(target))
        return self

    def Gac(self,target:Any):
        self.a.append(Gac(target))
        return self
    
    def Scc(self, cmdId:Any, cmdStr:Any, mute:bool=False, resName:str = None):
        self.a.append(Scc(cmdId,cmdStr,mute,resName))
        return self

    def Ucc(self, cmdId:Any, mute:bool=False, resName:str = None):
        self.a.append(Ucc(cmdId,mute,resName))
        return self
    
    def Cus(self, cmdId:Any, args:List[Any], mute:bool=False, resName:str=None):
        self.a.append(Cus(cmdId,args,mute=mute,resName=resName))
        return self
        
    def Append(self, cmd:Cmd):
        """Appends a command to the compound
        """
        self.a.append(cmd)
        return self

    def __repr__(self) -> str:
        return "["+super().__repr__()+"]"
            
RegisterCmdType(CMD_TYPES.CMP,0,-1,'A compound command composed of a list of subcommands.',Cmp,False) 

### HELPERS ###

def IsReadOnlyCmd(cmd:Cmd)->bool:
    """ Returns true for commands that do not modify the MDB
    """
    if(isinstance(cmd,Get)):
        return True
    elif (isinstance(cmd,Red)):
        return True
    elif(isinstance(cmd,Cmp)): #in case of compound commands it depends on the subcommands
        for a in cmd.a:
            if(not IsReadOnlyCmd(a)):
                return False
        return True
    else:
        return False #all other commands are expected to have changes
    



