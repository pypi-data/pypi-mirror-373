'''
Definition of queries and segments 
 
Bjoern Annighoefer 2024
'''

from ..value import VAL, STR, I64, QRY, EncVal, VAL_TYPES, RegisterValType
from ..error import EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_RUNTIME
#type checking
import typing


class SEG_TYPES:
    OBJ = 'OBJ' #object reference
    ONI = 'ONI' #object by name or id
    HIS = 'HIS' #history reference
    
    # Left only element-wise operations
    PTH = 'PTH' # path
    CLS = 'CLS' # class
    INO = 'INO' # instance of
    MET = 'MET' # meta
    NOT = 'NOT' # boolean not
    TRM = 'TRM' # terminate
    TRY = 'TRY' #try catch
    
    QRF = 'QRF' #querify
    STF = 'STF' #stringify
    SLF = 'SLF' #self: returns the context without modifications

    # Left only list-of-elements-wise operations
    IDX = 'IDX' # index
    SEL = 'SEL' # selector
    ARR = 'ARR' # outer array
    ZIP = 'ZIP' # inner array creation
    ANY = 'ANY' # at least one element from the right is found in the left --> Bool
    ALL = 'ALL' # all elements from the right are found in the left --> Bool
    
    # Left-vs-right element-wise operators
    EQU = 'EQU' # equal
    EQA = 'EQA' # equal any of the right elements
    NEQ = 'NEQ' # not equal
    LES = 'LES' # less
    GRE = 'GRE' # greater
    RGX = 'RGX' # regex (string only)
    
    ##generic operators
    ADD = 'ADD' # OR, addition,
    SUB = 'SUB' # XOR, subtraction,
    MUL = 'MUL' # AND, multiply,
    DIV = 'DIV' # NAND, divided,
    
    ##logic operator synonyms
    ORR = 'ORR' # OR synonym
    XOR = 'XOR' # XOR synonym
    AND = 'AND' # AND synonym
    NAD = 'NAD' # NAND synonym
    
    #Left-vs-right list-of-element-wise operators
    CSP = 'CSP' # cross product
    ITS = 'ITS' # intersection
    DIF = 'DIF' # set subtraction / relative complement
    UNI = 'UNI' # union
    CON = 'CON' # concat
        

# META OPERATORS 
# Use only three letters for meta operators

#element operators
class MET_MODES:
    CLS = 'CLASS' #class
    CLN = 'CLASSNAME' #class name
    CON = 'CONTAINER' #parent (container)
    PAR = 'PARENT' #parent (container)
    ALP = 'ALLPARENTS' #parent (container)
    ASO = 'ASSOCIATES' # All elements referring to this one beginning. In as argument a context can be given to limit the search
    ALC = 'ALLCHILDREN' #All M1 elements children of the context directly and indirectly
    IDX = 'INDEX' #index within its containment
    CFT = 'CONTAININGFEATURE' #the feature that contains the element
    FEA = 'FEATURES' #all features
    FEV = 'FEATUREVALUES' #all feature values
    FEN = 'FEATURENAMES' #all feature names
    ATT = 'ATTRIBUTES' #all attribute features
    ATN = 'ATTRIBUTENAMES' #all attribute feature names
    ATV = 'ATTRIBUTEVALUES' #all attribute feature values
    REF = 'REFERENCES' #all reference features
    REN = 'REFERENCENAMES' #all reference feature names
    REV = 'REFERENCEVALUES' #all reference feature values
    CNT = 'CONTAINMENTS' #all containment features
    CNV = 'CONTAINMENTVALUES' #all containment feature values
    CNN = 'CONTAINMENTNAMES' #all containment feature names
    
    #class operators
    PAC = 'PACKAGE' #class
    STY = 'SUPERTYPES' #directly inherited classes
    ALS = 'ALLSUPERTYPES' #all and also indirectly inherited classes
    IMP = 'IMPLEMENTERS' #all direct implementers of a class
    ALI = 'ALLIMPLEMENTERS' #all and also indirect implementers of a class  
    MMO = 'METAMODELS' #retrieve all metamodels
    
    #Control flow operators 
    IFF = 'IF' #if(condition,then,else);  #DEPRICATED
    TRY = 'TRY' #catch errors and return a default #NOT IMPLEMENTED
    
    
    #list operators
    LEN = 'SIZE' #size of a list #DEPRICATED
    
    #recursive operators
    REC = 'REPEAT' #REPEAT(<query>,depth) repeat a given query until no more results are found #NOT IMPLEMENTED
    
    
    
