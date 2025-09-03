"""
File Purpose: high-level xarray functions. May be especially useful for science.
E.g., gaussian filter, polynomial fit.
"""

import numpy as np
import xarray as xr

from ..imports import ImportFailed
try:
    import scipy.ndimage as scipy_ndimage
except ImportError as err:
    scipy_ndimage = ImportFailed('scipy.ndimage',
            'This module is required for some filtering functions.',
            err=err, locals=locals(), abbrv='scipy_ndimage')
try:
    import scipy.optimize as scipy_optimize
except ImportError as err:
    scipy_optimize = ImportFailed('scipy.optimize',
            'This module is required for some fitting functions.',
            err=err, locals=locals(), abbrv='scipy_optimize')


from .xarray_accessors import pcAccessor
from .xarray_agg_stats import xarray_sum
from .xarray_coords import xarray_is_sorted
from .xarray_dimensions import (
    xarray_promote_dim, xarray_ensure_dims, _paramdocs_ensure_dims,
    xarray_coarsened,
)
from .xarray_grids import xr1d
from .xarray_indexing import xarray_isel, xarray_map
from .xarray_misc import xarray_copy_kw
from ..docs_tools import format_docstring
from ..properties import simple_property
from ..sentinels import UNSET
from ...errors import (
    DimensionValueError,
    InputError, InputConflictError, InputMissingError,
)
from ...defaults import DEFAULTS


### --------------------- Interpolation --------------------- ###

