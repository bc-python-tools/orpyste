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
    if parent.name == "orPyste":
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

# We adapt "by hand" the source code.
source_mistool = source_mistool[:-2]

nb_change = -1

for nb, line in enumerate(source_mistool):
    if ">>> print(regexify(" in line:
        nb_change = nb + 1

    elif nb == nb_change:
        source_mistool[nb] = "    re.compile('{0}')\n".format(line.strip())


source_mistool.append(
"""    newpattern  = re.compile("^{0}$".format(newpattern))

    return newpattern
"""
)

source_mistool = "".join(source_mistool)

source_mistool = source_mistool.replace(
    """    return = str ;
             a regex uncompiled version of ``pattern``.""",
    """    return = _sre.SRE_Pattern ;
             a compiled regex version of ``pattern``."""
)

source_mistool = source_mistool.replace(
    "from mistool.os_use import regexify",
    "from orpyste.data import regexify"
)


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
        # Ugly patches !
        for varname in sorted(list(sources_global_constants.keys())):
            source = sources_global_constants[varname]
            firstchar = source[0]

            if firstchar in "[{":
                source = source[1:-1].split(", ")
                source.sort()

                if firstchar == "[":
                    source = "[{0}]".format(", ".join(source))

                else:
                    source = ",\n    ".join(source)
                    source = "{\n    " + source + "\n}"

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

print('    * Updating the local Python file ``orpyste/data.py``')

with PY_FILE.open(
    mode     = 'w',
    encoding = 'utf-8'
) as f:
    f.write(PY_TEXT)
