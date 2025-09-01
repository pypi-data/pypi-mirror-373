'''
2022 Bjoern Annighoefer
'''

from eoq3.concepts import CONCEPTS, MXELEMENT, M2CLASS, M2MODEL, M2ATTRIBUTE, \
    M2ASSOCIATION, M2COMPOSITION, M2ENUM, M2OPTIONOFENUM, M2PRIMITIVES, M1OBJECT, IsNameFeature
from eoq3.value import U32, U64, I64, STR, NON
from eoq3.command import Cmp
from eoq3.query import Obj, His, Cls
from eoq3.logger import Logger, ConsoleLogger, NoLogger
from eoq3.serializer import Serializer, TextSerializer
from eoq3.config import EOQ_DEFAULT_CONFIG
from eoq3.util.eoqfile import EoqFileOutStream

from pyecore.ecore import EObject, MetaEClass, EClass, EPackage, EAttribute, EReference, EEnum, EEnumLiteral, EProxy, EString
from pyecore.resources import ResourceSet 

from .genericstopyecore import IsEPrimitiveType, EPrimitiveTypeToGenericPrimitiveType, EAttributeTypeConceptPrimitiveId, EANNOTATION_SOURCES, EANNOTATION_KEYS
from .valuetopyecore import EValueToValue
from .pyecorepatch import IsEObjectAnnotationsPatchEnabled

import types #required for ModuleType
import os #required for file path split

from typing import Any


def ResolveEProxy(proxy:EObject, logger:Logger=NoLogger())->EObject:
    obj = proxy
    if(isinstance(proxy, EProxy)):
        try: 
            #resolve can fail if files have been modified or objects been deleted 
            # before the proxy has been resolved
            proxy.force_resolve()
            obj = proxy._wrapped #remove the outer proxy
        except Exception as e:
            logger.Warn("Unresolvable proxy found and removed: %s"%(e))
            obj = None
    if(isinstance(proxy, (MetaEClass,type,types.ModuleType))): 
        #this is necessary to mask compiled model instances
        obj = proxy.eClass
    return obj    


def NextObjectId(objCount:int)->str:
    objId = "o%d"%(objCount)
    objCount += 1
    return (objId,objCount)


### META-MODEL TO COMMAND CONVERSION ###


class EcoreConversionOptions:
    def __init__(self, includeSubpackages:bool=True, includeEnums:bool=True, includeDocumentation:bool=True, includeConstratins:bool=False, includePermissions:bool=False, muteUpdate=False):
        self.includeSubpackes = includeSubpackages
        self.includeEnums = includeEnums
        self.includeDocumentation = includeDocumentation
        self.includeConstraints = includeConstratins
        self.includePermissions = includePermissions
        self.muteUpdate = muteUpdate #mute UPD calls because they are not necessary
        self.autoOpositePrefix = '_opp_'
        self.maxStrLen = -1 #The number of characters in a string. -1 = unconstrained
        self.maxStrTruncationSymbol = '...' #added at the and of the string to indicate truncation
        self.translateChars = False #indicates whether some characters shall be replaced using translateTable
        self.translateTable = [] # a list of tuples of characters replaced during conversion
        self.packageIdFeature = 'nsURI' #by default it is the package namespace uri, can also be the name
        self.idSeperator = EOQ_DEFAULT_CONFIG.strIdSeparator
        self.skipEmptyStrings = True


def _EcoreValuePreprocessing(value:Any, options: EcoreConversionOptions):
    result = value #by default the input is the output
    if(str == type(value)):
        if(options.translateChars):
            for r in options.translateTable:
                result = result.replace(r[0],r[1])
        if(0 < options.maxStrLen and options.maxStrLen < len(result)):
            truncLen = len(options.maxStrTruncationSymbol)
            strLenLeft = max(0,options.maxStrLen-truncLen)
            trunLenLeft = min(truncLen,options.maxStrLen)#in case maxStrLen is smaller as the truncation symbol
            result = result[:strLenLeft] + options.maxStrTruncationSymbol[:trunLenLeft] #truncate and add truncation indication
    return result


