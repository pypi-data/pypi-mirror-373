"""
File Purpose: slices for fft.
"""
import warnings

from .fft_dimnames import FFTDimname
from ..docs_tools import format_docstring
from ..sentinels import UNSET
from ..xarray_tools import xarray_isel
from ...errors import InputError, DimensionKeyError

from ...defaults import DEFAULTS

_paramdocs_fft_slices = {
    'keep': f'''None, True, dict, or number in 0 < keep <= 1
        implies the fraction of each dimension to keep.
        (ignored for any dimensions which already have a slice specified.)
        e.g. keep=0.4 with length=1000 would result in slice(300, 700),
            since that keeps 400 out of 1000 points, and is centered at 1000/2.
        None --> ignored.
        True --> use keep = DEFAULTS.FFT_KEEP (default: {DEFAULTS.FFT_KEEP}).
        dict --> different value in each dimension;
                keys can be pre-fft OR post-fft dimension names.''',
    'half': '''None, str, or iterable of strs
        dimensions along which to keep only the right half of the result.
        (ignored for any dimensions which already have a slice specified.)
        None --> ignored.
        str or iterable of strs -->can be pre-fft OR post-fft dimension name(s).
        Applied after keep, e.g. keep=0.4, length=1000, half='x' --> slice(500, 700) for x.''',
    'step': '''None, dict, int, or non-integer between -1 and 1
        step to take along each dim.
        (ignored for any dimensions which already have a slice specified.)
        fractional value --> use fraction of length (e.g. 0.01 --> 1% of dim length), min |step|=1.
        negative --> reverses direction (and swaps start & stop for the slice)
        None --> equivalent to using step=1.
        dict --> different value in each dimension;
                keys can be pre-fft OR post-fft dimension names.''',
    'missing_slices': ''''ignore', 'warn', or 'raise'
        tells how to handle keys not matching any fft-related coordinate.
        'ignore' --> silently ignore these keys. This is the default.
        'warn' --> issue a warning.
        'raise' --> raise an error.'''
}


