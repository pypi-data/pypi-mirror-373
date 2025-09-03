"""
File Purpose: Faceplot: 3 plots on 3 faces of a box in 3D.

[TODO] faceplot with variable plot dim, via PlotDimsMixin.
"""

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as mpl3d
import numpy as np
import xarray as xr

from .labels import xarray_title_plot_node
from .movies import MoviePlotElement, MoviePlotNode
from .plot_settings import PlotSettings
from .plot_tools import (
    current_axes_or_None,
    update_vlims,
    infer_movie_dim,
)

from ..errors import PlottingAmbiguityError, PlottingNotImplementedError
from ..tools import (
    simple_property, alias, alias_child,
    # format_docstring, UNSET,
    is_iterable,
    xarray_isel, xarray_nondim_coords,
    pcAccessor,
)
from ..defaults import DEFAULTS


### --------------------- Helpful tools --------------------- ###

@pcAccessor.register('faces_3D', totype='array')
def xarray_faces_3D(array, ikeep=0, *, dims=('x', 'y', 'z')):
    '''infer the faces (at 0th index of dims) of a 3D xarray.DataArray.
    ikeep: int
        select ikeep'th value in the removed-dimension for each face.
        E.g. if ikeep=0: x_y=array.isel(z=0), x_z=array.isel(y=0), and y_z=array.isel(x=0).
    dims: 3-tuple of str
        the names of the dimensions for the x, y, and z faces.
        also affects resulting data var names,
            e.g. dims='abc' --> result will have 'a_b' instead of 'x_y'.
    
    returns xarray.Dataset with data vars x_y, x_z, y_z.
    '''
    x, y, z = dims
    result = {
        'x_y': array.isel({z: ikeep}),
        'x_z': array.isel({y: ikeep}),
        'y_z': array.isel({x: ikeep}),
    }
    return xr.Dataset(result)


### --------------------- Faceplot stuff --------------------- ###

