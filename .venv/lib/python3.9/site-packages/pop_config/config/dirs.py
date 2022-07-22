"""
Find the conf.py files specified in sources
"""
import copy
import importlib
import os.path
from typing import Dict
from typing import List
from typing import Tuple

import dict_tools.update


def load(hub, sources: List[str], dyne_names: List[str], cli: str):
    """
    Look over the sources list and find the correct conf.py files
    """
    # Dynamic names
    # First gather the defined sources, they are the authoritative ones
    # Then detect what the dynamic names are in the source
    # Merged the sources dyne names with any passed dyne names
    # Load up and extend the raw with all of the dynamic names
    dyne = hub.pop.dyne.get()
    if not isinstance(sources, list):
        sources = [sources]
    raw = hub.config.dirs.find_configs(sources)
    # Makes sure everything is unique
    dnames = set(dyne_names)
    for source in sources:
        dnames.update(raw[source]["DYNE"].keys())
    for name in dnames:
        if name in dyne:
            if name not in raw:
                raw[name] = {"CONFIG": {}, "CLI_CONFIG": {}}
            dyne_data = dyne[name]
            if "CONFIG" in dyne_data:
                dyne_data, config_draw = hub.config.dirs.parse_config(dyne_data, cli)
                dict_tools.update.update(raw[cli]["CONFIG"], config_draw)
            if "CLI_CONFIG" in dyne_data:
                cli_draw = hub.config.dirs.parse_cli(dyne_data, cli)
                dict_tools.update.update(raw[cli]["CLI_CONFIG"], cli_draw)
            if "SUBCOMMANDS" in dyne_data:
                subcmd_draw = hub.config.dirs.parse_subcommand(dyne_data, cli)
                dict_tools.update.update(raw[cli]["SUBCOMMANDS"], subcmd_draw)
    return raw


def find_configs(hub, sources: List[str]):
    raw = {}
    for source in sources:
        try:
            path, data = hub.config.dirs.import_conf(source)
        except ImportError:
            continue
        dict_tools.update.update(raw, data)
    return raw


def import_conf(hub, imp: str) -> Tuple[str, Dict]:
    """
    Load up a python path, parse it and return the conf dataset
    """
    ret = {imp: {}}
    cmod = importlib.import_module(f"{imp}.conf")
    path = os.path.dirname(cmod.__file__)
    for section in hub.config.SECTIONS:
        ret[imp][section] = copy.deepcopy(getattr(cmod, section, {}))
    return path, ret


def parse_config(hub, dyne_data: Dict[str, Dict], cli: str) -> Tuple[Dict, Dict]:
    config_draw = {}
    for key, val in dyne_data["CONFIG"].items():
        new_dyne = val.get("dyne")
        if new_dyne == "__cli__":
            new_dyne = cli
        if new_dyne:
            val["source"] = new_dyne
            config_draw[key] = val
            if (
                key in dyne_data.get("CLI_CONFIG", {})
                and "dyne" not in dyne_data["CLI_CONFIG"][key]
            ):
                dyne_data["CLI_CONFIG"][key]["dyne"] = new_dyne
    return dyne_data, config_draw


def parse_cli(hub, dyne_data: Dict, cli: str) -> Dict:
    cli_draw = {}
    for key, val in dyne_data["CLI_CONFIG"].items():
        new_dyne = val.get("dyne")
        if new_dyne == "__cli__":
            new_dyne = cli
        if new_dyne:
            val["source"] = new_dyne
            cli_draw[key] = val
    return cli_draw


def parse_subcommand(hub, dyne_data: Dict, cli: str) -> Dict:
    subcmd_draw = {}
    for key, val in dyne_data["SUBCOMMANDS"].items():
        new_dyne = val.get("dyne")
        if new_dyne == "__cli__":
            new_dyne = cli
        if new_dyne:
            val["source"] = new_dyne
        if new_dyne == cli:
            subcmd_draw[key] = val
    return subcmd_draw


def verify(hub, opts):
    """
    Verify that the environment and all named directories in the
    configuration exist
    """
    for imp in opts:
        for key in opts[imp]:
            if key == "root_dir":
                continue
            if key == "config_dir":
                continue
            if key.endswith("_dir"):
                if not os.path.isdir(opts[imp][key]):
                    os.makedirs(opts[imp][key])