def EPackageStructureToCmd(ePackage:EPackage, parentId:str, cmd:Cmp, objLut:dict, objCount:int, options:EcoreConversionOptions, logger:Logger=NoLogger())->list:
    importedObjs = []
    (packId,objCount) = NextObjectId(objCount)
    m2modelId = ePackage.eGet(options.packageIdFeature)
    if(None == parentId):
        cmd.Crt(CONCEPTS.M2MODEL,U32(1),[m2modelId],resName=packId)
    else:
        cmd.Crt(CONCEPTS.M2PACKAGE,U32(1),[m2modelId,His(parentId)],resName=packId)
    ArtificialEObjectFeaturesToCmd(ePackage, packId, cmd, options)
    # first import enum
    for c in ePackage.eClassifiers:
        if (options.includeEnums and EEnum == type(c)):
            (enumId,objCount) = NextObjectId(objCount)
            cmd.Crt(CONCEPTS.M2ENUM,U32(1),[c.name,His(packId)],resName=enumId)
            ArtificialEObjectFeaturesToCmd(c,enumId, cmd, options)
            for l in c.eLiterals:
                (optionId,objCount) = NextObjectId(objCount)
                cmd.Crt(CONCEPTS.M2OPTIONOFENUM,U32(1),[l.name,U64(l.value),His(enumId)],resName=optionId)
                ArtificialEObjectFeaturesToCmd(l, optionId, cmd, options)
                objLut[l] = His(optionId)
                importedObjs.append(l)
            objLut[c] = His(enumId)
            importedObjs.append(c)
    # second import classes
    for c in ePackage.eClassifiers:
        if (EClass == type(c)):
            (classId, objCount) = NextObjectId(objCount)
            cmd.Crt(CONCEPTS.M2CLASS, U32(1), [c.name, c.abstract, His(packId)], resName=classId)
            ArtificialEObjectFeaturesToCmd(c, classId, cmd, options)
            objLut[c] = His(classId)
            importedObjs.append(c)
    if(options.includeSubpackes):
        for p in ePackage.eSubpackages: #recursively import any subpackages
            subobjs = EPackageStructureToCmd(p,packId,cmd,objLut,objCount,options,logger)
            objCount += len(subobjs)
            importedObjs += subobjs
    objLut[ePackage] = His(packId)
    importedObjs.append(ePackage)
    return importedObjs
        
        
