import logging


def f(a, *args):
    print(locals())


def f0():
    """ a function no args """
    print('f0')
    d = dict(locals())
    for x in d:
        print('\t', x, d[x])


def f1(a, b=1):
    """ another function, lots of args """
    print('f1')
    d = dict(locals())
    for x in d:
        print('\t', x, d[x])


def f2(c, a=1, b=1, **kwargs):
    """ yet another function """
    print('f2')
    d = dict(locals())
    for x in d:
        print('\t', x, d[x])


def f3(a: 'first arg', aa: 'second arg', *args: 'other args', b: 'b variable'=3, **kwargs):
    """ one last one """
    print('f3')
    d = dict(locals())
    for x in d:
        print('\t', x, d[x])
