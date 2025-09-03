"""
File Purpose: base quantities for MuramCalculator
"""

from ...defaults import DEFAULTS
from ...dimensions import SINGLE_FLUID
from ...errors import (
    FluidValueError, FormulaMissingError, LoadingNotImplementedError,
    InputError, InputMissingError,
)
from ...mhd import MhdBasesLoader
from ...tools import (
    simple_property,
    UNSET,
)


### --------------------- MuramBasesLoader --------------------- ###

class MuramBasesLoader(MhdBasesLoader):
    '''base quantities based on Muram output.'''
    @known_var(dims=['snap'])
    def get_r(self):
        '''mass density. (directly from Muram)
        assumes single fluid mode, i.e. result corresponds to the single fluid from Muram.
        '''
        self.assert_single_fluid_mode('r')
        return self.load_maindims_var_across_dims('result_prim_r', u='mass_density', dims=['snap'])

    @known_var(dims=['snap', 'component'])
    def get_u(self):
        '''velocity. (directly from Muram)
        assumes single fluid mode, i.e. result corresponds to the single fluid from Muram.
        '''
        self.assert_single_fluid_mode('u')
        return self.load_maindims_var_across_dims('result_prim_u', u='speed', dims=['snap', 'component'])

    @known_var(dims=['snap'])
    def get_e(self):
        '''energy density. (directly from Muram)
        Per unit volume, e.g. the SI units would be Joules / meter^3.
        assumes single fluid mode, i.e. result corresponds to the single fluid from Muram.
        '''
        self.assert_single_fluid_mode('e')
        return self.load_maindims_var_across_dims('result_prim_e', u='energy_density', dims=['snap'])

    @known_var(dims=['snap', 'component'])
    def get_B(self):
        '''magnetic field. (directly from Muram)'''
        return self.load_maindims_var_across_dims('result_prim_b', u='b', dims=['snap', 'component'])

    @known_var
    def get_gamma(self):
        '''adiabatic index. Assumed to be 5/3.'''
        return 5/3.