@pcAccessor.register('interp_inverse', totype='array')
@format_docstring(**_paramdocs_ensure_dims)
def xarray_interp_inverse(array, interpto=None, output=None, *,
                          promote_dims_if_needed=True,
                          assume_sorted=None, assume_sorted_values=None,
                          method=None, kw_interp=None, **interpto_as_kw):
    '''interpolate a DataArray but using the array values as one of the interpolation variables;
    the result is the array of the unused interpolation coordinate.

    Example: if array has dims {{'x', 'y'}} and name 'T', and interpto specifies 'x' and 'T',
        then result will be a DataArray with dims {{'x', 'T'}} and values for 'y'.
        Special case: if interpto specifications are single values,
            the result will be scalar along that key instead of a dimension,
            e.g. if interpto['x'] = 7 (as a opposed to a 1D array like [1,2,3]),
                then result would have coordinate 'x'=7 but not have an 'x' dimension.

    [EFF] note: inefficient if choosing many values along vars other than array.name.
        each result value along those vars corresponds to its own interp call.

    The internal steps are roughly:
        (1) array.interp(all interpto vars except array.name)
        (2) array.assign_coords({{array.name: array}})
        (3) for each index along all interpto vars except array.name:
                tmp = array.isel(index).interp({{array.name: interpto[array.name]}})
                result[index] = tmp[output var]
        [TODO] still need to implement step 3 for 3D+ arrays instead of only 2D or less.

    array: xarray.DataArray
        must have non-None array.name.
    interpto: None or dict
        dictionary of {{var: value or 1D array of values}} to interpolate to.
        Keys must correspond to array.name, and coords for all except 1 dim of array.
        None --> provide interpto dict as kwargs to this function.
    output: None or str
        name for the result variable.
        None --> use the key from array.dims which is missing from interpto (after xarray_ensure_dims).
    promote_dims_if_needed: {promote_dims_if_needed}
    assume_sorted: None or bool
        whether to assume_sorted during step (1),
            i.e. during the initial interp for all interpto vars except array.name
        None --> assume_sorted if xarray_is_sorted.
        True --> assume_sorted without checking. CAUTION: only do this if you're 100% sure!
        False --> don't assume sorted. May be noticeably slower for large arrays.
    assume_sorted_values: None or bool
        whether to assume_sorted during step (3),
            i.e. during the interp using array.name as a coordinate.
        None --> assume_sorted if xarray_is_sorted. check at each index in step 3;
                 if False multiple times in a row, stop checking and just assume False.
        True --> assume_sorted without checking. CAUTION: only do this if you're 100% sure!
        False --> don't assume sorted. May be noticeably slower for large arrays.
    method: None or str
        method to pass to xarray.interp for all interpolations.
        if None, use xarray.interp method default.
    kw_interp: None or dict
        if provided, pass these kwargs to all calls of xarray.interp.
        These will eventually go to the internal interpolator method e.g. from scipy.

    interpto_as_kw: optionally, provide interpto dict as kwargs to this function.
    '''
    # misc. bookkeeping
    if array.name is None:
        raise InputError('interp_inverse expects non-None array.name.')
    if interpto and interpto_as_kw:
        raise InputConflictError('cannot provide both interpto and interpto_as_kw.')
    if interpto_as_kw:
        interpto = interpto_as_kw
    if interpto is None:
        raise InputMissingError('must provide interpto.')
    hard_var = array.name
    easy_vars = set(interpto.keys()) - {hard_var}
    interpto_easy = {k: v for k, v in interpto.items() if k != hard_var}
    interpto_hard = {hard_var: interpto[hard_var]}
    array = xarray_ensure_dims(array, easy_vars, promote_dims_if_needed=promote_dims_if_needed)
    if output is None:
        output = set(array.dims) - easy_vars - {hard_var}
        if len(output) == 0:
            errmsg = ('no acceptable output var found.'
                      f'dims={array.dims}, easy_vars={easy_vars}, hard_var={hard_var!r}')
            raise InputError(errmsg)  # [TODO] clearer debugging suggestions in errmsg.
        if len(output) >= 2:
            errmsg = ('too many acceptable output vars found.'
                      f'dims={array.dims}, easy_vars={easy_vars}, hard_var={hard_var!r}')
            raise InputError(errmsg)  # [TODO] clearer debugging suggestions in errmsg.
        output = output.pop()
    # bookkeeping of kwargs for interp
    if assume_sorted is None:
        assume_sorted = all(xarray_is_sorted(array[v]) for v in easy_vars)
    kw_interp = dict() if kw_interp is None else kw_interp.copy()
    if method is not None:
        if 'method' in kw_interp and method != kw_interp['method']:
            errmsg = f'method={method!r} but kw_interp["method"]={kw_interp["method"]!r}.'
            raise InputConflictError(errmsg)
        # else
        kw_interp['method'] = method
    # (1) intial interpolation
    array = array.interp(interpto_easy, assume_sorted=assume_sorted, **kw_interp)
    if np.any(np.isnan(array)):
        errmsg = ('initial interpolation (step 1 in xarray_interp_inverse) resulted in NaNs.\n'
                  f'This is likely due to some "out of bounds" interpto values ({easy_vars}),\n'
                  'i.e. lower than min or larger than max values of corresponding coords in array.\n'
                  'To fix, adjust requested interpolation coords for interpto vars.\n'
                  '(There is no way to find inverse when step 1 gives nans.)')
        raise DimensionValueError(errmsg)
    # (2) assign
    array = array.assign_coords({hard_var: array})
    # (3) iterating interpolations
    if array.ndim == 1:  # nothing to iterate - hard_var coord corresponds to exactly 1 dim already.
        array = xarray_promote_dim(array, hard_var)
        if assume_sorted_values is None:
            assume_sorted_values = xarray_is_sorted(array)
        array = array.interp(interpto_hard, assume_sorted=assume_sorted_values, **kw_interp)
        result = array[output].drop_vars(output)  # don't need output as a coord, it is result.values.
    elif array.ndim == 2:  # iterate over the 1 easy_var.
        if len(easy_vars) != 1:
            raise NotImplementedError('[TODO] figure out what is happening in this case & handle it.')
        easy_var = easy_vars.pop()
        easy_dim = array[easy_var].dims[0]  # not necessarily easy_var;
            # e.g. if interpto value for easy_var is DataArray with different dim.
        result = []
        if assume_sorted_values is None:
            _prev_assume_sorted = None
        else:
            _assume_sorted = assume_sorted_values
        for i_easy in range(array.sizes[easy_dim]):
            tmp = array.isel({easy_dim: i_easy})
            if assume_sorted_values is None:
                _assume_sorted = xarray_is_sorted(tmp)
                if _prev_assume_sorted == False and _assume_sorted == False:
                    assume_sorted_values = False
                _prev_assume_sorted = _assume_sorted
            tmp = xarray_promote_dim(tmp, hard_var)
            if not _assume_sorted:
                tmp = tmp.sortby(hard_var)
            tmp = tmp.drop_duplicates(hard_var)  # drop duplicates, since interp can't handle them.
            tmp = tmp.interp(interpto_hard, assume_sorted=True, **kw_interp)  # sorted=False handled above.
            tmp = tmp[output].drop_vars(output)  # don't need output as a coord, it is tmp.values.
            result.append(tmp)
        result = xr.concat(result, easy_dim)
    else:
        raise NotImplementedError('[TODO] xarray_interp_inverse with 3D+ array.')
    return result


### --------------------- Gaussian Filter --------------------- ###

