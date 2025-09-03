"""
File Purpose: DimensionlessPlasmaCalculatorFromDataset
"""

import numpy as np
import xarray as xr

from ..dimensions import SnapList, ComponentList, FluidList
from ..errors import LoadingNotImplementedError
from ..plasma_calculator import (
    DimensionlessPlasmaCalculator,
    ComponentHavingPlasmaCalculator, PlasmaCalculator, MultifluidPlasmaCalculator,
    VectorlessPlasmaCalculator, VectorlessMultifluidPlasmaCalculator,
)
from ..quantities import DirectBasesLoader
from ..tools import (
    alias,
    is_iterable, xr1d,
    xarray_sel,
)

class DimensionlessFromDatasetCalculator(DirectBasesLoader, DimensionlessPlasmaCalculator):
    '''PlasmaCalculator taking a Dataset as input.
    No smart behavior implemented here about dimensions,
        e.g. getting quantities depending on vector arithmetic or certain fluids will fail.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, mod_E, mod_B, E_perpmod_B, E_un0_perpmod_B,
                     m, n, mod_u, T, nusj,
                     m_neutral, n_neutral, mod_u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    # bases checked in self('bases')
    BASES_CHECK = ['ds', 'q', 'gamma', 'mod_E', 'mod_B', 'E_perpmod_B',
                    'm', 'n', 'mod_u', 'T', 'nusj',
                    'm_neutral', 'n_neutral', 'mod_u_neutral', 'T_neutral',
                    'nusn', 'E_un0_perpmod_B',
                    ]

    def __init__(self, ds, **kw_super):
        self.ds = ds
        super().__init__(**kw_super)

    def directly_loadable_vars(self):
        '''returns directly loadable variables from self.ds'''
        return list(self.ds.coords) + list(self.ds.data_vars)

    def load_fromfile(self, var, *args, **kw):
        '''load var from self.ds.'''
        if var in self.ds:
            return self.ds[var]
        else:
            raise LoadingNotImplementedError(f'var={var!r} not found in self.ds.')

    # # # KNOWN VARS / PATTERNS # # #
    @known_pattern(r'(mod|mag)2_(.+)', deps=[1])
    def get_mod2(self, var, *, _match=None):
        '''square of a variable. mod2_var = mod_var**2.
        mag2_var = mag_var**2.
        '''
        # [TODO] should this be defined elsewhere? E.g. in DimensionlessPlasmaCalculator...
        # (it's only necessary to understand mod2_var syntax without knowing vector arithmetic.)
        mod, here = _match.groups()
        return self(f'{mod}_{here}')**2

    @known_var(deps=BASES_CHECK)
    def get_bases(self, **kw_get_vars):
        '''return dataset of all bases gettable based on self.ds.
        checks all vars from self.BASES_CHECK.
        '''
        bases = self.BASES_CHECK
        kw_get_vars.setdefault('missing_vars', 'ignore')  # it's okay if some bases are un-gettable.
        return self.get_vars(bases, **kw_get_vars)

    # # # DISPLAY # # #
    def __repr__(self):
        ds_sizes = dict(self.ds.sizes)
        return f'{type(self).__name__}(ds={type(self.ds).__name__} with sizes={ds_sizes}))'

    # # # MISC. CONVENIENT METHODS # # #
    def with_isel(self, isel_dict, **kw_init):
        '''returns new instance of type(self), initialized with self.ds.isel(isel_dict).
        Does NOT maintain behavior attrs from self.
        Equivalent: type(self)(self.ds.isel(isel_dict), **kw_init)
        '''
        return type(self)(self.ds.isel(isel_dict), **kw_init)

    def with_scaling(self, scaling_dict, **kw_init):
        '''returns new instance of type(self), scaling some vars from self.ds.
        Does NOT maintain behavior attrs from self.
        result is type(self)(scaled_ds, **kw_init), where
            scaled_ds = self.ds.assign({v: scaling_dict[v] * self.ds[v] for v in scaling_dict}).

        scaling_dict: dict
            keys should be data_var names.
            vals should be numbers, 1D arraylike of numbers, or DataArray.
            if 1D non-DataArray arraylike, replace by xr1d(np.array(val), name='{var}_mul')

        Examples:
            cc = FromDatasetCalculator(...)
            cc_scaled1 = cc.with_scaling({'n': 1e-2})  # simple: scale densities by 1e-2.
            # testing multiple scalings at once: add a dimension!
            cc_scaled2 = cc.with_scaling({'n': pc.xr1d([1, 1e-2, 1e-4], name='n_mul')})
            # shorthand for above; internally uses pc.xr1d, name='{var}_mul'.
            cc_scaled3 = cc.with_scaling({'n': [1, 1e-2, 1e-4]})  # equivalent to cc_scaled2.
        '''
        scales = scaling_dict.copy()
        for var, value in scaling_dict.items():
            if is_iterable(value) and not isinstance(value, xr.DataArray):
                scales[var] = xr1d(np.array(value), name=f'{var}_mul')
        scaled_ds = self.ds.assign({v: scales[v] * self.ds[v] for v in scales})
        return type(self)(scaled_ds, **kw_init)


### --------------------- Inferring Dimensions From Dataset --------------------- ###

class InfersSnapsFromDataset():
    '''adds self.init_snaps() which infers snaps from self.ds['snap'] if available.
        (if ds['snap'] contents are not Snap objects, infer 't' from ds['t'] too if available.)
    '''
    snap_list_cls = SnapList

    def __init__(self, ds, **kw_super):
        super().__init__(ds, **kw_super)
        self.init_snaps()

    def init_snaps(self):
        '''initialize snaps from self.ds['snap'] if available.
        (Otherwise, self will have the default self.snap=None, self.snaps=None.)
        '''
        if 'snap' in self.ds:
            self.snaps = self.snap_list_cls.from_array(self.ds['snap'])
            self.snap = self.snaps[0] if self.ds['snap'].ndim == 0 else None

    def load_direct(self, var, *args, **kw):
        '''load var directly from self.ds if possible. slice snap dimension based on self.snap.'''
        result = super().load_direct(var, *args, **kw)
        if (self.snap is not self.snaps) and ('snap' in result.coords):
            result = xarray_sel(result, snap=self.snap)
        return result


class InfersFluidsFromDataset():
    '''adds self.init_fluids() which infers fluids and jfluids from self.ds['fluid'] and 'jfluid' if available.'''
    fluid_list_cls = FluidList
    jfluid_list_cls = alias('fluid_list_cls')

    def __init__(self, ds, **kw_super):
        super().__init__(ds, **kw_super)
        self.init_fluids()

    def init_fluids(self):
        '''initialize fluids and jfluids from self.ds['fluid'] and ds['jfluid'] if available.
        (Otherwise, self will have the default: self.fluid, fluids, jfluid, and jfluids=None.)
        '''
        if 'fluid' in self.ds:
            self.fluids = self.fluid_list_cls.from_array(self.ds['fluid'])
            self.fluid = self.fluids[0] if self.ds['fluid'].ndim == 0 else None
        if 'jfluid' in self.ds:
            self.jfluids = self.jfluid_list_cls.from_array(self.ds['jfluid'])
            self.jfluid = self.jfluids[0] if self.ds['jfluid'].ndim == 0 else None

    def load_direct(self, var, *args, **kw):
        '''load var directly from self.ds if possible. slice fluid & jfluid dims based on self.fluid & jfluids.'''
        result = super().load_direct(var, *args, **kw)
        if (self.fluid is not self.fluids) and ('fluid' in result.coords):
            result = xarray_sel(result, fluid=self.fluid)
        if (self.jfluid is not self.jfluids) and ('jfluid' in result.coords):
            result = xarray_sel(result, jfluid=self.jfluid)
        return result


class InfersComponentsFromDataset():
    '''adds self.init_components() which infers components from self.ds['component'] if available.'''
    component_list_cls = ComponentList

    def __init__(self, ds, **kw_super):
        super().__init__(ds, **kw_super)
        self.init_components()

    def init_components(self):
        '''initialize components from self.ds['component'] if available.
        (Otherwise, self will have the default self.component=None, self.components=None.)
        '''
        if 'component' in self.ds:
            self.components = self.component_list_cls.from_array(self.ds['component'])
            self.component = self.components[0] if self.ds['component'].ndim == 0 else None

    def load_direct(self, var, *args, **kw):
        '''load var directly from self.ds if possible. slice component dimension based on self.component.'''
        result = super().load_direct(var, *args, **kw)
        if (self.component is not self.components) and ('component' in result.coords):
            result = xarray_sel(result, component=self.component)
        return result


### --------------------- Dimensional From Dataset Calculators --------------------- ###

class ComponentHavingFromDatasetCalculator(InfersComponentsFromDataset,
                                           DimensionlessFromDatasetCalculator,
                                           ComponentHavingPlasmaCalculator):
    '''DimensionlessFromDatasetCalculator but with vector arithmetic and derivatives.
    Infers components from dataset if possible.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, E, B, m, n, u, T, nusj,
                     m_neutral, n_neutral, u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    BASES_CHECK = ['ds', 'q', 'gamma', 'E', 'B', 'm', 'n', 'u', 'T', 'nusj',
                    'm_neutral', 'n_neutral', 'u_neutral', 'T_neutral',
                    'nusn', 'E_un0',]
    # all other functionality inherited by super().


