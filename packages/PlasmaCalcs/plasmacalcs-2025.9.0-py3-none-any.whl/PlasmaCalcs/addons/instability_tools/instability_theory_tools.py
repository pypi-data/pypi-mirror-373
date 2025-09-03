"""
File Purpose: helpful tools for analyzing results of instability theory

E.g. "get growth rate maxxed across k", "plot growth vs k"
"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .instability_xarray_accessor import itAccessor
from ...defaults import DEFAULTS
from ...errors import InputError, DimensionalityError
from ...plotting import CMAPS, current_axes_or_None
from ...quantities import angle_xy_to_hat
from ...tools import (
    UNSET,
    format_docstring,
    xarray_at_max_of,
    scalar_item,
)


### --------------------- wavevector dims --------------------- ###

itAccessor._KNOWN_KDIMS = ['kmod_dim', 'log_kmod_dim', 'kmod', 'log_kmod', 'kang']
itAccessor.register_attr('kdims', totype=None,  # totype=None <--> works for both DataArrays & Datasets.
    value=property(lambda self: [d for d in self._KNOWN_KDIMS if d in self.obj.dims],
        doc=f'''list of dimensions associated with wavevector. E.g. ['kmod_dim', 'kang'].
        Checks: {itAccessor._KNOWN_KDIMS}'''))

itAccessor._KNOWN_KMOD_DIMS = ['kmod_dim', 'log_kmod_dim', 'kmod', 'log_kmod']
itAccessor.register_attr('kmod_dim',  # totype=None is the default, no need to specify explicitly.
    value=property(lambda self: scalar_item([d for d in self._KNOWN_KMOD_DIMS if d in self.obj.dims]),
        doc=f'''name of the dimension associated with wavevector magnitude.
        E.g. 'kmod_dim'.
        Checks: {itAccessor._KNOWN_KMOD_DIMS}'''))

itAccessor._KNOWN_KMOD_COORDS = ['kmod', 'log_kmod']
itAccessor.register_attr('kmod_coord',
    value=property(lambda self: scalar_item([c for c in self._KNOWN_KMOD_COORDS if c in self.obj.coords]),
        doc=f'''name of the coordinate associated with wavevector magnitude.
        E.g. 'kmod'.
        Checks: {itAccessor._KNOWN_KMOD_COORDS}.'''))

def _un_log10(arr):
    '''return arr but in linear space, not log10 space.
    if arr.name starts with 'log_', returns 10**arr, renamed to not have 'log_'.
    Else, returns arr, unchanged.
    '''
    return 10**arr.rename(arr.name[len('log_'):]) if arr.name.startswith('log_') else arr

itAccessor.register_attr('kmod',
    value=property(lambda self: _un_log10(self.obj[self.kmod_coord]),
        doc='''wavevector magnitude. probably array[kmod_coord]. 10**result if kmod_coord starts with 'log_'.'''))

itAccessor._KNOWN_KANG_DIMS = ['kang']
itAccessor.register_attr('kang_dim',
    value=property(lambda self: scalar_item([d for d in self._KNOWN_KANG_DIMS if d in self.obj.dims]),
        doc=f'''name of the dimension associated with wavevector angle.
        E.g. 'kang'.
        Checks: {itAccessor._KNOWN_KANG_DIMS}'''))

itAccessor.register_attr('kang',
    value=property(lambda self: self.obj[self.kang_dim] if self.kang_dim=='kang' else NotImplemented,
        doc='''wavevector angle. array['kang'].'''))

itAccessor.register_attr('has_kdims_polar',
    value=property(lambda self: any(d in self.obj.dims for d in self._KNOWN_KMOD_DIMS) \
                            and any(d in self.obj.dims for d in self._KNOWN_KANG_DIMS),
        doc='''whether the object has 2D polar kdims. I.e. one kmod_dim, and one kang_dim.'''))
itAccessor.register_attr('has_kmod_coord',
    value=property(lambda self: any(c in self.obj.coords for c in self._KNOWN_KMOD_COORDS),
        doc=f'''whether the object has a kmod coordinate. I.e. one of {itAccessor._KNOWN_KMOD_COORDS}.'''))

@itAccessor.register('khat')
def xarray_khat(array):
    '''returns unit vector in the kang direction.'''
    return angle_xy_to_hat(array.it.kang)

@itAccessor.register('k')
def xarray_k(array):
    '''returns wavevector as a vector in the x-y plane.
    (result will still have z component, but its value will be 0 everywhere.)
    '''
    return array.it.kmod * array.it.khat()


### --------------------- growth & real(omega) --------------------- ###

def _imag_and_rename(arr):
    '''return arr.imag, with name='imag_{arr.name}'.'''
    return arr.imag.rename(f'imag_{arr.name}')

itAccessor.register_attr('growth', totype='array',
    value=property(lambda self: _imag_and_rename(self.obj) if self.obj.dtype == 'complex' else self.obj,
        doc='''growth rate. array.imag if complex, else returns array unchanged.
        if took imaginary part, result.name will be 'imag_{array.name}', instead of just array.name.'''))
itAccessor.register_attr('growth', totype='dataset',
    value=property(lambda self: _imag_and_rename(self.obj['omega']),
        doc='''growth rate. ds['omega'].rename('imag_omega').'''))

def _real_and_rename(arr):
    '''return arr.real, with name='real_{arr.name}'.'''
    return arr.real.rename(f'real_{arr.name}')

itAccessor.register_attr('omega_real', totype='array',
    value=property(lambda self: _real_and_rename(self.obj) if self.obj.dtype == 'complex' else self.obj,
        doc='''real part of omega. array.real if complex, else returns array unchanged.
        if took real part, result.name will be 'real_{array.name}', instead of just array.name.'''))
itAccessor.register_attr('omega_real', totype='dataset',
    value=property(lambda self: _real_and_rename(self.obj['omega']),
        doc='''real part of omega. ds['omega'].rename('real_omega').'''))

@itAccessor.register('at_growmax')
def xarray_at_growmax(array, growth=None):
    '''returns array where growth rate is maxxed across k dims from array.

    array: xarray.DataArray, or xarray.Dataset
        result == array.isel(location where growth is maxxed across k dims).
        if growth is None, array also tells growth rates via array.it.growth.
    growth: None, xarray.DataArray or xarray.Dataset
        None --> use array.it.growth
        DataArray --> growth rates (if real) or omega (if complex).
        Dataset --> get growth from ds['omega'].imag.
    '''
    if len(array.it.kdims)==0:  # edge case; no kdims to max across.
        return array
    if growth is None:
        growth = array.it.growth
    return xarray_at_max_of(array, of=growth, dim=growth.it.kdims)


### --------------------- growth thinking about k --------------------- ###

itAccessor.register_attr('nonk_dims', totype='array',
    value=property(lambda self: sorted(list(set(self.obj.dims) - set(self.kdims))),
        doc='''list of dimensions associated with array but excluding kdims.
        Guaranteed to be sorted into alphabetical order.'''))
itAccessor.register_attr('nonk_dims', totype='dataset',
    value=property(lambda self: self.obj['omega'].it.nonk_dims,
        doc='''list of dimensions associated with ds['omega'] but excluding kdims.
        Guaranteed to be sorted into alphabetical order.'''))

@itAccessor.register('growth_kmax')
def xarray_growth_kmax(array):
    '''returns growth rate, maxxed across k dims.
    For DataArrays, assumes array is an array of growth rates (if real) or omega (if complex).
    For Datasets, gets growth from ds['omega'].
    '''
    return array.it.growth.max(array.it.kdims)

@itAccessor.register('grows')
def xarray_grows(array):
    '''returns boolean array telling where input growth rate (maxxed across k) > 0.
    Equivalent: xarray_growth_kmax(array) > 0.
    growth = array if real DataArray; imag(array) if complex DataArray; ds['omega'].imag if Dataset.
    '''
    return xarray_growth_kmax(array) > 0

@itAccessor.register('kmod_at_growmax')
def xarray_kmod_at_growmax(array):
    '''returns kmod where growth rate is maxxed across k.
    growth = array if real DataArray; imag(array) if complex DataArray; ds['omega'].imag if Dataset.
    '''
    return xarray_at_growmax(array.it.kmod, array.it.growth)

@itAccessor.register('kang_at_growmax')
def xarray_kang_at_growmax(array):
    '''returns kang where growth rate is maxxed across k.
    growth = array if real DataArray; imag(array) if complex DataArray; ds['omega'].imag if Dataset.
    '''
    return xarray_at_growmax(array.it.kang, array.it.growth)

@itAccessor.register('khat_at_growmax')
def xarray_khat_at_growmax(array):
    '''returns khat for kang where growth rate is maxxed across k.
    growth = array if real DataArray; imag(array) if complex DataArray; ds['omega'].imag if Dataset.
    '''
    return angle_xy_to_hat(array.it.kang_at_growmax())

@itAccessor.register('k_at_growmax')
def xarray_kds_at_growmax(array):
    '''returns dataset of kmod & kang, where growth rate is maxxed across k.
    growth = array if real DataArray; imag(array) if complex DataArray; ds['omega'].imag if Dataset.
    result is a dataset with 2 datavars (telling kmod and kang), with names:
        array.it.kmod_coord and array.it.kang_dim.
    '''
    kmod = xarray_kmod_at_growmax(array)
    kang = xarray_kang_at_growmax(array)
    return xr.Dataset({array.it.kmod_coord: kmod, array.it.kang_dim: kang})

@itAccessor.register('k_at_growmax')
def xarray_k_at_growmax(array):
    '''returns k (vector) where growth rate is maxxes across k.
    result varies with 'component', with x corresponding to kang = 0 degrees,
        and z not included (i.e., assumes k is 2D in the x-y plane).
    '''
    kmod = xarray_kmod_at_growmax(array)
    khat = xarray_khat_at_growmax(array)
    return kmod * khat


### --------------------- wave velocity --------------------- ###

@itAccessor.register('smod_vphase')
def xarray_smod_vphase(array):
    '''returns signed magnitude of phase velocity: smod_vphase = real(omega) / |k|.
    (result's sign is same sign as real(omega).)
    Phase velocity tells wave propagation speed. Group velocity tells wave envelope speed.

    For DataArrays, assumes array is an array of real(omega) if real, or omega (if complex).
    For Datasets, gets omega from ds['omega'].

    See also: mod_vphase, vphase.
    '''
    real_omega = array.it.omega_real
    kmod = array.it.kmod
    return real_omega / kmod

@itAccessor.register('mod_vphase')
def xarray_mod_vphase(array):
    '''returns magnitude of phase velocity: mod_vphase = |real(omega)| / |k|.
    Phase velocity tells wave propagation speed. Group velocity tells wave envelope speed.

    For DataArrays, assumes array is an array of real(omega) if real, or omega (if complex).
    For Datasets, gets omega from ds['omega'].

    See also: smod_phase, vphase.
    '''
    return np.abs(array.it.smod_vphase())

@itAccessor.register('vphase')
def xarray_vphase(array):
    '''returns phase velocity (vector): vphase = (real(omega) / |k|) * khat.
    Phase velocity tells wave propagation speed. Group velocity tells wave envelope speed.

    For DataArrays, assumes array is an array of real(omega) if real, or omega (if complex).
    For Datasets, gets omega from ds['omega'].

    See also: smod_vphase, mod_vphase.
    '''
    smod_vphase = array.it.smod_vphase()
    khat = array.it.khat()
    return smod_vphase * khat


### --------------------- targetted ops --------------------- ###

_paramdocs_targetted = {
    'growth': '''DataArray or Dataset
        xarray object containing growth info.
        real DataArray --> growth tells growth rates.
        complex DataArray --> growth tells omega; rates = omega.imag.
        Dataset --> growth rates = ds['omega'].imag''',
    'target': '''None, str, DataArray, or Dataset
        xarray object of interest.''',
}


@itAccessor.register('where_grows')
@format_docstring(**_paramdocs_targetted)
def xarray_where_grows(growth, target=None, *, drop=UNSET):
    '''return target where growth > 0. Roughly: target.where(xarray_grows(growth)).
    (or, growth.where(xarray_grows(growth)) if target is None).

    growth: {growth}
    target: {target}
        result tells target.where(grows).
    drop: UNSET or bool
        whether to drop as many nan values as possible from the result.
        UNSET --> True if growth_kmax has ndim==1, else False.
                (when growth_kmax has ndim==1, it's a list of points, easy to fully drop nans.
                when ndim>=2, might not be able to drop all the nans,
                    e.g. if (x,y)=(0,0) is nan but (0,1) and (1,0) are not, cannot drop (0,0).)

    Examples:
        dsR = xr.Dataset(...)  # dataset containing omega and maybe some other values
        dsR.it.where_grows()   # dataset where growth rate > 0 for any k. (i.e. dataset where dsR.it.grows())
        dsR.it.where_grows(drop=False)   # dataset where_grows() but keep all nan regions.
        dsR.it.where_grows(array)   # array where dsR.it.grows().
        # array where dsR.it.grows(), but assign array coords' original indexes as coords.
        #  e.g. if '_mask_stack' in array coords, result will have '_mask_stack_index' too.
        dsR.it.where_grows(array.pc.index_coords())
    '''
    if target is None:
        target = growth
    elif isinstance(target, str):
        target = growth[target]
    grows = xarray_grows(growth)
    if drop is UNSET:
        drop = (grows.ndim == 1)
    return target.where(grows, drop=drop)

@itAccessor.register('where_nogrows')
@format_docstring(**_paramdocs_targetted)
def xarray_where_nogrows(growth, target=None, *, drop=UNSET):
    '''return target where growth <= 0. Roughly: target.where(~xarray_grows(growth)).
    (or, growth.where(~xarray_grows(growth)) if target is None).

    growth: {growth}
    target: {target}
        result tells target.where(~grows).
    drop: UNSET or bool
        whether to drop as many nan values as possible from the result.

    see xarray_where_grows (or itAccessor.where_grows.f) for more details.
    '''
    if target is None:
        target = growth
    elif isinstance(target, str):
        target = growth[target]
    grows = xarray_grows(growth)
    nogrows = ~grows
    if drop is UNSET:
        drop = (nogrows.ndim == 1)
    return target.where(nogrows, drop=drop)

@itAccessor.register('stack_nonk_dims', aliases=['stack_nonk'])
@format_docstring(**_paramdocs_targetted)
def xarray_stack_nonk_dims(growth, target=None, stackdim='nonk', *, order=None):
    '''return target stacked along nonk dims.

    growth: {growth}
    target: {target}
    stackdim: str
        name of the new stacked dimension.
    order: None or list of str
        if provided, prefer dimensions in this order.
        all dims not in order will be sorted alphabetically.

    Examples:
        dsR = xr.Dataset(...)  # dataset containing omega and maybe some other values
        dsR.it.nonk_stack()   # dataset, stacking all nonk_dims
        dsR.it.nonk_stack(array)   # array, stacking all nonk_dims
    '''
    if target is None:
        target = growth
    elif isinstance(target, str):
        target = growth[target]
    nonk_dims = growth.it.nonk_dims
    if len(nonk_dims) == 0:
        errmsg = f'nonk_stack(growth,...) when growth has no nonk dims. Got growth.dims={growth.dims}'
        raise InputError(errmsg)
    if order is not None:
        ordered = [d for d in order if d in nonk_dims]
        nonk_dims = ordered + [d for d in nonk_dims if d not in ordered]
    return target.stack({stackdim: nonk_dims})


### --------------------- plotting --------------------- ###

itAccessor.register_attr('GROWMAP', CMAPS['growlight'])
itAccessor.register_attr('GROW_VMIN', 0)
itAccessor.register_attr('GROW_VMAX', None)
itAccessor.register_attr('GROWPLOT_WRAP', 6)

@itAccessor.register('kw_growthplot')
def xarray_kw_growthplot(array, **kw_override):
    '''returns kwargs to use for a growth rate plot (using imshow-style kwargs).
    if array has_kdims_polar, use default polar=True,
        and default y=array.it.kmod_coord if it starts with 'log', else 'log_{kmod_coord}',
    if using polar=True, use default axsize of (2,3), and grid=True.
    '''
    kw = kw_override
    if array.it.has_kdims_polar:
        kw.setdefault('polar', True)
        kw.setdefault('grid', True)
        if array.it.has_kmod_coord:
            y = array.it.kmod_coord
            kw.setdefault('y', y if y.startswith('log') else f'log_{y}')
    if kw.get('polar', False):
        kw.setdefault('axsize', (2, 3))
        kw.setdefault('grid', True)
    # [TODO] how to learn what class of itAccessor we are talking about in here?
    #       right now the implementation doesn't respect if using
    #       a subclass of itAccessor which defines a different value for these.
    kw.setdefault('cmap', itAccessor.GROWMAP)
    kw.setdefault('vmin', itAccessor.GROW_VMIN)
    kw.setdefault('vmax', itAccessor.GROW_VMAX)
    return kw

@itAccessor.register('growthplots')
def xarray_growthplots(array, *, klines=None, **kw):
    '''like array.pc.subplots, but with default kwargs from kw_growthplot.
    Also, plots array.it.growth.
        (E.g. if array is complex, use array.imag instead.
        and if array is actually a Dataset, use array['omega'].imag instead.)
    Also, if array has kdims, and has only 1 nonk_dim, use defaults:
        row = the nonkdim,
        wrap = 6 if array.sizes[nonk dim] > 6.  (actually itAccessor.GROWPLOT_WRAP; default 6.)

    klines: None, bool, Dataset, dict, or tuple of (Dataset, dict)
        whether to plot lines representing mean free paths, and debye lengths, on each subplot.
        None --> True if input was a Dataset; False if it was a DataArray.
                (cannot infer klims from DataArray of growth values.)
        Dataset --> use to infer klims. Use only default kwargs for xarray_klines.
        dict --> use as kwargs for xarray_klines. infer klims from `array` input (must be a Dataset).
        tuple --> (Dataset, dict). use dataset to infer klims; use dict as xarray_klines kwargs.
        Internally, uses different kwarg defaults than xarray_klines. Defaults here:
            label = '{shortvar} ({fluid})'
            add_legend = True for axs[0,0], False for all other plots.
            log = infer from ylabel of top-left ax (if direction=='h', else xlabel of bottom left.)
    '''
    inputted = array
    array = array.it.growth
    kw = xarray_kw_growthplot(array, **kw)
    if len(array.it.kdims) > 0:
        nonk_dims = array.it.nonk_dims
        if len(nonk_dims) == 1:
            nonk_dim = nonk_dims[0]
            kw.setdefault('row', nonk_dim)
            if array.sizes[nonk_dim] > array.it.GROWPLOT_WRAP:
                kw.setdefault('wrap', array.it.GROWPLOT_WRAP)
    result = array.pc.subplots(**kw)
    # do klines
    if klines is None:
        klines = isinstance(inputted, xr.Dataset)
    if isinstance(klines, xr.Dataset):
        klines = (klines, dict())
    if isinstance(klines, tuple):
        inputted, klines = klines
    if klines != False:
        if klines == True:
            klines = dict()
        if klines.get('log', None) is None:  # infer log for all axs based on a single ax.
            if klines.get('direction', 'h') == 'h':  # use ylabel of top-left ax
                axlabel = result.axs[0,0].get_ylabel()
            else:  # use xlabel of bottom left ax.
                axlabel = result.axs[-1,0].get_xlabel()
            log = 'log' in axlabel.split('_')
            klines = {**klines, 'log': log}
        plt.sca(result.axs.flat[0])  # handle ax [0,0] separately.
        kw0 = {'add_legend': True, 'label': '{shortvar} ({fluid})',
                'legend_kw': DEFAULTS.ADDONS.GROWTHPLOTS_LEGEND_KW, **klines}
        xarray_klines(inputted.isel(result.isels.flat[0]), **kw0)
        for ax, isel, im in zip(result.axs.flat[1:], result.isels.flat[1:], result.images.flat[1:]):
            if im is None: continue  # don't draw klines on empty axes...
            plt.sca(ax)
            kwi = {'add_legend': False, 'label': '{shortvar} ({fluid})', **klines}
            xarray_klines(inputted.isel(isel), **kwi)
    return result

@itAccessor.register('growthplot')
def xarray_growthplot(array, *, klines=None, **kw):
    '''like array.pc.image, but with default kwargs from kw_growthplot.
    Also, plots array.it.growth.
        (E.g. if array is complex, use array.imag instead.
        and if array is actually a Dataset, use array['omega'].imag instead.)

    klines: None, bool, or dict
        whether to plot lines representing mean free paths, and debye lengths.
        None --> True if input was a Dataset; False if it was a DataArray.
                (cannot infer klims from DataArray of growth values.)
        if dict, use as kwargs for xarray_klines.
    '''
    inputted = array
    array = array.it.growth
    kw = xarray_kw_growthplot(array, **kw)
    result = array.pc.image(**kw)
    # do klines
    if klines is None:
        klines = isinstance(inputted, xr.Dataset)
    if klines != False:
        if klines == True:
            klines = dict()
        xarray_klines(inputted, **klines)
    return result

@itAccessor.register('klims_physical', totype='dataset', aliases=['klims_phys'])
def xarray_klims_physical(ds, *, to_simple=False):
    '''return copy of dataset, but also having the physical values limiting k.
    if ds has 'ldebye', result['kdebye'] = 2*pi/ldebye.
    if ds has 'lmfp', result['kmfp'] = 2*pi/lmfp.

    (similarly, recognizes 'eqperp_ldebye' and 'eqperp_lmfp';
        result keys would be 'eqperp_kdebye' and 'eqperp_kmfp'.)

    if result does not have anything to indicate any klims_physical in it, raise InputError.

    to_simple: bool
        whether to instead return result as a dict containing:
        (if any debye length specifiers exist in ds):
            'kdebye_lim': result[kdebye var]
            'kdebye_var': kdebye var name
        (if any mean free path specifiers exist in ds):
            'kmfp_lim': result[kmfp var]
            'kmfp_var': kmfp var name
        In this case, if multiple specifiers exist, crash.
    '''
    result = ds
    known = {'ldebye': 'kdebye',
             'lmfp': 'kmfp',
             'eqperp_ldebye': 'eqperp_kdebye',
             'eqperp_lmfp': 'eqperp_kmfp',
            }
    if all(k not in ds for k in known.keys()) and all(k not in ds for k in known.values()):
        errmsg = (f'dataset has no klims_physical. Expected any of {list(known)} or {list(known.values())};'
                  f' got dataset with keys: {list(ds.data_vars)}')
        raise InputError(errmsg)
    for lkey, kkey in known.items():
        if lkey in ds:
            kval = 2 * np.pi / ds[lkey]
            if kkey in ds and not np.all(kval == ds[kkey]):
                raise InputError(f'{kkey!r} already in ds, but does not match 2*pi/{lkey!r}.')
            result = result.assign({kkey: kval})
    if to_simple:
        dres = {}
        if 'kdebye' in result.data_vars and 'eqperp_kdebye' in result.data_vars:
            raise InputError('dataset has both kdebye and eqperp_kdebye. Cannot return as simple dict.')
        if 'kmfp' in result.data_vars and 'eqperp_kmfp' in result.data_vars:
            raise InputError('dataset has both kmfp and eqperp_kmfp. Cannot return as simple dict.')
        kdebye_var = 'kdebye' if 'kdebye' in result.data_vars else 'eqperp_kdebye'
        if kdebye_var in result.data_vars:
            dres['kdebye_lim'] = result[kdebye_var]
            dres['kdebye_var'] = kdebye_var
        kmfp_var = 'kmfp' if 'kmfp' in result.data_vars else 'eqperp_kmfp'
        if kmfp_var in result.data_vars:
            dres['kmfp_lim'] = result[kmfp_var]
            dres['kmfp_var'] = kmfp_var
        return dres
    else:
        return result

@itAccessor.register('klines', totype='dataset')
def xarray_klines(ds, *, log=None, mfp=dict(lw=2, color='blue'), debye=dict(lw=2, color='red'),
                  fluids=None, fluid_styles=UNSET, direction='h',
                  label='({val:.3g}) {log}{shortvar} ({fluid})', add_legend=True, legend_kw=UNSET,
                  **kw_line):
    '''draw lines representing mean free path, and debye length, on a plot with a |k| axis.

    ds: Dataset
        dataset containing klims_physical values. (see: xarray_klims_physical)
        (at least one of: 'ldebye', 'lmfp', 'eqperp_ldebye', 'eqperp_lmfp',
                          'kdebye', 'kmfp', 'eqperp_kdebye', 'eqperp_kmfp'.)
    log: None or bool
        whether to plot log10 of values, instead of just the values themselves.
        None --> True if plt.gca() axis label has 'log_' in it, else False.
                (ylabel if direction says axhline; else xlabel.)
    mfp: dict or False
        style to apply to mean free path lines.
        False --> don't plot mean free path lines.
    debye: dict or False
        style to apply to debye length lines.
        False --> don't plot debye length lines.
    fluids: None, 'min', 'max', or ('min', 'max')
        None --> plot lines for each fluid.
        'min' --> plot line for only 1 fluid, whichever makes line at smallest |k|
        'max' --> plot line for only 1 fluid, whichever makes line at largest |k|
        ('min', 'max') --> plot 'min' and 'max' lines.
        note: to plot an arbitrary subset of fluids, just use ds.isel(fluid=...) beforehand.
    fluid_styles: UNSET or dict of lists
        styles to ensure fluid lines appear visually distinct.
        E.g. {'ls': ['-', '--', ':']} --> use ls='-' for first fluid, '--' for next, etc.
        UNSET --> use DEFAULTS.PLOT.TIMELINES_CYCLE1; default is a dict of different linestyles.
    direction: 'h', 'v', 'horizontal', or 'vertical'
        direction to plot lines.
        'h' or 'horizontal' --> plt.axhline
        'v' or 'vertical' --> plt.axvline
    label: str
        label for each line. will be hit by .format(...) with the following kwargs:
            'log': 'log10 ' if log else ''.
            'var': variable name. 'kdebye', 'kmfp', 'eqperp_kdebye', or 'eqperp_kmfp'.
            'kvar': alias to 'var'
            'lvar': length variable name. E.g. 'ldbeye' instead of 'kdebye'.
            'pubvar': variable suitable for publication. 'k Debye' or 'k mean free path'
            'shortvar': shorthand variable name. 'debye' or 'mfp'
            'fluid': fluid name
            'val': value at which the line is plotted
    add_legend: bool
        whether to plt.legend()
    legend_kw: UNSET or dict
        kwargs to pass to plt.legend().
        UNSET --> use DEFAULTS.ADDONS.GROWTHPLOT_LEGEND_KW
    additional kwargs go to plt.axhline or plt.axvline.
    '''
    # bookkeeping
    KNOWN_DIRECTIONS = {'h': 'h', 'v': 'v', 'horizontal': 'h', 'vertical': 'v'}
    if direction not in KNOWN_DIRECTIONS:
        raise InputError(f'invalid direction: {direction!r}. Expected any of {list(KNOWN_DIRECTIONS)}')
    direction = KNOWN_DIRECTIONS[direction]
    plt_axline = plt.axhline if direction == 'h' else plt.axvline
    if log is None:
        ax = current_axes_or_None()
        if ax is not None:
            axlabel = ax.get_ylabel() if direction == 'h' else ax.get_xlabel()
            log = 'log' in axlabel.split('_')
    if isinstance(fluids, str):
        fluids = [fluids]
    if fluids is not None and not all(f=='min' or f=='max' for f in fluids):
        raise InputError(f'invalid fluids: {fluids!r}. Expected None, "min", "max", or ("min", "max")')
    nfluids = ds.sizes.get('fluid', 1) if fluids is None else len(fluids)
    if fluid_styles is UNSET:
        fluid_styles = DEFAULTS.PLOT.TIMELINES_CYCLE1
        list_fluid_styles = [{k: v[i%len(v)] for k, v in fluid_styles.items()} for i in range(nfluids)]
    # making lines -- kmfp
    kdict = xarray_klims_physical(ds, to_simple=True)
    if 'kmfp_lim' in kdict and mfp != False:
        klim = kdict['kmfp_lim']
        if log: klim = np.log10(klim)
        if 'fluid' not in klim.dims: raise NotImplementedError('[TODO] different fluid dim name?')
        if klim.ndim != 1: raise DimensionalityError(f'klines expects 1D; got ndim={klim.ndim}')
        if fluids is not None:
            fidx = []
            if 'min' in fluids: fidx.append(klim.argmin('fluid').item())
            if 'max' in fluids: fidx.append(klim.argmax('fluid').item())
            klim = klim.isel(fluid=fidx)
        for (f, lim), fstyle in zip(klim.groupby('fluid'), list_fluid_styles):
            ffmt = {
                'log': 'log10 ' if log else '',
                'var': kdict['kmfp_var'],
                'kvar': kdict['kmfp_var'],
                'lvar': kdict['kmfp_var'].replace('kmfp', 'lmfp'),
                'pubvar': 'k mean free path',
                'shortvar': 'mfp',
                'fluid': str(f),
                'val': lim.item(),
            }
            flabel = label.format(**ffmt)
            kw_here = {**kw_line, **mfp, **fstyle}  # order matters, if any keys are repeated.
            plt_axline(lim.item(), label=flabel, **kw_here)
    # making lines -- kdebye  # [TODO] encapsulate instead of copy-pasting.
    if 'kdebye_lim' in kdict and debye != False:
        klim = kdict['kdebye_lim']
        if log: klim = np.log10(klim)
        if 'fluid' not in klim.dims: raise NotImplementedError('[TODO] different fluid dim name?')
        if klim.ndim != 1: raise DimensionalityError(f'klines expects 1D; got ndim={klim.ndim}')
        if fluids is not None:
            fidx = []
            if 'min' in fluids: fidx.append(klim.argmin('fluid').item())
            if 'max' in fluids: fidx.append(klim.argmax('fluid').item())
            klim = klim.isel(fluid=fidx)
        for (f, lim), fstyle in zip(klim.groupby('fluid'), list_fluid_styles):
            ffmt = {
                'log': 'log10 ' if log else '',
                'var': kdict['kdebye_var'],
                'kvar': kdict['kdebye_var'],
                'lvar': kdict['kdebye_var'].replace('kdebye', 'ldebye'),
                'pubvar': 'k Debye',
                'shortvar': 'debye',
                'fluid': str(f),
                'val': lim.item(),
            }
            flabel = label.format(**ffmt)
            kw_here = {**kw_line, **debye, **fstyle}  # order matters, if any keys are repeated.
            plt_axline(lim.item(), label=flabel, **kw_here)
    # legend
    if add_legend:
        if legend_kw is UNSET:
            legend_kw = DEFAULTS.ADDONS.GROWTHPLOT_LEGEND_KW
        plt.legend(**legend_kw)
