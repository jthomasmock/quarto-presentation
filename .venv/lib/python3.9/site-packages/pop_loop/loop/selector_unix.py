__virtualname__ = "selector"

try:
    import asyncio.unix_events

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def get(hub):
    return asyncio.unix_events.SelectorEventLoop()


def policy(hub):
    return asyncio.unix_events.DefaultEventLoopPolicy()


def executor(hub):
    ...
