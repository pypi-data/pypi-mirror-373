from typing import Dict, List, Type

# BASIC ERROR CLASS
class EOQ_ERROR(Exception):
    ''' The class a exceptions thrown in the EOQ eco system inherit from
    
    '''
    def __init__(self, prefix:str, code:int, msg:str, trace:str=""):
        self.prefix = prefix
        self.code = code
        self.msg = msg
        self.trace = trace
        
    def __str__(self):
        return "%s(%d): %s%s"%(self.prefix,self.code,self.msg," trace=%s"%(self.trace) if self.trace else "")

# EOQ ERROR REGISTRY
class EoqErrorInfo:
    ''' A class to store the error information in the EOQ error registry
    
    '''
    def __init__(self, code:int, description:str, errorClass):
        self.code = code
        self.description = description
        self.errorClass = errorClass
        
EOQ_ERROR_TYPE_REGISTRY:Dict[int,EoqErrorInfo] = {} # code -> EoqErrorInfo

def RegisterEoqErrorType(code:int, description:str, clazz:Type[EOQ_ERROR]):
    ''' Each new instance of EOQ should be registered in the error registry. 
    
    This enables automatic instantiation of the errors based on the code using the EoqErrorFactory.
    Each inherit error class must exhibit the same interface.
    
    '''
    if(code in EOQ_ERROR_TYPE_REGISTRY):
        raise EOQ_ERROR_RUNTIME('Error code %d is already registered.'%(code))
    else:
        EOQ_ERROR_TYPE_REGISTRY[code] = EoqErrorInfo(code, description, clazz)     




class EOQ_ERROR_CODES:
    ''' This is a general set of errors in EOQ that should be used for any error returned by eoq
    '''
    INVALID_TYPE           = 1 #not the the expected data type
    INVALID_VALUE          = 2 #not the expected value (e.g. range)
    INVALID_OPERATION      = 3 #operation is (currently) not possible
    DOES_NOT_EXIST         = 4 #no such element
    RUNTIME                = 5 #error during operation
    ACCESS_DENIED          = 6 #any failure resulting from access rights
    UNSUPPORTED            = 7 #something is not implemented or not supported with the current library
    UNKNOWN                = 9 #Something that should not happen and is not understood by EOQ
    
    
### SPECIALIZED ERROR CLASSES 
class EOQ_ERROR_INVALID_TYPE(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_INVALID_TYPE',EOQ_ERROR_CODES.INVALID_TYPE, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.INVALID_TYPE,'The data type used is not supported here.',EOQ_ERROR_INVALID_TYPE)

class EOQ_ERROR_INVALID_VALUE(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_INVALID_VALUE',EOQ_ERROR_CODES.INVALID_VALUE, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.INVALID_VALUE,'The value given is not expected.',EOQ_ERROR_INVALID_VALUE)

class EOQ_ERROR_INVALID_OPERATION(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_INVALID_OPERATION',EOQ_ERROR_CODES.INVALID_OPERATION, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.INVALID_OPERATION,'This operation is (currently) not possible.',EOQ_ERROR_INVALID_OPERATION)

class EOQ_ERROR_DOES_NOT_EXIST(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_DOES_NOT_EXIST',EOQ_ERROR_CODES.DOES_NOT_EXIST, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.DOES_NOT_EXIST,'Tried to access an non exiting element, attribute or index.',EOQ_ERROR_DOES_NOT_EXIST)

class EOQ_ERROR_RUNTIME(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_RUNTIME',EOQ_ERROR_CODES.RUNTIME, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.RUNTIME,'The operation failed.',EOQ_ERROR_RUNTIME)

class EOQ_ERROR_ACCESS_DENIED(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_ACCESS_DENIED',EOQ_ERROR_CODES.ACCESS_DENIED, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.ACCESS_DENIED,'Insufficient access rights.',EOQ_ERROR_ACCESS_DENIED)

class EOQ_ERROR_UNSUPPORTED(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_UNSUPPORTED',EOQ_ERROR_CODES.UNSUPPORTED, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.UNSUPPORTED,'The operation is not implemented.',EOQ_ERROR_UNSUPPORTED)

class EOQ_ERROR_UNKNOWN(EOQ_ERROR):
    def __init__(self, msg:str, trace:str=""):
        super().__init__('EOQ_ERROR_UNKNOWN',EOQ_ERROR_CODES.UNKNOWN, msg, trace)
RegisterEoqErrorType(EOQ_ERROR_CODES.UNKNOWN,'The reason for the error is not known.',EOQ_ERROR_UNKNOWN)



### ERROR FACTORY ###
        
def EoqErrorFactory(code:int, msg:str, trace:str='')->EOQ_ERROR:
    if(code in EOQ_ERROR_TYPE_REGISTRY):
        errorClass = EOQ_ERROR_TYPE_REGISTRY[code].errorClass
        return errorClass(msg, trace)
    else: 
        return EOQ_ERROR_UNKNOWN("Unknown error type %d: %s"%(code, msg))
    
def EoqErrorAsString(error:EOQ_ERROR):
    return str(error)
    
        

    