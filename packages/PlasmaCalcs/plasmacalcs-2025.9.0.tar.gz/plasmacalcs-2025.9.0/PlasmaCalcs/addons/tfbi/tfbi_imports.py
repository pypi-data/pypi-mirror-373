"""
File Purpose: handling imports related to tfbi.
"""

from ...defaults import DEFAULTS
from ...tools import ImportFailed

# if SymSolver or tfbi_theory imports fail, some tfbi methods will fail,
#  but not all methods --> still useful to load this addon.
try:
    import SymSolver
except ImportError as err:
    SymSolver = ImportFailed("SymSolver", err=err, locals=locals(), abbrv='SymSolver')
try:
    import tfbi_theory
except ImportError as err:
    tfbi_theory = ImportFailed("tfbi_theory", err=err, locals=locals(), abbrv='tfbi_theory')

if (DEFAULTS.ADDONS.LOAD_TFBI == True) and any(isinstance(x, ImportFailed) for x in (SymSolver, tfbi_theory)):
    errmsg = ("Failed to import SymSolver or tfbi_theory. To disable this error, "
              "Set PlasmaCalcs.defaults.DEFAULTS.LOAD_TFBI to 'attempt' or False.")
    raise ImportError(errmsg)
