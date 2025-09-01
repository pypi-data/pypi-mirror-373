'''Permissions are indicate the what can be done with a model element. 
A permission is composed of three byte:
1. byte: owner (O) rights
2. byte: group (G) rights
3. byte: anybody (A) rights
Each byte has four bit flags, i.e. the CRUD -> CDRU flags

1 bit C: Create  (only makes sense for classes)
2 bit R: Read 
3 bit U: Update
4 bit D: Delete

permissions are stored as big endian integers or hex strings

Example:

- A class that can only be modified by the owner, but instantiated by the group and can be read by anybody


      owner  |  group  | anybody
     C R U D | C R U D | C R U D     
Bit: 1 1 1 1 | 1 1 0 0 | 0 1 0 0

Bjoern Annighoefer 2022
'''

from ..error import EOQ_ERROR_INVALID_VALUE
#type checking
from typing import Tuple

### PERMISSION ###

class PERMISSION_FLAGS:
    #ANYBODY
    ANYBODY_CREATE    = (2**3)
    ANYBODY_READ      = (2**2)
    ANYBODY_UPDADE    = (2**1)
    ANYBODY_DELETE    = (2**0)
    #GROUP
    GROUP_CREATE      = (2**3)<<4
    GROUP_READ        = (2**2)<<4
    GROUP_UPDADE      = (2**1)<<4
    GROUP_DELETE      = (2**0)<<4
    #OWNER
    OWNER_CREATE      = (2**3)<<8
    OWNER_READ        = (2**2)<<8
    OWNER_UPDADE      = (2**1)<<8
    OWNER_DELETE      = (2**0)<<8

def PermissionToStr(permission:int)->str:
    return "%3x"%(permission)

def StrToPermission(permissionStr:str)->int:
    return int(permissionStr,base=16)
 
### FEATURE PERMISSSIONS ###   
    
PERMISSION_STR_SEPERATOR = '::'

WILDCARD_FEATURE_NAME = '*'
    
def GenerateFeaturePermissionStr(featureName:str, permission:int)->str:
    return "%3x%s%s"%(permission,PERMISSION_STR_SEPERATOR,featureName) 

def ParseFeaturePermissionStr(featurePermissionStr:str)->Tuple[str,int]:
    i = featurePermissionStr.find(PERMISSION_STR_SEPERATOR)
    if(i != 3):
        raise EOQ_ERROR_INVALID_VALUE("Invalid feature permission string: %s"%(featurePermissionStr))
    permission = StrToPermission(featurePermissionStr[0:3])
    featureName = featurePermissionStr[5:]
    return (featureName,permission)
    
