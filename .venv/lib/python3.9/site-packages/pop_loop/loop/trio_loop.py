import asyncio

try:
    import trio_asyncio._loop

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)

__virtualname__ = "trio"


def __virtual__(hub):
    return HAS_LIBS


def get(hub):
    trio_asyncio.open_loop()
    return asyncio.new_event_loop()


def policy(hub):
    ...


def executor(hub):
    return trio_asyncio.TrioExecutor()
