'''
 Read concepts information from concepts.xlsx.
 
 Dependencies
    - pandas
    - openpyxl
 
 Bjoern Annighoefer 2023
'''

import pandas

CONCEPT_PREFIX_LEN = 1
CONCEPT_UNIQUE_LEN = 4

def GenConceptKey(conceptName:str):
    paddedName = conceptName+"    "
    return paddedName[0:CONCEPT_UNIQUE_LEN]


### CLASSES

class Concepts:
    def __init__(self):
        self.layers = []
        self.conceptLuT = {} #look-up table for concepts
        self.testLuT = {}
        self.maxTestOrder = 1

class Layer:
    def __init__(self):
        self.name = "UNNAMED"
        self.description = ""
        self.concepts = []
        
class Concept:
    def __init__(self):
        self.name = "UNNAMED"
        self.id = "MISSING"
        self.description = ""
        self.nature = None
        self.abstract = False
        self.create = False
        self.delete = False
        self.clone = False
        self.instanceExists = False
        self.static = False
        self.superconcept = None
        self.properties = []
        self.ecore = None
        self.runmdb = None
        self.tests = []
        self.overwriteCreateProperties = False
        self.createPropertiesOverwrites = []
        self.propertyIdLuT = {}
        
    def GetAllSuperconcepts(self):
        superconcepts = []
        if(self.superconcept):
            superconcepts.append(self.superconcept)
            superconcepts += self.superconcept.GetAllSuperconcepts()
        return superconcepts
        
    def GetAllProperties(self):
        if(self.superconcept):
            overwritePool = [p.name for p in self.properties]
            return self.properties + [p for p in self.superconcept.GetAllProperties() if p.name not in overwritePool] 
        else:
            return self.properties
        
    def GetCreateProperties(self):
        createProperties = []
        if(self.overwriteCreateProperties):
            createProperties = list(self.createPropertiesOverwrites)
        elif(self.superconcept):
            createProperties = list(self.superconcept.GetCreateProperties()) #copy the properties
            for p in self.properties:
                if(p.createArg):
                    createProperties.append(p)
        return createProperties
        
        
class Property:
    def __init__(self):
        self.name = "UNNAMED"
        self.id = "MISSING"
        self.oppositePorpertyId = None
        self.abstract = False
        self.type = "UNSPECIFIED"
        self.nature = None
        self.unique = False
        self.min = 0
        self.max = 0
        self.createId = False
        self.createArg = False
        self.clonePath = False
        self.cloneBlocker = None #a string is expected here
        self.deletePath = False
        self.deleteBlocker = False
        self.read = False
        self.update = False
        self.derived = False
        self.recoveryArg = False
        self.description = ""
        self.ecore = None
        self.runmdb = None
        self.concept = None
        
class TestValue:
    def __init__(self,value,valueType):
        self.value = value
        self.type = valueType
        self.position = 0 #for update tests
        self.exception = None #name of the expected exception
        
    def __repr__(self)->str:
        return "%s"%(str(self.value))
        
class TestSpec:
    def __init__(self):
        self.name = "UNAMED_TEST"
        self.supertest = None
        self.order = 1
        self.result = True
        self.values = {}
        self.updateValues = {}
        self.number = -1
        self.variants = 1 #the number of variants is defined by the create arguments
        
class TestRef:
    def __init__(self):
        self.name = 'NAME_OF_TEST'
        self.index = None #no index is given, which is different from 0 index
        self.multiIndex = False
        self.create = True
        self.read = True
        self.update = False
        self.delete = True
    def __repr__(self)->str:
        return "#%s"%(self.name)
        
class ForeignClassRef:
    '''
    Reference to a foreign model
    '''
    def __init__(self):
        self.name = ''
        self.superclass = None
        self.artificial = False
        
    def InitFromString(self,text:str):
        '''expects a string like CLASSNAME[(SUPERCLASS)][*]
        Parts in [] are optional
        '''
        #artificial
        if(text.endswith("*")):
            self.artificial = True
            text = text[:-1] #shorten by one
        else:
            self.artificial = False
        #inherits
        if(text.endswith(")") and "(" in text):
            segs = text[:-1].split("(", 1)
            text = segs[0]
            self.superclass = segs[1]
        else:
            self.superclass = None
        #name
        self.name = text
        return     
        