class IDX_MODES:
    #structure operators
    FLT = 'FLATTEN' #flatten any sub list structure to a list #NOT IMPLEMENTED
    LEN = 'SIZE' #size of a list
    ASC = 'SORTASC' #sort ascending #NOT IMPLEMENTED
    DSC = 'SORTDSC' #sort descending #NOT IMPLEMENTED
    
    
class STF_MODES:
    FUL = 'FUL' #full, only a single string is returned
    LST = 'LST' #only the elements of a list are stringified on the uppermost level
    ELM = 'ELM' #elementwise

### (QUERY) SEGMENT CLASS ###
        
class Seg:
    def __init__(self,stype,args):
        self.seg = stype
        self.v = [EncVal(v) for v in args]
        
    def __repr__(self):
        s = '&' + self.seg
        nArgs = len(self.v)
        if(nArgs > 0):
            s += str(self.v[0])
        for i in range(1,nArgs):
            s += ';'+str(self.v[i])
        return s
        
    def __eq__(self, other):
        if(isinstance(other, Seg)):
            return self.seg == other.seg and self.v == other.v
        else: 
            return False #can not be equal if it is a different type
        
    def __lt__(self, other):
        if(isinstance(other,Seg)):
            #first compare the segment identifier
            if(self.seg != other.seg):
                return self.seg < other.seg
            #second compare the values
            n = len(self.v)
            m = len(other.v)
            #compare segments sequentially for equality
            for i in range(min(n,m)):
                if(self.v[i] != other.v[i]):
                    return self.v[i] < other.v[i]
            return n < m
        else:
            raise EOQ_ERROR_INVALID_TYPE("< not supported between instances of 'Seg' and '%d'."%(type(other).__name__))
        
    def __gt__(self, other):
        if(isinstance(other,Seg)):
            #first compare the segment identifier
            if(self.seg != other.seg):
                return self.seg > other.seg
            #second compare the values
            n = len(self.v)
            m = len(other.v)
            #compare segments sequentially for equality
            for i in range(min(n,m)):
                if(self.v[i] != other.v[i]):
                    return self.v[i] > other.v[i]
            return n > m
        else:
            raise EOQ_ERROR_INVALID_TYPE("< not supported between instances of 'Seg' and '%d'."%(type(other).__name__))
        
    def __hash__(self):
        return hash(self.__repr__())


def CopyNonDefaultArgs(args: typing.List[typing.Any], nMinArgs:int, nMaxArgs:int, defaultArgs: typing.List[typing.Any]) -> typing.List[typing.Any]:
    '''Copies the arguments and omits default values at the end
    '''
    nArgs = len(args)
    if(nArgs > nMaxArgs or nArgs < nMinArgs):
        raise EOQ_ERROR_RUNTIME("Expected between %d and %d arguments but got %d."%(nMinArgs,nMaxArgs,nArgs))
    nDefaultArgs = nArgs-nMinArgs
    lastNonDefaultArg = nMinArgs
    for i in range(nDefaultArgs):
        if(args[nMinArgs+i] != defaultArgs[i]):
            lastNonDefaultArg = nMinArgs+i+1
    return args[:lastNonDefaultArg]

### QUERY CLASS ###
        
