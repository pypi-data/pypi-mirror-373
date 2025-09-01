from ..model.actions import ACTIONS_MODEL_CMD, ACTIONS_MODEL_PACKETS, ACTIONS_MODEL_CLASSES

from eoq3.config import Config,EOQ_DEFAULT_CONFIG
from eoq3.logger import GetLoggerInstance
from eoq3.domain import Domain, DomainConnector
from eoq3.value import BOL, U32, I64, STR, NON, QRY
from eoq3.command import Cmp, Get, Scc, EVT_TYPES
from eoq3.query import Qry, His, Pth
from eoq3.concepts import CONCEPTS, MXMDB, MXELEMENT, M2PACKAGE, M1OBJECT
from eoq3.error import EOQ_ERROR
from eoq3.serializer import TextSerializer

class ActionManager(DomainConnector):
    """A class that extends a domain such that actions handlers
    can be registered, and actions called.
    Adds and actions meta-model to the domain
    Adds and Actions root class to the domain containing all 
    actions and jobs
    Registers action related commands
    """
    actionsM2Model:QRY
    actionsM1Model:QRY
    actionsContainer:QRY

    def __init__(self, config:Config=EOQ_DEFAULT_CONFIG):
        super().__init__(config)
        #internals
        self.__Reset()
        self.logger = GetLoggerInstance(config)
        self.serializer = TextSerializer()
    
    #@Override
    def Connect(self, domain:Domain, sessionId:str=None):
        """Connects to the domain and initializes the actions model.
        Moreover, registers the actions call command, the action abort command and the job close command.

        Args:
        - domain: The domain to connect to
        - sessionId: The session id to use for the connection. If None, no session id will be used.
        """
        super().Connect(domain, sessionId)
        # 1. upload actions meta model
        # check if the actions meta-model is already available
        metamodelExists = False
        cmd = Get(Pth(MXELEMENT.MDB).Pth(MXMDB.M2MODELS).Sel(Pth(M2PACKAGE.NAME).Equ(ACTIONS_MODEL_PACKETS.ACTIONS)))
        res = self.domain.Do(cmd,self.sessionId)
        if(0<len(res)):
            self.actionsM2Model = res[0]
            metamodelExists = True
        if(metamodelExists):
            self.logger.Info('Found actions meta-model.')
        else:
            self.logger.Info('Uploading actions meta-model..')
            self.actionsM2Model = self.domain.Do(ACTIONS_MODEL_CMD,self.sessionId,asDict=True)['o0']
            self.logger.Info('ok')
        #2. obtain or create actions root object
        try:
            cmd = Get(Pth(MXELEMENT.MDB).Cls(ACTIONS_MODEL_CLASSES.ACTIONS).Idx(0))
            self.actionsContainer = self.domain.Do(cmd,self.sessionId)
            self.logger.Info('Reconnected to actions container %s'%(self.actionsContainer))
        except EOQ_ERROR as e: #container does not exist, so create it.
            cmd = Cmp().Crt(CONCEPTS.M1MODEL,1,[self.actionsM2Model,'ActionsM1Model'],resName='m1model')\
                       .Crt(CONCEPTS.M1OBJECT,1,[ACTIONS_MODEL_CLASSES.ACTIONS,His('m1model'),'ActionsContainer'],resName='container')
            res = self.domain.Do(cmd,self.sessionId,asDict=True)
            self.actionsM1Model = res['m1model']
            self.actionsContainer = res['container']
            self.logger.Info('Created new actions container %s'%(self.actionsContainer))
        #3. register the actions call command -> CAL <name>
        self.callCmd = Cmp().Get(Qry(self.actionsContainer).Pth(STR('actions*')).Sel(Pth(STR(M1OBJECT.NAME)).Equ(His(I64(0)))).Idx(I64(0)),mute=True,resName='action')\
                       .Crt(CONCEPTS.M1OBJECT,U32(1),[STR(ACTIONS_MODEL_CLASSES.JOB),self.actionsM1Model,NON()],resName='job')\
                       .Get(Qry(self.actionsContainer).Pth(STR('actions*')).Idx(STR('SIZE')),mute=True,resName='jobid')\
                       .Get(STR('jobout'),mute=True,resName='prefixout').Get(STR('jobin'),mute=True,resName='prefixin')\
                       .Get(His(STR('prefixout')).Add(His(STR('jobid')).Stf(STR('FUL'))),resName='outputEvtKey')\
                       .Get(His(STR('prefixin')).Add(His(STR('jobid')).Stf(STR('FUL'))),resName='inputEvtKey')\
                       .Crt(CONCEPTS.M1ATTRIBUTE,U32(1),[STR('id'),His(STR('job')),His(STR('jobid'))],resName='idInstance')\
                       .Crt(CONCEPTS.M1ASSOCIATION,U32(1),[STR('action'),His(STR('job')),His(STR('action'))],resName='actionInstance')\
                       .Crt(CONCEPTS.M1ATTRIBUTE,U32(1),[STR('outputEvtKey'),His(STR('job')),His(STR('outputEvtKey'))],resName='outEvtKeyInstance')\
                       .Crt(CONCEPTS.M1ATTRIBUTE,U32(1),[STR('inputEvtKey'),His(STR('job')),His(STR('inputEvtKey'))],resName='inEvtKeyInstance')\
                       .Crt(CONCEPTS.M1ATTRIBUTE,U32(1),[STR('status'),His(STR('job')),STR('READY')],resName='statusInstance')\
                       .Crt(CONCEPTS.M1ATTRIBUTE,U32(1),[STR('controlFlag'),His(STR('job')),STR('RUN')],resName='controlFlagInstance')\
                       .Add(His(STR('job')),STR('arguments*'),His(I64(1)).Stf(STR('LST')),mute=True)\
                       .Crt(CONCEPTS.M1COMPOSITION,1,[STR('jobs'),Qry(self.actionsContainer),His(STR('job'))],mute=True)\
                       .Obs(EVT_TYPES.MSG,His('outputEvtKey'))\
                       .Obs(EVT_TYPES.UPD)\
                       .Obs(EVT_TYPES.ELM,His('statusInstance'))
        self.callCmdId = 'CAL' #call
        self.callCmdStr = self.serializer.Ser(self.callCmd)
        cmd = Scc(self.callCmdId, self.callCmdStr)
        self.domain.Do(cmd,self.sessionId)
        #4. register the action abort command -> ABC <job> -> BOL
        self.abortCmd = Cmp().Set(His(0),STR('controlFlag'),STR('CANCEL'),mute=True)\
                             .Get(BOL(True)) #augment a true return value
        self.abortCmdId = 'ABC' #abort call
        self.abortCmdStr = self.serializer.Ser(self.abortCmd)
        cmd = Scc(self.abortCmdId, self.abortCmdStr)
        self.domain.Do(cmd,self.sessionId)
        #5. register the job close command -> CCL <job> <status> [<results*>,...] -> BOL
        self.closeCallCmd = Cmp().Add(His(I64(0)),STR('results*'),His(I64(2)).Stf(STR('LST')),mute=True)\
                       .Set(His(I64(0)),STR('status'),His(I64(1)),mute=True)\
                       .Ubs(EVT_TYPES.ELM,His(I64(0)).Pth(STR(M1OBJECT.FEATUREINSTANCES+'controlFlag')))\
                       .Get(BOL(True)) #augment a true return value
        self.closeCallCmdId = 'CCL' #close call
        self.closeCallCmdStr = self.serializer.Ser(self.closeCallCmd)
        cmd = Scc(self.closeCallCmdId, self.closeCallCmdStr)
        self.domain.Do(cmd,self.sessionId)
        #5. observe job changes? #necessary?
        # might clean up jobs after a certain duration?
        self.SetConnected(True)

    #@Override
    def Disconnect(self) ->None:
        """Disconnects from the domain and cleans up the actions model.
        """
        if(self.IsConnected()):
            self.__Reset()
            super().Disconnect()

    #@Override
    def Close(self):
        super().Close() #no clean-up: keep the actions model in the MDB


    ### INTERNALS ###

    def __Reset(self):
        """Resets member variables.
        """
        self.actionsM2Model = NON()
        self.actionsM1Model = NON()
        self.actionsContainer = NON()
        