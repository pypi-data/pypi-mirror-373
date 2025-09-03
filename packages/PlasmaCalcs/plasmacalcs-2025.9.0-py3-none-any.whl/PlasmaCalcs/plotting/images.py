"""
File Purpose: tools related to plotting images or 3D data (e.g. imshow, pcolormesh)
"""
import xarray as xr
import matplotlib.pyplot as plt

from .labels import xarray_title_plot_node
from .movies import MoviePlotElement, MoviePlotNode
from .plot_settings import PlotSettings
from .plot_tools import (
    update_vlims, set_margins_if_provided, set_lims_if_provided, set_min_n_ticks,
    PlotDimsMixin,
    current_axes_or_None, current_figure_exists,
) 
from .scatter import (
    xarray_scatter_max, xarray_scatter_min, xarray_scatter_where,
)
from ..errors import (
    InputError,
    PlottingAmbiguityError,
)
from ..tools import (
    alias_key_of, alias_child, simple_property,
    UNSET,
    pcAccessor,
    xarray_ensure_dims, xarray_as_array, xarray_fill_coords,
)



### --------------------- ImagePlotElement & Image --------------------- ###

_paramdocs_ax = {
    'ax': '''None or Axes
        the attached mpl.axes.Axes object.
        None --> will use self.ax=plt.gca() when getting self.ax for the first time.''',
}

@PlotSettings.format_docstring(**_paramdocs_ax)
class ImagePlotElement(MoviePlotElement):
    '''image on an Axes.
    "image" refers to a matplotlib.cm.ScalarMappable object, e.g. the result of imshow or pcolormesh.

    array: array-like object, probably ndim=2.
        the data to be plotted. will be stored in self.data['array']
    ax: {ax}
    image_mode: {image_mode}

    Additional kwargs can be any PlotSettings; see help(self.plot_settings) for details.
    '''
    def __init__(self, array, *, ax=None,
                 image_mode=PlotSettings.default('image_mode'),  # <- could go in kw_super, but explicit is nice.
                  **kw_super):
        super().__init__(image_mode=image_mode, **kw_super)
        self._ax_init = ax
        self.array = array
        self.init_im()

    array = alias_key_of('data', 'array', doc='''array for plot. Internally, stored at self.data['array']''')
    im = simple_property('_im', doc='''the image object (instance of matplotlib.cm.ScalarMappable)''')
    ax = alias_child('im', 'axes', if_no_child=None, doc='''the axes containing this image''')
    fig = alias_child('ax', 'figure', if_no_child=None, doc='''figure containing this image''')

    # # # PLOTTING THIS ELEMENT # # #
    def init_im(self):
        '''initialize image; actually plot the data.
        stores plotted object in self.im & returns self.im.
        '''
        # plot settings / kwargs / bookkeeping
        image_mode = self.plot_settings['image_mode']
        settings_key_lookup = {'pcolormesh': 'plt.pcolormesh', 'imshow': 'plt.imshow'}
        if image_mode not in settings_key_lookup:
            raise InputError(f'invalid image_mode: {image_mode!r}, expected "pcolormesh" or "imshow".')
        settings_key = settings_key_lookup[image_mode]
        kw_plot = self.plot_settings.get_mpl_kwargs(settings_key)
        kw_plot = update_vlims(self.array, kw_plot)
        # ax to use for plot
        ax = self._ax_init
        if ax is None:
            ax = plt.gca()
        # make plot
        if image_mode == 'pcolormesh':
            self.im = ax.pcolormesh(self.array, **kw_plot)
        else:  # image_mode == 'imshow'
            self.im = ax.imshow(self.array, **kw_plot)
        return self.im

    # # # UPDATING (REQUIRED BY PARENT) # # #
    def update_data(self, data):
        '''update the plot using data['array'].
        return list of all updated matplotlib Artist objects.
        '''
        array = data['array']
        if self.plot_settings['image_mode'] == 'pcolormesh':
            self.im.set_array(array)
        else:  # image_mode == 'imshow'
            self.im.set_data(array)
        self.array = array  # <- updated for bookkeeping/consistency.
        return [self.im]

    # # # DISPLAY # # #
    def __repr__(self):
        array_info = f'{type(self.array).__name__} with shape={self.array.shape}'
        return f'{type(self).__name__}({array_info})'


