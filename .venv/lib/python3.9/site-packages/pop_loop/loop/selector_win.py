import os

try:
    import asyncio.windows_events

    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

__virtualname__ = "selector"


def __virtual__(hub):
    if os.name == "nt" and HAS_LIBS:
        return (True,)
    else:
        return False, "WindowsSelectorEventLoop only runs on windows"


def get(hub):
    return asyncio.windows_events.SelectorEventLoop()


def policy(hub):
    return asyncio.windows_events.DefaultEventLoopPolicy()


def executor(hub):
    ...
