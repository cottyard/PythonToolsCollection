import sys
from inspect import getargspec

def enter(func):
    default_args = len(getargspec(func).defaults)
    arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
    if len(sys.argv) < len(arg_names) - default_args + 1:
        print "arguments: " + ' '.join(arg_names)
        sys.exit(1)
    func(*sys.argv[1:])
