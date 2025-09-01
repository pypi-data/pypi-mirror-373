"""
 Bjoern Annighoefer 2024
"""

from eoq3.value import VAL, BOL, U32, U64, I64, STR, NON, QRY, LST, InitValOrNon
from eoq3.query import His, IsObj, IsHis, Obj
from eoq3.command import Cmd, CMD_TYPES, Crt, Upd
from eoq3.concepts import CONCEPTS, MXELEMENT, M2CLASS, M2MODEL, M2ATTRIBUTE,\
                          M2ASSOCIATION, M2COMPOSITION, M2ENUM, M2OPTIONOFENUM, M2PRIMITIVES, IsNameFeature
from eoq3.error import EOQ_ERROR_RUNTIME, EOQ_ERROR_INVALID_TYPE
from eoq3.config import Config, EOQ_DEFAULT_CONFIG
from eoq3.logger import GetLoggerInstance
from eoq3.util.eoqfile import CmdStream, SimpleResNameGen

from .ecoreutils import ResolveEProxy, GetEAnnotation
from .ecoreconversionoptions import EcoreConversionOptions, DEFAULT_ECORE_CONVERSION_OPTIONS
from .genericstopyecore import IsEPrimitiveType, EAttributeTypeConceptPrimitiveId, EANNOTATION_SOURCES, EANNOTATION_KEYS
from .valuetopyecore import EValueToValue
from .crudforpyecore import UpdateSingleValueEAnnotation, UpdateMultiValueEAnnotation
from .genericstopyecore import EANNOTATION_SOURCES, EANNOTATION_KEYS, GenericPrimitiveTypeToEPrimitiveType
from .pyecorepatch import IsEObjectAnnotationsPatchEnabled

from pyecore.ecore import EObject, EPackage, EClass, EAttribute, EReference, EEnum, EEnumLiteral, EProxy
from pyecore.resources import ResourceSet 

from typing import Dict, List, Tuple, Any, Hashable, Iterable


### AUXILARY CLASSES ###

class EObj(Obj):
    """Overwrite the native Obj, to store a reference on the EObject, 
    which can for instance be used for name generation.
    This is used when reading from an ecore resources. 
    """
    def __init__(self, eObj:EObject):
        """ The constructor takes the res name as object ID
        """
        super().__init__(I64(hash(eObj)))
        self._eObj = eObj
        
class EMxArtificialObject(EObject):
    """We need a mockup for all non-existing classes, but here only the name is relevant
    """
    def __init__(self, name:str):
        super().__init__()
        self.name = name
        
class EM1Model(EMxArtificialObject):
    """This does not exist in ecore. 
    This is an augmented class
    """
    def __init__(self, name:str):
        super().__init__(name)
        
class FromEObjectResNameGen(SimpleResNameGen):
    """Tries to generate readable names for resNames
    based on the concept type
    """
    def __init__(self, prefix:str="o", segmentSeperator="_"):
        super().__init__(prefix)
        #internals
        self.usedNames:Dict[str,bool] = {}
        
    #@Override
    def GenResName(self, res:VAL)->str:
        resName = None
        if(isinstance(res,EObj)):
            eObj = res._eObj
            name = None
            prefix = "OBJ"
            if(isinstance(eObj,EPackage)):
                name = eObj.name
                prefix = "PCK"
            elif(isinstance(eObj,EEnum)):
                name = eObj.name
            else:
                name = super().GenResName(res)
            resNameRaw = self.segmentSeperator.join([prefix.lower(),name if name else ""])
            resName = resNameRaw
            suffix = 1
            while(resName in self.usedNames):
                suffix += 1
                resName = "%s%d"%(resNameRaw,suffix) #append count to make name unique
            self.usedNames[resName] = True
            self.objNameLut[res] = resName
        else:
            raise EOQ_ERROR_INVALID_TYPE("Can only generate resNames from res of type EObj.")
        return resName
    

### CMDSTREAMS ###


