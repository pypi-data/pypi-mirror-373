

'''
 Used to generate Mako-Templates from concepts.xlsx.
 
 Dependencies
    - pandas
    - openpyxl
    - mako
    - argparse
 
 Bjoern Annighoefer 2023
'''

from .generatefromconcepts import GenerateFromConcepts

import argparse
## used for internal resources
from importlib.resources import files, as_file

class Generator:
    def __init__(self):
        self.name = None
        self.inFile = None
        self.genDate = None
        
if __name__ == "__main__":
    as_file(files("eoq3conceptsgen").joinpath('concepts.xlsx'))
    with as_file(files("eoq3conceptsgen").joinpath('concepts.xlsx')) as internalConceptsFile:
        defaultConceptsFile = str(internalConceptsFile)
    with as_file(files("eoq3conceptsgen").joinpath('sample.mako')) as internalTemplateFile:
        defaultTemplateFile = str(internalTemplateFile)
    
    
    parser = argparse.ArgumentParser(prog='eoq3conceptsgen.generatefromconceptscli',description='Generates mako templates from the content of concepts.xlsx')
    parser.add_argument('-c','--conceptsDefFile', required=False, type=str, default=defaultConceptsFile,help='the concept definition file')
    parser.add_argument('-i','--inFile', required=False, type=str, default=defaultTemplateFile,help='The input template')
    parser.add_argument('-o','--outFile', required=False, type=str, default='sample.txt',help='The generated file')
    parser.add_argument('-d','--dataFile', required=False, type=str, default=None,help='Optional json data file, whose content is available as "data.<fieldname>" in the template')

    args = parser.parse_args()
    
    print('*********************************************************')
    print('* Concepts generator                                    *')
    print('*********************************************************')
    print('Concept def: %s '%(args.conceptsDefFile))
    print('In file:     %s '%(args.inFile))
    print('Out file:    %s '%(args.outFile))
    print('Data file:   %s '%(args.dataFile))
    
    # configuration
    inFile = args.inFile
    conceptsDefFile = args.conceptsDefFile
    outFile = args.outFile
    dataFile = args.dataFile
    
    GenerateFromConcepts(inFile,conceptsDefFile,outFile,dataFile)
        
    