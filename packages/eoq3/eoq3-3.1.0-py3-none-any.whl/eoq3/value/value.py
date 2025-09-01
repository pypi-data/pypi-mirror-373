'''
Definition of value types used in EOQ in order to make sure that EOQ is type safe in all target languages and serialization.
 
Bjoern Annighoefer 2022
'''

from ..error import EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_UNSUPPORTED, EOQ_ERROR_RUNTIME
from datetime import datetime,timezone,timedelta
from math import floor
#type checking
from typing import Any, Dict, Union, Type, List, Tuple, Iterable
from abc import ABC


### START OF EOQ VALUE TYPES DEFINITION ###

class VAL_TYPES:
    BOL = 'BOL' #boolean
#     U8  = 'U8'  #byte
#     U16 = 'U16' #word
    U32 = 'U32' #unsigned nit 32 bit #NOT IMPLEMENTED
    U64 = 'U64' #unsigned nit 64 bit #NOT IMPLEMENTED
#     I16 = 'I16' #signed int 16 bit (short)
    I32 = 'I32' #signed int 32 bit (long)
    I64 = 'I64' #signed int 64 bit (long long)
    F32 = 'F32' #floating point 32 bit
    F64 = 'F64' #floating point 64 bit (double)
    STR = 'STR' #String
    DAT = 'DAT' #date and time #NOT IMPLEMENTED
    QRY = 'QRY' #query
    NON = 'NON' # none or null
    LST = 'LST' #list

### BASE CLASS FOR ALL VALUES ###
    
class VAL(ABC):
    '''The base class for any value in EOQ 
    
    '''
    def __init__(self, valType:str):
        self.val = valType #the json serializer relies on this
    # PYTHON SPECIFIC
    def __bool__(self):
        return self.IsTrue()
    def __eq__(self, other):
        if(self.Type() == type(other)):
            return (self.v == other.v)
        elif(None == other): #handles general None compares
            return self.IsNone()
        else:
            try:
                #try casting the value types to compare them.
                return (self.v == self.Cast(other).v)
            except:
                return False #everything that cannot be casted is not the same
    def __lt__(self, other):
        if(isinstance(other,VAL) and self.Type() == other.Type()):
            return (self.v < other.v)
        else:
            return self.v < self.Cast(other).v
    def __gt__(self, other):
        if(isinstance(other,VAL) and self.Type() == other.Type()):
            return (self.v > other.v)
        else:
            return self.v > self.Cast(other).v
    def __le__(self, other):
        return not (self > other)
    def __ge__(self, other):
        return not (self < other)
    def __hash__(self):
        return hash(self.__repr__())
    # VAL INTERFACE
    def Type(self):
        '''Returns the value type. 
        This is an own function to make it overridable, which makes sence in case of QRY
        '''
        return type(self) ##by default the class is returned
    def Cast(self, other):
        ''' Casts from any possible value to this value type
        Raises an exception if the value type cannot be casted
        '''
        T = self.Type()
        return other if isinstance(other,T) else T(other)
    def IsNone(self):
        '''Shall be used instead of none checks. 
        By default values are never None, except NON.
        
        '''
        return False 
    def IsTrue(self):
        '''Shall be used in if conditions like instead of only using the value
        
        '''
        return True if(self.v) else False
    def GetVal(self):
        '''Return the native value of the native programming language
        E.g I32 might return int in Python and Numeric in Javascript 
        '''
        return self.v #default implementation, but maybe overridden
    def SetVal(self,val) -> None:
        '''Set from the native value
        
        '''
        self.v = val #default implementation might be overridden
        
    


### VALUE REGISTRY ###

class ValInfo:
    def __init__(self, valType:str, description:str, clazz:Type[VAL], unpackArgs:bool):
        self.valType:str     = valType
        self.description:str = description
        self.clazz:Type[VAL] = clazz
        self.unpackArgs:bool = unpackArgs
        

VAL_TYPE_REGISTRY:Dict[str,ValInfo] = {}
    

def RegisterValType(valType:str, description:str, clazz:Type[VAL], unpackArgs:bool=False)->None:
    if(valType in VAL_TYPE_REGISTRY):
        raise EOQ_ERROR_RUNTIME('Value type %s is already registered.'%(valType))
    VAL_TYPE_REGISTRY[valType] = ValInfo(valType, description, clazz, unpackArgs)


