"""
File Purpose: loading quantities related to addons but specific to eppic.
"""

from ...addons import ADDON_LOADERS
from ...quantities import QuantityLoader

loaded_tfbi = any(_cls.__name__=='TfbiLoader' for _cls in ADDON_LOADERS)

class EppicAddonQuantityLoader(QuantityLoader):
    '''Loader for quantities related to addons but specific to eppic.'''
    if loaded_tfbi:
        @known_var(deps=['tfbi_vs_EBspeed'])
        def get_inputs_tfbi_vs_EBspeed(self):
            '''get tfbi_vs_EBspeed at self.set_vars_from_inputs().
            Makes a copy of self to do this computation, to avoid altering original self.
            [TODO] update this if internal methods for this don't alter the copy anymore
            '''
            ec = self.copy()
            ec.set_vars_from_inputs()
            return ec('tfbi_vs_EBspeed')
