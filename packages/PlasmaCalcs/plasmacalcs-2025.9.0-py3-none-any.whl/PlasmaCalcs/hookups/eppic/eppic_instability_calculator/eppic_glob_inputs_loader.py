"""
File Purpose: loading global (i.e., fluid-independent) eppic.i inputs,
from values in an EppicInstabilityCalculator.
"""
import numpy as np
import xarray as xr

from ....errors import LoadingNotImplementedError
from ....other_calculators import InstabilityCalculator
from ....quantities import QuantityLoader
from ....tools import (
    simple_property, format_docstring,
    xarray_copy_kw, xarray_max, xarray_minimum,
)
from ....defaults import DEFAULTS


class EppicGlobInputsLoader(QuantityLoader):
    '''loads global (fluid-independent) eppic.i inputs, from values in an EppicInstabilityCalculator.'''

    # # # GLOB_INPUTS -- "DISPATCH" # # #

    # {varname: name for eppic.i file.}
    # with {x} indicating "replace with component (x, y, or z)",
    # name can be dict --> expect varname to expand into vars upon loading.
    # order here will be same order as used by eppic.i.
    GLOB_INPUTS = {
        # grid size in space
        'ndim_space': 'ndim_space',
        'safe_pow2_nspace': {
            'safe_nsubdomains': 'nsubdomains',
            'safe_pow2_nspace': 'n{x}',
        },
        'safe_dspace': 'd{x}',
        # grid size in time
        'safe_dt': 'dt',
        'safe_rounded_nt': 'nt',
        'safe_rounded_nout': 'nout',
        # physical parameters
        'm_neutral': 'm_neutral',
        'vth_neutral': 'vth_neutral',
        'B': 'B{x}',
        'E_un0': 'E{x}0_external',
        'fwidth': 'fwidth',  # (not physical, but related to E.)
        'fsteep': 'fsteep',  # (not physical, but related to E.)
        'eps0': 'eps',  # eps sets the units.
        # output-related vars (user probably never needs to touch these)
        'safe_iwrite': 'iwrite',
        'iread': 'iread',
        'hdf_output_arrays': 'hdf_output_arrays',
        'nout_avg': 'nout_avg',
        'npout': 'npout',
        'divj_out_subcycle': 'divj_out_subcycle',
    }

    @known_var(deps=GLOB_INPUTS)
    def get_glob_inputs(self):
        '''Dataset of global input values which got to eppic.i, here using PlasmaCalcs datavar names.
        Named & dimensioned here with PlasmaCalcs conventions,
            e.g. uses 'E_un0' which varies across 'component' dim,
            instead of labeling Ex0_external, Ey0_external, Ez0_external like in eppic.i.
        internally uses self.dspace_mode = self.safe_dspace_mode.
        Result data_vars names are the keys of self.GLOB_INPUTS.

        see also: eppici_glob, which uses eppic.i datavar names instead.
        '''
        with self.using(_cached_safe_dt=self('safe_dt')):  # [EFF] caching improves efficiency.
            return self(list(self.GLOB_INPUTS), dspace_mode=self.safe_dspace_mode)


    # # # SPATIAL SCALE: dx (and y and z) # # #

    cls_behavior_attrs.register('dspace_safety', default=DEFAULTS.EPPIC.DSPACE_SAFETY)
    dspace_safety = simple_property('_dspace_safety', setdefault=lambda: DEFAULTS.EPPIC.DSPACE_SAFETY,
        doc=f'''safety factor for safe dspace calculations. Larger is LESS safe.
        safe_dspace = unsafe_dspace * dspace_safety.
        Default: DEFAULTS.EPPIC.DSPACE_SAFETY (default: {DEFAULTS.EPPIC.DSPACE_SAFETY})''')

    @known_var
    def get_dspace_safety(self):
        '''safety factor for safe dspace calculations. Larger is LESS safe.
        safe_dspace = unsafe_dspace * dspace_safety.
        internally, value is stored (and can be adjusted) at self.dspace_safety.
        '''
        return xr.DataArray(self.dspace_safety)

    def _default_dspace_mode(self):
        '''default dspace_mode: 'safe_eqperp_ldebye_total'.'''
        return 'safe_eqperp_ldebye_total'

    @property
    def safe_dspace_mode(self):
        '''self.dspace_mode with 'safe_' prepended if self.dspace_mode doesn't already start with 'safe_'.'''
        mode = self.dspace_mode
        return mode if mode.startswith('safe_') else f'safe_{mode}'

    @property
    def unsafe_dspace_mode(self):
        '''self.dspace_mode with leading 'safe_' removed if self.dspace_mode starts with 'safe_'.'''
        mode = self.dspace_mode
        return mode[len('safe_'):] if mode.startswith('safe_') else mode

    DSPACE_MODE_OPTIONS = InstabilityCalculator.DSPACE_MODE_OPTIONS.copy()
    DSPACE_MODE_OPTIONS.update({f'safe_{k}': f'{k} * self.dspace_safety' for k in DSPACE_MODE_OPTIONS})
    _DSPACE_MODE_TO_DEPS = InstabilityCalculator._DSPACE_MODE_TO_DEPS.copy()
    _DSPACE_MODE_TO_DEPS.update({f'safe_{k}': ['dspace_safety'] + v for k, v in _DSPACE_MODE_TO_DEPS.items()})
    @known_var(attr_deps=[('dspace_mode', '_DSPACE_MODE_TO_DEPS')], aliases=['dspace'])
    def get_ds(self):
        '''spatial scale. (required by self('timescales') for speed-based timescales.)
        result depends on self.dspace_mode. See self.DSPACE_MODE_OPTIONS for options.
        '''
        mode = self.dspace_mode
        if mode.startswith('safe_'):
            safe_mode = mode
            mode = mode[len('safe_'):]
            safety = self('dspace_safety')
            with self.using(dspace_mode=mode):
                result = super().get_ds() * safety
            return result.assign_attrs(dspace_mode=safe_mode)
        else:
            return super().get_ds()

    @known_var(deps=['dspace', 'dspace_safety'])
    def get_safe_dspace(self):
        '''ds to use for simulation, including safety factor(s).
        Result depends on self.dspace_mode. See self.DSPACE_MODE_OPTIONS for options.
        Equivalent to self('dspace', dspace_mode=self.safe_dspace_mode).
        '''
        return self('dspace', dspace_mode=self.safe_dspace_mode)

    @known_var(deps=['dspace'])
    def get_unsafe_dspace(self):
        '''ds to use for simulation, without dspace_safety factor.
        Equivalent to self('dspace', dspace_mode=self.unsafe_dspace_mode).
        '''
        return self('dspace', dspace_mode=self.unsafe_dspace_mode)

    @known_var(deps=['safe_dspace'])
    def get_ds_for_timescales(self):
        '''spatial scale used when calculating timescales. Might be a vector, e.g. [dx, dy, dz].
        The method here returns self('safe_dspace').
        '''
        return self('safe_dspace')

    @known_var(deps=['safe_dspace', 'unsafe_dspace'])
    def get_direct_dspace_safety(self):
        '''direct_dspace_safety = safe_dspace / unsafe_dspace.'''
        return self('safe_dspace') / self('unsafe_dspace')


    # # # SPATIAL EXTENT: nx (and y and z) # # #

    cls_behavior_attrs.register('nspace_safety', default=DEFAULTS.EPPIC.NSPACE_SAFETY)
    nspace_safety = simple_property('_nspace_safety', setdefault=lambda: DEFAULTS.EPPIC.NSPACE_SAFETY,
        doc=f'''safety factor for safe Nspace calculations. Larger is MORE safe.
        safe_Nspace = unsafe_Nspace * nspace_safety.
        Default: DEFAULTS.EPPIC.NSPACE_SAFETY (default: {DEFAULTS.EPPIC.NSPACE_SAFETY})''')

    @known_var
    def get_nspace_safety(self):
        '''safety factor for safe Nspace calculations. Larger is MORE safe.
        safe_Nspace = unsafe_Nspace * nspace_safety.
        internally, value is stored (and can be adjusted) at self.nspace_safety.
        '''
        return xr.DataArray(self.nspace_safety)

    @known_var(deps=['spacescale_growth', 'safe_dspace'])
    def get_unsafe_Nspace(self):
        '''Nspace to use for simulation, without nspace_safety factor.
        unsafe_Nspace = spacescale_growth / safe_dspace.
        '''
        return self('spacescale_growth') / self('safe_dspace')

    @known_var(deps=['unsafe_Nspace', 'nspace_safety'])
    def get_safe_Nspace(self):
        '''number of grid cells (along each spatial dimension) to use for simulation,
        including safety factors(s).
        safe_Nspace = (spacescale_growth / safe_dspace) * nspace_safety
        '''
        return self('unsafe_Nspace') * self('nspace_safety')

    @known_var(deps=['safe_Nspace'])
    def get_safe_pow2_Nspace(self):
        '''number of grid cells (along each spatial dimension) to use for simulation,
        including safety factors, and ensuring result is a power of 2.
        (uses the smallest power of 2 such that result is still larger than safe_Nspace.)
        '''
        Nspace = self('safe_Nspace')
        return 2 ** np.ceil(np.log2(Nspace)).astype('int')

    @known_var(deps=['safe_pow2_Nspace', 'unsafe_Nspace'])
    def get_direct_nspace_safety(self):
        '''direct_nspace_safety = safe_pow2_Nspace / unsafe_Nspace.'''
        return self('safe_pow2_Nspace') / self('unsafe_Nspace')

    cls_behavior_attrs.register('nx_min', default=DEFAULTS.EPPIC.NX_MIN)
    nx_min = simple_property('_nx_min', setdefault=lambda: DEFAULTS.EPPIC.NX_MIN,
        doc=f'''minimum nx for input deck. Nx = nx * nsubdomains. See also: self.nsubdomains_max.
        Default: DEFAULTS.EPPIC.NX_MIN (default: {DEFAULTS.EPPIC.NX_MIN})''')

    cls_behavior_attrs.register('nsubdomains_max', default=DEFAULTS.EPPIC.NSUBDOMAINS_MAX)
    nsubdomains_max = simple_property('_nsubdomains_max', setdefault=lambda: DEFAULTS.EPPIC.NSUBDOMAINS_MAX,
        doc=f'''maximum nsubdomains for input deck. Nx = nx * nsubdomains. See also: self.nx_min.
        Default: DEFAULTS.EPPIC.NSUBDOMAINS_MAX (default: {DEFAULTS.EPPIC.NSUBDOMAINS_MAX})''')

    @known_var(deps=['safe_pow2_Nspace'])
    def get_safe_pow2_nspace(self):
        '''nx, ny, nz to use for simulation, including safety factors, and as a power of 2.
        result is a dataset of 'safe_pow2_nspace' and 'safe_nsubdomains'. nx is safe_Nx_sim/nsubdomains.
        result depends on self.nx_min and self.nsubdomains_max.
        if self('ndim_space')==2, also sets nz=1 everywhere.
        '''
        Nspace = self('safe_pow2_Nspace')
        if 'component' in Nspace.dims:
            raise LoadingNotImplementedError('[TODO] nspace from Nspace varying with component.')
        Nx = Nspace.assign_coords(component=self.components.get('x'))
        ny = Nspace.assign_coords(component=self.components.get('y'))
        nz = Nspace.assign_coords(component=self.components.get('z'))
        # break Nx into nx and nsubdomains...
        nx = self.nx_min
        nsubdomains = Nx // nx  # [TODO] assert nx evenly divides Nx.
        nsubdomains = np.minimum(nsubdomains, self.nsubdomains_max)
        nx = Nx // nsubdomains
        # if ndim_space==2, make nz==1...
        if self('ndim_space') == 2:
            nz = nz.copy(data=np.ones(nz.shape, dtype='int'))
        # make result:
        nspace = xr.concat([nx, ny, nz], dim='component')
        copy_kw = xarray_copy_kw(Nspace, array_to_dataset=True)
        return xr.Dataset({'safe_pow2_nspace': nspace, 'safe_nsubdomains': nsubdomains}, **copy_kw)

    @known_var(deps=['safe_pow2_nspace'])
    def get_safe_nsubdomains(self):
        '''nsubdomains to use for simulation. Nx = nx * nsubdomains.
        result depends on self.nx_min and self.nsubdomains_max.
        Also depends on self('safe_pow2_Nspace').
        '''
        return self('safe_pow2_nspace')['safe_nsubdomains']


    # # # TIME SCALE AND EXTENT: dt, nt # # #

    cls_behavior_attrs.register('dt_safety', default=DEFAULTS.EPPIC.DT_SAFETY)
    dt_safety = simple_property('_dt_safety', setdefault=lambda: DEFAULTS.EPPIC.DT_SAFETY,
        doc=f'''safety factor for safe dt calculations. Larger is LESS safe.
        safe_dt = unsafe_dt * dt_safety.
        Default: DEFAULTS.EPPIC.DT_SAFETY (default: {DEFAULTS.EPPIC.DT_SAFETY})''')

    @known_var
    def get_dt_safety(self):
        '''safety factor for safe dt calculations. Larger is LESS safe.
        safe_dt = unsafe_dt * dt_safety.
        internally, value is stored (and can be adjusted) at self.dt_safety.
        '''
        return xr.DataArray(self.dt_safety)

    @known_var(deps=['minf_timescale'])
    def get_unsafe_dt(self):
        '''dt to use for simulation, without dt_safety factor.
        unsafe_dt == minf_timescale.
        '''
        return self('minf_timescale')

    @known_var(deps=['dt_safety', 'unsafe_dt'])
    def get_safe_dt(self):
        '''dt to use for simulation, including safety factors: minf_timescale * dt_safety.
        result depends on self.dt_safety, as well as self.dspace_mode (for speed-based timescales).
        '''
        if hasattr(self, '_cached_safe_dt'):  # [EFF] if internally repeating safe_dt many times,
            return self._cached_safe_dt       # can do "with self.using(_cached_safe_dt=...):"
        return self('unsafe_dt') * self('dt_safety')

    @known_var(deps=['safe_dt', 'unsafe_dt'])
    def get_direct_dt_safety(self):
        '''safe_dt / unsafe_dt.'''
        return self('safe_dt') / self('unsafe_dt')

    cls_behavior_attrs.register('ntime_safety', default=DEFAULTS.EPPIC.NTIME_SAFETY)
    ntime_safety = simple_property('_ntime_safety', setdefault=lambda: DEFAULTS.EPPIC.NTIME_SAFETY,
        doc=f'''safety factor for safe nt calculations. Larger is MORE safe.
        safe_nt = unsafe_nt * ntime_safety.
        Default: DEFAULTS.EPPIC.NTIME_SAFETY (default: {DEFAULTS.EPPIC.NTIME_SAFETY})''')

    @known_var
    def get_ntime_safety(self):
        '''safety factor for safe nt calculations. Larger is MORE safe.
        safe_nt = unsafe_nt * ntime_safety.
        internally, value is stored (and can be adjusted) at self.ntime_safety.
        '''
        return xr.DataArray(self.ntime_safety)

    @known_var(deps=['timescale_growth'])
    def get_unsafe_nt(self):
        '''nt to use for simulation, excluding ntime_safety factor.
        unsafe_nt = timescale_growth / safe_dt
        '''
        return self('timescale_growth') / self('safe_dt')

    @known_var(deps=['unsafe_nt', 'ntime_safety'], aliases=['safe_ntime'])
    def get_safe_nt(self):
        '''nt to use for simulation, including safety factors.
        safe_nt = (timescale_growth / safe_dt) * ntime_safety.
        result is not an int; for int see self('safe_rounded_nt')
        '''
        return self('unsafe_nt') * self('ntime_safety')

    @known_var(deps=['safe_nt', 'safe_rounded_nout'])
    def get_safe_rounded_nt(self):
        '''nt to use for simulation, including safety factors and rounding.
        Rounded up to nearest multiple of self('safe_rounded_nout').
        '''
        ntime = self('safe_nt')
        multiple = self('safe_rounded_nout')
        nmul = np.ceil(ntime / multiple)
        return (nmul * multiple).astype('int')

    @known_var(deps=['safe_rounded_nt', 'unsafe_nt'])
    def get_direct_ntime_safety(self):
        '''direct_ntime_safety = safe_rounded_nt / unsafe_nt.'''
        return self('safe_rounded_nt') / self('unsafe_nt')


    # # # SNAP SAVE FREQUENCY: nout # # #

    cls_behavior_attrs.register('nout_waveprop_safety', default=DEFAULTS.EPPIC.NOUT_WAVEPROP_SAFETY)
    nout_waveprop_safety = simple_property('_nout_waveprop_safety',
        setdefault=lambda: DEFAULTS.EPPIC.NOUT_WAVEPROP_SAFETY,
        doc=f'''safety factor for safe nout calculations. Larger is LESS safe.
        safe_nout = min(safe_nout_waveprop, safe_nout_growth);
        safe_nout_waveprop = unsafe_nout_waveprop * nout_waveprop_safety.
        Default: DEFAULTS.EPPIC.NOUT_WAVEPROP_SAFETY (default: {DEFAULTS.EPPIC.NOUT_WAVEPROP_SAFETY})''')

    cls_behavior_attrs.register('nout_growth_safety', default=DEFAULTS.EPPIC.NOUT_GROWTH_SAFETY)
    nout_growth_safety = simple_property('_nout_growth_safety',
        setdefault=lambda: DEFAULTS.EPPIC.NOUT_GROWTH_SAFETY,
        doc=f'''safety factor for safe nout calculations. Larger is LESS safe.
        safe_nout = min(safe_nout_waveprop, safe_nout_growth);
        safe_nout_growth = unsafe_nout_growth * nout_growth_safety.
        Default: DEFAULTS.EPPIC.NOUT_GROWTH_SAFETY (default: {DEFAULTS.EPPIC.NOUT_GROWTH_SAFETY})''')

    @known_var
    def get_nout_waveprop_safety(self):
        '''safety factor for safe_nout_waveprop. Larger is LESS safe.
        safe_nout = unsafe_nout * nout_safety.
        internally, value is stored (and can be adjusted) at self.nout_waveprop_safety.
        '''
        return xr.DataArray(self.nout_waveprop_safety)

    @known_var
    def get_nout_growth_safety(self):
        '''safety factor for safe_nout_growth. Larger is LESS safe.
        safe_nout = unsafe_nout * nout_safety.
        internally, value is stored (and can be adjusted) at self.nout_growth_safety.
        '''
        return xr.DataArray(self.nout_growth_safety)

    @known_var(deps=['nout_waveprop_safety', 'nout_growth_safety'])
    def get_nout_safety(self):
        '''dataset of safety factors for safe nout calculations. Larger is LESS safe.
        safe_nout = unsafe_nout * nout_safety.
        internally, values are at self.nout_waveprop_safety and self.nout_growth_safety.
        result has 'nout_waveprop_safety' and 'nout_growth_safety' data_vars.
        '''
        return self(['nout_waveprop_safety', 'nout_growth_safety'])

    @known_var(deps=['abs_real_omega_at_growmax'])
    def get_waveprop_time(self):
        '''time for wave to propagate 1 full wavelength, according to real(omega) at growmax.
        waveprop_time = 2*pi/|real(omega at growmax)|.
        '''
        return 2 * np.pi / self('abs_real_omega_at_growmax')

    @known_var(deps=['waveprop_time', 'safe_dt'])
    def get_unsafe_nout_waveprop(self):
        '''nout to resolve wave propagation, without nout_waveprop_safety factor.
        unsafe_nout_waveprop = waveprop_time / safe_dt.
        '''
        return self('waveprop_time') / self('safe_dt')

    @known_var(deps=['unsafe_nout_waveprop', 'nout_waveprop_safety'])
    def get_safe_nout_waveprop(self):
        '''safe number of timesteps between snapshots, to well-resolve wave propagation:
        safe_nout_waveprop = (waveprop_time / safe_dt) * nout_waveprop_safety.
        '''
        return self('unsafe_nout_waveprop') * self('nout_waveprop_safety')

    @known_var(deps=['timescale_growth', 'safe_dt'])
    def get_unsafe_nout_growth(self):
        '''nout to resolve growth rate, without nout_growth_safety factor.
        unsafe_nout_growth = timescale_growth / safe_dt.
        '''
        return self('timescale_growth') / self('safe_dt')

    @known_var(deps=['unsafe_nout_growth', 'nout_growth_safety'])
    def get_safe_nout_growth(self):
        '''safe number of timesteps between snapshots, to well-resolve growth rate:
        safe_nout_growth = (growth timescale / safe_dt) * nout_growth_safety.
        '''
        return self('unsafe_nout_growth') * self('nout_growth_safety')

    @known_var(deps=['safe_nout_waveprop', 'safe_nout_growth'])
    def get_safe_nout(self):
        '''safe number of timesteps between snapshots, to well-resolve physical processes:
            - wave motion (by a distance of 1 wavelength)
            - growth rate (1 e-folding of growth)
        safe_nout = min(safe_nout_waveprop, safe_nout_growth). (Rounding not handled here;
            see safe_rounded_nout for a rounded value appropriate for eppic.i files.)
        '''
        return xarray_minimum(self('safe_nout_waveprop'), self('safe_nout_growth'))

    cls_behavior_attrs.register('nout_multiple', default=DEFAULTS.EPPIC.NOUT_MULTIPLE)
    nout_multiple = simple_property('_nout_multiple', setdefault=lambda: DEFAULTS.EPPIC.NOUT_MULTIPLE,
        doc=f'''ensure safe_rounded_nout is a multiple of this value * max safe_pow2_subcycle.
        E.g., nout_multiple=5 causes nout to be a multiple of 10,
            assuming safe_pow2_subcycle > 1 for at least 1 specie
            (subcycle=2^N with N>0 --> subcycle * 5 will be divisible by 10).
        Use nout_multiple=1 to ignore this value and just use the max safe_pow2_subcycle requirement.
        Default: DEFAULTS.EPPIC.NOUT_MULTIPLE (default: {DEFAULTS.EPPIC.NOUT_MULTIPLE})''')

    @known_var(deps=['safe_nout'])
    @format_docstring(nout_multiple=DEFAULTS.EPPIC.NOUT_MULTIPLE)
    def get_safe_rounded_nout(self):
        '''number of timesteps between snapshots, suitable for use in eppic.i file.
        At most safe_nout, but rounds down to integer, and might round down further to ensure
        result is a multiple of self.nout_multiple * safe_pow2_subcycle for all fluids
            (eppic requires subcycling to evenly divide nout)
            (self.nout_multiple is set by user; default {nout_multiple}.
                Use self.nout_multiple=1 to ignore nout_multiple restriction.
                Either way, will always have safe_pow2_subcycle restriction.)
        '''
        nout = self('safe_nout')
        subcycle = xarray_max(self('safe_pow2_subcycle'), 'fluid')
        # ^ because all safe_pow2_subcycle vals are like 2^N, can just take the max :)
        multiple = self.nout_multiple * subcycle
        nmul = nout // multiple   # nmul = largest N such that N * multiple < safe_nout.
        return (nmul * multiple).astype('int')

    @known_var(deps=['safe_rounded_nout', 'unsafe_nout_waveprop'])
    def get_direct_nout_waveprop_safety(self):
        '''safe_rounded_nout / unsafe_nout_waveprop'''
        return self('safe_rounded_nout') / self('unsafe_nout_waveprop')

    @known_var(deps=['safe_rounded_nout', 'unsafe_nout_growth'])
    def get_direct_nout_growth_safety(self):
        '''safe_rounded_nout / unsafe_nout_growth'''
        return self('safe_rounded_nout') / self('unsafe_nout_growth')

    @known_var(deps=['direct_nout_waveprop_safety', 'direct_nout_growth_safety'])
    def get_direct_nout_safety(self):
        '''dataset containing direct_nout_waveprop_safety and direct_nout_growth_safety.'''
        with self.using(_cached_safe_dt=self('safe_dt')):  # [EFF] caching improves efficiency.
            return self(['direct_nout_waveprop_safety', 'direct_nout_growth_safety'])

    @known_var(deps=['safe_rounded_nout'])
    @format_docstring(default_iwrite_nsnap=DEFAULTS.EPPIC.IWRITE_NSNAP)
    def get_safe_iwrite(self):
        '''safe_iwrite = safe_rounded_nout * iwrite_nsnap.
        (someday, iwrite_nsnap might be directly in EPPIC, but it's not there yet.
            For now, default iwrite_nsnap = {default_iwrite_nsnap})
        '''
        return self('safe_rounded_nout') * self('iwrite_nsnap')
