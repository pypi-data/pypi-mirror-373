'''
 concepts.py provides a generic interface each model back-end working with eoq3 should support. 
 Concepts are generic constructs that should be available in any domain-specific framework and 
 modeling language. 
 
 This file is generated form: concepts.py.mako on 2025-08-29 10:20:40.090697 by calling E:/1_ILS/Projects/2025_IlsHackathon/Repos/hackathon/pyeoq/eoq3conceptsgen/generatefromconceptscli.py -i concepts.py.mako -o ../concepts.py.
 
 Bjoern Annighoefer 2023
'''

'''
DEFINITIONS 
'''

CONCEPT_PREFIX = '*'
FEATURE_MULTIVALUE_POSTFIX = '*'
CONCEPT_PREFIX_LEN = len(CONCEPT_PREFIX)
CONCEPT_UNIQUE_LEN = 4 #statically defined. Checked in generate concepts


class CONCEPTS:
    def __init__(self):
        raise NotImplementedError()
    MXMDB = "*MXMDB" # Create the MDB to get the ID. Always the same ID is returned.
    MXELEMENT = "*MXELEMENT" # 
    MXCONSTRAINT = "*MXCONSTRAINT" # 
    M2PRIMITIVES = "*M2PRIMITIVES" # The primitive data types. This is used to type M2 attributes. This concept cannot be instantiated.
    M2PACKAGE = "*M2PACKAGE" # A package is the container of M2 elements such as classes an enums. 
    M2MODEL = "*M2MODEL" # An M2 model is the root package of a M2 model.
    M2ENUM = "*M2ENUM" # An enumeration data type.
    M2OPTIONOFENUM = "*M2OPTIONOFENUM" # One option of one enumeration data type.
    M2CLASS = "*M2CLASS" # A class definition.
    M2ATTRIBUTE = "*M2ATTRIBUTE" # The definition of an attribute feature for an M2 class.
    M2ASSOCIATION = "*M2ASSOCIATION" # The definition of an association feature for an M2 class.
    M2COMPOSITION = "*M2COMPOSITION" # The definition of a composition feature for an M2 class.
    M2INHERITANCE = "*M2INHERITANCE" # An inheritance defines a bilateral inheritance of one M2 class from another.
    M1MODEL = "*M1MODEL" # A container for one user mode.
    M1OBJECT = "*M1OBJECT" # An instance of an M2 class.
    M1FEATURE = "*M1FEATURE" # 
    M1ATTRIBUTE = "*M1ATTRIBUTE" # An instance of an M2 attribute for one M1 object and one value.
    M1ASSOCIATION = "*M1ASSOCIATION" # An instance of an M2 association for a relation of two M1 objects.
    M1COMPOSITION = "*M1COMPOSITION" # An instance of an M2 composition for the containment of one M1 object in on other M1 object.


'''
Mx LAYER
Elements that can exist in M1 or M2 layer or outside of them.
'''
class MXMDB:
    def __init__(self):
        raise NotImplementedError()
    CONCEPT = "*CONCEPT" #   STR   1   1 The concept ID of the concept.
    M2MODELS = "*M2MODELS*" # M2Model   0  -1 All M2 models
    M1MODELS = "*M1MODELS*" # M1Model   0  -1 All M1 models
    MDB = "*MDB" # MxMdb   1   1 The MXMDB of this element. In this case it is pointing to myself
    
class MXELEMENT:
    def __init__(self):
        raise NotImplementedError()
    CONCEPT = "*CONCEPT" #   STR   1   1 The concept ID string
    STRID = "*STRID" #   STR   0   1 A unique ID within the MDB
    DOCUMENTATION = "*DOCUMENTATION" #   STR   0   1 A string describing this model element
    OWNER = "*OWNER" #   STR   0   1 TBD: The user name of the owner like in Unix file systems
    GROUP = "*GROUP" #   STR   0   1 TBD: The group name of the owing group like in Unix file systems
    PERMISSIONS = "*PERMISSIONS*" #   STR   0  -1 TBD: A list of string values where each string specifies the read write and create rights for the element or subelements
    HASH = "*HASH" #   I64   0   1 TBD: HASH shall make elements addressable independent of internally assigned IDs, but this is only an idea so far.
    CONSTRAINTS = "*CONSTRAINTS*" # MxConstraint   0  -1 All constraints attached to this element
    MDB = "*MDB" # MxMdb   1   1 The MXMDB of this element. In this case it is pointing to myself
    
class MXCONSTRAINT:
    def __init__(self):
        raise NotImplementedError()
    ELEMENT = "*ELEMENT" # MxElement   1   1 The element this constraint is attached to
    EXPRESSION = "*EXPRESSION" #   STR   1   1 A string holding the constraint expression. This must be a valid query resulting in a boolean.
    
