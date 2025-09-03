"""
Package Purpose: optional add-ons for PlasmaCalculators

[TODO] custom gettable vars (defined outside of PlasmaCalcs)?
[TODO] "load all addons" function; don't load until function called.
        this way, user could edit DEFAULTS before loading addons.
"""
from . import addon_tools
# load all addon modules (allowing them to register_addon_loader if appropriate)
from . import tfbi
from . import instability_tools

# import specific things from addon modules
from .instability_tools import itAccessor
from .addon_tools import ADDON_LOADERS

# create AddonLoader object with all loaded addon loaders
class AddonLoader(*ADDON_LOADERS):
    '''loader for all (successfully) imported addons.'''
    pass