@pcAccessor.register('gaussian_filter', aliases=['blur'])
@format_docstring(**_paramdocs_ensure_dims, default_sigma=DEFAULTS.GAUSSIAN_FILTER_SIGMA)
def xarray_gaussian_filter(array, dim=None, sigma=None, *,
                           promote_dims_if_needed=True, missing_dims='raise',
                           **kw_scipy_gaussian_filter):
    '''returns array after applying scipy.ndimage.gaussian_filter to it.

    array: xarray.DataArray or Dataset
        filters this array, or each data_var in a dataset.
    dim: None or str or iterable of strs
        dimensions to filter along.
        if None, filter along all dims.
    sigma: None, number, or iterable of numbers
        standard deviation for Gaussian kernel.
        if iterable, must have same length as dim.
        if None, will use DEFAULTS.GAUSSIAN_FILTER_SIGMA (default: {default_sigma}).
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs go to scipy.ndimage.gaussian_filter.
    '''
    if sigma is None:
        sigma = DEFAULTS.GAUSSIAN_FILTER_SIGMA
    return xarray_map(array, scipy_ndimage.gaussian_filter, sigma, axes=dim,
                      promote_dims_if_needed=promote_dims_if_needed,
                      missing_dims=missing_dims, **kw_scipy_gaussian_filter)


### --------------------- polyfit --------------------- ###

@pcAccessor.register('polyfit')
@format_docstring(xr_polyfit_docs=xr.DataArray.polyfit.__doc__)
def xarray_polyfit(array, coord, degree, *, stddev=False, full=False, cov=False,
                   eval=False, **kw_polyfit):
    '''returns array.polyfit(coord, degree, **kw_polyfit), after swapping coord to be a dimension, if needed.
    E.g. for an array with dimension 'snap' and associated non-dimension coordinate 't',
        xarray_polyfit(array, 't', 1) is equivalent to array.swap_dims(dict(snap='t')).polyfit('t', 1).

    stddev: bool
        whether to also return the standard deviations of each coefficient in the fit.
        if True, assign the variable 'polyfit_stddev' = diagonal(polyfit_covariance)**0.5,
            mapping the diagonal (across 'cov_i', 'cov_j') to the dimension 'degree'.
            if cov False when stddev True, do not keep_cov in the result.
        Not compatible with full=True.
    full: bool
        passed into polyfit; see below.
    cov: bool
        passed into polyfit; see below.
        Note: if stddev=True when cov=False, still use cov=True during array.polyfit,
            however then remove polyfit_covariance & polyfit_residuals from result.
    eval: bool
        whether to also return the fit, evaluated at array.coords[coord]
        if True, assign the variable 'polyfit_eval' = sum(coeff * coord**degree, 'degree').
            if stddev=True too, assign 'polyfit_eval-stddev' and 'polyfit_eval+stddev' too,
                using similar formula but using coeffs +/- stddev.

    Docs for xr.DataArray.polyfit copied below:
    -------------------------------------------
    {xr_polyfit_docs}
    '''
    array = xarray_promote_dim(array, coord)
    if stddev and full:
        raise InputConflictError('stddev=True incompatible with full=True.')
    cov_input = cov
    if stddev:
        cov = True
    result = array.polyfit(coord, degree, full=full, cov=cov, **kw_polyfit)
    if stddev:
        result = xarray_assign_polyfit_stddev(result, keep_cov=cov_input)
    if eval:
        evaled = xarray_polyfit_eval(result, at=array.coords[coord], to_dataset=True)
        result = result.assign(evaled)
    return result

@pcAccessor.register('assign_polyfit_stddev', totype='dataset')
def xarray_assign_polyfit_stddev(dataset, *, keep_cov=True):
    '''assign polyfit stddev to dataset['polyfit_stddev'], treating dataset like a result of polyfit.
    These provide some measure of "goodness of fit"; smaller stddev means better fit.

    Specifically, stddev[k] = (covariance matrix)[k,k]**0.5 for k in range(len(dataset['degree']));
        one might quote +-stddev[k] as the error bar for the coefficient at degree=dataset['degree'][k].

    dataset: xarray.Dataset
        dataset to use for calculating polyfit_stderr and in which to assign the result.
        must contain variable 'polyfit_covariance' and dimension 'degree'.
    keep_cov: bool
        whether to keep the 'polyfit_covariance' and 'polyfit_residuals' vars in the result.

    The original dataset will not be altered; a new dataset will be returned.
    '''
    cov = dataset['polyfit_covariance']
    degree = dataset['degree']
    ndeg = len(degree)
    stddev = [cov.isel(cov_i=k, cov_j=k)**0.5 for k in range(ndeg)]
    stddev = xr.concat(stddev, 'degree').assign_coords({'degree': degree})
    result = dataset.assign(polyfit_stddev=stddev)
    if not keep_cov:
        result = result.drop_vars(['polyfit_covariance', 'polyfit_residuals'])
    return result

