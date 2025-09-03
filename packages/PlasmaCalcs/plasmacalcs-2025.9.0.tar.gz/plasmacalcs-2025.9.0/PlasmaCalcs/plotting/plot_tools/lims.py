"""
File purpose: plot limits, e.g. vlims, xlim, ylim.
"""
import matplotlib.pyplot as plt
import numpy as np

from ..plot_settings import PlotSettings
from ...errors import InputConflictError, InputMissingError, InputError
from ...tools import (
    finite_min, finite_max, finite_percentile,
)

_paramdocs_lims = {
    'skipna': '''bool
        whether to return None instead of nan if min or max would be nan.''',
    'plot_settings': '''None or PlotSettings instance
        if margin is None, get from plot_settings (or matplotlib defaults if None in plot_settings)''',
    'data_interval': '''None or [min, max]
        if provided, use this instead of the actual range of data from the plot.''',
    'scale': '''None, 'linear', or 'log'
        whether margin is in linear or log space. If None, use ax's current scale.''',
}

### --------------------- COMPUTE LIMS --------------------- ###

@PlotSettings.format_docstring()
def calculate_vlims(values, *, vmin=None, vmax=None, robust=False, to_dict=False, expand_flat=True):
    '''return the calculated vmin, vmax, for all of these values.

    values: array-like or list of array-like objects
        the values to use for calculating the vlims.
        if list of array-like objects, the array-like objects may be of different shapes.
    vmin, vmax: None or value
        if provided, use this value for vmin, vmax. Otherwise, calculate it.
    robust: {robust}
    to_dict: bool
        if True, return dict(vmin=vmin, vmax=vmax) instead of (vmin, vmax)

    expand_flat: bool
        if True, and computed vmin > vmax, and provided vmin or vmax but not both,
        then adjust the not-provided value such that vmin > vmax. I.e.:
            provided vmin --> use vmax = vmin + 0.05.  (this matches matplotlib default when vmin=vmax)
            provided vmax --> use vmin = vmax - 0.05.  (this matches matplotlib default when vmin=vmax)
    '''
    if robust is True:
        robust = PlotSettings.get_default('robust')  # get robust percentile.
    provided = dict(vmin=vmin, vmax=vmax)
    if vmin is None:
        if robust:
            if getattr(values, 'dtype', None) == bool:
                vmin = 0  # booleans have no percentiles; vmin=0 always.
            else:
                vmin = finite_percentile(values, robust)
        else:
            vmin = finite_min(values)
    if vmax is None:
        if robust:
            if getattr(values, 'dtype', None) == bool:
                vmax = 1  # booleans have no percentiles; vmax=1 always.
            else:
                vmax = finite_percentile(values, 100 - robust)
        else:
            vmax = finite_max(values)
    if expand_flat and vmin > vmax:
        if provided['vmin'] is not None:
            vmax = vmin + 0.05
        elif provided['vmax'] is not None:
            vmin = vmax - 0.05
    return dict(vmin=vmin, vmax=vmax) if to_dict else (vmin, vmax)

@PlotSettings.format_docstring(sub_ntab=1)
def update_vlims(values, d, *, in_place=False):
    '''calculate vmin, vmax of values, and return copy of d updated appropriately.
    values: array-like or list of array-like objects
        the values to use for calculating the vlims.
        if list of array-like objects, the array-like objects may be of different shapes.
    d: dict which may have keys 'vmin', 'vmax', and/or 'robust', indicating:
        vmin, vmax: None or value
            if provided, use this value for vmin, vmax. Otherwise, calculate it.
        robust: {robust}
        
        Note: the 'robust' key will be popped from the result.
    in_place: bool, default False
        whether to perform the operation in place. True --> edit d directly.
    '''
    if not in_place:
        d = d.copy()
    robust = d.pop('robust', False)
    vmin = d.pop('vmin', None)
    vmax = d.pop('vmax', None)
    vmin, vmax = calculate_vlims(values, vmin=vmin, vmax=vmax, robust=robust)
    d['vmin'] = vmin
    d['vmax'] = vmax
    return d

