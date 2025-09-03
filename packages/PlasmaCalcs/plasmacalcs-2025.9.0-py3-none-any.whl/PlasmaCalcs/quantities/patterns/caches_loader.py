"""
File Purpose: caching into files / loading cached values from files

[TODO] calculator.behavior.serialize() would help avoid errors.
Implementation here is somewhat primitive.
"""
import os
import shutil

import numpy as np
import xarray as xr

from ..quantity_loader import QuantityLoader
from ...errors import (
    InputError, InputMissingError, MemorySizeError,
    CacheNotApplicableError,
)
from ...tools import (
    simple_property,
    format_docstring,
    code_snapshot_info,
    xarray_save, xarray_load,
)
from ...defaults import DEFAULTS


class CachesLoader(QuantityLoader):
    '''caching into files / loading cached values from files.
    Ideal for relatively small arrays which are expensive to calculate.
        (e.g. ln_std_blur_deltafrac_n, the blurring can take a bit of time for large blur_sigma.)
    For large arrays, recommended: just use xarray_save and xarray_load, directly.

    Stores relevant behavior_attrs and never gives a wrong answer when loading from cache.
        if self.behavior doesn't match stored behavior attrs, delete cached value.
        if current PlasmaCalcs version doesn't match version noted in array.attrs, delete cached value.
        E.g. can use self('caches_ln_std_blur_deltafrac_n') without worrying about blur_sigma;
            if current blur_sigma differs from stored blur_sigma, deletes cache instead of using it.
            And if default blur_sigma changes (via a change to PlasmaCalcs), the version will be different,
                so the cache will also be deleted. (checks __version__ and git commit hash if available.)
    
    Caution: may delete files with '_pc_caches' in their path, without warning.
    '''

    cache_dirname = simple_property('_cache_dirname', setdefaultvia='_default_cache_dirname',
        doc='''abspath to directory for containing cached values of this CachesLoader.
        Default: {self.dirname}/_pc_caches if self.dirname exists, else raise InputMissingError.
        Caution: PlasmaCalcs may delete files with '_pc_caches' in their path, without warning.''')

    def _default_cache_dirname(self):
        '''default for self.cache_dirname.
        {self.dirname}/_pc_caches if self.dirname exists, else raise InputMissingError.
        '''
        dirname = getattr(self, 'dirname', None)
        if isinstance(dirname, str):
            return os.path.join(dirname, '_pc_caches')
        else:
            errmsg = f'self.cache_dirname not set, and got non-str self.dirname={self.dirname}.'
            raise InputMissingError(errmsg)

    def _assert_cache_array_not_too_big(self, array):
        '''checks that array is not too big for caching. If too big, crash with MemorySizeError.'''
        mbmax = DEFAULTS.CACHE_ARRAY_MBYTES_MAX
        if (mbmax is not None) and (array.pc.nMbytes > mbmax):
            errmsg = (f'Array too big for caching ({array.pc.nMbytes} MB); limit={mbmax} MB.\n'
                      f'To adjust limit, set DEFAULTS.CACHE_ARRAY_MBYTES_MAX (currently {mbmax}).')
            raise MemorySizeError(errmsg)

    def _cache_dst(self, array_or_name):
        '''return abspath for cached array, given array (or name of array).
        (if DataArray, uses array.name; if Dataset, must provide name as str instead.)
        result will include .pcxarr extension.

        if inferred name includes '/', crash (and suggest to use ÷ character instead).
        '''
        if isinstance(array_or_name, str):
            name = array_or_name
        else:
            name = getattr(array_or_name, 'name', None)
        if name is None:
            raise InputError(f'cannot infer name; consider providing str directly. Got: {array_or_name}')
        if '/' in name:
            raise InputError("cannot get _cache_dst for name containing '/'. Consider using '÷' instead.")
        result = os.path.join(self.cache_dirname, f'{name}.pcxarr')
        return result

    def _delete_cache_dst_if_exists(self, dst):
        '''delete dst, if it exists, but first ensure it contains '_pc_caches' in the path.
        Never deletes files which don't contain '_pc_caches' in the path.
        '''
        if os.path.exists(dst):
            if '_pc_caches' in dst:
                if os.path.isdir(dst):  # folder
                    shutil.rmtree(dst)
                else:  # file
                    os.remove(dst)
            else:
                raise InputError(f"Refusing to auto-delete file without '_pc_caches' in path: {dst!r}")

    def _array_compatible_with_current_behavior(self, array, *, return_info=False):
        '''returns whether array is compatible with current self.behavior.

        Compatible if all of the following are true:
        (1) All attrs appearing in array.attrs & self.behavior must be equal.
                E.g., if 'units' in both, need array.attrs['units'] == self.behavior['units'].
        (2) All attrs appearing in self.behavior.nondefault(include_xr=False) must appear in array.attrs.
                E.g., if 'blur_sigma' in self.behavior.nondefault(), need 'blur_sigma' in array.attrs.
        (3) [TODO] If self.behavior.nondefault(include_xr='only') has any values,
            they must match values saved to arrays in os.path.join(array.attrs['filepath'], 'behavior_arrays')
                E.g., if 'tfbi_grid1_zeros' appears, need self.behavior['tfbi_grid1_zeros'].equals(behavarr),
                where behavarr = xarray_load(... the array at 'behavior_arrays/tfbi_grid1_zeros.pcxarr'))
            [TODO] currently, caching behavior array values is not implemented;
                see type(self).caches_behavior_skip_xr for details.
        (4) All appearing in array and self.behavior.dims must be equal.
                E.g., if 'fluid' in both, need array_equal(array['fluid'].values, self.behavior.dims['fluid'])
        (5) If array.attrs has 'pc__version__' and/or 'pc__commit_hash',
            they must match the current PlasmaCalcs version and commit hash, if known.

        return_info: bool
            whether to instead return (result, reason of mismatch, key, array value, behavior value).
            (reason will be 'version', 'attrs', 'dims', or 'array_attrs')
            (if result is True, all other values are None)
        '''
        behavior = self.behavior
        # (5)  # <-- check first for efficiency
        if 'pc__version__' in array.attrs or 'pc__commit_hash' in array.attrs:
            code_info = code_snapshot_info()
            for k in ['pc__version__', 'pc__commit_hash']:
                if k in array.attrs and k in code_info and array.attrs[k] != code_info[k]:
                    if return_info:
                        return False, 'version', k, array.attrs[k], code_info[k]
                    else:
                        return False
        # (1)
        for k, v in array.attrs.items():
            if k in behavior:
                if behavior[k] != v:
                    if return_info:
                        return False, 'attrs', k, v, behavior[k]
                    else:
                        return False
        # (2)
        for k in behavior.nondefault_keys(ql=self, include_xr=(not self.caches_behavior_skip_xr)):
            if k not in array.attrs:
                if return_info:
                    return False, 'attrs', k, None, behavior[k]
                else:
                    return False
        # (3)  # [TODO]
        # for k, v in behavior.nondefault(ql=self, include_xr='only').items():
        #     if 'filepath' not in array.attrs:
        #         if return_info:
        #             return False, 'array_attrs', k, None, object.__repr__(v)
        #         else:
        #             return False
        #     filepath = array.attrs['filepath']
        #     behavpath = os.path.join(filepath, 'behavior_arrays', f'{k}.pcxarr')
        #     if not os.path.exists(behavpath):
        #         if return_info:
        #             return False, 'array_attrs', k, None, object.__repr__(v)
        #         else:
        #             return False
        #     behavarr = xarray_load(behavpath)
        #     if not v.equals(behavarr):
        #         if return_info:
        #             return False, 'array_attrs', k, object.__repr__(behavarr), object.__repr__(v)
        #         else:
        #             return False
        # (4)
        for k, v in behavior.dims.items():
            if k in array.coords:
                if not np.array_equal(array[k].values, v):
                    if return_info:
                        return False, 'dims', k, array[k].values, v
                    else:
                        return False
        if return_info:
            return True, None, None, None, None
        else:
            return True

    def _assert_array_compatible_with_current_behavior(self, array):
        '''assert that array is compatible with current self.behavior.
        (if not, crash with CacheNotApplicableError)
        '''
        result, kind, key, arr_val, behav_val = self._array_compatible_with_current_behavior(array, return_info=True)
        if not result:
            errmsg = f'Cache {kind!r} mismatch for {key!r}:\n(>>cache<<) {arr_val}\n(>>current<<) {behav_val}.'
            raise CacheNotApplicableError(errmsg)

    cls_behavior_attrs.register('caches_behavior_skip_xr', default=False)
    caches_behavior_skip_xr = simple_property('_caches_behavior_skip_xr', default=False,
        doc='''where to skip array-valued behavior attrs when caching arrays (to _pc_caches)
        and when checking compatibility with already-cached arrays (in _pc_caches).
        CAUTION: if True, might give subtly incorrect results if the relevant array-valued behavior attrs change.
        Eventually, caching should save array-valued attrs too, but it's trickier so this is a workaround for now.''')

    @known_pattern(r'caches_(.+)', deps=[0])
    @format_docstring(default_mbmax=DEFAULTS.CACHE_ARRAY_MBYTES_MAX)
    def get_caches_var(self, var, *, _match=None):
        '''get var, possibly from folder within self.cache_dirname.
        puts self.behavior.nondefault() as attrs of result.
            (caching not yet implemented for arrays with complicated nondefault behavior,
            e.g. will fail if trying to use caches_var syntax and masking at the same time.
            Workaround: separately call xarray_save and xarray_load, for results you care about.
            Other workaround: use )

        if previously cached, check if applicable, i.e.
            whether attrs agree with self.behavior.nondefault(), and dims agree with self.behavior.dims.
            if applicable, then return cached result.
            else, destroy cache and proceed as if not already cached (see below).

        if not already cached, saves to {{self.cache_dirname}}/{{var}},
            unless result is too big (in which case, crash with MemorySizeError).
            "too big" [MB] == DEFAULTS.CACHE_ARRAY_MBYTES_MAX (default: {default_mbmax})

        see also: cached_var, cache_var
        '''
        here, = _match.groups()
        dst = self._cache_dst(here)
        if os.path.exists(dst):
            # get from cache
            result = xarray_load(dst)
            if self._array_compatible_with_current_behavior(result):
                return result
            else:
                # cache is incompatible; delete it and proceed as if not cached.
                self._delete_cache_dst_if_exists(dst)
        # not cached yet. get, then save to cache
        result = self(here, assign_behavior_attrs=True,
                      assign_behavior_attrs_skip_xr=self.caches_behavior_skip_xr,
                      assign_behavior_attrs_max_call_depth=2+self.call_depth)
        self._assert_cache_array_not_too_big(result)
        for attr, v in result.attrs.items():
            if isinstance(v, (xr.DataArray, xr.Dataset)):
                errmsg = (f'Cannot cache result when behavior attr {attr!r},\n'
                          f'has nondefault value of type DataArray or Dataset (got: {type(v)}).\n'
                          'Consider using self.caches_behavior_skip_xr=True as a workaround for now.')
                raise CacheNotApplicableError(errmsg)
        xarray_save(result, dst)  # might crash if complicated behavior attrs.
        return result

    @known_pattern(r'cached_(.+)', deps=[0])
    def get_cached_var(self, var, *, _match=None):
        '''get var from folder within self.cache_dirname.
        if not already cached, crash with CacheNotApplicableError.
        if previously cached, ensures attrs agree with self.behavior.nondefault(),
            and ensures dims agree with self.behavior.dims.

        see also: caches_var, cache_var
        '''
        here, = _match.groups()
        dst = self._cache_dst(here)
        if not os.path.exists(dst):
            raise CacheNotApplicableError(f'No cache file for {here!r}; checked: {dst!r}')
        result = xarray_load(dst)
        self._assert_array_compatible_with_current_behavior(result)
        return result

    @known_pattern(r'cache_(.+)', deps=[0])
    def get_cache_var(self, var, *, _match=None):
        '''get var, then save to cache. returns value of var.
        if cached result already exists, will overwrite it.
        if result is too big, crash with MemorySizeError.

        see also: caches_var, cached_var
        '''
        here, = _match.groups()
        result = self(here, assign_behavior_attrs=True,
                      assign_behavior_attrs_skip_xr=self.caches_behavior_skip_xr,
                      assign_behavior_attrs_max_call_depth=2+self.call_depth)
        for attr, v in result.attrs.items():
            if isinstance(v, (xr.DataArray, xr.Dataset)):
                errmsg = (f'Cannot cache result when behavior attr {attr!r},\n'
                          f'has nondefault value of type DataArray or Dataset (got: {type(v)}).\n'
                          'Consider using self.caches_behavior_skip_xr=True as a workaround for now.')
                raise CacheNotApplicableError(errmsg)
        self._assert_cache_array_not_too_big(result)
        dst = self._cache_dst(here)
        self._delete_cache_dst_if_exists(dst)
        xarray_save(result, dst)
        return result