@pcAccessor.register('polyfit_eval', totype='dataset')
def xarray_polyfit_eval(dataset, at=None, *, to_dataset=False):
    '''evaluate the polyfit in dataset at these coordinates.
    E.g. dataset has degree=2,1,0, polyfit_coefficients=7.5, -3.2, 0.4
        --> result == 7.5 * at**2 - 3.2 * at + 0.4

    if input dataset contains 'polyfit_stddev', instead returns a dataset with:
        'polyfit_eval': result (see above)
        'polyfit_eval-stddev': result when using polyfit_coefficients - polyfit_stddev.
        'polyfit_eval+stddev': result when using polyfit_coefficients + polyfit_stddev.

    at: None or array
        if provided, evaluate polyfit dataset here.
        None --> input MUST be a dataset which already has 'polyfit_eval';
            instead of computing terms, just return relevant info which exists in dataset,
            i.e. 'polyfit_eval', 'polyfit_eval-stddev', and/or 'polyfit_eval+stddev'.
    to_dataset: bool
        whether to return dataset even if input does not contain 'polyfit_stddev'
        True --> result will always be a dataset.
    '''
    if at is None:
        if 'polyfit_eval' not in dataset:
            return InputMissingError("when at=None, dataset must contain 'polyfit_stddev'.")
        relevant = ['polyfit_eval']
        for v in ['polyfit_eval-stddev', 'polyfit_eval+stddev']:
            if v in dataset:
                relevant.append(v)
        return dataset[relevant]
    coeffs = dataset['polyfit_coefficients']
    if 'polyfit_stddev' in dataset:
        stddev = dataset['polyfit_stddev']
        coeffs = xr.Dataset({'polyfit_eval': coeffs,
                             'polyfit_eval-stddev': coeffs - stddev,
                             'polyfit_eval+stddev': coeffs + stddev})
    elif to_dataset:
        coeffs = xr.Dataset({'polyfit_eval': coeffs})
    terms = coeffs * at**dataset['degree']
    return xarray_sum(terms, 'degree')

@pcAccessor.register('coarsened_polyfit')
@format_docstring(xr_polyfit_docs=xr.DataArray.polyfit.__doc__)
def xarray_coarsened_polyfit(array, coord, degree, window_len, *,
                             dim_coarse='window', keep_coord='middle',
                             assign_coarse_coords=True,
                             boundary=UNSET, side=UNSET,
                             stride=UNSET, fill_value=UNSET, keep_attrs=UNSET,
                             **kw_polyfit
                             ):
    '''returns result of coarsening array, then polyfitting along the fine dimension, in each window.
    E.g., make windows of length 10 along 't', then polyfit each window along 't',
    then concat the results from each window, along dim_coarse (default: 'window').

    coord: str
        coordinate to polyfit along.
    degree: int
        degree of polynomial to fit.
    window_len: int or None
        length of window to coarsen over.
        None --> polyfit without coarsening; equivalent to window_len = len(array.coords[coord])
    dim_coarse: str, default 'window'
        name of coarse dimension; the i'th value here corresponds to the i'th window.
    keep_coord: False or str in ('left', 'right', 'middle')
        along the dim_coarse dimension, also provide some of the original coord values.
        'left' --> provide the left-most value in each window.
        'middle' --> provide the middle value in each window.
        'right' --> provide the right-most value in each window.
        False --> don't provide any of the original coord values.
        if not False, result will swap dims such that coord is a dimension instead of dim_coarse.
    assign_coarse_coords: bool or coords
        coords to assign along the dim_coarse dimension.
        True --> use np.arange.
        False --> don't assign coords.
    boundary, side: UNSET or value
        if provided (not UNSET), pass this value to coarsen().
    stride, fill_value, keep_attrs: UNSET or value
        if provided (not UNSET), pass this value to construct().

    additional **kw are passed to polyfit.

    Docs for xr.DataArray.polyfit copied below:
    -------------------------------------------
    {xr_polyfit_docs}
    '''
    # bookkeeping
    if keep_coord not in ('left', 'middle', 'right', False):
        raise InputError(f'invalid keep_coord={keep_coord!r}; expected "left", "middle", "right", or False.')
    # if window_len is None or <1, don't coarsen at all.
    if window_len is None:
        return xarray_polyfit(array, coord, degree, **kw_polyfit)
    # coarsen
    coarsened = xarray_coarsened(array, coord, window_len,
                                dim_coarse=dim_coarse,
                                assign_coarse_coords=assign_coarse_coords,
                                boundary=boundary, side=side,
                                stride=stride, fill_value=fill_value, keep_attrs=keep_attrs)
    # bookkeeping
    n_windows = len(coarsened[dim_coarse])
    if n_windows < 1:
        errmsg = f'coarsened array has n_windows={n_windows} < 1; cannot polyfit.'
        raise DimensionValueError(errmsg)
    # polyfitting
    promoted = []
    for i_window in range(n_windows):
        prom = xarray_promote_dim(coarsened.isel({dim_coarse: i_window}), coord)
        promoted.append(prom)
    polyfits = []
    for arr in promoted:
        pfit = xarray_polyfit(arr, coord, degree, **kw_polyfit)
        polyfits.append(pfit)
    if keep_coord:
        results = []
        for i_window, (arr, prom) in enumerate(zip(polyfits, promoted)):  # i_window just for debugging
            i_keep = {'left': 0, 'middle': 0.5, 'right': -1}[keep_coord]
            # isel from coords[coord] instead of prom, to ensure associated coords are included too,
            #   e.g. t & snap are associated --> this will keep t & snap in the result.
            # if i_keep = 0.5, it is handled by xarray_isel fractional indexing.
            keep = xarray_isel(prom.coords[coord], {coord: i_keep})
            here = arr.assign_coords({coord: keep})
            results.append(here)
    else:
        results = polyfits
    result = xr.concat(results, dim_coarse)
    if keep_coord:
        result = xarray_promote_dim(result, coord)
    return result


