"""
WARNING! This is untested
"""
try:
    from twisted.internet import asyncioreactor

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __init__(hub):
    hub.loop.twisted.REACTOR = None


def __virtual__(hub):
    return HAS_LIBS


__virtualname__ = "twisted"


def get(hub):
    loop = asyncioreactor.SelectorEventLoop()
    hub.loop.twisted.REACTOR = asyncioreactor.AsyncioSelectorReactor(eventloop=loop)
    return loop


def policy(hub):
    ...


def executor(hub):
    ...