@PlotSettings.format_docstring(**_paramdocs_ax)
class Image(MoviePlotNode):
    '''stores an ImagePlotElement & has methods for plotting & updating the image!
    "image" refers to a matplotlib.cm.ScalarMappable object, e.g. the result of imshow or pcolormesh.

    array: array-like object, probably ndim=3.
        the data to be plotted. will be stored in self.data['array']
    '''
    def __init__(self, *args__TODO, **kw__TODO):
        raise NotImplementedError('[TODO]: MovieImage. In the meantime, use XarrayImage.')
        # no need to implement this if willing to convert arrays to xarrays before plotting.
        # most of PlasmaCalcs works with xarrays, so code development should focus on XarrayImage.


### --------------------- XarrayImagePlotElement & XarrayImage --------------------- ###

@PlotSettings.format_docstring(**_paramdocs_ax)
class XarrayImagePlotElement(ImagePlotElement):
    '''image on an Axes, for an xarray.DataArray.
    "image" refers to a matplotlib.cm.ScalarMappable object, e.g. the result of imshow or pcolormesh.

    array: xarray.DataArray, probably ndim=2.
        the data to be plotted.
    ax: {ax}
    image_mode: {image_mode}

    add_colorbar: {add_colorbar}
    add_labels: {add_labels}

    min_n_ticks: {min_n_ticks}
    min_n_ticks_cbar: {min_n_ticks_cbar}

    grid: {grid}
    '''
    def __init__(self, array, *, ax=None,
                 image_mode=PlotSettings.default('image_mode'),  # <- could go in kw_super, but explicit is nice.
                 add_colorbar=PlotSettings.default('add_colorbar'),
                 add_labels=PlotSettings.default('add_labels'),
                 **kw_super):
        kw_super.update(image_mode=image_mode, add_colorbar=add_colorbar, add_labels=add_labels)
        super().__init__(array, ax=ax, **kw_super)
    
    @property
    def cbar(self):
        '''Colorbar object associated with this image. False if no associated colorbar.
        None if self.im does not exist yet (i.e. not yet plotted).
        "associated" meaning: colorbar using this image as its scalar mappable.
        '''
        im = getattr(self, 'im', None)
        if im is None:
            return None
        else:
            result = getattr(im, 'colorbar', None)
            if result is None:  # im exists but has no colorbar
                return False
            else:
                return result

    def init_im(self):
        '''initialize image on self.ax; actually plot the data.
        stores plotted object in self.im & returns self.im.
        '''
        array = self.array
        image_mode = self.plot_settings['image_mode']
        kw_plot = self.plot_settings.get_mpl_kwargs('xarray.DataArray.plot[image]')
        kw_plot = update_vlims(array, kw_plot)
        plotter = getattr(array.plot, image_mode)  # e.g. array.plot.pcolormesh
        ax = self._ax_init
        if ax is None:
            ax = current_axes_or_None()
            if (ax is None) and (not current_figure_exists()):  # no current axes nor figure.
                kw_fig = self.plot_settings.get_mpl_kwargs('plt.figure')
                _fig = plt.figure(**kw_fig)
                # ax = None, still, but plotter can now create ax on current fig as needed.
            if (ax is None):
                polar = self.plot_settings.get('polar', last_resort_default=False)
                if polar:
                    ax = plt.gcf().add_subplot(polar=polar)
        self.im = plotter(ax=ax, **kw_plot)
        # labels
        if self.plot_settings['add_labels']:
            self.plot_labels()
        # formatting
        aspect = self.plot_settings['aspect']  # xarray plotter doesn't like 'aspect' kwarg; assign here instead.
        if aspect is not None:
            self.ax.set_aspect(aspect)
        set_margins_if_provided(self.plot_settings, ax=self.ax)
        set_lims_if_provided(self.plot_settings, ax=self.ax)
        min_n_ticks = self.plot_settings['min_n_ticks']
        if min_n_ticks is not None:
            fail_ok=self.plot_settings['min_n_ticks_fail_ok']
            set_min_n_ticks(min_n_ticks, ax=self.ax, fail_ok=fail_ok)
        if self.cbar is not False:
            min_n_ticks_cbar = self.plot_settings['min_n_ticks_cbar']
            if min_n_ticks_cbar is not None:
                fail_ok = self.plot_settings['min_n_ticks_cbar_fail_ok']
                set_min_n_ticks(min_n_ticks_cbar, ax=self.cbar.ax, fail_ok=fail_ok)
        grid = self.plot_settings.get('grid')
        if grid is not UNSET:
            if isinstance(grid, dict):
                self.ax.grid(**grid)
            else:
                self.ax.grid(grid)
        return self.im

    def plot_labels(self):
        '''plots xlabel and ylabel from self.plot_settings.
        If xlabel or ylabel not provided:
            - use defaults from xarray's plot method.
            - if array.attrs has 'coords_units', put that in brackets, e.g. 'x [si]'.
        If they are provided, use them, but also .format(**array.attrs).
            (e.g. 'x [{units}]' becomes 'x [si]' if array.attrs['units'] == 'si')
        '''
        xlabel = self.plot_settings.get('xlabel', default=None)
        ylabel = self.plot_settings.get('ylabel', default=None)
        if xlabel is None:
            if 'coords_units' in self.array.attrs:
                coords_units = self.array.attrs['coords_units']
                xlabel = ' '.join((self.ax.get_xlabel(), f'[{coords_units}]'))
                self.ax.set_xlabel(xlabel)
        else:
            xlabel = xlabel.format(**self.array.attrs)
            self.ax.set_xlabel(xlabel)
        if ylabel is None:
            if 'coords_units' in self.array.attrs:
                coords_units = self.array.attrs['coords_units']
                ylabel = ' '.join((self.ax.get_ylabel(), f'[{coords_units}]'))
                self.ax.set_ylabel(ylabel)
        else:
            ylabel = ylabel.format(**self.array.attrs)
            self.ax.set_ylabel(ylabel)