### --------------------- curve fit --------------------- ###

_paramdocs_curve_fit = {
    'array': '''xarray.DataArray or Dataset
        data to fit.
        Currently, Dataset allowed only if it has 'mean' and 'std' data_vars, when `stddev=True`,
            in which case will sample the implied gaussians (via np.random.normal),
            N=`werr_samples` times, performing N fits to f,
            reporting the mean and stddev of each fit param across all N fits, and
            ignoring scipy standard deviation info about params from each individual fit.''',
    'werr_samples': '''int
        number of fits to do if `array` is a Dataset with 'mean' and 'std' vars, when `stddev=True`,
            in which case result will tell mean and stddev of each fit param across all N fits,
            and ignore scipy standard deviation info about params from each individual fit.
        (Implemented this because default scipy linear least squares fitting with errorbars
            just weights each point's important by inverse of error bar,
            which highly favors points with small errors.
        That default does NOT correspond to the results of "repeating the experiment" N times,
            where "the experiment" is gathering data then fitting,
            and then asking "what is the mean and stddev of fit params across all N experiments?".
        However, using werr_samples DOES correspond to "repeating the experiment" N times.)''',
    'werr_seed': '''None or any object, default 0
        `np.random.seed(werr_seed)` beforehand, if doing werr_samples (with Dataset `array`).
        Default 0 ensures reproducible results.
        None --> don't call np.random.seed beforehand. Will give different results each time.''',
    'pnames': '''None or list of str
        names of params. If provided, 'param' coord will be assigned these names.''',
    'pbounds': '''None or list of [None, callable, or 2-tuple of value, None, or callable]
        bounds for each parameter. Provide `pbounds` or `bounds`, but not both.
        None --> no bounds provided.
        Each bound can be:
            callable --> call as bound(array, dim) (after doing array.pc.ensure_dims(dim)).
            None --> use (-np.inf, np.inf).
            2-tuple --> (lower, upper).
                callable --> use lower(array, dim) / upper(array, dim)
                None --> use -np.inf / np.inf.''',
    'bounds': '''UNSET or (list of lower bounds, list of upper bounds)
        bounds, formatted as expected by scipy curve_fit.
        Provide `pbounds` or `bounds`, but not both.''',
}



