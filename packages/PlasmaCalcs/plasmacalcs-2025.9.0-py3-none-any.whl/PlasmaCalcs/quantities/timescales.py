"""
File Purpose: calculating timescales, e.g. timescale from plasma oscillations.
(e.g., useful when trying to pick dt for a simulation)
"""
import numpy as np

from .quantity_loader import QuantityLoader
from ..errors import QuantCalcError, InputMissingError
from ..tools import (
    UNSET,
    xarray_min, xarray_minimum_of_datavars, xarray_varmin,
)

class TimescalesLoader(QuantityLoader):
    '''timescales, e.g. timescale from wplasma, or from vthermal / dx.
    Spatial scales come from self('ds')
        which must be defined elsewhere (e.g. in the relevant BasesLoader),
        otherwise trying to get the related timescales will cause a crash.
    '''
    # # # ALL TIMESCALES # # #
    TIMESCALE_VARS = [
        'timescale_wplasma', 'timescale_gyrof', 'timescale_nusn',  # raw timescales
        'timescale_vtherm', 'timescale_EBdrift',  # timescale from speed & ds
    ]

    @known_var(deps=TIMESCALE_VARS)
    def get_timescales(self):
        '''all timescales (from self.TIMESCALE_VARS) as a dataset.
        Consider also: self('timescales_abbrv')

        Useful patterns you might want to consider:
            self('timescales', maindims_means=True)  # timescales based on mean values only
            self('timescales').min('fluid')          # minimum timescales across all fluids
            self('timescales').pc.minimum()          # minimum timescale across all timescales
                equivalent: self('min_timescale')
            self('timescales').min('fluid').pc.minimum()  # minimum timescale at each point.
            self('timescales').pc.varmin()       # name of timescale with minimum value at each point.

            # timescale variable names, sorted from min to max values.
            self('timescales').to_dataarray().pc.sort_along('variable')['variable']
        '''
        timescale_vars = self.TIMESCALE_VARS
        return self(timescale_vars)

    @known_var(deps=TIMESCALE_VARS)
    def get_timescales_abbrv(self):
        '''all timescales (from self.TIMESCALE_VARS) as a dataset, abbreviating names.
        abbreviates 'timescale_var' --> 'var'.
        '''
        result = self('timescales')
        newnames = {v: v[len('timescale_'):] if v.startswith('timescale_') else v for v in result.data_vars}
        return result.rename(newnames)

    @known_var(deps=['timescales'])
    def get_min_timescale(self):
        '''minimum timescale across all timescales.
        Equivalent: self('timescales').pc.minimum()
        '''
        return xarray_minimum_of_datavars(self('timescales'))

    @known_var(deps=['timescales'])
    def get_minf_timescale(self):
        '''minimum timescale across all timescales and fluids.
        Equivalent: self('timescales').min('fluid').pc.minimum()
        '''
        minf = xarray_min(self('timescales'), 'fluid')
        return xarray_minimum_of_datavars(minf)

    @known_var(deps=['timescales_abbrv'])
    def get_min_timescale_type(self):
        '''tells which timescale has the minimum value (across all timescales).
        Equivalent: self('timescales_abbrv').pc.varmin()

        result is a string-valued array, values from self.TIMESCALE_VARS (removing 'timescale_' in names):
            'wplasma', 'gyrof', 'nusn', 'vtherm', 'EBspeed'
        '''
        return xarray_varmin(self('timescales_abbrv'))

    @known_var(deps=['timescales_abbrv'])
    def get_minf_timescale_type(self):
        '''tells which timescale has the minimum value (across all timescales and fluids).
        Equivalent: self('timescales_abbrv').min('fluid').pc.varmin()

        result is a string-valued array, values from self.TIMESCALE_VARS (removing 'timescale_' in names):
            'wplasma', 'gyrof', 'nusn', 'vtherm', 'EBspeed'
        '''
        minf = xarray_min(self('timescales_abbrv'), 'fluid')
        return xarray_varmin(minf)

    # # # HELPERS # # #
    @known_var(deps=['ds'])
    def get_ds_for_timescales(self):
        '''spatial scale used when calculating timescales. vector(ds), e.g. [dx, dy, dz].
        The method here just returns ds. Subclasses might overwrite if they use a different ds for timescales.
        '''
        return self('ds')
    
    @known_var(deps=['ds_for_timescales'])
    def get_dsmin_for_timescales(self):
        '''minimum spatial scale used when calculating timescales.
        min(ds_for_timescales) across components.
        '''
        return xarray_min(self('ds_for_timescales'), 'component', missing_dims='ignore')

    # # # TIMESCALES # # #
    @known_var(deps=['wplasma'])
    def get_timescale_wplasma(self):
        '''timescale from plasma oscillations. 2 * pi / wplasma.  (Hz, not rad/s)
        wplasma = sqrt(n q^2 / (m epsilon0)).
        '''
        return 2 * np.pi / self('wplasma')

    @known_var(deps=['gyrof'])
    def get_timescale_gyrof(self):
        '''timescale for cyclotron motion. 2 * pi / gyrof.  (Hz, not rad/s)
        gyrof = |q| |B| / m.
        '''
        return 2 * np.pi / self('gyrof')

    @known_var(deps=['nusn'])
    def get_timescale_nusn(self):
        '''timescale for collisions with neutrals. 1 / nusn.
        nusn = collision frequency of self.fluid with neutrals.
        '''
        return 1 / self('nusn')

    @known_var(deps=['dsmin_for_timescales', 'vthermal'], aliases=['timescale_vth', 'timescale_vthermal'])
    def get_timescale_vtherm(self):
        '''timescale from thermal velocity. dsmin / vthermal.
        vthermal = sqrt(kB T / m).
        '''
        return self('dsmin_for_timescales') / self('vthermal')

    @known_var(deps=['dsmin_for_timescales', 'E_un0_perpmod_B', 'mod_B'])
    def get_timescale_EBspeed(self):
        '''timescale from speed using E & B fields. dsmin / (|E_un0 cross B| / |B|^2).
        E_un0 (not E) because the derivation assumes neutral frame: u_neutral=0.

        note: to be more precise, use timescale_udrift instead.
        '''
        return self('dsmin_for_timescales') / (self('E_un0_perpmod_B') / self('mod_B'))

    @known_var(deps=['dsmin_for_timescales', 'u_drift'])
    def get_timescale_udrift(self):
        '''timescale from drift speed. dsmin / mod_u_drift.

        note: to be less precise (but computationally cheaper), use timescale_EBspeed instead.
        For electrons when kappae >> 1, timescale_EBspeed ~= timescale_udrift.
        When accounting for directionality, or kappae <~= 1, or non-electrons,
            timescale_EBspeed is always more conservative (i.e. smaller) than timescale_udrift.
        '''
        return self('dsmin_for_timescales') / self('mod_u_drift')

    @known_var(deps=['dsmin_for_timescales', 'timescale_udrift', 'timescale_EBspeed'])
    def get_timescale_EBdrift(self):
        '''timescale from drift speed if possible, else from speed using E & B fields.
        tries to return self('timescale_udrift'), but if that causes a QuantCalcError,
            use self('timescale_EBspeed') instead.
        '''
        try:
            return self('timescale_udrift')
        except QuantCalcError:
            return self('timescale_EBspeed')

    @known_var(deps=['min_timescale'])
    def get_best_subcycle(self):
        '''largest subcycling allowed: best_subcycle = min_timescale / minf_timescale.
        min_timescale = min timescale for self.fluid, across all timescales.
        minf_timescale = min timescale across all fluids and all timescales.
                (when computing minf_timescale here, always use all self.fluids.)
        E.g. fluid=fluids=['e','H+','C+'], min_timescale=[1e-8, 1e-7, 5e-7]
            --> minf_timescale will be 1e-8, so result will be [1, 10, 50].
        '''
        min_timescale = self('min_timescale')
        minf_timescale = self('minf_timescale', fluid=None)
        return min_timescale / minf_timescale

    @known_var(deps=['best_subcycle'])
    def get_best_pow2_subcycle(self):
        '''largest power of 2 subcycling allowed for each fluid in self.fluid.
        result = array of values like 2^N, with largest N such that result < best_subcycle.
        '''
        return 2 ** np.log2(self('best_subcycle')).astype('int')

    @known_var(deps=['best_subcycle'])
    def get_safe_pow2_subcycle(self, *, subcycle_safety=UNSET):
        '''largest "safe" power of 2 subcycling allowed for each fluid in self.fluid.
        result = array of values like 2^N, with largest N such that result < best_subcycle / safety.
        (larger safety produces "safer" results. For safe_subcycle, just use best_subcycle / safety.)
        '''
        if hasattr(self, '_cached_safe_pow2_subcycle'):  # [EFF] if internally getting safe_pow2_subcycle many times,
            return self._cached_safe_pow2_subcycle       # can do "with self.using(_cached_safe_pow2_subcycle=...):"
        if subcycle_safety is UNSET:
            if hasattr(self, 'subcycle_safety'):
                subcycle_safety = self.subcycle_safety
            else:
                raise InputMissingError('subcycle_safety must be set in self or entered as kwarg.')
        if subcycle_safety is None:
            subcycle_safety = 1
        return 2 ** np.log2(self('best_subcycle') / subcycle_safety).astype('int')