### BASE CLASSES FOR PRIMITIVE VALUES ###
class SIV(VAL):
    '''A single value data type
    
    '''


class PRM(SIV):
    '''A primitive type. This covers all except list
    
    '''
    
class NUM(PRM):
    '''All numeric values
    
    '''
    # PYTHON SPECIFIC
    def __add__(self,b):
        return self.Type()(self.v + self.Cast(b).v)
    def __sub__(self,b):
        return self.Type()(self.v - self.Cast(b).v)
    def __mul__(self,b):
        return self.Type()(self.v * self.Cast(b).v)
    def __truediv__(self,b):
        try:
            return self.Type()(self.v / self.Cast(b).v)
        except ZeroDivisionError:
            raise EOQ_ERROR_INVALID_VALUE('Division by zero')
    def __neg__(self):
        return self.Type()(-self.v)
    
class INT(NUM):
    '''All integer values
    
    '''
    
class FLO(NUM):
    '''All floating point values
    
    '''

      
### PRIMITIVE TYPES #####
        
class BOL(PRM):
    def __init__(self, value:Union[bool,VAL]=False):
        VAL.__init__(self,VAL_TYPES.BOL)
        self.v:bool = False
        if(bool == type(value)):
            self.v = value
        elif(isinstance(value,VAL)):
            self.v = value.IsTrue()
        else:
            self.v = True if value else False #TODO: this implicitly maps pythons True-policy to EOQ. Is that wanted? What about other languages?
    # PYTHON SPECIFIC
    def __repr__(self):
        return "b1" if self.v else "b0"
    # PYTHON SPECIFIC
    def __add__(self,b): #OR
        a = self.v; b = self.Cast(b).v
        return self.Type()(a or b)
    def __sub__(self,b): #XOR
        a = self.v; b = self.Cast(b).v
        return self.Type()((not a and b) or (a and not b))
    def __mul__(self,b): #AND
        a = self.v; b = self.Cast(b).v
        return self.Type()(a and b)
    def __truediv__(self,b): #NAND
        a = self.v; b = self.Cast(b).v
        return self.Type()(not (a and b))
    def __neg__(self):
        return self.Type()(not self.v)
RegisterValType(VAL_TYPES.BOL,'Boolean',BOL)