class ForeignPropertyRef:
    '''
    Reference to a foreign model
    '''
    def __init__(self):
        self.name = ''
        self.type = None
        self.artificial = True
        self.defaultValue = None
    def InitFromString(self,text:str):
        '''expects a string like NAME[:TYPE][ = DEFAULTVALUE][*]
        Parts in [] are optional
        '''
        #artificial
        if(text.endswith("*")):
            self.artificial = True
            text = text[:-1] #shorten by one
        else:
            self.artificial = False
        #default value
        if(" = " in text):
            segs = text.split(" = ", 1)
            text = segs[0]
            self.defaultValue = segs[1]
        else:
            self.defaultValue = None
        #type
        if(":" in text):
            segs = text.split(":", 1)
            text = segs[0]
            self.type = segs[1]
        else:
            self.type = None
        #name
        self.name = text
        return     

### FUNCTIONS

def ParseTestValues(valueStr,propType):
    value = None
    valueType = propType
    s = valueStr
    if("+" in s): #concatenation
        segs = s.split('+')
        value = tuple([ParseTestValues(v,propType) for v in segs if '' != v])
        valueType = "CONCAT"
    elif(s.startswith("[") and s.endswith("]")):
        segs = s[1:-1].split(',')
        value = [ParseTestValues(v,propType) for v in segs if '' != v]
        valueType = "LST"
    else:
        if("-" == s):
            value = None
        elif(5 < len(s) and "(" == s[3] and ")" == s[-1]): #is a value type given?
            [pt,vs] = s[:-1].split('(')
            value = ParseTestValues(vs,pt).value
            valueType = pt #value type is overwritten
        elif("BOL"==propType):
            value = bool(int(s))
        elif("STR"==propType):
            value = s
        elif("U32"==propType or "U64"==propType or "I32"==propType or "I64"==propType ):
            value = int(s)
        elif(propType.startswith("M")):
            valueType = "OBJ"
            value = TestRef()
            if(":" in s):
                [n,i] = s.split(":",1)
                value.name = n
                if("*" == i):
                    value.multiIndex = True
                else:
                    value.index = int(i)
            else:
                value.name = s
        else:
            raise ValueError("Invalid test value: '%s'"%(valueStr))
    #print("s=%s,v=%s,t=%s"%(s,value,type(value)))
    testValue = TestValue(value, valueType)
    return testValue

def ParseTestEntry(concept:Concept, prop:Property, testSpec:TestSpec, testEntry:str):
    '''Parses the entry of a test string for a property and add the information to the TestSpec.
    Test entries are expected as 
    <create/read value(s)>[-><update values>]
    parts in [] are optional for updatable properties.
    '''
    segs = testEntry.split("->",1)
    values = ParseTestValues(segs[0],prop.type)
    updateValues = None
    testSpec.values[prop.name] = values
    if(prop.createArg and "LST" == values.type):
        testSpec.variants *= len(values.value)
    if(1 < len(segs)): #test has also update values
        if(not prop.update):
            raise ValueError("Update test value for not updatable property: %s.%s"%(concept.name,prop.name))
        updateValues = ParseTestValues(segs[1],prop.type)
        testSpec.updateValues[prop.name] = updateValues
    print("Test %s.%s: read=%s, update=%s"%(concept.name,prop.name,values,updateValues))
        
def ParseTestName(entry:str):
    name = None
    supertest = None
    if(entry.endswith(")") and "(" in entry):
        segs = entry[:-1].split("(")
        name = segs[0]
        supertest = segs[1]
    else:
        name = entry
    return (name,supertest)
    
