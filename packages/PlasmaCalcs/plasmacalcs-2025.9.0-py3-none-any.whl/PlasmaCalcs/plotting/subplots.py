"""
File purpose: tools related to subplots.
"""
import builtins   # for unambiguous slice()

import numpy as np
import matplotlib.pyplot as plt

from .plot_settings import PlotSettings, PlotSettingsMixin
from .plot_tools import (
    colorbar, _paramdocs_colorbar, find_mappable,
    maintaining_current_axes,
    set_min_n_ticks,
)
from ..tools import (
    simple_property,
    format_docstring,
    UNSET,
)
from ..errors import (
    InputError, InputConflictError,
    MappableNotFoundError, PlottingAmbiguityError, TooManySubplotsError,
)

from ..defaults import DEFAULTS


### --------------------- tools for subplots --------------------- ###

def subplots_figsize(nrows=1, ncols=1, axsize=None, *,
                     left=None, right=None, bottom=None, top=None, wspace=None, hspace=None):
    '''returns figsize to use for subplots so that every subplot has size axsize.
    axsize: None, number, or (width, height)
        size of a single subplot, in inches.
        if None, use DEFAULTS.PLOT.SUBPLOTS_AXSIZE.
        if number, use width=height=axsize.
    left, right, bottom, top, wspace, hspace: None or number (probably between 0 and 1)
        corresponding value that will be used during plt.subplots_adjust;
        figsize must be adjust accordingly to account for whitespace between and around subplots.
        None --> plt.rcParams['figure.subplot.left'], plt.rcParams['figure.subplot.right'], etc.
        left, right, bottom, top: tell position of edge of subplots grid, as fraction of figure width / height.
        wspace, hspace: tell width of padding between subplots, as fraction of axsize width / height.
    '''
    # [TODO] why do I still need to fidget with left/top/bottom to get supxlabel, supylabel, suptitle in good positions?
    # (note: it seems to be especially bad when doing nrow or ncol=1 and the other one being a large value (e.g. 5).)
    if axsize is None:
        axsize = DEFAULTS.PLOT.SUBPLOTS_AXSIZE
    try:
        axwidth, axheight = axsize
    except TypeError:
        axwidth = axheight = axsize
    if left is None: left = plt.rcParams['figure.subplot.left']
    if right is None: right = plt.rcParams['figure.subplot.right']
    assert right > left, "can't make plot when right < left!"
    if bottom is None: bottom = plt.rcParams['figure.subplot.bottom']
    if top is None: top = plt.rcParams['figure.subplot.top']
    assert top > bottom, "can't make plot when top < bottom!"
    if wspace is None: wspace = plt.rcParams['figure.subplot.wspace']
    if hspace is None: hspace = plt.rcParams['figure.subplot.hspace']
    # calculate figsize
    left_margin, right_margin = left, 1 - right
    subplots_width_fraction = 1 - left_margin - right_margin  # fraction of figure width remaining for the subplots
    subplots_width_inches = ((ncols-1)*wspace + ncols)*axwidth
    total_width = subplots_width_inches / subplots_width_fraction
    bottom_margin, top_margin = bottom, 1 - top
    subplots_height_fraction = 1 - bottom_margin - top_margin  # fraction of figure height remaining for the subplots
    subplots_height_inches = ((nrows-1)*hspace + nrows)*axheight
    total_height = subplots_height_inches / subplots_height_fraction
    return (total_width, total_height)
    

### --------------------- Subplots --------------------- ###

