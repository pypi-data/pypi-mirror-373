"""
File Purpose: Contour: 2D contours; movie of contours for 3D data.
"""
import matplotlib.pyplot as plt
#import matplotlib.ticker as mpl_ticker  # [TODO] use this for good default levels.
import matplotlib.lines as mpl_lines
import numpy as np
import xarray as xr

from .labels import xarray_title_plot_node
from .movies import MoviePlotElement, MoviePlotNode
from .plot_settings import PlotSettings
from .plot_tools import (
    update_vlims, set_margins_if_provided, set_lims_if_provided,
    PlotDimsMixin,
) 
from ..errors import PlottingAmbiguityError
from ..tools import (
    alias, alias_key_of, alias_child, simple_property,
    UNSET,
    pcAccessor,
    xarray_gaussian_filter,
    xarray_ensure_dims, xarray_as_array, xarray_fill_coords,
)


@PlotSettings.format_docstring()
class XarrayContourPlotElement(MoviePlotElement):
    '''plot contours of 2D data.
    
    array: xarray.DataArray, probably ndim=2.
        the data to be plotted.
    add_colorbar: {add_colorbar}
    colorbar_linewidth: {colorbar_linewidth}
    colorbar_linestyle: {colorbar_linestyle}
    colorbar_lines_set: {colorbar_lines_set}
    label: {label}
        UNSET --> no label.
    legend_handle_kw: {legend_handle_kw}

    contourf: {contourf}
    '''
    def __init__(self, array, *, ax=None,
                 contourf=PlotSettings.default('contourf'),
                 **kw_super):
        kw_super.update(contourf=contourf)
        super().__init__(**kw_super)
        self._ax_init = ax
        self.array = array
        self.init_contour()

    array = alias_key_of('data', 'array', doc='''array for plot. Internally, stored at self.data['array']''')
    contour = simple_property('_contour', doc='''contour plot (instance of matplotlib.contour.QuadContourSet)''')
    ax = alias_child('contour', 'axes', if_no_child=None, doc='''the axes containing this contour plot''')
    fig = alias_child('ax', 'figure', if_no_child=None, doc='''figure containing this contour plot''')

    # # # PLOTTING THIS ELEMENT # # #
    def _contour_plotter(self, array):
        '''return plotter to use for making contours.
        array.plot.contourf or array.plot.contour, depending on self.plot_settings['contourf'].
        '''
        return array.plot.contourf if self.plot_settings['contourf'] else array.plot.contour

    def _contour_plotter_kwargs(self):
        '''return kwargs to use for making contours.
        array.plot.contourf or array.plot.contour, depending on self.plot_settings['contourf'].
        '''
        fname = 'contourf' if self.plot_settings['contourf'] else 'contour'
        return self.plot_settings.get_mpl_kwargs(f'xarray.DataArray.plot.{fname}')

    def init_contour(self):
        '''initialize the contour plot; actually plot the data.
        stores plotted object in self.contour and returns self.contour.
        '''
        array = self.array
        # plot settings / kwargs / bookkeeping
        kw_plot = self._contour_plotter_kwargs()
        kw_plot = update_vlims(array, kw_plot)  # [TODO] and update levels too?
        kw_plot.update(add_colorbar=False)  # we handle colorbar via self.colorbar() instead.
        if 'label' in kw_plot:
            kw_plot['label'] = kw_plot['label'].format(**xarray_nondim_coords(array))
        # make plot
        plotter = self._contour_plotter(array)
        self.contour = plotter(ax=self._ax_init, **kw_plot)
        # formatting
        aspect = self.plot_settings['aspect']  # xarray plotter doesn't like 'aspect' kwarg; assign here instead.
        if aspect is not None:
            self.ax.set_aspect(aspect)
        set_margins_if_provided(self.plot_settings, ax=self.ax)
        set_lims_if_provided(self.plot_settings, ax=self.ax)
        # make colorbar if appropriate
        if self.plot_settings['add_colorbar']:
            self.colorbar()
        return self.contour

    # # # UPDATING (REQUIRED BY PARENT) # # #
    def update_data(self, data):
        '''update the plot using data['array'].
        return the list of all updated matplotlib Artist objects.
        '''
        # [TODO] is there a way to update existing contours instead of making new ones?
        array = data['array']
        # remove existing contours (if any). Remember some old values first.
        old = getattr(self, 'contour', None)
        assert old is not None, "ContourPlotElement.update_data called before init_contour?"
        ax_old = self.ax
        kw_old = dict(  # be sure to use the same limits as old.
                levels = old.levels,
                vmin = old.get_clim()[0],
                vmax = old.get_clim()[1],
                cmap = old.cmap,
                )
        old.remove()
        # plot new contours
        kw_plot = self._contour_plotter_kwargs()
        kw_plot.update(add_colorbar=False,   # updating data --> no new colorbar...
                        add_labels=False,    # --> no new labels (from here) either.
                        )
        kw_plot = update_vlims(array, kw_plot)  # [TODO] and update levels too?
        kw_plot.update(kw_old)
        plotter = self._contour_plotter(array)
        self.contour = plotter(ax=ax_old, **kw_plot)
        return [self.contour]

    # # # ADDING STUFF TO PLOT # # #
    def colorbar(self, *,
                 colorbar_linewidth=UNSET, colorbar_linestyle=UNSET, colorbar_lines_set=UNSET,
                 **kw_plt_colorbar):
        '''add a colorbar to the plot. sets self.cbar = Colorbar object, and returns it.'''
        contour = self.contour
        kw_plt_colorbar.update(self.plot_settings.get('colorbar_kw', default=dict()))
        self.cbar = self.fig.colorbar(contour, **kw_plt_colorbar)
        # formatting for colorbar lines
        clines = self.cbar.ax.get_children()[1]  # matplotlib.collections.LineCollection of lines on colorbar.
        kw_clines = self.plot_settings.get('colorbar_lines_set', colorbar_lines_set, default=dict())
        kw_clines = kw_clines.copy()  # copy <--> don't edit default.
        lw = self.plot_settings.get('colorbar_linewidth', colorbar_linewidth)
        ls = self.plot_settings.get('colorbar_linestyle', colorbar_linestyle)
        if ls is not None:
            kw_clines['linestyle'] = ls
        if lw is not None:
            if isinstance(lw, tuple) and len(lw)==2:
                lwmin, lwmax = lw
                lwnow = clines.get_linewidth()  # current linewidth (is a list or array, e.g. [2])
                lwuse = np.clip(lwnow, lwmin, lwmax)
                kw_clines['linewidth'] = lwuse
            else:
                kw_clines['linewidth'] = lw
        clines.set(**kw_clines)
        return self.cbar

    def legend_handle(self, label=UNSET, **kw_line_2D_set):
        '''return a handle to be used in a legend for this plot.
        Will look like the first contour line in self.contour,
            but then apply any settings from kw_line_2D_set.
        E.g. provide color='black' to make a line like the first contour, but black.

        Recommend:
            plt.legend(handles=[self.legend_handle(), ...])
        filling in the ... with any other artists who have legend elements to draw.
        To grab the default list of handles, you can use:
            default_handles = ax.get_legend_handles_labels()[0].
        where ax is the axis where objects are plotted (maybe self.ax, or plt.gca()).
        Putting these together would result in something like:
            plt.legend(handles=[self.legend_handle(), *default_handles], ...)
        If the handles aren't long enough to visually distinguish, try handlelength=5 or more.
        '''
        baseline = self.contour.legend_elements()[0][0]  # Line2D matching 0th contour style.
        result = mpl_lines.Line2D([0],[0])
        result.update_from(baseline)
        label = self.plot_settings.get('label', label)
        kw_line_2D_set.update(self.plot_settings.get('legend_handle_kw', default=dict()))
        result.set(**kw_line_2D_set, label=label)
        return result

    handle = alias('legend_handle')