class EObjectInStream(CmdStream):
    def __init__(self, options:EcoreConversionOptions=DEFAULT_ECORE_CONVERSION_OPTIONS, config:Config=EOQ_DEFAULT_CONFIG):
        super().__init__()
        self.options = options
        self.config = config
        #internals
        self.logger = GetLoggerInstance(config)
        self.objLut:Dict[EObject,QRY] = None
        self.objCount:int = 0
        self.importedEObjects:List[EObject] = None
        self.m1Model:EObj = None #cache the m1 model to ensure that multiple objects are saved in the same m1 model
        
    def Begin(self):
        super().Begin()
        self.objLut = {}
        self.objCount = 0
        self.importedEObjects = []
        self.m1Model = None
        
    def GetImportedEObjects(self)->List[EObject]:
        return self.importedEObjects
        
    def LoadEObjects(self, eRoots:Iterable[EObject], m1ModelName:str="M1Model")->None:
        """ Generic function that decides based on the nature of the 
        provided EObject what to do. 
        For instance EPackages as well as user model EObjects can be provided.
        In case of user model objects a name for the m1Model concept 
        must be provided, since this does not exist in ecore.
        The full set of elements will be imported. 
        If  dependencies between eEbjects exist, they must be provided in one eRoots list.
        Otherwise resolving will fail.
        """
        #sort in packages (m2 model) and other eObjects (m1 model)
        ePackages = []
        eObjs = []
        for e in eRoots:
            if(isinstance(e,EPackage)):
                ePackages.append(e)
            else: #regular model
                eObjs.append(e)
        #start the actual import
        self.LoadEPackages(ePackages)
        self.LoadUserModelEObjects(eObjs, m1ModelName)
            
    def LoadEPackages(self, ePackages:List[EPackage])->None:
        for p in ePackages: #load structure of all packages first to be able to resolve dependencies
            self.LoadEPackageStructureOnly(p, None)
        for p in ePackages:
            self.LoadEPackageReferencesOnly(p)
        
    def LoadUserModelEObjects(self, eObjs:List[EObject], m1ModelName:str="M1Model")->None:
        for o in eObjs: #load structure of all objects first to be able to resolve dependencies
            self.LoadUserModelEObjectStructureOnly(o, m1ModelName)
            m1ModelName = None #chases that only one m1 model is created in the first loop
        for o in eObjs:
            self.LoadUserModelEObjectReferencesOnly(o)
    
    def LoadEPackageStructureOnly(self, ePackage:EPackage, parentPack:EObj)->None:
        package = EObj(ePackage)
        if(None == parentPack):
            self.PushCmd(Crt(CONCEPTS.M2MODEL,U32(1),LST([STR(ePackage.name)])),package)
        else:
            self.PushCmd(Crt(CONCEPTS.M2PACKAGE,U32(1),LST([STR(ePackage.name),parentPack])),package)
        self.__ArtificialEObjectFeaturesToCmd(ePackage, package)
        #first import enum
        for c in ePackage.eClassifiers:
            if(self.options.includeEnums and EEnum == type(c)):
                enum = EObj(c)
                self.PushCmd(Crt(CONCEPTS.M2ENUM,U32(1),LST([STR(c.name),package])),enum)
                self.__ArtificialEObjectFeaturesToCmd(c,enum)
                for l in c.eLiterals:
                    option = EObj(l)
                    self.PushCmd(Crt(CONCEPTS.M2OPTIONOFENUM,U32(1),LST([STR(l.name),U64(l.value),enum])),option)
                    self.__ArtificialEObjectFeaturesToCmd(l, option)
                    self.objLut[l] = option
                    self.importedEObjects.append(l)
                self.objLut[c] = enum
                self.importedEObjects.append(c)
        #second import classes
        for c in ePackage.eClassifiers:
            if(EClass == type(c)):
                clazz = EObj(c)
                self.PushCmd(Crt(CONCEPTS.M2CLASS,U32(1),LST([STR(c.name),BOL(c.abstract),package])),clazz)
                self.__ArtificialEObjectFeaturesToCmd(c,clazz)
                self.objLut[c] = clazz
                self.importedEObjects.append(c)
        if(self.options.includeSubpackes):
            for p in ePackage.eSubpackages: #recursively import any subpackages
                self.LoadEPackageStructureOnly(p,package)
        self.objLut[ePackage] = package
        self.importedEObjects.append(ePackage)
            
    def LoadEPackageReferencesOnly(self, ePackage:EPackage)->None:
        for c in ePackage.eClassifiers:
            if(EClass == type(c)):
                clazz = self.objLut[c]
                #fist import all attributes
                for f in c.eStructuralFeatures:
                    feature = EObj(f)
                    eType = ResolveEProxy(f.eType,False,self.__OnProxyResolveFailed)
                    if(EAttribute == type(f)):
                        attrName = f.name
                        attrType = None
                        if(IsNameFeature(attrName)):
                            self.logger.Warn('Skipped: %s.%s because it custom name features are not supported.'%(c.name,f.name))
                            continue
                        enum = NON()
                        try:
                            attrType = EAttributeTypeConceptPrimitiveId(eType)
                        except:
                            self.logger.Warn('Skipped: %s.%s because type %s is not supported or disabled'%(c.name,f.name,eType))
                            continue
                        if(M2PRIMITIVES.ENU == attrType):
                            enum = self.objLut[eType]
                        attrMul = f.upperBound  
                        attrUnit = InitValOrNon(GetEAnnotation(f, EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.UNIT, None),STR)
                        #create the attribute
                        self.PushCmd(Crt(CONCEPTS.M2ATTRIBUTE,U32(1),LST([STR(attrName),clazz,STR(attrType),I64(attrMul),attrUnit,enum])),feature)
                        self.__ArtificialEObjectFeaturesToCmd(f, feature)
                        self.__ArtificialEAttributeFeaturesToCmd(f, feature)
                        self.objLut[f] = feature
                        self.importedEObjects.append(f)
                #second import all associations
                for f in c.eStructuralFeatures:
                    feature = EObj(f)
                    eType = ResolveEProxy(f.eType,False,self.__OnProxyResolveFailed)
                    if((EReference == type(f)) and not f.containment):
                        if(self.__IsPrimaryEReference(f)):
                            dstName = f.name
                            srcMul = -1
                            srcName = dstName + self.options.autoOpositePrefix + f.eContainer().name
                            if(None != f.eOpposite):
                                srcName = f.eOpposite.name
                                srcMul = f.eOpposite.upperBound
                            srcClass = clazz
                            dstClass = None
                            anyDst = False
                            if(EObject.eClass==eType): #eClass seems necessary, since EObject is a build in class
                                anyDst = True
                            elif(isinstance(eType,EClass)):
                                dstClass = self.objLut[eType]
                            elif(None==eType):
                                self.logger.Warn('Skipped: %s.%s because type is not set.'%(c.name,f.name))
                                continue
                            else:
                                self.logger.Warn('Skipped: %s.%s because type %s is not supported.'%(c.name,f.name,eType))
                                continue
                            dstMul = f.upperBound
                            self.PushCmd(Crt(CONCEPTS.M2ASSOCIATION,U32(1),LST([STR(srcName),srcClass,I64(srcMul),STR(dstName),dstClass,I64(dstMul),BOL(anyDst)])),feature)
                            self.__ArtificialEObjectFeaturesToCmd(f, feature)
                            self.objLut[f] = feature
                            self.importedEObjects.append(f)
                        else:
                            pass #this is the opposite of a reference that is imported anyway
                #last import compositions
                for f in c.eStructuralFeatures:
                    feature = EObj(f)
                    eType = ResolveEProxy(f.eType,False,self.__OnProxyResolveFailed)
                    if((EReference == type(f)) and f.containment):
                        srcName = f.name
                        srcClass = clazz
                        dstClass = None
                        anyChild = False
                        if(EObject.eClass==eType):
                            anyChild = True
                        elif(isinstance(eType,EClass)):
                            try: 
                                dstClass = self.objLut[eType]
                            except KeyError:
                                self.logger.Warn('Skipped %s.%s because type cannot be resolved. Are subpackages disabled?'%(c.name,f.name))
                                continue
                        elif(None==eType):
                            self.logger.Warn('Skipped %s.%s because type is not set.'%(c.name,f.name))
                            continue
                        else:
                            self.logger.Warn('Skipped %s.%s because type %s is not supported.'%(c.name,f.name,eType))
                            continue
                        dstMul = f.upperBound
                        self.PushCmd(Crt(CONCEPTS.M2COMPOSITION,U32(1),LST([STR(srcName),srcClass,dstClass,I64(dstMul),BOL(anyChild)])),feature)
                        self.__ArtificialEObjectFeaturesToCmd(f, feature)
                        self.objLut[f] = feature
                        self.importedEObjects.append(f)
                #now inheritances
                for s in c.eSuperTypes:
                    subClass = clazz
                    try:
                        superClass = self.objLut[s]
                    except KeyError:
                        self.logger.Warn('Skipped %s -[inherits]-> %s because %s can not be resolved. Are subpackages disabled?'%(c.name,s.name,s.name))
                        continue
                    self.PushCmd(Crt(CONCEPTS.M2INHERITANCE,U32(1),LST([subClass,superClass])))
                    self.importedEObjects.append(s)
        if(self.options.includeSubpackes):
            for p in ePackage.eSubpackages: #recursively import any subpackages
                self.LoadEPackageReferencesOnly(p)
    
    def LoadUserModelEObjectStructureOnly(self, eObj:EObject, name:str)->None:
        m2ModelStrId = self.__EPackackeToStrId(eObj.eClass.ePackage)
        if(None != name):
            self.m1Model = EObj(EM1Model(name))
            name = STR(self.__EcoreValuePreprocessing(name,self.options))
            self.PushCmd(Crt(STR(CONCEPTS.M1MODEL),U32(1),LST([STR(m2ModelStrId),STR(name)])),self.m1Model)
        self.__EObjectStructureToCmd(eObj)
        
    def LoadUserModelEObjectReferencesOnly(self, eObj:EObject)->None:
        """ imports all non-containment references. 
        Should be done after the object tree was imported
        """
        eClass = eObj.eClass
        obj = None
        try:
            obj = self.objLut[eObj]
        except KeyError:
            self.logger.Warn("Skipped: Unknown object %s."%(str(eObj)))   
            return
        for f in eClass.eAllStructuralFeatures():
            if(EReference == type(f) and not f.containment):
                if(self.__IsPrimaryEReference(f)):
                    eValue = eObj.eGet(f)
                    feature = f.name
                    if(f.many):
                        i = 0
                        for v in eValue:
                            eValueResolved = ResolveEProxy(v,False,self.__OnProxyResolveFailed)
                            dst = self.objLut[eValueResolved]
                            try:
                                self.PushCmd(Crt(STR(CONCEPTS.M1ASSOCIATION),1,[feature,obj,dst]))
                            except KeyError:
                                self.logger.Warn("Skipped: Found unresolvable proxy in <%s>.%s:%d."%(eClass.name,f.name,i))
                            i+=1
                    elif(not f.many and None != eValue):
                        eValueResolved = ResolveEProxy(eValue,False,self.__OnProxyResolveFailed)
                        dst = self.objLut[eValueResolved]
                        try:
                            self.PushCmd(Crt(STR(CONCEPTS.M1ASSOCIATION),1,[feature,obj,dst]))
                        except KeyError:
                            self.logger.Warn("Skipped: Found unresolvable proxy in <%s>.%s."%(eClass.name,f.name))
                    else:
                        pass #if object is none, do nothing
                else:
                    pass #this is the opposite of a reference that is imported anyway
            elif(EReference == type(f) and f.containment):
                eValue = eObj.eGet(f)
                if(f.many):
                    for v in eValue:
                        self.LoadUserModelEObjectReferencesOnly(v) 
                elif(not f.many and None != eValue):
                    self.LoadUserModelEObjectReferencesOnly(eValue)
                    
    ### INTERNALS ###
    
    def __IsPrimaryEReference(self, f:EReference)->bool:
        """Opposite references appear twice in Ecore, but only once in concepts.
        This function determines on of the opposite reference as the primary one.
        For the primary reference, True is returned.
        If the reference is has no opposite reference, True is returned.
        Which references is the primary is deterministic, independent of f.
        """
        if(f.eOpposite):
            #if it is a containment, the reference is primary
            if(f.containment):
                return True
            #if the opposite is a containment, the opposite is primary
            elif(f.eOpposite.containment):
                return False
            #else determine the primary reference base on the higher upper bound
            elif(f.upperBound != f.eOpposite.upperBound):
                if(f.upperBound <0):
                    return True
                elif(f.eOpposite.upperBound <0):
                    return False
                else:
                    return f.upperBound > f.eOpposite.upperBound
            #if upper bounds are equal, determine based on the name
            elif(f.name != f.eOpposite.name):
                return f.name < f.eOpposite.name
            #if names are equal, determine based on the hash
            else:
                return hash(f) < hash(f.eOpposite)
        else:
            return True
    
    def __EPackackeToStrId(self, ePack:EPackage)->str:
        """ Retrieves a string ID for a package (including the superpackage path
        """
        allPackage = []
        currentPackage = ePack
        while(None != currentPackage):
            allPackage.append(currentPackage)
            currentPackage = currentPackage.eSuperPackage
        return self.options.idSeperator.join([p.eGet(self.options.packageIdFeature) for p in reversed(allPackage)])
        
    def __EObjectStructureToCmd(self, eObj:EObject)->None:
        eClass = eObj.eClass
        classStrId = self.__EPackackeToStrId(eClass.ePackage) + self.options.idSeperator + eClass.name
        obj = EObj(eObj)
        name = NON()
        try:
            name = STR(self.__EcoreValuePreprocessing(eObj.name,self.options))
        except:
            pass #no name given
        self.PushCmd(Crt(STR(CONCEPTS.M1OBJECT),U32(1),LST([STR(classStrId),self.m1Model,name])),obj)
        for f in eClass.eAllStructuralFeatures():
            eType = ResolveEProxy(f.eType,False,self.__OnProxyResolveFailed)
            featureName = f.name
            if(IsNameFeature(featureName)):
                continue #name is already in the M1OBJECT create args
            if EAttribute == type(f):
                if(IsEPrimitiveType(eType) or isinstance(eType,EEnum)):
                    eValue = eObj.eGet(f)
                    if(f.many):
                        for v in eValue:
                            if(EEnumLiteral == type(v)):
                                v = self.__EcoreValuePreprocessing(v.name,self.options) #literals shall not be stored as literals
                            else:
                                v = EValueToValue(self.__EcoreValuePreprocessing(v,self.options),eType)
                            self.PushCmd(Crt(STR(CONCEPTS.M1ATTRIBUTE),[STR(featureName),obj,v]))
                    elif(None!=eValue):
                        if(self.options.skipEmptyStrings and str == type(eValue) and 0 == len(eValue)):
                            continue
                        elif(EEnumLiteral == type(eValue)):
                            eValue = self.__EcoreValuePreprocessing(eValue.name,self.options) #literals shall not be stored as literals 
                        else:
                            eValue = EValueToValue(self.__EcoreValuePreprocessing(eValue,self.options),eType)
                        self.PushCmd(Crt(STR(CONCEPTS.M1ATTRIBUTE),1,[STR(featureName),obj,eValue]))
                else:
                    self.logger.Warn('Skipped %s.%s because type %s is not supported.'%(eObj,f.name,eType.name))
            elif(EReference == type(f) and f.containment):
                eValue = eObj.eGet(f)
                if(f.many):
                    for v in eValue:
                        self.__EObjectStructureToCmd(v) 
                        dstObj = self.objLut[self.importedEObjects[-1]]
                        self.PushCmd(Crt(STR(CONCEPTS.M1COMPOSITION),1,[STR(featureName),obj,dstObj]))
                elif(not f.many and None != eValue):
                    self.__EObjectStructureToCmd(eValue)
                    dstObj = self.objLut[self.importedEObjects[-1]]
                    self.PushCmd(Crt(STR(CONCEPTS.M1COMPOSITION),1,[STR(featureName),obj,dstObj]))
                else: #if object is none, do nothing
                    pass
        # import artificial features for objects if possible
        if(IsEObjectAnnotationsPatchEnabled()):
            self.__ArtificialEObjectFeaturesToCmd(eObj, obj)
        self.objLut[eObj] = obj
        self.importedEObjects.append(eObj)
    
    def __OnProxyResolveFailed(self, p:EProxy, e:Exception):
        self.logger.Warn("Unresolvable proxy found and removed: %s"%(e))
                
    ### EANNOTATION HANDLING
    
    def __ArtificialEObjectFeaturesToCmd(self, eObj:EObject, objRef:EObj):
        """ Import the features which are not real features in pyecore
        """
        if(self.options.includeDocumentation):
            self.__EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.DOCUMENTATION, EANNOTATION_SOURCES.DOCUMENTATION, EANNOTATION_KEYS.DOCUMENTATION)
        if(self.options.includeConstraints):
            self.__EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.CONSTRAINTS  , EANNOTATION_SOURCES.CONSTRAINTS  , None  ) 
        if(self.options.includePermissions):
            self.__EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.OWNER        , EANNOTATION_SOURCES.OWNER        , EANNOTATION_KEYS.OWNER        ) 
            self.__EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.GROUP        , EANNOTATION_SOURCES.GROUP        , EANNOTATION_KEYS.GROUP        ) 
            self.__EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.PERMISSIONS  , EANNOTATION_SOURCES.PERMISSIONS  , None                          )  
        
    def __ArtificialEAttributeFeaturesToCmd(self, eObj:EObject, objRef:str):
        """ Import the features which are not real features in pyecore
        """
        self.__EAnnotationToFeatureCmd(eObj, objRef, M2ATTRIBUTE.UNIT, EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.UNIT)
            
    def __EAnnotationToFeatureCmd(self, eObj:EObject, objRef:EObj, featureName:str, source:str, key:str)->None:
        for a in eObj.eAnnotations:
            if(source == a.source):
                if(None==key): #import all 
                    for v in a.details.values():
                        self.PushCmd(Upd(objRef,STR(featureName),STR(self.__EcoreValuePreprocessing(v,self.options)),I64(-1),mute=self.options.muteUpdate))
                else:
                    if(key in a.details):
                        text = a.details[key]
                        self.PushCmd(Upd(objRef,STR(featureName),STR(self.__EcoreValuePreprocessing(text,self.options)),mute=self.options.muteUpdate))
                break #break anyhow, there wont be a second identical source

    def __EcoreValuePreprocessing(self, value:Any, options:EcoreConversionOptions):
        result = value #by default the input is the output
        if(str == type(value)):
            if(self.options.translateChars):
                for r in self.options.translateTable:
                    result = result.replace(r[0],r[1])
            if(0 < self.options.maxStrLen and self.options.maxStrLen < len(result)):
                truncLen = len(self.options.maxStrTruncationSymbol)
                strLenLeft = max(0,self.options.maxStrLen-truncLen)
                trunLenLeft = min(truncLen,self.options.maxStrLen)#in case maxStrLen is smaller as the truncation symbol
                result = result[:strLenLeft] + self.options.maxStrTruncationSymbol[:trunLenLeft] #truncate and add truncation indication
        return result
    
    

