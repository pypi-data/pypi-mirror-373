"""
File Purpose: multifluid densities analysis from single-fluid muram data
"""

import numpy as np
import xarray as xr

from ...dimensions import SINGLE_FLUID
from ...defaults import DEFAULTS
from ...errors import (
    FluidValueError, FluidKeyError,
    InputError, FormulaMissingError, LoadingNotImplementedError,
)
from ...mhd import MhdMultifluidDensityLoader, Element, Specie
from ...tools import (
    simple_property,
    UNSET,
)


class MuramMultifluidDensityLoader(MhdMultifluidDensityLoader):
    '''density quantities based on Muram single-fluid values, & inferred multifluid properties.'''

    # # # N_MODE DISPATCH / CODE ARCHITECTURE # # #
    N_MODE_OPTIONS = {**MhdMultifluidDensityLoader.N_MODE_OPTIONS,
        'best': '''use best mode available, based on fluid:
            electron --> 'aux' if eosne files exist, else 'table'
            other Specie --> 'saha'.''',
        'aux': '''load directly from file. 'eosne' for electrons.
            (crash if not electron)''',
        'QN_aux': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'aux' method.
            (crash if not electron)''',
    }

    NE_MODE_OPTIONS = {**MhdMultifluidDensityLoader.NE_MODE_OPTIONS,
        'best': '''use 'aux' if eosne files exist, else 'table'.''',
        'aux': '''load directly from 'eosne' file.
            (if not possible, crash or return NaN, depending on self.typevar_crash_if_nan)''',
        'QN_aux': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'aux' method.''',
    }

    _NE_MODE_INTERNAL = {**MhdMultifluidDensityLoader._NE_MODE_INTERNAL,
        'QN_aux': 'aux',
    }

    # # # GENERIC NUMBER DENSITY # # #
    @known_var(load_across_dims=['fluid'])
    def get_ntype(self):
        '''ntype of self.fluid. Result depends on fluid as well as self.n_mode (and ne_mode if electron).
        See self.N_MODE_OPTIONS and self.NE_MODE_OPTIONS for options.
        possible results (possible in parent class)
            'SINGLE_FLUID' <--> n for SINGLE_FLUID
            'elem' <--> n for Element
            'saha' <--> n from saha equation. (not available for electrons)
            'table' <--> n from EOS table. (only available for electrons)
            'QN_table' <--> n from sum of qi ni across self.fluids, with ne from table.
        possible results (possible here but not in parent class)
            'aux' <--> n from 'eosne' file. (only available for electrons)
            'QN_aux' <--> n from sum of qi ni across self.fluids, with ne from 'eosne' file.
        '''
        result = 'nan'  # <-- nan unless set to something else below
        f = self.fluid
        if not isinstance(f, Specie):
            result = super().get_ntype()
        else:  # f is a Specie. fully handled here for readability, despite repetitiveness with super().
            # bookkeeping:
            e = f.is_electron()
            mode = self.ne_mode_explicit if e else self.n_mode
            aux = self._all_eos_aux_files_exist()
            non_aux = (not aux)
            # logic:
            if mode == 'elem' and f.element is not None:
                result = 'elem'
            elif (not e) and ((mode == 'saha') or (mode == 'best')):
                result = 'saha'
            elif e:
                if (mode == 'table') or ((mode == 'best') and non_aux):
                    result = 'table'
                elif aux and ((mode == 'aux') or (mode == 'best')):
                    result = 'aux'
                elif aux and ((mode == 'QN_aux') or (mode == 'QN')):
                    result = 'QN_aux'
                elif (mode == 'QN_table') or ((mode == 'QN') and non_aux):
                    result = 'QN_table'
        if result == 'nan':
            self._handle_typevar_nan(errmsg=f"ntype, when fluid={self.fluid!r}, n_mode={self.n_mode!r}.")
        return xr.DataArray(result)

    NTYPE_TO_VAR = {**MhdMultifluidDensityLoader.NTYPE_TO_VAR,
        'aux': 'n_aux',
    }
    _NTYPE_TO_NONSIMPLE_DEPS = {**MhdMultifluidDensityLoader._NTYPE_TO_NONSIMPLE_DEPS,
        'QN_aux': ['ne_QN', 'ne_aux'],
    }
    # _NTYPE_TO_DEPS property is inherited from MhdMultifluidDensityLoader.

    @known_var(partition_across_dim=('fluid', 'ntype'), partition_deps='_NTYPE_TO_DEPS')
    def get_n(self, *, ntype):
        '''number density. Formula depends on fluid:
        if SINGLE_FLUID, n = (r / m), from SINGLE_FLUID r & m.
            default m is the abundance-weighted average particle mass; see help(self.get_m) for details.
        if Element, n = (r / m), where
            r is inferred from abundances combined with SINGLE_FLUID r, and
            m is element particle mass (fluid.m)
        if Specie, n depends on ntype, determined from self.n_mode (and self.ne_mode, if electron);
            see help(self.get_ntype) for details.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        # super() can handle the NTYPE_TO_VAR stuff, and most other stuff;
        #    here we only need to handle the new stuff in _NTYPE_TO_NONSIMPLE_DEPS.
        if ntype == 'QN_aux':
            return self('ne_QN', ne_mode='aux')
        else:
            return super().get_n(ntype=ntype)


    # # # NON-EQUILIBRIUM NUMBER DENSITY # # #

    @known_var(deps=['ne_aux'], load_across_dims=['fluid'])
    def get_n_aux(self):
        '''number density of self.fluid specie(s); from aux files values.
        Result depends on fluid:
            electron --> 'eosne'
            other --> crash with FormulaMissingError.
        '''
        # load_across_dims for this one, instead of partition_across_dim,
        #   because here we don't expect multiple self.fluid with same formula,
        #   so there's basically no efficiency improvements from grouping.
        f = self.fluid
        if f.is_electron():
            return self('ne_aux')
        else:
            raise FormulaMissingError(f'n_aux for non-electron fluid {f}.')


    # # # NTYPE: SAHA # # #
    # inherited from MhdMultifluidDensityLoader


    # # # NTYPE: ELECTRON # # #

    _NE_TYPE_TO_DEPS = {**MhdMultifluidDensityLoader._NE_TYPE_TO_DEPS,
        'aux': ['ne_aux'],
        'QN_aux': ['ne_QN', 'ne_aux'],
    }

    @known_var(value_deps=[('ne_type', '_NE_TYPE_TO_DEPS')])
    def get_ne(self):
        '''electron number density. Result depends on self.ne_mode.
        See self.NE_MODE_OPTIONS for details.
        '''
        kind = self('ne_type').item()
        # 'aux' and 'QN_aux' are new in this subclass; all other kinds can be handled by super().
        if kind == 'aux':
            return self('ne_aux')
        elif kind == 'QN_aux':
            return self('ne_QN', ne_mode='aux')
        else:
            return super().get_ne()

    # get_ne_QN() is inherited from MhdMultifluidDensityLoader.

    @known_var(dims=['snap'], ignores_dims=['fluid'])
    def get_ne_aux(self):
        '''electron number density, from 'hionne' in aux.
        hionne in aux is stored in cgs units.
        '''
        result = super().get_ne_aux()  # see MuramEosLoader
        return self._assign_electron_fluid_coord_if_unambiguous(result)
