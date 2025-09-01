'''
 Bjoern Annighoefer 2024
'''

from eoq3.domain import Domain
from eoq3.config import Config, EOQ_DEFAULT_CONFIG
from eoq3.util.eoqfile import ToDomainCmdStream

from .ecoreutils import LoadAndRegisterEPackages
from .ecoreconversionoptions import EcoreConversionOptions, DEFAULT_ECORE_CONVERSION_OPTIONS
from .ecorecmdstream import EObjectInStream

from pyecore.resources import ResourceSet 
    

def LoadEcoreFile(infile:str, 
                  domain:Domain, 
                  sessionId:str=None, 
                  metafile:str=None, 
                  validateBeforeLoad:bool=True, 
                  loadMetamodelInAddition:bool=False, 
                  m1ModelName:str="M1Model", 
                  options:EcoreConversionOptions=DEFAULT_ECORE_CONVERSION_OPTIONS, 
                  config:Config=EOQ_DEFAULT_CONFIG)->None:
    '''Loads an ecore or user model file to a domain
    Metafile is only needed if a infile is a user model.
    '''
    rset = ResourceSet()
    ePackages = []
    #load the metafile if required
    if(metafile):
        ePackages = LoadAndRegisterEPackages(metafile,rset)
    #load the pyecore model to convert
    eResource = rset.get_resource(infile)
    #validate
    inStream = EObjectInStream(options,config)
    if(validateBeforeLoad):
        inStream.Begin()
        if(loadMetamodelInAddition):
            inStream.LoadEPackages(ePackages)
        inStream.LoadEObjects(eResource.contents, m1ModelName)
        inStream.Flush()
    #load to domain
    inStream.Connect(ToDomainCmdStream(domain,sessionId,True,False))
    inStream.Begin()
    if(loadMetamodelInAddition):
        inStream.LoadEPackages(ePackages)
    inStream.LoadEObjects(eResource.contents, m1ModelName)
    inStream.Flush()