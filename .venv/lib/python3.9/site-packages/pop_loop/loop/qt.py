try:
    import qasync

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)

__virtualname__ = "qt"


def __virtual__(hub):
    return HAS_LIBS


def __init__(hub):
    hub.loop.qt.APP = None


def get(hub):
    if not hub.loop.qt.APP:
        raise ValueError("A QApplication must be put on the hub at hub.loop.qt.APP")
    return qasync.QEventLoop(app=hub.loop.qt.APP)


def policy(hub):
    # return qasync.DefaultQEventLoopPolicy()
    ...


def executor(hub):
    return qasync.QThreadExecutor()