class U32(INT):
    def __init__(self, value:Union[int,float,INT,FLO]=0):
        VAL.__init__(self,VAL_TYPES.U32)
        self.v:int = 0
        if(int == type(value)):
            self.SetVal(value)
        elif(float == type(value)):
            self.SetVal(round(value))
        elif(isinstance(value,U32) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        elif(isinstance(value,INT) and not value.IsNone()):
            self.SetVal(value.GetVal())
        elif(isinstance(value,FLO) and not value.IsNone()):
            self.SetVal(round(value.GetVal()))
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected int, float, INT or FLO but got %s."%(value))
    # PYTHON SPECIFIC
    def __repr__(self):
        return "u%d"%(self.v)
    # VAL INTERFACE
    def SetVal(self,val:int) -> None:
        '''simulate u32 value space '''
        minVal = 0
        maxVal = 4294967296-1#2^32-1
        if(val < minVal):
            raise EOQ_ERROR_INVALID_VALUE("Underflow: value can not be smaller than %d, but got %d."%(minVal,val))
        elif(maxVal < val):
            raise EOQ_ERROR_INVALID_VALUE("Overflow: value can not be larger than %d, but got %d."%(maxVal,val))
        self.v = val
#         maxVal = 4294967296#2^32
#         #check if value is negative
#         if(0>val):
#             self.v = maxVal - ((-val) % maxVal) #simulate 2-complement
#         else:
#             self.v = val % maxVal #wrap around
RegisterValType(VAL_TYPES.U32,'32bit unsigned integer',U32)

class U64(INT):
    def __init__(self, value:Union[int,float,INT,FLO]=0):
        VAL.__init__(self,VAL_TYPES.U64)
        self.v:int = 0
        if(int == type(value)):
            self.SetVal(value)
        elif(float == type(value)):
            self.SetVal(round(value))
        elif(isinstance(value,U64) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        elif(isinstance(value,INT) and not value.IsNone()):
            self.SetVal(value.GetVal())
        elif(isinstance(value,FLO) and not value.IsNone()):
            self.SetVal(round(value.GetVal()))
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected int, float, INT or FLO but got %s."%(value))
    # PYTHON SPECIFIC    
    def __repr__(self):
        return "y%d"%(self.v)
    # VAL INTERFACE
    def SetVal(self,val:int) -> None:
        '''simulate u64 value space '''
        minVal = 0
        maxVal = 18446744073709551616-1#2^32-1
        if(val < minVal):
            raise EOQ_ERROR_INVALID_VALUE("Underflow: value can not be smaller than %d, but got %d."%(minVal,val))
        elif(maxVal < val):
            raise EOQ_ERROR_INVALID_VALUE("Overflow: value can not be larger than %d, but got %d."%(maxVal,val))
        self.v = val
RegisterValType(VAL_TYPES.U64,'64bit unsigned integer',U64)
    
class I32(INT):
    def __init__(self, value:Union[int,float,INT,FLO]=0):
        VAL.__init__(self,VAL_TYPES.I32)
        self.v:int = 0
        if(int == type(value)):
            self.SetVal(value)
        elif(float == type(value)):
            self.SetVal(round(value))
        elif(isinstance(value,I32) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        elif(isinstance(value,INT) and not value.IsNone()):
            self.SetVal(value.GetVal())
        elif(isinstance(value,FLO) and not value.IsNone()):
            self.SetVal(round(value.GetVal()))
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected int, float, INT or FLO but got %s."%(value))
    # PYTHON SPECIFIC     
    def __repr__(self):
        return "i%d"%(self.v)
    # VAL INTERFACE
    def SetVal(self, val:int) -> None:
        '''simulate i32 value space '''
        minVal = -2147483648 #-2^31
        maxVal = 2147483648-1#2^31-1
        if(val < minVal):
            raise EOQ_ERROR_INVALID_VALUE("Underflow: value can not be smaller than %d, but got %d."%(minVal,val))
        elif(maxVal < val):
            raise EOQ_ERROR_INVALID_VALUE("Overflow: value can not be larger than %d, but got %d."%(maxVal,val))
        self.v = val
RegisterValType(VAL_TYPES.I32,'32bit signed integer',I32)


class I64(INT):
    def __init__(self, value:Union[int,float,INT,FLO]=0):
        VAL.__init__(self,VAL_TYPES.I64)
        self.v:int = 0
        if(int == type(value)):
            self.SetVal(value)
        elif(float == type(value)):
            self.SetVal(round(value))
        elif(isinstance(value,I64) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        elif(isinstance(value,INT) and not value.IsNone()):
            self.SetVal(value.GetVal())
        elif(isinstance(value,FLO) and not value.IsNone()):
            self.SetVal(round(value.GetVal()))
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected int, float, INT or FLO but got %s."%(value))  
    def __repr__(self):
        return "l%d"%(self.v)
    # VAL INTERFACE
    def SetVal(self, val:int) -> None:
        '''simulate i64 value space '''
        minVal = -9223372036854775808 #-2^31
        maxVal = 9223372036854775808-1#2^31-1
        if(val < minVal):
            raise EOQ_ERROR_INVALID_VALUE("Underflow: value can not be smaller than %d, but got %d."%(minVal,val))
        elif(maxVal < val):
            raise EOQ_ERROR_INVALID_VALUE("Overflow: value can not be larger than %d, but got %d."%(maxVal,val))
        self.v = val
RegisterValType(VAL_TYPES.I64,'64bit signed integer',I64)
    
class F32(FLO):
    def __init__(self, value:Union[float,int,FLO,INT]=0.0):
        VAL.__init__(self,VAL_TYPES.F32)
        self.v:float = 0.0
        if(float == type(value)):
            self.v = value
        elif(int == type(value)):
            self.v = float(value)
        elif(isinstance(value,F32) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        elif(isinstance(value,FLO) and not value.IsNone()):
            self.v = value.GetVal()
        elif(isinstance(value,INT) and not value.IsNone()):
            self.v = float(value.GetVal())
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected int, float, INT or FLO but got %s."%(value))
    # PYTHON SPECIFIC         
    def __repr__(self):
        return "f%f"%(self.v)
RegisterValType(VAL_TYPES.F32,'32bit floating point (float)',F32)

class F64(FLO):
    def __init__(self, value:Union[float,int,FLO,INT]=0.0):
        VAL.__init__(self,VAL_TYPES.F64)
        self.v:float = 0.0
        if(float == type(value)):
            self.v = value
        elif(int == type(value)):
            self.v = float(value)
        elif(isinstance(value,F64) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        elif(isinstance(value,FLO) and not value.IsNone()):
            self.v = value.GetVal()
        elif(isinstance(value,INT) and not value.IsNone()):
            self.v = float(value.GetVal())
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected int, float, INT or FLO but got %s."%(value))
    # PYTHON SPECIFIC         
    def __repr__(self):
        return "d%f"%(self.v)
RegisterValType(VAL_TYPES.F64,'64bit floating point (double)',F64)
    
class STR(PRM):
    def __init__(self, value:Union[str,VAL]=''):
        VAL.__init__(self,VAL_TYPES.STR)
        self.v:str = ''
        if(str == type(value)):
            self.v = value
        elif(isinstance(value,STR) and not value.IsNone()): ##Copy constructor
            self.v = value.v
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected str or STR, but got %s."%(value))
    # PYTHON SPECIFIC         
    def __repr__(self):
        return self.v  
    def __len__(self):
        return len(self.v)
    def __getitem__(self,key:Union[int,slice,INT]):
        if(int == type(key)):
            return STR(self.v[key])
        elif(isinstance(key,slice)):
            return STR(self.v[key])
        elif(isinstance(key,INT) and not key.IsNone()):
            return STR(self.v[key.GetVal()])
        else:
            raise EOQ_ERROR_INVALID_TYPE('Expected int, slice or INT but got %s.'%(key))
    def __add__(self, other):
        return STR(self.v + self.Cast(other).v)
RegisterValType(VAL_TYPES.STR,'String',STR)

class DAT(PRM):
    def __init__(self, yearOrValue:Union[int,datetime,VAL]=0, month:int=0, day:int=0, hour:int=0, minute:int=0, second:int=0, microsec:float=0.0, utcoff:float=0.0):
        VAL.__init__(self,VAL_TYPES.DAT)
        self.v:Tuple[int,int,int,int,int,int,float,float] = (0,0,0,0,0,0,0.0,0.0)
        if(isinstance(yearOrValue,datetime)):
            self.SetVal(yearOrValue)
        elif(DAT == type(yearOrValue)):
            self.v = tuple(yearOrValue.v)
        elif(int == type(yearOrValue)):
            self.v = (int(yearOrValue),int(month),int(day),int(hour),int(minute),int(second),float(microsec),float(utcoff))
        else:
            raise EOQ_ERROR_INVALID_TYPE('Expected datetime, DAT or year as int but got %s.'%(yearOrValue))
    # PYTHON SPECIFIC
    def __repr__(self):
        # ISO 8601 format: YYYY-MM-DDThh:mm:ss.sss+hh:mm (https://en.wikipedia.org/wiki/ISO_8601)
        Y = self.v[0]
        M = self.v[1]
        D = self.v[2]
        h = self.v[3]
        m = self.v[4]
        s = self.v[5]
        ms = int(round(self.v[6]*1000)) # convert from us to full ms
        oh = int(floor(self.v[7])) #extract full h
        om = int(round((self.v[7] - oh)*60)) #extract full min
        return "%04d-%02d-%02dT%02d:%02d:%02d:%f%0+2d:%02d"%(Y,M,D,h,m,s,ms,oh,om)
    def __lt__(self, other):
        return self.GetVal() < self.Cast(other).GetVal()
    def __gt__(self, other):
        return self.GetVal() > self.Cast(other).GetVal()
    # VAL INTERFACE
    def GetVal(self) -> datetime:
        tz = timezone(timedelta(seconds=int(self.utcoff()*3600.0)))
        return datetime(self.year(),self.month(),self.day(),self.hour(),self.minute(),self.second(),int(self.microsec()),tz)
    def SetVal(self,val : datetime):
        utcoff = 0.0
        td = val.utcoffset() #timedelta
        if(td): #the timezone info is not always present
            h,r = divmod(td.seconds,3600)
            m,s = divmod(r,60)
            utcoff = float(h)+float(m)/60.0+float(s)/3600 #UTC offset in hours
        self.v = (val.year,val.month,val.day,val.hour,val.minute,val.second,val.microsecond,utcoff) #todo: timezone?
    # ADDITIONAL HELPER FUNCTIONS
    def year(self)->int:
        return self.v[0]
    def month(self)->int:
        return self.v[1]
    def day(self)->int:
        return self.v[2]
    def hour(self)->int:
        return self.v[3]
    def minute(self)->int:
        return self.v[4]
    def second(self)->int:
        return self.v[5]
    def microsec(self)->float:
        return self.v[6]
    def utcoff(self)->float:
        return self.v[7]
RegisterValType(VAL_TYPES.DAT,'Date and time',DAT,True)
    
class QRY(SIV):
    def __init__(self):
        VAL.__init__(self,VAL_TYPES.QRY)
        # is not implemented here but in query
    # VAL INTERFACE
    def GetVal(self):
        return self #query can not be resolved
    def SetVal(self,value)->None:
        raise EOQ_ERROR_UNSUPPORTED('QRY cannot be set')
    def Type(self):
        return QRY #make sure the inherited types also return QRY
    
# QRY is not registered because it is only a placeholder to initialize NON. The real query class is in query.py
    
# NON is something special, because every other value can also be none
class NON(BOL,I32,I64,F32,F64,STR,DAT,QRY):
    def __init__(self,value=None):
        VAL.__init__(self,VAL_TYPES.NON)
        self.v:list = []
        if(NON == type(value)):
            pass
        elif(None == value):
            pass
        else:
            raise EOQ_ERROR_INVALID_TYPE('Expected NON or None but got: %s.'%(value))
        #self.v = [] #empty list enables factory create better
    def __repr__(self):
        return "n0"
    # PYTHON SPECIFIC
    def __eq__(self, other):
        if(isinstance(other,VAL)):
            return other.IsNone()
        elif(None == other): #handles general None compares
            return True
        else:
            return False
    def __lt__(self, other):
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation < for NON')
    def __gt__(self, other):
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation > for NON')
    def __add__(self,b): #OR
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation + for NON')
    def __sub__(self,b): #XOR
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation - for NON')
    def __mul__(self,b): #AND
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation * for NON')
    def __truediv__(self,b): #NAND
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation / for NON')
    def __neg__(self):
        raise EOQ_ERROR_UNSUPPORTED('Unknown operation -x for NON')
    # VAL INTERFACE
    def IsNone(self):
        return True #this is the only None type
    def IsTrue(self):
        '''Override because NON values are always false'''
        return False
    # VAL INTERFACE
    def GetVal(self):
        '''Override because NON values are always None'''
        return None
    def SetVal(self,value)->None:
        pass #nothing. Cannot set NON to a different value
    def Type(self):
        return NON #make sure the inherited types also return QRY
RegisterValType(VAL_TYPES.NON,'None or null value',NON,True)
### COMPLEY TYPES ###

class LSTIterator:
    '''ListIterator is necessary to make LST iterable
    
    '''
    def __init__(self,lst):
        self.__lst = lst
        self.__i = 0 #start at zero
    def __next__(self):
        if(self.__i < len(self.__lst)):
            self.__i += 1
            return self.__lst[self.__i-1]
        else:
            raise StopIteration()
    def __iter__(self): #seems necessary for python >= 3.13
        return self
    
class LST(VAL):
    def __init__(self,value:Union[Iterable,VAL] = []):
        super().__init__(VAL_TYPES.LST)
        self.v:List[VAL] = []
        if(isinstance(value,Iterable)):
            #self.v = [v if isinstance(v,VAL) else raise EOQ_ERROR_INVALID_TYPE('Only VAL can be member of LST, but got %s'%(v)) for v in value ]
            self.v = []
            for v in value: 
                if(isinstance(v,VAL)):
                    self.v.append(v)
                else:
                    raise EOQ_ERROR_INVALID_TYPE('Only VAL can be member of LST, but got %s.'%(type(v).__name__))
        elif(isinstance(value,LST) and not value.IsNone()): #Copy constructor
            self.v = [x for x in value.v]
        else:
            raise EOQ_ERROR_INVALID_TYPE('Expected list or LST but got %s.'%(value))
    # PYTHON SPECIFIC    
    def __repr__(self):
        return str(self.v)
    def __len__(self):
        return len(self.v)
    def __getitem__(self,key:Union[int,slice,INT]):
        if(int == type(key)):
            return self.v[key]
        elif(isinstance(key,slice)):
            return LST(self.v[key])
        elif(isinstance(key,INT) and not key.IsNone()):
            return self.v[key.GetVal()]
        else:
            raise EOQ_ERROR_INVALID_TYPE('Expected int, slice or INT but got %s.'%(key))
    def __setitem__(self, key:int, newvalue:VAL):
        self.v[key] = newvalue
    def __iter__(self):
        return LSTIterator(self)
    def __contains__(self,item):
        return (item in self.v)
    def __add__(self, other:Union[list,'LST']):
        if(isinstance(other,LST)):
            return LST(self.v + other.v)
        else:
            return LST(self + self.Cast(other))
    ### simulate the list functions of python
    def append(self,val:VAL):
        if(isinstance(val,VAL)):
            self.v.append(val)
            return self
        else:
            raise EOQ_ERROR_INVALID_TYPE('Expected VAL but got %s.'%(val))
        
    def index(self,find):
        return self.v.index(find) 
    # VAL INTERFACE
    def GetVal(self)->list:
        return [v.GetVal() for v in self.v]
    def SetVal(self,value)->None:
        raise EOQ_ERROR_UNSUPPORTED('LST cannot be set')
RegisterValType(VAL_TYPES.LST,'list',LST)
    
#### VALUE INIT HELPERS ####

def EncVal(value:Union[VAL,None,bool,int,float,str,list]):
    '''Convert any primitive type in the corresponding EOQ value type
    
    '''
    if(None == value): #None checks are not handled via type compare
        return NON()
    elif(isinstance(value,VAL)):
        return value #nothing to do
    #all other types are handled by detecting the Python base type
    elif(bool == type(value)):
        return BOL(value)
    elif(int == type(value)):
        return I64(value)
    elif(float == type(value)):
        return F32(value)
    elif(str == type(value)):
        return STR(value)
    elif(list == type(value)):
        return LST([EncVal(v) for v in value])
    else:
        raise EOQ_ERROR_INVALID_TYPE("Data type %s is not supported."%(type(value).__name__))
    
def InitValOrNon(value,ValType):
    return  NON() if None==value else ValType(value)

### VALUE VALIDATION HELPERS ####
    
def ValidateVal(value:VAL, expectedTypes:list, varname:str, exact:bool=True)->VAL:
    '''Checks if the vale corresponds to a type from the list. 
    If not it raises a EOQ_ERROR_INVALID_TYPE exception with varname
    If exact is false it is checked for being an instance.
    '''
    for t in expectedTypes:
        if(exact and t == type(value) or isinstance(value,t)):
            return value
    #if going here all cast failed:
    expectedTypeStrs = " or ".join([t.__name__ for t in expectedTypes])
    raise EOQ_ERROR_INVALID_TYPE("%s: expected %s but got %s"%(varname,expectedTypeStrs,type(value).__name__)) 
    
def ValidateValAndCast(value:Union[VAL,bool,int,float,str,datetime,None], expectedTypes:List[Type[VAL]], varname:str)->VAL:
    '''Tries to cast the given value into the given VAL types after each other. The first that works is returned.
    If all fail an ValType exception is returned including varname
    '''
    for t in expectedTypes:
        if(t == type(value)):
            return value
        else:
            try:
                return t(value)
            except EOQ_ERROR_INVALID_TYPE:
                pass #do nothing since the next type might work 
    #if going here all cast failed:
    expectedTypeStrs = " or ".join([t.__name__ for t in expectedTypes])
    raise EOQ_ERROR_INVALID_TYPE("%s: expected %s but got %s."%(varname,expectedTypeStrs,type(value).__name__))

def ValCompare(a:Any,b:Any)->bool:
    '''Compares a and b for having equal values. 
    It compares values based on primitive values not based on data types, e.g. 
    U32(1) and 1 will be equal.
    For lists it does a deep compare, e.g. 
    LST([]) and [] will be equal.
    '''
    #In Python this is easy, because comparision by value is already implemented by the VAL classes.
    return a==b;


    
### VALUE FACTORY ###
    
def ValFactory(valType:str, args:list)->VAL:
    try: 
        valInfo = VAL_TYPE_REGISTRY[valType]
        if(valInfo.unpackArgs):
            return valInfo.clazz(*args) #create a new instance
        else:
            return valInfo.clazz(args) #create a new instance
    except Exception:#KeyError:
        raise EOQ_ERROR_INVALID_TYPE('Value type %s does not exist.'%(valType))