class FromDatasetCalculator(InfersSnapsFromDataset,
                            ComponentHavingFromDatasetCalculator,
                            PlasmaCalculator):
    '''PlasmaCalculator taking a Dataset as input. Knows about snaps and components dimensions.
    Infers snaps and components from dataset if possible.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, E, B, m, n, u, T, nusj,
                         m_neutral, n_neutral, u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    pass


class MultifluidFromDatasetCalculator(InfersFluidsFromDataset,
                                      FromDatasetCalculator,
                                      MultifluidPlasmaCalculator):
    '''PlasmaCalculator taking a Dataset as input. Knows about snaps, components, and fluids.
    Infers snaps, components, fluids, and jfluids from dataset if possible.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, E, B, m, n, u, T, nusj,
                         m_neutral, n_neutral, u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    pass


class SnaplessMultifluidFromDatasetCalculator(InfersFluidsFromDataset,
                                              ComponentHavingFromDatasetCalculator,
                                              MultifluidPlasmaCalculator):
    '''MultifluidFromDatasetCalculator but without snaps.
    Has all other features of MultifluidFromDatasetCalculator.
    Infers components, fluids, and jfluids from dataset if possible.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, E, B, m, n, u, T, nusj,
                         m_neutral, n_neutral, u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    pass


class VectorlessFromDatasetCalculator(InfersSnapsFromDataset,
                                      DimensionlessFromDatasetCalculator,
                                      VectorlessPlasmaCalculator):
    '''FromDatasetCalculator but without vector components/arithmetic/derivatives.
    Has all other features of FromDatasetCalculator.
    Infers snaps from dataset if possible.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, mod_E, mod_B, E_perpmod_B, E_un0_perpmod_B,
                     m, n, mod_u, T, nusj,
                     m_neutral, n_neutral, mod_u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    pass


class VectorlessMultifluidFromDatasetCalculator(InfersFluidsFromDataset,
                                                VectorlessFromDatasetCalculator,
                                                VectorlessMultifluidPlasmaCalculator):
    '''MultifluidFromDatasetCalculator but without vector components/arithmetic/derivatives.
    Has all other features of MultifluidFromDatasetCalculator.
    Infers snaps, fluids, and jfluids from dataset if possible.

    ds: xarray.Dataset
        self(var) looks in self.ds when can't find another way to compute var.
        For base vars, always checks ds first.
        (base vars): ds, q, gamma, mod_E, mod_B, E_perpmod_B, E_un0_perpmod_B,
                     m, n, mod_u, T, nusj,
                     m_neutral, n_neutral, mod_u_neutral, T_neutral.
        For simple derived vars, check ds first; compute from base vars if missing.
        (simple derived vars): r, p, P, Tjoule, e, nusn, nq, Jf, J, E_un0.
    '''
    pass
