"""
File Purpose: tools related to drawing (and maybe animating) 2D patches.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
import xarray as xr

from .movies import MoviePlotElement, MoviePlotNode
from .plot_settings import PlotSettings
from .plot_tools import plt_transformer
from ..errors import (
    InputError, InputMissingError, InputConflictError,
    PlottingAmbiguityError, DimensionalityError,
)
from ..tools import (
    alias, alias_key_of, alias_child, simple_property,
    UNSET,
    pcAccessor,
    xarray_fill_coords, xarray_ensure_dims,
)


### --------------------- PatchPlotElement & XarrayPatch --------------------- ###

@PlotSettings.format_docstring()
class PatchPlotElement(MoviePlotElement):
    '''plot a 2D Patch.
    Base class for useable 2D patch plot elements, e.g. XarrayRectanglePatchPlotElement.

    params: dict
        dict of patch-related parameters.
        Many are probably settable directly via patch.set(**params).
        E.g. 'width' and 'height' are options for rectangle patch.
    transform: {transform}

    cls.MPL_SETTERS: dict of {{param key: how to set that param}}
        for params with nonstandard setters in matplotlib, tells the alternative to patch.set(k=value):
            {{str k: str v}} --> patch.set(v=value)
            {{str k: (str attr, str v)}} --> patch.attr(v=value)
        Examples:
            - for Annulus patch, need MPL_SETTERS['r'] = 'radii',
                because patch.set(r=value) isn't allowed; it's patch.set(radii=value) instead.
            - for Arrow patch, need MPL_SETTERS['x'] = ('set_data', 'x'),
                because patch.set(x=value) isn't allowed; it's patch.set_data(x=value) instead.
    '''
    patch_cls = NotImplemented  # <-- subclass should specify.
    MPL_SETTERS = {}  # <-- subclass should specify.
    PATCH_SETTINGS_LOOKUP = 'mpl.patches.Patch'  # <-- subclass should update.

    def __init__(self, params, *, ax=None, transform=UNSET, **kw_super):
        kw_super.update(transform=transform)
        super().__init__(**kw_super)
        self._ax_init = ax
        self.params = params
        self.init_patch()

    def _params_to_patch_init_kwargs(self, params):
        '''returns kwargs to use for initializing the patch, based on these params.
        The implementation here just returns params, unchanged.
        Subclass might override (e.g. RectanglePatchPlotElement join 'x0' and 'y0' into 'xy').
        The result should be a dict of kwargs suitable for self.patch_cls.__init__.
        '''
        return params

    def _params_to_patch_update_kwargs(self, params):
        '''returns kwargs to use for updating the patch, based on these params.
        The implementation here just returns params, unchanged.
        Subclass might override (e.g. RectanglePatchPlotElement rename 'x0' to 'x' and 'y0' to 'y').
        The result should be a dict of kwargs suitable for self._set_patch_params
            (i.e., before applying logic due to MPL_SETTERS).
        '''
        return params

    params = alias_key_of('data', 'params',
        doc='''dict of patch parameters. Internally, stored at self.data['params']''')
    patch = simple_property('_patch', doc='''the matplotlib.patches.Patch object''')
    ax = alias_child('patch', 'axes', if_no_child=None, doc='''the axes containing this patch''')
    fig = alias_child('patch', 'figure', if_no_child=None, doc='''the figure containing this patch''')

    def _all_patch_params(self, ax):
        '''returns full list of all known patch params to use, i.e.:
        {**params_settings, **params_init}, where:
            params_settings = self.plot_settings.get_mpl_kwargs(self.PATCH_SETTINGS_LOOKUP)
            params_init = self._params_to_patch_init_kwargs()
        '''
        params_settings = self.plot_settings.get_mpl_kwargs(self.PATCH_SETTINGS_LOOKUP)
        params_init = self._params_to_patch_init_kwargs(self.params)
        params_transform = self._transform_kw(ax=ax)
         # settings first in order below --> other params takes precedence if overlap.
        return {**params_settings, **params_init, **params_transform}

    def _transform_kw(self, ax):
        '''get transform to use for this patch, as dict.
        result is probably dict(transform=Transform object), but might be empty dict().
        requires that self.ax is not None.
        '''
        transform = self.plot_settings['transform']
        if transform is UNSET:
            return {}
        transform = plt_transformer(transform, ax=ax)
        return {'transform': transform}

    # # # PLOTTING THIS ELEMENT # # #
    def init_patch(self):
        '''initialize the patch; actually draw the patch on self.ax.
        stores plotted object in self.patch and returns self.patch.
        '''
        ax = self._ax_init
        if ax is None: ax = plt.gca()
        kw_patch = self._all_patch_params(ax=ax)
        self.patch = self.patch_cls(**kw_patch)
        ax.add_patch(self.patch)
        return self.patch

    # # # UPDATING (REQUIRED BY PARENT) # # #
    def update_data(self, data):
        '''updating the plot using data['params'].
        return the list of all updated matplotlib Artist objects (i.e., [self.patch])
        '''
        params = data['params']
        params = self._params_to_patch_update_kwargs(params)
        self._set_patch_params(**params)
        self.params = {**self.params, **params}  # bookkeeping
        return [self.patch]

    def _set_patch_params(self, **params):
        '''update the parameters of self.patch.

        params: dict
            dict of patch parameters.
            All must be provideable during (type of patch).__init__.
            Many are probably settable directly via patch.set(**params).
            E.g. 'width' and 'height' are options for rectangle patch.
            Some might not be settable directly; see self.MPL_SETTERS and help(self) for details.
        '''
        to_set = {}
        for k, value in params.items():
            if k in self.MPL_SETTERS:
                v = self.MPL_SETTERS[k]
                if isinstance(v, tuple):
                    attr, v = v
                    setter = getattr(self.patch, attr)
                    setter(**{v: value})
                else:
                    to_set[v] = value
            else:
                to_set[k] = value
        self.patch.set(**to_set)

    # # # CONENIENCE # # #
    def legend_handle(self, *, hatch_density_scaling=2, label=UNSET):
        '''returns a Patch suitable for use as a handle in a legend.
        
        hatch_density_scaling: int
            increase the hatch density by this factor, relative to the plot itself, if using hatches.
        label: UNSET or str
            if not UNSET, use this as the label, instead of self.plot_settings['label']

        Example:
            handle1 = self.legend_handle()
            handle2 = other_patch_element.legend_handle()
            plt.legend(handles=[handle1, handle2])
        '''
        kw = self.plot_settings.get_mpl_kwargs('mpl.patches.Patch', label=label)
        # intentionally hard-coded 'mpl.patches.Patch' here; legend doesn't care about Patch subclass params.
        if 'hatch' in kw:
            kw['hatch'] = kw['hatch'] * hatch_density_scaling
        return mpl_patches.Patch(**kw)


@PlotSettings.format_docstring()
class XarrayPatch(MoviePlotNode):
    '''MoviePlotNode of 2D patch.
    stores a PatchPlotElement * has methods for plotting & updating it.
    "patch" refers to a matplotlib.patches.Patch object.

    ds: xarray.Dataset, probably 0D or 1D.
        xarray Dataset containing the patch params to be plotted.
        if ndim=0, can still plot, but nothing to animate.
        patch pa
    t: None or str
        the array dimension which frames will index. E.g. 'time'.
        None --> infer from ds.dims. (if ds is 1D, use t=ds.dims[0]).
    ax: None or Axes
        the attached mpl.axes.Axes object.
        None --> will use self.ax=plt.gca() when getting self.ax for the first time.

    init_plot: {init_plot}
    label: {label}

    additional kwargs can contain constant patch params with same key as in matplotlib,
        but only if not provided in ds. E.g. 'edgecolor', but only if no ds['edgecolor'].
    additional kwargs can also be any other PlotSettings.
    '''
    element_cls = PatchPlotElement
    PATCH_SETTINGS_LOOKUP = 'pc.PatchPlotElement'

    def __init__(self, ds, t=None, ax=None,
                 init_plot=PlotSettings.default('init_plot'),  # <- could go in kw_super, but explicit is nice.
                 **kw_super):
        if isinstance(ds, xr.DataArray):
            ds = ds.to_dataset()
        ds = xarray_fill_coords(ds, need=[t])
        ds = xarray_ensure_dims(ds, ({t} - {None}), promote_dims_if_needed=True)
        self.ds = ds
        self._ax_init = ax
        if len(ds.dims) > 1:
            raise DimensionalityError(f'XarrayPatch expects 0D or 1D input, got dims: {ds.dims}')
        if t is None and len(ds.dims) == 1:
            t = list(ds.dims)[0]
        self.t = t
        # super init
        kw_super.update(init_plot=init_plot)
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    t_plot_dim = alias('t')

    ax = alias_child('obj', 'ax', if_special_child={None: None, UNSET: None},
        doc='''mpl.axes.Axes where this XarrayPatch is plotted, or None if not plotted.''')

    fig = alias_child('ax', 'figure', if_special_child={None: None, UNSET: None},
        doc='''mpl.figure.Figure where this XarrayPatch is plotted, or None if not plotted.''')

    patch = alias_child('obj', 'patch', if_special_child={None: None, UNSET: None},
        doc='''mpl.patches.Patch object of this XarrayPatch, or None if not plotted.''')

    legend_handle = alias_child('obj', 'legend_handle',
        doc='''alias to self.obj.legend_handle;
        method which returns a Patch suitable for use as a handle in a legend.
        (implied handles are sometimes okay, but this is useful to increase hatch density if using hatches.)''')

    # # # PLOTTING METHODS (REQUIRED BY PARENT CLASS) # # #
    def init_plot(self):
        '''plot for the first time. Save the PatchPlotElement in self.obj.'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs(self.PATCH_SETTINGS_LOOKUP)
        # ensure no overlap with data['params'].
        if any(k in kw_plot for k in data['params']):
            overlap = set(kw_plot.keys()) & set(data['params'].keys())
            raise PlottingAmbiguityError(f"some XarrayPatch kwargs also found in ds: {overlap}")
        # >> actually plot the patch <<
        self.obj = self.element_cls(data['params'], ax=self._ax_init, **kw_plot)
        # bookkeeping
        self.frame = frame

    def get_data_at_frame(self, frame):
        '''returns {'params': params at this frame}.'''
        t = self.t_plot_dim
        ds = self.ds
        if t is not None:
            ds = ds.isel({t: frame})
        result = {}
        for k, v in ds.items():  # loop instead of list comprehension, helps with debugging.
            result[k] = v.item()
        return {'params': result}

    def get_nframes_here(self):
        '''return the number of frames that could be in the movie, based on this node.'''
        t = self.t_plot_dim
        if t is None:
            return 1
        return len(self.ds.coords[t])


### --------------------- RectanglePatchPlotElement & XarrayRectanglePatch --------------------- ###

@PlotSettings.format_docstring()
class RectanglePatchPlotElement(PatchPlotElement):
    '''plot a rectangle patch.

    params: dict
        dict of any rectangle patch related parameters.
        must contain 'x0' and 'y0'.
        rectangle params are 'x0', 'y0', 'width', 'height'.
        (x0 and y0 point to lower left corner unless negative width or height.
            units determined by `transform`; default data units.)
    transform: {transform}

    'height' and 'width' may either be specified via `params` or as additional kwargs.
    Additional kwargs can be any patch params (with same key as in matplotlib) or PlotSettings.
    E.g. 'angle', 'facecolor', 'hatch'.

    See also: XarrayRectanglePatch, LimsPatchPlotElement
    '''
    patch_cls = mpl_patches.Rectangle
    _MPL_REQUIRED_PARAMS = ('xy', 'width', 'height')  # <-- this is just a note for bookkeeping purposes...
    PATCH_SETTINGS_LOOKUP = 'pc.RectanglePatchPlotElement'

    def _params_to_patch_init_kwargs(self, params):
        '''returns kwargs to use for initializing the patch, based on these params.
        The implementation here joins 'x' and 'y' into 'xy', but keeps other params unchanged.
        '''
        params = params.copy()
        x = params.pop('x0')
        y = params.pop('y0')
        return {'xy': (x, y), **params}

    def _params_to_patch_update_kwargs(self, params):
        '''returns kwargs to use for updating the patch, based on these params.
        The implementation here renames 'x0' and 'y0' to 'x' and 'y', but keeps other params unchanged.
        '''
        params = super()._params_to_patch_update_kwargs(params).copy()
        x = params.pop('x0')
        y = params.pop('y0')
        return {'x': x, 'y': y, **params}


@pcAccessor.register('rectangle_patch')
@PlotSettings.format_docstring()
class XarrayRectanglePatch(XarrayPatch):
    '''MoviePlotNode of 2D rectangle.
    stores a RectanglePatchPlotElement and has methods for plotting & updating it.

    ds: xarray.Dataset, probably 0D or 1D.
        xarray Dataset containing the rectangle params to be plotted.
        if ndim=0, can still plot, but nothing to animate.
        rectangle params are 'x0', 'y0', 'width', 'height'.
        (x0 and y0 point to lower left corner unless negative width or height.
            units determined by transform; default data units.)
    t: None or str
        the array dimension which frames will index. E.g. 'time'.
        None --> infer from ds.dims. (if ds is 1D, use t=ds.dims[0]).
    ax: None or Axes
        the attached mpl.axes.Axes object.
        None --> will use self.ax=plt.gca() when getting self.ax for the first time.
    transform: {transform}

    init_plot: {init_plot}
    label: {label}

    additional kwargs can contain constant rectangle params with same key as in matplotlib,
        but only if not provided in ds. E.g. 'edgecolor', but only if no ds['edgecolor'].
    additional kwargs can also be any other PlotSettings.

    See also: XarrayLimsPatch
    '''
    element_cls = RectanglePatchPlotElement
    PATCH_SETTINGS_LOOKUP = 'pc.RectanglePatchPlotElement'


### --------------------- LimsPatchPlotElement & XarrayLimsPatch --------------------- ###


@PlotSettings.format_docstring()
class LimsPatchPlotElement(RectanglePatchPlotElement):
    '''plot a rectangle patch, from xmin, xmax, ymin, ymax, instead of x0, y0, width, height.

    params: dict
        dict of any rectangle patch related parameters.
        must contain ('xmin' and 'xmax') and/or ('ymin' and 'ymax').
        units determined by `transform`; default 'data' units.
        if xlims not provided, transform[0] must allow 'axes' units (will put 0 to 1, i.e. fill horizontally)
        if ylims not provided, transform[1] must allow 'axes' units (will put 0 to 1, i.e. fill vertically)
        (if transform restricted above but not input directly,
            default to 'axes' units where necessary, and 'data' units elsewhere.)
    transform: {transform}

    See also: XarrayLimsPatch, RectanglePatchPlotElement
    '''
    def _params_to_lims_and_transform(self, params):
        '''get (xmin, xmax, ymin, ymax, transform), from dict of params,
        and self.plot_settings['transform']
        '''
        transform = self.plot_settings.get('transform', params.get('transform', UNSET))
        if isinstance(transform, str):
            transform = (transform, transform)
        xmin = params.get('xmin', None)
        xmax = params.get('xmax', None)
        ymin = params.get('ymin', None)
        ymax = params.get('ymax', None)
        if (xmin is None) != (xmax is None):
            raise InputError(f'provide both xmin and xmax, or neither of them. Got xmin={xmin}, xmax={xmax}')
        if (ymin is None) != (ymax is None):
            raise InputError(f'provide both ymin and ymax, or neither of them. Got ymin={ymin}, ymax={ymax}')
        if xmin is None and ymin is None:
            raise InputMissingError('LimsPatchPlotElement requires at least one of xmin, xmax, ymin, ymax')
        if xmin is None:  # and ymin is not None
            if transform is UNSET:
                transform = ('axes', 'data')
            elif transform[0] != 'axes':
                raise InputConflictError('xmin and xmax not provided, but transform[0] is not "axes"')
            xmin = 0
            xmax = 1
        if ymin is None:
            if transform is UNSET:
                transform = ('data', 'axes')
            elif transform[1] != 'axes':
                raise InputConflictError('ymin and ymax not provided, but transform[1] is not "axes"')
            ymin = 0
            ymax = 1
        return (xmin, xmax, ymin, ymax, transform)

    def _params_to_patch_init_kwargs(self, params):
        '''returns kwargs to use for initializing the patch, based on self.params.
        The implementation converts xmin, xmax, ymin, ymax, into x0, y0, width, height,
            then calls super()._params_to_patch_init_kwargs() on the result.
        The implementation here also sets self.plot_settings['transform'].
        '''
        xmin, xmax, ymin, ymax, transform = self._params_to_lims_and_transform(params)
        width = xmax - xmin
        height = ymax - ymin
        x0 = xmin
        y0 = ymin
        params = params.copy()
        [params.pop(k, None) for k in ('xmin', 'xmax', 'ymin', 'ymax', 'transform')]
        params.update({'x0': x0, 'y0': y0, 'width': width, 'height': height})
        self.plot_settings['transform'] = transform
        return super()._params_to_patch_init_kwargs(params)

    def _params_to_patch_update_kwargs(self, params):
        '''returns kwargs to use for updating the patch, based on self.params.
        The implementation converts xmin, xmax, ymin, ymax, into x0, y0, width, height,
            then calls super()._params_to_patch_update_kwargs() on the result.
        '''
        xmin, xmax, ymin, ymax, _transform = self._params_to_lims_and_transform(params)
        width = xmax - xmin
        height = ymax - ymin
        x0 = xmin
        y0 = ymin
        params = params.copy()
        [params.pop(k, None) for k in ('xmin', 'xmax', 'ymin', 'ymax', 'transform')]
        params.update({'x0': x0, 'y0': y0, 'width': width, 'height': height})
        # <-- do NOT adjust params['transform'] here.
        return super()._params_to_patch_update_kwargs(params)


@pcAccessor.register('lims_patch')
@PlotSettings.format_docstring()
class XarrayLimsPatch(XarrayRectanglePatch):
    '''MoviePlotNode of 2D rectangle, from xmin, xmax, ymin, ymax, instead of x0, y0, width, height.
    stores a LimsPatchPlotElement and has methods for plotting & updating it.

    ds: xarray.Dataset, probably 0D or 1D.
        xarray Dataset containing the rectangle params to be plotted.
        must contain ('xmin' and 'xmax') and/or ('ymin' and 'ymax').
        units determined by `transform`; default 'data' units.
        if xlims not provided, transform[0] must allow 'axes' units (will put 0 to 1, i.e. fill horizontally)
        if ylims not provided, transform[1] must allow 'axes' units (will put 0 to 1, i.e. fill vertically)
        (if transform restricted above but not input directly,
            default to 'axes' units where necessary, and 'data' units elsewhere.)
    t: None or str
        the array dimension which frames will index. E.g. 'time'.
        None --> infer from ds.dims. (if ds is 1D, use t=ds.dims[0]).
    ax: None or Axes
        the attached mpl.axes.Axes object.
        None --> will use self.ax=plt.gca() when getting self.ax for the first time.
    transform: {transform}

    init_plot: {init_plot}
    label: {label}

    additional kwargs can contain constant rectangle params with same key as in matplotlib,
        but only if not provided in ds. E.g. 'edgecolor', but only if no ds['edgecolor'].
    additional kwargs can also be any other PlotSettings.

    See also: XarrayRectanglePatch

    Example:
        ds = xr.Dataset(dict(xmin=2.5, xmax=3.7))
        ds.pc.lims_patch(hatch='//', edgecolor='red', linewidth=0, facecolor='none')
        # produces a red hatched pattern between xmin=2.5 and xmax=3.7, with no outline and no fill, 
        #    extending from bottom to top of the axes.

        ds = xr.Dataset(dict(ymin=0.5, ymax=0.7), transform='axes')
        ds.pc.lims_patch(alpha=0.5)
        # produces a translucent rectangle between 50% and 70% of the way up the axes,
        #    extending from left to right of the axes.

        xx = pc.xr1d([2.5, 2.6, 2.7, 2.8, 2.9, 3.0], name='grid')
        ds = xr.Dataset(dict(xmin=xx, xmax=3.7))
        rect = ds.pc.lims_patch()
        rect.ani()  # or, xrect.save() to save to file instead of viewing in-line in Jupyter
        # produces an animation of rectangle gradually getting thinner (across 6 animation frames),
        #   spanning from x=2.5 to x=3.7 at first, but x=3.0 to x=3.7 by the end of the animation.
        # note: to attach this animation to an already existing PlasmaCalcs animation,
        #   e.g. xim=arr.image(), just add this MoviePlotNode to the tree, e.g. xim.add_child(rect).
    '''
    element_cls = LimsPatchPlotElement