class Qry(QRY): #Essential object query
    def __init__(self,value=None):
        QRY.__init__(self)
        self.v:typing.List[Seg] = []
        if(None == value):
            self.v = [] #empty list of segments
        elif(isinstance(value, Seg)):
            self.v = [value]
        elif(isinstance(value, list) and all([isinstance(s,Seg) for s in value])):
            self.v = [s for s in value]
        elif(isinstance(value, list) and all([isinstance(s,Qry) for s in value])):
            self.Arr([s for s in value])
        elif(isinstance(value, Qry)): #Clone operator
            self.v = [s for s in value.v]
        else:
            raise EOQ_ERROR_INVALID_TYPE("Expected None, Seg, list<Seg>, list<Obj> or Qry but got %s"%(value))
        
    def __repr__(self):
        queryStr = ''
        for seg in self.v:
            queryStr += str(seg)
        return '('+queryStr+')'

    def __lt__(self, other):
        if(isinstance(other,QRY)):
            n = len(self.v)
            m = len(other.v)
            #compare segments sequentially for equality
            for i in range(min(n,m)):
                if(self.v[i] != other.v[i]):
                    return self.v[i] < other.v[i]
            return n < m
        else:
            raise EOQ_ERROR_INVALID_TYPE("< not supported between instances of 'Qry' and '%d'."%(type(other).__name__))
    
    def __gt__(self, other):
        if(isinstance(other,QRY)):
            n = len(self.v)
            m = len(other.v)
            #compare segments sequentially for equality
            for i in range(min(n,m)):
                if(self.v[i] != other.v[i]):
                    return self.v[i] > other.v[i]
            return n > m
        else:
            raise EOQ_ERROR_INVALID_TYPE("> not supported between instances of 'Qry' and '%d'."%(type(other).__name__))
    
    def _(self,seg): #adds an existing segment
        self.v.append(seg)
    
    def Obj(self,v):
        if(isinstance(v,Seg)):
            self.v.append(v)
        else:
            self.v.append(Seg(SEG_TYPES.OBJ,[v]))
        return self
    
    def Oni(self,v):
        self.v.append(Seg(SEG_TYPES.ONI,[v]))
        return self
    
    def His(self,v):
        self.v.append(Seg(SEG_TYPES.HIS,[v]))
        return self
        
    def Pth(self,name):
        self.v.append(Seg(SEG_TYPES.PTH,[name]))
        return self
    
    def Cls(self,clazz):
        self.v.append(Seg(SEG_TYPES.CLS,[clazz]))
        return self
    
    def Ino(self,clazz):
        self.v.append(Seg(SEG_TYPES.INO,[clazz]))
        return self
    
    def Met(self,name,args=None):
        self.v.append(Seg(SEG_TYPES.MET,CopyNonDefaultArgs([name,args],1,2,[None])))
        # if(None == args):
        #     self.v.append(Seg(SEG_TYPES.MET,[name]))
        # else:
        #     self.v.append(Seg(SEG_TYPES.MET,[name, args]))
        return self
    
    def Not(self):
        self.v.append(Seg(SEG_TYPES.NOT,[]))
        return self
    
    def Trm(self,cond=None,fallback=None):
        self.v.append(Seg(SEG_TYPES.TRM,CopyNonDefaultArgs([cond,fallback],0,2,[None,None])))
        return self
    
    def Qrf(self):
        self.v.append(Seg(SEG_TYPES.QRF,[]))
        return self
    
    def Slf(self):
        self.v.append(Seg(SEG_TYPES.SLF,[]))
        return self
    
    def Stf(self, mode=STF_MODES.ELM):
        self.v.append(Seg(SEG_TYPES.STF,CopyNonDefaultArgs([mode],0,1,[STF_MODES.ELM])))
        return self
    
    def Try(self,query,fallback=None):
        self.v.append(Seg(SEG_TYPES.TRY,CopyNonDefaultArgs([query,fallback],1,2,[None])))
        return self
    
    def Idx(self,start,stop=None,step=None):
        self.v.append(Seg(SEG_TYPES.IDX,CopyNonDefaultArgs([start,stop,step],1,3,[None,None])))
        # if(None == stop):
        #     self.v.append(Seg(SEG_TYPES.IDX,[start]))
        # elif(None == step):
        #     self.v.append(Seg(SEG_TYPES.IDX,[start,stop]))
        # else:
        #     self.v.append(Seg(SEG_TYPES.IDX,[start,stop,step]))
        return self
    
    def Sel(self,query):
        self.v.append(Seg(SEG_TYPES.SEL,[query]))
        return self
    
    def Arr(self,elements):
        self.v.append(Seg(SEG_TYPES.ARR,[elements]))
        return self

    def Zip(self,elements):
        self.v.append(Seg(SEG_TYPES.ZIP,[elements]))
        return self
    
    def Any(self,query):
        self.v.append(Seg(SEG_TYPES.ANY,[query]))
        return self
    
    def All(self,query):
        self.v.append(Seg(SEG_TYPES.ALL,[query]))
        return self
    
    def Equ(self,query):
        self.v.append(Seg(SEG_TYPES.EQU,[query]))
        return self
    
    def Eqa(self,query):
        self.v.append(Seg(SEG_TYPES.EQA,[query]))
        return self
    
    def Neq(self,query):
        self.v.append(Seg(SEG_TYPES.NEQ,[query]))
        return self
    
    def Les(self,query):
        self.v.append(Seg(SEG_TYPES.LES,[query]))
        return self
    
    def Gre(self,query):
        self.v.append(Seg(SEG_TYPES.GRE,[query]))
        return self
        
    def Rgx(self,query):
        self.v.append(Seg(SEG_TYPES.RGX,[query]))
        return self
    
    def Add(self,query):
        self.v.append(Seg(SEG_TYPES.ADD,[query]))
        return self
    
    def Sub(self,query):
        self.v.append(Seg(SEG_TYPES.SUB,[query]))
        return self
    
    def Mul(self,query):
        self.v.append(Seg(SEG_TYPES.MUL,[query]))
        return self
    
    def Div(self,query):
        self.v.append(Seg(SEG_TYPES.DIV,[query]))
        return self
    
    def Orr(self,query):
        self.v.append(Seg(SEG_TYPES.ORR,[query]))
        return self
    
    def Xor(self,query):
        self.v.append(Seg(SEG_TYPES.XOR,[query]))
        return self
    
    def And(self,query):
        self.v.append(Seg(SEG_TYPES.AND,[query]))
        return self
    
    def Nad(self,query):
        self.v.append(Seg(SEG_TYPES.NAD,[query]))
        return self
    
    def Csp(self,query):
        self.v.append(Seg(SEG_TYPES.CSP,[query]))
        return self
    
    def Its(self,query):
        self.v.append(Seg(SEG_TYPES.ITS,[query]))
        return self
    
    def Dif(self,query):
        self.v.append(Seg(SEG_TYPES.DIF,[query]))
        return self
    
    def Uni(self,query):
        self.v.append(Seg(SEG_TYPES.UNI,[query]))
        return self
    
    def Con(self,query):
        self.v.append(Seg(SEG_TYPES.CON,[query]))
        return self
