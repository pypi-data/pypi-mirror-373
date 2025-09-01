'''
2019 Bjoern Annighoefer
'''

from ..value import VAL, NON, LST
from ..error import EOQ_ERROR_INVALID_VALUE

DATE_TIME_STR_FORMAT = "%m/%d/%Y %H:%M:%S"

'''
    A class indicating that nothing more to process here
'''
class TRM(VAL):
    def __init__(self,v):
        self.v = v
    def __eq__(self, other):
        if(isinstance(other, TRM)):
            return self.v == other.v
        else:
            return self.v == other

def Determinate(res:VAL) -> VAL:
    if(IsList(res)):
        res = LST([Determinate(r) for r in res])
    elif(isinstance(res, TRM)):
        res = res.v
    return res

'''
    Operations on multiple objects, structures and lists
    
'''

def ApplyToAllElements(context,functor):
    res = NON()
    if(IsList(context)):
        res = LST([ApplyToAllElements(c,functor) for c in context])
    elif(isinstance(context, TRM)):
        res = res
    else:
        res = functor(context)
    return res


def ApplyToAllElementsInA(a:VAL, b:VAL,functor) -> VAL:
    res = NON()
    if(IsList(a)):
        res = LST([ApplyToAllElementsInA(c,b,functor) for c in a])
    elif(isinstance(a, TRM)):
        res = a
    else:
        res = functor(a,b)
    return res

def ApplyToAllElementsInB(a:VAL, b:VAL, functor) -> VAL:
    res = NON()
    if(IsList(b)):
        res = LST([ApplyToAllElementsInB(a,c,functor) for c in b])
    else:
        res = functor(a,b)
    return res

def ApplyToAllListsOfElementsInA(a,b,functor):
    res = NON()
    if(IsListOfObjects(a)):
        res = functor(a,b)
    else:
        res = LST([ApplyToAllListsOfElementsInA(c,b,functor) for c in a])
    return res

def ApplyToAllListsOfElementsInB(a,b,functor):
    res = NON()
    if(IsListOfObjects(b)):
        res = functor(a,b)
    else:
        res = LST([ApplyToAllListsOfElementsInB(a,c,functor) for c in b])
    return res

def ApplyToSimilarListsOfObjects(op1,op2,listVsListFunc,listVsStructFunc,structVsListOp,param=None):
    res = NON()
    if(IsListOfObjects(op1) and IsListOfObjects(op2)):
        res = listVsListFunc(op1,op2,param)
    elif(IsListOfObjects(op1)):
        res = listVsStructFunc(op1,op2,param)
    elif(IsListOfObjects(op2)):
        res = structVsListOp(op1,op2,param)
    elif(len(op1) == len(op2)):
        res = LST([ApplyToSimilarListsOfObjects(op1[i],op2[i],listVsListFunc,listVsStructFunc,structVsListOp,param) for i in range(len(op1))])
    else:
        raise EOQ_ERROR_INVALID_VALUE("Non comparable element list structures detected.")
    return res

def ApplyToSimilarElementStrutures(op1,op2,elemVsElemFunc,elemVsStruct,structVsElemOp,param=None):
    res = NON()
    if(IsNoList(op1) and IsNoList(op2)):
        res = elemVsElemFunc(op1,op2,param)
    elif(IsNoList(op1)):
        res = elemVsStruct(op1,op2,param)
    elif(IsNoList(op2)):
        res = structVsElemOp(op1,op2,param)
    elif(len(op1) == len(op2)):
        res = LST([ApplyToSimilarElementStrutures(op1[i],op2[i],elemVsElemFunc,elemVsStruct,structVsElemOp,param) for i in range(len(op1))])
    else:
        raise EOQ_ERROR_INVALID_VALUE("Non comparable element structures detected.")
    return res

def IsList(val:VAL) -> bool:
    return LST == type(val)

def IsNoList(val:VAL) -> bool:
    return LST != type(val)

def IsListOfObjects(obj:VAL) -> bool:
    """Check if obj is a list of elements, but not a list of lists.
    """
    if(IsList(obj)):
        if(len(obj)==0): 
            return True
        for o in obj:
            if IsList(o):
                return False #any non list object make the search fail
        return True
    return False

def ShowProgress(progress):
    print('Total progress: %d%%'%(progress))
    return
