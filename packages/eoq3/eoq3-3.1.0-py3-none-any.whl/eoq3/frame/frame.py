'''
 An EOQ protocol communication frame
 Bjoern Annighoefer 2019
 '''
 
from .. import __version__

class FRM_TYPE:
    '''There are five options a frame is used in regular EOQ communication:
    command, a result (of a command), events, as well as obs and ubs calls
    '''
    CMD = 'CMD'
    RES = 'RES'
    EVT = 'EVT'
    OBS = 'OBS'
    UBS = 'UBS'
        
class Frm:
    '''Frame a container for commands
    '''
    def __init__(self, typ:str, uid:int, ser:str, data:str, sid:str, roc:bool=False, version:str=__version__):
        ''' A frame transports a eoq commands (res and evt are also commands)
        '''
        self.ver:str = version #the version of eoq that created the frame
        self.typ:str = typ     #[3 chars] the type of communication (see above)
        self.uid:int = uid     #a unique identifier used to match requests and results
        self.ser:str = ser     #[3chars]the serialization type
        self.dat:str = data    #already serialized command
        self.sid:str = sid     #the session id
        self.roc:bool = roc    #is read-only command?
    def __repr__(self):
        return "Frm(typ=%s, ver=%s, uid=%s, sid=%s, ser=%s, roc=%d, dat=%s"%(self.typ,self.ver,self.uid,self.sid,self.ser,self.roc,self.dat)
    def __eq__(self,other):
        if(isinstance(other,Frm)):
            return (self.ver == other.ver and 
                    self.typ == other.typ and 
                    self.uid == other.uid and 
                    self.ser == other.ser and 
                    self.sid == other.sid and 
                    self.roc == other.roc and
                    self.dat == other.dat 
                    )
        else:
            return False
