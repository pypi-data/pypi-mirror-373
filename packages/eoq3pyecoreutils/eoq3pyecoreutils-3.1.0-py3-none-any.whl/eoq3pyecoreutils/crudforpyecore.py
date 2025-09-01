'''
Functions for applying CRUD commands to pyecore models.

2022 Bjoern Annighoefer
'''


from .genericstopyecore import GenericPrimitiveTypeToEPrimitiveType, EANNOTATION_SOURCES, EANNOTATION_KEYS
from .pyecorepatch import IsEObjectAnnotationsPatchEnabled

from eoq3.concepts import *
from eoq3.error import EOQ_ERROR_INVALID_VALUE
from pyecore.ecore import EObject, EAnnotation, EClass, EPackage, EAttribute, EReference, EEnum, EEnumLiteral, EStructuralFeature,\
    EModelElement

### CONSTANTS ###
class UPDATE_MODES:
    REPLACE = 1
    INSERT = 2
    REMOVE = 3
    
GENERIC_ELEMENTS_LUT = {
    CONCEPTS.M2CLASS        : lambda n : EClass(n),
    CONCEPTS.M2PACKAGE      : lambda n : EPackage(n),
    CONCEPTS.M2ENUM         : lambda n : EEnum(n),
    CONCEPTS.M2ATTRIBUTE    : lambda n : EAttribute(n),
    CONCEPTS.M2ASSOCIATION  : lambda n : EReference(n,containement=False),
    CONCEPTS.M2COMPOSITION  : lambda n : EReference(n,containment=True),
    CONCEPTS.M2OPTIONOFENUM   : lambda n : EEnumLiteral(n)
}

GENERIC_FEATURE_TRANSLATE_LUT = {
    M2CLASS.NAME            : ("name", lambda e : True),
    M2CLASS.ATTRIBUTES      : ("eStructuralFeatures", lambda e : isinstance(e,EAttribute)),
    M2CLASS.DSTASSOCIATIONS : ("eStructuralFeatures", lambda e : isinstance(e,EReference) and not e.containment),
    M2CLASS.PARENTCOMPOSITIONS : ("eStructuralFeatures", lambda e : isinstance(e,EReference) and e.containment),
    M2PACKAGE.NAME            : ("name", lambda e : True),
#     M2MODEL.ID              : ("nsURI", lambda e : True),
    M2PACKAGE.CLASSES         : ("eClassifiers", lambda e : isinstance(e,EClass)),
    M2PACKAGE.ENUMS           : ("eClassifiers", lambda e : isinstance(e,EEnum)),
#     M2MODEL.SUBPACKAGES: ("eSubpackages", lambda e : True),
    M2ATTRIBUTE.NAME        : ("name", lambda e : True),
    M2ATTRIBUTE.MUL         : ("upperBound", lambda e : True),
    M2ATTRIBUTE.PRIMTYPE    : ("eType", lambda e : True),
    M2ASSOCIATION.DSTNAME   : ("name", lambda e : True),
    M2ASSOCIATION.DSTMUL    : ("upperBound", lambda e : True),
    M2ASSOCIATION.DSTCLASS  : ("eType", lambda e : True),
    M2COMPOSITION.NAME      : ("name", lambda e : True),
    M2COMPOSITION.MULCHILD    : ("upperBound", lambda e : True),
    M2COMPOSITION.CHILDCLASS  : ("eType", lambda e : True),
    M2ENUM.NAME             : ("name", lambda e : True),
    M2ENUM.OPTIONS          : ("eLiterals", lambda e : True),
    M2OPTIONOFENUM.NAME       : ("name", lambda e : True),
    M2OPTIONOFENUM.VALUE      : ("value", lambda e : True),
}


ECORE_CLASSID_SEPERATOR = '::'

