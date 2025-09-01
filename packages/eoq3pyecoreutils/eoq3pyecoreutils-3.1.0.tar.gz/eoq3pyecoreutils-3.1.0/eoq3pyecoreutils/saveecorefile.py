'''
 Bjoern Annighoefer 2024
'''

from eoq3.domain import Domain
from eoq3.value import STR
from eoq3.query import Qry, Obj
from eoq3.command import Get
from eoq3.util.eoqfile import FromDomainCmdStream, DependencyResolverStream

from .ecoreutils import LoadAndRegisterEPackages, RegisterEPackages
from .ecorecmdstream import EObjectOutStream
from .ecoreconversionoptions import EcoreConversionOptions, DEFAULT_ECORE_CONVERSION_OPTIONS

from pyecore.ecore import EPackage
from pyecore.resources import ResourceSet 
from eoq3.concepts.concepts import MXELEMENT, M1OBJECT, M1MODEL

def SaveEcoreFile(outfile:str, 
                rootObj:Obj, 
                domain:Domain, 
                sessionId:str=None,
                metafile:str=None,
                saveMetamodelInAddition:bool=False, 
                options:EcoreConversionOptions=DEFAULT_ECORE_CONVERSION_OPTIONS):
    '''Save a model to an eoqfile
    '''
    #initialize a resource set
    rset = ResourceSet()
    if(metafile and not saveMetamodelInAddition):
        LoadAndRegisterEPackages(metafile,rset)
    inStream = FromDomainCmdStream(domain,sessionId)
    sorter = DependencyResolverStream(True,False)
    outStream = EObjectOutStream(rset,options)
    inStream.Connect(sorter)
    sorter.Connect(outStream)
    if(metafile and saveMetamodelInAddition):
        #find the metamodel
        m2model = domain.Do( Get(Qry(rootObj).Pth(STR(M1MODEL.M2MODEL))),sessionId)
        inStream.Begin()
        inStream.LoadM2Model(m2model)
        ePackage = outStream.GetOrphans()[0]
        inStream.Flush()
        m2Resource = rset.create_resource(metafile)
        m2Resource.append(ePackage)
        m2Resource.save()
        RegisterEPackages(ePackage,rset) #make sure the metamodel is found, when the user model is loaded.
    #load user model only or only metamodel
    inStream.Begin()
    inStream.LoadElement(rootObj)
    eRoots = outStream.GetOrphans() #extract before flush deletes that
    inStream.Flush()
    resource = rset.create_resource(outfile)
    for eRoot in eRoots:
        resource.append(eRoot)
    resource.save()