@format_docstring(**_paramdocs_fft_slices, sub_ntab=2)
class FFTSlices(dict):
    '''slicing fft result.
    keys should be names of dimensions and/or coordinates.
        pre-fft OR post-fft names both work (e.g. 'x', 'freq_x', or 'k_x')
    values should be slices, or int, iterable, or non-integer between -1 and 1.
        fractional indexing is supported as per interprets_fractional_indexing;
        non-integers between -1 and 1 are interpreted as fractions of the length,
            e.g. slice(0.25, 0.75) --> slice(int(0.25*L), int(0.75*L))

    slices: dict
        can provide keys and values here if desired, instead of directly as kwargs.

    The following can be provided during __init__ or set as attrs of self:
        SPECIAL SLICES OPTIONS:
            keep: {keep}
            half: {half}
            step: {step}
        OTHER OPTIONS:
            missing_slices: {missing_slices}
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, *args_super, slices=dict(),
                 keep=None, half=None, step=None, missing_slices='ignore', **kw_super):
        super().__init__(*args_super, **slices, **kw_super)
        self.keep = keep
        self.half = half
        self.step = step
        self.missing_slices = missing_slices

    _kw_init = ('keep', 'half', 'step', 'missing_slices')

    def as_kw(self):
        '''return dict of kwargs to use to recreate this object.'''
        kw = {k: getattr(self, k) for k in self._kw_init}
        kw['slices'] = self
        return kw

    def copy(self):
        '''return a copy of self'''
        return type(self)(**self.as_kw())

    # # # APPLYING SLICES # # #
    @format_docstring(**_paramdocs_fft_slices, sub_ntab=1)
    def applied_to(self, fft_result, dims=None, *, missing_slices=UNSET):
        '''apply slices from self to fft_result.
        fft_result: array, probably xarray.DataArray.
            the result of an fft along one or more dimensions.
        dims: None or iterable of strs
            apply slicing only to these dimensions.
            None --> use fft_result.dims.
            any of these can be pre-fft dims, in which case will use the corresponding post-fft dim,
                inferred from fft_result. E.g. 'x' --> 'freq_x' or 'k_x' if one of those is in fft_result.
                Any pre-fft dims with no corresponding dim in fft_result will cause DimensionKeyError. 
        missing_slices: UNSET or {missing_slices}
            UNSET --> use self.missing_slices.
        additional kwargs are passed to self.get_slices.
        '''
        if dims is None:
            post_fft_dims = fft_result.dims
        else:
            post_fft_dims = []
            for d in dims:
                dname = FFTDimname.implied_from(d, fft_result.dims, post_fft=True)
                post_fft_dims.append(dname.post)
        slices = self.get_slices(post_fft_dims, missing_slices=missing_slices)
        return xarray_isel(fft_result, slices)

    @format_docstring(**_paramdocs_fft_slices, sub_ntab=1)
    def get_slices(self, post_fft_dims, *, missing_slices=UNSET):
        '''return slices for each dim in post_fft_dims.

        post_fft_dims: iterable of strs
            names of dimensions in the fft result, for which to get slices now.
        missing_slices: UNSET or {missing_slices}
            UNSET --> use self.missing_slices.

        result will be a dict with keys from post_fft_dims,
            excluding any keys for which self provides no slicing instructions.
        '''
        # missing slices bookkeeping
        if missing_slices is UNSET:
            missing_slices = self.missing_slices
        if missing_slices not in {'ignore', 'warn', 'raise'}:
            raise InputError(f"expected missing_slices in ('ignore', 'warn', 'raise'), but got {missing_slices}")
        if missing_slices != 'ignore':
            self._unfound_slices = set(self.keys())
        # getting result
        slices = dict()
        for dpost in post_fft_dims:
            dslice = self.get_slice(dpost)
            if dslice is not None:
                slices[dpost] = dslice
        # missing slices bookkeeping
        if missing_slices != 'ignore' and len(self._unfound_slices) > 0:
            errmsg = (f'Found slices keys {self._unfound_slices} not matching '
                      f'any post-fft dim ({post_fft_dims}) '
                      f'or pre-fft dim ({[FFTDimname.from_post(dpost).pre for dpost in post_fft_dims]}).')
            if missing_slices == 'warn':
                warnings.warn(errmsg)
            else:  # missing_slices == 'raise'
                raise DimensionKeyError(errmsg)
        # return result
        return slices

    def _mark_slice_as_found(self, key):
        '''self._unfound_slices -= {key}, if self._unfound_slices exists.'''
        if hasattr(self, '_unfound_slices'):
            self._unfound_slices -= {key}

    def get_slice(self, post_fft_dim):
        '''return slice for this dimension. Must provide name before & after fft,
        to ensure self is compatible with using pre & post fft names.
        '''
        if post_fft_dim in self:
            self._mark_slice_as_found(post_fft_dim)
            return self[post_fft_dim]
        # else, check pre_fft_dim
        pre_fft_dim = FFTDimname.from_post(post_fft_dim).pre
        if pre_fft_dim in self:
            self._mark_slice_as_found(pre_fft_dim)
            return self[pre_fft_dim]
        # else, get special slice
        return self.get_special_slice(post_fft_dim)
    
    def get_special_slice(self, post_fft_dim):
        '''return slice for this dim assuming it is a special case (only affected by keep, half, step).'''
        half = self.half
        keep = self.keep
        step = self.step
        if keep is None and half is None and step is None:
            return None
        # # else, get half, keep, & step along this dimension.
        pre_fft_dim = FFTDimname.from_post(post_fft_dim).pre
        # half
        half = [] if half is None else ([half] if isinstance(half, str) else half)
        half = pre_fft_dim in half or post_fft_dim in half
        # step
        if isinstance(step, dict):
            if pre_fft_dim in step:
                step = step[pre_fft_dim]
            elif post_fft_dim in step:
                step = step[post_fft_dim]
            else:
                step = None
        # keep
        input_keep = keep
        if isinstance(keep, dict):
            if pre_fft_dim in keep:
                keep = keep[pre_fft_dim]
            elif post_fft_dim in keep:
                keep = keep[post_fft_dim]
            else:
                keep = None
        if keep is True:
            keep = DEFAULTS.FFT_KEEP
        if keep is None:
            keep = 1
        if keep < 0 or keep > 1:
            raise InputError(f"expected keep in 0 < keep <= 1, but got keep={keep}")
        # calculate high & low values in slice, based on keep.
        if half:
            keeplow = 0.5
        else:
            keeplow = None if keep==1 else 0.5 - keep/2
        keephigh = None if keep==1 else 0.5 + keep/2
        # # now, get special slice
        if step is None or step > 0:
            return slice(keeplow, keephigh, step)
        else:
            return slice(keephigh, keeplow, step)

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''returns list of contents to go into self.__repr__.'''
        contents = []
        if self.keep is not None:
            contents.append(f'keep={self.keep!r}')
        if self.half is not None:
            contents.append(f'half={self.half!r}')
        if self.step is not None:
            contents.append(f'step={self.step!r}')
        if self.missing_slices != 'ignore':
            contents.append(f'missing_slices={self.missing_slices!r}')
        return contents

    def __repr__(self):
        contents = self._repr_contents()
        contents.append(super().__repr__())
        contents_str = ', '.join(contents)
        return f'{type(self).__name__}({contents_str})'

    # # # EQUALITY # # #
    def __eq__(self, other):
        '''return True if self is equal to other. (other can be any type.)'''
        if not isinstance(other, type(self)):
            return False
        if self.keep != other.keep:
            return False
        if self.half != other.half:
            return False
        if self.step != other.step:
            return False
        return super().__eq__(other)

    def __ne__(self, other):
        '''return self != other. Equivalent to: not (self==other).'''
        # (Defined in order to use __eq__ from this class instead of from super().)
        return not (self == other)
