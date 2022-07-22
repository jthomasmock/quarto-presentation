CLI_CONFIG = {
    "file": {
        "options": ["--file", "-f"],
    },
    "pipe": {
        "options": ["--pipe", "-p"],
    },
    "output": {
        "options": ["--output", "-o"],
    },
}
CONFIG = {
    "file": {
        "default": None,
        "help": "Pass in a file location that will be rendered",
    },
    "pipe": {
        "default": "yaml",
        "help": "Define what render pipeline should be used",
    },
    "output": {
        "default": None,
        "help": "Define which outputter system should be used to display the result of this render",
    },
}
GLOBAL = {}
SUBS = {}
DYNE = {
    "rend": ["rend"],
    "output": ["output"],
}
