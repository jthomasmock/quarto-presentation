import sys


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


def _get_logger(hub, name: str = ""):
    if name not in hub.log.LOGGER:
        hub.log.LOGGER[name]: aiologger.Logger = aiologger.Logger(
            name=name, loop=hub.pop.Loop
        )
        hub.log.LOGGER[name].level = hub.log.INT_LEVEL
        if hub.log.FILE_HANDLER:
            hub.log.LOGGER[name].handlers.append(hub.log.FILE_HANDLER)
        if hub.log.STREAM_HANDLER:
            hub.log.LOGGER[name].handlers.append(hub.log.STREAM_HANDLER)
    return hub.log.LOGGER[name]


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
    ch = aiologger.handlers.streams.AsyncStreamHandler(
        formatter=cf, loop=hub.pop.Loop, stream=sys.stderr
    )
    ch._level = hub.log.INT_LEVEL
    root.add_handler(ch)
    hub.log.STREAM_HANDLER = ch

    ff = aiologger.formatters.base.Formatter(
        fmt=conf["log_fmt_logfile"], datefmt=conf["log_datefmt"]
    )
    _, kwargs = hub.render.cli.args(conf["log_handler_options"])
    fh = aiologger.handlers.files.AsyncTimedRotatingFileHandler(
        conf["log_file"], **kwargs
    )
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