@pcAccessor.register('curve_fit')
@format_docstring(**_paramdocs_ensure_dims, **_paramdocs_curve_fit)
def xarray_curve_fit(array, f, dim, *, stddev=True, werr_samples=1000, werr_seed=0,
                     promote_dims_if_needed=True,
                     pnames=None, pbounds=None, bounds=UNSET, **kw_curve_fit):
    '''scipy.optimize.curve_fit(f, xdata=array[dim], ydata=array).
    Except, iterate over all other dims in array.
        E.g. arr.curve_fit('t', f) for arr with 't' and 'fluid' dims
        --> result reduces 't' dim but retains 'fluid' dim.

    array: {array}
    dim: str
        dim to fit along.
    f: callable like f(x, param1, param2, ...)
        function to fit.
    stddev: bool
        whether to include data_var 'stddev' telling standard deviation of the fit.
    werr_samples: {werr_samples}
    werr_seed: {werr_seed}
    promote_dims_if_needed: {promote_dims_if_needed}
    pnames: {pnames}
    pbounds: {pbounds}
    bounds: {bounds}

    additional kwargs go to scipy.optimize.curve_fit.

    returns xarray.Dataset with data_vars:
        params: iterable along 'param' dimension of the parameters of the fit.
            e.g. call f with f(x, *result['params'].values) if 1D array.
            e.g. f(x, *result['params'].isel(fluid=0).values) if 2D array.
        stddev: standard deviation of each parameter's fit.
    '''
    array_orig = array
    if isinstance(array, xr.Dataset):
        if stddev != True:
            raise InputError('xarray_curve_fit(Dataset), only implemented when stddev=True.')
        if 'mean' not in array or 'std' not in array:
            errmsg = ('xarray_curve_fit(Dataset) only implemented when input has "mean" and "std" data_vars;'
                     f' got data_vars: {list(array.data_vars)}')
            raise InputError(errmsg)
        if werr_seed is not None:
            np.random.seed(werr_seed)
        # sample the implied gaussians N times, then fit each sample.
        mean = array['mean']
        std = array['std']
        samples = np.random.normal(mean, std, size=(werr_samples,) + mean.shape)
        array = xr.DataArray(samples, dims=('__werr_sample__', *mean.dims),
                             coords=mean.coords)
        werrmode = True
        stddev = False  # don't compute the stddevs from scipy for individual fits, below!
    else:
        werrmode = False
    array = xarray_ensure_dims(array, dim, promote_dims_if_needed=promote_dims_if_needed)
    # bounds
    if pbounds is not None and bounds is not UNSET:
        raise InputConflictError('provide pbounds or bounds, but not both.')
    if pbounds is not None:
        bounds = [b(array, dim) if callable(b) else b for b in pbounds]
        bounds = [(-np.inf, np.inf) if b is None else b for b in bounds]
        bounds = [((l(array, dim) if callable(l) else l),
                   (u(array, dim) if callable(u) else u)) for l, u in bounds]
        bounds = [((-np.inf if l is None else l),
                   (np.inf if u is None else u)) for l, u in bounds]
        bounds = tuple(zip(*bounds))
    if bounds is not UNSET:
        kw_curve_fit['bounds'] = bounds
    # back to non-bound-stuff
    other = list(set(array.dims) - {dim})
    sizes = [array.sizes[d] for d in other]
    result = None
    stds = None
    for index in np.ndindex(*sizes):
        sub = array.isel(dict(zip(other, index)))
        x = sub[dim].values
        y = sub.values
        params, cov = scipy_optimize.curve_fit(f, x, y, **kw_curve_fit)
        if result is None:  # first time --> make full result with proper shape
            result = np.empty([*sizes, len(params)], dtype=params.dtype)
        result[index] = params
        if stddev:
            if stds is None:
                stds = np.empty([*sizes, len(params)], dtype=params.dtype)
            stds[index] = np.sqrt(np.diag(cov))
    # bookkeeping & putting it all together
    if werrmode:
        assert other[0] == '__werr_sample__'  # 0'th dim in "other" is the sample dim.
        stds = result.std(axis=0)
        result = result.mean(axis=0)
        stddev = True  # do include these stddevs in the final result, below!
        other = other[1:]
    kw = xarray_copy_kw(array_orig, dims=other)
    kw['dims'] = list(kw['dims']) + ['param']
    if pnames is not None:
        kw['coords'] = {**kw.get('coords', {}), 'param': pnames}
    result = xr.DataArray(result, **kw)
    result = xr.Dataset({'params': result})
    if stddev:
        stds = xr.DataArray(stds, **kw)
        result = result.assign(stddev=stds)
    return result