@PlotSettings.format_docstring(**_paramdocs_lims)
def calculate_lims_from_margin(min, max, margin=None, *, x=None, skipna=False, scale=None):
    '''calculate the lims to use, based on min, max, and margin.
    Return (min, max) after scaling them by this margin.

    min, max: None or number
        None --> return (None, None). (in this case, provided min and max must both be None.)
        number --> treat this as the before-applying-margin limits (in data-coordinates).
    margin: {margin}
    x: None, 'x', or 'y'
        must be provided if `margin` is not; tells which matplotlib default to use.
        ignored if `margin` is provided.
    skipna: {skipna}
    scale: {scale}
        (Actually, if None then default to 'linear' scale, in this function.)
    '''
    if min is None and max is None:
        return (None, None)
    elif min is None or max is None:
        errmsg = f'expected min and max to both be None or both be non-None, but got min={min!r}, max={max!r}.'
        raise InputConflictError(errmsg)
    # else, min and max are both non-None
    # bookkeeping
    if margin is None:
        margin = _get_margin_default(x=x)
    if scale is None:
        scale = 'linear'
    if scale not in ('linear', 'log'):
        raise InputError(f'expected scale to be None, "linear", or "log", but got scale={scale!r}.')
    if scale == 'log':
        min = np.log10(min)
        max = np.log10(max)
    # >> apply margin <<
    range_ = max - min
    max_result = max + range_ * margin
    min_result = min - range_ * margin
    # bookkeeping
    if skipna:
        if np.isnan(min_result): min_result = None
        if np.isnan(max_result): max_result = None
    if scale == 'log':
        min_result = 10 ** min_result
        max_result = 10 ** max_result
    return (min_result, max_result)

def _get_margin_default(*, margin=None, x=None, plot_settings=None):
    '''return the margin to use, based on margin and plot_settings.
    margin: None or number
        the margin to use. returned immediately if not None.
        if necessary, get it from matplotlib defaults, or from plot_settings if possible.
        raise InputError if failed to get margin.
    x: None, 'x', or 'y'
        get '{x}margin' from plot_settings. ('margin' if x is None)
        Or, from matplotlib defaults.
    plot_settings: None or PlotSettings
        get margin from plot_settings if provided, and margin is None.
        if plot_settings.get(f'{x}margin' is None, also try getting plot_settings.get('margin').
            if that is also None, get from matplotlib defaults.
    '''
    if margin is not None:
        return margin
    if plot_settings is not None:
        if x is None:
            margin = plot_settings.get('margin')
            if margin is None:
                raise InputMissingError('must provide "x", "margin", or non-None "margin" in plot_settings.')
        else:
            margin = plot_settings.get(f'{x}margin')
            if margin is None:
                margin = plot_settings.get('margin')
        if margin is not None:
            return margin
    # if reached this line, get from matplotlib defaults.
    if x is None:
        raise InputMissingError('must provide x or margin.')
    if x != 'x' and x != 'y':
        raise InputError(f'expected x to be None, "x", or "y", but got x={x!r}.')
    return plt.rcParams[f'axes.{x}margin']

def get_data_interval(x, ax=None):
    '''return the minimum interval containing all data on the plot axes.
    Returned as [min, max] regardless of axis orientation.

    x: 'x' or 'y'
        str telling the axis to get the data interval for.
    ax: None or matplotlib axis object
        the Axes to get the data interval from. None --> ax=plt.gca().
        will use ax.xaxis or ax.yaxis, depending on `x`.
    '''
    if x == 'x':
        axis = 'xaxis'
    elif x == 'y':
        axis = 'yaxis'
    else:
        raise InputError(f'expected x to be "x" or "y", but got x={x!r}.')
    if ax is None:
        ax = plt.gca()
    axis = getattr(ax, axis)
    return axis.get_data_interval()

def _get_scale_default(*, scale, x, ax=None):
    '''returns the scale to use, based on scale, x, and ax.'''
    if scale is not None:
        return scale
    if ax is None:
        ax = plt.gca()
    if x == 'x':
        scale = ax.get_xscale()
    elif x == 'y':
        scale = ax.get_yscale()
    else:
        raise InputError(f'expected x to be "x" or "y", but got x={x!r}.')
    return scale

@PlotSettings.format_docstring(**_paramdocs_lims)
def get_lims_with_margin(margin=None, *, x, ax=None, plot_settings=None,
                         data_interval=None, skipna=False, scale=None):
    '''returns lims to use for axis x, based on margin and the current data interval.

    margin: {margin}
    x: 'x' or 'y'
        str telling the axis to get the data interval for.
    ax: None or matplotlib axis object
        the Axes to get the data interval from. None --> ax=plt.gca().
        will use ax.xaxis or ax.yaxis, depending on `x`.
    plot_settings: {plot_settings}
    data_interval: {data_interval}
    skipna: {skipna}
    scale: {scale}
    '''
    if data_interval is None:
        data_min, data_max = get_data_interval(x, ax=ax)
    else:
        data_min, data_max = data_interval
    margin = _get_margin_default(margin=margin, x=x, plot_settings=plot_settings)
    scale = _get_scale_default(scale=scale, x=x, ax=ax)
    return calculate_lims_from_margin(data_min, data_max, margin=margin, skipna=skipna, scale=scale)


