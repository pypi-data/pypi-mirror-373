'''
2024 Bjoern Annighoefer
'''

from eoq3.config import Config, EOQ_DEFAULT_CONFIG
from eoq3.util.eoqfile import EoqFileOutStream, ObjToHisStream, ResNameGenStream, SimpleResNameGen

from .ecoreconversionoptions import EcoreConversionOptions, DEFAULT_ECORE_CONVERSION_OPTIONS
from .ecorecmdstream import EObjectInStream
from .ecoreutils import LoadAndRegisterEPackages

from pyecore.resources import ResourceSet 

def EcoreFileToEoqFile(infile:str, 
                       outfile:str, 
                       metafile:str=None, 
                       m1ModelName:str="m1Model", 
                       validateFirst:bool=False, 
                       options:EcoreConversionOptions=DEFAULT_ECORE_CONVERSION_OPTIONS, 
                       config:Config=EOQ_DEFAULT_CONFIG):
    # load ecore resource
    rset = ResourceSet()
    #load the metafile if required
    if(metafile):
        LoadAndRegisterEPackages(metafile,rset)
    #load the pyecore model to convert
    eResource = rset.get_resource(infile)
    #validate
    inStream = EObjectInStream(options,config)
    if(validateFirst):
        inStream.Begin()
        inStream.LoadEObjects(eResource.contents, m1ModelName)
        inStream.Flush()
    #setup cmd stream
    nameGenrator = ResNameGenStream(SimpleResNameGen())
    objToHis = ObjToHisStream()
    outStream = EoqFileOutStream(outfile,config.fileSerializer)
    inStream.Connect(nameGenrator)
    nameGenrator.Connect(objToHis)
    objToHis.Connect(outStream)
    #start conversion
    inStream.Begin()
    inStream.LoadEObjects(eResource.contents, m1ModelName)
    inStream.Flush()
        
    