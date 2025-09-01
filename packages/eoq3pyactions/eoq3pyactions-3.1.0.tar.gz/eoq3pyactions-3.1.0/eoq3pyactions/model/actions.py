from eoq3.value import BOL, U32, U64, I64, STR, LST, NON
from eoq3.query import His
from eoq3.command import Cmp

class ACTIONS_MODEL_PACKETS:
    ACTIONS = "https://www.eoq-dsm.org/models/actions"

class ACTIONS_MODEL_CLASSES:
    ACTIONS = "https://www.eoq-dsm.org/models/actions__Actions"
    ACTION = "https://www.eoq-dsm.org/models/actions__Action"
    ACTIONHANDLER = "https://www.eoq-dsm.org/models/actions__ActionHandler"
    JOB = "https://www.eoq-dsm.org/models/actions__Job"
    ACTIONARGUMENTA = "https://www.eoq-dsm.org/models/actions__ActionArgumentA"
    ACTIONARGUMENT = "https://www.eoq-dsm.org/models/actions__ActionArgument"
    ACTIONRESULT = "https://www.eoq-dsm.org/models/actions__ActionResult"
    ACTIONARGUMENTOPTION = "https://www.eoq-dsm.org/models/actions__ActionArgumentOption"

ACTIONS_MODEL_CMD = Cmp()\
    .Crt(STR('*M2MODEL'),U32(1),LST([STR('https://www.eoq-dsm.org/models/actions')]),NON(),LST([]),resName='o0')\
    .Crt(STR('*M2ENUM'),U32(1),LST([STR('JobStatusE'),His(STR('o0'))]),NON(),LST([]),resName='o1')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('READY'),U64(0),His(STR('o1'))]),NON(),LST([]),resName='o2')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('RUNNING'),U64(1),His(STR('o1'))]),NON(),LST([]),resName='o3')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('BLOCKED'),U64(2),His(STR('o1'))]),NON(),LST([]),resName='o4')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('FINISHED'),U64(3),His(STR('o1'))]),NON(),LST([]),resName='o5')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('FAILED'),U64(4),His(STR('o1'))]),NON(),LST([]),resName='o6')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('ABORTED'),U64(5),His(STR('o1'))]),NON(),LST([]),resName='o7')\
    .Crt(STR('*M2ENUM'),U32(1),LST([STR('JobControlFlagE'),His(STR('o0'))]),NON(),LST([]),resName='o8')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('RUN'),U64(0),His(STR('o8'))]),NON(),LST([]),resName='o9')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('PAUSE'),U64(1),His(STR('o8'))]),NON(),LST([]),resName='o10')\
    .Crt(STR('*M2OPTIONOFENUM'),U32(1),LST([STR('CANCEL'),U64(2),His(STR('o8'))]),NON(),LST([]),resName='o11')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('Actions'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o12')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('Action'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o13')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('ActionHandler'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o14')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('Job'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o15')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('ActionArgumentA'),BOL(True),His(STR('o0'))]),NON(),LST([]),resName='o16')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('ActionArgument'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o17')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('ActionResult'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o18')\
    .Crt(STR('*M2CLASS'),U32(1),LST([STR('ActionArgumentOption'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o19')\
    .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('actions'),His(STR('o12')),His(STR('o13')),I64(-1),BOL(False)]),NON(),LST([]),resName='o20')\
    .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('jobs'),His(STR('o12')),His(STR('o15')),I64(-1),BOL(False)]),NON(),LST([]),resName='o21')\
    .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('handlers'),His(STR('o12')),His(STR('o14')),I64(-1),BOL(False)]),NON(),LST([]),resName='o22')\
    .Crt(STR('*M2ASSOCIATION'),U32(1),LST([STR('handler_opp_Action'),His(STR('o13')),I64(-1),STR('handler'),His(STR('o14')),I64(1),BOL(False)]),NON(),LST([]),resName='o23')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('description'),His(STR('o13')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o24')\
    .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('arguments'),His(STR('o13')),His(STR('o17')),I64(-1),BOL(False)]),NON(),LST([]),resName='o25')\
    .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('results'),His(STR('o13')),His(STR('o18')),I64(-1),BOL(False)]),NON(),LST([]),resName='o26')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('tags'),His(STR('o13')),STR('*STR'),I64(-1),NON(),NON()]),NON(),LST([]),resName='o27')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('id'),His(STR('o14')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o28')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('description'),His(STR('o14')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o29')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('id'),His(STR('o15')),STR('*I64'),I64(1),NON(),NON()]),NON(),LST([]),resName='o30')\
    .Crt(STR('*M2ASSOCIATION'),U32(1),LST([STR('action_opp_Job'),His(STR('o15')),I64(-1),STR('action'),His(STR('o13')),I64(1),BOL(False)]),NON(),LST([]),resName='o31')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('arguments'),His(STR('o15')),STR('*STR'),I64(-1),NON(),NON()]),NON(),LST([]),resName='o32')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('results'),His(STR('o15')),STR('*STR'),I64(-1),NON(),NON()]),NON(),LST([]),resName='o33')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('outputEvtKey'),His(STR('o15')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o34')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('inputEvtKey'),His(STR('o15')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o35')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('owner'),His(STR('o15')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o36')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('status'),His(STR('o15')),STR('*ENU'),I64(1),NON(),His(STR('o1'))]),NON(),LST([]),resName='o37')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('controlFlag'),His(STR('o15')),STR('*ENU'),I64(1),NON(),His(STR('o8'))]),NON(),LST([]),resName='o38')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('timeout'),His(STR('o15')),STR('*F64'),I64(1),NON(),NON()]),NON(),LST([]),resName='o39')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('duration'),His(STR('o15')),STR('*F64'),I64(1),NON(),NON()]),NON(),LST([]),resName='o40')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('start'),His(STR('o15')),STR('*DAT'),I64(1),NON(),NON()]),NON(),LST([]),resName='o41')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('end'),His(STR('o15')),STR('*DAT'),I64(1),NON(),NON()]),NON(),LST([]),resName='o42')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('type'),His(STR('o16')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o43')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('minLen'),His(STR('o16')),STR('*I32'),I64(1),NON(),NON()]),NON(),LST([]),resName='o44')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('maxLen'),His(STR('o16')),STR('*I32'),I64(1),NON(),NON()]),NON(),LST([]),resName='o45')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('description'),His(STR('o16')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o46')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('default'),His(STR('o17')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o47')\
    .Crt(STR('*M2ASSOCIATION'),U32(1),LST([STR('options_opp_ActionArgument'),His(STR('o17')),I64(-1),STR('options'),His(STR('o19')),I64(-1),BOL(False)]),NON(),LST([]),resName='o48')\
    .Crt(STR('*M2INHERITANCE'),U32(1),LST([His(STR('o17')),His(STR('o16'))]),NON(),LST([]),resName='o49')\
    .Crt(STR('*M2INHERITANCE'),U32(1),LST([His(STR('o18')),His(STR('o16'))]),NON(),LST([]),resName='o50')\
    .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('value'),His(STR('o19')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o51')