def EPackageRefsToCmd(ePackage:EPackage, cmd:Cmp, objLut:dict, objCount:int, options:EcoreConversionOptions, logger:Logger=NoLogger())->list:
    importedObjs = []
    for c in ePackage.eClassifiers:
        if(EClass == type(c)):
            clazz = objLut[c]
            for f in c.eStructuralFeatures:
                (featId,objCount) = NextObjectId(objCount)
                eType = ResolveEProxy(f.eType,logger)
                if(EAttribute == type(f)):
                    attrName = f.name
                    attrType = None
                    # skip name-like features
                    if(IsNameFeature(attrName)):
                        logger.Warn('Skipped: %s.%s because it custom name features are not supported.'%(c.name,f.name))
                        continue
                    enum = NON()
                    try:
                        attrType = EAttributeTypeConceptPrimitiveId(eType)
                    except:
                        logger.Warn('Skipped: %s.%s because type %s is not supported or disabled'%(c.name,f.name,eType))
                        continue
                    if(M2PRIMITIVES.ENU == attrType):
                        enum = objLut[eType]
                    attrMul = f.upperBound  
                    attrUnit = GetEAnnotation(f, EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.UNIT, NON())
                    #create the attribute
                    cmd.Crt(CONCEPTS.M2ATTRIBUTE,U32(1),[attrName,clazz,attrType,attrMul,attrUnit,enum],resName=featId)
                    ArtificialEObjectFeaturesToCmd(f, featId, cmd, options)
                    ArtificialEAttributeFeaturesToCmd(f, featId, cmd, options)
                    objLut[f] = His(featId)
                    importedObjs.append(f)
                elif(EReference == type(f)):
                    if not f.containment:
                        dstName = f.name
                        srcMul = -1
                        srcName = dstName + options.autoOpositePrefix + f.eContainer().name
                        if(None != f.eOpposite):
                            srcName = f.eOpposite.name
                            srcMul = f.eOpposite.upperBound
                        srcClass = clazz
                        dstClass = None
                        anyDst = False
                        if(EObject.eClass==eType): #eClass seems necessary, since EObject is a build in class
                            anyDst = True
                        elif(isinstance(eType,EClass)):
                            dstClass = objLut[eType]
                        elif(None==eType):
                            logger.Warn('Skipped: %s.%s because type is not set.'%(c.name,f.name))
                            continue
                        else:
                            logger.Warn('Skipped: %s.%s because type %s is not supported.'%(c.name,f.name,eType))
                            continue
                        dstMul = f.upperBound
                        cmd.Crt(CONCEPTS.M2ASSOCIATION,U32(1),[srcName,srcClass,I64(srcMul),dstName,dstClass,I64(dstMul),anyDst],resName=featId)
                        ArtificialEObjectFeaturesToCmd(f, featId, cmd, options)
                        objLut[f] = His(featId)
                        importedObjs.append(f)
                    else: #containment
                        srcName = f.name
                        srcClass = clazz
                        dstClass = None
                        anyChild = False
                        if(EObject.eClass==eType):
                            anyChild = True
                        elif(isinstance(eType,EClass)):
                            try: 
                                dstClass = objLut[eType]
                            except KeyError:
                                logger.Warn('Skipped %s.%s because type cannot be resolved. Are subpackages disabled?'%(c.name,f.name))
                                continue
                        elif(None==eType):
                            logger.Warn('Skipped %s.%s because type is not set.'%(c.name,f.name))
                            continue
                        else:
                            logger.Warn('Skipped %s.%s because type %s is not supported.'%(c.name,f.name,eType))
                            continue
                        dstMul = f.upperBound
                        cmd.Crt(CONCEPTS.M2COMPOSITION,U32(1),[srcName,srcClass,dstClass,dstMul,anyChild],resName=featId)
                        ArtificialEObjectFeaturesToCmd(f, featId, cmd, options)
                        objLut[f] = His(featId)
                        importedObjs.append(f)
            for s in c.eSuperTypes:
                (inhId,objCount) = NextObjectId(objCount)
                subClass = clazz
                try:
                    superClass = objLut[s]
                except KeyError:
                    logger.Warn('Skipped %s -[inherits]-> %s because %s can not be resolved. Are subpackages disabled?'%(c.name,s.name,s.name))
                    continue
                cmd.Crt(CONCEPTS.M2INHERITANCE,U32(1),[subClass,superClass],resName=inhId)
                importedObjs.append(s)
    if(options.includeSubpackes):
        for p in ePackage.eSubpackages: #recursively import any subpackages
            subobjs = EPackageRefsToCmd(p, cmd, objLut, objCount, options, logger)
            objCount += len(subobjs)
            importedObjs += subobjs
    return importedObjs
        
        
### USER MODEL TO COMMAND CONVERSION ###

def EPackackeToStrId(ePack:EPackage,options:EcoreConversionOptions)->str:
    ''' Retrieves a string ID for a package (including the superpackage path
    '''
    allPackage = []
    currentPackage = ePack
    while(None != currentPackage):
        allPackage.append(currentPackage)
        currentPackage = currentPackage.eSuperPackage
    return options.idSeperator.join([p.eGet(options.packageIdFeature) for p in reversed(allPackage)])

