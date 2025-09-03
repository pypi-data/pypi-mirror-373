"""
File Purpose: calculator for analyzing results of instability theory.
[TODO] this should probably go in the same place as addons.instability_tools code,
    however DimensionlessFromDatasetCalculator currently inherits from AddonsLoader.
    Would probably require refactoring AddonsLoader...
    (e.g., maybe subclasses of AddonsLoader should inject their known_vars
        at the same priority level as AddonsLoader known_vars?)
"""
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .from_dataset import (
    MultifluidFromDatasetCalculator,
    VectorlessMultifluidFromDatasetCalculator,
)
from ..defaults import DEFAULTS
from ..dimensions import XHAT, YHAT, ZHAT
from ..plotting import cmap, title_from_coords
from ..quantities import magnitude
from ..errors import (
    LoadingNotImplementedError, InputConflictError,
    PlottingAmbiguityError,
)
from ..tools import (
    simple_property,
    xarray_min, xarray_drop_vars, xarray_sel,
    xarray_at_min_of, xarray_at_max_of,
)

### --------------------- VectorlessInstabilityCalculator --------------------- ###

class VectorlessInstabilityCalculator(VectorlessMultifluidFromDatasetCalculator):
    '''calculator for analyzing results of instability theory.
    (Assumes itAccessor from instability_tools has been imported;
        some methods use syntax like, e.g., array.it.growth.)

    ds: xarray.Dataset
        should probably have all relevant base vars (& simple derived vars).
        Possibilities include:
            ds, m, q, gamma, n, mod_u, T, nusj, nusn, mod_E, mod_B, mod_E_un0, E_un0_perpmod_B,
            m_n or m_neutral, n_n or n_neutral, mod_u_n or mod_u_neutral, T_n or T_neutral.

        Probably should also have omega and k info.
    '''
    # # # CREATION OPTIONS # # #
    def __init__(self, ds, **kw_super):
        ds = self.assign_bases(ds)
        super().__init__(ds, **kw_super)

    @staticmethod
    def assign_bases(ds):
        '''return copy of ds, with some missing base vars assigned based on values in ds, if possible.
        Possibilities (only do it if all required values are present):
            q = skappa * m * nusn / mod_B
        '''
        if all([var in ds for var in ['m', 'mod_B', 'skappa', 'nusn']]):
            ds = ds.assign(q=ds['skappa'] * ds['m'] * ds['nusn'] / ds['mod_B'])
        return ds

    # # # VARS WHICH SHOULD COME FIRST # # #
    # (order matters. Check for these vars first.)

    @known_pattern(r'(.+)_at_kmax_of_(.+)', deps=[0,1])  # '{var}_at_kmax_of_{ref}'
    def get_var_at_kmax_of_ref(self, var, *, _match=None):
        '''var_at_kmax_of_ref --> self(var) at argmax of self(ref),
        taking argmax across all kdims in self(ref).
        For more precise control, consider directly using xarray_at_max_of.
        '''
        here, ref = _match.groups()
        refval = self(ref)
        return xarray_at_max_of(self(here), refval, refval.it.kdims)

    @known_pattern(r'(.+)_at_kmin_of_(.+)', deps=[0,1])  # '{var}_at_kmin_of_{ref}'
    def get_var_at_kmin_of_ref(self, var, *, _match=None):
        '''var_at_kmin_of_ref --> self(var) at argmin of self(ref),
        taking argmin across all kdims in self(ref).
        For more precise control, consider directly using xarray_at_min_of.
        '''
        here, ref = _match.groups()
        refval = self(ref)
        return xarray_at_min_of(self(here), refval, refval.it.kdims)

    # # # SPATIAL SCALE (need for timescales & compare to k) # # #
    cls_behavior_attrs.register('dspace_mode')
    DSPACE_MODE_OPTIONS = {
        'ds': '''self.load_direct('ds'). I.e. use self.ds['ds'].''',
        'k_at_growmax': '''infer from |k| at location (in k-space) of max growth. ds = 2 pi / |k|.''',
        'ldebye': '''infer from self('ldebye').''',
        'ldebye_total': '''infer from self('ldebye_total').''',
        'ldebye_minf': '''infer from self('ldebye'), taking min across all fluids.''',
        'eqperp_ldebye': '''infer from self('eqperp_ldebye').''',
        'eqperp_ldebye_total': '''infer from self('eqperp_ldebye_total').''',
        'eqperp_ldebye_minf': '''infer from self('eqperp_ldebye'), taking min across all fluids.''',
    }
    dspace_mode = simple_property('_dspace_mode',
        setdefaultvia='_default_dspace_mode', validate_from='DSPACE_MODE_OPTIONS',
        doc='''mode for calculating spatial scale self('ds') (required by speed-based timescales).
        See self.DSPACE_MODE_OPTIONS for options.''')
    def _default_dspace_mode(self):
        '''default dspace_mode. 'ds' if in self.ds, else 'k_at_growmax'.'''
        return 'ds' if 'ds' in self.ds else 'k_at_growmax'

    _DSPACE_MODE_TO_DEPS = {
        'ds': [],
        'k_at_growmax': ['kmod_at_growmax'],
        'ldebye': ['ldebye'],
        'ldebye_total': ['ldebye_total'],
        'ldebye_minf': ['ldebye'],
        'eqperp_ldebye': ['eqperp_ldebye'],
        'eqperp_ldebye_total': ['eqperp_ldebye_total'],
        'eqperp_minf_ldebye': ['eqperp_ldebye'],
    }
    @known_var(attr_deps=[('dspace_mode', '_DSPACE_MODE_TO_DEPS')], aliases=['dspace'])
    def get_ds(self):
        '''spatial scale. (required by self('timescales') for speed-based timescales.)
        result depends on self.dspace_mode. See self.DSPACE_MODE_OPTIONS for options.
        '''
        mode = self.dspace_mode
        if mode == 'ds':
            result = self.load_direct('ds')
        elif mode == 'k_at_growmax':
            result = 2 * np.pi / self('kmod_at_growmax')
        elif mode == 'ldebye':
            result = self('ldebye')
        elif mode == 'eqperp_ldebye':
            result = self('eqperp_ldebye')
        elif mode == 'ldebye_total':
            result = self('ldebye_total')
        elif mode == 'eqperp_ldebye_total':
            result = self('eqperp_ldebye_total')
        elif mode == 'ldebye_minf':
            result = xarray_min(self('ldebye'), 'fluid', missing_dims='ignore')
        elif mode == 'eqperp_ldebye_minf':
            result = xarray_min(self('eqperp_ldebye'), 'fluid', missing_dims='ignore')
        else:
            raise LoadingNotImplementedError(f'dspace_mode={mode!r} not recognized.')
        return result.assign_attrs(dspace_mode=mode)

    @known_var(deps=['ds'])
    def get_minf_ds(self):
        '''spatial scale, taking minimum across all fluids (i.e. most restrictive length scale).
        result depends on self.dspace_mode. See self.DSPACE_MODE_OPTIONS for options.
        '''
        return xarray_min(self('ds'), 'fluid', missing_dims='ignore')

    # # # GROWTH VARS # # #
    @known_var
    def get_omega(self):
        '''omega, directly from self.ds. (probably: roots of dispersion relation.)'''
        return self.load_direct('omega')

    @known_var(deps=['imag_omega'])
    def get_growth(self):
        '''imaginary part of omega.
        Equivalent: self('imag_omega'). Also equivalent: self('omega').it.growth
        '''
        return self('omega').it.growth

    @known_var(deps=['imag_omega'])
    def get_growth_kmax(self):
        '''imaginary part of omega, maxxed across k dims.
        Equivalent: self('omega').it.growth_kmax()
        Also equivalent: self('growth_at_growmax')
        '''
        return self('omega').it.growth_kmax()

    @known_var(deps=['imag_omega'])
    def get_grows(self):
        '''boolean array telling where self('growth_kmax')>0.
        Equivalent: self('omega').it.grows()
        '''
        return self('omega').it.grows()

    @known_pattern(r'(.+)_at_growmax', deps=[0, 'growth'])  # '{var}_at_growmax'
    def get_at_growmax(self, var, *, _match=None):
        '''value of var at location (in-kspace) of max growth.
        self('var_at_growmax') = self('var').it.at_growmax(self('growth'))

        Also equivalent: self('var_at_kmax_of_growth')
        '''
        # [TODO][EFF] slice before computing self(here), instead of after. 
        here, = _match.groups()
        return self(here).it.at_growmax(self('growth'))


    # [TODO][FIX] if trying to do '(.+)_at_growmax_where_(.+)' pattern,
    #   it gets picked up by '(.+)_where_(.+)' pattern first, for some reason.
    # workaround for now: use 'var_at_kmax_of_(growth_where_condition)'
    # @known_pattern(r'(.+)_at_growmax_where_(.+)', deps=[0, 1, 'growth'])
    # def get_at_growmax_where(self, var, *, _match=None):
    #     '''value of var at location (in-kspace) of max growth where condition is also True.
    #     Equivalent: self('var').it.at_growmax(self('growth').where(self('condition')))
    #     Equivalent: self('var_at_kmax_of_(growth_where_condition)')
    #     '''
    #     here, condition = _match.groups()
    #     return self(f'{var}_at_kmax_of_(growth_where_{condition})')

    @known_pattern(r'(.+)_within_kdebye', deps=[0, 'kmod', 'eqperp_ldebye'])
    def get_var_within_kdebye(self, var, *, _match=None):
        '''self(var) within |k| < eqperp_kdebye (==k corresponding to eqperp_ldebye).
        values at larger |k| are replaced with np.nan.
        '''
        here, = _match.groups()
        return self(f'{here}_where_(kmod<l2k_eqperp_ldebye)')

    @known_pattern(r'(.+)_within_kmfp', deps=[0, 'kmod', 'eqperp_lmfp'])
    def get_var_within_kmfp(self, var, *, _match=None):
        '''self(var) within |k| < eqperp_kmfp (==k corresponding to eqperp_lmfp).
        values at larger |k| are replaced with np.nan.
        '''
        here, = _match.groups()
        return self(f'{here}_where_(kmod<l2k_eqperp_lmfp)')

    # # # WAVEVECTOR VARS # # #
    @known_pattern(r'k2l_(.+)', deps=[0])  # k2l_var --> 2 * np.pi / var
    @known_pattern(r'l2k_(.+)', deps=[0])  # k2l_var --> 2 * np.pi / var
    def get_k2l(self, var, *, _match=None):
        '''convert from wavenumber to length, or vice versa.
        k2l_var = 2 pi / var.
        l2k_var = 2 pi / var.
        '''
        here, = _match.groups()
        return 2 * np.pi / self(here)

    @known_var
    def get_kmod(self):
        '''|k|, from self.ds kmod-related coord.
        (if self.ds tells 'log_kmod', returns 10**self.ds['log_kmod'].rename('kmod').
        else, returns self.ds['kmod'], unchanged.)
        Equivalent: self.ds.it.kmod
        '''
        return self.ds.it.kmod

    @known_var
    def get_kang(self):
        '''k angle, from self.ds kang-related coord.
        Equivalent: self.ds.it.kang
        '''
        return self.ds.it.kang

    @known_var(deps=['kang'])
    def get_khat(self):
        '''unit vector in direction of k.
        Roughly: self.ds.it.khat(), then sel(component=self.component)
        '''
        return xarray_sel(self.ds.it.khat(), component=self.component)

    @known_var(deps=['kmod', 'khat'])
    def get_k(self):
        '''k (vector). Inferred from kmod and kang.
        Roughly: self.ds.it.k(), then sel(component=self.component)
        Equivalent: self('kmod') * self('khat')
        '''
        return xarray_sel(self.ds.it.k(), component=self.component)

    # # # WAVE VELOCITY VARS # # #
    @known_var(deps=['real_omega', 'kmod'])
    def get_smod_vphase(self):
        '''signed magnitude of phase velocity: real(omega) / |k|.
        Phase velocity tells wave propagation speed. Group velocity tells wave envelope speed.
        Equivalent: self('omega').it.smod_vphase()
        See also: mod_vphase, vphase
        '''
        return self('omega').it.smod_vphase()

    @known_var(deps=['real_omega', 'kmod'], aliases=['mag_vphase'])
    def get_mod_vphase(self):
        '''magnitude of phase velocity: |real(omega) / |k||.
        Phase velocity tells wave propagation speed. Group velocity tells wave envelope speed.
        Equivalent: self('omega').it.mod_vphase()
        See also: smod_vphase, vphase
        '''
        return self('omega').it.mod_vphase()

    @known_var(deps=['real_omega', 'k'])
    def get_vphase(self):
        '''phase velocity (vector): vphase = (real(omega) / |k|) * khat.
        Phase velocity tells wave propagation speed. Group velocity tells wave envelope speed.
        Equivalent: self('omega').it.vphase()
        See also: smod_vphase, mod_vphase
        '''
        return self('omega').it.vphase()

    # # # GROWTH SPACESCALE VARS # # # 
    @known_var(deps=['kmod_at_growmax'])
    def get_spacescale_growth(self):
        '''length scale where growth is maximized: 2 pi / |k| at max growth.'''
        return 2 * np.pi / self('kmod_at_growmax')

    @known_var(deps=['spacescale_growth', 'minf_ds'])
    def get_spacesteps_growth(self):
        '''number of spacesteps (e.g. grid cells) needed to resolve length scale with max growth rate.
        Equivalent: self('spacescale_growth') / self('minf_ds').
        result depends on self.dspace_mode.

        Suggestion: if simulation grid cells have width ds, use N=safety * spacesteps_growth,
            with safety > 1 (e.g. safety = 10); safety will be approx. number of waves across the box.
        See also: self('ldebyesteps_growth'), self('eqperp_ldebyesteps_growth')
        '''
        return (self('spacescale_growth') / self('minf_ds')).assign_attrs(dspace_mode=self.dspace_mode)

    @known_var(deps=['spacescale_growth', 'ldebye'])
    def get_ldebyesteps_growth(self):
        '''number of Debye lengths needed to resolve length scale with max growth rate.
        Equivalent: self('spacescale_growth') / self('ldebye').
        Equivalent: self('spacesteps_growth', dspace_mode='ldebye').
        See also: self('spacesteps_growth'), self('eqperp_ldebyesteps_growth')
        '''
        return self('spacescale_growth') / self('ldebye')

    @known_var(deps=['spacescale_growth', 'eqperp_ldebye'])
    def get_eqperp_ldebyesteps_growth(self):
        '''number of eqperp Debye lengths needed to resolve length scale with max growth rate.
        Equivalent: self('spacescale_growth') / self('eqperp_ldebye').
        Equivalent: self('spacesteps_growth', dspace_mode='eqperp_ldebye').
        See also: self('spacesteps_growth'), self('ldebyesteps_growth')
        '''
        return self('spacescale_growth') / self('eqperp_ldebye')

    # # # GROWTH TIMESCALE VARS # # #
    TIMESCALE_VARS = VectorlessMultifluidFromDatasetCalculator.TIMESCALE_VARS.copy()
    if 'timescale_vtherm' in TIMESCALE_VARS:
        TIMESCALE_VARS.remove('timescale_vtherm')  # use eqperp_vtherm instead.
        TIMESCALE_VARS.append('timescale_eqperp_vtherm')
    TIMESCALE_VARS.extend(['timescale_vphase', 'timescale_growth'])

    @known_var(deps=['dsmin_for_timescales', 'mod_vphase_at_growmax'])
    def get_timescale_vphase(self):
        '''timescale from phase speed for waves at k with largest growthrate.
        timescale_vphase = dsmin / mod_vphase_at_growmax.
        '''
        return self('dsmin_for_timescales') / self('mod_vphase_at_growmax')

    @known_var(deps=['growth_kmax'])
    def get_timescale_growth(self):
        '''amount of time required for growth by a factor of e, at k with largest growthrate.
        Equivalent to 1/self('growth_kmax').
        Negative values indicate regions where growth rate is negative;
            consider using self('where_grows_timescale_growth') instead.
        '''
        return 1 / self('growth_kmax')

    @known_var(deps=['timescale_growth', 'minf_timescale'])
    def get_timesteps_growth(self):
        '''number of timesteps needed to see growth by a factor of e,
        assuming timestep = self('minf_timescale').
        Equivalent to self('timescale_growth') / self('minf_timescale').
        '''
        return self('timescale_growth') / self('minf_timescale')

    @known_var(deps=['timesteps_growth', 'spacesteps_growth'])
    def get_spacetimesteps_growth(self):
        '''number of "cells" across space AND time required to simulate growth. (Assumes 2D)
        Equivalent: self('spacesteps_growth')**2 * self('timesteps_growth').
        Result depends on self.dspace_mode.

        Note: if later applying safety factors to space, multiply result by safety**2.
            (e.g. might want to multiply spacesteps_growth 10 to see 10 waves in space, not just 1;
             to reflect that change in 'spacetimesteps_growth', need to multiply by 10**2 instead.)
        '''
        return self('spacesteps_growth')**2 * self('timesteps_growth')

    # # # NEW CALCULATOR VARS # # #
    BASES_CHECK = ['k', 'omega'] + list(VectorlessMultifluidFromDatasetCalculator.BASES_CHECK)
    # putting omega first ensures we keep all k dim info during self('bases').

    @known_var(deps=BASES_CHECK)
    def get_bases(self, **kw_get_vars):
        '''return dataset of all bases gettable based on self.ds.
        checks all vars from self.BASES_CHECK.
        '''
        return super().get_bases(**kw_get_vars)

    # # # ROSENBERG # # #
    @known_var(deps=['rosenberg_n_margin', 'ionnefrac_tiny'], ignores_dims='fluid')
    def get_rosenberg_n_scaler(self):
        '''return factor to DIVIDE all ion densities by, to push to rosenberg=1,
        for the ion with the most restrictive value for rosenberg criterion,
            ignoring all ions with tiny nnefrac.
            (i.e. ignore if n/ne < self.nnefrac_tiny_thresh. Default 0.01.)
        
        Equivalent: self('rosenberg_n_margin_where_not_nnefrac_tiny', fluid=self.fluids.ions()).min('fluid')

        densities scaling (of charged species) is "safe" for farley-buneman when rosenberg << 1,
            i.e. in that case it doesn't noticeably affect the physics.
        Suggestion: scale all (charged) densities by n_new = n_old / (safety * rosenberg_n_scaler),
            with safety less than 1, e.g. safety = 0.1.
        '''
        n_margins = self('rosenberg_n_margin_where_not_nnefrac_tiny', fluid=self.fluids.ions())
        return xarray_min(n_margins, 'fluid', missing_dims='ignore')

    # # # TITLE # # #
    default_title_width = simple_property('_default_title_width', default=80,
        doc='''default width for self._default_title(). Default: 80.''')

    title = simple_property('_title', setdefaultvia='_default_title',
        doc='''title for plots. Default: title_from_coords(self.ds, width=80)
        (uses self.default_title_width, which can also be edited if desired.)
        del self.title to reset to default.''')
    def _default_title(self):
        '''default title for plots. Uses title_from_coords.'''
        return title_from_coords(self.ds, width=self.default_title_width)


