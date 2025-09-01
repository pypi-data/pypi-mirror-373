# eoq3pyecoremdb - action handler and python actions for EOQ3

Actions are scripts to be applied on elements of a domain. 
The application is triggered throug the domain and script execution can be remote.
Actions might be parameterized to configure their targets and/or execution.

This comprises action handler and action manager. Per domain one action manager and several action handlers can be instantiated.

* action manager: extends the domain by an action model as well as commands to call and abort actions.
* action handler: registers local python scripts as actions in the actions manager and listens to execution requests.
		
## Usage

### API

Imports:

    from eoq3pyactions.actionhandler import ActionHandler
    from eoq3pyactions.actionmanager import ActionManager
    from eoq3pyactions.util import *

Create and connect an action manager:

    amaSessionId = GenerateSessionId() #action manager
    domain.Do(Hel('actionmanager','xxx'),amaSessionId)
    ama = ActionManager(config)
    ama.Connect(domain, amaSessionId)
	
Create and connect an action handler:

	ahaSessionId = GenerateSessionId() #action handler
    domain.Do(Hel('actionhandler','xxx'),ahaSessionId) 
    aha = ActionHandler(basedir=ACTIONS_DIR)
    aha.Connect(domain,ahaSessionId)
	
Call an action and retrieve the results (for the action itself, see example action below):

    res = domain.Do( Cus('CAL',['Misc/helloworld',[1]]) ,asDict=True)
    job = res['job']
    #wait for action to finish
    sleep(1.0) #make sure action has finished
    #check result 
	res = domain.Do( Get( Qry(job).Pth('results*').Idx(0) ) )
	# res should be STR("I printed 1 times Hello world!")
	
Alternative ways to call actions:

	#action call by util funciton and wait seperate
	res = CallAction(domain,sessionId,'helloworld',[1])
    job = res['job']
	jobStatus = res['statusInstance']
	WaitForAction(domain,sessionId,job,jobStatus,10.0)
	#call and wait with one helper
	CallActionAndWait(domain,sessionId,'helloworld',[],10.0)
	
See also Test/Eoq3/test_eoq3pyactions.py.
	
### Example action

This must reside as in ACTIONS_DIR:

    __tags__ = ['misc','test'] #classification tags to be used in clients #tags are optional
    
    def helloworld(domain : 'Domain', times : 'I64=2')->'STR':
        t = times.GetVal()
        for i in range(t):
            print("Hello world!",end='')
        return "I printed %d times Hello world!"%(t)
	
## Implementation

Large parts of the wrapper between pyecore an EOQ3 are generated from the concepts generation. To regenerate use:

    gen/generatepyecoremdb.py

## Documentation

For more information see EOQ3 documentation: https://eoq.gitlab.io/doc/eoq3/

## Author

2024 Bjoern Annighoefer
