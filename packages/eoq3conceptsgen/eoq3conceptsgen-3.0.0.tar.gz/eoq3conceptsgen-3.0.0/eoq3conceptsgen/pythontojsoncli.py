'''
 Extracts python methods to json file for injection in a template. 
 This can be used to use python method content from as optional "data" input in a concept template generation.
 
 Dependencies
    - json
 
 Bjoern Annighoefer 2023
'''

from .pythontojson import PythonToJson

import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='pytojson',description='Extracts Method names and bodies to a json dict')
    parser.add_argument('-i','--inFile', required=False, type=str, default='input.py',help='The input python file')
    parser.add_argument('-o','--outFile', required=False, type=str, default='output.json',help='The output json file')
    parser.add_argument('-g','--ignoreBefore', required=False, type=str, default='_IGNORE_BEFORE_',help='Drops the content of a def section before a line containing this string, including this line.')

    args = parser.parse_args()
    
    print('*************************************************')
    print('* py to json                                    *')
    print('*************************************************')
    print('In file:     %s'%(args.inFile))
    print('Out file:    %s'%(args.outFile))
    print('Ignore bef.: %s'%(args.ignoreBefore))
    
    # configuration
    inFile = args.inFile
    outFile = args.outFile
    ignoreBefore = args.ignoreBefore
    
    PythonToJson(inFile,outFile,ignoreBefore)        
    