@pcAccessor.register('contour')
@PlotSettings.format_docstring()
class XarrayContour(MoviePlotNode, PlotDimsMixin):
    '''MoviePlotNode of contours.
    stores an XarrayContourPlotElement & has methods for plotting & updating the plot.
    "contour" refers to a matplotlib.contour.QuadContourSet object, e.g. the result of plt.contour.

    Troubleshooting jagged contours? Try using blur=1 or larger!

    array: xarray.DataArray, probably ndim=3.
        the data to be plotted. if ndim=2, can still plot, but nothing to animate.
    t: None or str
        the array dimension which frames will index. E.g. 'time'.
        None -> infer from array & any other provided dimensions.
    x, y: None or str
        if provided, tells dimensions for the x, y plot axes.
        None -> infer from array & any other provided dimensions.
    ax: None or Axes
        the attached mpl.axes.Axes object.
        None --> will use self.ax=plt.gca() when getting self.ax for the first time.
    blur: None or number
        if non-None, apply gaussian filter to array before storing it;
        use sigma=blur, and only blur along x_plot_dim & y_plot_dim.
        e.g. equivalent to arr.pc.blur(['x', 'y'], sigma=blur).pc.contour(..., blur=None)
        This is useful if the contours are too jagged / noisy!

    init_plot: {init_plot}

    label: {label}
    legend_handle_kw: {legend_handle_kw}

    {kw_ax_margin}

    title: {title}
    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}
    '''
    element_cls = XarrayContourPlotElement

    def __init__(self, array, t=None, *, x=None, y=None, ax=None, blur=None,
                 init_plot=PlotSettings.default('init_plot'),  # <- could go in kw_super, but explicit is nice.
                 label=PlotSettings.default('label'),
                 **kw_super):
        if isinstance(array, xr.Dataset):
            array = xarray_as_array(array)
        array = xarray_fill_coords(array, need=[x, y, t])
        array = xarray_ensure_dims(array, ({x, y, t} - {None}), promote_dims_if_needed=True)
        self.array = array
        self.t = t
        self.x = x
        self.y = y
        self._ax_init = ax
        kw_super.update(init_plot=init_plot, label=label)
        self.plot_dims_attrs = self.plot_dims_attrs.copy()  # copy cls attr to avoid overwriting by accident
        if blur is not None:
            self.array = xarray_gaussian_filter(self.array, self.xy_plot_dims, sigma=blur)
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    ax = alias_child('obj', 'ax', doc='''mpl.axes.Axes where this Contour is plotted.''')
    @ax.getter
    def ax(self):  # ax=None if not self.plotted
        return self.obj.ax if self.plotted else None

    fig = alias_child('obj', 'fig', doc='''figure where this Contour is plotted.''')
    @fig.getter
    def fig(self):  # fig=None if not self.plotted
        return self.obj.fig if self.plotted else None

    handle = alias_child('obj', 'handle', doc='''creates legend handle to use for this Contour.''')

    # # # PLOTTING METHODS (REQUIRED BY PARENT CLASS) # # #
    def init_plot(self):
        '''plot for the first time. Save the XarrayContourPlotElement at self.obj'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs('pc.XarrayContourPlotElement')
        # -- determine vlims (based on the entire array, not just this frame)
        kw_plot = update_vlims(self.array, kw_plot)
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
        x, y = self.xy_plot_dims   # (x and y are strings, the dimension names)
        result = result.transpose(y, x)   # transposed to get correct order for plotting
        return {'array': result}

    def get_nframes_here(self):
        '''return the number of frames that could be in the movie, based on this node.'''
        t = self.t_plot_dim
        if t is None:
            return 1
        return len(self.array.coords[t])

    # # # INFERRING DIMS (REQUIRED BY PARENT CLASS) # # #
    plot_dims_attrs = dict(x='x', y='y', t='t', dims='_array_dims', t_necessary_if='_array_is_not_2D')
    _array_dims = property(lambda self: self.array.dims, doc='''the dimensions of the array''')
    # x_plot_dim, y_plot_dim, t_plot_dim are already defined by PlotDimsMixin.

    def _array_is_not_2D(self):
        '''tells whether self.array is not 2D'''
        return self.array.ndim != 2

    def _has_valid_plot_dims(self):
        '''return whether this array is plottable, i.e. all plot_dims can be inferred,
        and array doesn't have more than 3 dims.'''
        if self.array.ndim > 3:
            return False
        try:
            _plot_dims = self.xyt_plot_dims
        except PlottingAmbiguityError:
            return False
        return True

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
