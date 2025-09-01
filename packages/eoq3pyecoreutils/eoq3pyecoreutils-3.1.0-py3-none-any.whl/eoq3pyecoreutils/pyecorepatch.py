'''
Functions to extend the function of pyecore
 Bjoern Annighoefer 2022
'''

from pyecore.ecore import EClass, EObject, EReference, EAnnotation


def IsEObjectAnnotationsPatchEnabled():
    try: #test if the annotations have been added before
        test = EObject.eAnnotations
        return True
    except AttributeError:
        return False

def EnableEObjectAnnotationsPatch():
    try: #test if the annotations have been added before
        test = EObject.eAnnotations
    except AttributeError:
        # add eAnnotations to all eObjects
        EObject.eAnnotations = EReference('eAnnotations', EAnnotation, upper=-1, containment=True)
        EAnnotation.eObject = EReference('eObject', EObject, eOpposite=EObject.eAnnotations)
        EObject.eClass.eStructuralFeatures.append(EObject.eAnnotations)  # only to be sure it will serialize the data
        # EClass.findEStructuralFeature need a replacement, because it does not include EObject in the super type search hierarchy
        def findEStructuralFeaturePatch(self, name):
            #old part
            eFeature = next((f for f in self._eAllStructuralFeatures_gen()
                         if f.name == name),
                        None)
            #new part: see if it is part of EObject
            if(None==eFeature): 
                eFeature = next((f for f in EObject.eClass._eAllStructuralFeatures_gen()
                         if f.name == name),
                        None)
            return eFeature
        #patch the EClass method
        EClass.findEStructuralFeature = findEStructuralFeaturePatch

