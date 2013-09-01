#!/usr/bin/env python3
import os
import sys
import inspect
import cli.log
import importlib
import site
import re
import logging


def main():
    stripped_argv = [x for x in sys.argv if not x.startswith('-')]
    other_argv = [x for x in sys.argv if x not in stripped_argv]
    if len(stripped_argv) < 2:
        print('usage: clirun.py module.py ...')
        sys.exit(1)
    fullModName = stripped_argv[1]
    modPath = os.path.dirname(fullModName)
    modName = re.sub('.py$', '', os.path.basename(fullModName))
    site.addsitedir(modPath)
    module = importlib.import_module(modName)
    funs = inspect.getmembers(module, inspect.isfunction)
    if len(stripped_argv) == 2:
        print(usage(funs))
        sys.exit(1)

    fname = stripped_argv[2]
    sys.argv = stripped_argv[2:] + other_argv  # shift but be careful with the options
    # funs is a list of (func_name, func_ref) tuples
    funs = [x for x in funs if not x[0].startswith('_')]

    try:
        fref = dict(funs)[fname]
    except KeyError as e:
        sys.stderr.write("No function %s in module %s\n" % (fname, fullModName))
        print(usage(funs))
        sys.exit(1)

    argspec = inspect.getfullargspec(fref)

    parse_known = False
    if argspec.varkw is not None:
        parse_known = True

    @cli.log.LoggingApp(parse_known=parse_known)
    def prog(app):
        args = []
        kwargs = dict()

        if argspec.args is not None:
            for x in argspec.args:
                args += [app.params.__dict__[x]]
        if argspec.varargs is not None:
            args += app.params.__dict__[argspec.varargs]
        if argspec.kwonlydefaults is not None:
            for x in argspec.kwonlydefaults:
                kwargs[x] = argspec.kwonlydefaults[x]

        def parseArgs(kws):
            """ parse_known_args returns a raw string ... need to deal with it """
            args = [x for x in kws if not x.startswith('-')]
            kws = [x for x in kws if x.startswith('-')]
            kws = [x.lstrip('-') for x in kws]
            kws = [x.split('=') for x in kws]
            kws = [(x[0], '='.join(x[1:])) for x in kws]
            kws = dict(kws)
            return(args, kws)

        if argspec.varkw is not None:
            newArgs, newKW = parseArgs(argspec.varkw)
            kwargs.update(newKW)

        logging.info("Calling %s with args %s and kwargs %s" % (fname, args, kwargs))
        fref(*args, **kwargs)

    # optional arguments that are passed in as positions argument with default values if it is possible
    # (i.e. if no *args is present)
    defaults = [None] * len(argspec.args)
    if argspec.defaults is not None:
        defaults = list(argspec.defaults)
        defaults = [None] * (len(argspec.args) - len(defaults)) + defaults
    for x, default in zip(argspec.args, defaults):
        prog.add_param(x, help=argspec.annotations.get(x, 'no help'), default=default, nargs=None if default is None else '?')
    if argspec.varargs is not None:
        prog.add_param(argspec.varargs, help=argspec.annotations.get(argspec.varargs, 'no help'), nargs='*')
    for x in argspec.kwonlyargs:
        prog.add_param('--%s' % x, help=argspec.annotations.get(x, 'no help'), default=argspec.kwonlydefaults[x])
    if argspec.varkw is not None:
        prog.add_param('--kwargs', help="Will parse any optional arguments from the command line and pass as **kwargs to function.", default=None)

    prog.run()


def usage(funs):
    lines = ''
    lines += 'Available commands:\n'
    rows = [(fname, fref.__doc__) for fname, fref in funs]
    for row in rows:
        lines += '\t%s: %s\n' % row
    return(lines)

if __name__ == '__main__':
    main()