'''
M2 LAYER
The meta-model layer.
'''
class M2PRIMITIVES:
    def __init__(self):
        raise NotImplementedError()
    BOL = "*BOL" #   BOL   0   0 Boolean value
    U32 = "*U32" #   U32   0   0 Unsigned integer 32 bit value
    U64 = "*U64" #   U64   0   0 Unsigned integer 64 bit value
    I32 = "*I32" #   I32   0   0 Signed integer 32 bit value
    I64 = "*I64" #   I64   0   0 Signed integer 64 bit value
    F32 = "*F32" #   F32   0   0 Floating point 32 bit value
    F64 = "*F64" #   F64   0   0 Floating point 64 bit value
    STR = "*STR" #   STR   0   0 String value
    DAT = "*DAT" #   DAT   0   0 Date and time value
    ENU = "*ENU" #   ENU   0   0 Enum value. This is only a place holder for enums defined in the meta model.
    
class M2PACKAGE:
    def __init__(self):
        raise NotImplementedError()
    NAME = "*NAME" #   STR   1   1 Name of the package
    SUPERPACKAGE = "*SUPERPACKAGE" # M2Package   0   1 The parent package or m2 model this package is contained in.
    SUBPACKAGES = "*SUBPACKAGES*" # M2Package   0  -1 All contained subpackage
    CLASSES = "*CLASSES*" # M2Class   0  -1 All M2 classes
    ENUMS = "*ENUMS*" # M2Enum   0  -1 All M2 Enums
    M1MODELS = "*M1MODELS*" # M1Model   0  -1 All M1 models instantiating this package
    
class M2MODEL:
    def __init__(self):
        raise NotImplementedError()
    
class M2ENUM:
    def __init__(self):
        raise NotImplementedError()
    NAME = "*NAME" #   STR   1   1 The name of the enum
    PACKAGE = "*PACKAGE" # M2Package   1   1 The package the enum is contained in.
    OPTIONS = "*OPTIONS*" # M2OptionOfEnum   0  -1 All options of the enum.
    ATTRIBUTES = "*ATTRIBUTES*" # M2Attribute   0  -1 All M2 attributes using this enum as type
    
class M2OPTIONOFENUM:
    def __init__(self):
        raise NotImplementedError()
    NAME = "*NAME" #   STR   1   1 The name of the enum option. This is used for setting the enum
    VALUE = "*VALUE" #   U64   1   1 An optional integer value for the enum option
    ENUM = "*ENUM" # M2Enum   1   1 The enum this option belongs to.
    M1ATTRIBUTESUSINGOPTION = "*M1ATTRIBUTESUSINGOPTION*" # M1Attribute   0  -1 All instances of attributes on M1 level, that use this value
    
class M2CLASS:
    def __init__(self):
        raise NotImplementedError()
    NAME = "*NAME" #   STR   1   1 The name of the M2 class
    ISABSTRACT = "*ISABSTRACT" #   BOL   1   1 Whether the class is abstract or not.
    PACKAGE = "*PACKAGE" # M2Package   1   1 Whether this class is abstract or not.
    INSTANCES = "*INSTANCES*" # M1Object   0  -1 All instances of this or derived classes. This is not a delete blocker, because if inherit classes exist the inheritance will prevent the deletion already.
    MYINSTANCES = "*MYINSTANCES*" # M1Object   0  -1 All type-identical instances of this class. This is a delete blocker.
    MYATTRIBUTES = "*MYATTRIBUTES*" # M2Attribute   0  -1 The attribute definitions of this class.
    ATTRIBUTES = "*ATTRIBUTES*" # M2Attribute   0  -1 The attribute definitions of this and all superclasses.
    MYSRCASSOCIATIONS = "*MYSRCASSOCIATIONS*" # M2Association   0  -1 Associations, which start at this class.
    SRCASSOCIATIONS = "*SRCASSOCIATIONS*" # M2Association   0  -1 Associations, which start at this class or any superclass.
    MYDSTASSOCIATIONS = "*MYDSTASSOCIATIONS*" # M2Association   0  -1 Associations, which end at this class. Must not include any-associations
    DSTASSOCIATIONS = "*DSTASSOCIATIONS*" # M2Association   0  -1 Associations, which end at this class or any super class. Should include any-associations
    MYPARENTCOMPOSITIONS = "*MYPARENTCOMPOSITIONS*" # M2Composition   0  -1 Composition where I am the parent
    PARENTCOMPOSITIONS = "*PARENTCOMPOSITIONS*" # M2Composition   0  -1 Compositions where I am the parent, including the ones from superclasses.
    MYCHILDCOMPOSITIONS = "*MYCHILDCOMPOSITIONS*" # M2Composition   0  -1 Compositions where I am the child. 
    CHILDCOMPOSITIONS = "*CHILDCOMPOSITIONS*" # M2Composition   0  -1 Compositions where I am the child, including the ones from superclasses.
    MYSPECIALIZATIONS = "*MYSPECIALIZATIONS*" # M2Inheritance   0  -1 All inheritances where this class is the inheriting class.
    SPECIALIZATIONS = "*SPECIALIZATIONS*" # M2Inheritance   0  -1 All inheritances where this class or any superclass is the inheriting class.
    MYGENERALIZATIONS = "*MYGENERALIZATIONS*" # M2Inheritance   0  -1 All inheritances where this class is the superclass.
    GENERALIZATIONS = "*GENERALIZATIONS*" # M2Inheritance   0  -1 All inheritances where this class or any subclass is the superclass.
    
