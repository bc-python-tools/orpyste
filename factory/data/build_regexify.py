#!/usr/bin/env python3

# Sources:
#    * http://stackoverflow.com/q/768634/4589608
#    * http://stackoverflow.com/a/67692/4589608


# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

import ast
from collections import OrderedDict
import inspect
from importlib.machinery import SourceFileLoader
from pprint import pformat

from mistool import os_use
from mistool.os_use import (
    regexify,
    PPath
)



# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath(__file__).parent

for parent in THIS_DIR.parents:
    if parent.name == "orPySte":
        break

PY_FILE = parent / 'orpyste/data.py'

with PY_FILE.open(
    encoding = "utf-8",
    mode     = "r"
) as f:
    SOURCE_MODULE = f.readlines()


# ------------------------------ #
# -- CHANGING A PIECE OF CODE -- #
# ------------------------------ #

print('    * Looking for the last code of ``mistool.os_use.regexify``')

# Codes of the functions

source_mistool, _ = inspect.getsourcelines(regexify)
source_mistool    = "".join(source_mistool)

# Global constants used (upper case convention)

treeregexify = ast.parse(source_mistool)

global_constants = []

for node in ast.walk(treeregexify):
    if isinstance(node, ast.Name):
        varname = node.id

        if varname.upper() == varname \
        and varname not in global_constants:
            global_constants.append(varname)

# Codes of the global constants

sources_global_constants = OrderedDict([
    (varname, repr(getattr(os_use, varname)))
    for varname in global_constants
])


# Infos about the local and NOT the installed version !
localorpyste = SourceFileLoader("orpyste.data", str(PY_FILE)).load_module()

OrderedRecuDictUpdate = localorpyste.regexify

source_orpyste, start = inspect.getsourcelines(OrderedRecuDictUpdate)

start -= 1
end    = start + len(source_orpyste)


source_orpyste, start = inspect.getsourcelines(OrderedRecuDictUpdate)

for varname in global_constants:
    for nbline, line in enumerate(SOURCE_MODULE):
        if nbline == start:
            break

        if line.startswith(varname):
            start = min(start, nbline)


# Building of the new source code.

PY_TEXT = []

for nbline, line in enumerate(SOURCE_MODULE):
    if nbline < start or nbline > end:
        PY_TEXT.append(line)

    elif nbline == start:
        for varname, source in sources_global_constants.items():
            # Ugly patches !
            if source[0] == "{":
                source = "{" + "\n    " + source[1:-1] + "\n}"
                source = source.replace("', '", "',\n    '")

            source = "{0} = {1}".format(varname, source)
            PY_TEXT.append(source)
            PY_TEXT.append("\n"*2)

        PY_TEXT.append("\n")

        PY_TEXT.append(source_mistool)
        PY_TEXT.append("\n")

PY_TEXT = "".join(PY_TEXT)


# ---------------------------- #
# -- UPDATE THE PYTHON FILE -- #
# ---------------------------- #

print('    * Updating the Python file')

with PY_FILE.open(
    mode     = 'w',
    encoding = 'utf-8'
) as f:
    f.write(PY_TEXT)