def EUserModelToCmd(eObj:EObject, cmd:Cmp, objLut:dict, objCount:int, options:EcoreConversionOptions, name:str="UNNAMED", logger:Logger=NoLogger())->list:    
    #m2ModelStrId = eObj.eClass.ePackage.eGet(options.packageIdFeature)
    m2ModelStrId = EPackackeToStrId(eObj.eClass.ePackage,options)
    (modelId,objCount) = NextObjectId(objCount)
    name = STR(_EcoreValuePreprocessing(name,options))
    cmd.Crt(STR(CONCEPTS.M1MODEL),U32(1),[m2ModelStrId,name],resName=modelId)
    importedObjs = EObjectStructureToCmd(eObj, modelId, cmd, objLut, objCount, options, logger)
    return importedObjs
    
def EObjectStructureToCmd(eObj:EObject, modelId:str, cmd:Cmp, objLut:dict, objCount:int, options:EcoreConversionOptions, logger:Logger=NoLogger())->list:
    importedObjs = []
    eClass = eObj.eClass
    #classStrId = eClass.name #this is ambiguous
    #classStrId = eClass.eContainer().eGet(options.packageIdFeature) + options.idSeperator + eClass.name
    classStrId = EPackackeToStrId(eClass.ePackage,options) + options.idSeperator + eClass.name
    #obj = mdb.Create(classId)
    (objId,objCount) = NextObjectId(objCount)
    #obj = self.domain.Do( Crt(classId,U32(1)))
    name = "UNNAMED"
    try:
        name = STR(_EcoreValuePreprocessing(eObj.name,options))
    except:
        pass #no name given
    cmd.Crt(STR(CONCEPTS.M1OBJECT),U32(1),[classStrId,His(modelId),name],resName=objId)
    for f in eClass.eAllStructuralFeatures():
        eType = ResolveEProxy(f.eType,logger)
        fClass = f.eContainingClass
        featureName = f.name
        #feature = fClass.eContainer().eGet(options.packageIdFeature) + options.idSeperator + fClass.name + options.idSeperator + f.name
        #feature = objLut[f]
        if EAttribute == type(f):
            # skip name-like features
            if (IsNameFeature(featureName)):
                continue  # name is already in the M1OBJECT create args
            if(IsEPrimitiveType(eType) or isinstance(eType,EEnum)):
                eValue = eObj.eGet(f)
                if(f.many):
                    for v in eValue:
                        if(EEnumLiteral == type(v)):
                            v = _EcoreValuePreprocessing(v.name,options) #literals shall not be stored as literals
                        else:
                            v = EValueToValue(_EcoreValuePreprocessing(v,options),eType)
                        cmd.Crt(STR(CONCEPTS.M1ATTRIBUTE), 1,[featureName,His(objId),v])
                elif(None!=eValue):
                    if(options.skipEmptyStrings and str == type(eValue) and 0 == len(eValue)):
                        continue
                    elif(EEnumLiteral == type(eValue)):
                        eValue = _EcoreValuePreprocessing(eValue.name,options) #literals shall not be stored as literals 
                    else:
                        eValue = EValueToValue(_EcoreValuePreprocessing(eValue,options),eType)
                    cmd.Crt(STR(CONCEPTS.M1ATTRIBUTE),1,[featureName,His(objId),eValue])
            else:
                logger.Warn('Skipped %s.%s because type %s is not supported.'%(eObj,f.name,eType.name))
        elif(EReference == type(f) and f.containment):
            eValue = eObj.eGet(f)
            if(f.many):
                for v in eValue:
                    subobjs = EObjectStructureToCmd(v, modelId, cmd, objLut, objCount, options, logger) 
                    dstObj = objLut[subobjs[-1]]
                    cmd.Crt(STR(CONCEPTS.M1COMPOSITION),1,[featureName,His(objId),dstObj])
                    objCount += len(subobjs)
                    importedObjs += subobjs
            elif(not f.many and None != eValue):
                subobjs = EObjectStructureToCmd(eValue, modelId, cmd, objLut, objCount, options, logger)
                dstObj = objLut[subobjs[-1]]
                cmd.Crt(STR(CONCEPTS.M1COMPOSITION),1,[featureName,His(objId),dstObj])
                objCount += len(subobjs)
                importedObjs += subobjs
            else: #if object is none, do nothing
                pass
    # import artificial features for objects if possible
    if(IsEObjectAnnotationsPatchEnabled()):
        ArtificialEObjectFeaturesToCmd(eObj, objId, cmd, options)
    objLut[eObj] = His(objId)
    importedObjs.append(eObj)
    return importedObjs


