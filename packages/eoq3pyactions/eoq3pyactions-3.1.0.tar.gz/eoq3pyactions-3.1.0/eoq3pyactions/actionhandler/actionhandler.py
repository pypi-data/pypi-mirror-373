"""
 2019 Bjoern Annighoefer
"""

#check for all actions in folder


from .action import Action,ActionArg,ActionArgOption
from .job import Job
from ..model.actions import ACTIONS_MODEL_CLASSES

from eoq3.config import Config, EOQ_DEFAULT_CONFIG
from eoq3.logger import GetLoggerInstance
from eoq3.domain import Domain, DomainConnector
from eoq3.concepts import CONCEPTS, MXELEMENT, M1OBJECT, M1ATTRIBUTE 
from eoq3.value import I32, F64, DAT, STR, LST, QRY, NON, EncVal
from eoq3.query import Obj, Qry, Pth, His, Slf, IDX_MODES
from eoq3.command import Cmp, Get, Msg, Cus, Evt, EVT_TYPES, DEL_MODES
from eoq3.serializer import TextSerializer
from eoq3.domainwrappers import MultiprocessingQueueDomainClient, MultiprocessingQueueDomainHost
from eoq3.error import EOQ_ERROR, EOQ_ERROR_DOES_NOT_EXIST
from eoq3.util import Observable

from multiprocessing import Process, Queue
from threading import Thread, Lock, Semaphore
from collections import deque

import sys
import os
import importlib.util
import time
import traceback
from datetime import datetime, timezone

from timeit import default_timer as timer

from typing import List, Dict, Union

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
ACTION_ARG_SERIALIZER = TextSerializer() #must be text serializer, because action call uses the stringify command


class SyncWriteRedirector:
    def __init__(self, stream, domain:Domain, sessionId:str, outputEvtKey:str, bufferTime:float, processLessMode:bool):
        self.stream = stream
        self.domain = domain
        self.sessionId = sessionId
        self.outputEvtKey = outputEvtKey
        self.bufferTime = bufferTime
        self.processLessMode = processLessMode
        #internals
        self.lastWriteTime = time.perf_counter()
        self.buffer = ''
        # IMPORTANT:
        # in processLessMode, the  captured outputs must be stored till the end, 
        # because otherwise an endless loop of printing is created, because all threads 
        # share the same stdout!
        self.postponedMsgs = [] 
        
    def Redirect(self):
        self.legacyWriteFcn = self.stream.write
        self.stream.write = self.write

    def Restore(self):
        self.flush()
        self.stream.write = self.legacyWriteFcn
        if(self.processLessMode):
            #now we can safely forward all collected outputs
            for m in self.postponedMsgs:
                self.domain.Do(Msg(STR(self.outputEvtKey),STR(m)),self.sessionId)
        
    def __ForwardOutput(self,output:str):
        """forward the output to the domain
        """
        if(self.processLessMode):
            self.postponedMsgs.append(output)
        else:
            self.domain.Do(Msg(STR(self.outputEvtKey),STR(output)),self.sessionId)
     
    # with handlers   
    def __enter__(self):
        self.Redirect()
        
    def __exit__(self,exc_type,exc_val,exc_tb):
        self.Restore()
         
    # overwrite stream functions        
    def write(self,data,*args):
            currentWriteTime = time.perf_counter()
            try:
                if(self.legacyWriteFcn):
                    self.legacyWriteFcn(data)
                if(isinstance(data, str) and 0<len(data)):
                    #data = data.encode('utf-8')
                    self.buffer+=data
                    if(currentWriteTime-self.lastWriteTime>self.bufferTime):
                        self.__ForwardOutput(self.buffer)
                        self.buffer = ''
                        self.lastWriteTime = currentWriteTime
            except Exception as e:
                sys.stderr.write(str(e))
    def flush(self):
            try:
                if(0<len(self.buffer)):
                    self.__ForwardOutput(self.buffer)
                    self.buffer = ''
            except:
                pass
        

