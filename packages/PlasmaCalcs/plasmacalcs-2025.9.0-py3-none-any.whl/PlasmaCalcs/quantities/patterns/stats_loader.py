"""
File Purpose: statistics (e.g. mean, std, min, max)
"""
import warnings

from ..quantity_loader import QuantityLoader
from ...errors import MemorySizeError
from ...tools import (
    simple_property, UNSET,
    xarray_where_finite, xarray_stats, xarray_mean,
    xarray_werrmean, xarray_mean_pm_std,
    xarray_werr2pmstd, xarray_pmstd2werr,
    xarray_werradd, xarray_werrsub, xarray_werrmul, xarray_werrdiv,
    xarray_dims_coords,
)
from ...defaults import DEFAULTS

class StatsLoader(QuantityLoader):
    '''statistics, e.g. mean, std, min, max. Usually applied only along self.stat_dims_for(array).
    By default, stat_dims(array) returns only the self.maindims which appear in the array.
    '''

    # # # "STANDARD" LOGIC / PROPERTIES / HELPER METHODS # # #

    cls_behavior_attrs.register('stat_dims', getdefault=lambda ql: getattr(ql, 'maindims', []))
    @property
    def stat_dims(self):
        '''the dims over which to possibly apply statistics (StatsLoader methods).
        will only apply statics along these dims for an array if they actually appear in the array.
        None --> use self.maindims. (this is the default.)
        See also: self.stat_dims_for(array).
        '''
        if getattr(self, '_stat_dims', None) is None:
            return getattr(self, 'maindims', [])
        else:
            return self._stat_dims
    @stat_dims.setter
    def stat_dims(self, value):
        self._stat_dims = value

    def stat_dims_for(self, array):
        '''return the dims to apply statistics over, for this array.
        Here, returns tuple of d from self.stat_dims if d in array.dims.
        '''
        return tuple(d for d in self.stat_dims if d in array.dims)

    stats_dimpoint_wise = simple_property('_stats_dimpoint_wise', default=None,
        doc='''whether to apply stat calculations at each DimPoint, or after loading the full array.
        [EFF] this setting is just for efficiency; it doesn't affect results (when no MemorySizeError crash).

        True --> apply stat calculations to each array (at each DimPoint) before joining arrays.
                e.g., self('mean_n') gets 'mean_n' at each fluid & snap, then joins results.
        False --> join arrays across all DimPoints before applying stat calculations.
                e.g., self('mean_n') gets 'n' (which varies across fluid & snap), then takes mean.
        None --> if result.size will be > DEFAULTS.STATS_DIMPOINT_WISE_MIN_N / self.get_ncpu(), use True.
                otherwise try using False, then use True if MemorySizeError is raised.
                (True seems to be faster for large arrays but slower for small arrays.
                But also, when ncpu>1, loading across dimpoints is faster due to parallelization.)

        regardless of this setting, stat calculations are applied only along self.stat_dims(array).''')

    @property
    def _extra_kw_for_quantity_loader_call(self):
        '''extra kwargs which can be used to set attrs self during self.__call__.
        The implementation here returns ['stats_dimpoint_wise'] + any values from super().
        '''
        # 'stats_dimpoint_wise' doesn't affect numerical results, just efficiency,
        #   which is why it's not in self.behavior_attrs. But, user might still want to set it during __call__.
        return ['stats_dimpoint_wise'] + super()._extra_kw_for_quantity_loader_call

    def _print_or_warn(self, msg, debug_thresh=1):
        '''if DEBUG>=debug_thresh, print msg. Else, warnings.warn(msg).'''
        if DEFAULTS.DEBUG >= debug_thresh:
            print(msg)
        else:
            warnings.warn(msg)

    def _get_stat_var(self, var, statfunc):
        '''returns result of applying statfunc to self(var), possibly one dimpoint at a time then joining results.
        see help(type(self).stats_dimpoint_wise) for details.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.stats_dimpoint_wise is None:
            # if result will be a certain size or larger, use True (faster for large arrays).
            ncpu = self.get_ncpu() if hasattr(self, 'get_ncpu') else 1
            min_n = DEFAULTS.STATS_DIMPOINT_WISE_MIN_N
            size_threshold = min_n / ncpu
            if size_threshold is not None:
                try:
                    result_size = self.match_var_result_size(var, maindims=True)
                except Exception:
                    if DEFAULTS.DEBUG >= 1 or getattr(self, 'verbose', False) >= 1:
                        warnmsg = (f'Error when guessing result size for var={var!r}.\n'
                                   f'Could not guess result_dims; maybe self.tree(var={var!r}) crashed.\nUsing default guess: '
                                   f'result_size = self.current_n_dimpoints() * self.maindims_size '
                                   f'== {self.current_n_dimpoints()} * {getattr(self, "maindims_size", 1)}')
                        self._print_or_warn(warnmsg, debug_thresh=1)
                    result_size = self.current_n_dimpoints() * getattr(self, 'maindims_size', 1)
                if result_size > size_threshold:
                    if DEFAULTS.DEBUG >= 1 or getattr(self, 'verbose', False) >= 1:
                        warnmsg = (f'temporarily using stats_dimpoint_wise=True for efficiency; predicted '
                                   f'result_size ({result_size}) > DEFAULTS.STATS_DIMPOINT_WISE_MIN_N (={min_n}) / ncpu (={ncpu}).')
                        self._print_or_warn(warnmsg, debug_thresh=1)
                    return self._get_stat_var_dimpoint_wise_true(var, statfunc)
            # else, try with False first (faster for small arrays). Switch to True if MemorySizeError when False.
            try:
                return self._get_stat_var_dimpoint_wise_false(var, statfunc)
            except MemorySizeError:
                if DEFAULTS.DEBUG >= 1 or getattr(self, 'verbose', False) >= 1:
                    warnmsg = (f'MemorySizeError when avoiding dimpoint_wise stats due to stats_dimpoint_wise=None. '
                               f'Will use stats_dimpoint_wise=True instead. (var={var!r}) '
                               f'(Might want to adjust DEFAULTS.ARRAY_MBYTES_MAX, '
                               f'or explicity set stats_dimpoint_wise=False to see the MemorySizeError crash.)')
                    self._print_or_warn(warnmsg, debug_thresh=1)
                return self._get_stat_var_dimpoint_wise_true(var, statfunc)
        elif self.stats_dimpoint_wise:
            return self._get_stat_var_dimpoint_wise_true(var, statfunc)
        else:
            return self._get_stat_var_dimpoint_wise_false(var, statfunc)

    def _get_stat_var_dimpoint_wise_false(self, var, statfunc):
        '''returns result of applying statfunc to self(var). (Used when self.stats_dimpoint_wise=False.)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        value = self(var)
        return statfunc(value)
    
    def _get_statfunc_of_var(self, var, statfunc):
        '''load this stat, for self(var).'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        value = self(var)
        return statfunc(value)

    def _get_stat_var_dimpoint_wise_true(self, var, statfunc, min_split=UNSET):
        '''returns result of applying statfunc to self(var). (Used when self.stats_dimpoint_wise=True.)
        min_split: UNSET or int
            [EFF] min length of dimension before actually applying dimpointwise stats along it.
            1 --> no minimum. If MemorySizeError when min_split > 1, try again but with min_split=1.
            UNSET --> use DEFAULTS.STATS_DIMPOINT_WISE_MIN_SPLIT.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        def loading_stat():
            '''loads this stat, for self(var), at a single dimpoint.'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            var_value = self(var)
            return statfunc(var_value)
        if min_split is UNSET: min_split = DEFAULTS.STATS_DIMPOINT_WISE_MIN_SPLIT
        try:
            value = self.load_across_dims_implied_by(var,
                        self._get_statfunc_of_var, var, statfunc,   # loader & *args_loader
                        _min_split=min_split)
        except MemorySizeError:
            if min_split == 1:
                raise
            # else
            if DEFAULTS.DEBUG >= 5 or getattr(self, 'verbose', False) >= 4:
                warnmsg = (f'MemorySizeError when min_split={min_split}, during stats_dimpoint_wise=True. '
                           f'Trying min_split=1 instead. var={var!r}. (Might want to adjust DEFAULTS.ARRAY_MBYTES_MAX.)')
                if not (DEFAULTS.DEBUG >= 5):
                    warnings.warn(warnmsg)  # only verbose, not DEBUG.
                else:
                    print(warnmsg)  # DEBUG --> print, not warn.
            return self._get_stat_var_dimpoint_wise_true(var, statfunc, min_split=1)
        return value


    # # # "STANDARD" STATS (ACROSS MAINDIMS) # # #

    # 'sum_{var}'
    @known_pattern(r'sum_(.+)', deps=[0])
    def get_sum(self, var, *, _match=None):
        '''sum. sum(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_sum)
    def _stat_dims_sum(self, array):
        return array.sum(dim=self.stat_dims_for(array))

    # 'prod_{var}'
    @known_pattern(r'prod_(.+)', deps=[0])
    def get_prod(self, var, *, _match=None):
        '''prod. prod(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_prod)
    def _stat_dims_prod(self, array):
        return array.prod(dim=self.stat_dims_for(array))

    # 'mean_{var}'
    @known_pattern(r'mean_(.+)', deps=[0])
    def get_mean(self, var, *, _match=None):
        '''mean. mean(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_mean)
    def _stat_dims_mean(self, array):
        return array.mean(dim=self.stat_dims_for(array))

    # 'std_{var}'
    @known_pattern(r'std_(.+)', deps=[0])
    def get_std(self, var, *, _match=None):
        '''standard deviation. std(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_std)
    def _stat_dims_std(self, array):
        return array.std(dim=self.stat_dims_for(array))

    # 'min_{var}'
    @known_pattern(r'min_(.+)', deps=[0])
    def get_min(self, var, *, _match=None):
        '''minimum. min(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_min)
    def _stat_dims_min(self, array):
        return array.min(dim=self.stat_dims_for(array))

    # 'max_{var}'
    @known_pattern(r'max_(.+)', deps=[0])
    def get_max(self, var, *, _match=None):
        '''maximum. max(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_max)
    def _stat_dims_max(self, array):
        return array.max(dim=self.stat_dims_for(array))

    # 'median_{var}'
    @known_pattern(r'median_(.+)', deps=[0])
    def get_median(self, var, *, _match=None):
        '''median. median(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_median)
    def _stat_dims_median(self, array):
        return array.median(dim=self.stat_dims_for(array))

    # 'rms_{var}'
    @known_pattern(r'rms_(.+)', deps=[0])
    def get_rms(self, var, *, _match=None):
        '''root mean square. sqrt(mean(var**2)). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_rms)
    def _stat_dims_rms(self, array):
        return (array**2).mean(dim=self.stat_dims_for(array))**0.5

    # 'delta_{var}'
    @known_pattern(r'delta_(.+)', deps=[0])
    def get_delta(self, var, *, _match=None):
        '''perturbation. var - mean(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_delta)
    def _stat_dims_delta(self, array):
        return array - array.mean(dim=self.stat_dims_for(array))

    # 'deltafrac_{var}'
    @known_pattern(r'deltafrac_(.+)', deps=[0])
    def get_deltafrac(self, var, *, _match=None):
        '''perturbation. (var - mean(var)) / mean(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_deltafrac)
    def _stat_dims_deltafrac(self, array):
        return (array / array.mean(dim=self.stat_dims_for(array))) - 1  # == (array - mean) / mean

    # 'meannormed_{var}'
    @known_pattern(r'meannormed_(.+)', deps=[0])
    def get_meannormed(self, var, *, _match=None):
        '''normalized by mean. var / mean(var). Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_meannormed)
    def _stat_dims_meannormed(self, array):
        return array / array.mean(dim=self.stat_dims_for(array))

    # 'weighted_{weights}_mean_{var}'
    @known_pattern(r'weighted_(.+)_mean_(.+)', deps=[0, 1])
    def get_weighted_mean(self, weights_var, *, _match=None):
        '''mean, weighted by weights. mean(weights*var)/mean(weights).
        E.g. 'weighted_n_mean_T' --> mean(n * T) / mean(n).
            (see also: 'nmean_[var]', which is a shorthand for 'weighted_n_mean_[var]')
        Applied only along any self.stat_dims in array.
        '''
        weights, var = _match.groups()
        return self(f'mean_({var}*meannormed_{weights})')  # mean(T*n/mean(n)) equivalent to mean(n*T)/mean(n).

    # 'weighted_{weights}_std_{var}'
    @known_pattern(r'weighted_(.+)_std_(.+)', deps=[0, 1])
    def get_weighted_std(self, weights_var, *, _match=None):
        '''std, weighted by weights. std(weights*var)/mean(weights).
        E.g. 'weighted_n_std_mod_u' --> std(n * mod_u) / mean(n).
            (see also: 'nstd_[var]', which is a shorthand for 'weighted_n_std_[var]')
        Applied only along any self.stat_dims in array.

        Currently, equivalent to self('(std_({weights}*{var}))/mean(weights)')
        [TODO][EFF] internally, don't compute weights twice...
        '''
        weights, var = _match.groups()
        return self(f'(std_({weights}*{var}))/mean_{weights}')

    # 'stats_{var}'
    @known_pattern(r'stats_(.+)', deps=[0])
    def get_stats(self, var, *, _match=None):
        '''return dataset of stats for var
        stats include: mean, std, min, max, median, rms.
        Applied only along any self.stat_dims in array.

        Incompatible with Dataset vars.
        Consider also: self('astats_var'), self('var').pc.stats()
        '''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_stats)
    def _stat_dims_stats(self, array):
        return xarray_stats(array, dim=self.stat_dims_for(array))

    @known_pattern(r'astats_(.+)', deps=[0])
    def get_astats(self, var, *, _match=None):
        '''return dataarray of stats for var, reporting stats along new dim: 'stat'.
        stats include: mean, std, min, max, median, rms.
        Applied only along any self.stat_dims in array.

        Compatible with Dataset vars (without existing 'stat' coord or dim).
        The result excludes whichever dims the stats are being taken across,
            and adds the new dim 'stat' with the stats.

        Consider also: self('stats_var'), self('var').pc.stats(to_da='stat')
        '''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_astats)
    def _stat_dims_astats(self, array):
        return xarray_stats(array, dim=self.stat_dims_for(array), to_da='stat')

    # # # FINITE VALUES ONLY - e.g. "nanmean" # # #

    @known_pattern(r'finite_(.+)', deps=[0])    # 'finite_{var}'
    def get_finite(self, var, *, _match=None):
        '''var, masked with NaN wherever values are not finite.'''
        here, = _match.groups()
        value = self(here)
        return xarray_where_finite(value)

    @known_pattern(r'nanmean_(.+)', deps=[0])    # 'nanmean_{var}'
    def get_nanmean(self, var, *, _match=None):
        '''mean. mean(var), ignoring NaNs AND infs. Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self(f'mean_finite_{here}')

    @known_pattern(r'nanstd_(.+)', deps=[0])    # 'nanstd_{var}'
    def get_nanstd(self, var, *, _match=None):
        '''standard deviation. std(var), ignoring NaNs AND infs. Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self(f'std_finite_{here}')

    @known_pattern(r'nanmin_(.+)', deps=[0])    # 'nanmin_{var}'
    def get_nanmin(self, var, *, _match=None):
        '''minimum. min(var), ignoring NaNs AND infs. Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self(f'min_finite_{here}')

    @known_pattern(r'nanmax_(.+)', deps=[0])    # 'nanmax_{var}'
    def get_nanmax(self, var, *, _match=None):
        '''maximum. max(var), ignoring NaNs AND infs. Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self(f'max_finite_{here}')

    @known_pattern(r'nanmedian_(.+)', deps=[0])    # 'nanmedian_{var}'
    def get_nanmedian(self, var, *, _match=None):
        '''median. median(var), ignoring NaNs AND infs. Applied only along any self.stat_dims in array.'''
        here, = _match.groups()
        return self(f'median_finite_{here}')

    @known_pattern(r'nanrms_(.+)', deps=[0])    # 'nanrms_{var}'
    def get_nanrms(self, var, *, _match=None):
        '''root mean square. sqrt(mean(var**2)), ignoring NaNs AND infs.
        Applied only along any self.stat_dims in array.
        '''
        here, = _match.groups()
        return self(f'rms_finite_{here}')

    @known_pattern(r'nandelta_(.+)', deps=[0])    # 'nandelta_{var}'
    def get_nandelta(self, var, *, _match=None):
        '''perturbation. var - mean(var), ignoring NaNs AND infs.
        Applied only along any self.stat_dims in array.
        '''
        here, = _match.groups()
        return self(f'delta_finite_{here}')

    @known_pattern(r'nandeltafrac_(.+)', deps=[0])    # 'nandeltafrac_{var}'
    def get_nandeltafrac(self, var, *, _match=None):
        '''perturbation. (var - mean(var)) / mean(var), ignoring NaNs AND infs.
        Applied only along any self.stat_dims in array.
        '''
        here, = _match.groups()
        return self(f'deltafrac_finite_{here}')


    # # # ERROR PROPAGATION / MATH # # #

    cls_behavior_attrs.register('werrmath_require_std', default=False)
    werrmath_require_std = simple_property('_werrmath_require_std', default=False,
        doc='''whether to require 'std' data var appear in at least 1 input for all werrmath operations.
        E.g. if True and doing A_werradd_B but neither A nor B has 'std', crash with InputError.''')

    @known_pattern(r'werrmean_(.+)', deps=[0])   # 'werrmean_{var}'
    def get_werrmean(self, var, *, _match=None):
        '''dataset of 'mean' and 'std' of var. Computed along self.stat_dims in array.'''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_werrmean)
    def _stat_dims_werrmean(self, array):
        return xarray_werrmean(array, dim=self.stat_dims_for(array))

    @known_pattern(r'mean_pm_std_(.+)', deps=[0])   # 'mean_pm_std_{var}'
    def get_mean_pm_std(self, var, *, _match=None):
        '''return dataset of 'mean+std', 'mean', 'mean-std' for var.
        Computed along any self.stat_dims in array.

        Equivalent: werr2pmstd_werrmean_var
        '''
        here, = _match.groups()
        return self._get_stat_var(here, self._stat_dims_mean_pm_std)
    def _stat_dims_mean_pm_std(self, array):
        return xarray_mean_pm_std(array, dim=self.stat_dims_for(array))

    @known_pattern(r'werr2pmstd_(.+)', deps=[0])   # 'werr2pmstd_{var}'
    def get_werr2pmstd(self, var, *, _match=None):
        '''convert dataset with 'mean' and 'std' into dataset with 'mean+std', 'mean', 'mean-std'.
        werr2pmstd_var will crash if self(var) doesn't have 'mean' and 'std' data vars.
        '''
        here, = _match.groups()
        werr_val = self(here)
        return xarray_werr2pmstd(werr_val)

    @known_pattern(r'pmstd2werr_(.+)', deps=[0])   # 'pmstd2werr_{var}'
    def get_pmstd2werr(self, var, *, _match=None):
        '''convert dataset with 'mean+std' and 'mean-std' into dataset with 'mean' and 'std'.
        pmstd2werr_var will crash if self(var) doesn't have 'mean+std' and 'mean-std' data vars.
        '''
        here, = _match.groups()
        pmstd_val = self(here)
        return xarray_pmstd2werr(pmstd_val)

    @known_pattern(r'(.+)_werradd_(.+)', deps=[0, 1])   # '{var}_werradd_{var2}'
    def get_werradd(self, var, *, _match=None):
        '''A_werradd_B = A + B, but result is a dataset with 'mean' and 'std'.
        Does not take any means or stds here, but if A or B has 'std' already,
        assumes independent errors and applies "error propagation" formula:
            mean(A + B) = mean(A) + mean(B)
            std(A + B) = sqrt(std(A)**2 + std(B)**2)
        (if A or B is DataArray, treat as 'mean'. if missing 'std', assume 0.)
        '''
        A, B = _match.groups()
        Aval = self(A)
        Bval = self(B)
        return xarray_werradd(Aval, Bval, require_std=self.werrmath_require_std)

    @known_pattern(r'(.+)_werrsub_(.+)', deps=[0, 1])   # '{var}_werrsub_{var2}'
    def get_werrsub(self, var, *, _match=None):
        '''A_werrsub_B = A - B, but result is a dataset with 'mean' and 'std'.
        Does not take any means or stds here, but if A or B has 'std' already,
        assumes independent errors and applies "error propagation" formula:
            mean(A - B) = mean(A) - mean(B)
            std(A - B) = sqrt(std(A)**2 + std(B)**2)
        (if A or B is DataArray, treat as 'mean'. if missing 'std', assume 0.)
        '''
        A, B = _match.groups()
        Aval = self(A)
        Bval = self(B)
        return xarray_werrsub(Aval, Bval, require_std=self.werrmath_require_std)

    @known_pattern(r'(.+)_werrmul_(.+)', deps=[0, 1])   # '{var}_werrmul_{var2}'
    def get_werrmul(self, var, *, _match=None):
        '''A_werrmul_B = A * B, but result is a dataset with 'mean' and 'std'.
        Does not take any means or stds here, but if A or B has 'std' already,
        assumes independent errors and applies "error propagation" formula:
            z = A * B
            mean(z) = mean(A) * mean(B)
            std(z) = abs(mean(z)) * sqrt((std(A)/mean(A))**2 + (std(B)/mean(B))**2)
        (if A or B is DataArray, treat as 'mean'. if missing 'std', assume 0.)
        '''
        A, B = _match.groups()
        Aval = self(A)
        Bval = self(B)
        return xarray_werrmul(Aval, Bval)

    @known_pattern(r'(.+)_werrdiv_(.+)', deps=[0, 1])   # '{var}_werrdiv_{var2}'
    def get_werrdiv(self, var, *, _match=None):
        '''A_werrdiv_B = A / B, but result is a dataset with 'mean' and 'std'.
        Does not take any means or stds here, but if A or B has 'std' already,
        assumes independent errors and applies "error propagation" formula:
            z = A / B
            mean(z) = mean(A) / mean(B)
            std(z) = abs(mean(z)) * sqrt((std(A)/mean(A))**2 + (std(B)/mean(B))**2)
        (if A or B is DataArray, treat as 'mean'. if missing 'std', assume 0.)
        '''
        A, B = _match.groups()
        Aval = self(A)
        Bval = self(B)
        return xarray_werrdiv(Aval, Bval)


    # # # MISC # # #
    # stats but not applied across maindims.

    @known_pattern(r'meant_(.+)', deps=[0])
    def get_meant(self, var, *, _match=None):
        '''mean-across-time of var.
        self(meant_var) --> self(var).mean(tdim), where tdim is the dim associated with time,
                (tdim default 'snap', but if 't' coord associated with a dim, use that dim.)
        '''
        here, = _match.groups()
        val = self(here)
        tdim = 'snap'  # default tdim
        dims_coords = xarray_dims_coords(val)
        for k, coords in dims_coords.items():
            if 't' in coords:
                tdim = k
        return xarray_mean(val, tdim, missing_dims='ignore')

    @known_pattern(r'werrmeant_(.+)', deps=[0])
    def get_werrmeant(self, var, *, _match=None):
        '''dataset of 'mean' and 'std' of var, taking stats across time dimension.
        self(werrmeant_var) --> self(var).werrmean(tdim), where tdim is the dim associated with time,
                (tdim default 'snap', but if 't' coord associated with a dim, use that dim.)
        '''
        here, = _match.groups()
        val = self(here)
        tdim = 'snap'
        dims_coords = xarray_dims_coords(val)
        for k, coords in dims_coords.items():
            if 't' in coords:
                tdim = k
        return xarray_werrmean(val, tdim, missing_dims='ignore')
