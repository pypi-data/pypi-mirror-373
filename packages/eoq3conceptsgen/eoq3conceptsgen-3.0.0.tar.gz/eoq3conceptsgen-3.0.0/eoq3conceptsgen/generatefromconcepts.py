

'''
 Used to generate Mako-Templates from concepts.xlsx.
 
 Dependencies
    - pandas
    - openpyxl
    - mako
    - argparse
 
 Bjoern Annighoefer 2023
'''

from .readconcepts import ReadConcepts

import sys
import datetime
import json
from mako.template import Template
from mako import exceptions

class Generator:
    def __init__(self):
        self.name = None
        self.inFile = None
        self.genDate = None
        
 
def GenerateFromConcepts(inFile:str,conceptsDefFile:str,outFile:str,dataFile:str=None)->None:

    data = {}

    # store basic information in generator class
    generator = Generator()
    generator.inFile = inFile
    generator.genDate =  datetime.datetime.now()
    generator.name = sys.argv[0]
    generator.cmd = " ".join(sys.argv)

    # load concepts class
    concepts = ReadConcepts(conceptsDefFile)
    
    # optionally load data
    if(dataFile): 
        with open(dataFile, 'r') as f:
            data = json.load(f)
        
    #render template
    template = Template(filename=inFile,preprocessor=[lambda x: x.replace("\r\n", "\n")]) #preprocessor is necessary on Windows
    try:
        renderedTemplate = template.render_unicode(generator=generator,concepts=concepts,data=data)
        with open(outFile, 'w') as f:
            f.write(renderedTemplate)
    except:
        msg = exceptions.text_error_template().render()
        print(msg, file=sys.stderr)
        
    