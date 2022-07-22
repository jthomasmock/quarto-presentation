"""
Support embedding version number lookup into cli
"""
import sys


def run(hub, opts):
    """
    Output a config file based on the current command
    """
    hub.pop.sub.add(dyne_name="rend")
    outputter = opts.get("rend", {}).get("output") or "yaml"

    output_opts = {}
    # Trim old values from opt
    for dyne, config in opts.items():
        if not config:
            continue

        output_config = {}
        for k, v in config.items():
            # config_template will be "True" for this run, which would make the config file always result in exit
            if k in ("config_template", "config"):
                continue
            output_config[k] = v
        output_opts[dyne] = output_config

    out = hub.output[outputter].display(output_opts)

    print(out)
    sys.exit(0)
