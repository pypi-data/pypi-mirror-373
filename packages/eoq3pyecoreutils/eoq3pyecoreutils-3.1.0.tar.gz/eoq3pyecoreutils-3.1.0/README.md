# eoq3pyecoreutils - pyecore-eoq3 bridge

An auxilary package for using eoq3 with pyecore, e.g. value type and model conversion as well as operation conversion and Concepts wrappers.

### Usage

Imports:

    from eoq3pyecoreutils.ecorefiletoeoqfile import EcoreFileToEoqFile
    from eoq3pyecoreutils.eoqfiletoecorefile import EoqFileToEcoreFile
	
Uploading ecore files:
    
    m2EcoreFile = "testdata/Workspace/Meta/oaam.ecore"
    m1EcoreFile = "testdata/Workspace/MinimalFlightControl.oaam"
    
    LoadEcoreFile(m2EcoreFile,domain,options=resource.options,config=resource.config)
    LoadEcoreFile(m1EcoreFile,domain,metafile=m2EcoreFile,options=resource.options,config=resource.config)
	
Saving ecore files:

	SaveEcoreFile(m2EcoreFileSaved, rootObj, domain, options=resource.options)
	SaveEcoreFile(m1EcoreFileSaved, rootObj, domain, metafile=m2EcoreFile, options=resource.options)
	SaveEcoreFile(m1EcoreFileSaved, rootObj, domain, metafile=m2EcoreFileSaved, saveMetamodelInAddition=True, options=resource.options)

## Documentation

For more information see EOQ3 documentation: https://eoq.gitlab.io/doc/eoq3/

## Author

2024 Bjoern Annighoefer