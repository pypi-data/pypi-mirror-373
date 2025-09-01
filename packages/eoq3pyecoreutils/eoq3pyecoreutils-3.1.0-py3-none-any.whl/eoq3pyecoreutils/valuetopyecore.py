'''
 Bjoern Annighoefer 2021
'''

from eoq3.value import VAL, BOL, I32, I64, F32, F64, STR, DAT, NON
from eoq3.error import EOQ_ERROR_UNSUPPORTED
from pyecore.ecore import EBoolean,EInt,EInteger,ELong,EFloat,EDouble,EString,EDate,EObject

    
### VALUE TO ECORE MAPPINGS AND BACK ####    

ETYPE_TO_VALUETYPE_LOT = { EBoolean : BOL,
                            EInteger : I32,
                            EInt : I32,
                            ELong : I64,
                            EFloat : F32,
                            EDouble : F64,
                            EString : STR,
                            EDate : DAT}  

VALUETYPE_TO_ETYPE_LOT = {v: k for k, v in ETYPE_TO_VALUETYPE_LOT.items()}


EVALUE_TO_VALUE_LOT = { EBoolean : lambda v: BOL(v),
                        EInteger : lambda v: I32(v),
                        EInt : lambda v: I32(v),
                        ELong : lambda v: I64(v),
                        EFloat : lambda v: F32(v),
                        EDouble : lambda v: F64(v),
                        EString : lambda v: STR(v),
                        EDate : lambda v: DAT(v)}  


VALUE_TO_EVALUE_LOT = { BOL : lambda v: v.GetVal(),
                        I32 : lambda v: v.GetVal(),
                        I64 : lambda v: v.GetVal(),
                        F32 : lambda v: v.GetVal(),
                        F64 : lambda v: v.GetVal(),
                        STR : lambda v: v.GetVal(),
                        DAT : lambda v: v.GetVal(),
                        NON : lambda v: v.GetVal()}  

def ETypeToValueType(eType : EObject) -> object:
    try:
        return ETYPE_TO_VALUETYPE_LOT[eType]
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Ecore type %s is not supported'%(eType.name))
    
def ValueTypeToEType(vType : object) -> EObject:
    try:
        return VALUETYPE_TO_ETYPE_LOT[vType]
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Value type %s is not supported'%(vType.__name__))

def EValueToValue(eValue,eType : EObject) -> VAL: #two parameters are needed because pyecore uses the native python types which can not retrieve the EDataType
    try:
        if(None == eValue):
            return NON()
        else:
            return EVALUE_TO_VALUE_LOT[eType](eValue)
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Ecore type %s is not supported'%(eType.name))
    
def ValueToEValue(value : VAL):
    try:
        lot = VALUE_TO_EVALUE_LOT[type(value)]
        return lot(value) 
    except KeyError:
        raise EOQ_ERROR_UNSUPPORTED('Value type %s is not supported by ecore'%(value.val))
    
    