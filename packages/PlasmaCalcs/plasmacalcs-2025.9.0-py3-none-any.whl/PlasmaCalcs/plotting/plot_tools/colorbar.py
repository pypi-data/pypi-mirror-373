"""
File purpose: tools related to colorbar (see also: colors.py)
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colorbar as cbar

from ..plot_settings import PlotSettings
from ...tools import format_docstring, UNSET
from ...errors import MappableNotFoundError, PlottingAmbiguityError
from ...defaults import DEFAULTS


_paramdocs_colorbar = {
    'ax': '''ax: None or axes object
        the axes which will inform the size and position for cax.
        None --> use plt.gca()''',
    'mappable': '''mappable: None or mpl.cm.ScalarMappable
        the mappable for this colorbar.
        if None, attempt to find it using find_mappable(ax=ax, im=mappable).''',
    'cax': '''cax: None or axes object
        the axes for this colorbar.
        None --> use make_cax(...), or make cax using mpl_get_cax(...), depending on cax_mode.''',
    'location': f'''location: None, 'right', 'left', 'top', or 'bottom'
        location of colorbar relative to image.
        None --> use DEFAULTS.PLOT.CAX_LOCATION (default: {DEFAULTS.PLOT.CAX_LOCATION})''',
    'sca': '''sca: bool (default False)
        whether to adjust the plt.gca() to cax.
        False --> plt.gca() will be unchanged by this operation.''',
    'ticks_position': '''ticks_position: None (default), 'right', 'left', 'top', or 'bottom'
        None -> ticks are on opposite side of colorbar from image.
        string -> use this value to set ticks position.''',
    'pad': f'''pad: None or number (default 0.01)
        padding between cax and ax, as a percentage of ax size.
        None --> use DEFAULTS.PLOT.CAX_PAD (default: {DEFAULTS.PLOT.CAX_PAD})''',
    'size': f'''size: None or number (default 0.02)
        size of colorbar, as a percentage of ax size.
        None --> use DEFAULTS.PLOT.CAX_SIZE (default: {DEFAULTS.PLOT.CAX_SIZE})''',
}


### --------------------- making a colorbar - helper functions --------------------- ###

@format_docstring(**_paramdocs_colorbar)
def make_cax(ax=None, location=None, *, sca=False, ticks_position=None,
             pad=None, size=None, **kw_add_axes):
    ''' Creates an axis appropriate for putting a colorbar. Does not "steal" space; makes a new axis.
    This means the colorbar will appear to be the appropriate size even when using aspect='equal',
    however it might seem to have some placement issues if using sharex=True or sharey=True.

    Troubleshooting... if colorbar appears cutoff, off the side of the figure (e.g. if making a movie),
        you might want to use plt.subplots_adjust(right=0.8 (or smaller)),
        to ensure the colorbar actually technically appears within the figure's bbox.
        (Or top=0.8 (or smaller), or left or bottom=0.2 (or larger), depending on cbar location.)

    {ax}
    {location}
        Note: you will still want to set orientation appropriately, via location or orientation.
    {sca}
    {ticks_position}
        Note: you will still want to set colorbar orientation appropriately, via location or orientation.
        NOTE: for horizontal colorbars, the ticks_position may be overriden by the plt.colorbar() call.
    {pad}
    {size}

    additional kwargs go to plt.gcf().add_axes(...)

    Adapted from https://stackoverflow.com/a/56900830.
    Returns cax.
    '''
    if pad is None: pad = DEFAULTS.PLOT.CAX_PAD
    if size is None: size = DEFAULTS.PLOT.CAX_SIZE
    if location is None: location = DEFAULTS.PLOT.CAX_LOCATION
    if ax is None:
        ax = plt.gca()
    p = ax.get_position()
    # calculate cax params.
    ## fig.add_axes(rect) has rect=[x, y, w, h],
    ## where x and y are location for lower left corner of axes.
    ## and w and h are width and height, respectively.
    assert location in ('right', 'left', 'top', 'bottom')
    if location in ('right', 'left'):
        y = p.y0
        h = p.height
        w = size
        if location == 'right':
            x = p.x1 + pad
        else: #'left'
            x = p.x0 - pad - w
    else: #'top' or 'bottom'
        x = p.x0
        w = p.width
        h = size
        if location == 'top':
            y = p.y1 + pad
        else: #'bottom'
            y = p.y0 - pad - h

    # make the axes
    ax0 = plt.gca()
    try:
        cax = plt.gcf().add_axes([x, y, w, h], **kw_add_axes)
    finally:
        if not sca:  # (don't set sca to colorbar, i.e., need to restore ax0.)
            plt.sca(ax0)
    
    # Change ticks position
    if ticks_position is None:
        ticks_position = location
    if ticks_position in ('left', 'right'):
        cax.yaxis.set_ticks_position(ticks_position)
    else: #'top' or 'bottom'
        cax.xaxis.set_ticks_position(ticks_position)

    return cax

def find_mappable(ax=None, *, im=None):
    '''return the relevant mappable. By default, return plt.gci().
    if plt.gci() is None, instead attempt to find a mappable on plt.gca();
        if there is exactly 1, return it, else raise PlottingError.
        the error will be MappableNotFoundError if 0, else PlottingAmbiguityError.

    providing im uses im instead of plt.gci()
    providing ax using ax instead of plt.gca()  (only if didn't provide im)
    
    ax: None or axes object
        if provided, use ax.findobj to find mappable.
        (cannot provide both ax and im)
        if None, check plt.gci() first, then use findobj if that is also None.
    im: None or mappable.
        if provided, return it.
        if None, attempt plt.gci(); returning it if that is not None
    '''
    if (ax is None) and (im is None):
        im = plt.gci()
    elif (ax is not None) and (im is not None):
        raise ValueError('cannot provide both ax and im.')
    if im is not None:
        return im
    # else, im and plt.gci() are both None, so attempt to find mappable on ax.
    if ax is None:
        _ax_used = 'plt.gca()'  # for more informative error string, if necessary
        ax = plt.gca()
    else:
        _ax_used = 'ax provided'  # for more informative error string, if necessary
    search = ax.findobj(lambda obj: isinstance(obj, mpl.cm.ScalarMappable))
    if len(search)==0:
        raise MappableNotFoundError(f'plt.gci()=None, and no mappable found on {_ax_used}.')
    elif len(search)>1:
        raise PlottingAmbiguityError(f'multiple mappables found on axes: {search}')
    else:
        return search[0]

def mpl_get_cax(mappable, *, cax=None, ax=None, use_gridspec=True, **kwargs):
    '''get the cax to use for a colorbar, using the same logic as plt.colorbar().
    (This is adapted from copy-pasting the source code from plt.colorbar().'''
    if cax is not None:
        return cax
    if ax is None:
        ax = getattr(mappable, "axes", None)
    if ax is None:
        raise ValueError(
            'Unable to determine Axes to steal space for Colorbar. '
            'Either provide the *cax* argument to use as the Axes for '
            'the Colorbar, provide the *ax* argument to steal space '
            'from it, or add *mappable* to an Axes.')
    fig = (  # Figure of first axes; logic copied from make_axes.
        [*ax.flat] if isinstance(ax, np.ndarray)
        else [*ax] if np.iterable(ax)
        else [ax])[0].figure
    current_ax = fig.gca()
    if (fig.get_layout_engine() is not None and
            not fig.get_layout_engine().colorbar_gridspec):
        use_gridspec = False
    if (use_gridspec
            and isinstance(ax, mpl.axes._base._AxesBase)
            and ax.get_subplotspec()):
        cax, kwargs = cbar.make_axes_gridspec(ax, **kwargs)
    else:
        cax, kwargs = cbar.make_axes(ax, **kwargs)
    # make_axes calls add_{axes,subplot} which changes gca; undo that.
    fig.sca(current_ax)
    cax.grid(visible=False, which='both', axis='both')
    return cax

### --------------------- Colorbar and colorbar --------------------- ###
# Colorbar is the colorbar class here (like Colorbar from matplotlib but with more convenience);
# colorbar is like plt.colorbar but creates an instance of this Colorbar class.

class Colorbar(mpl.colorbar.Colorbar):
    '''matplotlib.colorbar.Colorbar class with more methods.
    use Colorbar.here(...) to create a colorbar if cax and/or mappable not known.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, cax, mappable, *args_super, **kw_super):
        super().__init__(cax, mappable, *args_super, **kw_super)

    find_mappable = staticmethod(find_mappable)

    @classmethod
    @PlotSettings.format_docstring(**_paramdocs_colorbar, sub_indent=DEFAULTS.TAB)
    def here(cls, mappable=None, *, cax=None, ax=None, cax_mode=UNSET,
             location=None, sca=False, ticks_position=None,
             pad=None, size=None, kw_add_axes=dict(), **kw_colorbar):
        '''create a colorbar, like plt.colorbar(), but using Colorbar class instead.
        {mappable}
        {cax}
            kwargs for make_cax would be:
                ax, location, sca, ticks_position, pad, size, **kw_add_axes.
        cax_mode: {cax_mode}
        {location}
            also passed to super().__init__, so that orientation is set appropriately.

        The following are relevant if cax not provided, and using cax_mode='mpl':
        {sca}
        {ticks_position}
        {pad}
        {size}
        kw_add_axes: dict
            passed to make_cax(..., **kw_add_axes)... which passes it to plt.gcf().add_axes().

        additional kwargs get passed to matplotlib.colorbar.Colorbar.__init__.
        '''
        if mappable is None:
            mappable = cls.find_mappable(ax=ax, im=mappable)
        if location is None:
            location = DEFAULTS.PLOT.CAX_LOCATION
        if cax is None:
            cax_mode = PlotSettings(cax_mode=cax_mode).get('cax_mode')
            if cax_mode == 'pc':
                cax = make_cax(ax=ax, location=location, sca=sca, ticks_position=ticks_position,
                               pad=pad, size=size, **kw_add_axes)
            elif cax_mode == 'mpl':
                # get the relevant kwargs; PlotSettings knows how to do it, so we can just pass all the kwargs.
                kw = PlotSettings.cls_get_mpl_kwargs('plt.colorbar',
                            cax=cax, ax=ax, cax_mode=cax_mode, location=location,
                            sca=sca, ticks_position=ticks_position, pad=pad, size=size,
                            kw_add_axes=kw_add_axes, **kw_colorbar)
                # PlotSettings doesn't know how to handle converting None to rcParams defaults..
                if 'pad' in kw and kw['pad'] is None: del kw['pad']
                # actually get the cax:
                cax = mpl_get_cax(mappable, **kw)
        return cls(cax, mappable, **kw_colorbar)

    # # # MISC. PROPERTIES # # #
    label = property(lambda self: self.get_label(),
                     lambda self, value: self.set_label(value),
                     doc='''the label on this colorbar. Works regardless of orientation.''')
    def get_label(self):
        '''return the label on this colorbar.'''
        return self.ax.get_ylabel() if (self.orientation=='vertical') else self.ax.get_xlabel()


@format_docstring(doc_here=Colorbar.here.__doc__)
def colorbar(mappable=None, *, cax=None, ax=None,
             location=None, size=None, pad=None, **kw_colorbar_here):
    '''{doc_here}'''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    return Colorbar.here(mappable=mappable, cax=cax, ax=ax,
                         location=location, size=size, pad=pad,
                         **kw_colorbar_here)
