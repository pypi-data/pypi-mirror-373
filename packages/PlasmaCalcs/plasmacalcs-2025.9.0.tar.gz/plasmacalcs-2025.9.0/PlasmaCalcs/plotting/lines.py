"""
File Purpose: Line: 1D lines; movie of lines for 2D data.
[TODO] why does plt.legend() move around during animation (if loc not specified)?
"""
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .labels import xarray_title_plot_node
from .movies import MoviePlotElement, MoviePlotNode, MovieOrganizerNode
from .plot_settings import PlotSettings
from .plot_tools import (
    set_margins_if_provided, set_lims_if_provided,
    infer_movie_dim, infer_xy_dims, infer_xyt_dims,
    calculate_vlims, calculate_lims_from_margin,
) 
from ..errors import PlottingAmbiguityError, DimensionError
from ..tools import (
    alias, alias_key_of, alias_child, simple_property,
    UNSET,
    pcAccessor, take_along_dimensions, xarray_nondim_coords,
    xarray_object_coords_to_str,
    xarray_as_array, xarray_fill_coords, xarray_ensure_dims,
)
from ..defaults import DEFAULTS


@PlotSettings.format_docstring()
class XarrayLinePlotElement(MoviePlotElement):
    '''plot line of 1D data.
    
    array: xarray.DataArray, probably ndim=1.
        the data to be plotted.
        coords with ndim>0, dtype=object will be converted to strings suitable for ticklabels.
    label: {label}
    '''
    def __init__(self, array, *, ax=None,
                 aspect=None,  # <-- different from PlotSettings default!
                 **kw_super):
        super().__init__(aspect=aspect, **kw_super)
        self._ax_init = ax
        if array.ndim != 1:
            raise DimensionError(f'line expected array.ndim=1, but got ndim={array.ndim}.')
        self.array = xarray_object_coords_to_str(array, maxlen=DEFAULTS.PLOT.XTICKLABEL_MAXLEN, ndim_min=1)
        self.init_line()

    array = alias_key_of('data', 'array', doc='''array for plot. Internally, stored at self.data['array']''')
    line = simple_property('_line', doc='''line plot (instance of matplotlib.lines.Line2D)''')
    ax = alias_child('line', 'axes', if_no_child=None, doc='''the axes containing this line plot''')
    fig = alias_child('ax', 'figure', if_no_child=None, doc='''figure containing this line plot''')

    # # # PLOTTING THIS ELEMENT # # #
    def init_line(self):
        '''initialize the line plot; actually plot the data.
        stores plotted object in self.line and returns self.line.
        '''
        array = self.array
        # plot settings / kwargs / bookkeeping
        kw_plot = self.plot_settings.get_mpl_kwargs('xarray.DataArray.plot.line')
        if 'label' in kw_plot:
            kw_plot['label'] = kw_plot['label'].format(**xarray_nondim_coords(array))
        # make plot
        plotter = array.plot.line
        lines = plotter(ax=self._ax_init, **kw_plot)
        self.line = lines[0]
        if len(lines) > 1:
            raise PlottingAmbiguityError(f'xarray.DataArray.plot.line made {len(lines)} lines, expected 1.')
        # formatting
        aspect = self.plot_settings['aspect']  # xarray plotter doesn't like 'aspect' kwarg; assign here instead.
        if aspect is not None:
            self.ax.set_aspect(aspect)
        set_margins_if_provided(self.plot_settings, ax=self.ax)
        set_lims_if_provided(self.plot_settings, ax=self.ax)
        return self.line

    # # # UPDATING (REQUIRED BY PARENT) # # #
    def update_data(self, data):
        '''update the plot using data['array'].
        return the list of all updated matplotlib Artist objects (i.e., [self.line])
        '''
        array = data['array']
        line = self.line
        linex = line.get_xdata()
        line.set_data(linex, array)
        self.array = array  # <-- bookkeeping
        return [self.line]


