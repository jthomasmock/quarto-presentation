import os

try:
    import asyncio.windows_events

    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

__virtualname__ = "proactor"


def __virtual__(hub):
    if os.name == "nt" and HAS_LIBS:
        return (True,)
    else:
        return False, "WindowsProactorEventLoop only runs on windows"


def get(hub):
    # The default event loop on Windows, "SelectorEventLoop" has certain limitations
    # ProactorEventLoop makes use of Window's I/O Completion Ports:
    #   https://docs.microsoft.com/en-ca/windows/win32/fileio/i-o-completion-ports
    return asyncio.windows_events.ProactorEventLoop()


def policy(hub):
    return asyncio.windows_events.WindowsProactorEventLoopPolicy()


def executor(hub):
    ...
