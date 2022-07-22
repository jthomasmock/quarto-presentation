"""
The os sub is used to gather configuration options from the OS facility
to send configuration options into applications.
"""
import itertools
import os
from typing import Dict


def gather(hub, raw: Dict) -> Dict[str, Dict]:
    """
    Collect the keys that need to be found and pass them to the
    os specific loaded plugin
    """
    ret = {}
    for sec, imp in itertools.product(hub.config.CONFIG_SECTIONS, raw):
        for key in raw[imp].get(sec, ()):
            osvar = raw[imp][sec][key].get("os")
            if osvar is None:
                continue
            val = os.environ.get(osvar.upper())
            if val is None:
                continue
            src = raw[imp][sec][key].get("source", imp)
            if src not in ret:
                ret[src] = {}
            ret[src][key] = val
    return ret
