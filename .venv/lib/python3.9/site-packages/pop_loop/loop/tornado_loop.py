"""
WARNING! This is untested
"""
try:
    import tornado.ioloop
    import tornado.platform.asyncio

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)

__virtualname__ = "tornado"


def __virtual__(hub):
    return HAS_LIBS


def get(hub):
    return tornado.ioloop.IOLoop()


def policy(hub):
    return tornado.platform.asyncio.AnyThreadEventLoopPolicy()


def executor(hub):
    ...
