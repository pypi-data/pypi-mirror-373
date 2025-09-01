'''
 Bjoern Annighoefer 2024
'''

from eoq3.config import EOQ_DEFAULT_CONFIG

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
        self.packageIdFeature = 'name' #by default it is the package namespace uri, can also be the name
        self.idSeperator = EOQ_DEFAULT_CONFIG.strIdSeparator
        self.prefixSeperator = '.' #used for nsPrefix construction
        self.skipEmptyStrings = True
        
DEFAULT_ECORE_CONVERSION_OPTIONS = EcoreConversionOptions()

### Special section for ADA EOQ
DEFAULT_ADAEOQ_CONVERSION_OPTIONS = EcoreConversionOptions()
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.includeSubpackes = True
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.includeEnums = True
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.includeDocumentation = True
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.includeConstraints = False
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.includePermissions = False
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.muteUpdate = False
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.maxStrLen = 20
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.maxStrTruncationSymbol = "..."
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.translateChars = True
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.translateTable = [(' ','_'),(':','_'),('\n',''),('#',''),('-',''),('%',''),('\r','_'),('\t','_'),(',','_'),('/','_'),('(','_'),(')','_'),('[','_'),(']','_'),('{','_'),('}','_'),(';','_'),('\\','_'),('=','_')]
DEFAULT_ADAEOQ_CONVERSION_OPTIONS.packageIdFeature = 'name'
