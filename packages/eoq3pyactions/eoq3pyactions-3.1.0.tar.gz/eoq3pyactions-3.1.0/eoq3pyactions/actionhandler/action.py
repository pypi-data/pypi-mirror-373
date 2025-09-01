'''
 2019 Bjoern Annighoefer
'''

class Action:
    def __init__(self,name,handlerFunction,args=[],results=[],description="",category="",tags=[]):
        self.name = name
        self.handlerFunction = handlerFunction
        self.args = args
        self.results = results
        self.description = description
        self.category = category # a / seperated list of categories and subcategories
        self.tags = tags
        
class ActionArg:
    def __init__(self,name,datatype,min=1,max=1,description="",default="",options=[]):
        self.name = name
        self.type = datatype
        self.min = min
        self.max = max
        self.default = default
        self.description = description
        self.options = options
        
class ActionArgOption:
    def __init__(self,value,description=""):
        self.value = value
        self.description = description
        
