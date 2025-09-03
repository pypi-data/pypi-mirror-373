"""
File Purpose: tools related to scatter plots (possibly animated)
"""

import matplotlib.lines as mpl_lines
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .labels import xarray_title_plot_node
from .movies import MoviePlotElement, MoviePlotNode
from .plot_settings import PlotSettings
from .plot_tools import (
    set_margins_if_provided, set_lims_if_provided,
    infer_movie_dim, infer_xy_dims,
) 
from ..defaults import DEFAULTS
from ..errors import (
    InputError, InputConflictError,
    PlottingAmbiguityError,
)
from ..tools import (
    alias, alias_key_of, alias_child, simple_property,
    UNSET,
    pcAccessor,
    xarray_fill_coords, xarray_ensure_dims,
    xarray_nondim_coords, xarray_dims_coords,
)


### --------------------- ScatterPlotElement & XarrayScatter --------------------- ###

@PlotSettings.format_docstring()
class ScatterPlotElement(MoviePlotElement):
    '''scatter plot.

    array: xarray.DataArray, probably ndim=1.
        the data to be plotted.
        if ndim != 1, must provide `x`; all other dims will be stacked.
    x: None or str
        the coordinate to use for x-axis values.
        None --> if array ndim==1, use the (first 1D) coord associated with the 1 dim,
            (or just use the dim itself, if no such associated coord).
            if array ndim!=1, crash with PlottingAmbiguityError.

    aliases, provide at most one of each pair:
        s, markersize: `s` from plt.scatter. size of markers.
        facecolors, facecolor: `facecolors` from plt.scatter. Color of marker faces in plot.
        edgecolors, edgecolor: `edgecolors` from plt.scatter. Color of marker edges in plot.
        linewidths, linewidth: `linewidths` from plt.scatter. Width of marker edges in plot.

    label: {label}
    {kw_ax_margin}
    '''
    def __init__(self, array, x=None, *, ax=None,
                 s=UNSET, markersize=UNSET,
                 facecolors=UNSET, facecolor=UNSET,
                 edgecolors=UNSET, edgecolor=UNSET,
                 linewidths=UNSET, linewidth=UNSET,
                 **kw_super):
        self._update_kw_from_aliases(kw_super, 's', s=s, markersize=markersize)
        self._update_kw_from_aliases(kw_super, 'facecolors', facecolors=facecolors, facecolor=facecolor)
        self._update_kw_from_aliases(kw_super, 'edgecolors', edgecolors=edgecolors, edgecolor=edgecolor)
        self._update_kw_from_aliases(kw_super, 'linewidths', linewidths=linewidths, linewidth=linewidth)
        super().__init__(**kw_super)
        self._ax_init = ax
        self._x_init = x  # <-- might help with debugging at some point
        self.x = self._infer_x(x, array)
        self.array = self._ensure_x_dim_in_array(array)
        self.init_scatter()

    array = alias_key_of('data', 'array', doc='''array for plot. Internally, stored at self.data['array']''')
    scatter = simple_property('_scatter', doc='''scatter plot object (matplotlib.collections.PathCollection)''')
    ax = alias_child('scatter', 'axes', if_no_child=None, doc='''the axes containing this scatter plot''')
    fig = alias_child('ax', 'figure', if_no_child=None, doc='''the figure containing this scatter plot''')

    def _update_kw_from_aliases(self, kw, key, **aliases):
        '''update kw[key] = value implied from aliases.
        if multiple aliases' values are not UNSET, raise InputConflictError.
        if all aliases' values are UNSET, do not update kw[key].
        returns the updated value, or UNSET of no update was made.
        '''
        exists = [k for k, v in aliases.items() if v is not UNSET]
        if len(exists) == 0:
            return UNSET
        elif len(exists) == 1:
            val = aliases[exists[0]]
            kw[key] = val
            return val
        else:  # len(exists) >= 2
            raise InputConflictError(f'Cannot provide multiple values for {key!r}: {exists}')

    def _infer_x(self, x, array):
        '''set self.x and self.array. See help(type(self)) for more details.'''
        if x is None:
            if array.ndim == 1:
                dim_x = array.dims[0]
                dims_coords = xarray_dims_coords(array, include_dims_as_coords=False)
                for x_opt in dims_coords[dim_x]:
                    if array[x_opt].ndim == 1:
                        x = x_opt
                        break
                else:  # didn't break, no decent coord option found
                    x = dim_x
            else:
                raise PlottingAmbiguityError(f"array.ndim={array.ndim} but x=None. Cannot infer x.")
        else:
            if x not in array.coords:
                raise InputError(f"x={x!r} not in array.coords={set(array.coords)}")
        return x

    def _ensure_x_dim_in_array(self, array):
        '''Return array if self.x already a dim, else array.expand_dims(self.x)'''
        if self.x in array.dims:
            return array
        else:
            return array.expand_dims(self.x)

    # # # PLOTTING THIS ELEMENT # # #
    def init_scatter(self):
        '''initialize the scatter plot; actually plot the data (probably).
        stores plotted object in self.scatter and returns self.scatter.

        if the array is all nan, plot nothing and return None.
        otherwise, set self._plotted_at_least_once = True.
        '''
        array = self.array
        # plot settings / kwargs / bookkeeping
        kw_plot = self.plot_settings.get_mpl_kwargs('xarray.DataArray.plot.scatter')
        if 'label' in kw_plot:
            kw_plot['label'] = kw_plot['label'].format(**xarray_nondim_coords(array))
        # make plot
        if array.isnull().all():
            self._plotted_at_least_once = False
            return None
        else:
            self.scatter = array.plot.scatter(ax=self._ax_init, x=self.x, **kw_plot)
            self._plotted_at_least_once = True
            # formatting
            set_margins_if_provided(self.plot_settings, ax=self.ax)
            set_lims_if_provided(self.plot_settings, ax=self.ax)
            return self.scatter

    # # # UPDATING (REQUIRED BY PARENT) # # #
    def update_data(self, data):
        '''update the plot using data['array'].
        return the list of all updated matplotlib Artist objects;
            Probably [self.scatter], but might be empty list (if array is all nan).
        (if self.init_scatter() didn't make a plot due to all nan initial values, use that instead.)
        '''
        # [TODO][EFF] if same number of points, update existing points instead of making new ones.
        array = data['array']
        array = self._ensure_x_dim_in_array(array)
        if not getattr(self, '_plotted_at_least_once', False):
            # if never plotted anything yet due to all nans, try init_scatter() instead
            self.array = array
            result = self.init_scatter()
            return [] if result is None else [result]
        # remove existing scatter (if any). Remember some old values first.
        ax_old, kw_old = self._remember_then_remove_old()
        # plot new scatter
        if array.isnull().all():
            return []
        else:
            kw_plot = self.plot_settings.get_mpl_kwargs('xarray.DataArray.plot.scatter')
            kw_plot.update(add_labels=False)  # no adjusting existing labels here.
            kw_plot.update(kw_old)
            self.scatter = array.plot.scatter(ax=ax_old, x=self.x, **kw_plot)
            return [self.scatter]

    def _remember_then_remove_old(self):
        '''remember any relevant details from the old scatter plot (before removing it).
        saves self._ax_old and self._kw_old, then does old.remove(), where old=self.scatter.
        If self.scatter doesn't exist, return the saved _ax_old and _kw_old.

        returns (self._ax_old, self._kw_old)
        '''
        old = getattr(self, 'scatter', None)
        if old is None:
            assert hasattr(self, '_ax_old'), "ScatterPlotElement.update_data called before init_scatter?"
            assert hasattr(self, '_kw_old'), "ScatterPlotElement.update_data called before init_scatter?"
        else:
            self._ax_old = self.ax
            kw_old = {}
            if 'c' not in self.plot_settings:
                # if all points same color, keep it; don't use ax color_cycler.
                old_colors = old.get_facecolors()
                if len(old_colors)>0 and np.all(old_colors == old_colors[0]):
                    kw_old.update(color=old_colors[0])
            old.remove()
            del self.scatter
            self._kw_old = kw_old
        return (self._ax_old, self._kw_old)

    # # # CONENIENCE # # #
    def legend_handle(self, *, label=UNSET):
        '''returns a matplotlib.lines.Line2D suitable for use as a handle in a legend.
        Caution: not yet compatible with scatter plots with varying marker colors / sizes.
        
        label: UNSET or str
            if not UNSET, use this as the label, instead of self.plot_settings['label']

        Example:
            handle1 = self.legend_handle()
            handle2 = other_scatter_plot.legend_handle()
            plt.legend(handles=[handle1, handle2])

        One reason to consider using this is that self might plot 0 points on an axis sometimes,
            so if creating the legend "automatically" instead, then it wouldn't show up.
        '''
        kw = self.plot_settings.get_mpl_kwargs('mpl.lines.Line2D', label=label)
        # some aliases (because matplotlib is annoyingly inconsistent...):
        kw_scatter = self.plot_settings.get_mpl_kwargs('xarray.DataArray.plot.scatter')
        if 'linewidths' in kw_scatter:
            kw['markeredgewidth'] = kw_scatter['linewidths']
        if 's' in kw_scatter:
            # Line2D markersize actually means sqrt(s)...
            kw['markersize'] = np.sqrt(kw_scatter['s'])
        # color-related aliases (need to check if marker is filled...):
        marker = kw.get('marker', plt.rcParams['scatter.marker'])
        if marker in mpl_lines.Line2D.filled_markers:
            # facecolor means facecolor. (nice.)
            # edgecolor means edgecolor. (also nice.)
            if 'facecolors' in kw_scatter:
                kw['markerfacecolor'] = kw_scatter['facecolors']
            if 'edgecolors' in kw_scatter:
                kw['markeredgecolor'] = kw_scatter['edgecolors']
        else:
            # facecolor means edgecolor. (ew.)
            # edgecolor gets ignored entirely. (ewww.)
            if 'facecolors' in kw_scatter:
                kw['markeredgecolor'] = kw_scatter['facecolors']
            if 'edgecolors' in kw_scatter:
                pass  # don't do anything, matplotlib doesn't want to know about it.
        # always overwrite:
        kw['linestyle'] = ''  # no line
        return mpl_lines.Line2D([], [], **kw)


