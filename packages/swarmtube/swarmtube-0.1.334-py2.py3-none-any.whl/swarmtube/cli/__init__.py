"""CLI for 'SwarmTube' package.

# Autocompletion

https://click.palletsprojects.com/en/8.1.x/shell-completion/

_SWARMTUBE_COMPLETE=bash_source swarmtube > ~/.swarmtube-complete.bash

. ~/.swarmtube-complete.bash

"""

# ==============================================================
# Implementation of 1st ports interface for CLI
# ==============================================================
import sys
import os

ACTIVE_WINGDEBUG = os.environ.get("ACTIVE_WINGDEBUG", "False").lower()

if ACTIVE_WINGDEBUG in ("true", "yes", "1"):
    try:
        # print(f"Trying to connect to a remote debugger..")
        sys.path.append(os.path.dirname(__file__))
        from . import wingdbstub

        sys.path.remove(os.path.dirname(__file__))
    except Exception as why:
        print(f"{why}")
        print(
            "Remote debugging is not found or configured: Use ACTIVE_WINGDEBUG=True to activate"
        )
else:
    # don't show: problem with bash_source autocompletion
    # print("Remote debugging is not selected")
    pass


# ---------------------------------------------------------
# local imports
# ---------------------------------------------------------
from ..helpers.loaders import ModuleLoader

# -----------------------------------------------
# import main cli interface (root)
# -----------------------------------------------

from .main import main

# ---------------------------------------------------------
# Load active port (click) modules
# from `config.yaml` config file
# ---------------------------------------------------------

loader = ModuleLoader(__file__)
names = loader.available_modules()
if ACTIVE_WINGDEBUG not in ("true", "yes", "1"):
    if "wingdbstub" in names:
        names.remove("wingdbstub")
ACTIVE_PORTS = loader.load_modules(names)
