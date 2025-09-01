'''
 Bjoern Annighoefer 2024
'''

from .ecoreutils import LoadAndRegisterEPackages
from .ecorecmdstream import EObjectOutStream
from .ecoreconversionoptions import EcoreConversionOptions, DEFAULT_ECORE_CONVERSION_OPTIONS

from eoq3.util.eoqfile import EoqFileInStream
from pyecore.resources import ResourceSet 

def EoqFileToEcoreFile(infile:str,
                        outfile:str, 
                        metafile:str=None,
                        validateBeforeLoad:bool=False, 
                        options:EcoreConversionOptions=DEFAULT_ECORE_CONVERSION_OPTIONS):
    '''Load an eoq file and convert to ecore
    '''
    inStream = EoqFileInStream()
    if(validateBeforeLoad):
        #load the file, before the domain is connected.
        inStream.Begin()
        inStream.LoadEoqFile(infile)
        inStream.Flush()
    #initialize a resource set
    rset = ResourceSet()
    if(metafile):
        LoadAndRegisterEPackages(metafile,rset)
    outStream = EObjectOutStream(rset,options)
    inStream.Connect(outStream)
    #load user model only or only metamodel
    inStream.Begin()
    inStream.LoadEoqFile(infile)
    eRoots = outStream.GetOrphans() #extract before flush deletes that
    inStream.Flush()
    resource = rset.create_resource(outfile)
    for eRoot in eRoots:
        resource.append(eRoot)
    resource.save()