@pcAccessor.register('line', totype='array')
@PlotSettings.format_docstring()
class XarrayLine(MoviePlotNode):  # [TODO] refactor PlotDimsMixin to use it here.
    '''MoviePlotNode of line.
    stores an XarrayLinePlotElement & has methods for plotting & updating the plot.
    "line" refers to a matplotlib.lines.Line2D object, e.g. the result of plt.plot.

    array: xarray.DataArray, probably ndim=2.
        the data to be plotted. if ndim=1, can still plot, but nothing to animate.
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
    aspect: {aspect}

    title: {title}
    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}
    '''
    element_cls = XarrayLinePlotElement

    def __init__(self, array, t=None, *, x=None, ax=None,
                 init_plot=PlotSettings.default('init_plot'),  # <- could go in kw_super, but explicit is nice.
                 label=PlotSettings.default('label'),
                 aspect=None,  # <-- different from PlotSettings default!
                 **kw_super):
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
        # super init
        kw_super.update(init_plot=init_plot, label=label, aspect=aspect)
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    t_plot_dim = alias('t')

    ax = alias_child('obj', 'ax', if_special_child={None: None, UNSET: None},
        doc='''mpl.axes.Axes where this XarrayLine is plotted, or None if not plotted.''')

    fig = alias_child('obj', 'fig', if_special_child={None: None, UNSET: None},
        doc='''figure where this XarrayLine is plotted, or None if not plotted.''')

    # # # PLOTTING METHODS (REQUIRED BY PARENT CLASS) # # #
    def init_plot(self):
        '''plot for the first time. Save the ContourPlotElement at self.obj'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs('pc.XarrayLinePlotElement')
        # -- determine ylims (based on the entire array, not just this frame)
        d = kw_plot
        robust = d.get('robust', False)
        ylim = d.pop('ylim', None)
        ymargin = 0 if (ylim is not None) else d.get('ymargin', None)
        ymin, ymax = (None, None) if (ylim is None) else ylim
        ymin, ymax = calculate_vlims(self.array, vmin=ymin, vmax=ymax, robust=robust)
        ymin, ymax = calculate_lims_from_margin(ymin, ymax, margin=ymargin, x='y')
        d['ylim'] = (ymin, ymax)
        # >> actually plot the contour <<
        self.obj = self.element_cls(data['array'], ax=self._ax_init, **kw_plot)
        # -- if add_labels, add title:
        if self.plot_settings['add_labels']:
            self.plot_title()
        # bookkeeping
        self.frame = frame

    # [TODO] encapsulate similarities between this & XarrayImage???
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



### --------------------- MULTIPLE LINES --------------------- ###

@pcAccessor.register('lines')
class XarrayLines(MovieOrganizerNode):
    '''MovieOrganizerNode for organizing multiple XarrayLines.

    array: xarray.DataArray or xarray.Dataset
        the array to plot lines from. Any number of dimensions is allowed.
        if dataset, will be converted to array using to_array(dim='variable').
        Note that dims other than t & x should be "not too long" otherwise plot will have lots of lines.
    dims: None , str, or list of str
        dimensions to iterate over; plot one line per point in these dimensions.
        E.g. dims = ['fluid', 'component'] --> plot one line per fluid-component pair.
        [TODO] improve formatting; currently uses default cycler for line properties,
            but if using multiple dims it would be nicer to have a different cycler for each dim,
            e.g. colors for fluid, linestyles for component.
        None --> infer from array.dims, t, and x.
    t: None or str
        dimension name for the time axis (for movies).
        None --> infer from the array coords. See also: DEFAULTS.PLOT.DIMS_INFER
        If no time dimension (None provided & can't infer), that's okay, but animation will fail.
    x: None or str
        dimension name for the x axis.
        None --> infer from the array coords. See also: DEFAULTS.PLOT.DIMS_INFER
    cstyles: None or dict of {{coordname: dict or list of tuples of (val, dict of kwargs for XarrayLine)}}
        if provided, pass these dicts to individual lines with corresponding scalar val for coord.
        use tuples of values to test equality instead of indexing a dict.
        E.g., styles={{'fluid': [('e', dict(ls='--')), ('H_II', dict(color='blue'))]}}
            would ensure dashed line when arr['fluid']=='e', blue line when arr['fluid']=='H_II',
            and have no effect whenever arr['fluid'] is not scalar, doesn't exist, or isn't 'e' or 'H_II'.
    cstyles_default: bool
        tells how to handle conflict between kwargs from cstyles and kwargs passed directly to self.
        True --> treat cstyles as 'defaults'; kwargs from self override kwargs from cstyles.
        False --> kwargs from cstyles take precedence.

    robust: {robust}
    ymargin: {ymargin}
    add_legend: bool
        whether to plot a legend, by default.
    label: {label}
        UNSET --> 'dim=val' for each line, for each dim in dims, e.g. 'fluid=e-, component=x'
    '''
    def __init__(self, array, dims=None, t=None, *, x=None, ax=None, add_legend=True,
                 label=UNSET, cstyles=None, cstyles_default=False, **kw):
        name = '' if (getattr(array, 'name', None) is None) else array.name
        self._dims_init = dims
        self.cstyles = cstyles
        dims_provided = None if dims is None else [dims] if isinstance(dims, str) else dims
        dims_need = [] if dims_provided is None else dims_provided
        if isinstance(array, xr.Dataset):
            array = xarray_as_array(array)
        array = xarray_fill_coords(array, need=[x, t, *dims_need])
        array = xarray_ensure_dims(array, ({x, t, *dims_need} - {None}), promote_dims_if_needed=True)
        self.array = array
        # infer plot dims & get xarray.DataArray for each line
        x, y, t = infer_xyt_dims(self.array.dims, t=t, x=x, exclude=dims_need,
                                 xy_fail_ok=True, t_fail_ok=True)  # [TODO] improve plot_dims code?
        self.x, self.t = x, t  # <-- bookkeeping, store for convenience.
        if x is None:  # note: it's okay if t is None; that just means "single frame, not a movie".
            errmsg = 'Cannot infer x. Provide additional info (x, t, and/or dims) then try again.'
            raise PlottingAmbiguityError(errmsg)
        if dims is None:
            dims = [dim for dim in self.array.dims if dim not in [t, x]]
        else:
            dims = dims_provided
        # labels (for legend)
        if label is UNSET:
            label = ', '.join(['dim={dim}'.replace('dim', dim) for dim in dims])
            if label=='': label = UNSET
        kw['label'] = label
        # list of xarray DataArrays.
        arrs = take_along_dimensions(self.array, dims, atleast_1d=True)
        self.arrs = arrs
        if arrs.ndim >= 2:
            raise NotImplementedError(f"[TODO] XarrayLines across 2D+ ({dims!r}). Workaround: use different x/t/dims.")
        # handle ylims, taking all arrays into account.
        init_plot_settings = PlotSettings(**kw)
        robust = init_plot_settings.get('robust', last_resort_default=False)
        ylim = init_plot_settings.get('ylim', last_resort_default=None)
        ymargin = 0 if (ylim is not None) else init_plot_settings.get('ymargin', last_resort_default=None)
        ymin, ymax = (None, None) if (ylim is None) else ylim
        ymin, ymax = calculate_vlims(self.array, vmin=ymin, vmax=ymax, robust=robust)
        ymin, ymax = calculate_lims_from_margin(ymin, ymax, margin=ymargin, x='y')
        kw['ylim'] = (ymin, ymax)
        # create array of XarrayLine nodes (but don't init_plot yet!)
        kw_line = kw.copy()
        kw_line['title'] = None  # <-- allow self to determine title, not any of the lines.
        lines = np.full(arrs.shape, None, dtype=object)
        for idx, arr in np.ndenumerate(arrs):
            # cstyle management ([TODO] encapsulate this and put it elsewhere...?)
            cstyle_here = dict()
            if cstyles is not None:
                for cname, csty in cstyles.items():
                    if cname in arr.coords and arr[cname].size==1:
                        if isinstance(csty, dict):
                            cstyle_here.update(csty.get(arr[cname].item(), {}))
                        else:  # csty must be an iterable of 2-tuples
                            for cval, cvalstyle in csty:
                                if arr[cname].item() == cval:
                                    cstyle_here.update(cvalstyle)
            kw_here = {**cstyle_here, **kw_line} if cstyles_default else {**kw_line, **cstyle_here}
            # >> actually make the XarrayLine. Don't plot it yet though. <<
            line = XarrayLine(arr, t=t, x=x, ax=ax, init_plot=False, **kw_here)
            lines[idx] = line
            # never mess with title or labels after the first one.
            kw_line['add_labels'] = False
        self.nodes = lines
        # init super
        super().__init__(name=name, **kw)

        if self.plot_settings['init_plot']:
            self.init_plot()

        self.add_legend = add_legend
        if add_legend:
            self.plot_legend()

    def init_plot(self):
        '''plot for the first time: call init_plot on all nodes, and connect to tree.

        This is fundamentally different from MoviePlotNode.init_plot's usual purpose,
            since this is about calling init_plot on the nodes, not on self.obj.
            [TODO] should this function be renamed, for clarity?
        '''
        # checks: skip the usual checks; init_plot on nodes, not self.obj.
        # but, do check if self.init_plot was already called; don't want to call it twice!
        if getattr(self, '_called_init_plot', False):
            errmsg = (f'init_plot was already called; cannot call it again. '
                      f'For {type(self).__name__}(name={self.name!r}) with id={hex(id(self))}')
            raise PlottingAmbiguityError(errmsg)
        for i, line in np.ndenumerate(self.nodes):
            line.init_plot()
            line.parent = self
        # -- if add_labels, add title:
        if self.plot_settings['add_labels']:
            self.plot_title()
        self._called_init_plot = True

    # # # PROPERTIES # # #
    lines = alias('nodes')
    line0 = property(lambda self: self.lines[0], doc='''first line; lines[0].''')
    ax = alias_child('line0', 'ax', doc='''mpl.axes.Axes where the lines are plotted.''')
    fig = alias_child('line0', 'fig', doc='''figure where the lines are plotted.''')

    # # # LEGEND # # #
    def plot_legend(self):
        '''plot a legend! Plots to the right of the axes.
        For more precise control of legend,
            use add_legend=False during self.__init__,
            and just call plt.legend() separately...

        Also fig.set_layout_engine('tight') if layout engine was None;
            otherwise the legend might get cut off at the edges.
        '''
        if self.fig.get_layout_engine() is None:
            self.fig.set_layout_engine('tight')
        self.ax.legend(loc='upper left', bbox_to_anchor=(1.02, 0.95))

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
            title_node = xarray_title_plot_node(self.array, title, t=self.t,
                                                ax=self.ax, parent=self, **kw_title)
            self.title_node = title_node  # <-- for bookkeeping/debugging
