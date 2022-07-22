"""
WARNING! This is untested
"""
import asyncio
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Optional

try:
    import curio

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


__virtualname__ = "curio"


def get(hub):
    return CurioLoop()


def policy(hub):
    return asyncio.unix_events.DefaultEventLoopPolicy()


def executor(hub):
    ...


class CurioLoop(asyncio.AbstractEventLoop):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._kernel = curio.Kernel(*args, **kwargs)

    def run_until_complete(self, future):
        self._kernel.run(corofunc=future)

    def stop(self) -> None:
        self._kernel.run(shutdown=True)

    def is_running(self) -> bool:
        return self._kernel._runner is not None

    def is_closed(self) -> bool:
        return self._kernel._runner is None

    def close(self) -> None:
        self._kernel.run(shutdown=True)

    def create_task(self, coro, *, name: Optional[str] = ...):
        return curio.spawn(coro)

    def run_in_executor(self, executor_: Any, func: Callable, *args: Any) -> Awaitable:
        return curio.run_in_executor(executor_, func, *args)
