'''
 Bjoern Annighoefer 2019
'''

from ..frame import Frm
from ..command import Cmd
from ..query import Qry, Seg
from ..error import EOQ_ERROR_DOES_NOT_EXIST
#type checking
from typing import Type, Dict


class Serializer:
    ''' Base class for any serializer
    
    '''
    def Name(self)->str:
        '''Returns a three letter identifier for this kind of serialization 
        '''
        raise NotImplemented()
    
    ### SERIALIZE INTERFACES
    def Ser(self, val)->str:
        ''' Auto-selecting based on the content
        '''
        if(isinstance(val, Frm)):
            return self.SerFrm(val)
        elif(isinstance(val, Cmd)):
            return self.SerCmd(val)
        elif(isinstance(val, Qry)):
            return self.SerQry(val)
        elif(isinstance(val, Seg)):
            return self.SerSeg(val)
        else:
            return self.SerVal(val)
    
    def SerFrm(self, frm:Frm)->str:
        pass
    
    def SerCmd(self, cmd:Cmd)->str:
        pass
    
    def SerQry(self, qry:Qry)->str:
        pass
    
    def SerSeg(self, seg:Seg)->str:
        pass
    
    def SerVal(self, val):
        pass
    
    
    ### DESERIALIZE INTERFACES
    def Des(self, data):
        ''' Auto-selecting based on the content
        '''
        #stupid version,  just try the different parsers starting with the frame
        try: return self.DesFrm(data)
        except: pass
        try: return self.DesCmd(data)
        except: pass
        try: return self.DesQry(data)
        except: pass
        try: return self.DesSeg(data)
        except: pass
        try: return self.DesVal(data)
        except: pass
    
    def DesFrm(self, data) -> Frm:
        pass
    
    def DesCmd(self, data) -> Cmd:
        pass
    
    def DesQry(self, data) -> Qry:
        pass
    
    def DesSeg(self, data) -> Seg:
        pass
    
    def DesVal(self, data):
        pass
    
    
    
### SERIALIZER REGISTRY AND FACTORY ###
SERIALIZER_REGISTRY:Dict[str,Type[Serializer]] = {} #a list of serializer classes that can be instantiated
DEFAULT_SERIALIZERS:Dict[str,Serializer] = {} #a list of serializer instances that can be used

def RegisterSerializer(serializerClass:Type[Serializer]):
    serializer = serializerClass()
    name = serializer.Name()
    SERIALIZER_REGISTRY[name] = serializerClass
    DEFAULT_SERIALIZERS[name] = serializer

def CreateSerializer(name:str):
    try:
        return SERIALIZER_REGISTRY[name]()
    except KeyError:
        raise EOQ_ERROR_DOES_NOT_EXIST('Unknown serializer: %s'%(name))
    
def GetDefaultSerializer(name:str):
    try:
        return DEFAULT_SERIALIZERS[name]
    except KeyError:
        raise EOQ_ERROR_DOES_NOT_EXIST('Unknown serializer: %s'%(name))
    

# GLOBAL DESERIALIZATION FUNCTIONS ###    

def DesCmd(name:str, data:str) -> Cmd:
    '''Deserializes a command based on the serializer name'''
    serializer = GetDefaultSerializer(name)
    return serializer.DesCmd(data)


def SerCmd(name:str, cmd:Cmd) -> str:
    '''Serializes a command based on the serializer name'''
    serializer = GetDefaultSerializer(name)
    return serializer.SerCmd(cmd)






    
    

    