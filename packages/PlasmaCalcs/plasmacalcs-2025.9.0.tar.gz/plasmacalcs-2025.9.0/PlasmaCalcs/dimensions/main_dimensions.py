"""
File Purpose: MainDimensionsHaver

Since it may include multiple axes, and many values along each axis,
the code architecture for MainDimensionsHaver is different than for the other DimensionHavers.

main dimensions are also NOT included in the regular list of dimensions,
to avoid iterating through each point in space when iterating through dimension values.

"dimpoints" in PlasmaCalcs refers to a point in the space of other dimensions,
i.e. a set of values for (some or all of) the other dimensions, but not maindims,
e.g. (snap=0, fluid=0, jfluid=1)
"""
import numpy as np
import xarray as xr

from .dimension_tools import DimensionHaver, MultiSlices, _paramdocs_multi_slices
from .snaps import INPUT_SNAP
from ..errors import LoadingNotImplementedError
from ..defaults import DEFAULTS
from ..tools import (
    format_docstring,
    simple_property, alias_child,
    product,
    xarray_isel, is_iterable_dim,
    interprets_fractional_indexing, is_iterable,
)


class UnsettableDict(dict):
    '''a dict whose values cannot be set. raise ValueError if attempting to set any items.'''
    def __init__(self, *args, errmsg='cannot set values in UnsettableDict', **kw):
        self.errmsg = errmsg
        super().__init__(*args, **kw)
    def __setitem__(self, key, value):
        raise ValueError(self.errmsg)
    def update(self, *args, **kw):
        raise ValueError(self.errmsg)