### --------------------- SET LIMS --------------------- ###

@PlotSettings.format_docstring(**_paramdocs_lims)
def plt_zoom(x='both', margin=None, *, ax=None, plot_settings=None,
             data_interval=None, skipna=True, scale=None):
    '''zoom in/out to view the data with the specified margin.
    Default is to zoom both axes such that all data is viewable, with a small margin.

    x: 'both', 'x', or 'y'
        axis for which to set the margin.
        if None, set margin for xaxis and yaxis.
    margin: {margin}
    ax: None or matplotlib axis object
        the Axes on which to set the margin(s). None --> ax=plt.gca().
    plot_settings: {plot_settings}
    data_interval: {data_interval}
    skipna: {skipna}
    scale: {scale}

    returns the new plt.xlim() or plt.ylim().
    If x is None, returns (plt.xlim(), plt.ylim()) instead.
    '''
    _x_input = x  # save original x to help with debugging.
    if ax is None:
        ax = plt.gca()
    xvals = ['x', 'y'] if x=='both' else [x]
    result = []
    for x in xvals:
        lims = get_lims_with_margin(margin=margin, x=x, ax=ax, plot_settings=plot_settings,
                                    data_interval=data_interval, skipna=skipna, scale=scale)
        if x == 'x':
            result.append(ax.set_xlim(lims))
        elif x == 'y':
            result.append(ax.set_ylim(lims))
        else:
            raise InputError(f'expected x to be None, "x", or "y", but got x={x!r}.')
    return result[0] if len(xvals)==1 else result

@PlotSettings.format_docstring(**_paramdocs_lims)
def plt_zoomx(margin=None, *, ax=None, plot_settings=None,
              data_interval=None, skipna=True, scale=None, **kw_set_margin):
    '''zoom in/out along the x axis. Equivalent: plt_zoom(x='x', ...)

    margin: {margin}
    ax: None or matplotlib axis object
        the Axes on which to set the margin. None --> ax=plt.gca().
    plot_settings: {plot_settings}
    data_interval: {data_interval}
    skipna: {skipna}
    scale: {scale}

    returns the new plt.xlim()
    '''
    return plt_zoom(x='x', margin=margin, ax=ax, plot_settings=plot_settings,
                    data_interval=data_interval, skipna=skipna, scale=scale)

@PlotSettings.format_docstring(**_paramdocs_lims)
def plt_zoomy(margin=None, *, ax=None, plot_settings=None,
              data_interval=None, skipna=True, scale=None, **kw_set_margin):
    '''zoom in/out along the y axis. Equivalent: plt_zoom(x='y', ...)

    margin: {margin}
    ax: None or matplotlib axis object
        the Axes on which to set the margin. None --> ax=plt.gca().
    plot_settings: {plot_settings}
    data_interval: {data_interval}
    skipna: {skipna}
    scale: {scale}

    returns the new plt.ylim()
    '''
    return plt_zoom(x='y', margin=margin, ax=ax, plot_settings=plot_settings,
                    data_interval=data_interval, skipna=skipna, scale=scale)


### --------------------- SET LIMS (FROM PLOT SETTINGS) --------------------- ###

def set_margins_if_provided(plot_settings, *, ax=None):
    '''sets the margins for a plot, if they are non-None in plot_settings.
    see also: plt_set_margin.

    ax: None or matplotlib axis object
        the Axes on which to set the margin. None --> ax=plt.gca().
    '''
    margin = plot_settings.get('margin', default=None)
    for x in ('x', 'y'):
        xmargin = plot_settings.get(f'{x}margin', default=margin)
        if xmargin is not None:
            plt_zoom(x=x, margin=xmargin, ax=ax)

def set_lims_if_provided(plot_settings, *, ax=None):
    '''sets plt.xlim and/or plt.ylim, if they are non-None in plot_settings.

    ax: None or matplotlib axis object
        the Axes on which to set the lims. None --> ax=plt.gca().

    returns (bool, bool) indicating whether xlim, ylim were set.
    '''
    xlim = plot_settings.get('xlim', default=None)
    ylim = plot_settings.get('ylim', default=None)
    set_x = xlim is not None
    set_y = ylim is not None
    if set_x: ax.set_xlim(xlim)
    if set_y: ax.set_ylim(ylim)
    return (set_x, set_y)
