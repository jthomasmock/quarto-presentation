import asyncio
import inspect
import sys

import pop.contract

try:
    import aiologger
    import aiologger.handlers.streams
    import aiologger.handlers.files
    import aiologger.handlers.base
    import aiologger.levels
    import aiologger.formatters.base
    import aiologger.records

    HAS_AIOLOGGER = (True,)
except ImportError as e:
    HAS_AIOLOGGER = False, str(e)


def __init__(hub):
    hub.log.LOGGER = {}
    hub.log.FILE_HANDLER = None
    hub.log.STREAM_HANDLER = None


def __virtual__(hub):
    return HAS_AIOLOGGER


def _stack_frames(relative_start: int) -> inspect.FrameInfo:
    """
    Efficiently access stack frames.
    :param relative_start: Starting stack depth; The default, 2 is the parent of the
                           caller of stack_frames - the first function that may be unknown.
    :return: a stack frame
    """
    if hasattr(sys, "_getframe"):
        # implementation detail of CPython, speeds things up by 100x.
        frame = sys._getframe(relative_start)
        while frame:
            yield frame
            frame = frame.f_back
    else:
        for frame_info in inspect.stack(context=0)[relative_start:]:
            yield frame_info.frame


def _get_hub_ref():
    # Minimize lookup time by starting at frame 5, it will be at least that far back
    for frame in _stack_frames(5):
        if isinstance(frame.f_locals.get("self"), pop.contract.Contracted):
            contracted = frame.f_locals["self"]
            return contracted, frame.f_lineno

    # Default to the root reference
    return None, 0


def _get_logger(hub, name: str = ""):
    if name not in hub.log.LOGGER:
        hub.log.LOGGER[name]: aiologger.Logger = aiologger.Logger(name=name)
        hub.log.LOGGER[name].level = hub.log.INT_LEVEL
        if hub.log.FILE_HANDLER:
            hub.log.LOGGER[name].handlers.append(hub.log.FILE_HANDLER)
        if hub.log.STREAM_HANDLER:
            hub.log.LOGGER[name].handlers.append(hub.log.STREAM_HANDLER)
    return hub.log.LOGGER[name]


def log(hub, level: int, msg: str, *args, **kwargs):
    if hub.log.INT_LEVEL > level:
        return
    contract, lineno = _get_hub_ref()

    if contract:
        caller = f"{contract.ref}.{contract.func.__name__}"
        mod = contract.func.__module__
        func = contract.func.__name__
    else:
        caller = "hub"
        mod = "hub"
        func = "hub"

    logger: aiologger.Logger = _get_logger(hub, caller)
    record = aiologger.records.LogRecord(
        name=caller,
        pathname=mod,
        lineno=lineno,
        level=0,  # We have to overwrite this in a secure way
        msg=msg,
        args=args,
        func=func,
        **kwargs,
    )
    record.levelno = level
    if level == 5:
        record.levelname = "TRACE"
    else:
        try:
            record.levelname = aiologger.records.get_level_name(level)
        except ValueError:
            record.levelname = f"LEVEL {level}"

    ret = logger.handle(record)
    if asyncio.iscoroutine(ret):
        hub.pop.loop.CURRENT_LOOP.create_task(ret)


def setup(hub, conf):
    """
    Given the configuration data set up the logger
    """
    # Use the saved root logger
    root = _get_logger(hub, name="")

    raw_level = conf["log_level"].strip().lower()
    if raw_level.isdigit():
        hub.log.INT_LEVEL = int(raw_level)
    else:
        hub.log.INT_LEVEL = hub.log.LEVEL.get(raw_level, root.level)

    root.level = hub.log.INT_LEVEL
    cf = aiologger.formatters.base.Formatter(
        fmt=conf["log_fmt_console"], datefmt=conf["log_datefmt"]
    )
    ch = aiologger.handlers.streams.AsyncStreamHandler(formatter=cf, stream=sys.stderr)
    ch._level = hub.log.INT_LEVEL
    root.add_handler(ch)
    hub.log.STREAM_HANDLER = ch

    ff = aiologger.formatters.base.Formatter(
        fmt=conf["log_fmt_logfile"], datefmt=conf["log_datefmt"]
    )
    _, kwargs = hub.render.cli.args(conf["log_handler_options"])
    fh = aiologger.handlers.files.AsyncFileHandler(conf["log_file"], **kwargs)
    fh._level = hub.log.INT_LEVEL
    fh.formatter = ff
    root.add_handler(fh)
    hub.log.FILE_HANDLER = fh

    # Put all these functions higher up on the hub
    hub.log.log = hub.log["async"].log
    hub.log.trace = lambda msg, *args, **kwargs: hub.log.log(
        level=5, msg=msg, *args, **kwargs
    )
    hub.log.debug = lambda msg, *args, **kwargs: hub.log.log(
        level=aiologger.levels.LogLevel.DEBUG, msg=msg, *args, **kwargs
    )
    hub.log.info = lambda msg, *args, **kwargs: hub.log.log(
        level=aiologger.levels.LogLevel.INFO, msg=msg, *args, **kwargs
    )
    hub.log.warning = lambda msg, *args, **kwargs: hub.log.log(
        level=aiologger.levels.LogLevel.WARNING, msg=msg, *args, **kwargs
    )
    hub.log.error = lambda msg, *args, **kwargs: hub.log.log(
        level=aiologger.levels.LogLevel.ERROR, msg=msg, *args, **kwargs
    )
    hub.log.critical = lambda msg, *args, **kwargs: hub.log.log(
        level=aiologger.levels.LogLevel.CRITICAL, msg=msg, *args, **kwargs
    )
