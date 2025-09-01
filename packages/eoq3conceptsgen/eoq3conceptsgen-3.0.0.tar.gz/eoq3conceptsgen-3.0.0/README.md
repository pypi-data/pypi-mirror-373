# eoq3conceptsgen - Code generator for EOQ3 concepts

Scripts for generating code out of the formal definition of concepts using mako templates.

## Command-line Interface (CLI)

### Usage

    python -m eoq3conceptsgen.generatefromconceptscli --help
    usage: generatefromconcepts [-h] [-c CONCEPTSDEFFILE] [-i INFILE] [-o OUTFILE] [-d DATAFILE]
    
    Generates mako templates from the content of concepts.xlsx
    
    options:
      -h, --help            show this help message and exit
      -c CONCEPTSDEFFILE, --conceptsDefFile CONCEPTSDEFFILE
                            the concept definition file
      -i INFILE, --inFile INFILE
                            The input template
      -o OUTFILE, --outFile OUTFILE
                            The generated file
      -d DATAFILE, --dataFile DATAFILE
                            Optional json data file, whose content is available as "data" in the template
							
### Examples

Generate concepts.py from sample.mako (included in package):

    python -m eoq3conceptsgen.generatefromconceptscli -o concepts.py
	
## API Interface

    from .generatefromconcepts import GenerateFromConcepts
	...
	GenerateFromConcepts(inFile,conceptsDefFile,outFile,dataFile)

## Documentation

For more information see EOQ3 documentation: https://eoq.gitlab.io/doc/eoq3/

## Author

2024 Bjoern Annighoefer