### --------------------- InstabilityCalculator --------------------- ###

class InstabilityCalculator(VectorlessInstabilityCalculator,
                            MultifluidFromDatasetCalculator):
    '''instability calculator which also includes vector components.

    ds: xarray.Dataset
        should probably have all relevant base vars (& simple derived vars).
        Possibilities include:
            ds, m, q, gamma, n, u, T, nusj, nusn, E, B, E_un0,
            m_n or m_neutral, n_n or n_neutral, u_n or u_neutral, T_n or T_neutral.
    '''
    BASES_CHECK = ['k', 'omega'] + list(MultifluidFromDatasetCalculator.BASES_CHECK)

    @staticmethod
    def assign_bases(ds):
        '''return copy of ds, with some missing base vars assigned based on values in ds, if possible.
        Possibilities (only do it if all required values are present):
            q = skappa * m * nusn / mod_B   (will do mod(B) if B in ds but mod_B is not.)
            if component in ds and ds['component'] == ['Ehat', '-ExBhat']:
                replace 'Ehat' component with XHAT
                replace '-ExBhat' component with -YHAT
                B = ZHAT * mod_B
                E = XHAT * mod_E
                E_un0 = XHAT * E_un0_perpmod_B
            if component NOT in ds:
                B = ZHAT * mod_B
                E = XHAT * mod_E
                E_un0 = XHAT * E_un0_perpmod_B
            [TODO] further generalize component handling?
        '''
        if all([var in ds for var in ['m', 'mod_B', 'skappa', 'nusn']]):
            ds = ds.assign(q=ds['skappa'] * ds['m'] * ds['nusn'] / ds['mod_B'])
        elif all([var in ds for var in ['m', 'B', 'skappa', 'nusn']]):
            ds = ds.assign(q=ds['skappa'] * ds['m'] * ds['nusn'] / magnitude(ds['B']))
        # check if component needs to be converted for E & B...
        if 'component' in ds and ds['component'].size==2 and np.all(ds['component'] == ['Ehat', '-ExBhat']):
            to_assign = {}
            for varname, val in ds.data_vars.items():
                if 'component' in val.coords:
                    to_assign[varname] = val.isel(component=0)*XHAT + val.isel(component=1)*(-YHAT)
            ds = xarray_drop_vars(ds, to_assign, drop_unused_dims=True)  # make sure the old 'component' dim goes away.
            ds = ds.assign(to_assign)
            if 'mod_B' in ds:
                B = ZHAT * ds['mod_B']
                if 'B' in ds and not np.allclose(ds['B'], B):
                    raise InputConflictError('B conflicts with mod_B')
                ds = ds.assign(B=B)
            if 'mod_E' in ds:
                E = XHAT * ds['mod_E']
                if 'E' in ds and not np.allclose(ds['E'], E):  # [TODO] encapsulte instead of repeating...
                    raise InputConflictError('E conflicts with mod_E')
                ds = ds.assign(E=E)
            if 'E_un0_perpmod_B' in ds:
                E_un0 = XHAT * ds['E_un0_perpmod_B']
                if 'E_un0' in ds and not np.allclose(ds['E_un0'], E_un0):
                    raise InputConflictError('E_un0 conflicts with E_un0_perpmod_B')
                ds = ds.assign(E_un0=E_un0)
        elif 'component' not in ds:
            if 'mod_B' in ds:
                B = ZHAT * ds['mod_B']
                if 'B' in ds and not np.allclose(ds['B'], B):
                    raise InputConflictError('B conflicts with mod_B')
                ds = ds.assign(B=B)
            if 'mod_E' in ds:
                E = XHAT * ds['mod_E']
                if 'E' in ds and not np.allclose(ds['E'], E):
                    raise InputConflictError('E conflicts with mod_E')
                ds = ds.assign(E=E)
            if 'E_un0_perpmod_B' in ds:
                E_un0 = XHAT * ds['E_un0_perpmod_B']
                if 'E_un0' in ds and not np.allclose(ds['E_un0'], E_un0):
                    raise InputConflictError('E_un0 conflicts with E_un0_perpmod_B')
                ds = ds.assign(E_un0=E_un0)
        return ds

    # # # PLOTTERS # # #
    NMUL_TIMELINES_STYLE = {
        'cycles': [{
            'color': cmap('tab10').colors[:5],
            'markersize': [18,15,12,10,8],
            'markeredgewidth': [2,1.5,1.5,1,1],
        }],
    }

    @known_plotter(kinds=['timelines', 'k', 'at_growmax', 'n_mul'], cost=11)
    def plot_kmod_at_growmax(ec, **kw_plot_settings):
        '''timelines of kmod_at_growmax vs n_mul. (log-log plot.)
        Also includes lines for each fluid, for:
            kmod_at_growmax with kmod limited by kmfp or kdebye, i.e.:
                kmod_at_kmax_of_growth_within_eqperp_kmfp,
                kmod_at_kmax_of_growth_within_eqperp_ldebye,
            eqperp_kmfp and eqperp_ldebye, i.e.:
                l2k_eqperp_lmfp,
                l2k_eqperp_ldebye,
        '''
        plt.figure(figsize=(9, 6))
        arr = ec('log10_kmod_at_growmax')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')        
        n_mul = arr.coords['n_mul']
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, label='(full)',
                         color='black', lw=8, alpha=0.2,
                         **kw_plot_settings)
        plt.grid()
        # kmfp limited and kdebye limited
        arr = ec('log10_kmod_at_kmax_of_growth_within_kdebye')
        arr.pc.timelines(tCOORD, label='(kdebye_limited)',
                         marker='X', fillstyle='none',
                         **{**ec.NMUL_TIMELINES_STYLE, **kw_plot_settings})
        arr = ec('log10_kmod_at_kmax_of_growth_within_kmfp')
        arr.pc.timelines(tCOORD, label='(kmfp_limited)',
                         marker='o', fillstyle='none',
                         **{**ec.NMUL_TIMELINES_STYLE, **kw_plot_settings})
        arr = ec('log10_l2k_eqperp_lmfp')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            arr = arr * xr.ones_like(n_mul)
        arr.pc.timelines(tCOORD, label='(mfp)',
                         cycles=[DEFAULTS.PLOT.TIMELINES_CYCLE1],
                         color='blue', lw=2, alpha=0.3, zorder=-5,
                         **kw_plot_settings)

        arr = ec('log10_l2k_eqperp_ldebye')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            arr = arr * xr.ones_like(n_mul)
        arr.pc.timelines(tCOORD, label='(ldebye)',
                         cycles=[DEFAULTS.PLOT.TIMELINES_CYCLE1],
                         color='red', lw=2, alpha=0.3, zorder=-5,
                         **kw_plot_settings)
        # better labels
        plt.title(f'log10_kmod [{ec.units}]\n{ec.title}')
        plt.ylabel(f'log10_kmod_at_growmax [{ec.units}]')
        plt.xlabel('log10_n_mul')
        return result

    @known_plotter(kinds=['timelines', 'k', 'at_growmax', 'n_mul'], cost=10)
    def plot_kang_at_growmax(ec, **kw_plot_settings):
        '''timelines of kang_at_growmax vs n_mul. (using log of n_mul)
        Also includes lines for each fluid, for:
            kang_at_growmax with kmod limited by kmfp or kdebye, i.e.:
                kang_at_kmax_of_growth_within_eqperp_kmfp,
                kang_at_kmax_of_growth_within_eqperp_ldebye,
        '''
        plt.figure(figsize=(9, 4))
        arr = ec('rad2deg_kang_at_growmax')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, label='(full)',
                         color='black', lw=8, alpha=0.2,
                         **kw_plot_settings)
        plt.grid()
        # kmfp limited and kdebye limited
        arr = ec('rad2deg_kang_at_kmax_of_growth_within_kdebye')
        arr.pc.timelines(tCOORD, label='(kdebye_limited)',
                         marker='X', fillstyle='none',
                         **{**ec.NMUL_TIMELINES_STYLE, **kw_plot_settings})
        arr = ec('rad2deg_kang_at_kmax_of_growth_within_kmfp')
        arr.pc.timelines(tCOORD, label='(kmfp_limited)',
                         marker='o', fillstyle='none',
                         **{**ec.NMUL_TIMELINES_STYLE, **kw_plot_settings})
        # better labels
        plt.title(f'kang [deg]\n{ec.title}')
        plt.ylabel('kang_at_growmax [deg]')
        plt.xlabel('log10_n_mul')
        return result

    @known_plotter(kinds=['timelines', 'growth', 'at_growmax', 'n_mul'], cost=10)
    def plot_growth_at_growmax(ec, **kw_plot_settings):
        '''timelines of growth_at_growmax vs n_mul. (using log of n_mul)
        Also includes lines for each fluid, for:
            growth_at_growmax with kmod limited by kmfp or kdebye, i.e.:
                growth_at_kmax_of_growth_within_eqperp_kmfp,
                growth_at_kmax_of_growth_within_eqperp_ldebye,
        '''
        plt.figure(figsize=(9, 5))
        arr = ec('log10_growth_at_growmax')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, label='(full)',
                         color='black', lw=8, alpha=0.2,
                         **kw_plot_settings)
        plt.grid()
        # kmfp limited and kdebye limited
        arr = ec('log10_growth_at_kmax_of_growth_within_kdebye')
        arr.pc.timelines(tCOORD, label='(kdebye_limited)',
                         marker='X', fillstyle='none',
                         **{**ec.NMUL_TIMELINES_STYLE, **kw_plot_settings})
        arr = ec('log10_growth_at_kmax_of_growth_within_kmfp')
        arr.pc.timelines(tCOORD, label='(kmfp_limited)',
                         marker='o', fillstyle='none',
                         **{**ec.NMUL_TIMELINES_STYLE, **kw_plot_settings})
        # better labels
        plt.title(f'log10_growth [{ec.units}]\n{ec.title}')
        plt.ylabel(f'log10_growth_at_growmax [{ec.units}]')
        plt.xlabel('log10_n_mul')
        return result

    @known_plotter(kinds=['2D', 'subplots', 'growth', 'n_mul'], cost=21)
    def plot_growthplots(ec, *, share_vlims='row', **kw_plot_settings):
        '''ec.ds.it.growthplots(row='n_mul', wrap=6, **kw_plot_settings).
        Sets |k| plot lims to be the same on each plot,
            which is useful e.g. if |k| lims in ec.ds is based on kdebye, which varies with n_mul,
            e.g. from tfbi_solver(kres='mid', mod=dict(min=2*np.pi/1e2, max=(1.01, 'kdebye'))).solve()
        '''
        defaults = {
            'row': 'n_mul',
            'wrap': 6,
            'share_vlims': share_vlims,
            'suptitle_width': ec.default_title_width,
            'top': 1.1,  # fudge factor for prettier subplot spacing
        }
        log_kmod = ec.ds['log_kmod'] if 'log_kmod' in ec.ds else np.log10(ec.ds['kmod'])
        klims = [log_kmod.min().item(), log_kmod.max().item()]
        kw = {**defaults, **kw_plot_settings}
        return ec.ds.it.growthplots(y='log_kmod', ylim=klims, **kw)