GENERIC_FEATURES_ANNOTATION_LUT = {
    MXELEMENT.DOCUMENTATION : (EANNOTATION_SOURCES.DOCUMENTATION,EANNOTATION_KEYS.DOCUMENTATION), 
    MXELEMENT.CONSTRAINTS   : (EANNOTATION_SOURCES.CONSTRAINTS  ,None),
    MXELEMENT.OWNER         : (EANNOTATION_SOURCES.OWNER        ,EANNOTATION_KEYS.OWNER),
    MXELEMENT.GROUP         : (EANNOTATION_SOURCES.GROUP        ,EANNOTATION_KEYS.GROUP),
    MXELEMENT.PERMISSIONS   : (EANNOTATION_SOURCES.PERMISSIONS  ,None),
    M2ATTRIBUTE.UNIT        : (EANNOTATION_SOURCES.UNIT         ,EANNOTATION_KEYS.UNIT)
}

### HELPER FUNCTIONS ###

def ClassIdToPackageAndName(classId:str)->(str,str):
    if(ECORE_CLASSID_SEPERATOR not in classId):
        raise EOQ_ERROR_INVALID_VALUE('No valid class ID: %s'%(classId))
    segs = classId.split(ECORE_CLASSID_SEPERATOR,1)
    return (segs[0],segs[1])
 
### UPDATE MODE AND POSITION ###   
    
def GetUpdateModeAndAbsPosition(nElements:int, position:int, eValue)->(int,int):
    # determine mode and absolute position from the index
    mode = UPDATE_MODES.REPLACE
    absPos = position
    if(None == eValue): #REMOVE
        mode = UPDATE_MODES.REMOVE
        if(position == -1):
            absPos = nElements-1
        elif(position < -1):
            absPos = -position-2 # -2 equals index 0, -3 equals index 1
    else: #REPLACE OR INSERT
        if(position == -1 or position == nElements):
            absPos = nElements
            mode = UPDATE_MODES.INSERT
        elif(position < -1):
            absPos = -position-2 # -2 equals index 0, -3 equals index 1
            mode = UPDATE_MODES.INSERT
    return (mode,absPos)

def ValidateUpdatePosition(mode,nElements,featureLength,position):
    if(UPDATE_MODES.REPLACE == mode):
        if(position >= nElements): 
            raise EOQ_ERROR_INVALID_VALUE('Cannot replace at position %d. This is after the last element which is %d'%(position,nElements))
    elif(UPDATE_MODES.INSERT == mode):
        if(featureLength > -1 and featureLength <= nElements):
            raise EOQ_ERROR_INVALID_VALUE('Cannot add element because the maximum of %d elements is reached.'%(featureLength))
        if(position >= nElements+1): 
            raise EOQ_ERROR_INVALID_VALUE('Cannot insert at position %d. This two or more positions behind the last element which is %d'%(position,nElements))

### CRUD FUNCTIONS ###

def CreateEObject(classId:str,name:str,eMetaModelRegistry:dict)->EObject:
    eObj = None
    eClass = None
    if(classId in GENERIC_ELEMENTS_LUT):
        eClass = GENERIC_ELEMENTS_LUT[classId]
        if(None == name):
            eObj = eClass()
        else:
            eObj = eClass(name)
    else:
        (packId,className) = ClassIdToPackageAndName(classId)
        #find the class given by the name and package
        try:
            ePackage = eMetaModelRegistry[packId]
        except KeyError:
            raise EOQ_ERROR_INVALID_VALUE("Unknown package: %s"%(packId))
        eClass = ePackage.getEClassifier(className)
        if(None == eClass):
            raise EOQ_ERROR_INVALID_VALUE("Unknown class %s of package %s"%(className,packId))
        eObj = eClass()
        if(None != name):
            eObj.name = name
    return eObj



