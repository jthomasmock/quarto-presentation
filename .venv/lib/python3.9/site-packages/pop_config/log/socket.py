import logging.handlers


def setup(hub, conf):
    """
    Given the configuration data set up the logger.

    Output to a network socket.  If no port is specified, a Unix domain socket is created using the value in `host`

    To specify the host and port add `--log-file="host:port"` to your command line

    I.E.  `--log-file="127.0.0.1:80`

    """
    root = logging.getLogger()

    raw_level = conf["log_level"].strip().lower()
    if raw_level.isdigit():
        hub.log.INT_LEVEL = int(raw_level)
    else:
        hub.log.INT_LEVEL = hub.log.LEVEL.get(raw_level, root.level)

    root.setLevel(hub.log.INT_LEVEL)
    cf = logging.Formatter(fmt=conf["log_fmt_console"], datefmt=conf["log_datefmt"])
    ch = logging.StreamHandler()
    ch.setLevel(hub.log.INT_LEVEL)
    ch.setFormatter(cf)
    root.addHandler(ch)

    _, kwargs = hub.render.cli.args(conf["log_handler_options"])
    ff = logging.Formatter(
        fmt=conf["log_fmt_logfile"], datefmt=conf["log_datefmt"], **kwargs
    )
    if ":" in conf["log_file"]:
        host, port = conf["log_file"].split(":")
    else:
        host = conf["log_file"]
        port = None
    fh = logging.handlers.SocketHandler(host=host, port=port)
    fh.setLevel(hub.log.INT_LEVEL)
    fh.setFormatter(ff)
    root.addHandler(fh)
