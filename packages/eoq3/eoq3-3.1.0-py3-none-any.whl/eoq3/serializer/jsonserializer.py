'''
 Bjoern Annighoefer 2019
'''

from .serializer import Serializer, RegisterSerializer
'''

JSON Serializer

'''
   
from ..frame import Frm
from ..command import Cmd, CmdFactory
from ..query import Qry, Seg
from ..value import VAL, ValFactory, U64, I64, VAL_TYPES
from ..error import EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_RUNTIME

import json
#from unittest.mock import patch

## JSON float formating patch: https://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
# We need to ensure that c encoder will not be launched
# @patch('json.encoder.c_make_encoder', None)
# def JsonDumpsWithWithControlledFloatFormat(obj, **kw):
#     # saving original method
#     of = json.encoder._make_iterencode
#     def inner(*args, **kwargs):
#         args = list(args)
#         # fifth argument is float formater which will we replace
#         args[4] = lambda o: ('%f'%(o)).rstrip('0').rstrip('.') #remove trailing 0 and .
#         return of(*args, **kwargs)
#     
#     with patch('json.encoder._make_iterencode', wraps=inner):
#         return json.dumps(obj, **kw)

def JsonSerializeHook(obj):
    if(isinstance(obj,Frm)):
        return {"frm":"ami","ver":obj.ver,"typ":obj.typ,"uid":obj.uid,"sid":obj.sid,"ser":obj.ser,"roc":obj.roc,"dat":obj.dat}
    elif(isinstance(obj,Cmd)):
        dct = {"cmd":obj.cmd,"a":obj.a}
        #serialize mute and name only if given
        if(obj.m): dct["m"] = obj.m
        if(obj.r): dct["r"] = obj.r
        return dct
    elif(isinstance(obj,VAL)):
        if(type(obj) in (U64,I64)): #64 integer need special care, because JSON does not support BigInt
            return {"val":obj.val,"v":str(obj.v)}
        else:
            return {"val":obj.val,"v":obj.v}
    elif(isinstance(obj,Seg)):
        return {"seg":obj.seg,"v":obj.v}
    else:
        raise EOQ_ERROR_INVALID_TYPE('Can not serialize element of type: %s'%(type(obj).__name__))

def JsonDeserializeHook(dct):
        if "frm" in dct:
            return Frm(dct["typ"],int(dct["uid"]),dct["ser"],dct["dat"],dct["sid"],dct["roc"],dct["ver"])
        if "cmd" in dct:
            cmdType = dct["cmd"]
            a = dct["a"]
            m = False
            r = None
            if "m" in dct: m = dct["m"]
            if "r" in dct: r = dct["r"]
            cmd = CmdFactory(cmdType, a, m, r)
            return cmd
        elif "val" in dct: 
            valType = dct["val"]
            value = None
            if(valType in [VAL_TYPES.U64, VAL_TYPES.I64]): #64 integer need special care, because JSON does not support BigInt
                value = int(dct["v"])
            else:
                value = dct["v"]
            val = ValFactory(valType,value)
            return val
        elif "seg" in dct: 
            return Seg(dct["seg"],dct["v"])
        return dct


class JsonSerializer(Serializer):
    def Name(self):
        '''Returns a three letter identifier for this kind of serialization 
        '''
        return 'JSO'
    
    #@override
    def Ser(self, val):
        try:
            return json.dumps(val,separators=(',', ':'),default=JsonSerializeHook,ensure_ascii=False)
            #return JsonDumpsWithWithControlledFloatFormat(val,separators=(',', ':'),default=JsonSerializeHook) #disabled, because it slows down json dumps by a factor of 5
        except Exception as e:
            raise EOQ_ERROR_RUNTIME('Serialization failed: %s'%(str(e)))
        
    #@override    
    def SerFrm(self,frm : Frm):
        return self.Ser(frm)
    
    #@override    
    def SerCmd(self, cmd : Cmd):
        return self.Ser(cmd)
    
    #@override
    def SerQry(self, qry : Qry):
        return self.Ser(qry)
    
    #@override
    def SerSeg(self, seg : Seg):
        return self.Ser(seg)
    
    #@override
    def SerVal(self,val):
        return self.Ser(val)
    
    #@override
    def Des(self,code):
        return json.loads(code,object_hook=JsonDeserializeHook)
    
    #@override
    def DesFrm(self,data) -> Frm:
        return self.Des(data)
        
    #@override
    def DesCmd(self,data) -> Cmd:
        return self.Des(data)
    
    #@override
    def DesQry(self,data) -> Qry:
        return self.Des(data)
    
    #@override
    def DesSeg(self,data) -> Seg:
        return self.Des(data)
    
    #@override
    def DesVal(self,data):
        return self.Des(data)

### make this serializer known globally 
RegisterSerializer(JsonSerializer)
    
