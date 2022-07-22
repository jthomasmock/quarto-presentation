"""
Support embedding version number lookup into cli
"""
import importlib
import sys


def run(hub, primary):
    """
    Check the version number and then exit
    """
    mod = importlib.import_module(f"{primary}.version")
    print(f"{primary} {mod.version}")
    sys.exit(0)