@format_docstring(subplots_doc=plt.subplots.__doc__)
def subplots(nrows=1, ncols=1, *, squeeze=False, cls=None, **kw_subplots):
    '''returns a new Subplots object. Like calling plt.subplots(...), but a bit fancier.
    args & kwargs go to Subplots(...), then to plt.subplots(...).

    To avoid ambiguity, squeeze = True is not allowed.
        I.e., the axs will always be 2D, for the resulting Subplots object.

    cls: None or type
        the type to use for the Subplots class.
        None --> use DEFAULTS.PLOT.SUBPLOTS_TYPE
                (which is set inside subplots.py, and might be adjusted by other modules.
                it is probably Subplots or a subclass of Subplots.)

    For reference the docs for plt.subplots:
    ----------------------------------------
    {subplots_doc}
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    if cls is None:
        cls = DEFAULTS.PLOT.SUBPLOTS_TYPE
    return cls(nrows=nrows, ncols=ncols, squeeze=squeeze, **kw_subplots)

@PlotSettings.format_docstring(subplots_doc=plt.subplots.__doc__)
class Subplots(PlotSettingsMixin):
    '''grid of subplots, with methods for plotting on them.

    axsize: {axsize}
    figsize: {figsize}
    {kw_subplots_adjust}
    {kw_share_axlike}
    {kw_share_ax}
    max_nrows_ncols: {max_nrows_ncols}
    squeeze: {squeeze}
    min_n_ticks: {min_n_ticks}

    fig: None or plt.Figure
        if provided, use fig.subplots(...) instead of plt.subplots(...)

    Notes:
        - axs is always 2D, even if nrows=1 or ncols=1.

    Additional kwargs go to plt.subplots.

    For reference, here are the docs from plt.subplots:
    ---------------------------------------------------
    {subplots_doc}
    '''
    axes_class = UNSET

    def __init__(self, nrows=1, ncols=1, *, sharexlike=UNSET, shareylike=UNSET, fig=None, **kw):
        # # plot_settings # #
        super().__init__(nrows=nrows, ncols=ncols, sharexlike=sharexlike, shareylike=shareylike, **kw)
        ps = self.plot_settings
        # max_nrows_ncols:
        max_nrows_ncols = ps['max_nrows_ncols']
        if nrows > max_nrows_ncols or ncols > max_nrows_ncols:
            errmsg = f'nrows={nrows} or ncols={ncols} exceeds the non-None max_nrows_ncols={max_nrows_ncols}.'
            raise TooManySubplotsError(errmsg)
        # squeeze:
        if ps['squeeze']:
            raise InputError('squeeze=True is not allowed for Subplots(...).')
        # sharexlike, shareylike, use same value as sharex, sharey if provided:
        if sharexlike is UNSET and ps['sharex'] is not None:
            ps['sharexlike'] = ps['sharex']
        if shareylike is UNSET and ps['sharey'] is not None:
            ps['shareylike'] = ps['sharey']
        # figsize:
        if ps.get('figsize', default=UNSET) is UNSET:
            subplots_figsize_keys = ('axsize', 'left', 'right', 'bottom', 'top', 'wspace', 'hspace')
            ps['figsize'] = self.subplots_figsize(nrows=nrows, ncols=ncols, **{key: ps[key] for key in subplots_figsize_keys})
        elif ps.get('axsize', default=UNSET) is not UNSET:
            raise InputConflictError('cannot provide both axsize and figsize.')
        # axes_class:
        if (self.axes_class is not None) and ps.get('axes_class', default=None) is None:
            ps['axes_class'] = self.axes_class
        # # make the subplots # #
        kw_fig = ps.get_mpl_kwargs('plt.figure')
        if fig is None:
            fig = plt.figure(**kw_fig)
        kw_subplots = ps.get_mpl_kwargs('fig.subplots')
        if DEFAULTS.DEBUG >= 4:
            print('using kw_subplots', kw_subplots)
        axs = fig.subplots(nrows=nrows, ncols=ncols, **kw_subplots)
        assert axs.ndim == 2, f'expected axs.ndim == 2, got {axs.ndim}. Probably made a coding error...'
        self.fig = fig
        self.axs = axs
        # # cleanup plot formatting # #
        self.subplots_adjust()
        self.remove_redundant_labels(which={x for x in ('x', 'y') if ps[f'share{x}like']==True})
        self.apply_misc_formatting()

    subplots_figsize = staticmethod(subplots_figsize)

    # # # AXS # # #
    axs = simple_property('_axs', doc='''array of axes objects.''')
    @axs.setter  # update axs setter so that setting axs updates self.cache_state too.
    def axs(self, value):
        '''set self._axs=value; also update caching state.'''
        self._axs = value
        self.cache_state += 1

    cache_state = simple_property('_cache_state', default=0, doc='''int, associated with cached results.''')

    shape = property(lambda self: self.axs.shape, doc='''shape of axs array, as (nrows, ncols).''')
    nrows = property(lambda self: self.axs.shape[0], doc='''number of rows in axs array.''')
    ncols = property(lambda self: self.axs.shape[1], doc='''number of columns in axs array.''')

    @property
    def ax_idx(self):
        '''array of indices (irow, icol), with same shape as axs array, dtype=object'''
        try:
            cached_state, cached_result = self._ax_idx
        except AttributeError:
            pass
        else:
            if cached_state == self.cache_state:
                return cached_result
        # else, not found in cache; calculate result
        result = np.empty(self.shape, dtype=object)
        for irow, row in enumerate(self.axs):
            for icol, _ax in enumerate(row):
                result[(irow, icol)] = (irow, icol)
        # store in cache then return
        self._ax_idx = (self.cache_state, result)
        return result

    def __getitem__(self, idx):
        '''return self.axs[idx]'''
        return self.axs[idx]

    def __len__(self):
        '''return len(self.axs)'''
        return len(self.axs)

    # # # ITERATING # # #
    def __iter__(self):
        '''when iterating, return (self.fig, self.axs). To iterate over axs, see self.iter_ax.'''
        return iter((self.fig, self.axs))

    # # # ITER_AX, AX_APPLY # # #
    _iter_ax_paramdocs = {
        'slice': '''None, int, slice, or tuple
            if provided, only include the axes from axs[slice].
            when in this mode, (irow, icol) will still correspond to self.axs[(irow, icol)],
                (not self.axs[slice][irow, icol]).''',
        'sca': '''bool
            if True, call plt.sca(ax) before yielding each ax.''',
        'restore': '''bool
            if True, restore original plt.gca() after iteration is stopped.''',
    }

    def sca(self, irow, icol):
        '''set current axis to self.axs[irow, icol]'''
        plt.sca(self.axs[irow, icol])

    @format_docstring(**_iter_ax_paramdocs)
    def iter_ax(self, slice=None, *, sca=True, restore=True, skip=None):
        '''iterate over axs, one at a time, yielding ((irow, icol), ax) for each ax.
        slice: {slice}
        sca: {sca}
        restore: {restore}
        skip: None or callable of ((irow, icol), ax) --> bool
            if provided, skip axes for which skip(irow, icol, ax) returns True.
        '''
        with maintaining_current_axes(enabled=restore):
            if slice is None:
                slice = builtins.slice(None)
            ax_idx = self.ax_idx[slice]
            for sliced_index, ax in np.ndenumerate(self.axs[slice]):
                ax_idx_here = ax_idx if isinstance(ax_idx, tuple) else ax_idx[sliced_index]
                if skip is None or not skip(ax_idx_here, ax):
                    if sca: plt.sca(ax)
                    yield (ax_idx_here, ax)

    @format_docstring(**_iter_ax_paramdocs)
    def iter_row(self, irow, *, sca=True, restore=True, **kw_iter_ax):
        '''iterate over axs in row irow, yielding ((irow, icol), ax) for each ax. See also: self.iter_ax
        irow: int or slice
            row index(es) to iterate over. Can be negative int, e.g. -1 will be the bottom row.
        {sca}
        {restore}
        '''
        return self.iter_ax(slice=(irow, slice(None)), sca=sca, restore=restore, **kw_iter_ax)

    @format_docstring(**_iter_ax_paramdocs)
    def iter_col(self, icol, *, sca=True, restore=True, **kw_iter_ax):
        '''iterate over axs in column icol, yielding ((irow, icol), ax) for each ax. See also: self.iter_ax
        icol: int or slice
            column index(es) to iterate over. Can be negative int, e.g. -1 will be the rightmost column.
        {sca}
        {restore}
        '''
        return self.iter_ax(slice=(slice(None), icol), sca=sca, restore=restore, **kw_iter_ax)

    def ax_apply(self, f, *, sca=True):
        '''return numpy array of f(ax) applied to each ax. result has dtype=object.
        if sca, call plt.sca() before working on each ax.
        '''
        result = np.empty(self.shape, dtype=object)
        for (irow, icol), ax in self.iter_ax(sca=sca):
            result[(irow, icol)] = f(ax)
        return result

    # # # LABELS # # #
    def xlabel(self, xlabel, mode=None, *, only=True, **kw):
        '''set xlabel on relevant axs, or as supxlabel.
        mode: None or str in ('edge', 'all', 'sup')
            None --> use self.xlabel_mode
            'edge' --> only set xlabel on axs in bottom row
            'all' --> set xlabel on all axs.
            'sup' --> set xlabel on self.fig, as supxlabel.
        only: bool, default True
            if only, then also set xlabel to '' on all other axes.
        kwargs are passed to ax.set_xlabel or fig.supxlabel, as appropriate.
        '''
        if mode is None:
            mode = 'edge' if self.plot_settings['sharexlike'] else 'all'
        if mode=='edge':
            for _, ax in self.iter_row(-1):
                ax.set_xlabel(xlabel, **kw)
            if only:
                for _, ax in self.iter_row(slice(0, -1)): ax.set_xlabel('')
        elif mode=='all':
            for _, ax in self.iter_ax():
                ax.set_xlabel(xlabel, **kw)
        elif mode=='sup':
            self.fig.supxlabel(xlabel, **kw)
            if only:
                for _, ax in self.iter_ax(): ax.set_xlabel('')
        else:
            raise InputError(f'invalid mode: {mode}')

    def ylabel(self, ylabel, mode=None, *, only=True, **kw):
        '''set ylabel on relevant axs, or as supylabel.
        mode: None or str in ('edge', 'all', 'sup')
            None --> use self.xlabel_mode
            'all' --> set ylabel on all axs.
            'sup' --> set ylabel on self.fig, as supylabel.
        only: bool, default True
            if only, then also set ylabel to '' on all other axes.
        kwargs are passed to ax.set_ylabel or fig.supylabel, as appropriate.
        '''
        if mode is None:
            mode = 'edge' if self.plot_settings['shareylike'] else 'all'
        if mode=='edge':
            for _, ax in self.iter_col(0):
                ax.set_ylabel(ylabel, **kw)
            if only:
                for _, ax in self.iter_col(slice(1, None)): ax.set_ylabel('')
        elif mode=='all':
            for _, ax in self.iter_ax():
                ax.set_ylabel(ylabel, **kw)
        elif mode=='sup':
            self.fig.supylabel(ylabel, **kw)
            if only:
                for _, ax in self.iter_ax(): ax.set_ylabel('')
        else:
            raise InputError(f'invalid mode: {mode}')

    def remove_redundant_labels(self, which=['x', 'y'], *, ignore_empty=True):
        '''remove labels which are redundant, e.g. ticklabels,
        ylabels except in left col, xlabels except in bottom row.
        if sharexlike=False or shareylike=False, will not remove the corresponding labels.

        if self.plot_settings['polar'], keep xticklabels (i.e. angles) on top row instead of bottom.

        which: iterable of str in ('x', 'y')
            which labels to remove. Default: ('x', 'y')
        ignore_empty: bool
            whether to ignore empty axes (checked via ax.has_data())
        '''
        for x in which:
            self._remove_redundant_ticklabels(x, ignore_empty=True)
            self._remove_redundant_labels(x, ignore_empty=True)

    def _remove_redundant_ticklabels(self, x, *, ignore_empty=True):
        '''remove x or y ticklabels in self which are redundant, i.e. same across col (if 'x') or row (if 'y').
        x: 'x' or 'y'.
        ignore_empty: bool, whether to ignore axes in this column which have no data.
        '''
        if x not in ('x', 'y'): raise InputError(f'invalid x: {x!r}, expected "x" or "y".')
        _override = self.plot_settings[f'sharexlike'] if x=='x' else self.plot_settings[f'shareylike']
        for iline in (range(self.ncols) if x=='x' else range(self.nrows)):
            if _override is UNSET:
                common = self._get_common_tick_info(x, iline, ignore_empty=ignore_empty)
            else:
                common = (True if _override else None)
            if common is not None:
                axes = self.axs[:, iline][::-1] if x=='x' else self.axs[iline, :]
                if x=='x' and self.plot_settings.get('polar', last_resort_default=False):
                    axes = axes[::-1]
                first_nonempty = True
                for ax in axes:
                    if ignore_empty and not ax.has_data():
                        continue
                    elif first_nonempty:  # don't remove labels from first nonempty ax.
                        first_nonempty = False
                    else:
                        ax.set_xticklabels([]) if x=='x' else ax.set_yticklabels([])

    def _get_common_tick_info(self, x, iline, *, ignore_empty=True):
        '''return the x or y tick_info shared by all nonempty plots in this line, or None if that's impossible.
        tick_info is (xticklocs, xticklabels, xlim) (or y if x='y'), with str xticklabels (not Text objects).
        x: 'x' or 'y'.
        iline: int, index of the line to check. (icol if 'x', irow if 'y')
        ignore_empty: bool, whether to ignore axes in this column which have no data.
        '''
        if x not in ('x', 'y'): raise InputError(f'invalid x: {x!r}, expected "x" or "y".')
        _need0 = True  # flag - still need to find first ax to compare values to.
        axes = self.axs[:, iline] if x=='x' else self.axs[iline, :]
        for ax in axes:
            if ignore_empty and not ax.has_data():
                continue
            ticks_here = ax.get_xticks() if x=='x' else ax.get_yticks()
            _ticklabels = ax.get_xticklabels() if x=='x' else ax.get_yticklabels()
            labels_here = [label.get_text() for label in _ticklabels]
            lims_here = ax.get_xlim() if x=='x' else ax.get_ylim()
            if _need0:
                ticks = ticks_here
                labels = labels_here
                lims = lims_here
                _need0 = False
            else:  # compare to known values
                if not np.array_equal(ticks, ticks_here):
                    return None
                if not all(label==label_here for label, label_here in zip(labels, labels_here)):
                    return None
                if not np.array_equal(lims, lims_here):
                    return None
        if _need0:  # all plots in this row (or column) are empty
            return None
        return (ticks, labels, lims)

    def _remove_redundant_labels(self, x, *, ignore_empty=True):
        '''remove xlabels or ylabels in self which are redundant, i.e. same across col (if 'x') or row (if 'y').
        x: 'x' or 'y'.
        ignore_empty: bool, whether to ignore axes in this column which have no data.
        '''
        if x not in ('x', 'y'): raise InputError(f'invalid x: {x!r}, expected "x" or "y".')
        _override = self.plot_settings['sharexlike'] if x=='x' else self.plot_settings['shareylike']
        for iline in (range(self.ncols) if x=='x' else range(self.nrows)):
            if _override is UNSET:
                common = self._get_common_label(x, iline, ignore_empty=ignore_empty)
            else:
                common = (True if _override else None)
            if common is not None:
                axes = self.axs[:, iline][::-1] if x=='x' else self.axs[iline, :]
                first_nonempty = True
                for ax in axes:
                    if ignore_empty and not ax.has_data():
                        continue
                    elif first_nonempty:  # don't remove labels from first nonempty ax.
                        first_nonempty = False
                    else:
                        ax.set_xlabel('') if x=='x' else ax.set_ylabel('')

    def _get_common_label(self, x, iline, *, ignore_empty=True):
        '''return the x or y label shared by all nonempty plots in this line, or None if that's impossible.
        x: 'x' or 'y'.
        iline: int, index of the line to check. (icol if 'x', irow if 'y')
        ignore_empty: bool, whether to ignore axes in this column which have no data.
        '''
        if x not in ('x', 'y'): raise InputError(f'invalid x: {x!r}, expected "x" or "y".')
        _need0 = True  # flag - still need to find first ax to compare values to.
        axes = self.axs[:, iline] if x=='x' else self.axs[iline, :]
        for ax in axes:
            if ignore_empty and not ax.has_data():
                continue
            label_here = ax.get_xlabel() if x=='x' else ax.get_ylabel()
            if _need0:
                label = label_here
                _need0 = False
            else:  # compare to known values
                if label != label_here:
                    return None
        if _need0:  # all plots in this row (or column) are empty
            return None
        return label

    # # # SUBPLOTS_ADJUST # # #
    @format_docstring(doc=plt.subplots_adjust)
    def subplots_adjust(self, **kw):
        '''plt.subplots_adjust, using values from self.plot_settings by default.
        Note: adjusts the parameters for self.fig, not necessarily plt.gcf().

        plt.subplots_adjust docs:
        -------------------------
        {doc}
        '''
        if self.plot_settings.get('layout') in ('compressed', 'constrained', 'tight'):
            return   # do nothing! subplots_adjust not compatible with this layout.
        kw = self.plot_settings.get_mpl_kwargs('plt.subplots_adjust', **kw)
        return self.fig.subplots_adjust(**kw)

    # # # COLORBAR(S) # # #
    colorbar = staticmethod(colorbar)

    @format_docstring(**_iter_ax_paramdocs)
    @format_docstring(**_paramdocs_colorbar, sub_indent=DEFAULTS.TAB)
    def colorbars_at(self, slice=None, *, sca=False, missing_ok=True, iter_ax='all',
                  location=None, ticks_position=None, pad=None, size=None,
                  kw_add_axes=dict(), **kw_colorbar):
        '''create colorbars for each ax in self.iter_ax(slice), using self.colorbar(...).
        slice: {{slice}}
        sca: bool
            whether to set current axis to the last-created colorbar, after the operation is complete.
            False --> afterwards, plt.gca() will be restored to what it was before this operation began.
        missing_ok: bool
            whether it is okay for some axs to not have a mappable.
        iter_ax: 'all', 'row', or 'col'
            which axes to iterate over.
            slice will be passed to the appropriate iter func. E.g. 'row' --> iter_row(slice, ...)

        The remaining kwargs go to self.colorbar(...):
        {location}
        {ticks_position}
        {pad}
        {size}
        kw_add_axes: dict
            passed to make_cax(..., **kw_add_axes)... which passes it to plt.gcf().add_axes().
        '''
        # [TODO] skip_existing option, to skip axes that already have a colorbar...
        iter_func_lookup = {'all': self.iter_ax, 'row': self.iter_row, 'col': self.iter_col}
        iter_func = iter_func_lookup[iter_ax]
        for _, ax in iter_func(slice, sca=True, restore=(not sca)):
            try:
                cbar = self.colorbar(ax=ax, sca=sca,
                          location=location, ticks_position=ticks_position, pad=pad, size=size,
                          kw_add_axes=kw_add_axes, **kw_colorbar)
            except MappableNotFoundError:
                if missing_ok:
                    pass  # -- we can ignore this error.
                else:
                    raise
            else:
                # formatting
                min_n_ticks = self.plot_settings['min_n_ticks_cbar']
                if min_n_ticks is not None:
                    fail_ok = self.plot_settings['min_n_ticks_cbar_fail_ok']
                    set_min_n_ticks(min_n_ticks, cbar.ax, fail_ok=fail_ok)

    def colorbars_row(self, irow, **kw_colorbars_at):
        '''create colorbars for each ax in row irow, using self.colorbars_at(...).
        Equivalent to self.colorbars_at(irow, iter_ax='row', ...)
        '''
        return self.colorbars_at(irow, iter_ax='row', **kw_colorbars_at)

    def colorbars_col(self, icol, **kw_colorbars_at):
        '''create colorbars for each ax in column icol, using self.colorbars_at(...).
        Equivalent to self.colorbars_at(icol, iter_ax='col', ...)
        '''
        return self.colorbars_at(icol, iter_ax='col', **kw_colorbars_at)

    def colorbars(self, mode='auto', **kw_colorbars_at):
        '''create colorbars for each image in self.
        mode: True, 'auto', 'all', 'row', slice, or tuple
            tells where to create the colorbars.
            True --> use mode='auto'
            'auto' --> infer, by checking which images have equal im.get_clim() and im.cmap.
                       For rows where all image subplots have the same clim and cmap, mode='row'
                       (unless the right-most in row has no image; then use mode='all').
            'all' --> each image gets its own colorbar.
            'row' --> each row gets its own colorbar, at the right-most image in the row.
            slice or tuple --> self.colorbars_at(slice, ...)

            # [TODO] add 'col' option, for horizontal colorbars at top of columns.
            # [TODO] add 'single' option, for one tall colorbar on the right of figure.
            #        [TODO] make_shared_cax() which makes a tall colorbar with same height as multiple axes.
        '''
        if mode is True: mode = 'auto'
        if mode=='auto':
            return self._colorbars_auto(**kw_colorbars_at)
        elif mode=='all':
            return self.colorbars_at(**kw_colorbars_at)
        elif mode=='row':
            return self.colorbars_col(-1, **kw_colorbars_at)
        elif isinstance(mode, (slice, tuple)):
            return self.colorbars_at(mode, **kw_colorbars_at)
        else:
            raise InputError(f'invalid mode: {mode}, expected True, "auto", "all", "row", or a slice or tuple object.')

    def _colorbars_auto(self, **kw_colorbars_at):
        '''create colorbars for each image in self. Equivalent to self.colorbars(mode='auto', ...).
        infer where to put colorbars by checking which images have equal im.get_clim() and im.cmap.
        for rows where all subplots have the same clim and cmap, put colorbar at right.
        '''
        images = self.ax_images()
        row_modes = []
        for row in images:
            first_image = None
            mode = 'all'  # default, unless stuff matches below.
            for i, im in enumerate(row):
                if im is None:
                    if i==len(row)-1:
                        mode = 'all'  # right-most ax has no image --> must use mode='all'
                elif first_image is None:
                    first_image = im  # found the first image!
                elif self.color_scheme_matches(first_image, im):
                    mode = 'row'  # multiple images with same scheme --> can maybe use mode='row'.
                else:
                    mode = 'all'  # not all images in row have same scheme --> use mode='all'.
                    break
            row_modes.append(mode)
        # now, create colorbars according to row_modes.
        for irow, mode in enumerate(row_modes):
            if mode=='all':
                self.colorbars_at((irow, slice(None)), **kw_colorbars_at)
            elif mode=='row':
                self.colorbars_at((irow, -1), **kw_colorbars_at)

    @staticmethod
    def color_scheme_matches(im0, im1):
        '''return whether color for im0 matches color scheme for im1'''
        return im0.get_clim() == im1.get_clim() and im0.cmap == im1.cmap

    # # # MISC FORMATTING # # #
    def apply_misc_formatting(self):
        '''apply misc formatting according to self.plot_settings.'''
        grid = self.plot_settings.get('grid')
        if grid is not UNSET:
            if isinstance(grid, dict):
                self.grid(**grid)
            else:  # bool, hopefully
                self.grid(grid)
        self.set_min_n_ticks()

    def grid(self, *args_grid, **kw_grid):
        '''ax.grid(...) on all axs'''
        for _, ax in self.iter_ax():
            ax.grid(*args_grid, **kw_grid)

    def set_min_n_ticks(self, min_n_ticks=UNSET):
        '''set_min_n_ticks on all axs.
        Use min_n_ticks from self.plot_settings if not provided here.
        '''
        min_n_ticks = self.plot_settings.get('min_n_ticks', min_n_ticks)
        fail_ok = self.plot_settings['min_n_ticks_fail_ok']
        for _, ax in self.iter_ax():
            set_min_n_ticks(min_n_ticks, ax=ax, fail_ok=fail_ok)

    # # # HIDE EMPTY AXES # # #
    def hide_empty_axes(self):
        '''hide axes (ax.set_visible(False)) without any data (check via ax.has_data())'''
        for _, ax in self.iter_ax():
            if not ax.has_data():
                ax.set_visible(False)

    # # # IMAGES # # #
    find_mappable = staticmethod(find_mappable)

    def ax_images(self, *, fill_value=None):
        '''return array of the image on each ax (or fill_value if no image on that ax).'''
        def get_image(ax):
            '''return the image on ax, or None if no image.'''
            try:
                return self.find_mappable(ax=ax)
            except MappableNotFoundError:
                return fill_value
        return self.ax_apply(get_image)

    def iter_images(self):
        '''iterate across axs, yielding ((irow, icol), image) for each ax with an image.
        (axs without image will be skipped.)
        '''
        images = self.ax_images(fill_value=None)
        for (irow, icol), image in np.ndenumerate(images):
            if image is not None:
                yield ((irow, icol), image)

    def ax_cbars(self, *, no_image=None, no_cbar=False):
        '''return array of colorbars associated with images on each ax.
        for ax with no image, value will be `no_image` (default None).
        for ax with image but no colorbar, value will be `no_cbar` (default False).
        '''
        def get_cbar(ax):
            '''return the colorbar on ax, or None if no colorbar.'''
            try:
                result = self.find_mappable(ax=ax)
            except MappableNotFoundError:
                return no_image
            result = getattr(result, 'colorbar', None)
            if result is None:
                return no_cbar
            else:
                return result
        return self.ax_apply(get_cbar)

    def iter_cbars(self):
        '''iterate across axs, yielding ((irow, icol), cbar) for each ax with a colorbar.
        (axs without colorbars will be skipped.)
        '''
        cbars = self.ax_cbars(no_image=None, no_cbar=None)
        for (irow, icol), cbar in np.ndenumerate(cbars):
            if cbar is not None:
                yield ((irow, icol), cbar)

    @property
    def cbars(self):
        '''list of colorbars appearing on any ax across self.
        equivalent: [cbar for ((irow, icol), cbar) in self.iter_cbars()]
        '''
        return [cbar for _, cbar in self.iter_cbars()]
    
    # # # UPDATERS # # #
    def updaters(self, *, fill_value=None):
        '''return array of updaters for each ax (or fill_value if no updater on that ax).'''
        return self.ax_apply(lambda ax: getattr(ax, 'updater', fill_value))

    def set_updater(self, irow, icol, updater):
        '''set updater on ax[irow, icol] to updater'''
        ax = self.axs[irow, icol]
        ax.updater = updater


_dsp = getattr(DEFAULTS.PLOT, 'SUBPLOTS_TYPE', None)
if isinstance(_dsp, type) and issubclass(_dsp, Subplots):
    pass  # don't set DEFAULTS.PLOT in this case; it's already a subclass of Subplots.
else:
    DEFAULTS.PLOT.SUBPLOTS_TYPE = Subplots
