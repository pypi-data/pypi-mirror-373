"""
File Purpose: fft calculations
"""

from ..quantity_loader import QuantityLoader
from ...errors import DimensionError, DimensionKeyError
from ...tools import (
    simple_property, alias, alias_child,
    format_docstring,
    UNSET,
    xarray_fftN, xarray_ifftN, xarray_lowpass,
    FFTDimname, FFTSlices,
)
from ...defaults import DEFAULTS

FFT_VARS = 'xyzt'  # one-letter string coordinate name options for fft.
_MAX_N_FFT_VARS = len(FFT_VARS)   # max number of FFT_VARS in a single call

class FFTLoader(QuantityLoader):
    '''fft calculations, e.g. fft2, fft. 
    self.fft_dims controls which dims to take the fft over.
    '''
    # # # HELPER METHODS # # #
    @format_docstring(xarray_fftN_docs=xarray_fftN.__doc__, sub_ntab=2)
    def fftN(self, array, dim=UNSET, ds=None, *, slices=UNSET, **kw_xarray_fftN):
        '''xarray_fftN with defaults for dim & slices determined by self.fft_dims, self.fft_slices.
        kwargs are passed to xarray_fftN. For convenience, docs for xarray_fftN are copied below.

        xarray_fftN docs
        ----------------
            {xarray_fftN_docs}
        '''
        if dim is UNSET:
            dim = self.fft_dims_for(array)
        if slices is UNSET:
            slices = self.fft_slices
        return xarray_fftN(array, dim, ds=ds, slices=slices, **kw_xarray_fftN)

    fft = alias('fftN')  # alias to fftN, for improved discoverability.

    @format_docstring(xarray_ifftN_docs=xarray_ifftN.__doc__, sub_ntab=2)
    def ifftN(self, array, dim=UNSET, df=None, *, x0=0, ds=None, **kw_xarray_ifftN):
        '''xarray_ifftN with defaults for dim determined by self.fft_dims.
        kwargs are passed to xarray_ifftN. For convenience, docs for xarray_ifftN are copied below.

        xarray_ifftN docs
        -----------------
            {xarray_ifftN_docs}
        '''
        if dim is UNSET:
            dim = self.ifft_dims_for(array)
        return xarray_ifftN(array, dim, df=df, x0=x0, ds=ds, **kw_xarray_ifftN)

    ifft = alias('ifftN')  # alias to ifftN, for improved discoverability.

    @format_docstring(xarray_lowpass_docs=xarray_lowpass.__doc__, sub_ntab=2)
    def lowpass(self, array, dim=UNSET, keep=UNSET, *, keep_r=UNSET, **kw_xarray_lowpass):
        '''xarray_lowpass with defaults for dim & keep determined by self.fft_dims, self.lowpass_keep.
        kwargs are passed to xarray_lowpass. For convenience, docs for xarray_lowpass are copied below.

        xarray_lowpass docs
        -------------------
            {xarray_lowpass_docs}
        '''
        if dim is UNSET:
            dim = self.fft_dims_for(array)
        if keep is UNSET and keep_r is UNSET:
            keep = self.lowpass_keep
        return xarray_lowpass(array, dim, keep=keep, keep_r=keep_r, **kw_xarray_lowpass)

    # # # BEHAVIOR ATTRS # # #
    cls_behavior_attrs.register('fft_dims', getdefault=lambda ql: getattr(ql, 'maindims', []))
    
    @property
    def _extra_kw_for_quantity_loader_call(self):
        '''extra kwargs which can be used to set attrs self during self.__call__.
        The implementation here returns ['fft_keep', 'fft_half', 'fft_step'] + any values from super().
        '''
        return ['fft_keep', 'fft_half', 'fft_step'] + super()._extra_kw_for_quantity_loader_call

    @property
    def fft_dims(self):
        '''the dims over which to possibly apply fft (FFTLoader methods).
        will only apply fft along these dims for an array if they actually appear in the array.
        None --> use self.maindims. (this is the default.)
        See also: self.fft_dims_for(array).
        '''
        if getattr(self, '_fft_dims', None) is None:
            return getattr(self, 'maindims', [])
        else:
            return self._fft_dims
    @fft_dims.setter
    def fft_dims(self, value):
        self._fft_dims = value

    def fft_dims_for(self, array):
        '''return the dims over which to apply fft for this array.
        This is the intersection of self.fft_dims and array.dims.
        '''
        return tuple(dim for dim in self.fft_dims if dim in array.dims)

    def ifft_dims_for(self, array):
        '''return dims over which to apply ifft for this array.
        This is the self.fft_dims which correspond to dims in array.dims,
            though not via exact match.
            E.g. 'freq_x' or 'k_x' in array.dims, if 'x' in fft_dims.
        '''
        names = []
        for s in self.fft_dims:
            try:
                names.append(FFTDimname.implied_from(s, array.dims, post_fft=True))
            except DimensionKeyError:
                continue
        return tuple(names)

    _fft_slices_cls = FFTSlices  # cls used for self.fft_slices.

    cls_behavior_attrs.register('fft_slices', default=FFTSlices())
    fft_slices = simple_property('_fft_slices', setdefaultvia='_new_fft_slices',
            doc='''the dict of indexers to apply to all fft results from self, by default.
            keys can be a pre-fft or post-fft dimension name,
                e.g. 'x' or 'freq_x' both lead to slicing of the result's 'freq_x' dimension.
                (note if rad=True it would be 'k_x' in the result, and 'x' would apply but not 'freq_x'.)
                all other keys (not a pre-fft or post-fft dimension name) are ignored.
            values can be slice, int, iterable, or non-integer value between -1 and 1.
                fractional values are interpreted as a fraction of the length of the corresponding dimension,
                as per interprets_fractional_indexing. Negative fractions refer to distance from the end.
                e.g., dict(x=slice(-0.3, None, 0.01), y=0.8), where x and y correspond to length 1000,
                    would be equivalent to dict(x=slice(-300, None, 10), y=800).
            Can also have special keys (which apply to all fft dims without a specifically-related key):
                keep: fraction of each dimension to keep,
                    e.g. keep=0.4 with length=1000 would result in slice(300, 700),
                    since that keeps 400 out of 1000 points, and is centered at 1000/2.
                half: dimension(s) along which to keep only the right half of the result.
                step: slice step. Can also be fractional to use fraction of dimension length.

                For more help on special keys, see help(self._fft_slices_cls) or help(FFTSlices)''')
    @fft_slices.setter
    def fft_slices(self, value):
        '''set self.fft slices. If value is not an instance of FFTSlices, convert it to one.'''
        if not isinstance(value, self._fft_slices_cls):
            if not isinstance(value, dict):
                raise TypeError(f'fft_slices must be a dict, but got type(value)={type(value)}')
            value = self._fft_slices_cls(**value)
        self._fft_slices = value

    def _new_fft_slices(self):
        '''Called when self.fft_slices accessed but not yet set; create & return new FFTSlices.'''
        return self._fft_slices_cls()

    fft_keep = alias_child('fft_slices', 'keep')  # alias to fft_slices.keep
    fft_half = alias_child('fft_slices', 'half')  # alias to fft_slices.half
    fft_step = alias_child('fft_slices', 'step')  # alias to fft_slices.step

    cls_behavior_attrs.register('lowpass_keep', default=DEFAULTS.LOWPASS_KEEP)
    lowpass_keep = simple_property('_lowpass_keep', setdefault=lambda: DEFAULTS.LOWPASS_KEEP,
        doc='''the default value for "keep" in self.lowpass. 0 < lowpass_keep <= 1.
            Or, can be a dict of {dim: keep} pairs, to use different keep for different dims.
            To use keep_r instead of keep, call lowpass directly and enter keep_r there.''')


    # # # LOADABLE QUANTITIES # # #
    @known_pattern(r'(rad)?fft(\d*)_(.+)', deps=[2])  # 'radfft_{var}', 'fft_{var}', 'radfft{N}_{var}', or 'fft{N}_{var}'
    def get_fft(self, var, *, _match=None):
        '''N-dimensional fft. fft(var). Applied along all fft_dims in array.
        self.get('[rad]fft[N]_[var]'), where [rad]='rad' or '', and [N]=any integer or ''
            E.g. 'fft_var', 'radfft_var', 'fft1_var', 'fft2_var', 'radfft1_var', 'radfft2_var'.
        'rad' --> multiply result's frequency coordinates by 2 * pi.
                (array values will be the same either way, but coordinates will be different.)
        N provided --> fft must be along exactly this many dimensions, else crash with DimensionError.
                E.g. N=2 means self(array) must have exactly 2 dims which are also in self.fft_dims.
                Feel free to separately self.fft_dims, or enter it as a kwarg via self(..., fft_dims=...).
        '''
        radstr, Nstr, here = _match.groups()
        array = self(here)
        fft_dims = self.fft_dims_for(array)
        if len(Nstr) > 0:
            N = int(Nstr)
            if len(fft_dims) != N:
                errmsg = f"'{radstr}fft{N}_...' requires exactly {N} dims, but got {len(fft_dims)} dims: {fft_dims}"
                raise DimensionError(errmsg)
        rad = (radstr == 'rad')
        # [TODO] for efficiency, put 'ds' in deps and pass 'ds' values to xarray_fftN,
        #    instead of generating coord array, then making xarray_fftN determine ds from coord array.
        #    (bookkeeping might be a bit tricky since fft_dims aren't guaranteed to be only spatial.)
        return self.fftN(array, fft_dims, rad=rad)

    # 'radfft{dims}_{var}' or 'fft{dims}_{var}'. {dims} can be any dims from FFT_VARS, e.g. 'xy', 'zyt', 'xt', 'xyzt'
    @known_pattern(fr'(rad)?fft([{FFT_VARS}]{{1,{_MAX_N_FFT_VARS}}})_(.+)', deps=[2])
    @format_docstring(FFT_VARS=FFT_VARS)
    def get_fft_with_dims(self, var, *, _match=None):
        '''N-dimensional fft. fft(var). Applied along the indicated dims.
        self.get('([rad]fft[dims]_[var]'), where [rad]='rad' or '', and [dims]=any combination of {FFT_VARS}.
            E.g. 'fftx_var', 'fftt_var', 'fftyz_var', 'radfftxy_var', 'fftzyt_var', 'radfftyzt_var'.
        'rad' --> multiply result's frequency coordinates by 2 * pi.
                (array values will be the same either way, but coordinates will be different.)
        '''
        radstr, fft_dims, here = _match.groups()
        array = self(here)
        fft_dims_list = list(fft_dims)
        dims_match = self.fft_dims_for(array)
        if not all(dim in dims_match for dim in fft_dims):
            errmsg = (f"'{radstr}fft{fft_dims}_...' requires all dims ({fft_dims_list}) to be in self.fft_dims_for(array),"
                      f" but some are missing!"
                      f"\nGot self.fft_dims_for(array)={dims_match}. Note: self.fft_dims={self.fft_dims}, array.dims={array.dims}")
            raise DimensionError(errmsg)
        rad = (radstr == 'rad')
        return self.fftN(array, fft_dims, rad=rad)

    @known_pattern(r'ifft(\d*)_(.+)', deps=[1])  # 'ifft_{var}', 'ifft{N}_{var}'
    def get_ifft(self, var, *, _match=None):
        '''N-dimensional ifft. ifft(var). Applied along all fft_dims in array.
        self.get('ifft[N]_[var]'), where [N]=any integer or ''
            E.g. 'ifft_var', 'ifft1_var', 'ifft2_var'.
        N provided --> ifft must be along exactly this many dimensions, else crash with DimensionError.
                E.g. N=2 means self(array) must have exactly 2 dims which are also in self.fft_dims.
                Feel free to separately self.fft_dims, or enter it as a kwarg via self(..., fft_dims=...).
        '''
        Nstr, here = _match.groups()
        array = self(here)
        dims = self.ifft_dims_for(array)
        if len(Nstr) > 0:
            N = int(Nstr)
            if len(dims) != N:
                errmsg = f"'ifft{N}_...' requires exactly {N} dims, but got {len(fft_dims)} dims: {fft_dims}"
                raise DimensionError(errmsg)
        return self.ifftN(array, dims)

    @known_pattern(r'lowpass_(.+)', deps=[0])  # 'lowpass_{var}'
    @format_docstring(default_lowpass_keep=DEFAULTS.LOWPASS_KEEP)
    def get_lowpass(self, var, *, _match=None):
        '''lowpass filter across self.fft_dims; keep low frequencies, zero high frequencies.
        ifft(fft(self(var) * filter), where filter = 1 for low frequencies, 0 for high frequencies.

        fraction of each fft'd dimension to keep is determined by self.lowpass_keep.
            Default is DEFAULTS.LOWPASS_KEEP (default: {default_lowpass_keep}).
        '''
        here, = _match.groups()
        array = self(here)
        return self.lowpass(array)