@pcAccessor.register('scatter')
@PlotSettings.format_docstring()
class XarrayScatter(MoviePlotNode):  # [TODO] refactor PlotDimsMixin to use it here.
    '''MoviePlotNode of scatter.
    stores a ScatterPlotElement & has methods for plotting & updating the plot.
    "scatter" refers to a matplotlib.collections.PathCollection object, e.g. the result of plt.scatter.

    array: xarray.DataArray, probably ndim=2.
        the data to be plotted. if ndim=1, can still plot, but nothing to animate.
        For ndim >= 3, consider manually iterating over the 3rd+ dim(s),
            putting multing scatter plots onto the same axes,
            making a movie=MovieOrganizerNode() and doing movie.add_child(s) for each plot.
            [TODO] add a class (or just a function?) to handle this sort of thing automatically.
    t: None or str
        the array dimension which frames will index. E.g. 'time'.
        None -> infer from array & any other provided dimensions.
    x: None or str
        if provided, tells dimensions for the x plot axes.
        None -> infer from array & any other provided dimensions.
    ax: None or Axes
        the attached mpl.axes.Axes object.
        None --> will use self.ax=plt.gca() when getting self.ax for the first time.

    init_plot: {init_plot}
    label: {label}

    {kw_ax_margin}

    title: {title}
    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}
    '''
    element_cls = ScatterPlotElement

    def __init__(self, array, t=None, *, x=None, ax=None,
                 init_plot=PlotSettings.default('init_plot'),  # <- could go in kw_super, but explicit is nice.
                 label=PlotSettings.default('label'),
                 **kw_super):
        if isinstance(array, xr.Dataset):
            array = xarray_as_array(array)
        array = xarray_fill_coords(array, need=[x, t])
        array = xarray_ensure_dims(array, ({x, t} - {None}), promote_dims_if_needed=True)
        self.array = array
        self._ax_init = ax
        # infer dims ([TODO]: refactor plot dims code & offload this logic to PlotDimsMixin.)
        if array.ndim != 1:
            t = infer_movie_dim(array.dims, t, fail_ok=True)
        if (array.ndim != 1) and (t is None):
            errmsg = 't=None but is required (when array.ndim != 2). But cannot infer t from data provided.'
            raise PlottingAmbiguityError(errmsg)
        if x is None:
            x = infer_xy_dims(array.dims, x=x, y=None, exclude=[t], fail_ok=True)[0]
        if x is None:
            errmsg = 'x=None but is required. But cannot infer x from data provided.'
            raise PlottingAmbiguityError(errmsg)
        self.t = t
        self.x = x
        kw_super.update(init_plot=init_plot, label=label)
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    t_plot_dim = alias('t')

    ax = alias_child('obj', 'ax', if_special_child={None: None, UNSET: None},
        doc='''mpl.axes.Axes where this XarrayScatter is plotted, or None if not plotted.''')

    fig = alias_child('obj', 'fig', if_special_child={None: None, UNSET: None},
        doc='''figure where this XarrayScatter is plotted, or None if not plotted.''')

    scatter = alias_child('obj', 'scatter', if_special_child={None: None, UNSET: None},
        doc='''mpl.collections.PathCollection object of this XarrayScatter, or None if not plotted.''')

    legend_handle = alias_child('obj', 'legend_handle',
        doc='''alias to self.obj.legend_handle;
        method which returns a Line2D object suitable for use as a handle in a legend.
        (implied handles are sometimes okay, but this is useful in case self is sometimes all-nan.)''')

    # # # PLOTTING METHODS (REQUIRED BY PARENT CLASS) # # #
    def init_plot(self):
        '''plot for the first time. Save the ScatterPlotElement at self.obj'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs(f'pc.ScatterPlotElement')
        # -- determine ylims (based on the entire array, not just this frame)
        # DISABLED. Usually I scatter on top of existing plots, and don't want scatter to touch ylim.
        #   Workaround: use XarrayLine() instead. [TODO] optionally enable?
        # d = kw_plot
        # robust = d.get('robust', False)
        # ylim = d.pop('ylim', None)
        # ymin, ymax = (None, None) if (ylim is None) else ylim
        # ymin, ymax = calculate_vlims(self.array, vmin=ymin, vmax=ymax, robust=robust)
        # d['ylim'] = (ymin, ymax)
        # >> actually plot the scatter <<
        self.obj = self.element_cls(data['array'], ax=self._ax_init, x=self.x, **kw_plot)
        # -- if add_labels, add title:
        if self.plot_settings['add_labels']:
            self.plot_title()
        # bookkeeping
        self.frame = frame

    def get_data_at_frame(self, frame):
        '''returns {'array': array at this frame}, properly transposed & ready for plotting.'''
        t = self.t_plot_dim
        result = self.array
        if t is not None:  # there is a dimension for the time axis.
            result = result.isel({t: frame})
        return {'array': result}

    def get_nframes_here(self):
        '''return the number of frames that could be in the movie, based on this node.'''
        t = self.t_plot_dim
        if t is None:
            return 0
        return len(self.array.coords[t])

    # # # TITLE # # #
    def plot_title(self):
        '''adds title (as a MovieTextNode) on self.ax.
        raise PlottingAmbiguityError if title already plotted
            (this prevents having multiple title nodes).
        '''
        if hasattr(self, 'title_node'):
            raise PlottingAmbiguityError(f'{type(self).__name__} title was already plotted!')
        title = self.plot_settings['title']
        if title is None:
            plt.title('')  # remove xarray's default title.
        else:
            kw_title = {**self.plot_settings.kw, 'init_plot': True}
            title_node = xarray_title_plot_node(self.array, title, t=self.t_plot_dim,
                                                ax=self.ax, parent=self, **kw_title)
            self.title_node = title_node  # <-- for bookkeeping/debugging


### --------------------- scatter-related methods --------------------- ###

@pcAccessor.register('scatter_max')
def xarray_scatter_max(array, x, y, *, t=None, **kw_scatter):
    '''use XarrayScatter to plt.scatter() a single marker, at the argmax of array.
    default style: {**DEFAULTS.PLOT.SCATTER_STYLE, **DEFAULTS.PLOT.SCATTER_MAX}

    array: xarray.DataArray
        array whose max will be marked.
    x: str
        coordinate to use for x-axis values.
    y: str
        coordinate to use for y-axis values.
    t: None or str
        coordinate to use for "time" (iterate across movie frames).
        None --> probably can't animate; might show all points in 1 frame.

    [TODO] optionally infer x, y, t automatically if not provided directly.

    additional kwargs go to XarrayScatter
    returns XarrayScatter object.
    '''
    xdim = x
    ydim = y
    argmax = array.argmax((xdim, ydim))
    x = array[xdim].isel({xdim: argmax[xdim]})
    y = array[ydim].isel({ydim: argmax[ydim]})
    kw = {**DEFAULTS.PLOT.SCATTER_STYLE,
          **DEFAULTS.PLOT.SCATTER_MAX,
          **kw_scatter}
    scatarr = y.assign_coords({xdim: x})
    return XarrayScatter(scatarr, x=xdim, t=t, **kw)

@pcAccessor.register('scatter_min')
def xarray_scatter_min(array, x, y, *, t=None, **kw_scatter):
    '''use XarrayScatter to plt.scatter() a single marker, at the argmin of array.
    default style: {**DEFAULTS.PLOT.SCATTER_STYLE, **DEFAULTS.PLOT.SCATTER_MIN}

    array: xarray.DataArray
        array whose min will be marked.
    x: str
        coordinate to use for x-axis values.
    y: str
        coordinate to use for y-axis values.
    t: None or str
        coordinate to use for "time" (iterate across movie frames).
        None --> probably can't animate; might show all points in 1 frame.

    [TODO] optionally infer x, y, t automatically if not provided directly.

    additional kwargs go to XarrayScatter
    returns XarrayScatter object.
    '''
    xdim = x
    ydim = y
    argmin = array.argmin((xdim, ydim))
    x = array[xdim].isel({xdim: argmin[xdim]})
    y = array[ydim].isel({ydim: argmin[ydim]})
    kw = {**DEFAULTS.PLOT.SCATTER_STYLE,
          **DEFAULTS.PLOT.SCATTER_MIN,
          **kw_scatter}
    scatarr = y.assign_coords({xdim: x})
    return XarrayScatter(scatarr, x=xdim, t=t, **kw)

@pcAccessor.register('scatter_where')
def xarray_scatter_where(arr, condition=None, *, x, y, t=None, **kw_scatter):
    '''use XarrayScatter to plt.scatter() markers wherever arr==True.
    Roughly equivalent: arr[y].where(arr).pc.scatter(x=x, t=t, **kw_scatter)

    arr: xarray.DataArray
        array of bools, or array to be provided to condition if condition is callable.
    condition: None, array of bools, or callable
        None --> use condition = `arr`, and `arr` must be array of bools.
        array --> ignore arr entirely. `condition` must be array of bools.
        callable --> use condition = condition(`arr`), which must return array of bools.
    x: str
        coordinate to use for x-axis values.
    y: str
        coordinate to use for y-axis values.
    t: None or str
        coordinate to use for "time" (iterate across movie frames).
        None --> probably can't animate; might show all points in 1 frame.

    [TODO] optionally infer x, y, t automatically if not provided directly.

    additional kwargs go to XarrayScatter
    returns XarrayScatter object.
    '''
    if condition is None:
        where = arr
    elif callable(condition):
        where = condition(arr)
    else:
        where = condition
    where = xarray_ensure_dims(where, ({x, y, t} - {None}), promote_dims_if_needed=True)
    scatarr = where[y].where(where)
    return XarrayScatter(scatarr, x=x, t=t, **kw_scatter)
