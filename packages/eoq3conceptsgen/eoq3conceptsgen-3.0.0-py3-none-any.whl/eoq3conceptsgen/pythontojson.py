'''
 Extracts python methods to json file for injection in a template. 
 This can be used to use python method content from as optional "data" input in a concept template generation.
 
 Dependencies
    - json
 
 Bjoern Annighoefer 2023
'''

import json
    
def PythonToJson(inFile:str, outFile:str, ignoreBefore:str='_IGNORE_BEFORE_'):
    
    data = {"class":{},"def":{}}
    
    with open(inFile, 'r') as f:
        lines = f.readlines()
        functionBlock = None
        parentBlock = data
        annotations = []
        defIndent = 0 #indention at the beginning of def
        lineNumber = 0
        for l in lines:
            lineNumber += 1
            t = l.lstrip()
            curIndent = len(l)-len(t)
            if(t.startswith('def ')):
                defIndent = curIndent
                fNameBegin = t[4:]
                fName = fNameBegin[:fNameBegin.find("(")]
                functionBlock = {"type": "def", "name" : fName, "annotations": annotations, "head": l.rstrip(), "body" : []}
                parentBlock["def"][fName] = functionBlock
                annotations = []
            elif(t.startswith('class ')):
                cNameBegin = t[6:]
                if("(" in cNameBegin): 
                    cName = cNameBegin[:cNameBegin.find("(")]
                else: 
                    cName = cNameBegin[:cNameBegin.find(":")]
                parentBlock = {"type":"class", "name": cName, "head": l.rstrip(), "def":{}}
                data["class"][cName] = parentBlock
            elif(t.startswith("#@")):
                annotations.append(l.rstrip())
            elif(ignoreBefore in t and functionBlock):
                functionBlock["body"] = [] #empty the current function block
            elif(len(t) > 0 and (curIndent<=defIndent)):
                #close current function
                functionBlock = None
            elif(functionBlock):
                functionBlock["body"].append(l.rstrip())
                
    with open(outFile, 'w') as f:
        f.write(json.dumps(data, indent=4))
        
    