RegisterValType(VAL_TYPES.QRY,'EOQ query',Qry)
    
''' Shortcuts to start queries '''
    
class Obj(Qry):
    def __init__(self,v):
        super().__init__()
        self.Obj(v)
        
class Oni(Qry):
    def __init__(self,v):
        super().__init__()
        self.Oni(v)
        
class His(Qry):
    def __init__(self,v):
        super().__init__()
        self.His(v)

class Pth(Qry):
    def __init__(self,name):
        super().__init__()
        self.Pth(name)
    
class Cls(Qry):
    def __init__(self,clazz):
        super().__init__()
        self.Cls(clazz)
        
class Ino(Qry):
    def __init__(self,clazz):
        super().__init__()
        self.Ino(clazz)
        
class Try(Qry):
    def __init__(self,query,fallback):
        super().__init__()
        self.Try(query,fallback)
        
class Met(Qry):
    def __init__(self,name,args=None):
        super().__init__()
        self.Met(name,args)
        
class Qrf(Qry):
    def __init__(self):
        super().__init__()
        self.Qrf()
        
class Stf(Qry):
    def __init__(self, mode=STF_MODES.ELM):
        super().__init__()
        self.Stf(mode)
        
class Slf(Qry):
    def __init__(self):
        super().__init__()
        self.Slf()
        
class Not(Qry):
    def __init__(self):
        super().__init__()
        self.Not()
        
class Idx(Qry):
    def __init__(self,start,stop=None,step=None):
        super().__init__()
        self.Idx(start,stop,step)
        
class Sel(Qry):
    def __init__(self,query):
        super().__init__()
        self.Sel(query)
        
class Arr(Qry):
    def __init__(self,elements):
        super().__init__()
        self.Arr(elements)       
    
class Zip(Qry):
    def __init__(self,elements):
        super().__init__()
        self.Zip(elements)   
        
class Any(Qry):
    def __init__(self,select):
        super().__init__()
        self.Any(select)
        
class All(Qry):
    def __init__(self,select):
        super().__init__()
        self.All(select)
        
class Equ(Qry):
    def __init__(self,query):
        super().__init__()
        self.Equ(query)
        
class Eqa(Qry):
    def __init__(self,query):
        super().__init__()
        self.Eqa(query)
        
class Neq(Qry):
    def __init__(self,query):
        super().__init__()
        self.Neq(query)
        
class Les(Qry):
    def __init__(self,query):
        super().__init__()
        self.Les(query)
        
class Gre(Qry):
    def __init__(self,query):
        super().__init__()
        self.Gre(query)
        
class Rgx(Qry):
    def __init__(self,query):
        super().__init__()
        self.Rgx(query)

### HELPERS ###

def IsObj(e:typing.Any)->bool:
    '''Checks if an Query is a special Object query
    '''
    return (isinstance(e,QRY) and 1==len(e.v) and SEG_TYPES.OBJ == e.v[0].seg)

def ObjId(e:typing.Any)->VAL:
    '''Returns safely the framework-specific object ID
    '''
    if(IsObj(e)):
        return e.v[0].v[0]
    else:
        raise EOQ_ERROR_INVALID_TYPE("Requires element of type Obj.")
    
def IsHis(e:typing.Any)->bool:
    '''Checks if an Query is a special Object query
    '''
    return (isinstance(e,QRY) and 1==len(e.v) and SEG_TYPES.HIS == e.v[0].seg)

def HisId(e:typing.Any)->typing.Tuple[STR,I64]:
    '''Returns safely history Id
    '''
    if(IsHis(e)):
        return e.v[0].v[0]
    else:
        raise EOQ_ERROR_INVALID_TYPE("Requires element of type His.")