class MainDimensionsHaver(DimensionHaver):
    '''All the dimensions which remain after indexing by all other DimensionHavers.
    E.g., for simulation output from a 1024 x 512 x 512 simulation (in x, y, z),
        for a given fluid, jfluid, component, and snapshot,
        the array would be (1024, 512, 512).
    This is probably the shape of (most) arrays as stored in memory.

    use self.slices and self.slicing to control slicing behavior

    Subclasses should implement:
        maindims: listlike of strs
            tells main dimensions. Will be accessed as instance.maindims.
            Best to use a property if maindims depends on class.
        get_maindims_coords: method
            self.get_maindims_coords() should return dict of {dim: coords} for dims in self.maindims.
            it should also slice coords appropriately, according to self.slices;
                for this task, one helpful method might be self._apply_maindims_slices_to_dict().
    '''
    # # # BEHAVIOR ATTRS # # #

    @property
    def _extra_kw_for_quantity_loader_call(self):
        '''extra kwargs which can be used to set attrs self during self.__call__.
        The implementation here returns ['multi_slices_ndim', 'multi_slices_ikeep'] + any values from super().
        '''
        return ['multi_slices_ndim', 'multi_slices_ikeep'] + super()._extra_kw_for_quantity_loader_call

    # # # MAINDIMS -- SUBCLASS SHOULD IMPLEMENT # # #
    maindims = NotImplemented   # listlike of main dimensions, e.g. ['x', 'y', 'z']

    def get_maindims_coords(self):
        '''return dict of {dim: coords} for all dimensions in self.main_dims.
        E.g., {'x': xcoords, 'y': ycoords, 'z': zcoords}, if main dimensions are x, y, z.
        coords will each be sliced using the appropriate slices from self.slices.
        '''
        raise LoadingNotImplementedError(f'{type(self).__name__}.get_maindims_coords')

    # # # MAINDIMS -- IMPLEMENTED HERE # # #
    @property
    def maindims_shape(self):
        '''tuple of (len(self.get_maindims_coords()[dim]) for dim in self.maindims).
        Note, this should be sensitive to changes in self.slices. See also: self.maindims_full_shape.
        '''
        coords = self.get_maindims_coords()
        result = []
        for dim in self.maindims:
            try:
                L = len(coords[dim])
            except TypeError:
                L = 1
            result.append(L)
        return tuple(result)

    @property
    def maindims_size(self):
        '''product of terms in self.maindims_shape.
        Note, this should be sensitive to changes in self.slices. See also: self.maindims_full_size.
        '''
        return product(self.maindims_shape)

    @property
    def maindims_sizes(self):
        '''dict of {dim: size of dim} for dim in self.maindims.
        Note, this should be sensitive to changes in self.slices. See also: self.maindims_full_sizes.
        '''
        shape = self.maindims_shape
        return {dim: shape[i] for i, dim in enumerate(self.maindims)}

    @property
    def maindims_full_shape(self):
        '''self.maindims_shape when self.slices=None'''
        with self.using(slices=None):
            return self.maindims_shape

    @property
    def maindims_full_size(self):
        '''self.maindims_size when self.slices=None'''
        with self.using(slices=None):
            return self.maindims_size

    @property
    def maindims_full_sizes(self):
        '''self.maindims_sizes when self.slices=None'''
        with self.using(slices=None):
            return self.maindims_sizes

    cls_behavior_attrs.register('maindims_means', default=False)
    maindims_means = simple_property('_maindims_means', default=False,
            doc='''whether to immediately take means across maindims when loading arrays. (default False.)
            True --> treat data across maindims as if it were the mean values, only.
                    Caution: this is different from taking means after doing calculations;
                    e.g., with maindims_means = True, 'n*T' --> mean(n)*mean(T), not mean(n*T).''')

    # # # SLICES # # #
    slicing = simple_property('_slicing', default=True,
            doc='''whether to slice maindims when loading arrays & during get_maindims_coords.
            if False, self.slices will return an empty dict.''')

    cls_behavior_attrs.register('slices', default={})
    @property
    def slices(self):
        '''slices for maindims when loading arrays & during get_maindims_coords.
        E.g. slices = dict(x=slice(0,50), y=7)
            --> slice arrays along x & y, taking the first 50 x values, and only the 7th y value.

        Notes:
            - only applies slices along arrays which actually contain the related coordinates,
                e.g. if z=10 appears in slice but loading an array with only x & y, won't apply z=10 slice.
            - supports fractional indexing, as per interprets_fractional_indexing.
                Non-integer values between -1 and 1 can be used to infer to a fraction of the dimension length,
                with negative values referring to a distance from the end, just like with integer indexing.
                Example: dict(x=slice(-0.3, None, 0.01), y=0.8), where x and y each have length 1000
                    --> equivalent to dict(x=slice(-300, None, 10), y=800).

        if self.slicing is False, self.slices will give an empty dict and cannot be set to any value!
            however, the old value of self.slices will be remembered in case slicing is set to True later.
        '''
        if not self.slicing:
            return UnsettableDict(errmsg='cannot set slices when slicing is False.')
        try:
            return self._slices
        except AttributeError:
            self._slices = dict()
            return self._slices
    @slices.setter
    def slices(self, value):
        if not self.slicing:
            raise ValueError('cannot set slices when slicing is False.')
        if value is None:
            value = dict()
        self._slices = value
    @slices.deleter
    def slices(self):
        del self._slices

    def _apply_maindims_slices_to_dict(self, d):
        '''slice entries in dict using self.slices. returns d. (Note: d will be directly altered.)'''
        for key, s_ in self.slices.items():
            if key in d:
                slice_ = interprets_fractional_indexing(s_, len(d[key]))
                d[key] = d[key][slice_]
        return d

    def standardized_slices(self):
        '''returns a copy of self.slices, but calling interprets_fractional_indexing on all slices,
        using lengths from self.maindims_full_sizes.
        '''
        maindims_sizes = self.maindims_full_sizes
        result = {}
        for key, s_ in self.slices.items():
            result[key] = interprets_fractional_indexing(s_, maindims_sizes.get(key, None))
        return result

    def slicestr(self, *, sep=', ', keep_None=False):
        '''string representation of self.slices, for use in filenames, titles, etc.
        comma-separated, alphabetized, ignoring slice(None).
        Supports single-indexes (e.g. x=5), slices (e.g. y=slice(0, 4)),
            and fractional indexing (e.g. z=slice(0, 0.5, 0.01)),
            though fractional indexing will be converted to ints.

        sep: str, separator between slices
        keep_None: bool, whether to keep slices with value None in the string.
        '''
        slices = self.slices
        order = sorted(slices.keys())
        results = []
        maindims_sizes = None
        for key in order:
            ss = slices[key]
            if ss == slice(None):
                if keep_None:
                    results.append(f'{key}=None')
                else:
                    continue
            elif isinstance(ss, int):
                results.append(f'{key}={ss}')
                continue
            # else
            if maindims_sizes is None:  # first time getting sizes
                with self.using(slices=None):
                    maindims_sizes = self.maindims_sizes
            ss = interprets_fractional_indexing(ss, L=maindims_sizes.get(key, None))
            if isinstance(ss, slice):
                if ss.start is None and ss.step is None:
                    results.append(f'{key}=slice({ss.stop})')
                elif ss.step is None:
                    results.append(f'{key}=slice({ss.start},{ss.stop})')
                else:
                    results.append(f'{key}=slice({ss.start},{ss.stop},{ss.step})')
            elif is_iterable(ss):
                raise InputError(f'cannot produce slicestr with iterable self.slices[{key!r}]={ss}')
            else:  # probably an int
                results.append(f'{key}={slice_}')
        return sep.join(results)

    def title_with_slices(self, *, sep=', ', keep_None=False):
        '''return self.title with slicestr appended (after sep), if slicestr is not empty.
        see self.slicestr() for more details.
        '''
        slicestr = self.slicestr(sep=sep, keep_None=keep_None)
        title = self.title
        return title if slicestr == '' else f'{title}{sep}{slicestr}'

    # # # MULTI-SLICES # # #
    cls_behavior_attrs.register('multi_slices', getdefault=lambda ql: MultiSlices(dims=ql.maindims))
    @property
    @format_docstring(**_paramdocs_multi_slices, sub_ntab=2)
    def multi_slices(self):
        '''dict of {{key: slices dict}}.
        When getting any vars across maindims, make a Dataset by applying each of these, separately.
        If len(multi_slices)>0 then ignore self.slices.

        Can also provide special keys 'ndim' and/or 'ikeep' to create special slices:
            Example: if self.maindims=['x', 'y', 'z'], then self.multi_slices = dict(ndim=2, ikeep=0)
                is equivalent to: self.multi_slices = dict(x_y=dict(z=0), x_z=dict(y=0), y_z=dict(x=0))
            Details:
                ndim: {ndim}
                ikeep: {ikeep}

            Can also set these as attributes of self.multi_slices to achieve the same effect.
            E.g. self.multi_slices.ndim = 2
        '''
        if not self.slicing:
            return UnsettableDict(errmsg='cannot set multi_slices when slicing is False.')
        try:
            return self._multi_slices
        except AttributeError:
            self._multi_slices = self._new_multi_slices()
            return self._multi_slices
    @multi_slices.setter
    def multi_slices(self, value):
        '''set self.multi_slices. If value is not an instance of MultiSlices, convert it to one.'''
        if not self.slicing:
            raise ValueError('cannot set multi_slices when slicing is False.')
        if not isinstance(value, self._multi_slices_cls):
            if not isinstance(value, dict):
                errmsg = (f'multi_slices must be a dict or a {self._multi_slices} object,'
                          f' but got type(value)={type(value)}.')
                raise ValueError(errmsg)
            value = self._new_multi_slices(**value)  # dict but not MultiSlices
        self._multi_slices = value
    @multi_slices.deleter
    def multi_slices(self):
        del self._multi_slices

    _multi_slices_cls = MultiSlices  # cls used for self.multi_slices.

    def _new_multi_slices(self, **kw):
        '''called when self.multi_slices accessed but not yet set; create & return new MultiSlices.'''
        kw.setdefault('dims', self._multi_slices_dims_default)
        return self._multi_slices_cls(**kw)

    def _multi_slices_dims_default(self):
        '''function to get multi_slices dims, by default.
        Would love to use (lambda: self.maindims) instead of this function,
            however lambdas are not pickleable, thus incompatible with multiprocessing module.
        Providing this function allows the default multi_slices to still be pickleable.
        '''
        return self.maindims

    multi_slices_ndim = alias_child('multi_slices', 'ndim', doc=_paramdocs_multi_slices['ndim'])
    multi_slices_ikeep = alias_child('multi_slices', 'ikeep', doc=_paramdocs_multi_slices['ikeep'])

    # # # LOAD MAINDIMS VAR # # #
    def load_maindims_var(self, var, *args, u=None, assign_labels=True, **kw):
        '''return var, formatted as an xarray with proper details for PlasmaCalcs.
        loading var should give an array with self.maindims as dimensions.

        Also does these steps:
            1) assign maindims coords via self.assign_maindims_coords().
            2) slice array via self.slices.
            3) convert units, if u is not None
            4) set result.attrs['units'] = self.units
            5) if self.maindims_means: take mean of result, across all maindims.
            6) use result = self._maindims_postprocess_callback(result), if possible.

        u: None, value, or str
            units factor for the result.
            None --> don't do any units conversions.
            str --> multiply result by self.u(u)
            value --> multiply result by u
        assign_labels: bool
            whether to assign_maindims_coords and self.record_units.
            Recommend to always use True, unless using this function internally.
            (e.g. for load_maindims_var_across_dims, only use the first time, for efficiency.)
            IGNORED if self.maindims_means.

        Note:
            If load_direct(var) uses an override or gets from cache or self.setvars,
                skip steps 1,2,3,4
            ([TODO] Might need to reconsider this behavior?)
        Note:
            If self.multi_slices are provided, load_maindims_var for each slice,
            then combine results into an xarray.Dataset.
            if assign_labels=False, combine results into a dict instead.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        # if multi_slices are provided, load_maindims_var for each slice then combine results.
        orig_multi_slices = self.multi_slices.get_slices()
        if len(orig_multi_slices) > 0:
            with self.using(multi_slices=dict()):  # don't recurse on multi_slices.
                results = dict()
                for key, mslice in orig_multi_slices.items():
                    with self.using(slices=mslice):
                        results[key] = self.load_maindims_var(var, *args, u=None,
                                                              assign_labels=assign_labels, **kw)
            if assign_labels:
                # convert to Dataset; be sure to keep any common attrs too!
                keys = list(results.keys())
                if len(keys) == 0:
                    common_attrs = None
                elif len(keys) == 1:
                    common_attrs = results[keys[0]].attrs.copy()
                else:
                    common_attrs = results[keys[0]].attrs.copy()
                    for key in keys[1:]:
                        for k, v in results[key].attrs.items():
                            if k in common_attrs and common_attrs[k] != v:
                                del common_attrs[k]
                return xr.Dataset(results, attrs=common_attrs)
            else:  # if not assigning labels, return as dict.
                return results
        # <-- multi_slices were not provided.
        # bookkeeping
        assigning_labels = (assign_labels or self.maindims_means)
        # [TODO](maybe) internally maybe write two different functions,
        #   one with assigning_labels=True, one with assigning_labels=False...
        # get value
        result = self.load_direct(var, *args, **kw)
        if getattr(self, '_load_direct_used_override', False) is not None:
            # either used an override, or got value from cache or self.setvars.
            # in this case, skip steps 1-4. (see docstring)
            pass
        elif getattr(self, 'snap', None) is INPUT_SNAP:
            # used the "override": load value based on eppic.i file.
            pass
        else:
            # got result directly from a file. Do steps 1-4. (see docstring).
             # (1) assign maindims coords
            if assigning_labels:
                result = self.assign_maindims_coords(result)
            # (2) slice array (unless already sliced it in load_direct)
            if not self._slice_maindims_in_load_direct:
                if assigning_labels:
                    result = self.slice_maindims(result)
                else:
                    result = self._slice_maindims_numpy(result)
            # (3) convert units
            if u is not None:
                if isinstance(u, str):
                    u = self.u(u)
                result = result * u
            # (4) set result.attrs['units']
            if assigning_labels:
                try:
                    self_record_units = self.record_units
                except AttributeError:
                    pass  # that's fine, we just won't record units.
                else:
                    result = self_record_units(result)
        # (5) take mean across maindims, if applicable.
        if self.maindims_means:
            # only take mean across maindims which actually appear in result.dims
            if hasattr(result, 'dims') and hasattr(result, 'mean'):
                dims = result.dims
                to_mean = [dim for dim in self.maindims if dim in dims]
                if len(to_mean) > 0:
                    result = result.mean(to_mean)
        # (6) postprocess with self._maindims_postprocess_callback, if applicable.
        try:
            callback = self._maindims_postprocess_callback
        except AttributeError:
            pass  # that's fine, just don't do any postprocessing.
        else:
            if callback is not None:
                result = callback(result)
        # finished. return result.
        return result

    _slice_maindims_in_load_direct = False  # if True, load_direct should slice maindims

    def _load_maindims_var_with_labels(self, var, *args, **kw):
        '''equivalent to self.load_maindims_var(var, *args, assign_labels=True, **kw)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.load_maindims_var(var, *args, assign_labels=True, **kw)

    def _load_maindims_var_without_labels(self, var, *args, **kw):
        '''equivalent to self.load_maindims_var(var, *args, assign_labels=False, **kw)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.load_maindims_var(var, *args, assign_labels=False, **kw)

    def assign_maindims_coords(self, array):
        '''assign maindims dims and coords, based on self.get_maindims_coords() with slicing=False.
        array must have same shape as implied by maindims and coords.
            if array is 0D, just return a 0D xr.DataArray.
        returns an xarray with proper details for PlasmaCalcs.

        This function creates a *new* xarray based on array, and maindims & coords are >0 dimensional.
        This is not like assign_{dim}_coord functions, which assign 0D coord to an existing xarray.
        '''
        ndim = np.ndim(array)
        if ndim == 0:
            return array if isinstance(array, xr.DataArray) else xr.DataArray(array)
        dims = self.maindims
        if self._slice_maindims_in_load_direct and self.slicing:
            coords = self.get_maindims_coords()
            # any non-iterable coords are not dims
            dims = [d for d in dims if is_iterable_dim(coords[d])]
        else:
            assert len(self.maindims) == ndim, f"expected {len(self.maindims)}D, but got ndim={np.ndim(array)}"
            with self.using(slicing=False):
                coords = self.get_maindims_coords()
        array = xr.DataArray(array, coords=coords, dims=dims)
        return array

    def _slice_maindims_numpy(self, array, *, h5=False):
        '''slice first len(maindims) dims of array, using self.slices.

        h5: bool
            whether 'array' might be an h5py dataset.
            if True, handle negative step in the intuitive way;
                i.e. slice with positive step, to select the expected points, then reverse order.
                (This is necessary because h5 datasets crash when sliced by negative step...)
        '''
        slices = self.slices
        if len(slices) == 0:
            return array
        slices = [slices.get(dim, slice(None)) for dim in self.maindims]
        # handle fractional indexing
        shape = array.shape
        for i, slice_ in enumerate(slices):
            slices[i] = interprets_fractional_indexing(slice_, shape[i])
        if h5:  # handle negative steps
            pre_slices = slices
            post_slices = [slice(None) for _ in slices]
            for i, (pre, post) in enumerate(zip(pre_slices, post_slices)):
                if isinstance(pre, slice) and (pre.step is not None) and (pre.step < 0):
                    raise NotImplementedError('[TODO] slicing with step<0, when h5=True')
        return array[tuple(slices)]

    def _slices_which_scalarize(self):
        '''return list of maindims which become scalars when hit by self.slices.'''
        slices = self.slices
        result = []
        for x in self.maindims:
            slicex = slices.get(x, None)
            if not ((slicex is None) or isinstance(slicex, slice) or is_iterable(slicex)):
                result.append(x)
        return result

    def slice_maindims(self, array, **kw_xarray_isel):
        '''slice maindims of array using self.slices. See help(type(self).slices) for more details.
        (if slices is an empty dict, return array, unchanged, without making a copy.)
        Only slice dims which actually appear in array.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        slices = self.slices
        if len(slices) == 0:
            return array
        array_dims = array.dims
        if len(array_dims) == 0:  # [EFF] quickcheck to handle 0D case
            return array
        to_slice = {k: v for k, v in slices.items() if k in array_dims}
        if len(to_slice) == 0:
            return array
        kw_xarray_isel.setdefault('promote_dims_if_needed', False)  # don't promote non-dimension coords here.
        return xarray_isel(array, to_slice, **kw_xarray_isel)  # <-- handles fractional indexing internally.

    # # # LOAD MAINDIMS VAR ACROSS DIMS # # #
    def load_maindims_var_across_dims(self, var, dims=None, *, skip=[], u=None, **kw):
        '''load maindims var across these dims. Use all dims from self.dimensions if dims is None.
        Only loads across the current value of these dims (e.g., self.fluid, not self.fluids).
            (Can set current value to multiple values e.g. self.component = ('x', 'y').)

        u: None, value, or str
            units factor for the result.
            None --> don't do any units conversions.
            str --> multiply result by self.u(u)
            value --> multiply result by u
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        _shift_special = {'snap': [INPUT_SNAP]}  # [TODO] allow subclass to alter... don't hard-code it here.
        return self.load_across_dims(loader=self._load_maindims_var_without_labels, var=var,
                                     loader0=self._load_maindims_var_with_labels,
                                     dims=dims, skip=skip, u=u,
                                     _shift_special=_shift_special, **kw)