def EObjectRefsToCmd(eObj:EObject, cmd:Cmp, objLut:dict, options:EcoreConversionOptions, logger:Logger=NoLogger())->None:
    ''' imports all non-containment references. 
    
    Should be done after the object tree was imported
    '''
    eClass = eObj.eClass
    obj = None
    try:
        obj = objLut[eObj]
    except KeyError:
        logger.Warn("Skipped: Unknown object %s."%(str(eObj)))   
        return
    for f in eClass.eAllStructuralFeatures():
        if(EReference == type(f) and not f.containment):
            eType = ResolveEProxy(f.eType,logger)
            eValue = eObj.eGet(f)
            #feature = objLut[f]
            feature = f.name
            #fClass = f.eContainingClass
            #feature = fClass.eContainer().eGet(options.packageIdFeature) + options.idSeperator + fClass.name + options.idSeperator + f.name
            if(f.many):
                i = 0
                for v in eValue:
                    eValueResolved = ResolveEProxy(v,logger)
                    dst = objLut[eValueResolved]
                    try:
                        cmd.Crt(STR(CONCEPTS.M1ASSOCIATION),1,[feature,obj,dst])
                        #cmd.Upd(obj,f.name+'*',objLut[eValueResolved],I64(-1),mute=options.muteUpdate)
                    except KeyError:
                        logger.Warn("Skipped: Found unresolvable proxy in <%s>.%s:%d."%(eClass.name,f.name,i))   
                    i+=1 
            elif(not f.many and None != eValue):
                eValueResolved = ResolveEProxy(eValue,logger)
                dst = objLut[eValueResolved]
                try:
                    cmd.Crt(STR(CONCEPTS.M1ASSOCIATION),1,[feature,obj,dst])
                    #cmd.Upd(obj,f.name,objLut[eValueResolved],mute=options.muteUpdate)
                except KeyError:
                    logger.Warn("Skipped: Found unresolvable proxy in <%s>.%s."%(eClass.name,f.name))   
                
            else: #if object is none, do nothing
                pass
        elif(EReference == type(f) and f.containment):
            eValue = eObj.eGet(f)
            if(f.many):
                for v in eValue:
                    EObjectRefsToCmd(v, cmd, objLut, options, logger) 
            elif(not f.many and None != eValue):
                EObjectRefsToCmd(eValue, cmd, objLut, options, logger)
                
### EANNOTATION HANDLING

def ArtificialEObjectFeaturesToCmd(eObj:EObject, objRef:str, cmd:Cmp, options:EcoreConversionOptions):
    ''' Import the features which are not real features in pyecore
    '''
    if(options.includeDocumentation):
        EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.DOCUMENTATION, EANNOTATION_SOURCES.DOCUMENTATION, EANNOTATION_KEYS.DOCUMENTATION, cmd, options)
    if(options.includeConstraints):
        EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.CONSTRAINTS  , EANNOTATION_SOURCES.CONSTRAINTS  , None  , cmd, options) 
    if(options.includePermissions):
        EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.OWNER        , EANNOTATION_SOURCES.OWNER        , EANNOTATION_KEYS.OWNER        , cmd, options) 
        EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.GROUP        , EANNOTATION_SOURCES.GROUP        , EANNOTATION_KEYS.GROUP        , cmd, options) 
        EAnnotationToFeatureCmd(eObj, objRef, MXELEMENT.PERMISSIONS  , EANNOTATION_SOURCES.PERMISSIONS  , None                          , cmd, options)  
    
