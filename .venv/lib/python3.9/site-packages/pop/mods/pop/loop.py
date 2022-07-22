"""
The main interface for management of the aio loop
"""
import asyncio
import signal
from typing import Any
from typing import AsyncGenerator
from typing import Callable
from typing import Coroutine
from typing import Iterable

import lazy_object_proxy

import pop.contract
import pop.hub

__virtualname__ = "loop"


def __init__(hub):
    hub.pop.loop.FUT_QUE = None
    hub.pop.loop.CURRENT_LOOP = None
    hub.pop.loop.EXECUTOR = None
    hub.pop.loop.POLICY = None
    hub.pop.sub.add(dyne_name="loop")
    hub.pop.Loop = lazy_object_proxy.Proxy(hub.loop.init.get)


def create(hub, loop_plugin: str = None):
    """
    Call the pop-loop dyne for creating the event loop.
    This is an idempotent operation.

    :param hub:
    :param loop_plugin: The plugin from pop-loop to use to initialize the loop
    """
    if not hub.pop.loop.CURRENT_LOOP:
        hub.loop.init.create(loop_plugin)


def call_soon(hub: "pop.hub.Hub", ref: str, *args, **kwargs):
    """
    Schedule a coroutine to be called when the loop has time. This needs
    to be called after the creation of the loop
    """
    coro = hub.pop.loop.wrap(hub[ref], *args, **kwargs)
    return hub.pop.loop.CURRENT_LOOP.call_soon(hub.pop.loop.unwrap, coro)


def ensure_future(hub: "pop.hub.Hub", ref: str, *args, **kwargs) -> asyncio.Future:
    """
    Schedule a coroutine to be called when the loop has time. This needs
    to be called after the creation of the loop. This function also uses
    the hold system to await the future when it is done making it easy
    to create a future that will be cleanly awaited in the background.
    """
    future = asyncio.ensure_future(hub[ref](*args, **kwargs))

    if hub.pop.loop.FUT_QUE is None:
        raise RuntimeError(
            "Run 'await hub.pop.loop.init_futures()' to create the futures queue in the proper loop"
        )

    def callback(fut):
        hub.pop.loop.FUT_QUE.put_nowait(fut)

    future.add_done_callback(callback)
    return future


async def init_futures(hub):
    if hub.pop.loop.FUT_QUE is None:
        hub.pop.loop.FUT_QUE = asyncio.Queue()


def start(
    hub: "pop.hub.Hub",
    *coros,
    hold: bool = False,
    sigint: Callable = None,
    sigterm: Callable = None,
    loop_plugin: asyncio.AbstractEventLoop = None,
) -> Any:
    """
    Start a loop that will run until complete
    """
    hub.pop.loop.create(loop_plugin=loop_plugin)
    loop: asyncio.AbstractEventLoop = hub.pop.loop.CURRENT_LOOP

    if sigint:
        s = signal.SIGINT
        loop.add_signal_handler(s, lambda s=s: loop.create_task(sigint(s)))
    if sigterm:
        s = signal.SIGTERM
        loop.add_signal_handler(s, lambda s=s: loop.create_task(sigterm(s)))
    if hold:
        coros = list(coros)
        coros.append(_holder(hub))

    try:
        # DO NOT CHANGE THIS CALL TO run_forever! If we do that then the tracebacks
        # do not get resolved.
        return loop.run_until_complete(asyncio.gather(*coros))
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling...")
    finally:
        loop.close()


async def _holder(hub):
    """
    Just a sleeping while loop to hold the loop open while it runs until
    complete
    """
    if hub.pop.loop.FUT_QUE is None:
        hub.pop.loop.FUT_QUE = asyncio.Queue()

    while True:
        future = await hub.pop.loop.FUT_QUE.get()
        await future


async def await_futures(hub: "pop.hub.Hub"):
    """
    Scan over the futures that have completed and manually await them.
    This function is used to clean up futures when the loop is not opened
    up with hold=True so that ensured futures can be cleaned up on demand
    """
    if hub.pop.loop.FUT_QUE is None:
        hub.pop.loop.FUT_QUE = asyncio.Queue()

    while not hub.pop.loop.FUT_QUE.empty():
        future = await hub.pop.loop.FUT_QUE.get()
        await future


async def kill(hub: "pop.hub.Hub", wait: int or float = 0):
    """
    Close out the loop
    """
    await asyncio.sleep(wait)
    hub.pop.loop.CURRENT_LOOP.stop()
    while True:
        if hub.pop.loop.CURRENT_LOOP is not None:
            if not hub.pop.loop.CURRENT_LOOP.is_running():
                hub.pop.loop.CURRENT_LOOP.close()
                hub.pop.loop.CURRENT_LOOP = None
            else:
                await asyncio.sleep(1)


# Helpers for async operations


async def as_yielded(
    hub: "pop.hub.Hub", gens: Iterable[AsyncGenerator]
) -> AsyncGenerator:
    """
    Concurrently run multiple async generators and yield the next yielded
    value from the soonest yielded generator.

    async def many():
        for n in range(10):
            yield os.urandom(6).hex()

    async def run():
        gens = []
        for n in range(10):
            gens.append(many())
        async for y in as_yielded(gens):
            print(y)
    """
    fin = object()
    que = asyncio.Queue()
    to_clean = []

    async def _yield(agen: AsyncGenerator):
        async for comp in agen:
            await que.put(comp)

    async def _ensure(coroutines: Iterable[Coroutine]):
        for f in asyncio.as_completed(coroutines):
            await f

    async def _set_done():
        await que.put(fin)

    def _done(future: asyncio.Future):
        to_clean.append(asyncio.ensure_future(_set_done()))

    coros = []
    for gen in gens:
        coros.append(_yield(gen))

    fut = asyncio.ensure_future(_ensure(coros))
    fut.add_done_callback(_done)

    while True:
        ret = await que.get()
        if ret is fin:
            break
        yield ret
    for c in to_clean:
        await c


async def sleep(hub, delay: float, *args, **kwargs):
    await asyncio.sleep(delay, *args, **kwargs)


async def wrap(
    hub: "pop.hub.Hub",
    synchronous_function: Callable,
    *args,
    **kwargs,
):
    """
    Run a synchronous function asynchronously

    :param hub:
    :param synchronous_function: The function to wrap
    """
    return await hub.pop.loop.CURRENT_LOOP.run_in_executor(
        executor=hub.pop.loop.EXECUTOR,
        func=pop.contract.Partial(synchronous_function, *args, **kwargs),
    )


async def unwrap(hub, function_ret: Coroutine or Any):
    """
    Take the return of a function, if it is awaitable, await it.
    Return the result

    :param hub:
    :param function_ret: The return from a possibly asynchronous function
    """
    while asyncio.iscoroutine(function_ret):
        function_ret = await function_ret
    return function_ret