@PlotSettings.format_docstring(sub_ntab=1)
class FaceplotPlotElement(MoviePlotElement):
    '''3 plots on 3 faces of a box in 3D.
    Faceplot.__init__ will make these plots.

    Troubleshooting colors? Try providing vmin, vmax, & levels, explicitly!
    
    coords: dictlike with keys 'x', 'y', 'z'
        1D coordinate arrays along each dimension.
    data: dictlike with keys 'x_y', 'x_z', 'y_z'
        2D arrays of data to plot on the faces.
        E.g. 'x_z' data will go on the x-z face.
    ax: None or axes with 3d projection.
        e.g. fig.add_subplot(1,1,1, projection='3d')
        if None, use plt.gca() if current axes exist, else make new axes.

    Additional kwargs control settings for the plot:
        faceplot_view_angle: {faceplot_view_angle}
        faceplot_edge_kwargs: {faceplot_edge_kwargs}
        faceplot_axes_zoom: {faceplot_axes_zoom}
        aspect3d: {aspect3d}

        any of these kwargs for ax.contourf:
            'vmin', 'vmax', 'levels', 'cmap',

        any of these kwargs for ax.set:
            'xlabel', 'ylabel', 'zlabel', 'xlim', 'ylim', 'zlim',
            'xticks', 'yticks', 'zticks', 'xticklabels', 'yticklabels', 'zticklabels'
            Note the defaults for 'xlabel', 'ylabel', 'zlabel' will be 'x', 'y', 'z'.

        add_colorbar: bool
            whether to self.colorbar() during __init__.
        colorbar_kw: {colorbar_kw}

    These attrs of self will be created/updated during init (here, face='x_y', 'x_z', or 'y_z'):
        meshgrids: {{face: {{x: 2d array of x values at face}} for x in face}}
        coord_lims: {{x: [min, max] for x in 'x', 'y', 'z'}}
        data_lims: {{'all': [min, max], **{{face: [min, max]}} }}
        ax: the axes object to plot on; create if needed.
        faces: {{face: the mpl_toolkits.mplot3d.art3d.QuadContourSet3D plotted on this face}}
        edges: {{x: the mpl_toolkits.mplot3d.art3d.Line3D plotted at x=0. x='x', 'y' or 'z'}}
    '''
    # # # CREATING & INITIALIZING # # #
    def __init__(self, coords, data, *, ax=None,
                 xlabel='x', ylabel='y', zlabel='z',
                 add_colorbar=True,
                 **kw_super):
        self.coords = coords
        self._data_init = data  # <-- may help with debugging
        self._ax_init = ax
        kw_super.update(xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, add_colorbar=add_colorbar)
        super().__init__(**kw_super)
        # super().__init__ assigns self.data, so this line must go after that:
        self.data = {face: data[face] for face in ('x_y', 'x_z', 'y_z')}
        # create the whole plot:
        self.init_all()

    fig = alias_child('ax', 'figure', if_no_child=None, doc='''figure containing this faceplot.''')

    def init_all(self):
        '''call all relevant init_* methods.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.init_meshgrids()
        self.init_coord_lims()
        self.init_data_lims()
        self.init_ax()
        self.init_faces()
        self.init_edges()
        self.init_viewing()
        if self.plot_settings['add_colorbar']:
            self.colorbar()

    @classmethod
    def from_dataset(cls, ds, **kw):
        '''create Faceplot from an xarray.Dataset.
        Equivalent: cls(ds.coords, ds, **kw)
        '''
        return cls(ds.coords, ds, **kw)

    def init_meshgrids(self):
        '''initialize self.meshgrids based on coords from self.coords.
        self.meshgrids = {
            'x_y': {'x': 2d array of x coords in x_y plot,
                    'y': 2d array of y coords in x_y plot},
            'x_z': {'x': 2d array of x coords in x_z plot,
                    'z': 2d array of z coords in x_z plot},
            'y_z': {'y': 2d array of y coords in y_z plot,
                    'z': 2d array of z coords in y_z plot},
        }
        returns self.meshgrids.
        '''
        coords = self.coords
        grid_lists = dict()
        grid_lists['x_y'] = np.meshgrid(coords['x'], coords['y'], indexing='ij')
        grid_lists['x_z'] = np.meshgrid(coords['x'], coords['z'], indexing='ij')
        grid_lists['y_z'] = np.meshgrid(coords['y'], coords['z'], indexing='ij')
        result = dict()
        result['x_y'] = {'x': grid_lists['x_y'][0], 'y': grid_lists['x_y'][1]}
        result['x_z'] = {'x': grid_lists['x_z'][0], 'z': grid_lists['x_z'][1]}
        result['y_z'] = {'y': grid_lists['y_z'][0], 'z': grid_lists['y_z'][1]}
        self.meshgrids = result
        return self.meshgrids

    def init_coord_lims(self):
        '''initialize self.coord_lims based on self.coords.
        self.coord_lims = {x: [min, max] for x in 'x', 'y', 'z'}
        returns self.coord_lims.
        '''
        coords = self.coords
        self.coord_lims = {x: [coords[x].min(), coords[x].max()] for x in ('x', 'y', 'z')}
        return self.coord_lims

    def init_data_lims(self):
        '''initialize self.data_lims based on self.data.
        data_lims = {
            'x_y': [min, max] of data['x_y'],
            'x_z': [min, max] of data['x_z'],
            'y_z': [min, max] of data['y_z'],
            'all': [min, max] of all data,
        }
        returns self.data_lims.
        '''
        data = self.data
        data_lims = dict()
        data_lims['x_y'] = [data['x_y'].min(), data['x_y'].max()]
        data_lims['x_z'] = [data['x_z'].min(), data['x_z'].max()]
        data_lims['y_z'] = [data['y_z'].min(), data['y_z'].max()]
        all_min = min(data_lims['x_y'][0], data_lims['x_z'][0], data_lims['y_z'][0])
        all_max = max(data_lims['x_y'][1], data_lims['x_z'][1], data_lims['y_z'][1])
        data_lims['all'] = [all_min, all_max]
        self.data_lims = data_lims

    def init_ax(self):
        '''initialize ax for self. returns self.ax'''
        ax = self._ax_init
        if ax is None:
            ax = current_axes_or_None()
        if ax is None:
            fig = plt.gcf()
            kw_ax = self.plot_settings.get_mpl_kwargs('mpl_toolkits.mplot3d.axes3d.Axes3D')
            ax = fig.add_subplot(1,1,1, projection='3d', **kw_ax)
        else:
            if not isinstance(ax, mpl3d.axes3d.Axes3D):
                errmsg = f'expected instance of mpl_toolkits.mplot3d.axes3d.Axes3D, got ax of type {type(ax)}'
                raise TypeError(errmsg)
        self.ax = ax
        return self.ax

    def init_faces(self):
        '''initialize the faces on self.ax; actually plot the data.
        stores plotted objects in self.faces & returns self.faces.
        '''
        ax = self.ax
        data = self.data
        grids = self.meshgrids
        kw_plot = self.plot_settings.get_mpl_kwargs('plt.contourf')
        # determine vlims for each face.
        kw_plot = update_vlims(list(data.values()), kw_plot)
        self.kw_plot = kw_plot  # remember kw for self._plot_face later.
        # actually plot the faces:
        self.faces = dict()
        for face in ('x_y', 'x_z', 'y_z'):
            self._plot_face(face, data[face])
        return self.faces

    def _plot_face(self, face, data2d):
        '''plots this data (2d array) on this face.
        updates self.faces accordingly. removes old face if it exists.
        returns the newly plotted face.
        '''
        ax = self.ax
        grids = self.meshgrids
        if face in self.faces:
            to_remove = self.faces[face]
        else:
            to_remove = None
        kw_plot = self.kw_plot
        if face == 'x_y':
            result = ax.contourf(grids['x_y']['x'], grids['x_y']['y'], data2d, zdir='z', offset=0, **kw_plot)
        elif face == 'x_z':
            result = ax.contourf(grids['x_z']['x'], data2d, grids['x_z']['z'], zdir='y', offset=0, **kw_plot)
        elif face == 'y_z':
            result = ax.contourf(data2d, grids['y_z']['y'], grids['y_z']['z'], zdir='x', offset=0, **kw_plot)
        else:
            raise ValueError(f'got face={face!r}; expected "x_y", "x_z", or "y_z".')
        self.faces[face] = result
        # remove old face:
        if to_remove is not None:
            to_remove.remove()  # remove old face from the figure, first.
        # return plotted face
        return result

    def init_edges(self):
        '''initialize the edges on self.ax; actually plot the edges.
        stores plotted objects in self.edges & returns self.edges.

        edges will not be plotted if self.plot_settings.get('faceplot_edge_kwargs') is None.
        '''
        kw_edges = self.plot_settings.get('faceplot_edge_kwargs')
        if kw_edges is None:
            self.edges = None
            return self.edges
        ax = self.ax
        lims = self.coord_lims
        edges = dict()
        edges['x'] = ax.plot(lims['x'], [lims['y'][0], lims['y'][0]], [lims['z'][0], lims['z'][0]], **kw_edges)
        edges['y'] = ax.plot([lims['x'][0], lims['x'][0]], lims['y'], [lims['z'][0], lims['z'][0]], **kw_edges)
        edges['z'] = ax.plot([lims['x'][0], lims['x'][0]], [lims['y'][0], lims['y'][0]], lims['z'], **kw_edges)
        self.edges = edges
        return self.edges

    def init_viewing(self):
        '''initialize view-related things: labels, viewing angle, aspect ratio, etc.'''
        ax = self.ax
        # set viewing angle
        view_angle = self.plot_settings.get('faceplot_view_angle')
        if view_angle is not None:  # (None --> use matplotlib default instead of setting angle.)
            ax.view_init(*view_angle)
        # set aspect ratio
        aspect = self.plot_settings.get('aspect3d')
        if aspect == 'auto':
            sizes = None
        elif aspect == 'equal' or aspect == 1 or (is_iterable(aspect) and len(aspect)==4):
            # matplotlib doesn't make it easy... need to calculate manually.
            coords = self.coords
            sizes = [len(coords[x]) for x in 'xyz']
            if is_iterable(aspect) and len(aspect)==4:
                sizes = [s*mul for s, mul in zip(sizes, aspect[1:])]
        elif is_iterable(aspect) and len(aspect)==3:
            sizes = aspect
        else:
            errmsg = f'aspect={aspect} not yet implemented; expected "auto", "equal", 3-tuple, or 4-tuple.'
            raise PlottingNotImplementedError(errmsg)
        if sizes is not None:
            zoom = self.plot_settings.get('faceplot_axes_zoom')
            ax.set_box_aspect(sizes, zoom=zoom)
        # set labels
        ax_setting = self.plot_settings.get_mpl_kwargs('ax.set')
        ax.set(**ax_setting)

    # # # BEHAVIORS # # #
    def __getitem__(self, k):
        '''returns self.faces[k] for 'x_y', 'x_z', or 'y_z', else self.edges[k] for 'x', 'y', or 'z',
        else crash with KeyError.
        '''
        if k in ('x_y', 'x_z', 'y_z'):
            return self.faces[k]
        elif k in ('x', 'y', 'z'):
            return self.edges[k]
        else:
            raise KeyError(f'key {k} not in {self.__class__.__name__}')

    # # # UPDATING # # #
    def update_data(self, data):
        '''updates the data on the plot to match the data provided here.
        data: dictlike with keys 'x_y', 'x_z', 'y_z'
            2D arrays of data to plot on the faces.
            E.g. 'x_z' data will go on the x-z face.
        returns the list of updated face artist objects.
        '''
        result = []
        for face in ('x_y', 'x_z', 'y_z'):
            #self.faces[face].set_array(data[face])  # this would be better, but it crashes...
            result.append(self._plot_face(face, data[face]))
            self.data[face] = data[face]  # <- updated for bookkeeping/consistency.
        return result

    # # # ADDING STUFF TO PLOT # # #
    def colorbar(self, **kw_plt_colorbar):
        '''add a colorbar to the figure. sets self.cbar = Colorbar object, and returns it.
        Troubleshooting colors? Try providing vmin, vmax, & levels, explicitly!
        '''
        face = self.faces['x_y']
        kw_plt_colorbar.update(self.plot_settings.get('colorbar_kw', default=dict()))
        self.cbar = self.fig.colorbar(face, **kw_plt_colorbar)
        return self.cbar


@pcAccessor.register('faceplot')
@PlotSettings.format_docstring()
class Faceplot(MoviePlotNode):  # [TODO] refactor PlotDimsMixin to use it here.
    '''MoviePlotNode of a faceplot.
    stores a FaceplotPlotElement, and updates it for each frame of the movie.
    "faceplot" refers to 3  plots on 3 faces of a box in 3D.

    Troubleshooting colors? Try providing vmin, vmax, & levels, explicitly!

    data: dictlike with keys 'x_y', 'x_z', 'y_z', or an xarray.DataArray.
        2D arrays of data to plot on the faces. E.g. 'x_z' data goes on the x-z face.
        xarray.DataArray --> infer faces via isel z=0, y=0, and x=0, respectively.
    coords: None or dictlike with keys 'x', 'y', 'z'
        1D coordinate arrays along each dimension.
        If None, infer from data['x'], data['y'], data['z'].
    t: None, str, or int
        the array dimension which frames will index. E.g. 'time'.
        None --> infer it via infer_movie_dim(data['x_y'].dims, t).
        str --> name of time dimension. And, data should be xarray object(s).
        int --> index of time dimension. And, data should be dict of numpy arrays.

    init_plot: {init_plot}

    add_colorbar: {add_colorbar}
    add_labels: {add_labels}

    title: {title}
    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}
    '''
    element_cls = FaceplotPlotElement

    def __init__(self, data, *, coords=None, t=None, ax=None,
                 init_plot=PlotSettings.default('init_plot'),  # <- could go in kw_super, but explicit is nice.
                 add_colorbar=PlotSettings.default('add_colorbar'),
                 add_labels=PlotSettings.default('add_labels'),
                 **kw_super):
        if isinstance(data, xr.DataArray):
            data = xarray_faces_3D(data)
        xyarr = data['x_y']
        if hasattr(xyarr, 'dims') and xyarr.ndim > 2:
            t = infer_movie_dim(xyarr.dims, t)
        if (xyarr.ndim != 2) and (t is None):
            errmsg = 't=None but is required (when array.ndim != 2). But cannot infer t from data provided.'
            raise PlottingAmbiguityError(errmsg)
        self.t = t
        if coords is None:
            coords = {x: data[x] for x in 'xyz'}
        self.coords = coords
        self.data = data
        self._ax_init = ax
        kw_super.update(init_plot=init_plot, add_colorbar=add_colorbar, add_labels=add_labels)
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    ax = alias_child('obj', 'ax', doc='''mpl_toolkits.mplot3d.axes3d.Axes3D where this Faceplot is plotted.''')
    @ax.getter
    def ax(self):  # ax=None if not self.plotted
        return self.obj.ax if self.plotted else None

    fig = alias_child('obj', 'fig', doc='''figure where this Faceplot is plotted.''')
    @fig.getter
    def fig(self):  # fig=None if not self.plotted
        return self.obj.fig if self.plotted else None

    # # # METHODS FOR PLOTTING (parent class wants these to be implemented here) # # #
    def init_plot(self):
        '''plot for the first time. Save the FaceplotPlotElement at self.obj.'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs('pc.FaceplotPlotElement')
        # -- determine vlims (based on the entire dataset, not just this frame)
        kw_plot = update_vlims([self.data[face] for face in ('x_y', 'x_z', 'y_z')], kw_plot)
        # >> actually make the plot on self.ax <<
        self.obj = self.element_cls(self.coords, data, ax=self._ax_init, **kw_plot)
        # -- if add_labels, add title:
        if self.plot_settings['add_labels']:
            self.plot_title()
        # bookkeeping
        self.frame = frame

    def get_data_at_frame(self, frame):
        '''returns dict-like of data at this frame, ready for plotting.'''
        t = self.t
        result = self.data
        if t is not None:  # there is a dimension for the time axis.
            if isinstance(result, xr.Dataset):
                result = xarray_isel(result, {t: frame})
            else:
                result = dict()
                for face in ('x_y', 'x_z', 'y_z'):
                    if isinstance(result[face], xr.DataArray):
                        result[face] = xarray_isel(result[face], {t: frame})
                    else:
                        result[face] = result[face].take(frame, axis=t)
        return result

    def get_nframes_here(self):
        '''return the number of frames that could be in the movie, based on this node.'''
        t = self.t
        if t is None:
            return 1
        # else, there is a time dimension. return its length:
        data = self.data
        if isinstance(data, xr.Dataset):
            result = len(data[t])
        else:
            if isinstance(data['x_y'], xr.DataArray):
                result = len(data['x_y'][t])
            else:
                result = data['x_y'].shape[t]
        return result

    # # # TITLE # # #
    def plot_title(self):
        '''adds title (as a MovieTextNode) on self.ax.
        raise PlottingAmbiguityError if title already plotted
            (this prevents having multiple title nodes).
        '''
        if hasattr(self, 'title_node'):
            raise PlottingAmbiguityError(f'{type(self).__name__} title was already plotted!')
        title = self.plot_settings['title']
        if title is not None:
            kw_title = {**self.plot_settings.kw, 'init_plot': True}
            title_node = xarray_title_plot_node(self.data['x_y'], title, t=self.t,
                                                ax=self.ax, parent=self, **kw_title)
            self.title_node = title_node  # <-- for bookkeeping/debugging
