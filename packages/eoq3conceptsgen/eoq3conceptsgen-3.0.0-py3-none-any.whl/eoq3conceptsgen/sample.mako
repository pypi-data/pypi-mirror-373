## -*- coding: utf-8 -*-
'''
 concepts.py provides a generic interface each model back-end working with eoq3 should support. 
 Concepts are generic constructs that should be available in any domain-specific framework and 
 modeling language. 
 
 This file is generated form: ${generator.inFile} on ${generator.genDate} by calling ${generator.cmd}.
 
 Bjoern Annighoefer 2023
'''

'''
DEFINITIONS 
'''

CONCEPT_PREFIX = '*'
FEATURE_MULTIVALUE_POSTFIX = '*'
CONCEPT_PREFIX_LEN = len(CONCEPT_PREFIX)
CONCEPT_UNIQUE_LEN = 4 #statically defined. Checked in generate concepts


class CONCEPTS:
    def __init__(self):
        raise NotImplementedError()
% for layer in concepts.layers:
% for concept in layer.concepts:
    ${concept.name.upper()} = "*${concept.id}"
% endfor
% endfor


% for layer in concepts.layers:
'''
${layer.name} LAYER
'''
% for concept in layer.concepts:
class ${concept.name.upper()}:
    def __init__(self):
        raise NotImplementedError()
    % for property in concept.properties:
    % if property.read or property.update:
    ${property.name.upper()} = "*${property.id}${'*' if(property.max>1 or property.max<0) else ''}" # ${"%5s %3s %3s %s"%(property.type,property.min,property.max,property.description)}
    % endif
    % endfor
    
% endfor
% endfor

def IsConcept(name : str):
    return name.startswith(CONCEPT_PREFIX)

def IsMultivalueFeature(featureName : str):
    return featureName.endswith(FEATURE_MULTIVALUE_POSTFIX)

def NormalizeFeatureName(featureName : str):
    n = len(featureName)
    #start = 1 if featureName.startswith(GENERIC_FEATURE_PREFIX) or featureName.startswith(FEATURE_READONLY_PREFIX) else 0
    end = n-1 if featureName.endswith(FEATURE_MULTIVALUE_POSTFIX) else n
    return featureName[:end]

def GetConceptKeyString(conceptName:str)->str:
    '''Extracts the first and unique chars of a concept or concept feature name and returns it
    '''
    paddedName = conceptName+"    "
    return paddedName[CONCEPT_PREFIX_LEN:(CONCEPT_PREFIX_LEN+CONCEPT_UNIQUE_LEN)]
