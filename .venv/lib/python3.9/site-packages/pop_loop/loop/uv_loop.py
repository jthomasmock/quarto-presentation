try:
    import uvloop

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)

__virtualname__ = "uv"


def __virtual__(hub):
    return HAS_LIBS


def get(hub):
    return uvloop.new_event_loop()


def policy(hub):
    return uvloop.EventLoopPolicy()


def executor(hub):
    ...