def UpdateEObject(eTarget:EObject,featureName:str,eValue,position:int):
    eFeatureName = None
    oldEValue = None
    oldEParent = None
    if(featureName in GENERIC_FEATURES_ANNOTATION_LUT):
        (eAnnotationSource,eAnnotationKey) = GENERIC_FEATURES_ANNOTATION_LUT[featureName]
        if(eAnnotationKey): #single value annotation
            oldEValue = UpdateSingleValueEAnnotation(eTarget, eAnnotationSource, eAnnotationKey, eValue)
        else: #multivalue annotation
            oldEValue = UpdateMultiValueEAnnotation(eTarget, eAnnotationSource, eValue, position)
    else: #is a regular feature
        #try to find the feature name
        eFeatureName = None
        filterFunc = None
        if(featureName in GENERIC_FEATURE_TRANSLATE_LUT):
            (eFeatureName,filterFunc) = GENERIC_FEATURE_TRANSLATE_LUT[featureName]
        else:
            eFeatureName = NormalizeFeatureName(featureName)
            filterFunc = lambda e : True
        #see if we can find an old parent for the element    
        if(isinstance(eValue,EObject)):
            oldEParent = eValue.eContainer()
        #look if the feature exists
        eFeature = eTarget.eClass.findEStructuralFeature(eFeatureName)
        if(None == eFeature):
            raise EOQ_ERROR_INVALID_VALUE("Unknown feature: %s"%(eFeatureName))
        if(eFeature.many):
            oldEValue = UpdateMultiValueFeature(eTarget, eFeatureName, position, filterFunc, eValue)
        else: #single value feature
            oldEValue = UpdateSingleValueFeature(eTarget,eFeatureName,eValue)
    return (eFeatureName,oldEValue,oldEParent)

def DeleteEObject(eTarget:EObject)->None:
    eTarget.delete(True)

def UpdateSingleValueFeature(eTarget:EObject, eFeatureName:str, eValue):
    oldEValue = eTarget.eGet(eFeatureName)
    if(isinstance(eTarget,EStructuralFeature) and eFeatureName=="eType" and str == type(eValue)): #types of attributes are special, because those can be primitives
        eValue = GenericPrimitiveTypeToEPrimitiveType(eValue)
    eTarget.eSet(eFeatureName,eValue)
    return oldEValue

def UpdateMultiValueFeature(eTarget:EObject, eFeatureName:str, position:int, filterFunc:callable, eValue):
    oldEValue = None
    eSet = eTarget.eGet(eFeatureName)
    filteredElems = [e for e in eSet if filterFunc(e)]
    nElems = len(filteredElems)
    #n = len(eSet)
    
    (mode,absPos) = GetUpdateModeAndAbsPosition(nElems,position,eValue)
    # position sanity checks
    ValidateUpdatePosition(mode,nElems,-1,absPos)
    #3. carry out the update
    if(nElems == absPos): #can not happen for delete
        #old value stays None
        eSet.add(eValue)
    else: #it is not the last element that is added
        if(UPDATE_MODES.REPLACE == mode):
            oldEValue = filteredElems[position]
            sucessors = []
            sucessor = eSet.pop()
            while(sucessor != oldEValue):
                sucessors.append(sucessor)
                sucessor = eSet.pop()
            #add the new value
            eSet.add(eValue)
            #re-add the successors
            sucessors.reverse()
            for s in sucessors: #pop the elements until the deleted element
                eSet.add(s)
        elif(UPDATE_MODES.REMOVE == mode):
            absPos = -2-position if (position<0) else position
            oldEValue = filteredElems[absPos]
            sucessors = []
            sucessor = eSet.pop()
            while(sucessor != oldEValue):
                sucessors.append(sucessor)
                sucessor = eSet.pop()
            #re-add the successors
            sucessors.reverse()
            for s in sucessors: #pop the elements until the deleted element
                eSet.add(s)
        elif(UPDATE_MODES.INSERT == mode):
            #old value stays None
            elemToInsertBefore = filteredElems[absPos]
            sucessors = []
            sucessor = eSet.pop()
            while(sucessor != elemToInsertBefore):
                sucessors.append(sucessor)
                sucessor = eSet.pop()
            #add the new value
            eSet.add(eValue)
            eSet.add(elemToInsertBefore) #because this was popped before
            #re-add the successors
            sucessors.reverse()
            for s in sucessors: #pop the elements until the deleted element
                eSet.add(s)
        else: #should never go here
            raise EOQ_ERROR_INVALID_VALUE('Fatal: unknown update mode: %d'%(mode))
    return oldEValue

### EANNOTATION GETTER AND SETTER ###

