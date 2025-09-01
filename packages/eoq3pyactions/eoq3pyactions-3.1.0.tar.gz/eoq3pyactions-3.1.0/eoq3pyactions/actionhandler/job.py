'''
A local structure to store job informations on running jobs
 2022 Bjoern Annighoefer
'''

from eoq3.query import Obj
from .action import Action


class Job:
    def __init__(self,jobObj:Obj, action:Action, arguments:list, outputEvtKey:str, inputEvtKey:str, timeout:float, statusInstance:Obj, controlFlagInstance:Obj):
        self.jobObj = jobObj
        self.action = action
        self.arguments = arguments
        self.outputEvtKey = outputEvtKey
        self.inputEvtKey = inputEvtKey
        self.timeout = timeout
        self.statusInstance = statusInstance
        self.controlFlagInstance = controlFlagInstance
        #internals
        self.started = False
        self.aborted = False
        self.jobMonitorThread = None
        self.jobWorkerProcess = None
        self.domainWrapper = None
        
    def SetStarted(self,process,domainWrapper):
        self.started = True
        self.process = process
        self.domainWrapper = domainWrapper
        
    def HasStarted(self):
        return self.started;
    
    def IsAborted(self):
        return self.aborted;
    
    def Abort(self):
        self.aborted = True;