"""
Configuration file core loading functions
"""
import pathlib

import dict_tools.update


def parse(hub, raw, cli, os_vars, cli_args, loader):
    """
    Determine if a config file or a config dir has been set up and load it up!
    """
    # This function is the entry point for the config.conf_file sub
    # Figure out what config file value to use in this priority
    default = raw[cli]["CONFIG"].get("config", {}).get("default")
    default_dir = raw[cli]["CONFIG"].get("config_dir", {}).get("default")
    if cli in os_vars:
        os_conf = os_vars[cli].get("config", default)
        os_dir = os_vars[cli].get("config_dir", default_dir)
    else:
        os_conf = os_vars.get("config", default)
        os_dir = os_vars.get("config_dir", default_dir)
    conf = cli_args.get("config", os_conf)
    dir_ = cli_args.get("config_dir", os_dir)
    file_opts = {}
    dir_opts = {}
    if dir_:
        file_opts = hub.config.file.load_dir(dir_, loader)
    if conf:
        dir_opts = hub.config.file.load(conf, loader)
    ret = dict_tools.update.update(dir_opts, file_opts)
    return ret


def load(hub, paths, loader, includes=True):
    """
    Load a single configuration file
    """
    opts = {}
    if not isinstance(paths, list):
        paths = [paths]
    add = []
    for fn in paths:
        for path in pathlib.Path(fn).rglob("**"):
            add.append(str(path))
    paths.extend(add)
    for fn in paths:
        fn_data = hub.render.init.load_file(loader, fn)
        if includes:
            fn_data = hub.config.file.proc_include(fn, fn_data, loader)
        dict_tools.update.update(opts, fn_data)
    return opts


def load_dir(
    hub,
    confdir,
    loader,
    includes=True,
    recurse=True,
):
    """
    Load takes a directory location to scan for configuration files. These
    files will be read in.
    """
    opts = {}
    if not isinstance(confdir, list):
        confdir = [confdir]
    confdirs = []
    for dirs in confdir:
        if not isinstance(dirs, (list, tuple)):
            dirs = [dirs]
        for dir_ in dirs:
            for g in pathlib.Path(dir_).rglob("**"):
                confdirs.append(g)
    paths = []
    for dir_ in confdirs:
        dirpaths = []
        if not dir_.is_dir():
            continue
        if not recurse:
            for path in dir_.iterdir():
                if path.is_dir():
                    # Don't process directories
                    continue
                dirpaths.append(str(path))
        else:
            for p in dir_.iterdir():
                dirpaths.append(str(p))

        # Sort confdir directory paths like:
        # /b.txt
        # /c.txt
        # /a/x.txt
        # /b/x.txt
        paths.extend(sorted(dirpaths, key=lambda p: (p.count(pathlib.os.path.sep), p)))
    dict_tools.update.update(opts, hub.config.file.load(paths, loader, includes))
    return opts


def proc_include(hub, fn, opts, loader):
    """
    Process include and include_dir
    """
    dirname = pathlib.Path(fn).parent
    root = pathlib.Path(pathlib.os.sep).absolute()
    if opts.get("include_dir"):
        idir = pathlib.Path(opts.pop("include_dir"))
        pathlib.sep
        if not str(idir).startswith(str(root)):
            idir = dirname / idir
        dict_tools.update.update(opts, hub.config.file.load_dir(str(idir), loader))
        hub.config.file.proc_include(str(idir / "f"), opts, loader)
    if opts.get("include"):
        ifn = opts.pop("include")
        if not ifn.startswith(str(root)):
            ifn = dirname / ifn
        dict_tools.update.update(opts, hub.config.file.load(ifn, loader))
        hub.config.file.proc_include(ifn, opts, loader)
    return opts
