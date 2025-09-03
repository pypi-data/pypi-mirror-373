"""
File Purpose: MultiSlices class

[TODO] encapsulate code shared between here and FFTSlices?
[TODO] record coordinate at ikeep, e.g. keep_x_y array should have coordinate z=...
"""
import itertools

from ...tools import (
    UNSET,
    format_docstring,
    simple_property,
)

_paramdocs_multi_slices = {
    'ndim': '''None or int
        None --> ignore, and do not create special slices.
        int --> create special slices to keep this many dims after applying each slice.
        Example: MultiSlices(ndim=2) is shorthand for
            "MultiSlices with one slices for every possible combination of keeping 2 dims".
        Example: MultiSlices(ndim=2, dims=['x', 'y', 'z'], ikeep=0) is equivalent to:
            MultiSlices(keep_x_y=dict(z=0), keep_y_z=dict(x=0), keep_x_z=dict(y=0))
        Example: MultiSlices(ndim=1, dims=['x', 'y', 'z'], ikeep=0) is equivalent to:
            MultiSlices(keep_x=dict(y=0, z=0), keep_y=dict(x=0, z=0), keep_z=dict(x=0, y=0))''',
    'dims': '''None, iterable of str, or callable of 0 arguments -> iterable of str.
        dimensions to consider when applying special slices.
        None --> do not create any special slices.''',
    'ikeep': '''int or number between -1 < ikeep < 1
        index to take when picking a single value for sliced dimensions for special slices.
        Default is 0, e.g. when slicing x, keep x[0].
        int --> when slicing dim, keep dim[ikeep]. E.g. 10 --> keep x[10]
        non-int between -1 and 1 --> multiply by length of dim to get index.
                                    see interprets_fractional_indexing for more details.''',
}


@format_docstring(**_paramdocs_multi_slices, sub_ntab=2)
class MultiSlices(dict):
    '''managing multiple slices dicts in one place, while also providing options for "special slices".
    Special slices options involve creating slices dicts for each possible combination of N dimensions,
        e.g. in a 3D simulation with dimensions ['x', 'y', 'z'], creating slices for N=2 means
        slices would be dict(keep_x_y=dict(z=0), keep_y_z=dict(x=0), keep_x_z=dict(y=0)).

    keys should be ANY names; these will be associated with results from applying each slice.
        (in MainDimensionsHaver, keys tell names of data_vars in resulting xarray.Dataset)
    values should be a dicts of slices or other indexers.
        e.g. one value might be {{'x': slice(0, 10), 'y': 5, 'z': 0}}.
        (in MainDimensionsHaver, these correspond to any valid value for obj.slices)

    multi_slices: dict
        can provide keys and values here if desired, instead of directly as kwargs.

    The following can be provided during __init__ or set as attrs of self:
        SPECIAL SLICES OPTIONS:
            ndim: {ndim}
            dims: {dims}
            ikeep: {ikeep}

            if ndim and dims are provided, special slices will be included in self.get_slices().
            Note that the naming convention for keys will be 'keep_'+'_'.join(unsliced_dims),
                e.g. 'keep_x', 'keep_x_y', or 'keep_x_y_z'.
                unsliced_dims will be in the same order as dims.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, *args_super, multi_slices=dict(), ndim=None, dims=None, ikeep=0, **kw_super):
        super().__init__(*args_super, **multi_slices, **kw_super)
        self.ndim = ndim
        self.dims = dims
        self.ikeep = ikeep

    _kw_init = ('ndim', 'dims', 'ikeep')

    def as_kw(self):
        '''return dict of kwargs to use to recreate this object.'''
        kw = {k: getattr(self, k) for k in self._kw_init}
        kw['multi_slices'] = self
        return kw

    def copy(self):
        '''return a copy of self'''
        return type(self)(**self.as_kw())

    # # # PROPERTIES # # #
    dims = simple_property('_dims',
            doc='''dims to consider when applying special slices.
            if set to be a callable, will call it each time getting self.dims.''')
    @dims.getter
    def dims(self):
        return self._dims() if callable(self._dims) else self._dims

    # # # GETTING SLICES # # #
    @format_docstring(**_paramdocs_multi_slices, sub_ntab=2)
    def get_slices(self, dims=UNSET, *, ikeep=UNSET):
        '''return dict of all multi_slices to apply.
        if self.ndim is None, only use the slices explicitly provided to self.
            (i.e. don't get any special slices.)
        otherwise, create and include special slices in the result.
            see self.get_special_slices for details.
            if any special slices' names match slice names explicitly provided in self,
                use the explicitly-provided slice name instead.

        dims, ikeep: passed to self.get_special_slices, if creating any special slices.
            dims: {dims}
            ikeep: {ikeep}
        '''
        result = self.get_special_slices(dims=dims, ikeep=ikeep)
        result.update(self)
        return result

    @format_docstring(**_paramdocs_multi_slices, sub_ntab=1)
    def get_special_slices(self, ndim=UNSET, dims=UNSET, *, ikeep=UNSET):
        '''return dict of special slices to apply.

        ndim: UNSET or {ndim}
            UNSET --> use self.ndim
        dims: UNSET or {dims}
            UNSET --> use self.dims
        ikeep: UNSET or {ikeep}
            UNSET --> use self.ikeep

        Note that the naming convention for keys will be 'keep_'+'_'.join(unsliced_dims),
            e.g. 'keep_x', 'keep_x_y', or 'keep_x_y_z'.
            unsliced_dims will be in the same order as dims.

        returns dict of dicts, where each inner dict is instructions for applying a slice.
            result will be empty if ndim is None or if dims is None.
        '''
        if ndim is UNSET: ndim = self.ndim
        if dims is UNSET: dims = self.dims
        if ikeep is UNSET: ikeep = self.ikeep
        if ndim is None or dims is None:
            return dict()
        if ikeep is UNSET or ikeep is None:
            raise TypeError(f'ikeep should be an int or number between -1 and 1, but got ikeep={ikeep!r}')
        result = dict()
        for unsliced_dims in itertools.combinations(dims, ndim):
            dims_to_slice = tuple(dim for dim in dims if dim not in unsliced_dims)
            key = 'keep_'+'_'.join(unsliced_dims)
            result[key] = {dim: ikeep for dim in dims_to_slice}
        return result

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''return list of strings to include in repr of self.'''
        contents = []
        if self.ndim is not None:
            contents.append(f'ndim={self.ndim}')
        if self.dims is not None:
            contents.append(f'dims={self.dims}')
        if self.ikeep != 0:
            contents.append(f'ikeep={self.ikeep}')
        return contents

    def __repr__(self):
        contents = self._repr_contents()
        contents.append(super().__repr__())
        contents_str = ', '.join(contents)
        return f'{type(self).__name__}({contents_str})'

    # # # EQUALITY # # #
    def __eq__(self, other):
        '''return whether self is equal to other.'''
        if not isinstance(other, type(self)):
            return False
        if self.ndim != other.ndim:
            return False
        if self.dims != other.dims:
            return False
        if self.ikeep != other.ikeep:
            return False
        return super().__eq__(other)

    def __ne__(self, other):
        '''return whether self is not equal to other.'''
        # (Defined in order to use __eq__ from this class instead of from super().)
        return not (self == other)
