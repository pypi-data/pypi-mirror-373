'''
 Bjoern Annighoefer 2024
'''

from pyecore.ecore import EObject, MetaEClass, EProxy, EPackage
from pyecore.resources import ResourceSet 

import types #required for ModuleType
from typing import Any, Callable, List

def GetEAnnotation(eObj:EObject, source:str, key:str, defaultReturn:Any)->Any:
    for a in eObj.eAnnotations:
        if(source == a.source):
            if(key in a.details):
                text = a.details[key]
                return text
    return defaultReturn

def ResolveEProxy(proxy:EObject, failOnNotResolved=False, cannotResolveCallback:Callable[[EProxy,Exception],None]=None)->EObject:
    obj = proxy
    if(isinstance(proxy, EProxy)):
        try: 
            #resolve can fail if files have been modified or objects been deleted 
            # before the proxy has been resolved
            proxy.force_resolve()
            obj = proxy._wrapped #remove the outer proxy
        except Exception as e:
            if(cannotResolveCallback):
                cannotResolveCallback(obj)
            if(failOnNotResolved):
                raise e
            else:
                obj = None
    if(isinstance(proxy, (MetaEClass,type,types.ModuleType))): 
        #this is necessary to mask compiled model instances
        obj = proxy.eClass
    return obj

def RegisterEPackages(ePackage:EPackage, rset:ResourceSet)->None:
    ''' Registers the package and all subpackages
    in the metamodel_registry of a resource set.
    '''
    #register package 
    rset.metamodel_registry[ePackage.nsURI] = ePackage 
    #register any subpackage 
    for child in ePackage.eAllContents():
        if(isinstance(child,EPackage)):
            rset.metamodel_registry[child.nsURI] = child

def LoadAndRegisterEPackages(metafile:str, rset:ResourceSet)->List[EPackage]:
    '''loads an ecore meta model from a file 
    and registers the package and all subpackages
    in the metamodel_registry of a resource set.
    '''
    eResourceMeta = rset.get_resource(metafile)
    ePackages = [p for p in eResourceMeta.contents if isinstance(p, EPackage)]
    for p in ePackages:
        RegisterEPackages(p,rset)
    return ePackages