def ArtificialEAttributeFeaturesToCmd(eObj:EObject, objRef:str, cmd:Cmp, options:EcoreConversionOptions):
    ''' Import the features which are not real features in pyecore
    '''
    EAnnotationToFeatureCmd(eObj, objRef, M2ATTRIBUTE.UNIT       , EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.UNIT, cmd, options)
        
def EAnnotationToFeatureCmd(eObj:EObject, objRef:str, featureName:str, source:str, key:str, cmd:Cmp, options:EcoreConversionOptions)->None:
    for a in eObj.eAnnotations:
        if(source == a.source):
            if(None==key): #import all 
                for v in a.details.values():
                    cmd.Upd(His(objRef),STR(featureName),STR(_EcoreValuePreprocessing(v,options)),I64(-1),mute=options.muteUpdate)
            else:
                if(key in a.details):
                    text = a.details[key]
                    cmd.Upd(His(objRef),STR(featureName),STR(_EcoreValuePreprocessing(text,options)),mute=options.muteUpdate)
            break #break anyhow, there wont be a second identical source
        
def GetEAnnotation(eObj:EObject, source:str, key:str, defaultReturn:Any)->Any:
    for a in eObj.eAnnotations:
        if(source == a.source):
            if(key in a.details):
                text = a.details[key]
                return text
    return defaultReturn
                

### SINGLE (META-)MODEL FILE CONVERSIONS               
                
def EcoreFileToCmdFile(infile:str, outfile:str, metafile:str=None, serializer:Serializer=TextSerializer(), options:EcoreConversionOptions=EcoreConversionOptions())->None:
    ''' Converts an ecore resource to the corresponding list of EOQ commands and writes that to a file
    '''
    cmd = EcoreFileToCmd(infile, metafile, options)
    outStream = EoqFileOutStream(outfile)
    outStream.Begin()
    for c in cmd.a:
        outStream.PushCmd(c)
    outStream.Flush()
    #end
    
    
def EcoreFileToCmd(infile:str, metafile:str=None, options:EcoreConversionOptions=EcoreConversionOptions())->(Cmp,dict,dict):
    ''' Converts an ecore resource to the corresponding list of EOQ commands
    '''
    logger = ConsoleLogger()
    
    rset = ResourceSet()
    
    
    #load the metafile if required
    if(metafile):
        eResourceMeta = rset.get_resource(metafile)
        ePackage = eResourceMeta.contents[0]  
        #register package 
        rset.metamodel_registry[ePackage.nsURI] = ePackage 
        #register any subpackage 
        for child in ePackage.eAllContents():
            if(isinstance(child,EPackage)):
                rset.metamodel_registry[child.nsURI] = child
            
    #load the pyecore model to convert
    eResource = rset.get_resource(infile)
    eRoot = eResource.contents[0]
    
    
    cmd = Cmp()
    packageIds = {}
    classIds = {}
    objLut = {}
    objCount = 0
    if(isinstance(eRoot,EPackage)):
        elems = EPackageStructureToCmd(eRoot, None, cmd, objLut, objCount, options, logger)
        objCount += len(elems)
        EPackageRefsToCmd(eRoot, cmd, objLut, objCount, options, logger)
        #retrieve the list of packages and classes
        packageIds[eRoot.name]  = eRoot.nsURI  
        for child in eRoot.eAllContents():
            if(isinstance(child,EPackage)):
                packageIds[child.name] = child.nsURI 
            elif(isinstance(child, EClass)):
                classIds[child.name] = child.eContainer().nsURI+options.idSeperator+child.name
        
        
    else: #regular model
        [path, name] = os.path.split(infile)
        elems = EUserModelToCmd(eRoot, cmd, objLut, objCount, options, name, logger)
        EObjectRefsToCmd(eRoot, cmd, objLut, options, logger)
        
    return (cmd,packageIds,classIds)
    #end