class EObjectOutStream(CmdStream):
    """Cmd stream that converts a series of commands in a pyecore data structure.
    For instance, 
    The cmd stream given must be a His-based and dependency-ordered stream.
    """
    def __init__(self, rset:ResourceSet, options:EcoreConversionOptions=DEFAULT_ECORE_CONVERSION_OPTIONS):
        """
        rset is necessary to get access to the metamodel registry and resolve names
        """
        super().__init__()
        self.rset = rset
        self.options = options
        #internals
        self.eObjLUT:Dict[Hashable,EObject] = None #reverse lookup for EObjects already created
        self.orphans:List[EObject] = None
        
    def Begin(self):
        self.eObjLUT = {} #reverse lookup for EObjects already created
        self.orphans = []
        
    def GetOrphans(self)->List[EObject]:
        return self.orphans
    
    #@Override
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        """Depends on the fact that there are no unresolved dependencies in the stream
        """
        cmdType = cmd.cmd
        if(CMD_TYPES.CRT == cmdType):
            concept = cmd.a[0]
            createArgs = cmd.a[2]
            if(CONCEPTS.M2MODEL==concept):
                eName = createArgs[0].GetVal()
                eNsUri = eName.lower() #no nsURI in concepts so use the name
                eNsPrefix = eName.lower() #no prefix, so use name
                newEObj = EPackage(eName,eNsUri,eNsPrefix)
                self.__RememberEObj(newEObj,res,cmd.r)
                self.orphans.append(newEObj) #special case, M2 models always are new root objects
            elif(CONCEPTS.M2PACKAGE==concept):
                eName = createArgs[0].GetVal()
                eSuperPackage = self.__ResolveEObj(createArgs[1])
                eNsUri = self.__GenEpackageHirarchyName(eName,eSuperPackage,self.options.idSeperator)
                eNsPrefix = self.__GenEpackageHirarchyName(eName,eSuperPackage,self.options.prefixSeperator)
                newEObj = EPackage(eName,eNsUri,eNsPrefix)
                eSuperPackage.eSubpackages.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2ENUM==concept):
                eName = createArgs[0].GetVal()
                ePackage = self.__ResolveEObj(createArgs[1])
                newEObj = EEnum(eName)
                ePackage.eClassifiers.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2OPTIONOFENUM==concept):
                eName = createArgs[0].GetVal()
                eValue = createArgs[1].GetVal()
                eEnum = self.__ResolveEObj(createArgs[2])
                newEObj = EEnumLiteral(eName)
                newEObj.value = eValue
                eEnum.eLiterals.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2CLASS==concept):
                eName = createArgs[0].GetVal()
                eIsAbstract = createArgs[1].GetVal()
                ePackage = self.__ResolveEObj(createArgs[2])
                newEObj = EClass(eName, abstract=eIsAbstract)
                ePackage.eClassifiers.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2ATTRIBUTE==concept):
                eName = createArgs[0].GetVal()
                eClass = self.__ResolveEObj(createArgs[1])
                primType = createArgs[2].GetVal()
                eUpper = createArgs[3].GetVal()
                eUnit = createArgs[4].GetVal()
                eLower = 0
                eType = None
                if(M2PRIMITIVES.ENU == primType):
                    eType = self.__ResolveEObj(createArgs[5])
                else:
                    eType = GenericPrimitiveTypeToEPrimitiveType(primType)
                newEObj = EAttribute(eName, eType=eType, lower=eLower, upper=eUpper)
                if(eUnit):
                    UpdateSingleValueEAnnotation(newEObj, EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.DOCUMENTATION, eUnit)
                eClass.eStructuralFeatures.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2ASSOCIATION==concept):
                eSrcName = createArgs[0].GetVal()
                eSrcClass = self.__ResolveEObj(createArgs[1])
                eSrcUpper = createArgs[2].GetVal()
                eDstName = createArgs[3].GetVal()
                eDstClass = self.__ResolveEObj(createArgs[4])
                eDstUpper = createArgs[5].GetVal()
                eIsAny = createArgs[6].GetVal()
                eLower = 0
                eType = None
                if(eIsAny):
                    eType = EObject.eClass
                else:
                    eType = eDstClass
                newEObj = EReference(eDstName, eType=eType, containment=False, lower=eLower, upper=eDstUpper)
                if(not eIsAny and self.options.autoOpositePrefix not in eSrcName):
                    #generate an opposite only if it was not automatically created.
                    eOpposite = EReference(eSrcName, eType=eSrcClass, containment=False, lower=eLower, upper=eSrcUpper, eOpposite=newEObj)
                    eDstClass.eStructuralFeatures.add(eOpposite)
                    #newEObj.eOpposite = eOpposite
                eSrcClass.eStructuralFeatures.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2COMPOSITION==concept):
                eName = createArgs[0].GetVal()
                eParentClass = self.__ResolveEObj(createArgs[1])
                eChildClass = self.__ResolveEObj(createArgs[2])
                eUpper = createArgs[3].GetVal()
                eIsAny = createArgs[4].GetVal()
                eLower = 0
                eType = None
                if(eIsAny):
                    eType = EObject.eClass
                else:
                    eType = eChildClass
                newEObj = EReference(eName, eType=eChildClass, containment=True, lower=eLower, upper=eUpper)
                eParentClass.eStructuralFeatures.add(newEObj)
                self.__RememberEObj(newEObj,res,cmd.r)
            elif(CONCEPTS.M2INHERITANCE==concept):
                eSubClass = self.__ResolveEObj(createArgs[0])
                eSuperClass = self.__ResolveEObj(createArgs[1])
                eSubClass.eSuperTypes.add(eSuperClass)
            elif(CONCEPTS.M1MODEL==concept):
                pass #skip M1 models. Does not exist in ecore
            elif(CONCEPTS.M1OBJECT==concept):
                eClass = self.__ResolveEClass(createArgs[0])
                eName = createArgs[2].GetVal()
                newEObj = eClass()
                self.__RememberEObj(newEObj,res,cmd.r)
                self.orphans.append(newEObj) #M1 objects are always first orphans and removed if child in a composition
            elif(CONCEPTS.M1ATTRIBUTE==concept):
                eObject = self.__ResolveEObj(createArgs[1])
                eFeature = self.__ResolveEFeature(createArgs[0], eObject)
                eValue = createArgs[2].GetVal()
                if(eFeature.many):
                    eObject.eGet(eFeature).add(eValue)
                else:
                    eObject.eSet(eFeature,eValue)
            elif(CONCEPTS.M1ASSOCIATION==concept):
                eObject = self.__ResolveEObj(createArgs[1])
                eFeature = self.__ResolveEFeature(createArgs[0], eObject)
                eValue = self.__ResolveEObj(createArgs[2])
                if(eFeature.many):
                    eObject.eGet(eFeature).add(eValue)
                else:
                    eObject.eSet(eFeature,eValue)
            elif(CONCEPTS.M1COMPOSITION==concept):
                eObject = self.__ResolveEObj(createArgs[1])
                eFeature = self.__ResolveEFeature(createArgs[0], eObject)
                eValue = self.__ResolveEObj(createArgs[2])
                if(eFeature.many):
                    eObject.eGet(eFeature).add(eValue)
                else:
                    eObject.eSet(eFeature,eValue)
                if(eValue in self.orphans):
                    self.orphans.remove(eValue)
            elif(CONCEPTS.MXCONSTRAINT==concept):
                pass #TODO
            else:
                raise EOQ_ERROR_RUNTIME("CRT invalid concept: %s"%(concept))
        elif(CMD_TYPES.UPD == cmdType):
            eTarget = self.__ResolveEObj(cmd.a[0])
            eFeatureName = cmd.a[1].GetVal()
            eValue = cmd.a[2].GetVal()
            if(MXELEMENT.DOCUMENTATION==eFeatureName):
                UpdateSingleValueEAnnotation(eTarget, EANNOTATION_SOURCES.DOCUMENTATION, EANNOTATION_KEYS.DOCUMENTATION, eValue)
            elif(MXELEMENT.OWNER==eFeatureName):
                UpdateSingleValueEAnnotation(eTarget, EANNOTATION_SOURCES.OWNER, EANNOTATION_KEYS.OWNER, eValue)
            else:
                raise EOQ_ERROR_RUNTIME("UPD unsupported feature: %s"%(eFeatureName))
        else:
            raise EOQ_ERROR_RUNTIME("Invalid cmd type: %s"%(cmdType))
        return (cmd,res)
    
    ### INTERNALS ###
    
    def __GenEpackageHirarchyName(self, eName:str, eParent:EPackage, seperator:str)->str:
        segments = [eName.lower()]
        while(eParent):
            segments.append(eParent.name.lower())
            eParent = eParent.eSuperPackage
        segments.reverse()
        return seperator.join(segments)
    
    
    def __RememberEObj(self, eObj:EObject, res:VAL, resName:str):
        if(None!=resName):
            self.eObjLUT[His(STR(resName))] = eObj
        if(IsObj(res)):
            self.eObjLUT[res] = eObj

    def __ResolveEObj(self, ref:Hashable)->EObject:
        if(isinstance(ref,VAL) and ref.IsNone()):
            return None
        elif(ref in self.eObjLUT):
            return self.eObjLUT[ref]
        #only goes here if his element is unknown.
        raise EOQ_ERROR_RUNTIME("Cannot resolve: %s"%(str(ref)))
    
    def __ResolveEClass(self, clazz:Any)->EObject:
        if(IsHis(clazz)):
            return self.__ResolveEObj(clazz)
        elif(isinstance(clazz,STR)):
            clazzId = clazz.GetVal()
            segments = clazzId.split(self.options.idSeperator)
            ePackage = None
            for s in segments[:-1]:
                packageFound = False
                for p in self.rset.metamodel_registry.values():
                    if(s == p.name):
                        ePackage = p
                        packageFound = True
                        break;
                if(not packageFound):
                    raise EOQ_ERROR_RUNTIME("Unknown package: %s"%(s))
            eClassName = segments[-1] #the last element is the class name
            classFound = False
            eClass = None
            for c in [e for e in ePackage.eClassifiers if isinstance(e, EClass.eClass)]:
                if(eClassName==c.name):
                    eClass = c
                    classFound = True
                    break
            if(not classFound):
                raise EOQ_ERROR_RUNTIME("Unknown class: %s"%(eClassName))
            return eClass    
        else: 
            raise EOQ_ERROR_RUNTIME("EClass cannot resolve: %s"%(str(clazz)))
        
    def __ResolveEFeature(self, feature:Any, eObj:EObject)->EObject:
        if(IsHis(feature)):
            return self.__ResolveEObj(feature)
        elif(isinstance(feature,STR)):
            eFeatureName = feature.GetVal()
            eClass = eObj.eClass
            featureFound = False
            eFeature = None
            for f in eClass.eAllStructuralFeatures():
                if(eFeatureName==f.name):
                    eFeature = f
                    featureFound = True
                    break
            if(not featureFound):
                raise EOQ_ERROR_RUNTIME("Unknown feature: %s"%(eFeatureName))
            return eFeature    
        else: 
            raise EOQ_ERROR_RUNTIME("EFeature cannot resolve: %s"%(str(feature)))
            

