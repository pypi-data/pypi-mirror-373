"""CLI for 'agp Tools' package.

# Autocompletion

https://click.palletsprojects.com/en/8.1.x/shell-completion/

_AGPTOOLS_COMPLETE=IGNORE_WINGDEBUG=0 bash_source agptools > ~/.agptools-complete.bash

. ~/.agptools-complete.bash

"""

import sys
import os

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
