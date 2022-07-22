import asyncio
import concurrent.futures

import sniffio


def __init__(hub):
    hub.loop.init.BACKEND = None


def get(hub) -> asyncio.AbstractEventLoop:
    """
    Reliably get an active loop
    """
    if hub.pop.loop.CURRENT_LOOP is None:
        if hub.loop.init.BACKEND and hub.loop.init.BACKEND != "init":
            hub.pop.loop.CURRENT_LOOP = hub.loop[hub.loop.init.BACKEND].get()
        else:
            hub.pop.loop.CURRENT_LOOP = asyncio.get_event_loop()

    return hub.pop.loop.CURRENT_LOOP


def policy(hub):
    if hub.loop.init.BACKEND:
        return hub.loop[hub.loop.init.BACKEND].policy()


def executor(hub):
    if hub.loop.init.BACKEND:
        return hub.loop[hub.loop.init.BACKEND].executor()
    return concurrent.futures.ThreadPoolExecutor(thread_name_prefix="pop-loop-init")


def create(hub, loop_plugin: str = None):
    """
    Create the event loop with the named plugin

    :param hub:
    :param loop_plugin: The pop-loop plugin to use for the async loop backend
    """
    # Automatically determine which backend to use
    # Use the named plugin to set up the loop
    if loop_plugin is None:
        loop_plugin = "auto"
    hub.pop.loop.POLICY = hub.loop[loop_plugin].policy()
    try:
        asyncio.set_event_loop_policy(hub.pop.loop.POLICY)
    except AssertionError as e:
        hub.log.debug(f"Could not set event loop policy: {e}")
    if loop_plugin == "init":
        hub.pop.loop.CURRENT_LOOP = asyncio.new_event_loop()
    else:
        hub.pop.loop.CURRENT_LOOP = hub.loop[loop_plugin].get()
    asyncio.set_event_loop(hub.pop.loop.CURRENT_LOOP)
    hub.pop.loop.EXECUTOR = hub.loop[loop_plugin].executor()
    hub.loop.init.BACKEND = loop_plugin


def backend(hub) -> str:
    """
    Determine the async library backend for the current loop
    """

    async def _backend():
        # An asynchronous context for sniffio to use
        return sniffio.current_async_library()

    try:
        # Run the sniffio function with the current loop
        return hub.pop.Loop.run_until_complete(_backend())
    except Exception as e:
        hub.log.debug(f"Unable to detect aio backend: {e}")
        return "unknown"
