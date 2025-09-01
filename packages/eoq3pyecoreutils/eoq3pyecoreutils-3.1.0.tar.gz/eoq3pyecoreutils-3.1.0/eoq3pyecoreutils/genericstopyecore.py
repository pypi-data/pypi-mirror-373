'''
 Bjoern Annighoefer 2021
'''

from eoq3.concepts import M2PRIMITIVES
from eoq3.value import BOL, U32, U64, I32, I64, F32, F64, STR, DAT
from eoq3.error import EOQ_ERROR_UNSUPPORTED
from pyecore.ecore import EBoolean, EInteger, EInt, ELong, EFloat, EDouble, EString, EDate, EObject, EEnum

### EANNOTATION SOURCE AND KEY DEFINITIONS ###

EOQ_GENERICS_SOURCE = 'https://www.eoq-dsm.org/ecoremapping/generics'

class EANNOTATION_SOURCES:
    DOCUMENTATION = 'http://www.eclipse.org/emf/2002/GenModel'
    CONSTRAINTS   = 'https://www.eoq-dsm.org/ecoremapping/constraints' #value = <query expression that evals to bool>
    OWNER         = EOQ_GENERICS_SOURCE
    GROUP         = EOQ_GENERICS_SOURCE
    PERMISSIONS   = 'https://www.eoq-dsm.org/ecoremapping/access' #value = <feature name>::<string in the form "sss" = s in {x,r,w} for owner, group and all (like unix file permissions>
    UNIT          = EOQ_GENERICS_SOURCE
    ID            = EOQ_GENERICS_SOURCE
    
class EANNOTATION_KEYS:
    DOCUMENTATION = 'documentation'
    OWNER         = 'owner'
    GROUP         = 'group'
    UNIT          = 'unit'
    ID            = 'id'
    


### GENERICS TO ECORE MAPPINGS AND BACK ###

SUPPORTED_ETYPES = [EBoolean, EInteger, EInt, ELong, EFloat, EDouble, EString, EDate]

SUPPORTED_GENERICS = [g for g in M2PRIMITIVES.__dict__.keys() if not g.startswith('_') ]


GENERICS_TO_EVALUE_LOT = {  M2PRIMITIVES.BOL : EBoolean,
                            M2PRIMITIVES.U32 : EInt,
                            M2PRIMITIVES.U64 : ELong,
                            M2PRIMITIVES.I32 : EInt,
                            M2PRIMITIVES.I64 : ELong,
                            M2PRIMITIVES.F32 : EFloat,
                            M2PRIMITIVES.F64 : EDouble,
                            M2PRIMITIVES.STR : EString, 
                            M2PRIMITIVES.DAT : EDate,
                            None : None }

EVALUE_TO_CONCEPTID_LOT = { EBoolean : M2PRIMITIVES.BOL,
                            EInt : M2PRIMITIVES.I32,
                            ELong : M2PRIMITIVES.I64,
                            EFloat : M2PRIMITIVES.F32,
                            EDouble : M2PRIMITIVES.F64,
                            EString : M2PRIMITIVES.STR ,
                            EDate : M2PRIMITIVES.DAT,
                            None : None}

EVALUE_TO_CONCEPT_LOT = {   EBoolean : BOL,
                            EInt : I32,
                            ELong : I64,
                            EFloat : F32,
                            EDouble : F64,
                            EString : STR ,
                            EDate : DAT}

PRMCLASS_TO_PRMID_LOT = {   BOL : M2PRIMITIVES.BOL,
                            U32 : M2PRIMITIVES.U32,
                            U64 : M2PRIMITIVES.U64,
                            I32 : M2PRIMITIVES.I32,
                            I64 : M2PRIMITIVES.I64,
                            F32 : M2PRIMITIVES.F32,
                            F64 : M2PRIMITIVES.F64,
                            STR : M2PRIMITIVES.STR ,
                            DAT : M2PRIMITIVES.DAT}

PRMID_TO_PRMCLASS_LOT = {   M2PRIMITIVES.BOL : BOL,
                            M2PRIMITIVES.U32 : U32,
                            M2PRIMITIVES.U64 : U64,
                            M2PRIMITIVES.I32 : I32,
                            M2PRIMITIVES.I64 : I64,
                            M2PRIMITIVES.F32 : F32,
                            M2PRIMITIVES.F64 : F64,
                            M2PRIMITIVES.STR : STR,
                            M2PRIMITIVES.DAT : DAT}
    

### Special ECORE methods ###


def IsEPrimitiveType(eType : EObject):
    return (eType in SUPPORTED_ETYPES) #EObject is not desired here, but there is usually no entry for EObject

def IsGenericPrimitiveType(valueType : str) -> EObject:
    return (valueType in SUPPORTED_GENERICS)

def EAttributeTypeConceptPrimitiveId(eType : EObject) -> str:
    try:
        return EVALUE_TO_CONCEPTID_LOT[eType]
    except KeyError:
        if(isinstance(eType,EEnum)):
            return M2PRIMITIVES.ENU
        else:
            raise EOQ_ERROR_UNSUPPORTED('Unsupported ecore primitive type %s'%(eType.name))
    
def EPrimitiveTypeToGenericPrimitiveType(eType : EObject) -> str:
    try:
        return EVALUE_TO_CONCEPT_LOT[eType]
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Unsupported ecore primitive type %s'%(eType.name))
    
def GenericPrimitiveTypeToEPrimitiveType(valueType : str):
    try: 
        return GENERICS_TO_EVALUE_LOT[valueType]
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Unsupported primitive type %s'%(valueType))
    
def ConceptPrimitiveTypeToPrimitiveId(clazz:object):
    try: 
        return PRMCLASS_TO_PRMID_LOT[clazz]
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Unsupported primitive %s'%(clazz))
    
def ConceptPrimitiveIdToPrimitiveType(prmId:str):
    try: 
        return PRMID_TO_PRMCLASS_LOT[prmId]
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Unsupported primitive %s'%(prmId))
    