class M2ATTRIBUTE:
    def __init__(self):
        raise NotImplementedError()
    NAME = "*NAME" #   STR   1   1 The name of the attribute.
    CLASS = "*CLASS" # M2Class   1   1 The class this attribute definition is assigned to.
    PRIMTYPE = "*PRIMTYPE" #   STR   1   1 The primitive type, i.e. *BOL,*U32, *U64, ...., *STR, *ENU
    MUL = "*MUL" #   I64   1   1 The maximum number of values that can be stored in this attribute.
    UNIT = "*UNIT" #   STR   0   1 A unit string for that shall be valid for all values stored in this attribute.
    ENUM = "*ENUM" # M2Enum   0   1 An M2Enum, if PrimType is *NEU, else NON.
    MYINSTANCES = "*MYINSTANCES*" # M1Attribute   0  -1 All instances of this attribute definition in any M1 model.
    
class M2ASSOCIATION:
    def __init__(self):
        raise NotImplementedError()
    SRCNAME = "*SRCNAME" #   STR   1   1 The source name, i.e. the name used to navigate from the destination object to the source object(s).
    SRCCLASS = "*SRCCLASS" # M2Class   1   1 The source class.
    SRCMUL = "*SRCMUL" #   I64   1   1 The maximum number of elements on the source side of the association.
    DSTNAME = "*DSTNAME" #   STR   1   1 The destination name, i.e. the name used to navigate from the source object to the destination object(s).
    DSTCLASS = "*DSTCLASS" # M2Class   0   1 The destination class.
    DSTMUL = "*DSTMUL" #   I64   1   1 The maximum number of elements on the destination side of the association.
    ANYDST = "*ANYDST" #   BOL   1   1 If true, any elements of any type can be at the source. If true, dstClass must be NON.
    MYINSTANCES = "*MYINSTANCES*" # M1Association   0  -1 All instances of this association definition in any M1 model.
    
class M2COMPOSITION:
    def __init__(self):
        raise NotImplementedError()
    NAME = "*NAME" #   STR   1   1 The name of the composition.
    PARENTCLASS = "*PARENTCLASS" # M2Class   1   1 The parent class.
    CHILDCLASS = "*CHILDCLASS" # M2Class   0   1 The child class.
    MULCHILD = "*MULCHILD" #   I64   1   1 The maximum number of children in on the child side of this composition.
    ANYCHILD = "*ANYCHILD" #   BOL   1   1 If true, any elements of any type can be at the child. If true, childClass must be NON.
    MYINSTANCES = "*MYINSTANCES*" # M1Composition   0  -1 All instances of this composition
    
class M2INHERITANCE:
    def __init__(self):
        raise NotImplementedError()
    SUBCLASS = "*SUBCLASS" # M2Class   1   1 The inheriting class.
    SUPERCLASS = "*SUPERCLASS" # M2Class   1   1 The superclass.
    M1ATTRIBUTESBYINHERITANCE = "*M1ATTRIBUTESBYINHERITANCE*" # M1Attribute   0  -1 Delete blocker for inheritances. It is not valid to delete an inheritance if instances of the subclass exist.
    M1ASSOCIATIONSBYINHERITANCE = "*M1ASSOCIATIONSBYINHERITANCE*" # M1Association   0  -1 Delete blocker for inheritances. It is not valid to delete an inheritance if instances of the subclass exist.
    M1COMPOSITIONSBYINHERITANCE = "*M1COMPOSITIONSBYINHERITANCE*" # M1Composition   0  -1 Delete blocker for inheritances. It is not valid to delete an inheritance if instances of the subclass exist.
    
