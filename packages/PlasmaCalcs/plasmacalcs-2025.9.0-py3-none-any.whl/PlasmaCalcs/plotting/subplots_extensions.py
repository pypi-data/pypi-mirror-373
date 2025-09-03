"""
File Purpose: various extensions to the Subplots class
"""
import numpy as np
import xarray as xr

from .images import XarrayImage
from .labels import XarraySubplotTitlesInferer, xarray_suptitle_plot_node, XarrayText
from .movies import MovieOrganizerNode, EmptyMovieNode
from .plot_settings import PlotSettings
from .plot_tools import calculate_vlims, plot_note
from .subplots import Subplots
from ..errors import (
    InputError, InputMissingError, InputConflictError,
    PlottingError, PlottingAmbiguityError,
)
from ..tools import (
    alias, alias_child,
    UNSET,
    wraplist, ndenumerate_nonNone, is_iterable,
    pcAccessor, take_along_dimensions, xarray_fill_coords,
    Tree,
)


@PlotSettings.format_docstring()
class MovieSubplots(MovieOrganizerNode, Subplots):
    '''MoviePlotNode for organizing a grid of subplots.
    Expects input 2D array (or nested list) of MoviePlotNodes,
        which were all created with init_plot=False
        (to allow MovieSubplots to create & assign the axes).
        For images, probably also want nodes to use add_colorbar=False
        (to allow MovieSubplots to create & assign the colorbar(s)).

    nodes: 2D array-like of MoviePlotNode or None objects
        the MoviePlotNodes associated with each subplot.
        None --> no MoviePlotNode for that subplot.
    name: str
        name for the MovieSubplots node; to be displayed in __repr__.
    parent: None or MoviePlotNode
        if provided, the parent of this node. None -> this node has no parent.
    init_plot: {init_plot}
    add_colorbars: {add_colorbars}

    kwargs which go to Subplots:
    axsize: {axsize}
    figsize: {figsize}
    {kw_subplots_adjust}
    {kw_share_axlike}
    {kw_share_ax}
    max_nrows_ncols: {max_nrows_ncols}
    squeeze: {squeeze}

    additional kwargs go to plt.subplots.

    Roughly equivalent functionality:
        subs = subplots(..., squeeze=False)  # creates a Subplots object
        axs = subs.axs  # the grid of axes in the Subplots
        msubs = MovieOrganizerNode()
        msubs_row0 = MovieOrganizerNode(parent=msubs)
        msubs_row1 = MovieOrganizerNode(parent=msubs)
        # ... as many rows as needed.
        MoviePlotNode(..., ax=axs[0,0], parent=msubs_row0)
        MoviePlotNode(..., ax=axs[0,1], parent=msubs_row0)
        # ...
        MoviePlotNode(..., ax=axs[1,0], parent=msubs_row1)
        MoviePlotNode(..., ax=axs[1,1], parent=msubs_row1)
        # ... as many nodes as needed.
        # --> while msubs wouldn't be a MovieSubplots object,
        #     it would still provide most of the same functionality,
        #     e.g. msubs.save(...) would properly animate & save movie!
    '''
    def __init__(self, nodes, name='', *, parent=None,
                 init_plot=PlotSettings.default('init_plot'),  # <- could go in kw_super, but explicit is nice.
                 add_colorbars=PlotSettings.default('add_colorbars'),
                 **kw_super):
        nodes = np.asanyarray(nodes)
        self.nodes = nodes
        if nodes.ndim != 2:
            raise InputError(f'nodes must be 2D, got shape {nodes.shape}')
        nrows, ncols = nodes.shape

        kw_super.update(nrows=nrows, ncols=ncols,
                init_plot=init_plot,
                add_colorbars=add_colorbars,
                name=name, parent=parent)
        # MovieOrganizerNode won't accidentally init_plot before axs are created,
        #   because it has obj=None so it never calls init_plot during __init__.
        super().__init__(**kw_super)

        if self.plot_settings['init_plot']:
            self.init_plot()

    def init_plot(self):
        '''plot for the first time: call init_plot on all nodes,
        and organize into a nice tree structure which can be indexed like an array.

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
        # bookkeeping
        name_append = f' {self.name}' if self.name else ''
        axs = self.axs
        # call init_plots on nodes, set up row organizers, & create appropriate node tree.
        for i, row in enumerate(self.nodes):
            row_organizer = MovieOrganizerNode(name=f'(row={i}){name_append}', parent=self)
            for j, node in enumerate(row):
                if node is None:
                    node = EmptyMovieNode()
                else:
                    node._ax_init = axs[i,j]
                    node.init_plot()
                node.parent = row_organizer
        # formatting
        self.remove_redundant_labels()
        self.hide_empty_axes()
        add_colorbars = self.plot_settings['add_colorbars']
        if add_colorbars:
            if self.plot_settings.get('add_colorbar', False):
                raise InputConflictError('Can add_colorbars or add_colorbar, but not both!')
            self.colorbars(mode=add_colorbars)

    # # # INHERITANCE FUNNY BUSINESS # # #
    # we want this object to behave sometimes like MoviePlotNode, sometimes like Subplots.
    # Those two classes have mostly non-overlapping methods, but there is some overlap.

    # In particular, both define methods for indexing. Here we want to use Tree-like indexing!
    __getitem__ = Tree.__getitem__
    __iter__ = Tree.__iter__
    # [TODO] if there's a "cleaner" way to do this, that might be nice...

    # # # DISPLAY # # #
    DEFAULT_TREE_SHOW_DEPTH = 2   # use self.display(show_depth=...) to see with a different depth.


@pcAccessor.register('subplots')
@PlotSettings.format_docstring()
class XarraySubplots(MovieSubplots):
    '''grid of subplots from xarray data. Can be animated as a movie!

    xarray: xarray.DataArray or xarray.Dataset
        the array to plot. up to 5D (row, col, x, y, t).
        (Note that row & col dims should be "not too long" otherwise plot will be very large)
        if dataset, up to 4D; will be converted to DataArray with new dim named 'variable'.
        internally, will store xarray_fill_coords(xarray) to utilize coordless dims' indices in titles.
    row: None or str
        dimension to plot ACROSS rows.
        None --> subplots will have ncols=1 (nothing varies across a row --> only 1 column).
        E.g. if row=='fluid', then the i'th COLUMN will be fluid i.
        [TODO] infer row directly from xarray, somehow?
    col: None or str
        dimension to plot DOWN columns.
        None --> subplots will have nrows=1 (nothing varies down a column --> only 1 row).
        E.g. if col=='component', then the j'th ROW will be component j.
    wrap: None or int
        wrap row or col dimension after this many images.
        can only be provided if provided row or col but not both.
        E.g. if row=='fluid', wrap=4, and input has 10 fluids, will make rows of 4, 4, 2 images.
            Any remaining "empty" plots will have their axes hidden.
    x, y: None or str
        dimension name for the x and y axes of an individual subplot.
        None --> infer from the xarray coords. See also: DEFAULTS.PLOT.DIMS_INFER
    t: None or str
        dimension name for the time axis (for movies).
        None --> infer from the xarray coords. See also: DEFAULTS.PLOT.DIMS_INFER

    vmin, vmax: None, scalar value, or array-like
        if provided, tells value for vmin, vmax for all subplots, ignoring share_vlims and robust.
        if providing only one, still use share_vlims and robust for the other
            (e.g. if provided vmax but vmin=None, use share_vlims and robust when deciding on vmin).
        if array-like vmin, use vmin=vmin[i][j] for plot in i'th row and j'th column. Similar for vmax.
            (doesn't squeeze. e.g., if only 1 row exists, because row=None, then use vmin[0][j])
            (if non-None wrap, vlims shape should correspond to the shape after wrapping.)
            (use None limit to instead use share_vlims and robust for that subplot.
                E.g. vmin=[[0, 2, None]], share_vlims='row', robust=10, for subplots with 1 row, 3 cols,
                will use vmin=0 for first plot, 2 for second plot,
                    and vmin=10th percenticle across all values in all three plots, for the third plot.)
    share_vlims: {share_vlims}
    robust: {robust}

    axsize: {axsize}
    aspect: {aspect}
    layout: {layout}

    suptitle: {suptitle}
    suptitle_y: {suptitle_y}
    suptitle_font: {suptitle_font}
    suptitle_kw: {suptitle_kw}
    suptitle_width: {suptitle_width}

    title: {title}
    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}
    subplot_title_width: {subplot_title_width}

    rtitle: {rtitle}
    rtitle_kw: {rtitle_kw}
    ttitle: {ttitle}
    ttitle_kw: {ttitle_kw}

    cax_mode: {cax_mode}
    colorbar_kw: {colorbar_kw}
    add_colorbars: {add_colorbars}

    additional kwargs go to other places [TODO][DOC] fill in the details.
    '''
    def __init__(self, xarray, row=None, col=None, *, wrap=None, x=None, y=None, t=None,
                 fig=None,
                 vmin=None, vmax=None,
                 robust=PlotSettings.default('robust'),  # <- could go in **kw, but explicit is nice.
                 share_vlims=PlotSettings.default('share_vlims'),
                 title=PlotSettings.default('title'),
                 title_y=PlotSettings.default('title_y'),
                 suptitle=PlotSettings.default('suptitle'),
                 suptitle_y=PlotSettings.default('suptitle_y'),
                 rtitle=PlotSettings.default('rtitle'),
                 ttitle=PlotSettings.default('ttitle'),
                 aspect=PlotSettings.default('aspect'),
                 layout=PlotSettings.default('layout'),
                 cax_mode=PlotSettings.default('cax_mode'),
                 axsize=PlotSettings.default('axsize'),
                 add_colorbars=PlotSettings.default('add_colorbars'),
                 **kw):
        name = '' if (getattr(xarray, 'name', None) is None) else xarray.name
        if isinstance(xarray, xr.Dataset):
            xarray = xarray.to_array(dim='variable')
        xarray = xarray_fill_coords(xarray, need=[row, col, x, y, t])
        self.array = xarray
        # grid of xarray DataArrays, based on self.array, row, col, and wrap.
        arrs = self._get_xarray_arr(self.array, row=row, col=col, wrap=wrap)
        self.arrs = arrs
        # settings -- update kw with settings which are explicitly in function call signature.
        kw.update(title=title, title_y=title_y,
                  suptitle=suptitle, suptitle_y=suptitle_y,
                  rtitle=rtitle, ttitle=ttitle,
                  aspect=aspect, layout=layout, cax_mode=cax_mode,
                  add_colorbars=add_colorbars, axsize=axsize,
                  share_vlims=share_vlims, robust=robust)
        init_plot_settings = PlotSettings(**kw)
        # [TODO] infer row & col plot dimensions if not provided.
        self.row_plot_dim = row
        self.col_plot_dim = col
        self._wrap_input = wrap
        # vmin and vmax are handled separately in case we are sharing vlims or using robust:
        vlims_arr = self._get_vlims_arr(arrs, vmin=vmin, vmax=vmax, share_vlims=share_vlims, robust=robust)
        # create array of XarrayImage nodes (but don't init_plot or add_colorbar yet!)
        images = np.full(arrs.shape, None, dtype=object)
        for idx, arr in ndenumerate_nonNone(arrs):
            vmin, vmax = vlims_arr[idx]
            image = XarrayImage(arr, t=t, x=x, y=y,
                                vmin=vmin, vmax=vmax,
                                **{**kw,  # override input kw for these options here:
                                'init_plot': False, 'add_colorbar': False,
                                })
            # ensure arr is 2D or 3D (with an inferred t_plot_dim); else crash with helpful message.
            if not image._has_valid_plot_dims():
                errmsg = (f'failed to infer plot dimensions; image array has dims {image.array.dims!r}.\n'
                          'Most likely, you forgot to specify row, col, x, y, and/or t.')
                raise PlottingAmbiguityError(errmsg)
            images[idx] = image
        # infer subplot titles where not provided
        self.images = images  # <-- must do this before accessing self.t_plot_dim.
        kw_infer_titles = init_plot_settings.get_mpl_kwargs('pc.XarraySubplotTitlesInferer')
        self.titles_inferer = XarraySubplotTitlesInferer(self.array, t=self.t_plot_dim,
                                        row=self.row_plot_dim, col=self.col_plot_dim,
                                        **kw_infer_titles)  # titles_inferer might be used later even if not now.
        if (ttitle is not UNSET) and title is not PlotSettings.default('title'):
            raise InputConflictError('Cannot provide both ttitle and title at the same time!')
        if init_plot_settings['add_labels']:
            if ttitle is UNSET:
                if title is PlotSettings.default('title'):
                    for idx, image in ndenumerate_nonNone(images):
                        image.plot_settings['title'] = self.titles_inferer.infer_title()
            else:  # provided ttitle
                font = {'fontfamily': init_plot_settings['title_font'],
                        **init_plot_settings.get('title_kw', default={})}['fontfamily']
                ttitle_kw = {'fontfamily': font, **init_plot_settings['ttitle_kw']}
                for image in images[0, :]:
                    image.plot_settings['title'] = ttitle
                    image.plot_settings['title_kw'] = ttitle_kw
                for image in images[1:, :].flat:
                    image.plot_settings['title'] = None
        # init super
        super().__init__(images, fig=fig, name=name, **kw)  # [TODO] does non-None fig work here?
        # <- rtitle handled by self.init_plot()

    # # # INIT PLOT # # #
    def init_plot(self):
        '''plot for the first time: call init_plot on all nodes,
        and organize into a nice tree structure which can be indexed like an array.

        This is fundamentally different from MoviePlotNode.init_plot's usual purpose,
            since this is about calling init_plot on the nodes, not on self.obj.
            [TODO] should this function be renamed, for clarity?
        '''
        super().init_plot()
        # add suptitle after super().init_plot() adds children nodes for subplots.
        if self.plot_settings['add_labels']:
            self.plot_suptitle()
            self.plot_rtitles()

    # # # PROPERTIES # # #
    images = alias('nodes')
    image0 = property(lambda self: self.images[0,0], doc='''top-left image; images[0,0].''')
    x_plot_dim = alias_child('image0', 'x_plot_dim')
    y_plot_dim = alias_child('image0', 'y_plot_dim')
    t_plot_dim = alias_child('image0', 't_plot_dim')

    @property
    def isels(self):
        '''np.array (dtype=object) of (None or dict of index details), one for each subplot.
        E.g. full_array.isel(self.isels[1,4]) == self.images[1,4].array.
        '''
        rowdim = self.row_plot_dim
        coldim = self.col_plot_dim
        if (rowdim is None) and (coldim is None):
            raise NotImplementedError('[TODO] isels when row and col are both None')
        if (rowdim is not None) and (coldim is None):
            Lrowdim = self.array.sizes[rowdim]
            idxarr = np.empty(Lrowdim, dtype=object)
            for i in range(Lrowdim):
                 idxarr[i] = {rowdim: i}
            idxarr = xr.DataArray(idxarr, dims=[rowdim])
        elif (rowdim is None) and (coldim is not None):
            Lcoldim = self.array.sizes[coldim]
            idxarr = np.empty(Lcoldim, dtype=object)
            for i in range(Lcoldim):
                 idxarr[i] = {coldim: i}
            idxarr = xr.DataArray(idxarr, dims=[coldim])
        elif (rowdim is not None) and (coldim is not None):
            Lrowdim = self.array.sizes[rowdim]
            Lcoldim = self.array.sizes[coldim]
            idxarr = np.empty((Lrowdim, Lcoldim), dtype=object)
            for i in range(Lrowdim):
                for j in range(Lcoldim):
                    idxarr[i, j] = {rowdim: i, coldim: j}
            idxarr = xr.DataArray(idxarr, dims=[rowdim, coldim])
        result = self._get_xarray_arr(idxarr, row=rowdim, col=coldim, wrap=self._wrap_input)
        as_numpy = np.empty(result.shape, dtype=object)
        for idx, arr in np.ndenumerate(result):
            as_numpy[idx] = None if arr is None else arr.item()
        return as_numpy

    def rightmost_images(self, *, as_idx=False, missing_ok: True):
        '''list of rightmost existing image (i.e., non-None) in each row.
        as_idx: bool
            whether to return indices of images within self.images, instead of image objects.
        missing_ok: bool
            whether it is okay for some row to have no images (result will be None in those rows).
        '''
        result = []
        for irow, row in enumerate(self.images):
            for minus_icol, image in enumerate(row[::-1]):
                icol = len(row) - minus_icol - 1
                if image is not None:
                    result.append((irow, icol) if as_idx else image)
                    break
            else:
                if missing_ok:
                    result.append(None)
                else:
                    raise PlottingError(f'row {irow} has no images, and missing_ok=False!')
        return result

    # # # SUPTITLE # # #
    def plot_suptitle(self):
        '''adds suptitle (as a MovieText node)
        raise PlottingAmbiguityError if suptitle already plotted
            (this prevents having multiple suptitle nodes).
        '''
        if hasattr(self, 'suptitle_node'):
            errmsg = (f'suptitle already plotted; cannot plot it again. '
                      f'For {type(self).__name__}(name={self.name!r}) with id={hex(id(self))}')
            raise PlottingAmbiguityError(errmsg)
        suptitle = self.plot_settings['suptitle']
        if suptitle is UNSET:
            suptitle = self.titles_inferer.infer_suptitle()
        if isinstance(suptitle, str):
            kw_suptitle = {**self.plot_settings.kw, 'init_plot': True}
            suptitle_node = xarray_suptitle_plot_node(self.array, suptitle, t=self.t_plot_dim,
                                                      fig=self.fig, parent=self, **kw_suptitle)
            self.suptitle_node = suptitle_node  # <-- for bookkeeping/debugging

    # # # RTITLES # # #
    def plot_rtitles(self):
        '''adds rtitles (as MovieText node objects) via plot_note() on right-hand-side of right-most images.
        (only if self.plot_settings['rtitle'] is not UNSET.)
        '''
        rtitle = self.plot_settings['rtitle']
        if rtitle is UNSET:
            return
        # else, rtitle was provided.
        rimages = self.rightmost_images(as_idx=False, missing_ok=True)
        font = {'fontfamily': self.plot_settings['title_font'],
                **self.plot_settings.get('title_kw', default={})}['fontfamily']
        rtitle_kw = {'fontfamily': font, **self.plot_settings['rtitle_kw']}
        for image in rimages:
            if image is None:
                continue
            rtitle_text = plot_note(rtitle, ax=image.ax, **rtitle_kw)
            rtitle_node = XarrayText(image.array, rtitle_text, parent=image)
            image.rtitle_node = rtitle_node  # <-- for bookkeeping/debugging

    # # # ARRS FROM INPUTS # # #
    def _get_xarray_arr(self, xarray, row=None, col=None, wrap=None):
        '''return array of xarray.DataArray objects, organized into a grid.
        E.g. when wrap=None, result[i,j] = self.array.isel({row: i, col: j}).
        see help(type(self)) for details on row, col, wrap.
        '''
        if wrap is None:
            # [col, row] order agrees with definition of row & col kwargs.
            result = take_along_dimensions(xarray, [col, row])
        else:  # wrap is not None
            if row is None and col is None:
                raise InputMissingError(f'row or col, when wrap is not None. (got wrap={wrap!r})')
            if row is not None and col is not None:
                errmsg = ('wrap can only be provided if provided row or col but not both. '
                          f'Got wrap={wrap!r}, row={row!r}, col={col!r}')
                raise InputConflictError(errmsg)
            if row is not None:
                result = take_along_dimensions(xarray, row)
                result = wraplist(result, wraprow=wrap)
            else: # col is not None:
                result = take_along_dimensions(xarray, col)
                result = wraplist(result, wrapcol=wrap)
        return result

    # # # VLIMS # # #
    _calculate_vlims = staticmethod(calculate_vlims)

    @PlotSettings.format_docstring(ntab=2)
    def _get_vlims_arr(self, arrs=None, *, vmin=None, vmax=None, share_vlims=False, robust=UNSET):
        '''return array of vmin, vmax, for each array in arrs.
        arrs: None or array of arrays.
            if None, use self.arrs.
        vmin, vmax: None, value, or array-like with same shape as `arrs`
            if provided, use this value for vmin, vmax for all subplots, ignoring share_vlims and robust.
            See help(type(self)) for more details.
        share_vlims: {share_vlims}
        robust: {robust}
        '''
        # [EFF] handle simple edge case first (both non-None scalars):
        if not is_iterable(vmin) and not is_iterable(vmax) and vmin is not None and vmax is not None:
            result = np.empty(arrs.shape, dtype=object)
            for idx, _ in np.ndenumerate(result): result[idx] = (vmin, vmax)
            return result
        # bookkeeping
        if robust is UNSET:
            robust = PlotSettings.get_default('robust')
        if arrs is None:
            arrs = self.arrs 
        if not is_iterable(vmin):
            vmin = np.full(arrs.shape, vmin, dtype=object)
        elif not hasattr(vmin, 'ndim'):
            vmin = np.asarray(vmin)
        if not is_iterable(vmax):
            vmax = np.full(arrs.shape, vmax, dtype=object)
        elif not hasattr(vmax, 'ndim'):
            vmax = np.asarray(vmax)
        def has_None_where_other_doesnt(array0, array1):
            return (None in array0) and any(a0 is None and a1 is not None for a0, a1 in zip(array0.flat, array1.flat))
        result = np.full(arrs.shape, None, dtype=object)  # array of tuples.
        # compute results
        if share_vlims is True or share_vlims=='all':
            if True:  # I just wanted the indentation to match code below...
                avals = [a.values for a in arrs.flat if a is not None]
                kw_vlims = dict(vmin=None if has_None_where_other_doesnt(vmin, arrs) else 0,
                                vmax=None if has_None_where_other_doesnt(vmax, arrs) else 1)
                rmin, rmax = self._calculate_vlims(avals, robust=robust, **kw_vlims, expand_flat=False)
                for idx, _ in np.ndenumerate(result):
                    result[idx] = (rmin if vmin[idx] is None else vmin[idx],
                                   rmax if vmax[idx] is None else vmax[idx])
        elif share_vlims == 'row':
            for i, row in enumerate(arrs):
                avals = [a.values for a in row if a is not None]
                kw_vlims = dict(vmin=None if has_None_where_other_doesnt(vmin[i], row) else 0,
                                vmax=None if has_None_where_other_doesnt(vmax[i], row) else 1)
                rmin, rmax = self._calculate_vlims(avals, robust=robust, **kw_vlims, expand_flat=False)
                for j, _ in enumerate(row):
                    result[i,j] = (rmin if vmin[i,j] is None else vmin[i,j],
                                   rmax if vmax[i,j] is None else vmax[i,j])
        elif share_vlims == 'col':
            for j in range(arrs.shape[1]):
                col = arrs[:, j]
                avals = [a.values for a in col if a is not None]
                kw_vlims = dict(vmin=None if has_None_where_other_doesnt(vmin[:,j], col) else 0,
                                vmax=None if has_None_where_other_doesnt(vmax[:,j], col) else 1)
                rmin, rmax = self._calculate_vlims(avals, robust=robust, **kw_vlims, expand_flat=False)
                for i in range(arrs.shape[0]):
                    result[i,j] = (rmin if vmin[i,j] is None else vmin[i,j],
                                   rmax if vmax[i,j] is None else vmax[i,j])
        elif not share_vlims:
            for idx, arr in np.ndenumerate(arrs):
                if arr is None:
                    result[idx] = (None, None)
                    continue
                avals = arr.values
                kw_vlims = dict(vmin=None if (vmin[idx] is None and arr is not None) else 0,
                                vmax=None if (vmax[idx] is None and arr is not None) else 1)
                rmin, rmax = self._calculate_vlims(avals, robust=robust, **kw_vlims, expand_flat=False)
                result[idx] = (rmin if vmin[idx] is None else vmin[idx],
                               rmax if vmax[idx] is None else vmax[idx])
        else:
            raise InputError(f'invalid share_vlims: {share_vlims}, expected True, False, "all", "row", or "col".')
        return result


    # # # MISC CONVENIENT METHODS # # #
    def scatter_max(self, **kw_scatter):
        '''use XarrayScatter to plt.scatter() a marker at argmax of each subplot image's array.
        animatable (e.g. different max for each frame); for each image, image.add_child(scatter result).
        default style: {**DEFAULTS.PLOT.SCATTER_STYLE, **DEFAULTS.PLOT.SCATTER_MAX}
        returns np.array with same shape as self, containing the results of XarrayScatter calls.
        '''
        results = np.full(self.shape, None, dtype=object)
        for idx, image in ndenumerate_nonNone(self.images):
            results[idx] = image.scatter_max(**kw_scatter)
        return results

    def scatter_min(self, **kw_scatter):
        '''use XarrayScatter to plt.scatter() a marker at argmin of each subplot image's array.
        animatable (e.g. different max for each frame); for each image, image.add_child(scatter result).
        default style: {**DEFAULTS.PLOT.SCATTER_STYLE, **DEFAULTS.PLOT.SCATTER_MAX}
        returns np.array with same shape as self, containing the results of XarrayScatter calls.
        '''
        results = np.full(self.shape, None, dtype=object)
        for idx, image in ndenumerate_nonNone(self.images):
            results[idx] = image.scatter_min(**kw_scatter)
        return results

    def scatter_where(self, condition, **kw_scatter):
        '''use XarrayScatter to plt.scatter() markers where condition is True.
        animatable (e.g. different max for each frame); for each image, image.add_child(scatter result).

        condition: callable or DataArray of bools
            callable --> use condition(arr) for each image in self, where arr=image.array.
            DataArray --> use condition.isel(ii) for each image in self,
                        where ii is the corresponding dict of indices from self.isels.

        returns np.array with same shape as self, containing the results of XarrayScatter calls.

        Example:
            xsubs = array.pc.image(...)
            xsubs.scatter_where(lambda arr: arr > 7.5)  # markers at all values larger than 7.5
            xsubs.save(filename)  # save animation to filename (if xsubs.t_plot_dim is not None)
        '''
        results = np.full(self.shape, None, dtype=object)
        for idx, isel in ndenumerate_nonNone(self.isels):
            image = self.images[idx]
            if image is None:
                continue
            if callable(condition):
                where = condition  # image.scatter_where handles the rest.
            else:
                where = condition.isel(isel, missing_dims='ignore')
            results[idx] = image.scatter_where(where, **kw_scatter)
        return results
