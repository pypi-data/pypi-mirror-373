"""
File Purpose: loading Bifrost number densities
"""
import numpy as np
import xarray as xr

from ....defaults import DEFAULTS
from ....errors import FormulaMissingError
from ....mhd import MhdMultifluidDensityLoader, Specie
from ....tools import simple_property

class BifrostMultifluidDensityLoader(MhdMultifluidDensityLoader):
    '''density quantities based on Bifrost single-fluid values, & inferred multifluid properties.'''

    cls_behavior_attrs.register('did_hion', default=False)
    did_hion = simple_property('_did_hion', setdefaultvia='_default_did_hion',
        doc='''whether this BifrostMultifluidCalculator has params['do_hion'] == True.
        Default is to just use the value from params.get('do_hion', False).
        when determining whether neq values exist (see self.N_MODE_OPTIONS), checks self.did_hion.

        User may wish to explicitly set did_hion, e.g. did_hion=
            =False to disable neq if bifrost had do_hion=True but hion file is missing or corrupted;
            =True to enable neq if bifrost had do_hion=False but hion file is provided separately...?''')
    def _default_did_hion(self):
        '''return default value for self.did_hion. Equivalent: self.params.get('do_hion', False).'''
        return self.params.get('do_hion', False)

    # # # N_MODE DISPATCH / CODE ARCHITECTURE # # #
    N_MODE_OPTIONS = {**MhdMultifluidDensityLoader.N_MODE_OPTIONS,
        'best': '''use best mode available, based on fluid:
            electron --> 'neq' if simulation neq enabled, else 'table'.
            H or He Specie --> 'neq' if simulation neq enabled, else 'saha'
            other Specie --> 'saha'.''',
        'neq': '''load value directly from file if simulation neq enabled and relevant to fluid.
            (crash if not electron)''',
        'QN_neq': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'neq' method.
            (crash if not electron)''',
    }

    NE_MODE_OPTIONS = {**MhdMultifluidDensityLoader.NE_MODE_OPTIONS,
        'best': '''use 'neq' if simulation neq enabled, else 'table'.''',
        'neq': '''load value directly from file if simulation neq enabled.
            neq possibly available in aux:
                e-     --> 'hionne'
                H_I    --> sum('n1', 'n2', 'n3', 'n4', 'n5')
                H_II   --> 'n6'
                He_I   --> 'nhe1'  (actually, exp('nhe1'); aux stores log values)
                He_II  --> 'nhe2'  (actually, exp('nhe2'); aux stores log values)
                He_III --> 'nhe3'  (actually, exp('nhe3'); aux stores log values)
            (if not possible, crash or return NaN, depending on self.typevar_crash_if_nan)''',
        'QN_neq': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'neq' method.''',
    }

    _NE_MODE_INTERNAL = {**MhdMultifluidDensityLoader._NE_MODE_INTERNAL,
        'QN_neq': 'neq'
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
            'nan' <--> nan or crash, depending on self.typevar_crash_if_nan.
        possible results (possible here but not in parent class)
            'neq' <--> n from neq-related files.
            'QN_neq' <--> n from sum of qi ni across self.fluids, with ne from neq.
        '''
        result = 'nan'  # <-- nan unless set to something else below
        f = self.fluid
        if not isinstance(f, Specie):
            result = super().get_ntype()
        else:  # f is a Specie. fully handled here for readability, despite repetitiveness with super().
            result = 'nan'
            # bookkeeping:
            e = f.is_electron()
            mode = self.ne_mode_explicit if e else self.n_mode
            H = (f.element == 'H')
            He = (f.element == 'He')
            if e or H:
                neq = self.did_hion
            elif He:
                neq = self.params.get('do_helium', False)
            else:
                neq = False
            non_neq = (not neq)
            # logic:
            if mode == 'elem' and f.element is not None:
                result = 'elem'
            elif neq and (mode == 'best' or mode == 'neq'):
                result = 'neq'
            elif (not e) and ((mode == 'saha') or (mode == 'best' and non_neq)):
                result = 'saha'
            elif e:
                if (mode == 'table') or (mode == 'best' and non_neq):
                    result = 'table'
                elif (mode == 'QN_neq') or (mode == 'QN' and neq):
                    result = 'QN_neq'
                elif (mode == 'QN_table') or (mode == 'QN' and non_neq):
                    result = 'QN_table'
        if result == 'nan':
            self._handle_typevar_nan(errmsg=f"ntype, when fluid={self.fluid!r}, n_mode={self.n_mode!r}.")
        return xr.DataArray(result)

    NTYPE_TO_VAR = {**MhdMultifluidDensityLoader.NTYPE_TO_VAR,
        'neq': 'n_neq',
    }
    _NTYPE_TO_NONSIMPLE_DEPS = {**MhdMultifluidDensityLoader._NTYPE_TO_NONSIMPLE_DEPS,
        'QN_neq': ['ne_QN', 'ne_neq'],
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
        if ntype == 'QN_neq':
            return self('ne_QN', ne_mode='neq')
        else:
            return super().get_n(ntype=ntype)


    # # # NON-EQUILIBRIUM NUMBER DENSITY # # #

    @known_var(load_across_dims=['fluid'])
    def get_n_neq(self):
        '''number density of self.fluid specie(s); non-equilibrium values.
        Result depends on fluid:
            electron --> 'hionne'
            'H_I'    --> sum('n1', 'n2', 'n3', 'n4', 'n5')
            'H_II'   --> 'n6'
            'He_I'   --> 'nhe1'  (actually, exp('nhe1'); aux stores log values)
            'He_II'  --> 'nhe2'  (actually, exp('nhe2'); aux stores log values)
            'He_III' --> 'nhe3'  (actually, exp('nhe3'); aux stores log values)
            other --> crash with FormulaMissingError.
        the electron fluid is tested via fluid.is_electron(),
        while the other species are tested via name-matching to the names above.
        '''
        # load_across_dims for this one, instead of partition_across_dim,
        #   because here we don't expect multiple self.fluid with same formula,
        #   so there's basically no efficiency improvements from grouping.
        f = self.fluid
        if f.is_electron():
            return self('ne_neq')
        elif f == 'H_I':
            n1 = self('load_n1')
            n2 = self('load_n2')
            n3 = self('load_n3')
            n4 = self('load_n4')
            n5 = self('load_n5')
            result_cgs = n1 + n2 + n3 + n4 + n5
        elif f == 'H_II':
            result_cgs = self('load_n6')
        elif f == 'He_I':
            result_cgs = np.exp(self('load_nhe1'))
        elif f == 'He_II':
            result_cgs = np.exp(self('load_nhe2'))
        elif f == 'He_III':
            result_cgs = np.exp(self('load_nhe3'))
        else:
            raise FormulaMissingError(f'n_neq for fluid {f}.')
        result_cgs = self._upcast_if_max_n_requires_float64(result_cgs)  # <- maybe make float64.
        result = result_cgs * self.u('n', convert_from='cgs')  # <- convert to self.units system.
        return self.record_units(result)


    # # # NTYPE: SAHA # # #
    # inherited from MhdMultifluidDensityLoader


    # # # NTYPE: ELECTRON # # #

    _NE_TYPE_TO_DEPS = {**MhdMultifluidDensityLoader._NE_TYPE_TO_DEPS,
        'neq': ['ne_neq'],
        'QN_neq': ['ne_QN', 'ne_neq'],
    }

    @known_var(value_deps=[('ne_type', '_NE_TYPE_TO_DEPS')])
    def get_ne(self):
        '''electron number density. Result depends on self.ne_mode.
        See self.NE_MODE_OPTIONS for details.
        '''
        kind = self('ne_type').item()
        # 'neq' and 'QN_neq' are new in this subclass; all other kinds can be handled by super().
        if kind == 'neq':
            return self('ne_neq')
        elif kind == 'QN_neq':
            return self('ne_QN', ne_mode='neq')
        else:
            return super().get_ne()

    # get_ne_QN() is inherited from MhdMultifluidDensityLoader.

    @known_var(dims=['snap'], ignores_dims=['fluid'])
    def get_ne_neq(self):
        '''electron number density, from 'hionne' in aux.
        hionne in aux is stored in cgs units.
        '''
        result = super().get_ne_neq()  # see BifrostEosLoader
        return self._assign_electron_fluid_coord_if_unambiguous(result)
