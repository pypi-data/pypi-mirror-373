'''
 2019 Bjoern Annighoefer
'''

from eoq3.value import VAL, NON, LST
from eoq3.query import Qry, Obj
from eoq3.command import Cmp, Get, Cus, EVT_TYPES
from eoq3.error import EOQ_ERROR_RUNTIME
from eoq3.domain import Domain
from eoq3.concepts import M1ATTRIBUTE
from eoq3.util import GenerateSessionId
from eoq3.serializer import TextSerializer

from threading import Semaphore
#type annotation
from typing import Dict, Any

RESULTS_SERIALIZER = TextSerializer()


def ShowProgress(progress):
    print('Total progress: %d%%'%(int(progress)))
    return

def WaitForAction(domain:Domain, sessionId:str, job:Obj, jobStatusAttr:Obj, timeout:float=None)->bool:
    '''Waits until the job status changes to FINISH, FAILED or CANCELED
    timeout=None blocks to infinity
    
    WARNING: this requires that UPD events are observed for the session
    '''
    JOB_END_STATES = ['FINISHED','FAILED','ABORTED']
    isJobFinished = False
    finishSignal = Semaphore(0)
    def LocalOnDomainEvent(evts:list, context:str, sourceSessionId:str)->None:
        for e in evts:
            evtType = e.a[0]
            if(EVT_TYPES.UPD == evtType):
                evtData = e.a[1]
                target = evtData[1]
                featureName = evtData[2]
                value = evtData[3]
                if(jobStatusAttr == target and M1ATTRIBUTE.VALUE == featureName and value in JOB_END_STATES ):
                    #a new job was added, retrieve the jobs information
                    finishSignal.release() #signal the semaphore such that the main thread can continue
    #add the new event listener to the domain
    context = GenerateSessionId() #create a random context
    domain.Observe(LocalOnDomainEvent, context, sessionId)
    #check if the job is still running 
    state = domain.Do(Get(Qry(job).Pth('status'))).GetVal()
    if(state in JOB_END_STATES):
        isJobFinished = True
    else: #if the job has not finished so far, wait for the job to return
        signalReceived = finishSignal.acquire(timeout=timeout)
        if(signalReceived):
            isJobFinished =  True
    #clean up
    domain.Unobserve(LocalOnDomainEvent, context, sessionId)
    return isJobFinished

def CallAction(domain:Domain, sessionId:str, actionName:str, args:list=[])->Dict[str,Any]:
    ''' Starts an action
    
    Returns: 
    if successful returns a dict with the following fields
    - job:Obj: Handler to the job element
    - outputEvtKey:STR: MSG event key for job outputs 
    - inputEvtKey:STR: MSG event key for job inputs 
    - idInstance:Obj: Handler to the job id attribute
    - actionInstance:Obj: Handler to the job instance attribute
    - outEvtKeyInstance:Obj: Handler to the job output EvtKey attribute
    - inEvtKeyInstance:Obj: Handler to the job inputEvtKey attribute
    - statusInstance:Obj: Handler to the job status attribute
    - controlFlagInstance: Obj: Handler to the job controlFlag attribute
    '''
    cmd = Cus('CAL',[actionName,args])
    res = domain.Do(cmd,sessionId,asDict=True)
    return res

def CallActionAndWait(domain:Domain, sessionId:str, actionName:str, args:list=[], timeout:float=None)->VAL:
    ''' Starts an action and waits until it is finished or the timeout occures
    timeout=None blocks to infinity
    
    WARNING: this requires that UPD events are observed for the session
    '''
    results = NON()
    res = CallAction(domain,sessionId,actionName,args)
    job = res['job']
    statusInstance = res['statusInstance']
    isJobFinished = WaitForAction(domain,sessionId,job,statusInstance,timeout)
    if(isJobFinished):
        cmd = Cmp().Get(Qry(job).Pth('results*'), resName="results")\
                   .Get(Qry(job).Pth('status'), resName="status")
        res = domain.Do(cmd,sessionId,asDict=True)
        results = LST([RESULTS_SERIALIZER.DesVal(r.GetVal()) for r in res['results']]) 
        status = res['status']
        if(status != "FINISHED"):
            raise EOQ_ERROR_RUNTIME("Job failed or was canceled: %s"%(results[0])) #the first result should be the error message
    else:
        raise EOQ_ERROR_RUNTIME("Timeout")
    return results

def AbortAction(domain:Domain, sessionId:str, job:Obj)->None:
    ''' Stops a running action.
    '''
    cmd = Cus('ABC',[job])
    domain.Do(cmd,sessionId)

def GetActionResults(domain:Domain, sessionId:str, job:Obj)->LST:
    ''' Returns the results of a job as VAL types.
    '''
    cmd = Get( Qry(job).Pth('results*'))
    res = domain.Do(cmd,sessionId)
    results = LST([RESULTS_SERIALIZER.DesVal(r.GetVal()) for r in res]) 
    return results


def UiMessageGeneric(state,*args):
    """ prints generalized messages that can be parsed by the UI """
    print('[{state}]'.format(state=state),*args)


def UiShowProgress(progress):
    """ Displays current progress """
    UiMessageGeneric('progress','{progress}%'.format(progress=round(progress)))


def ShowCalculatedProgress(index,target,startPercentage=0,targetPercentage=100,incrementer=1):
    """ Displays calculated process """
    return UiShowProgress(startPercentage + (index + incrementer) / target * (targetPercentage - startPercentage))


def UiStartTask(taskName):
    """ Indicates task start """
    UiMessageGeneric('Started Task',taskName)


def UiEndTask(taskName):
    """ Indicated task end """
    UiMessageGeneric('Ended Task',taskName)


def UiAnnounceTasks(taskNum):
    """ Indicated how many tasks are to be expected """
    UiMessageGeneric('Announced Tasks',taskNum)


def UiMessageInfo(*args):
    """ Indicates an info message """
    UiMessageGeneric('INFO',*args)


def UiMessageError(*args):
    """ Indicates an error message """
    UiMessageGeneric('ERROR',*args)


def UiMessageWarning(*args):
    """ Indicates a warning message """
    UiMessageGeneric('WARNING',*args)


def UiMessageSuccess(*args):
    """ Indicates a success message """
    UiMessageGeneric('SUCCESS',*args)


def UiItemSaved(*args):
    """ Indicates a saved-event """
    UiMessageGeneric('SAVED',*args)


def UiItemDeleted(*args):
    """ Indicates a deleted-event """
    UiMessageGeneric('DELETED',*args)


def UiItemChanged(*args):
    """ Indicates a changed-event """
    UiMessageGeneric('CHANGED',*args)


def UiItemCreated(*args):
    """ Indicates a created-event """
    UiMessageGeneric('CREATED',*args)


def UiItemLoaded(*args):
    """ Indicates a loaded-event """
    UiMessageGeneric('LOADED',*args)


def UiItemFound(*args):
    """ Indicates a found-event """
    UiMessageGeneric('FOUND',*args)
