"""CLI for 'syncmodels' package.

# Autocompletion

https://click.palletsprojects.com/en/8.1.x/shell-completion/

_SYNCMODELS_COMPLETE=IGNORE_WINGDEBUG=0 bash_source syncmodels > ~/.syncmodels-complete.bash

. ~/.syncmodels-complete.bash

"""

import sys
import os

if not os.environ.get("IGNORE_WINGDEBUG", False):
    try:
        # print(f"Trying to connect to a remote debugger..")
        sys.path.append(os.path.dirname(__file__))
        from . import wingdbstub
    except Exception:
        print("Remote debugging is not found or configured...")

# -----------------------------------------------
# import main cli interface (root)
# -----------------------------------------------

from .main import *
from .config import *
from .workspace import *

# -----------------------------------------------
# import other project submodules/subcommands
# -----------------------------------------------

# from .inventory import inventory
# from .plan import plan
# from .real import real
# from .roles import role
# from .run import run
# from .target import target
# from .test import test
# from .users import user
# from .watch import watch