@pcAccessor.register('image')
@PlotSettings.format_docstring(**_paramdocs_ax)
class XarrayImage(MoviePlotNode, PlotDimsMixin):
    '''MoviePlotNode of an xarray.DataArray.
    stores an XarrayImagePlotElement & has methods for plotting & updating the image!
    "image" refers to a matplotlib.cm.ScalarMappable object, e.g. the result of imshow or pcolormesh.

    array: xarray.DataArray, probably ndim=3; or xarray.Dataset with single data_var
        the data to be plotted. if ndim=2, can still plot, but nothing to animate.
        if xarray.Dataset, must have only one data_var; will create image of that data_var.
    t: None or str
        the array dimension which frames will index. E.g. 'time'.
        None -> infer from array & any other provided dimensions.
        if provided but dimension not found, attempt xarray_promote_dim before crashing.
    x, y: None or str
        if provided, tells dimensions for the x, y plot axes.
        None -> infer from array & any other provided dimensions.
        if provided but dimension not found, attempt xarray_promote_dim before crashing.
    ax: {ax}
    image_mode: {image_mode}
    init_plot: {init_plot}

    {kw_ax_margin}

    title: {title}
    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}

    grid: {grid}

    # [TODO] example
    '''
    element_cls = XarrayImagePlotElement

    def __init__(self, array, t=None, *, x=None, y=None, ax=None,
                 image_mode=PlotSettings.default('image_mode'),  # <- could go in kw_super, but explicit is nice.
                 init_plot=PlotSettings.default('init_plot'),
                 add_colorbar=PlotSettings.default('add_colorbar'),
                 add_labels=PlotSettings.default('add_labels'),
                 title=PlotSettings.default('title'),
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
        kw_super.update(image_mode=image_mode, init_plot=init_plot,
                        add_colorbar=add_colorbar, add_labels=add_labels,
                        title=title,
                        )
        self.plot_dims_attrs = self.plot_dims_attrs.copy()  # copy cls attr to avoid overwriting by accident
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    ax = alias_child('obj', 'ax', if_special_child={None: None, UNSET: None},
        doc='''mpl.axes.Axes where this XarrayImage is plotted, or None if not plotted.''')

    fig = alias_child('obj', 'fig', if_special_child={None: None, UNSET: None},
        doc='''figure where this XarrayImage is plotted, or None if not plotted.''')

    im = alias_child('obj', 'im', if_special_child={None: None, UNSET: None},
        doc='''mpl.cm.ScalarMappable object of this XarrayImage, or None if not plotted.''')

    cbar = alias_child('obj', 'cbar', if_special_child={None: None, UNSET: None},
        doc='''the mpl.colorbar.Colorbar of this XarrayImage.
        None if image not plotted.
        False if image plotted but does not have an associated colorbar.''')

    # # # PLOTTING METHODS (REQUIRED BY PARENT CLASS) # # #
    def init_plot(self):
        '''plot for the first time. Save the XarrayImagePlotElement at self.obj.'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs('pc.XarrayImagePlotElement')
        # -- determine vlims (based on the entire array, not just this frame)
        kw_plot = update_vlims(self.array, kw_plot)
        # >> actually plot the image <<
        self.obj = self.element_cls(data['array'], ax=self._ax_init, **kw_plot)
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
            self.ax.set_title('')  # remove xarray's default title.
        else:
            kw_title = {**self.plot_settings.kw, 'init_plot': True}
            title_node = xarray_title_plot_node(self.array, title, t=self.t_plot_dim,
                                                ax=self.ax, parent=self, **kw_title)
            self.title_node = title_node  # <-- for bookkeeping/debugging

    # # # MISC CONVENIENT METHODS # # #
    def scatter_max(self, **kw_scatter):
        '''use XarrayScatter to plt.scatter() a single marker, at the argmax of self.array.
        animatable (e.g. different max for each frame); does self.add_child(scatter result)
        default style: {**DEFAULTS.PLOT.SCATTER_STYLE, **DEFAULTS.PLOT.SCATTER_MAX}
        returns XarrayScatter object (which got added as child of self).

        see also: xarray_scatter_max (or, array.pc.scatter_max)
        '''
        kw_scatter = {'add_labels': False,   # by default, don't let scatter overwrite image title.
                      **kw_scatter}
        result = xarray_scatter_max(self.array, x=self.x_plot_dim, y=self.y_plot_dim,
                                    t=self.t_plot_dim, ax=self.ax, **kw_scatter)
        self.add_child(result)
        return result

    def scatter_min(self, **kw_scatter):
        '''use XarrayScatter to plt.scatter() a single marker, at the argmin of self.array.
        animatable (e.g. different min for each frame); does self.add_child(scatter result)
        default style: {**DEFAULTS.PLOT.SCATTER_STYLE, **DEFAULTS.PLOT.SCATTER_MIN}
        returns XarrayScatter object (which got added as child of self).

        see also: xarray_scatter_min (or, array.pc.scatter_min)
        '''
        kw_scatter = {'add_labels': False,   # by default, don't let scatter overwrite image title.
                      **kw_scatter}
        result = xarray_scatter_min(self.array, x=self.x_plot_dim, y=self.y_plot_dim,
                                    t=self.t_plot_dim, ax=self.ax, **kw_scatter)
        self.add_child(result)
        return result

    def scatter_where(self, condition, **kw_scatter):
        '''use XarrayScatter to plt.scatter() markers where condition is True.
        animatable (e.g. different condition for each frame); does self.add_child(scatter result)
        returns XarrayScatter object (which got added as child of self).

        condition: callable or DataArray of bools
            callable --> use condition(self.array)
            DataArray --> ignore self.array entirely.

        For x, y, t plot dims, uses self.x_plot_dim, self.y_plot_dim, self.t_plot_dim.

        see also: xarray_scatter_where (or, array.pc.scatter_where)

        Example:
            xim = array.pc.image(...)
            xim.scatter_where(lambda arr: arr > 7.5)  # marker at all points where arr > 7.5
            xim.save(filename)  # save animation to filename (if xim.t_plot_dim is not None)
        '''
        kw_scatter = {'add_labels': False,   # by default, don't let scatter overwrite image title.
                      **kw_scatter}
        if callable(condition):
            condition = condition(self.array)
        x, y, t = self.x_plot_dim, self.y_plot_dim, self.t_plot_dim
        condition = xarray_fill_coords(condition, need=[x,y,t])
        condition = xarray_ensure_dims(condition, ({x, y, t} - {None}), promote_dims_if_needed=True)
        # [TODO] ^ be more lenient if appropriate coords don't exist in condition?
        result = xarray_scatter_where(condition, x=x, y=y, t=t, ax=self.ax, **kw_scatter)
        self.add_child(result)
        return result