'''
M1 LAYER
The user model layer.
'''
class M1MODEL:
    def __init__(self):
        raise NotImplementedError()
    M2MODEL = "*M2MODEL" # M2Model   1   1 The M2 model instantiated by this M1 model.
    NAME = "*NAME" #   STR   1   1 The name of the M1 model.
    OBJECTS = "*OBJECTS*" # M1Object   0  -1 All M1 objects in this model.
    
class M1OBJECT:
    def __init__(self):
        raise NotImplementedError()
    M2CLASS = "*M2CLASS" # M2Class   1   1 The M2 class instantiated.
    MODEL = "*MODEL" # M1Model   1   1 The M1 model this object belongs to.
    NAME = "*NAME" #   STR   1   1 The name of the M1 object.
    ATTRIBUTES = "*ATTRIBUTES*" # M1Attribute   0  -1 All attribute instances. One instance is one value of any attribute definition of the class.
    SRCASSOCIATIONS = "*SRCASSOCIATIONS*" # M1Association   0  -1 All associations instances where I am the source. One instance is a 1-to-1 link.
    DSTASSOCIATIONS = "*DSTASSOCIATIONS*" # M1Association   0  -1 All associations instances where I am the destination. One instance is a 1-to-1 link.
    PARENTCOMPOSITIONS = "*PARENTCOMPOSITIONS*" # M1Composition   0  -1 All composition instances where I am the parent. One instance is a 1-to-1 containment.
    CHILDCOMPOSITION = "*CHILDCOMPOSITION" # M1Composition   0   1 The composition instance where I am the child . It is a 1-to-1 containment.
    FEATUREVALUES = "*FVAL" #   VAL   0   1 
    FEATUREINSTANCES = "*FINS" # M1Feature   0   1 
    
class M1FEATURE:
    def __init__(self):
        raise NotImplementedError()
    
class M1ATTRIBUTE:
    def __init__(self):
        raise NotImplementedError()
    M2ATTRIBUTE = "*M2ATTRIBUTE" # M2Attribute   1   1 The M2 attribute this is an instance of.
    OBJECT = "*OBJECT" # M1Object   1   1 The M1 object this instance belongs to.
    VALUE = "*VALUE" #   PRM   1   1 The value of this instance. There is exactly one value per instance.
    POS = "*POS" #   U64   1   1 The position of the value in multi-value attributes, e.g. M2 attribute mul > 1.
    
class M1ASSOCIATION:
    def __init__(self):
        raise NotImplementedError()
    M2ASSOCIATION = "*M2ASSOCIATION" # M2Association   1   1 The M2 association this is an instance of.
    SRC = "*SRC" # M1Object   1   1 The M1 object being at the source end of this association.
    SRCPOS = "*SRCPOS" #   U64   1   1 The position of the src in multi-element associations, e.g. M2 association srcMul > 1.
    DST = "*DST" # M1Object   1   1 The M1 object being at the destination end of this association. Type must be MXELEMENT to allow ASSOCIATIONs to meta elements.
    DSTPOS = "*DSTPOS" #   U64   1   1 The position of the dst in multi-element associations, e.g. M2 association dstMul > 1.
    
class M1COMPOSITION:
    def __init__(self):
        raise NotImplementedError()
    M2COMPOSITION = "*M2COMPOSITION" # M2Composition   1   1 The M2 composition this is an instance of.
    PARENT = "*PARENT" # M1Object   1   1 The M1 object being at the parent of this composition.
    CHILD = "*CHILD" # M1Object   1   1 The M1 object being at the child ff this composition. Type must be MXELEMENT to allow ASSOCIATIONs to meta elements.
    POS = "*POS" #   U64   1   1 This is the position of the child. The parent position is always 1.
    

def IsConcept(name : str):
    return name.startswith(CONCEPT_PREFIX)

def IsMultivalueFeature(featureName : str):
    return featureName.endswith(FEATURE_MULTIVALUE_POSTFIX)

def NormalizeFeatureName(featureName : str):
    n = len(featureName)
    #start = 1 if featureName.startswith(GENERIC_FEATURE_PREFIX) or featureName.startswith(FEATURE_READONLY_PREFIX) else 0
    end = n-1 if featureName.endswith(FEATURE_MULTIVALUE_POSTFIX) else n
    return featureName[:end]

def IsNameFeature(featureName : str):
    '''Checks whether the given feature corresponds to a name feature.
    *NAME is a concept feature and custom name features are not supported.
    '''
    return featureName.upper() == "NAME"

def GetConceptKeyString(conceptName:str)->str:
    '''Extracts the first and unique chars of a concept or concept feature name and returns it
    '''
    paddedName = conceptName+"    "
    return paddedName[CONCEPT_PREFIX_LEN:(CONCEPT_PREFIX_LEN+CONCEPT_UNIQUE_LEN)]