def ParseTestSpec(concepts,testEntry:str,i:int):
    ''' Parse a test definition field and return a TestSpec.
    The expected format is
    <test name>[!<order>]
    [] are optional.
    '''
    segs = testEntry.split("!",2)
    (testName, supertest) = ParseTestName(segs[0])
    if(testName in concepts.testLuT):
        raise ValueError("Dublicated test name: %s"%(testName))
    newTest = TestSpec()
    newTest.name = testName
    newTest.supertest = supertest
    newTest.number = i
    if(1<len(segs)):
        testOrder = int(segs[1])
        newTest.order = testOrder
        if(concepts.maxTestOrder<testOrder):
            concepts.maxTestOrder = testOrder
    concepts.testLuT[newTest.name] = newTest
    return newTest
    


def ReadConcepts(inFile:str)->list:
    #read input table
    maxTests = 7
    concepts = Concepts() #the return data structure
    conceptsTable = pandas.read_excel(inFile,sheet_name = 0)
    currentLayer = None
    currentConcept = None
    currentProperty = None
    currentTests = None
    rowNumber = 0
    for index, row in conceptsTable.iterrows():
        rowNumber = rowNumber+1
        try:
            if(not row.isna()['Layer']):
                currentLayer = Layer()
                currentLayer.name = row['Layer']
                concepts.layers.append(currentLayer)
                if(not row.isna()["Description"]):
                    currentLayer.description = row["Description"]
            elif(not row.isna()["Concept"]):
                currentConcept = Concept()
                currentConcept.name = row['Concept']
                currentTests = [None for i in range(maxTests)]
                if(not row.isna()["Concept ID"]):
                    currentConcept.id = row["Concept ID"]
                if("x"==row['Instance exists']):
                    currentConcept.instanceExists = True
                if("x"==row['Static']):
                    currentConcept.static = True
                if(not row.isna()["Superconcept"]):
                    superconceptName = row["Superconcept"]
                    if(superconceptName in concepts.conceptLuT):
                        superconcept = concepts.conceptLuT[superconceptName]
                        currentConcept.superconcept = superconcept
                    else:
                        raise ValueError("Superconcept %s not found."%(superconceptName))
                if("x"==row['Abstract']):
                    currentConcept.abstract = True
                if("x"==row['Create']):
                    currentConcept.create = True
                if("x"==row['Delete']):
                    currentConcept.delete = True
                if("x"==row['Clone']):
                    currentConcept.clone = True
                if(not row.isna()["Nature"]):
                    currentConcept.nature = row["Nature"]
                if(not row.isna()["Description"]):
                    currentConcept.description = row["Description"]
                if(not row.isna()["Ecore"]):
                    currentConcept.ecore = ForeignClassRef()
                    currentConcept.ecore.InitFromString(row["Ecore"])
                if(not row.isna()["RUNMDB"]):
                    currentConcept.runmdb = ForeignClassRef()
                    currentConcept.runmdb.InitFromString(row["RUNMDB"])
                for i in range(maxTests):
                    colName = "Test%d"%(i+1)
                    if(not row.isna()[colName]):
                        newTest = ParseTestSpec(concepts,str(row[colName]),i)
                        currentTests[i] = newTest
                        currentConcept.tests.append(newTest)
                currentLayer.concepts.append(currentConcept)  
                concepts.conceptLuT[currentConcept.name] = currentConcept
            elif(not row.isna()["Property"]):
                propertyName = row['Property']
                currentProperty = None
                if("x"==row['Test only'] or "x"==row['Create arg overwrite']): 
                    #this is only a name of an existing property, so find it
                    propertyLookUp = {p.name : p for p in currentConcept.GetAllProperties()}
                    if(propertyName in propertyLookUp):
                        currentProperty = propertyLookUp[propertyName]
                    else:
                        raise ValueError("Test or overwrite property %s is not defined for %s"%(propertyName,currentConcept.name))
                    if("x"==row['Create arg overwrite']):
                        if("x"==row['Create arg.']):
                            currentConcept.overwriteCreateProperties = True
                            currentConcept.createPropertiesOverwrites.append(currentProperty)
                else:
                    currentProperty = Property()
                    currentProperty.name = propertyName
                    currentProperty.concept = currentConcept
                    if(not row.isna()["Property ID"]):
                        currentProperty.id = row["Property ID"]
                    if(not row.isna()["Opposite Property ID"]):
                        currentProperty.oppositePorpertyId = row["Opposite Property ID"]
                    if(not row.isna()["Nature"]):
                        currentProperty.nature = row["Nature"]
                    if(not row.isna()["Type"]):
                        currentProperty.type = row["Type"]
                    if("x"==row['Unique']):
                        currentProperty.unique = True
                    if(not row.isna()["Min"]):
                        if('*' == row["Min"]):
                            currentProperty.min = -1
                        else:
                            currentProperty.min = int(row["Min"])
                    if(not row.isna()["Max"]):
                        if('*' == row["Max"]):
                            currentProperty.max = -1
                        else:
                            currentProperty.max = int(row["Max"])
                    if("x"==row['Create ID']):
                        currentProperty.createId = True
                    if("x"==row['Create arg.']):
                        currentProperty.createArg = True
                    if("x"==row['Abstract']):
                        currentProperty.abstract = True
                    if("x"==row['Read']):
                        currentProperty.read = True
                    if("x"==row['Update']):
                        currentProperty.update = True
                    if("x"==row['Derived']):
                        currentProperty.derived = True
                    if("x"==row['Clone path']):
                        currentProperty.clonePath = True
                    if(not row.isna()['Clone blocker']):
                        currentProperty.cloneBlocker = row['Clone blocker']
                    if("x"==row['Delete path']):
                        currentProperty.deletePath = True
                    if("x"==row['Delete blocker']):
                        currentProperty.deleteBlocker = True
                    if("x"==row['Recovery arg.']):
                        currentProperty.recoveryArg = True
                    if(not row.isna()["Description"]):
                        currentProperty.description = row["Description"]
                    if(not row.isna()["Ecore"]):
                        currentProperty.ecore = ForeignPropertyRef()
                        currentProperty.ecore.InitFromString(row["Ecore"])
                    if(not row.isna()["RUNMDB"]):
                        currentProperty.runmdb = ForeignPropertyRef()
                        currentProperty.runmdb.InitFromString(row["RUNMDB"])
                    currentConcept.properties.append(currentProperty)
                    currentConcept.propertyIdLuT[currentProperty.id] = currentProperty
                #Test values
                for i in range(maxTests):
                    colName = "Test%d"%(i+1)
                    if(not row.isna()[colName]):
                        ParseTestEntry(currentConcept,currentProperty,currentTests[i],str(row[colName]))
                        #currentTests[i].values[currentProperty.name] = ParseTestValues(row[colName],currentProperty.type)
        except:
            print("FAILED IN ROW %d!"%(rowNumber))
            raise
        
    # sanity checks
    # 1. check if chars of concept IDs and property IDs are unique
    cKeyDict = {}
    for l in concepts.layers:
        for c in l.concepts:
            cKey = GenConceptKey(c.id)
            if(CONCEPT_UNIQUE_LEN > len(cKey)):
                print("WARNING: %s of %s has less then %d chars"%(cKey,c.name,CONCEPT_UNIQUE_LEN))
            if(cKey in cKeyDict):
                print("WARNING: %s of %s is not unique amoungst concepts"%(cKey,c.name))
            else:
                cKeyDict[cKey] = c
            # 2. check if property name is unique
            pKeyDect = {}
            for p in c.GetAllProperties():
                pKey = GenConceptKey(p.id)
                if(CONCEPT_UNIQUE_LEN > len(pKey)):
                    print("WARNING: %s.%s of %s has less then %d chars"%(c.name,pKey,p.name,CONCEPT_UNIQUE_LEN))
                if(pKey in pKeyDect):
                    print("WARNING: %s.%s of %s is not unique amoungst concepts"%(c.name,pKey,p.name))
                else:
                    pKeyDect[pKey] = p
        
    return concepts