@pcAccessor.register('curve_eval')
def xarray_curve_eval(params, f, xdata, *, stddev=False):
    '''evaluate a curve fit result (params) for this function at these xdata.
    [EFF] note: well-vectorized f could equivalently do:
        f(xdata, *params.transpose('param', ...))
        and that would probably be much faster, if it is an available option.

    params: xarray.DataArray or xarray.Dataset
        curve_fit result, or result['params']. Must have 'param' dimension.
        if Dataset, will internally use params['params'].
    f: callable like f(x, param1, param2, ...)
        function which was fit / to be evaluated.
    xdata: 1D xarray.DataArray
        x values at which to evaluate the fit.
    stddev: bool
        whether to instead return Dataset with data_vars 'eval+std', 'eval', and 'eval-std',
        telling f(xdata, *(params+std)), f(xdata, *params), and f(xdata, *(params-std)).
        Fails if params is not a Dataset with 'stddev' data_var.
    '''
    if stddev:
        if not isinstance(params, xr.Dataset) or 'stddev' not in params:
            raise InputError('stddev=True but params is not a Dataset with "stddev" data_var.')
        stds = params['stddev']
    if isinstance(params, xr.Dataset):
        params = params['params']
    if not isinstance(xdata, xr.DataArray) or xdata.ndim != 1:
        raise InputError('xdata must be a 1D xarray.DataArray.')
    # misc. bookkeeping:
    other = list(set(params.dims) - {'param'})
    sizes = [params.sizes[d] for d in other]
    kw = xarray_copy_kw(params, dims=other)
    kw['dims'] = list(kw['dims']) + [xdata.dims[0]]
    kw_xdata = xarray_copy_kw(xdata)
    kw['coords'] = {**kw.get('coords', {}), **kw_xdata.get('coords', {})}
    # computing result:
    # [TODO] encapsulate "apply function looping across irrelevant dims" elsewhere...
    if stddev:
        result = np.empty([3, *sizes, len(xdata)], dtype=params.dtype)
        for index in np.ndindex(*sizes):
            ii = dict(zip(other, index))
            params_ii = params.isel(ii)
            stds_ii = stds.isel(ii)
            result[0][index] = f(xdata, *(params_ii+stds_ii).values)
            result[1][index] = f(xdata, *(params_ii).values)
            result[2][index] = f(xdata, *(params_ii-stds_ii).values)
        evaled = {
            'eval+std': xr.DataArray(result[0], **kw),
            'eval':     xr.DataArray(result[1], **kw),
            'eval-std': xr.DataArray(result[2], **kw),
        }
        kw.pop('dims', None)  # Dataset doesn't want you to enter 'dims' explicitly.
        kw.pop('name', None)  # Dataset doesn't want you to enter 'name'.
        result = xr.Dataset(evaled)
    else:
        result = np.empty([*sizes, len(xdata)])
        for index in np.ndindex(*sizes):
            sub = params.isel(dict(zip(other, index)))
            result[index] = f(xdata, *sub.values)
        result = xr.DataArray(result, **kw)
    # bookkeeping & putting it all together
    return result

@format_docstring(**_paramdocs_ensure_dims, **_paramdocs_curve_fit)
class XarrayCurveFitter():
    '''class for helping with curve fitting.
    Not intended for direct use; subclass must define f:
        f: function to fit. callable like f(x, param1, param2, ...)

    (For direct curve fitting from array, with arbitrary function f,
        without implementing subclass, consider array.pc.curve_fit(f, dim) instead.)

    array: {array}
    dim: str
        dim to fit along.
    stddev: bool
        whether to include data_var 'stddev' telling standard deviation of the fit.
        (Internally, stored inside self.kw_curve_fit)
    werr_samples: {werr_samples}
        (Internally, stored inside self.kw_curve_fit)
    werr_seed: {werr_seed}
    promote_dims_if_needed: {promote_dims_if_needed}
    pnames: UNSET or {pnames}
        UNSET --> use cls.pnames (default: None)
    pbounds: UNSET or {pbounds}
        UNSET --> use cls.pbounds (default: None)
    bounds: {bounds}

    additional kwargs go to xarray_curve_fit, then scipy.optimize.curve_fit.
    '''
    pnames = None
    pbounds = None

    def __init__(self, array, dim, *, promote_dims_if_needed=True,
                 pnames=UNSET, pbounds=UNSET, bounds=UNSET, **kw_curve_fit):
        array = xarray_ensure_dims(array, dim, promote_dims_if_needed=promote_dims_if_needed)
        self.array = array
        self.dim = dim
        if pnames is not UNSET: self.pnames = pnames
        if pbounds is not UNSET: self.pbounds = pbounds
        self.bounds = bounds
        self.kw_curve_fit = kw_curve_fit

    def f(self, x, *params):
        '''function to fit. callable like f(x, param1, param2, ...).
        [Not implemented here; subclass should implement]
        '''
        raise NotImplementedError(f'{type(self).__name__}.f')

    fitted = simple_property('_fitted', default=None,
        doc='''result of latest call to self.fit().
        None if never called self.fit(), or if crashed before finishing self.fit().''')

    @property
    def params(self):
        '''alias to self.fitted['params'], the params from latest call to self.fit.
        crash with helpful message if self.fitted doesn't exist.
        '''
        if self.fitted is None:
            raise AttributeError('params not available; call self.fit() first.')
        return self.fitted['params']

    @property
    def xdata(self):
        '''alias to self.array[self.dim]'''
        return self.array[self.dim]

    def fit(self, *, stddev=UNSET):
        '''curve_fit to ydata = self.array, xdata = self.array[self.dim].
        Remembers result in self.fitted. Returns self.fitted.

        stddev: UNSET or bool
            whether to include data_var 'stddev' telling standard deviation of the fit.
            UNSET --> use value from self.kw_curve_fit, else default of xarray_curve_fit.
        '''
        self.fitted = None  # clear old result, if one exists.
        kw = dict(pnames=self.pnames, pbounds=self.pbounds, bounds=self.bounds)
        kw.update(self.kw_curve_fit)
        if stddev is not UNSET: kw['stddev'] = stddev
        result = xarray_curve_fit(self.array, self.f, self.dim, **kw)
        self.fitted = result
        return self.fitted

    def eval(self, xdata=UNSET, params=UNSET, stddev=False):
        '''evaluate curve fit result (params) at these xdata.
        Equivalent: xarray_curve_eval(params, self.f, xdata)

        xdata: UNSET, 1D xarray.DataArray, or other 1D array-like
            x values at which to evaluate the fit.
            UNSET --> use self.xdata.
            non-xarray 1D array-like --> convert to 1D DataArray via xr1d(xdata, self.dim)
        params: UNSET or values of params from a fit.
            UNSET --> use self.fitted
        stddev: bool
            whether to instead return Dataset with data_vars 'eval+std', 'eval', and 'eval-std',
            telling f(xdata, *(params+std)), f(xdata, *params), and f(xdata, *(params-std)).
            Fails if params is not a Dataset with 'stddev' data_var.

        [EFF] note: if self.f is well-vectorized, it is equivalent (when stddev=False) and faster to do:
            self.f(xdata, *params.transpose('param', ...))
        '''
        if xdata is UNSET: xdata = self.xdata
        elif not isinstance(xdata, xr.DataArray):
            xdata = xr1d(xdata, self.dim)
        if params is UNSET: params = self.fitted
        return xarray_curve_eval(params, self.f, xdata, stddev=stddev)

    def __repr__(self):
        contents = []
        if self.array is not None:
            contents.append(f'array=<{type(self.array).__name__} at {hex(id(self.array))}>')
        if self.fitted is not None:
            contents.append(f'fitted=<{type(self.fitted).__name__} at {hex(id(self.fitted))}>')
        return f'{type(self).__name__}({", ".join(contents)})'