def GetAllEAnnotations(eObj:EObject, source:str)->list:
    value = []
    if(IsEObjectAnnotationsPatchEnabled() or isinstance(eObj,EModelElement)):
        for a in eObj.eGet('eAnnotations'):
            if(source == a.source):
                value = [v for v in a.details.values()]
                break
    return value


def GetEAnnotation(eObj:EObject, source:str, key:str)->str:
    value = None
    if(IsEObjectAnnotationsPatchEnabled() or isinstance(eObj,EModelElement)):
        for a in eObj.eGet('eAnnotations'):
            if(source == a.source):
                if(key in a.details):
                    return a.details[key]
                break
    return value

def UpdateSingleValueEAnnotation(eObj:EObject, source:str, key:str, value:str, newEAnnotationCallback:callable=None)->str:
    oldValue = None
    if(IsEObjectAnnotationsPatchEnabled() or isinstance(eObj,EModelElement)):
        eAnnotation = None
        for a in eObj.eAnnotations:
            if(source == a.source):
                eAnnotation = a
                if(key in eAnnotation.details):
                    oldValue = eAnnotation.details[key]
                break
        if(not eAnnotation):
            eAnnotation = EAnnotation(source)
            eObj.eAnnotations.add(eAnnotation)
            if(None != newEAnnotationCallback):
                newEAnnotationCallback(eAnnotation)
        if(None == value):
            if(key in eAnnotation.details):
                del eAnnotation.details[key]
                #check if the eAnnotation is empty now and if yes, remove
                if(0==len(eAnnotation.details)):
                    eObj.eAnnotations.remove(eAnnotation)
                    eAnnotation.delete()
                    del eAnnotation
        else:
            eAnnotation.details[key] = value
    else:
        raise EOQ_ERROR_INVALID_VALUE('%s has not eAnnotations. Enable pyecore EAnnotationPatch.'%(eObj))
    return oldValue

def UpdateMultiValueEAnnotation(eObj:EObject, source:str, eValue:str, position:int, newEAnnotationCallback:callable=None)->str:
    oldValue = None
    #1. see if we find the annotation or need to create it
    if(IsEObjectAnnotationsPatchEnabled() or isinstance(eObj,EModelElement)):
        eAnnotation = None
        for a in eObj.eAnnotations:
            if(source == a.source):
                eAnnotation = a
                break
        if(not eAnnotation):
            eAnnotation = EAnnotation(source)
            eObj.eAnnotations.add(eAnnotation)
            if(None != newEAnnotationCallback):
                newEAnnotationCallback(eAnnotation)
        #2. determine the annotation positions
        values = [v for v in  eAnnotation.details.values()]
        nValues = len(values)
        # determine update mode
        (mode,absPos) = GetUpdateModeAndAbsPosition(nValues,position,eValue)
        # position sanity checks
        ValidateUpdatePosition(mode,nValues,-1,absPos)
        #3. carry out the update
        if(nValues == absPos): #can not happen for delete
            #old value stays None
            values.append(eValue)
        else: #it is not the last element that is added
            if(UPDATE_MODES.REPLACE == mode):
                oldValue = values[absPos]
                values[absPos] = eValue
            elif(UPDATE_MODES.REMOVE == mode):
                oldValue = values.pop(absPos)
            elif(UPDATE_MODES.INSERT == mode):
                #old value stays None
                values.insert(absPos, eValue)
            else: #should never go here
                raise EOQ_ERROR_INVALID_VALUE('Fatal: unknown update mode: %d'%(mode))
        #5. rebuild annotation dict
        eAnnotation.details.clear() #clear the annotation keys
        for i in range(len(values)): # rebuild the dict
            key = '%d'%i
            eAnnotation.details[key] = values[i]
        #6. check if eAnnotation is still needed or can be removed
        if(0==len(eAnnotation.details)):
            eObj.eAnnotations.remove(eAnnotation)
            eAnnotation.delete()
            del eAnnotation
    else:
        raise EOQ_ERROR_INVALID_VALUE('%s has not eAnnotations. Enable pyecore EAnnotationPatch.'%(eObj))
    return oldValue