def JobWorkerProcess(actiondir:str, jobObjStr:str, actionname:str, arguments:list, sessionId:str, outputEvtKey:str, inputEvtKey:str, cmdTxQueue:Queue, cmdRxQueue:Queue, config:Config):
    #restore job
    jobObj = ACTION_ARG_SERIALIZER.DesVal(jobObjStr)
    #restore args
    args = [ACTION_ARG_SERIALIZER.DesVal(a) for a in arguments] #convert the arguments back into python values
    print("Args: %s"%(args)) #DEBUG
    #connect to domain
    domain = MultiprocessingQueueDomainClient(cmdTxQueue, cmdRxQueue, config=config, name="MultiprocessingQueueDomainClient(job: %s, action:%s)"%(jobObj,actionname))
    stdoutRedirector = SyncWriteRedirector(sys.stdout, domain, sessionId, outputEvtKey, 0.0, config.processLessMode)
    stdoutRedirector.Redirect()
    relpathname = actionname+".py"
    pythonfile = os.path.join(actiondir,relpathname)
    pathname, filename = os.path.split(pythonfile)
    actionfunctionname = filename[:-3]
    modulename = actionname
    actionmodulespec = importlib.util.spec_from_file_location(modulename, pythonfile, submodule_search_locations=[pathname])
    sys.path.append(pathname)
    actionmodule = importlib.util.module_from_spec(actionmodulespec)
    actionmodulespec.loader.exec_module(actionmodule)
    actionFunction = getattr(actionmodule,actionfunctionname)
    results = LST([])
    #convert input values
    if(actionFunction):
        #stop the internal benchmark time
        stime = timer()
        finalCallStatus = 'RUNNING'
        try:
            value = actionFunction(domain,*args)
            #see what kind of return value we have
            if( (isinstance(value,list) and
                 not str == type(value)) or
                 tuple == type(value)): #multivalue
                for v in value:
                    results.append(EncVal(v))
            else: #single return value
                results.append(EncVal(value))
            
            finalCallStatus = 'FINISHED'
        except Exception as e:
            traceback.print_exc()#
            results.append(STR(str(e)))
            finalCallStatus = 'FAILED'
        #make sure all output was printed to the domain
        stdoutRedirector.flush()
        stdoutRedirector.Restore()
        # measure the end-point
        duration = F64(timer()-stime)
        end = DAT(datetime.now(LOCAL_TIMEZONE))
        #finally change the call status to FINISHED
        cmd = Cmp().Crt(CONCEPTS.M1ATTRIBUTE,1,['duration',jobObj,duration])\
                   .Crt(CONCEPTS.M1ATTRIBUTE,1,['end',jobObj,end])\
                   .Cus('CCL',[jobObj,finalCallStatus,results])
        domain.Do(cmd,sessionId)
    domain.Close() #stop the event listener thread of the domain
    