@pcAccessor.register('line_fitter')
@format_docstring(**_paramdocs_ensure_dims, **_paramdocs_curve_fit)
class XarrayLineFitter(XarrayCurveFitter):
    '''XarrayCurveFitter with f a line: f(x, slope, intercept) = slope * x + intercept.

    array: {array}
    dim: str
        dim to fit along.
    stddev: bool
        whether to include data_var 'stddev' telling standard deviation of the fit.
        (Internally, stored inside self.kw_curve_fit)
    werr_samples: {werr_samples}
        (Internally, stored inside self.kw_curve_fit)
    werr_seed: {werr_seed}
         (Internally, stored inside self.kw_curve_fit)
    promote_dims_if_needed: {promote_dims_if_needed}
    pnames: UNSET or {pnames}
        UNSET --> use cls.pnames (default: None)
    pbounds: UNSET or {pbounds}
        UNSET --> use cls.pbounds (default: None)
    bounds: {bounds}

    additional kwargs go to xarray_curve_fit, then scipy.optimize.curve_fit.
    '''
    @staticmethod
    def f(x, slope, intercept):
        '''function to fit: just a simple line. f(x, slope, intercept) = slope * x + intercept.'''
        return slope * x + intercept

    pnames = ['slope', 'intercept']


@pcAccessor.register('line_fit', aliases=['linear_fit'])
@format_docstring(**_paramdocs_ensure_dims, **_paramdocs_curve_fit)
def xarray_line_fit(array, dim, *, pnames=UNSET, pbounds=UNSET, **kw_curve_fitter):
    '''returns result of xarray_curve_fit with f a line:
        f(x, slope, intercept) = slope * x + intercept.

    array: {array}
    dim: str
        dim to fit along.
    stddev: bool
        whether to include data_var 'stddev' telling standard deviation of the fit.
    werr_samples: {werr_samples}
    werr_seed: {werr_seed}
    promote_dims_if_needed: {promote_dims_if_needed}
    pnames: UNSET or {pnames}
        UNSET --> use pnames = ['slope', 'intercept']
    pbounds: UNSET or {pbounds}
        UNSET --> use pbounds = None
    bounds: {bounds}

    additional kwargs go to XarrayCurveFitter, then xarray_curve_fit, then scipy.optimize.curve_fit.
    '''
    fitter = XarrayLineFitter(array, dim, pnames=pnames, pbounds=pbounds, **kw_curve_fitter)
    return fitter.fit()
