"""
File Purpose: BifrostMultifluidCalculator
"""

from .bifrost_multifluid_densities import BifrostMultifluidDensityLoader
from ..bifrost_calculator import BifrostCalculator
from ....dimensions import SINGLE_FLUID
from ....mhd import MhdMultifluidCalculator, SpecieList
from ....tools import format_docstring

@format_docstring(bifrost_calculator_docs=BifrostCalculator.__doc__, sub_ntab=1)
class BifrostMultifluidCalculator(BifrostMultifluidDensityLoader,
                                  MhdMultifluidCalculator,
                                  BifrostCalculator):
    '''MultifluidPlasmaCalculator for Bifrost outputs.
    various possible ways to infer fluids.
        One possibility is to use abundances + saha ionization equation.
        [TODO] explain this in more detail.
        [TODO] allow to enter fluids as list of strings during init.

    set self.fluid=SINGLE_FLUID to get single-fluid values,
        otherwise will get inferred multifluid values.

    --- Docstring from BifrostCalculator copied below ---
        {bifrost_calculator_docs}
    '''

    SINGLE_FLUID = SINGLE_FLUID  # convenient reference to SINGLE_FLUID. Subclass should NEVER override.

    def __init__(self, snapname=None, *, units='si', **kw_super):
        super().__init__(snapname=snapname, units=units, **kw_super)
        self.init_fluids()

    # # # FLUIDS # # #
    def init_fluids(self):
        '''initialize self.fluids, fluid, jfluids, and jfluid.'''
        self.fluids = self.chromo_fluid_list()
        self.fluid = None
        self.jfluids = self.fluids
        self.jfluid = self.jfluids.get_neutral()

    def chromo_fluid_list(self):
        '''SpecieList of species relevant to the chromosphere, maybe.
        currently, just produces list of [electron, H_I, H_II, *other_once_ionized_ions]
            also includes He_III (after He_II) if self.params['do_helium'].
        '''
        elements = self.tabin.elements
        if (elements[0] != 'H') or (elements[1] != 'He'):
            raise NotImplementedError('[TODO] chromo_fluid_list for other elements list?')
        H = elements.get('H')
        He = elements.get('He')
        other = elements[2:]
        result = [SpecieList.value_type.electron(),
                  H.neutral(),
                  H.ion(1),
                  He.ion(1),
                  ]
        if self.params.get('do_helium', False):
            result.append(He.ion(2))  # include He_III
        result.extend(other.ion_list(q=1))
        return SpecieList(result, istart=0)  # istart=0 --> renumber for this list.