class ActionHandler(DomainConnector):
    """The external action handler
    """
    name:str
    basedir:str
    actionsM1Model:QRY
    actionsContainer:QRY               # the model element containing the actions
    actionHandler:QRY                  # the model element for this action handler
    actionRegistry:Dict[str,Action]    # name -> Action
    myJobs:Dict[QRY,Job]
    evtQueue:deque
    evtSignal:Semaphore
    evtQueueLock:Lock
    shallRun:bool = True
    evtListenerThread:Union[None,Thread]


    def __init__(self, basedir:str='actions', handlername:str='eoq3actionhandlerpy', config:Config=EOQ_DEFAULT_CONFIG):
        #constants
        super().__init__(config)
        self.ANNOTATION_ESCAPE_SYMBOLS = [r'\:',r'\[',r'\]',r'\{',r'\}',r"\'",r'\"',r'\\']
        #parameters
        self.basedir = basedir
        self.name = handlername #the name that identifies the actions belonging to this handler
        # initialize internal vars
        self.__Reset()
        self.logger = GetLoggerInstance(config)

    #@Override
    def Connect(self, domain:Domain, sessionId:str=None,)->None:
        """ Connects and synchronizes with a domain.
        """
        super().Connect(domain,sessionId)
        self.__ConnectToDomain()
        self.__ReloadActions()
        self.__StartActionHandling()
        self.SetConnected(True)

    #@Override
    def Disconnect(self)->None:
        """Disconnects the action handler i.e.
        stop all threads, unregister
        """
        if(self.IsConnected()):
            self.__StopActionHandling()
            self.__DisconnectFromDomain()
            super().Disconnect()

    #@Override
    def Close(self):
        """Close the action handler gracefully, i.e.
        stop all threads, unregister and clean-up
        """
        super().Close()

    ### INTERNAL FUNCTIONS ###
        
    def __ConnectToDomain(self):
        """Connects to the domain checks if the actions meta-model is existing.
        If no meta-model is found, it is assumed that no actions manager is present and connect fails.
        Afterward, it registers itself as an action handler in the domain, if a handler with the same name does not exist.
        Otherwise, it reconnects to the existing handler.
        """
        #check if the actions meta-model and container exists
        try:
            cmd = Cmp().Get(Pth(MXELEMENT.MDB).Cls(ACTIONS_MODEL_CLASSES.ACTIONS).Idx(0),resName='container')\
                       .Get(His('container').Pth(M1OBJECT.MODEL),resName='m1model')
            res = self.domain.Do(cmd,self.sessionId,asDict=True)
            self.actionsM1Model = res['m1model']
            self.actionsContainer = res['container']
        except EOQ_ERROR as e:
            raise EOQ_ERROR_DOES_NOT_EXIST('No suitable action manager found in domain: %s'%str(e))
        #open or create the handler for this class
        try:
            cmd = Get(Qry(self.actionsContainer).Pth('handlers*').Sel(Pth(M1OBJECT.NAME).Equ(self.name)).Idx(0))
            self.actionHandler = self.domain.Do(cmd,self.sessionId)
            self.logger.Info('Reconnected to actions handler %s'%(self.actionHandler))
        except EOQ_ERROR: #container does not exist, so create it.
            cmd = Cmp().Crt(CONCEPTS.M1OBJECT,1,[ACTIONS_MODEL_CLASSES.ACTIONHANDLER,self.actionsM1Model,self.name],resName='handler')\
                       .Crt(CONCEPTS.M1COMPOSITION,1,['handlers',self.actionsContainer,His('handler')])
            res = self.domain.Do(cmd,self.sessionId,asDict=True)
            self.actionHandler = res['handler']
            self.logger.Info('Created new action handler %s'%(self.actionHandler))

    def __DisconnectFromDomain(self):
        """Stops the event listener thread and waits for it to finish
        """
        pass #nothing to do here
        
    def __StartActionHandling(self):
        #register featureInstanceservation callback
        self.domain.Observe(self.__OnDomainEvent,self.sessionId,self.sessionId)
        #tell the domain that we are listening
        cmd = Cmp().Obs(EVT_TYPES.CRT)\
                   .Obs(EVT_TYPES.UPD)\
                   .Obs(EVT_TYPES.ELM,self.actionsContainer)#listen to changes or known elements, i.e. the action container
        self.domain.Do(cmd,self.sessionId)
        #start the processing loop
        self.evtListenerThread = Thread(target=self.__EventListenerThread)
        self.evtListenerThread.start()

    def __StopActionHandling(self):
        """Stops the event listener thread and waits for it to finish
        """
        #stop listening to events
        self.domain.Unobserve(self.__OnDomainEvent, self.sessionId, self.sessionId)
        # tell the domain that we are not listening anymore
        cmd = Cmp().Ubs(EVT_TYPES.CRT) \
            .Ubs(EVT_TYPES.UPD) \
            .Ubs(EVT_TYPES.ELM, self.actionsContainer)  # listen to changes or known elements, i.e. the action container
        self.domain.Do(cmd, self.sessionId)
        #stop the event listener thread
        self.shallRun = False
        self.evtListenerThread.join()

    def __OnDomainEvent(self, evts:List[Evt], context:str, source:Observable):
        """' Receives events from the domain and copies the events to the internal 
        dequeue and informs the listener thread to process the events
        """
        self.evtQueueLock.acquire()
        self.evtQueue.appendleft(evts)
        self.evtQueueLock.release()
        self.evtSignal.release()
        
    def __EventListenerThread(self):
        """Continuously looks for new events in the internal event
        and processes them
        """
        while(self.shallRun):
            newEvent = self.evtSignal.acquire(timeout=0.1)
            if(newEvent):
                self.evtQueueLock.acquire()
                evts = self.evtQueue.pop()
                self.evtQueueLock.release()
                #process the event
                for e in evts:
                    self.__ProcessEvent(e)
                    
    def __ProcessEvent(self, e:Evt)->None:
        evtType = e.a[0]
        if(EVT_TYPES.CRT == evtType):
            evtData = e.a[1]
            concept = evtData[2]
            createArgs = evtData[3]
            if(CONCEPTS.M1COMPOSITION == concept):
                if("jobs" == createArgs[0].GetVal() and self.actionsContainer == createArgs[1] ):
                    #a new job was added, retrieve the jobs information
                    self.__HandleNewJob(createArgs[2]) #this is the new job
        elif(EVT_TYPES.UPD == evtType):
            evtData = e.a[1]
            target = evtData[1]
            featureName = evtData[2].GetVal()
            value = evtData[3].GetVal()
            controlFlagInstances = {v.controlFlagInstance:v for v in self.myJobs.values()}
            if(target in controlFlagInstances and M1ATTRIBUTE.VALUE == featureName and 'CANCEL' == value):
                # cancel for a job that executed by me is requested
                job = controlFlagInstances[target]
                self.__AbortJob(job)
            
    def __HandleNewJob(self,jobObj:Obj)->None:
        ##get all information about the job
        cmd = Cmp().Get( Qry(jobObj).Pth('id'),resName='jobid')\
                   .Get( Qry(jobObj).Pth('action'),resName='action')\
                   .Get( Qry(jobObj).Pth('arguments*'),resName='arguments')\
                   .Get( Qry(jobObj).Pth('outputEvtKey'),resName='outputEvtKey')\
                   .Get( Qry(jobObj).Pth('inputEvtKey'),resName='inputEvtKey')\
                   .Get( Qry(jobObj).Pth('owner'),resName='owner')\
                   .Get( Qry(jobObj).Pth('status'),resName='status')\
                   .Get( Qry(jobObj).Pth(M1OBJECT.FEATUREINSTANCES+'status').Idx(0),resName='statusInstance')\
                   .Get( Qry(jobObj).Pth('controlFlag'),resName='controlFlag')\
                   .Get( Qry(jobObj).Pth(M1OBJECT.FEATUREINSTANCES+'controlFlag').Idx(0),resName='controlFlagInstance')\
                   .Obs( EVT_TYPES.ELM, His('controlFlagInstance'))\
                   .Get( Qry(jobObj).Pth('timeout'),resName='timeout')
        res = self.domain.Do(cmd, self.sessionId, asDict=True)
        jobId                = res['jobid'].GetVal()
        actionObj            = res['action']
        arguments            = res['arguments'].GetVal()
        outputEvtKey         = res['outputEvtKey'].GetVal()
        inputEvtKey          = res['inputEvtKey'].GetVal()
        owner                = res['owner'].GetVal()
        status               = res['status'].GetVal()
        statusInstance       = res['statusInstance']
        controlFlag          = res['controlFlag'].GetVal()
        controlFlagInstance  = res['controlFlagInstance'].GetVal()
        timeout              = res['timeout'].GetVal()
        #see if it my action and the job is ready to run
        if(actionObj in self.actionRegistry and 'READY' == status and 'RUN' == controlFlag):
            action = self.actionRegistry[actionObj]
            # try to take the job and mark it as running if I am the first one.
            self.logger.Info("%s called"%(action.name))
            cmd = Cmp().Get(Qry(jobObj).Pth('status'))\
                       .Set(jobObj,'status','RUNNING')
            res = self.domain.Do(cmd, self.sessionId)
            # check if somebody else took the job before
            if('READY' != res[0].GetVal()):
                #status changed in the meantime. Job was either taken by somebody else or canceled
                self.logger.Info("%s is already processed. Skipping request."%(action.name))
            else:
                #this is now my job so create an new internal job handle
                job = Job(jobObj,action,arguments,outputEvtKey,inputEvtKey,timeout,statusInstance,controlFlagInstance)
                self.myJobs[jobObj] = job
                self.__ExecJob(job)
                
    def __ExecJob(self,job:Job)->None:
        self.logger.Info("Executing job %s."%(job.jobObj))
        # add the start timestamp to the domain
        start = DAT(datetime.now(LOCAL_TIMEZONE))
        cmd = Cmp().Set(job.jobObj,'start',start)
        self.domain.Do(cmd,self.sessionId)
        #start the job managing thread
        job.jobMonitorThread = Thread(target=self.__JobMonitorThread, args=(job,))
        job.jobMonitorThread.start()
        
    def __AbortJob(self,job:Job)->None:
        self.logger.Info("Aborting job %s."%(job.jobObj))
        job.Abort()
        if(job.HasStarted()):
            if(self.config.processLessMode):
                pass #threads cannot be killed. Can not do anything here.
            else:
                #kill the process
                job.process.terminate() 
        #update the job status
        start = self.domain.Do(Get(Qry(job.jobObj).Pth('start'))).GetVal()
        end = datetime.now(LOCAL_TIMEZONE) #timezone is important, because values converted from DAT will have a timezone anyhow
        duration = 0.0 if None == start else (end-start).total_seconds()
        #finally change the call status to ABORTED
        results = LST([STR("Aborted by user.")])
        cmd = Cmp().Set(job.jobObj,['duration','end'],[F64(duration),DAT(end)])\
                   .Cus('CCL',[job.jobObj,'ABORTED',results])
        self.domain.Do(cmd,self.sessionId)
                
    
    def __ScanForActions(self)->List[Action]:
        actions = []
    
        #find all python files in the action directory
        pythonfiles = []
        for root, dirs, files in os.walk(self.basedir, topdown=True):
            for file in files:
                if(file.endswith('.%s'%('py'))):
                    #relativeRoot = os.path.relpath(root, self.basedir)
                    #pythonfiles += [os.path.join(relativeRoot,file)] #2: omits the ./ at the beginning
                    pythonfiles += [os.path.join(root,file)] #2: omits the ./ at the beginning
        
        
        for pythonfile in pythonfiles:
            pathname, filename = os.path.split(pythonfile)
            if(os.path.isfile(os.path.join(pathname,'__init__.py'))):
                continue #skip any submodules from beeing loaded as an action
            actionfunctionname = filename[:-3] #without .py
            relpathname = os.path.relpath(pathname, self.basedir)
            modulename = None
            if(relpathname=="."): #it is the root folder
                modulename = actionfunctionname
            else: #any subfolder
                prefixfreepath = relpathname.replace('./','')
                packagename = prefixfreepath.replace('/','.').replace('\\','.')
                modulename = packagename+'.'+actionfunctionname
            actionname = modulename.replace('.','/')
            try: #prevent server crash by broken action scripts
                actionmodulespec = importlib.util.spec_from_file_location(actionfunctionname, pythonfile, submodule_search_locations=[pathname])
                sys.path.append(pathname)
                actionmodule = importlib.util.module_from_spec(actionmodulespec)
                actionmodulespec.loader.exec_module(actionmodule)
                #check for a unique name
                if(actionfunctionname in actions):
                    self.logger.Warn("Found external action %s in file %s, but an action with the same name is already registered from file %s. Action names must be unique!"%(actionname,pythonfile,self._actions[actionname].filepath))
                    continue
                #check if the module contains a function with the same name
                if(actionfunctionname not in actionmodule.__dict__):
                    self.logger.Warn("Skipped no-action %s in %s."%(actionname,pythonfile))
                    continue
                self.logger.Info("Found external action %s in file %s"%(actionname,pythonfile))
                #register the new action 
                
                actionFunction = getattr(actionmodule,actionfunctionname)
                actionArguments = self.__ParseActionArguments(actionname,actionFunction)
                actionResults = self.__ParseActionResults(actionname,actionFunction)
                actionDescription = actionmodule.__doc__
                actionTags = getattr(actionmodule, '__tags__', [])
                if actionTags:
                    self.logger.Info("Action has tags: %s"%(actionTags))
                actionCategory = ""
                action = Action(actionname,actionFunction,actionArguments,actionResults,actionDescription,actionCategory,actionTags)

                actions.append(action)
                #Action(actionname,pythonfile,actionFunction,actionArguments,actionResults,actionDescription)
            except Exception as e:
                self.logger.Error("Error loading external action %s from %s: %s"%(actionname,pythonfile,str(e)))
                traceback.print_exc(file=sys.stdout)
        return actions
            
    def __ParseActionArguments(self,actionName,actionFunction):
        args = []
        nArguments = actionFunction.__code__.co_argcount
        functionVariables = actionFunction.__code__.co_varnames
        actionArguments = functionVariables[0:nArguments]
        actionArgumentTypeInfos = actionFunction.__annotations__
        
        if(nArguments==0):
            self.logger.Warn("Action %s has no argument. Actions must have at least one argument of type Domain."%(actionName))
        else:
            #look for the first argument. This must always be a domain
            argumentName = actionArguments[0]
            argument = None
            if(argumentName not in actionArgumentTypeInfos):
                self.logger.Warn("Argument 1 of action %s is not annotated assuming Domain as type."%(actionName))
            else:
                argumentAnnotation = actionArgumentTypeInfos[argumentName]
                if("Domain"!=argumentAnnotation):
                    self.logger.Warn("Argument 1 of action %s has type %s but expected is %s. This will probably not work."%(actionName,argumentAnnotation,"Domain"))
            #add all args after the first 
            for i in range(1,nArguments):
                argumentName = actionArguments[i]
                argument = None
                if(argumentName not in actionArgumentTypeInfos):
                    self.logger.Warn("Argument %s of action %s has no annotation. Assuming * as type"%(argumentName,actionName))
                    argument = ActionArg(argumentName,'*',1,1,'','',[])
                else:
                    argumentAnnotation = actionArgumentTypeInfos[argumentName]
                    [argumentType, argumentMin, argumentMax, description, default, choices] = self.__ParseArgumentAnnotation(argumentAnnotation)
                    argument = ActionArg(argumentName,argumentType, argumentMin, argumentMax, description, default, choices)
                args.append(argument)
        return args
        
    def __ParseActionResults(self,actionName,actionFunction):
        args = []
        nArguments = actionFunction.__code__.co_argcount
        functionVariables = actionFunction.__code__.co_varnames
        actionArgumentTypeInfos = actionFunction.__annotations__
        
        argumentName = 'return' #'return' is the default key for return annotations in python
        if(argumentName not in actionArgumentTypeInfos):
            self.logger.Warn("Action %s has no return annotation. Assuming no return value"%(actionName))
        else:
            argumentAnnotation = actionArgumentTypeInfos[argumentName]
            if('' != argumentAnnotation):
                [argumentType, argumentMin, argumentMax, description, default, choices] = self.__ParseArgumentAnnotation(argumentAnnotation)
                args.append(ActionArg(argumentName,argumentType, argumentMin, argumentMax, description, default, choices))
        return args
    
    def __MaskEscapeArgumentAnnotation(self,annotation):
        maskedAnnotation = annotation
        for s in self.ANNOTATION_ESCAPE_SYMBOLS:
            maskedAnnotation = maskedAnnotation.replace(s,'x')
        return maskedAnnotation
        
    def __UnescapeArgumentAnnotation(self,annotation):
        
        maskedAnnotation = annotation
        for s in self.ANNOTATION_ESCAPE_SYMBOLS:
            maskedAnnotation = maskedAnnotation.replace(s,s[1])
        return maskedAnnotation
        
        
    def __ParseArgumentAnnotation(self,argumentAnnotation):
        #a annotation should look like this: <Type>[<multiplicity=0..1|*>]{<choice1>',<choice2>,...}=<default>:<Description>
        #all parameters except type are optional
        argumentType = ''
        argumentMin = 1
        argumentMax = 1
        description = ''
        default = ''
        choices = []
        
        #parse string
        nArgumentAnnotation = len(argumentAnnotation)+1
        maskedAnnotation = self.__MaskEscapeArgumentAnnotation(argumentAnnotation) #neglect all escaped symbols
        multiplicityStart = maskedAnnotation.find('[')
        choiceStart = maskedAnnotation.find('{')
        defaultStart = maskedAnnotation.find('=')
        descriptionStart = maskedAnnotation.find(':')
        # remove all escape sequences
        argumentAnnotation = self.__UnescapeArgumentAnnotation(argumentAnnotation)
        
        #multiplicity
        if(multiplicityStart > 0):
            multiplicityEnd = multiplicityStart+argumentAnnotation[multiplicityStart:].find(']')
            if(multiplicityEnd>0 and multiplicityEnd>multiplicityStart):
                multiplicityStr = argumentAnnotation[multiplicityStart+1:multiplicityEnd]
                if('..' in multiplicityStr):
                    multiplicity = multiplicityStr.split('..')
                    if(len(multiplicity)==2):
                        argumentMin = int(multiplicity[0])
                        if('*' == multiplicity[1]):
                            argumentMax = -1
                        else:
                            argumentMax = int(multiplicity[1])
                else:
                    if('*' == multiplicityStr):
                        argumentMin = 0
                        argumentMax = -1
                    else:
                        argumentMin = int(multiplicityStr)
                        argumentMax = int(multiplicityStr)
            else:
                self.logger.Warn("Malformed multiplicity in argument annotation %s"%(argumentAnnotation))

        #choice
        if(choiceStart > 0):
            choiceEnd = choiceStart+argumentAnnotation[choiceStart:].find('}')
            if(choiceEnd>0 and choiceEnd>choiceStart+1): #skip { and }
                choiceStr = argumentAnnotation[choiceStart+1:choiceEnd]
                choices = [ActionArgOption(v,'') for v in choiceStr.split(',')]
            else:
                self.logger.Warn("Malformed choice in argument annotation %s"%(argumentAnnotation))
        #default
        if(defaultStart > 0):
            defaultEnd = min([nArgumentAnnotation,
                              descriptionStart%nArgumentAnnotation])
            if(defaultEnd>0 and defaultEnd>defaultStart+1):
                default = argumentAnnotation[defaultStart+1:defaultEnd] #skip :' and '
            else:
                self.logger.Warn("Malformed default in argument annotation %s"%(argumentAnnotation))

        #description
        if(descriptionStart > 0):
            descriptionEnd = nArgumentAnnotation 
            if(descriptionEnd>0 and descriptionEnd>descriptionStart+1): #skip :
                description = argumentAnnotation[descriptionStart+1:descriptionEnd] #skip :
            else:
                self.logger.Warn("Malformed description in argument annotation %s"%(argumentAnnotation))


        #type
        typeStart = 0
        typeEnd = min([nArgumentAnnotation,
                       multiplicityStart%nArgumentAnnotation,
                       choiceStart%nArgumentAnnotation,
                       defaultStart%nArgumentAnnotation,
                       descriptionStart%nArgumentAnnotation])
        argumentType = argumentAnnotation[typeStart:typeEnd]                 
        return [argumentType, argumentMin, argumentMax, description, default, choices] 
    
    def __UpdateActionRegister(self,actions):
        #clear the local registry
        self.actionRegistry.clear()
        #check which actions are available in the domain and assigned to this handler
        actionsInDomain = self.domain.Do(Get(Qry(self.actionsContainer).Pth('actions*').Zip([Slf(),Pth(M1OBJECT.NAME),Pth('handler'),Pth('tags*').Idx(IDX_MODES.LEN)])),self.sessionId)
        actionsInDomainLut = {a[1].GetVal() : [a[0],a[2],a[3].GetVal(),False] for a in actionsInDomain} # (actionObj, name, handler, tags length)
        #create the update command for the new actions
        cmd = Cmp()
        i = 0;
        #update or create actions
        for a in actions:
            i += 1
            actionId = "a%d"%(i)
            #see if the action is already registered
            if(a.name in actionsInDomainLut):
                existingActionRecord = actionsInDomainLut[a.name]
                existingActionRecord[3] = True #mark this action as processed, all not marked actions will be deleted, i.e. those of this handler that do not exist any more
                if(self.actionHandler == existingActionRecord[1]): #this is my action, update it
                    cmd.Get(existingActionRecord[0],resName=actionId)\
                       .Del(Qry(existingActionRecord[0]).Pth('arguments*'),DEL_MODES.FUL,mute=True)\
                       .Del(Qry(existingActionRecord[0]).Pth('results*'),DEL_MODES.FUL,mute=True)
                    if(0<existingActionRecord[2]):
                        cmd.Del(Qry(existingActionRecord[0]).Pth('tags*'),DEL_MODES.FUL,mute=True)
                    self.logger.Info('Updating action %s.'%(a.name))
                else: #this is not my action, skip it.
                    self.logger.Warn('Action %s is already registered and belongs to another action handler (%s). Skipping.'%(a.name,existingActionRecord[1]))
            else: #create a new record
            #if(None==actionRef):
                cmd.Crt(CONCEPTS.M1OBJECT,1,[ACTIONS_MODEL_CLASSES.ACTION,self.actionsM1Model,a.name],resName=actionId)
                cmd.Crt(CONCEPTS.M1ASSOCIATION,1,['handler',His(actionId),self.actionHandler],mute=True)
                if(a.description): cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['description',His(actionId),a.description],mute=True)
                cmd.Crt(CONCEPTS.M1COMPOSITION,1,['actions',self.actionsContainer,His(actionId)],mute=True)
                self.logger.Info('New action %s.'%(a.name))
            #Update the args and results descriptions
            for t in a.tags:
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['tags',His(actionId),t],mute=True)
            for p in a.args:
                paramId = actionId+'__'+p.name
                #createCmd.Crt(PARAM_CLASS_ID,1,a.)
                cmd.Crt(CONCEPTS.M1OBJECT,1,[ACTIONS_MODEL_CLASSES.ACTIONARGUMENT,self.actionsM1Model,p.name],resName=paramId,mute=True)
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['type',His(paramId),p.type],mute=True)
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['minLen',His(paramId),I32(p.min)],mute=True)
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['maxLen',His(paramId),I32(p.max)],mute=True)
                if(p.description): cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['description',His(paramId),p.description],mute=True)
                cmd.Crt(CONCEPTS.M1COMPOSITION,1,['arguments',His(actionId),His(paramId)],mute=True)
            for r in a.results:
                resId = actionId+'__'+r.name
                cmd.Crt(CONCEPTS.M1OBJECT,1,[ACTIONS_MODEL_CLASSES.ACTIONRESULT,self.actionsM1Model,r.name],resName=resId,mute=True)
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['type',His(resId),r.type],mute=True)
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['minLen',His(resId),I32(r.min)],mute=True)
                cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['maxLen',His(resId),I32(r.max)],mute=True)
                if(r.description): cmd.Crt(CONCEPTS.M1ATTRIBUTE,1,['description',His(resId),r.description],mute=True)
                cmd.Crt(CONCEPTS.M1COMPOSITION,1,['results',His(actionId),His(resId)],mute=True)
        #remove actions that do not exist any more
        for k,v in actionsInDomainLut.items():
            if(not v[3]):
                cmd.Del(v[0],DEL_MODES.FUL,mute=True)     
                self.logger.Info('Removing action %s.'%(k))     
        # TODO: it might be a problem if the actio<n list changes after building the command
        #apply all changes
        res = self.domain.Do(cmd,self.sessionId)
        #build internal registry
        for i in range(len(actions)):
            self.actionRegistry[res[i]] = actions[i]
                
    
    def __ReloadActions(self):
        #scan directory for scripts
        actions = self.__ScanForActions()
        #register all actions
        self.__UpdateActionRegister(actions)
        
    
    def __JobMonitorThread(self, job:Job):
        self.logger.Info("Job %s started."%(job.jobObj))
        jobObjStr = ACTION_ARG_SERIALIZER.SerVal(job.jobObj)
        wasAborted = False
        hasTimeout = job.timeout > 0.0
        #initialize queues for the communication with the subprocess
        cmdTxHostQueue = Queue()
        cmdRxHostQueue = Queue()
        
        domainWrapper = MultiprocessingQueueDomainHost(cmdTxHostQueue, cmdRxHostQueue, self.domain, False, self.config, )
        proc = None
        #start the process but switch the queues to make sure rx and tx complement
        # WARNING: Make sure no non-python-primitive arguments are passed in the following, because these might not be serialized and deserialized well by python!
        if(self.config.processLessMode): #in debug mode no process is created, but the server executed in the same Process
            proc = Thread(name="JobWorker (Thread)", target=JobWorkerProcess, args=(self.basedir, jobObjStr,\
                                                       job.action.name, job.arguments,\
                                                       self.sessionId, job.outputEvtKey, job.inputEvtKey,\
                                                       cmdRxHostQueue, cmdTxHostQueue, self.config, ))
        else:
            proc = Process(name="JobWorker (Process)", target=JobWorkerProcess, args=(self.basedir, jobObjStr,\
                                                       job.action.name, job.arguments,\
                                                       self.sessionId, job.outputEvtKey, job.inputEvtKey,\
                                                       cmdRxHostQueue, cmdTxHostQueue, self.config, ))
        sTime = timer()
    
        if(not job.IsAborted()): #check if the call was aborted before the process was created
            proc.start()
            job.SetStarted(proc,domainWrapper)
          
            while(proc.is_alive()): #wait until the thread has finished
                time.sleep(0.1)
                if(hasTimeout):
                    cTime = timer()
                    pTime = cTime-sTime
                    if(not wasAborted and pTime > job.timeout): 
                        #abort the process if it took to long
                        self.logger.Info('Job %s: Timeout of %f s reached. Aborting.'%(job.jobObj, job.timeout))
                        self.domain.Do(Cus('ABC'),[job.jobObj])
                        wasAborted = True
                
            domainWrapper.Stop()

    def __Reset(self):
        """Resets member variables.
        """
        self.actionsM1Model = NON()
        self.actionsContainer = NON()  # the model element containing the actions
        self.actionHandler = NON()  # the model element for this action handler
        self.actionRegistry = {}  # name -> (action,handlerfunction)
        self.myJobs = {}
        self.evtQueue = deque()
        self.evtSignal = Semaphore(0)
        self.evtQueueLock = Lock()
        self.shallRun = True
        self.evtListenerThread = None