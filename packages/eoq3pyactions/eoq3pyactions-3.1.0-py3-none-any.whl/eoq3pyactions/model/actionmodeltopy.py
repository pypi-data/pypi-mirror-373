from eoq3pyecoreutils.pyecoretoeoq import EcoreFileToCmd
from eoq3.serializer import TextSerializer, PySerializer


if __name__ == "__main__":
    infile = 'actions.ecore'
    outfile = 'actions.py'
    
    prefix = 'ACTIONS_MODEL'
    
    
    serializer = PySerializer()
    
    (cmd,pkgIds,clsIds) = EcoreFileToCmd(infile)
    
    
    with open(outfile, 'w') as f:
        f.write('from eoq3.value import BOL, U32, U64, I64, STR, LST, NON\n')
        f.write('from eoq3.query import His\n')
        f.write('from eoq3.command import Cmp\n')
        #write package list
        f.write('\n')
        f.write('class %s_PACKETS:\n'%(prefix))
        for k,v in pkgIds.items():
            f.write('    %s = "%s"\n'%(k.upper(),v))
        #write class list
        f.write('\n')
        f.write('class %s_CLASSES:\n'%(prefix))
        for k,v in clsIds.items():
            f.write('    %s = "%s"\n'%(k.upper(),v))
        #write model creation command
        f.write('\n')
        f.write('%s_CMD = Cmp()'%(prefix))
        for c in cmd.a:
            f.write('\\\n')
            cmdStr = serializer.SerCmd(c)
            f.write('    .%s'%(cmdStr))
            #f.write('ACTIONS_MODEL = Cmp()')