"""
File purpose: manage plot settings & kwargs, to make the other code more readable

Note that the code here doesn't enforce any particular values or relationships for kwargs,
it just makes it easier to manage kwargs & docs for all these settings.

[TODO] add list of kwargs for mpl funcs as options in format_docstring.
E.g. want to say "additional kwargs go to FuncAnimation.save, particularly: {list of kwargs}"
"""

import inspect
import textwrap

import matplotlib.pyplot as plt

from ..errors import InputError, InputConflictError, PlotSettingsError
from ..tools import (
    UNSET, NO_VALUE, RESULT_MISSING,
    format_docstring,
)
from ..defaults import DEFAULTS


# # # DEFAULT SETTINGS FOR PLOTS # # #
DEFAULT_PLOT_SETTINGS = {
    # key: (default, type, docstring, (key in DEFAULTS; optional))
    # will all be converted to PlotSetting instances.

    # key: [subkeys, type, docstring, (key in DEFAULTS; optional)]
    # will all be converted to SharedPlotSetting instances.

    # # # GENERIC # # #
    'dpi': (UNSET, "UNSET, None, or number",
        """dots per inch... used by various matplotlib functions.""",
        ),
    # # # PLOT LIMITS / MARGINS # # #
    'kw_ax_lim': [
        ('xlim', 'ylim'),
            (None, "None or 2-tuple of None or number",
            """plt.xlim / plt.ylim for each plot. None --> don't adjust plot limits."""),
        ],
    'kw_ax_margin': [
        ('xmargin', 'ymargin', 'margin'),
            (None, "None or number (greater than -0.5, probably close to 0.05)",
            r"""margin to use for x/y axis, as a fraction of the data interval for that axis.
            None --> use matplotlib defaults
                    (e.g., plt.rcParams["axes.xmargin"] or ["axes.ymargin"], or 0 if using imshow)
            positive number --> pad around the data region, with this much whitespace.
                    E.g. 0.05 means adding 5% whitespace on each side.
                    Use this to zoom out.
            negative number --> remove this much of the outer parts of the data region.
                    E.g. -0.2 means removing 20% space from each side.
                    Use this to zoom in.
            For line plots, if also using `robust`, ymargin will be applied to the robust y lims.
            (margin-related params share the same docstring, but refer to:
                'xmargin': x-axis, 'ymargin': y-axis, 'margin': x and/or y-axis.)""",),
        ],
    'robust': (UNSET, "UNSET, bool, or number between 0 and 50",
        """use np.percentile when determining vmin/vmax, if robust.
        For imshow/image plots, this refers to colorbar lims; for line plots, this refers to y lims.
        UNSET --> use {default}.
        False --> just use min and max of values, don't use percentile.
        True --> use {defaults_dict_True}
        number --> use np.percentile with this percentile for vmin (and 100 - this percentile for vmax).""",
        ('DEFAULTS.PLOT.ROBUST', {True: 'DEFAULTS.PLOT.ROBUST_PERCENTILE'}),
        ),
    'ybounds': (None, "None, False, or 2-tuple/iterable of [max_ymin, min_ymax]",
        """tells the (maximum ymin, minimum ymax) when determining ylims.
            None --> use the current ylims if current_axes_has_data(), else (None, None).
            False --> equivalent to (None, None), i.e. ignore this setting.
        E.g., overlaying multiple plots; plot 1 from -10 to 10, plot 2 from -5 to 15;
        by default would use plot 2 ybounds=(-10, 10) --> final ylims of (-10, 15).
        If provided plot 2 ybounds=(-7, 12), would instead have ylims of (-7, 15).""",
        ),
    # # # PLOT TICKS # # #
    'min_n_ticks': (UNSET, "UNSET, None, int, or 2-tuple of ints",
        """minimum number of ticks to use on plot axes, e.g. x & y axes.
        UNSET --> use {default}.
        None --> use matplotlib default (probably 2).
        int --> use this number of ticks.
        tuple --> provides (min for x, min for y).""",
        'DEFAULTS.PLOT.MIN_N_TICKS',
        ),
    'min_n_ticks_fail_ok': (UNSET, "bool",
        """whether it is okay for set_min_n_ticks() to fail silently in general,
        by default, when called from PlasmaCalcs plotting codes.
        UNSET --> use {default}.""",
        'DEFAULTS.PLOT.MIN_N_TICKS_FAIL_OK',
        ),
    'min_n_ticks_cbar': (UNSET, "UNSET, None, int, or 2-tuple of ints",
        """minimum number of ticks to use on colorbars.
        UNSET --> use {default}.
        None --> use matplotlib default (probably 2).
        int --> use this number of ticks.
        tuple --> provides (min for horizontal cbars, min for vertical cbars).""",
        'DEFAULTS.PLOT.MIN_N_TICKS_CBAR',
        ),
    'min_n_ticks_cbar_fail_ok': (UNSET, "bool",
        """whether it is okay for set_min_n_ticks() to fail silently for colorbars,
        by default, when called from PlasmaCalcs plotting codes.
        True enables to specify x and y minimums simultaneously,
            while only applying x mins to horizontal cbars, and y mins to vertical cbars.
        UNSET --> use {default}.""",
        'DEFAULTS.PLOT.MIN_N_TICKS_CBAR_FAIL_OK',
        ),
    # # # SUBPLOTS # # #
    'nrows': (1, "int",
        """number of rows in the subplots""",
        ),
    'ncols': (1, "int",
        """number of columns in the subplots""",
        ),
    'axsize': (UNSET, "UNSET, number, or (width, height) in inches",
        """size of a single subplot, in inches.
        UNSET --> use {default}.
        number --> use width = height = axsize.
        mutually exclusive with figsize, cannot provide both.""",
        'DEFAULTS.PLOT.SUBPLOTS_AXSIZE',
        ),
    'figsize': (UNSET, "UNSET, None, or (width, height) in inches",
        """if provided (even if None) pass to matplotlib.
        otherwise, for subplots, use axsize to determine figsize.""",
        ),
    'squeeze': (False, "False",
        """To avoid ambiguity, squeeze=True is not allowed; Subplots.axs will always be 2D.""",
        ),
    'kw_subplots_adjust': [
        ('hspace', 'wspace', 'bottom', 'top', 'left', 'right'),
            (None, "None or number (probably between 0 and 1)",
            """corresponding value that will be used during plt.subplots_adjust(...).
            If any region of a saved plot is getting cut off, try adjusting these values.
            None --> use rcParams["figure.subplot.*"]."""),
        ],
    'kw_share_ax': [
        ('sharex', 'sharey'),
            (None, "None, bool, or str ('all', 'row', 'col')",
            """whether & how to share x & y axes.
            None --> use False, by default, due to a formatting issue with sharex/sharey and make_cax.
            if provided, also set sharexlike and shareylike appropriately."""),
        ],
    'kw_share_axlike': [
        ('sharexlike', 'shareylike'),
            (UNSET, "UNSET or bool",
            """whether ticks and plot labels behave like there is a shared x, y axis.
            True --> remove tick labels for all but the bottom/left subplots,
                and Subplots.xlabel and .ylabel will only affect bottom/left subplots, by default.
            False --> retain all tick labels and all axes labels.
            UNSET --> use sharex/sharey if provided, else infer based on existing labels & ticks."""),
        ],
    'max_nrows_ncols': (UNSET, "UNSET, None, or int",
        """maximum number of rows or cols in subplots grid before crashing.
        UNSET --> use {default}
        None --> no maximum. Use maxlen=None to turn off the maximum if making a very large plot.""",
        'DEFAULTS.PLOT.SUBPLOTS_MAX_NROWS_NCOLS',
        ),
    'grid': (UNSET, "UNSET, bool, or dict",
        """whether to ax.grid() for each axes.
        UNSET --> use rcParams["axes.grid"].
        True --> ax.grid(True) for all axes.
        False --> ax.grid(False) for all axes.
        dict --> ax.grid(**grid) for all axes.""",
        ),
    # # # MOVIE (GENERIC) # # #
    'frames': (UNSET, "UNSET, None, int, iterable, or slice",
        """passed to FuncAnimation. Tells number of frames or which frames to plot.
        If UNSET, use value from self.plot_settings if possible else getattr(self, 'frames', None).
        if slice, use range(self.get_nframes())[frames], crashing if self doesn't have 'get_nframes'.""",
        ),
    'fps': (UNSET, "UNSET, None, or number",
        """frames per second.
        UNSET --> use {default}.
                (Or use value from self.plot_settings, if provided.)
        None --> use matplotlib defaults.""",
        'DEFAULTS.PLOT.FPS',
        ),
    'blit': (UNSET, "UNSET, None, or bool",
        """whether to use blitting.
        UNSET --> use {default}.
                (Or use value from self.plot_settings, if provided.)
        if None, use matplotlib defaults.""",
        'DEFAULTS.PLOT.BLIT',
        ),
    'progress_callback': (UNSET, "UNSET, None, or callable",
        """called when rendering each frame of the animation, as:
            progress_callback(current frame number, total number of frames).
        UNSET --> default to lambda i, n: updater.print('saving frame '+str(i)+' of '+str(n)),
                    where updater = ProgressUpdater(print_freq=1 if verbose else -1).
                    (Or use value from self.plot_settings, if provided)
        None --> don't call anything, regardless of self.verbose.""",
        ),
    # # # MOVIE IMAGE # # #
    'image_mode': ('pcolormesh', "str ('imshow' or 'pcolormesh')",
        """tells whether this image will be pcolormesh or imshow.""",
        None,  # no value from DEFAULTS
        ('pcolormesh', 'imshow'),  # apply validation immediately when setting; value must be one of these.
        ),
    'init_plot': (True, "bool",
        """whether to call self.init_plot() immediately, during __init__.
        (as a PlotSetting: tells the value of init_plot passed during __init__.)
        False --> still must call self.init_plot() before using self(...) or self.updater(...)
            (end-user will probably never use init_plot=False; it's mostly for internal code.)
            (might use False if creating MovieImage before defining the associated Axes.)""",
        ),
    'init_plot_frame': (0, "int",
        """default frame to use when calling self.init_plot()""",
        ),
    # # # XARRAY IMAGE # # #
    'add_colorbar': (UNSET, "UNSET or bool",
        """if provided, default for add_colorbar when making xarray plots.""",
        ),
    'add_labels': (True, "bool",
        """whether to add labels to xarray plots.""",
        ),
    # # # PATCHES # # #
    'transform': (UNSET, "UNSET, 'data', 'axes', 2-tuple of ('data' or 'axes'), or Transform object",
        """indicate coordinate system to use for x and y inputs.
        single string --> x and y both in this coordinate system.
        tuple --> xy[0] tells x system; xy[1] tells y system.
        'data' coords means input values match data values.
        'axes' coords means input values correspond to distance across axis:
            for x: left=0, right=1.
            for y: bottom=0, top=1.""",
        ),
    # # # UPDATABLE TEXT / TITLE / SUPTITLE # # #
    'text_kw': (UNSET, "UNSET, None, or dict",
        """any additional kwargs for text, e.g. text_kw=dict(fontweight=bold).
        Applied to titles too, but individual kw can be overridden by title settings.
        [TODO] ability to enter unambiguous text_kw directly, e.g. fontweight.""",
        ),
    'title': (UNSET, "UNSET, None, or str",
        """title for a single axes/subplot. For xarrays, will title.format(**xarray_nondim_coords(array)).
        (Note: plot_settings['title'] should always be the 'base' title, before title.format(...))
        UNSET --> use array_at_current_frame._title_for_slice() if XarrayImage (or other single-array plot).
                  use XarraySubplotTitlesInferer.infer_title() if XarraySubplots (or other multi-array plot).
        None --> do not add a title.""",
        ),
    'title_font': (UNSET, "UNSET, None, or str",
        """font for title, e.g. 'serif', 'sans-serif', or 'monospace'
        UNSET --> use {default}.
        None --> use matplotlib default.""",
        'DEFAULTS.PLOT.MOVIE_TITLE_FONT',
        ),
    'title_y': (UNSET, "UNSET, None, or number",
        """y position for title, in axes coordinates.""",
        ),
    'title_kw': (UNSET, "UNSET, or dict",
        """any additional kwargs for plt.title.""",
        ),
    'subplot_title_width': (UNSET, "UNSET, None, or number",
        """suggested width [number of characters] for subplot titles;
        default title routines might make multiline title if title would be longer than this.
        UNSET --> use {default}.
        None --> no maximum width.""",
        'DEFAULTS.PLOT.SUBPLOT_TITLE_WIDTH',
        ),
    'rtitle': (UNSET, "UNSET or str",
        """rightmost-column 'title' to put only on righthand side of subplots on the rightmost column.
        For xarrays, will rtitle.format(**xarray_nondim_coords(array)).
        Note: rtitles created via PlasmaCalcs' plot_note(), which uses plt.annotate, not plt.ylabel().
        UNSET --> do not add rtitle.""",
        ),
    'rtitle_kw': (UNSET, "UNSET, or dict",
        """any additional kwargs for plot_note() when making rtitle.
        (note: includes font=plot_settings['title_font'] unless `fontfamily` specified in rtitle_kw.)
        (note: to specify location, use `loc` or `xy` in axes coords or as str; see plot_note() for details.)
        UNSET --> use {default}.""",
        'DEFAULTS.PLOT.RTITLE_KW',
        ),
    'ttitle': (UNSET, "UNSET or str",
        """topmost-row title to put only on subplots in the top row.
        For xarrays, will ttitle.format(**xarray_nondim_coords(array)).
        Mutually exclusive with providing `title`, and overrides default titles if provided.
        UNSET --> do not add ttitle.""",
        ),
    'ttitle_kw': (UNSET, "UNSET, or dict",
        """any additional kwargs for plt.title when making ttitle.
        (note: includes font=plot_settings['title_font'] unless `fontfamily` specified in ttitle_kw.)
        UNSET --> use {default}.
        None --> use no title.""",
        'DEFAULTS.PLOT.TTITLE_KW',
        ),
    'suptitle': (UNSET, "UNSET, None, or str",
        """suptitle for a single axes/subplot. For xarrays, will suptitle.format(**xarray_nondim_coords(array)).
        (Note: plot_settings['suptitle'] should always be the 'base' suptitle, before suptitle.format(...))
        UNSET --> use self.default_suptitle. For XarraySubplots this includes information about t_plot_dim.
        None --> use no suptitle.
        (Note - self.plot_settings['suptitle'] will always be the 'base' suptitle, before applying suptitle_format.)""",
        ),
    'suptitle_font': (UNSET, "UNSET, None, or str",
        """font for suptitle, e.g. 'serif', 'sans-serif', or 'monospace'
        UNSET --> use {default}.
        None --> use matplotlib default.""",
        'DEFAULTS.PLOT.MOVIE_TITLE_FONT',
        ),
    'suptitle_y': (UNSET, "UNSET, None, or number",
        """y position for suptitle, in figure coordinates.""",
        ),
    'suptitle_kw': (UNSET, "UNSET, or dict",
        """any additional kwargs for plt.suptitle.""",
        ),
    'suptitle_width': (UNSET, "UNSET, None, or number",
        """suggested width [number of characters] for suptitle;
        default routines might make multiline suptitle to avoid going longer than this.
        UNSET --> use {default}.
        None --> no maximum width.""",
        'DEFAULTS.PLOT.SUPTITLE_WIDTH',
        ),
    # # # IMAGE SUBPLOTS # # #
    'add_colorbars': (True, "UNSET, bool, or str",
        """whether to add colorbars during init_plot, for ImageSubplots.
        str --> use self.colorbars(mode=add_colorbars). E.g. 'auto', 'all', 'row'.""",
        ),
    'aspect': (UNSET, "UNSET, None, str, or number",
        """aspect ratio for each Axes, by default.
        UNSET --> use {default}.
        None --> use matplotlib defaults.
        str --> use 'equal', or 'auto'. Note that 'equal' is equivalent to using aspect=1.
        number --> height scaling / width scaling.
                E.g. aspect=2 --> 1 data unit of height is twice long as 1 data unit of width.""",
        'DEFAULTS.PLOT.ASPECT',
        ),
    'layout': (UNSET, "UNSET, None, or str",
        """layout for subplots, by default.
        Suggestion: use layout='compressed', make_cax='mpl', and tweak wspace & hspace,
            OR use layout='none', make_cax='pc', and tweak suptitle_y, left, top, and bottom.
        UNSET --> use {default}.
        None --> use matplotlib defaults.
        str --> should be 'constrained', 'compressed', 'tight', or 'none'.""",
        'DEFAULTS.PLOT.LAYOUT',
        ),
    'share_vlims': (False, "bool or str ('all', 'row', 'col')",
        """whether to share vmin/vmax across ImageSubplots.
        True --> use 'all'
        'all' --> share vlims across all image subplots.
        'row' --> share vlims across each row of image subplots.
        'col' --> share vlims across each column of image subplots.""",
        ),
    # # # COLORBARS # # #
    'cax_mode': (UNSET, "UNSET, 'mpl', 'pc'",
        """tells how to make a new axis for a colorbar if one was not provided.
        UNSET --> use {default}.
        'mpl' --> use matplotlib logic, the same exact logic as in plt.colorbar.
        'pc' --> use PlasmaCalcs logic; it looks better when using layout='none',
                however 'pc' logic doesn't play nicely with other layout options yet.""",
        'DEFAULTS.PLOT.CAX_MODE',
        ),
    'colorbar_kw': (UNSET, "unset or dict",
        """any additional kwargs for plt.colorbar.""",
        ),
    # # # 3D FACEPLOTS # # #
    'faceplot_view_angle': (UNSET, "UNSET, None, or 3-tuple of numbers",
        """viewing angle for 3D faceplots, as (elevation, azimuth, roll).
        UNSET --> use {default}.
        None --> use matplotlib defaults.""",
        'DEFAULTS.PLOT.FACEPLOT_VIEW_ANGLE',
        ),
    'faceplot_edge_kwargs': (UNSET, "UNSET, None, or dict",
        """kwargs for edge lines in 3D faceplots.
        UNSET --> use {default}.
        None --> don't plot edge lines.
        empty dict --> use matplotlib defaults.""",
        'DEFAULTS.PLOT.FACEPLOT_EDGE_KWARGS',
        ),
    'faceplot_axes_zoom': (UNSET, "UNSET or number>0",
        """zoom for faceplot axis. matplotlib default is zoom=1.
        UNSET --> use {default}.""",
        'DEFAULTS.PLOT.FACEPLOT_AXES_ZOOM',
        ),
    'aspect3d': (UNSET, "UNSET, None, str, 3-tuple of numbers, or 4-tuple of numbers",
        """aspect ratio for 3D plots.
        UNSET --> use {default}.
        str --> 'auto' or 'equal'
        tuple of 3 numbers --> (x aspect, y aspect, z aspect)
        tuple of 4 numbers --> (1, x multiplier, y multiplier, z multiplier);
                multiplier multiplies aspect determined by data lengths.""",
        'DEFAULTS.PLOT.ASPECT3D',
        ),
    'proj_type': (UNSET, "UNSET, 'persp', or 'ortho'",
        """projection type for 3D plots. For details see mpl_toolkits.mplot3d.axes3d.Axes3D.
        UNSET --> use {default}.""",
        'DEFAULTS.PLOT.PROJ_TYPE',
        ),
    # # # CONTOUR # # #
    'colorbar_linewidth': (UNSET, "UNSET, None, int, list-like, or 2-tuple of None/int.",
        """linewidth for lines in contour colorbar.
        UNSET --> use {default}.
        None --> use same width as contour lines.
        int or list-like --> use this as the linewidth
                (as per matplotlib.collections.LineCollection.set(linewidth=...))
        tuple --> defines (min, max) linewidths; use None for no bound.
                E.g. (4, None) says "for thinner lines use 4; others same as contour lines".""",
        'DEFAULTS.PLOT.COLORBAR_LINEWIDTH',
        ),
    'colorbar_linestyle': (UNSET, "UNSET, None, or str",
        """linestyle for lines in contour colorbar.
        UNSET --> use {default}.
        None --> use same style as contour lines.""",
        'DEFAULTS.PLOT.COLORBAR_LINESTYLE',
        ),
    'colorbar_lines_set': (UNSET, "UNSET, or dict",
        """any additional attrs to set for contour colorbar lines,
        via cbar.ax.get_children()[1].set(...)""",
        ),
    'label': (UNSET, "UNSET or str",
        """label for this plot element, to be included in a legend.
        For xarrays, will label.format(**xarray_nondim_coords(array)).""",
        ),
    'legend_handle_kw': (UNSET, "UNSET or dict",
        """any additional kwargs to use when creating legend handles.""",
        ),
    'contourf': (False, "bool",
        """whether to use filled contours (i.e., plt.contourf) or not (i.e., plt.contour).""",
        ),
}

# # # ALL KWARGS TO PASS DIRECTLY TO MATPLOTLIB FUNCTIONS # # #
MPL_KWARGS = {
    # these should be the kwargs which are passed to matplotlib functions.
    # 'here' means the kwarg is used by that matplotlib function directly.
    # 'from' means "also accept any kwargs from these other matplotlib function(s)"
    # other keys mean "pass these kwargs as this key=dict(other kwargs)".
    #    (e.g. plt.subplots > subplot_kw > from mpl.figure.Figure.add_subplot means
    #    plt.subplots(..., subplot_kw=dict(**(kwargs from mpl.figure.Figure.add_subplot)))

    # ... actually, this is compatible with any function, not just matplotlib functions.
    # [TODO] clarify this, somehow.

    'plt.figure': {
        'here': ('figsize', 'dpi', 'facecolor', 'edgecolor', 'FigureClass',
                  'clear', 'layout', 'zorder'),
        },
    'fig.subplots': {
        'here': ('width_ratios', 'height_ratios', 'squeeze'),
        'subplot_kw': {
            'from': ['mpl.figure.Figure.add_subplot'],
            },
        },
    'plt.subplots': {
        'from': ['plt.figure', 'fig.subplots'],
        },
    'plt.subplots_adjust': {
        'here': ('left', 'bottom', 'right', 'top', 'wspace', 'hspace'),
        },
    'mpl.figure.Figure.add_subplot': {
        'here': ('projection', 'polar', 'axes_class',
                 'aspect'),
        },
    'mpl.animation.FuncAnimation': {
        'here': ('blit', 'frames', 'save_count', 'repeat', 'cache_frame_data',
                 'repeat_delay'),
        },
    'mpl.animation.FuncAnimation.save': {
        'here': ('codec', 'bitrate', 'metadata', 'savefig_kwargs', 'dpi'),
        },
    'xarray.DataArray.plot': {
        'here': ('xscale', 'yscale', 'xlim', 'ylim', 'xincrease', 'yincrease',
                 #'aspect',  # <-- don't include aspect here since it is finicky (requires "size" too)
                 ),
        },
    'xarray.DataArray.plot[image]': {   # for arr.plot.imshow & arr.plot.pcolormesh
        'here': ('cmap', 'vmin', 'vmax', 'add_colorbar', 'add_labels',
                'robust',
                'subplot_kws',
                ),
        'from': ['xarray.DataArray.plot'],
        },
    'xarray.DataArray.plot.contour': {
        'here': (),
        'from': ['xarray.DataArray.plot[image]', 'plt.contour'],
        },
    'xarray.DataArray.plot.contourf': {
        'here': (),
        'from': ['xarray.DataArray.plot[image]', 'plt.contourf'],
        },
    'xarray.DataArray.plot.line': {
        'here': (),
        'from': ['xarray.DataArray.plot', 'plt.plot'],
        },
    'xarray.DataArray.plot.scatter': {
        'here': ('add_labels',),
        'from': ['xarray.DataArray.plot', 'plt.scatter'],
        },
    'plt.colorbar': {
        'here': ('mappable', 'cax', 'use_gridspec', 'location', 'orientation',
                'fraction', 'shrink', 'aspect', 'pad', 'anchor', 'panchor', 'extend',
                'extendfrac', 'extendrect', 'spacing', 'ticks', 'format', 'drawedges',
                'label', 'boundaries', 'values',
                ),
        },
    'mpl.lines.Line2D': {
        'here': ('alpha', 'animated', 'antialiased', 'clip_box', 'clip_on', 'clip_path',
                'color', 'dash_capstyle', 'dash_joinstyle', 'dashes', 'drawstyle',
                'fillstyle', 'label', 'linestyle', 'ls', 'linewidth', 'lw', 'marker',
                'markeredgecolor', 'mec', 'markeredgewidth', 'mew', 'markerfacecolor', 'mfc',
                'markersize', 'ms', 'markevery', 'solid_capstyle', 'solid_joinstyle',
                'visible', 'zorder',
                ),
    },
    'plt.plot': {
        'here': ('scalex', 'scaley'),
        'from': ['mpl.lines.Line2D'],
        },
    'plt.errorbar': {
        'here': ('ecolor', 'elinewidth', 'capsize', 'capthick', 'barsabove',
                'lolims', 'uplims', 'xlolims', 'xuplims',
                'errorevery',
                ),
        'from': ['mpl.lines.Line2D'],
        },
    'mpl.collections.Collection': {
        'here': ('edgecolors', 'facecolors', 'linewidths', 'linestyles', 'capstyle',
                 'joinstyle', 'offsets', 'cmap', 'norm', 'hatch', 'pickradius', 'zorder',
                 # implicit, available via set_{key}(val):
                 'alpha', 'animated', 'antialiased', 'clip_box', 'clip_on', 'clip_path',
                 'color', 'edgecolor', 'facecolor', 'hatch_linewidth', 'in_layout',
                 'joinstyle', 'label', 'linestyle', 'linewidth', 'mouseover',
                 'path_effects', 'paths', 'picker', 'visible',
                 ),
    },
    'plt.fill_between': {
        'here': ('step',),
        'from': ['mpl.collections.Collection'],
    },
    'plt.contour': {
        'here': ('colors', 'alpha', 'cmap', 'vmin', 'vmax', 'levels',
                 'linestyles', 'linewidths',
                 ),
        },
    'plt.contourf': {
        'here': ('colors', 'alpha', 'cmap', 'vmin', 'vmax', 'levels',
                 'hatches',
                 ),
        },
    'plt.legend': {
        'here': ('loc', 'handlelength', 'bbox_to_anchor', 'ncols',
                 ),  # [TODO] more options for plt.legend.
        },
    'plt.imshow': {
        'here': ('cmap', 'vmin', 'vmax', 'norm', 'alpha',
                 'aspect', 'interpolation', 'origin', 'extent',
                 ),
        },
    'plt.pcolormesh': {
        'here': ('cmap', 'vmin', 'vmax', 'norm', 'alpha',
                 'edgecolors', 'shading', 'snap', 'rasterized',
                 ),
        },
    'plt.scatter': {
        'here': ('s', 'c', 'marker', 'cmap', 'norm', 'vmin', 'vmax', 'alpha',
                 'linewidths', 'edgecolors', 'colorizer', 'plotnonfinite',
                 'facecolors', 'label', 'visible', 'color',
                 ),
        },
    'ax.set': {
        'here': ('xlabel', 'ylabel', 'zlabel', 'xlim', 'ylim', 'zlim',
                 'xticks', 'yticks', 'zticks', 'xticklabels', 'yticklabels', 'zticklabels',
                 ),
        },
    'mpl_toolkits.mplot3d.axes3d.Axes3D': {
        'here': ('elev', 'azim', 'roll', 'proj_type', 'focal_length', 'shareview',
                 ),
        },
    'mpl.patches.Patch': {
        'here': ('alpha', 'animated', 'antialiased', 'capstyle', 'clip_box', 'clip_on', 'clip_path',
                 'color', 'edgecolor', 'ec', 'facecolor', 'fc', 'fill', 'hatch', 'hatch_linewidth',
                 'in_layout', 'joinstyle', 'label', 'linestyle', 'ls', 'linewidth', 'lw',
                 'mouseover', 'path_effects', 'picker', 'rasterized', 'sketch_params', 'snap',
                 'visible', 'zorder',
                 ),
        },
    'mpl.patches.Rectangle': {
        'here': ('width', 'height', 'angle', 'rotation_point'),
        'from': ['mpl.patches.Patch'],
        },
    # technically the rest of these aren't matplotlib functions but... still useful to have.
    'pc.TextPlotElement': {
        'here': ('text_kw',),
        },
    'pc.XarrayImagePlotElement': {
        'here': ('image_mode', 'aspect', 'xlabel', 'ylabel', 'grid', 'polar',
                 'min_n_ticks', 'min_n_ticks_cbar',
                 ),
        'from': ['xarray.DataArray.plot[image]', 'plt.figure'],
        },
    'pc.XarraySubplotTitlesInferer': {
        'here': ('subplot_title_width', 'suptitle_width'),
        },
    'pc.XarrayContourPlotElement': {
        'here': ('add_colorbar', 'add_labels', 'contourf',
                 'label', 'legend_handle_kw',
                 'colorbar_linewidth', 'colorbar_linestyle', 'colorbar_lines_set',
                 'aspect',
                 ),
        'from': ['xarray.DataArray.plot.contour', 'xarray.DataArray.plot.contourf'],
        },
    'pc.FaceplotPlotElement': {  
        'here': ('faceplot_view_angle', 'faceplot_edge_kwargs', 'faceplot_axes_zoom',
                 'aspect3d',
                 'add_colorbar', 'colorbar_kw',
                 ),
        'from': ['ax.set', 'plt.contourf'],
        },
    'pc.XarrayLinePlotElement': {
        'here': ('add_labels', 'label', 'aspect',
                 'robust', 'ymargin',
                 ),
        'from': ['xarray.DataArray.plot.line'],
        },
    'pc.ScatterPlotElement': {
        'here': (
                 # it always bugs me that these aliases aren't options by default in plt.scatter...:
                 'markersize',  # alias to 's'
                 'color',  # alias to 'c'
                 'facecolor',  # alias to 'facecolors'
                 'edgecolor',  # alias to 'edgecolors'
                 'linewidth',  # alias to 'linewidths'
                 ),
        'from': ['xarray.DataArray.plot.scatter'],
    },
    'pc.PatchPlotElement': {
        'here': ('transform',),
        'from': ['mpl.patches.Patch'],
        },
    'pc.RectanglePatchPlotElement': {
        'from': ['pc.PatchPlotElement', 'mpl.patches.Rectangle'],
        },
}


### --------------------- PlotSetting and PlotSettings classes --------------------- ###

class PlotSetting():
    '''a single plot setting, with default value.
    key: key for this setting.
    default: default value for this setting
    typsetr: string describing the type for this setting
    doc: docstring for this setting (not including the typestr) (will be hit by inspect.cleandoc)
    defaults_keystring: None, string of the form 'DEFAULTS.<key>', or tuple of (defaults_keystring, dict)
        if string, self.get(provided=UNSET) will get value from DEFAULTS.
        if tuple, first element must be str, and first behaves as if just a str,
            but then based on result of self.get, might use dict as follows:
            if val=self.get(provided=UNSET) in dict, use value from DEFAULTS implied by dict[val].
            E.g. ('DEFAULTS.PLOT.ROBUST', {True: 'DEFAULTS.PLOT.ROBUST_PERCENTILE'}) -->
                if val=self.get(provided=UNSET)==True, use DEFAULTS.PLOT.ROBUST_PERCENTILE;
                if provided not UNSET, or val!=True, just use val.
            Also, in this case, stores the dict portion as defaults_keystring_dict.
    validation: None, list-like, or callable.
        if provided, tells how to validate any value provided to this property.
        list-like --> value must be in this list.
        callable --> ensure that bool(callable(value)) evaluates to True.
    validation_message: None or str.
        if provided, tells what to append to error message if validation fails;
        base error message will always be: "invalid value for {self.key!r}: {value!r}."
        If validation_message does not start with a space, one will be prepended.

    ntab: number of tabs to indent doc by, underneath typestr.
        default 1, is a good number for docstrings of module-level objects.
        (but, e.g. for methods defined inside a class, probably use ntab=2.)
    tab: string to use for a single tab.
    '''

    def __init__(self, key, default, typestr, doc, defaults_keystring=None,
                 validation=None, validation_message=None, *, ntab=1, tab=DEFAULTS.TAB):
        # essential info:
        self.key = key
        self.default = default
        self.typestr = typestr
        self.doc = inspect.cleandoc(doc)
        if isinstance(defaults_keystring, tuple):
            assert len(defaults_keystring)==2
            assert isinstance(defaults_keystring[1], dict)
            self.defaults_keystring = defaults_keystring[0]
            self.defaults_keystring_dict = defaults_keystring[1]
        else:
            self.defaults_keystring = defaults_keystring
            self.defaults_keystring_dict = None
        self.validation = validation
        self.validation_message = validation_message
        # formatting:
        self.ntab = ntab
        self.tab = tab

    def get(self, provided=UNSET):
        '''get the value from self. return provided if not UNSET, else return self.get_default()'''
        if provided is UNSET:
            return self.get_default()
        else:
            return provided

    def get_default(self):
        '''get the default value: self.default if defaults_keystring is None else value from DEFAULTS.'''
        if self.defaults_keystring is None:
            return self.default
        else:
            result = self.defaults_keystring_value()
            if (self.defaults_keystring_dict is not None) and (result in self.defaults_keystring_dict):
                result = self._value_from_DEFAULTS_str(self.defaults_keystring_dict[result],
                                                        s_name=f'self.defaults_keystring_dict[{result!r}]')
            return result

    def defaults_keystring_value(self):
        '''get the value from DEFAULTS.'''
        s = self.defaults_keystring
        return self._value_from_DEFAULTS_str(s, s_name='self.defaults_keystring')

    @staticmethod
    def _value_from_DEFAULTS_str(s, *, s_name=''):
        '''get any value from DEFAULTS. s_name used if raising an error message.'''
        assert s is not None, f"{s_name} must be provided in order to get value from defaults"
        assert s.startswith('DEFAULTS.'), f"{s_name} must start with 'DEFAULTS.'"
        s = s[len('DEFAULTS.'):]
        if s.startswith('PLOT.'):
            s = s[len('PLOT.'):]
            return getattr(DEFAULTS.PLOT, s)
        else:
            return getattr(DEFAULTS, s)

    def __iter__(self):
        '''returns iter of tuple of (key, default, typestr, doc, defaults_keystring, validation).
        Thus, can create new PlotSetting with:
            PlotSetting(self.key, *iter(self))
        '''
        return iter((self.default, self.typestr, self.doc, self.defaults_keystring, self.validation))

    # # # VALIDATION # # #
    def validate(self, value):
        '''ensures that value is valid for this setting. Raise InputError if it is not.
        return (if no InputError is raised) depends on self.validation:
            None --> return None
            iterable --> return True if valid in self.validation
            callable --> return self.validation(value)
        '''
        vv = self.validation
        if vv is None:
            return
        elif callable(vv):
            result = vv(value)
            if result:
                return result
            else:
                errmsg_add = self._get_validation_message()
                raise InputError(f'invalid value for {self.key!r}: {value!r}.{errmsg_add}')
        else:
            if value in vv:
                return True
            else:
                errmsg_add = self._get_validation_message(default=f'Expected one of: {vv!r}.')
                raise InputError(f'invalid value for {self.key!r}: {value!r}.{errmsg_add}')

    def _get_validation_message(self, default=None):
        '''return self.validation_message, with a space prepended if needed.
        if default provided and self.validation_message is None, use default.'''
        vmessage = self.validation_message
        if vmessage is None and default is not None:
            vmessage = default
        if (vmessage is not None) and (len(vmessage)>0) and (not vmessage[0].isspace()):
            vmessage = f' {vmessage}'  # prepend a space.
        return vmessage

    # # # DOCUMENTATION # # #
    def defaults_keystring_formatting(self):
        '''returns dict which will be used to .format the docstring.
        If self.defaults_keystring is provided:
            {'default_value': self.defaults_keystring_value(),
            'default_key': self.defaults_keystring,
            'default': f'{self.defaults_keystring} (default: {self.defaults_keystring_value()})'}
        Also, if self.defaults_keystring_dict is provided, include something similar for each key in dict,
            adding 'defaults_dict_{key}_value', 'defaults_dict_{key}_key', and 'defaults_dict_{key}'.
        E.g. if defaults_keystring=('DEFAULTS.PLOT.ROBUST', {True: 'DEFAULTS.PLOT.ROBUST_PERCENTILE'}),
            when DEFAULTS.PLOT.ROBUST = True and DEFAULTS.PLOT.ROBUST_PERCENTILE = 2.0:
                {'default_value': True
                'default_key': 'DEFAULTS.PLOT.ROBUST',
                'default': 'DEFAULTS.PLOT.ROBUST (default: True)',
                'defaults_dict_True_value': 2.0,
                'defaults_dict_True_key': 'DEFAULTS.PLOT.ROBUST_PERCENTILE',
                'defaults_dict_True': 'DEFAULTS.PLOT.ROBUST_PERCENTILE (default: 2.0)'}
        '''
        if self.defaults_keystring is None:
            result = dict()
        else:
            default_value = self.defaults_keystring_value()
            default_key = self.defaults_keystring
            result = {'default_value': default_value,
                        'default_key': default_key,
                        'default': f'{default_key} (default: {default_value})'}
        if getattr(self, 'defaults_keystring_dict', None) is not None:
            for key, value in self.defaults_keystring_dict.items():
                default_key = value
                default_value = self._value_from_DEFAULTS_str(value, s_name=f'self.defaults_keystring_dict[{key}]')
                result[f'defaults_dict_{key}_value'] = default_value
                result[f'defaults_dict_{key}_key'] = default_key
                result[f'defaults_dict_{key}'] = f'{default_key} (default: {default_value})'
        return result

    def docstring(self, ntab=UNSET):
        '''return the docstring for this setting, in format:
        {self.typestr} (default: {self.default})
            {self.doc}

        the typestr line will not be indented at all;
        the docstring line(s) will be indented by self.tab * ntab.

        self.doc will be hit by .format(**self.defaults_keystring_formatting()).
        (If self.defaults_keystring is None, this shouldn't change the result.)
        '''
        if ntab is UNSET: ntab = self.ntab
        indent = self.tab * (ntab + 1)
        s = f'{self.typestr} (default: {self.default})'
        s += f'\n{textwrap.indent(self.doc, indent)}'
        s = s.format(**self.defaults_keystring_formatting())
        return s

    def docs_dict(self, ntab=UNSET):
        '''returns {self.key: self.docstring(ntab)}'''
        return {self.key: self.docstring(ntab)}

    def __str__(self):
        return self.docstring()

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}({self.key!r}, default={self.default!r}, typestr={self.typestr!r})'


class SharedPlotSetting(PlotSetting):
    '''PlotSetting which is shared amongst multiple kwargs.
    E.g., in DEFAULT_PLOT_SETTINGS:
        'kw_subplots_adjust': [
            ('hspace', 'wspace', 'bottom', 'top', 'left', 'right'),
            (None, "None or number (probably between 0 and 1)",
            """corresponding value that will be used during plt.subplots_adjust(...).
            None --> use rcParams["figure.subplot.*"]."""),
            ],
        corresponds to 6 kwargs, all with the same default value and docstring.
        No need to repeat the docstring multiple times.

    self.docs_dict() will contain the value from super(),
        in addition to {docs_key: "{', '.join(self.subkeys)}: {docstring}"}.
        E.g. when doing PlotSettings.format_docstring(),
            formatted func could either contain individual keys, like:
                hspace: {hspace}
                wspace: {wspace}
                ...
            OR, just contain the docs_key, like:
                {kw_subplots_adjust}
    '''
    def __init__(self, *args_super, docs_key, shared_keys, **kw_super):
        super().__init__(*args_super, **kw_super)
        self.docs_key = docs_key
        self.shared_keys = shared_keys

    def _docs_key_docs_dict(self, ntab=UNSET):
        '''return dict with key self.docs_key, "{', '.join(self.subkeys)}: {self.docstring(ntab)}".'''
        return {self.docs_key: f'{", ".join(self.shared_keys)}: {self.docstring(ntab)}'}

    def docs_dict(self, ntab=UNSET):
        '''returns super().docs_di'''
        result = self._docs_key_docs_dict(ntab)
        super_docs_dict = super().docs_dict(ntab)
        result.update(super_docs_dict)
        return result

    def __repr__(self):
        contents = [f'{self.key!r}',
                    f'docs_key={self.docs_key!r}',
                    f'shared_keys={self.shared_keys!r}',
                    f'default={self.default!r}',
                    f'typestr={self.typestr!r}',]
        return f'{type(self).__name__}({", ".join(contents)})'


class PlotSettings():
    '''class for managing plot settings.
    class stores default settings and docstrings;
    instance stores current settings, e.g. for a particular object.

    UNSET is used as default value for many settings;
    this is to distinguish between "not provided" and "provided as None",
    since None is a valid value for many settings (usually, None means "use matplotlib defaults).

    all settings can be provided as kwargs during __init__.
    kwargs which are not recognized as valid PlotSettings.valid_keys() will be ignored.

    CAUTION: adjusting plot settings after instantiation might break mutually-dependent settings.
        [TODO] make mutually-dependent settings be property-like, instead, to mitigate this?^

    CAUTION: do not use self.kw directly;
        instead, use self.get(key), self.set(**kw), self[key], self[key]=value, or del self[key].
        This ensures values are validated and that only valid keys are used.
    '''
    DEFAULT_SETTINGS = DEFAULT_PLOT_SETTINGS
    MPL_KWARGS = MPL_KWARGS

    def __init__(self, *, pop_from=dict(), **kw):
        self.kw = self.dict_from_valid_keys(kw)
        self.update(pop_from, pop=True)

    # # # SET / GET # # #
    def set(self, **kw):
        '''set plot settings, in self.
        kwargs which are not recognized as valid PlotSettings.valid_keys() will be ignored.
        '''
        self.update(self.dict_from_valid_keys(kw))

    def get(self, key, provided=UNSET, *, default=NO_VALUE, fdefault=NO_VALUE, last_resort_default=NO_VALUE):
        '''get a plot setting. if provided is not UNSET, return it.
    
        There are multiple ways to set defaults.
        A pneumonic for the order of precedence when multiple defaults / values are entered, is:
            "provided > self.kw > default > fdefault > self.DEFAULT_SETTINGS > last_resort_default"

        More precisely, when getting key, does the following, in order:
            -- assert key in self.valid_keys(); raise PlotSettingsError if not.
            - return provided (if not UNSET).
            - return self.kw[key] (if it exists and is not UNSET)
            - return default (if not NO_VALUE).
            - return fdefault() (if not NO_VALUE).
            - return self.get_default(key), if key in self.DEFAULT_SETTINGS.
            - return last_resort_default, if it was provided (not NO_VALUE).
            -- give up; raise PlotSettingsError.
        '''
        # note: the defaults for kwargs to this function are NO_VALUE instead of UNSET,
        # to avoid ambiguity with possibly wanting to use UNSET as a default value...
        # however, provided must have a default of UNSET, to ease with usage like:
        #   def func(..., setting_name=UNSET, ...):
        #       setting_value = plot_settings..get('setting_name', setting_name, ...)
        #       ...
        if key not in self.valid_keys():
            raise PlotSettingsError(f'invalid key: {key!r}. Not found in self.valid_keys()')
        if provided is not UNSET:
            return provided
        result = self.kw.get(key, UNSET)
        if result is not UNSET:
            return result
        if default is not NO_VALUE:
            return default
        if fdefault is not NO_VALUE:
            return fdefault()
        if key in self.DEFAULT_SETTINGS:
            return self.get_default(key)
        if last_resort_default is not NO_VALUE:
            return last_resort_default
        # else, failed to get key.
        errmsg = (f'key missing: {key!r}. key is in {type(self).__name__}.valid_keys(), '
                    'but not set in self.kw, and not in self.DEFAULT_SETTINGS;\n'
                    "also did not enter value for 'provided', 'default', 'fdefault', or 'last_resort_default'.")
        raise PlotSettingsError(errmsg)

    @classmethod
    def default(cls, key):
        '''get the default for a plot setting.
        This is the default entered at the definition of the setting; it might be UNSET.
        See also cls.get_default.
        '''
        setting = cls.DEFAULT_SETTINGS[key]
        return setting.default

    @classmethod
    def get_default(cls, key):
        '''get the default value for a plot setting.
        This is setting.get_default(), where setting is cls.DEFAULT_SETTINGS[key].
        Note that setting.get_default() does not necessarily equal setting.default;
            in particular they will differ if the default is UNSET,
            and a defaults_keystring was provided to that setting.
        '''
        setting = cls.DEFAULT_SETTINGS[key]
        return setting.get_default()

    def is_default(self, key):
        '''return whether key has the default value for this setting.'''
        return key not in self.kw

    def __getitem__(self, key):
        '''return self.get(key).'''
        return self.get(key)

    def __setitem__(self, key, value):
        '''set self.kw[key] = value, after ensuring this is valid, via self.validate.
        Only set key if value is not self.default(key) or self.get_default(key) (compared via 'is').
        '''
        self.validate(key, value)
        if DEFAULTS.DEBUG>=1:
            self.kw[key] = value
        elif key not in self.DEFAULT_SETTINGS:
            self.kw[key] = value   # not in default settings; default & get_default would crash.
        elif value is not self.default(key) and value is not self.get_default(key):
            self.kw[key] = value

    def __delitem__(self, key):
        '''delete self.kw[key]'''
        del self.kw[key]

    def __contains__(self, key):
        '''returns whether key is in self.kw.'''
        return key in self.kw

    def update(self, d, *, pop=False):
        '''update self.kw with d, but only for keys in self.valid_keys().
        if pop, pop keys from d instead of just copying values.
        '''
        valid_keys = self.valid_keys()
        d_keys = tuple(d.keys())
        for key in d_keys:
            if key in valid_keys:
                value = d.pop(key) if pop else d[key]
                self.__setitem__(key, value)

    def take_from(self, d):
        '''update self.kw with d, popping keys from d instead of just copying values.'''
        self.update(d, pop=True)

    def copy(self):
        '''return new PlotSettings, with copy of self.kw'''
        return PlotSettings(**self.kw)

    # # # VALIDATION OF KEYS & VALUES # # #
    @classmethod
    def validate(cls, key, value):
        '''raise InputError if value is invalid for key, or PlotSettingsError if key not in self.valid_keys().
        return None if no validation was performed, else the result of validate (see PlotSetting.validate()).
        '''
        if key in cls.valid_keys():
            if key in cls.DEFAULT_SETTINGS:
                setting = cls.DEFAULT_SETTINGS[key]
                return setting.validate(value)
        else:
            raise PlotSettingsError(f'invalid key: {key!r}. Not found in self.valid_keys()')

    @classmethod
    def valid_keys(cls):
        '''return set of all valid keys for plot settings.
        This includes all keys from cls.DEFAULT_SETTINGS as well as all mpl keys.
        '''
        result = set(cls.DEFAULT_SETTINGS.keys())
        for mpl_funcname in cls.MPL_KWARGS:
            result.update(cls.get_mpl_keys(mpl_funcname, mode='flat'))
        return result

    @classmethod
    def dict_from_valid_keys(cls, d, *, pop=False):
        '''return dict but only with keys that are valid for PlotSettings, i.e. in PlotSettings.valid_keys().
        if pop, also pop these keys from d instead of just copying their values.
        '''
        result = dict()
        for key in cls.valid_keys():
            if key in d:
                if pop:
                    result[key] = d.pop(key)
                else:
                    result[key] = d[key]
        return result

    # # # DOCUMENTATION # # #
    @classmethod
    def docs_dict(cls, ntab=1):
        '''return dict of {key: docstring} for all settings. See: format_docstring.'''
        result = dict()
        for key, setting in cls.DEFAULT_SETTINGS.items():
            result.update(setting.docs_dict(ntab))
        return result

    @classmethod
    def format_docstring(cls, *, ntab=1, **kw_format_docstring):
        '''return function decorator which formats docstring of a plotter function.
        Provides docs for all settings, by default.
        ntab tells number of tabs for docs.
            Use 1 for module-level functions, 2 for class methods, 3+ if indenting deeper than that...
        additional kw go to tools.format_docstring.
        '''
        return format_docstring(**cls.docs_dict(ntab=ntab), **kw_format_docstring)
        
    # # # DEFAULTS # # #
    @classmethod
    def _instantiate_default_settings(cls):
        '''convert all DEFAULT_SETTINGS to PlotSetting (or SharedPlotSetting) instances.'''
        result = dict()
        for key, value in cls.DEFAULT_SETTINGS.items():
            if isinstance(value, tuple):
                result[key] = PlotSetting(key, *value)
            elif isinstance(value, list):
                shared_keys, v = value
                for subkey in shared_keys:
                    result[subkey] = SharedPlotSetting(subkey, *v, docs_key=key, shared_keys=shared_keys)
            else:
                raise TypeError(f'invalid type for DEFAULT_SETTINGS[{key}]: {type(value)}')
        cls.DEFAULT_SETTINGS = result

    # # # POP MATPLOTLIB KWARGS # # #
    @classmethod
    def cls_pop_mpl_kwargs(cls, mpl_funcname, kw, *, defaults=dict(), **other_kwargs):
        '''pops kwargs from kw which are supposed to go to matplotlib func with name mpl_funcname.
        valid mpl_funcname options determined by cls.MPL_KWARGS.

        returns dict of kwargs to pass to matplotlib func.

        if other_kwargs provided, use these for values not found in kw, if not UNSET.
        if defaults provided, use these for values not found in kw or other_kwargs, if not UNSET.

        Note: might be fancy, e.g. 'axes_class' from kw for 'plt.subplots'
            would be passed as subplot_kw=dict(axes_class=...).
        '''
        result = dict()
        for key in cls.get_mpl_keys(mpl_funcname):
            if isinstance(key, str):
                v = RESULT_MISSING
                if key in kw:
                    v = kw.pop(key)
                if v is RESULT_MISSING or v is UNSET:
                    if key in other_kwargs:
                        v = other_kwargs.pop(key)
                    if v is RESULT_MISSING or v is UNSET:
                        if key in defaults:
                            v = defaults[key]
                if v is not RESULT_MISSING and v is not UNSET:
                    result[key] = v
            elif isinstance(key, tuple):
                # nested kwargs. [TODO] encapsulate repeated code from above...
                key, nested_keys = key
                nested_kw = dict()
                for k in nested_keys:
                    v = RESULT_MISSING
                    if k in kw:
                        v = kw.pop(k)
                    if v is RESULT_MISSING or v is UNSET:
                        if k in other_kwargs:
                            v = other_kwargs.pop(k)
                        if v is RESULT_MISSING or v is UNSET:
                            if k in defaults:
                                v = defaults[k]
                    if v is not RESULT_MISSING and v is not UNSET:
                        nested_kw[k] = v
                if len(nested_kw) > 0:
                    result[key] = nested_kw
        return result

    @classmethod
    def cls_get_mpl_kwargs(cls, mpl_funcname, **kw):
        '''returns dict of kwargs to pass to matplotlib func with name mpl_funcname.
        see also: pop_mpl_kwargs.
        '''
        return cls.cls_pop_mpl_kwargs(mpl_funcname, kw)   # kw was passed with ** so don't need to make a .copy()

    @classmethod
    def get_mpl_keys(cls, mpl_funcname, *, mode='nested'):
        '''returns tuple of keys which are supposed to go to matplotlib func with name mpl_funcname, as kwargs.

        some elements might be tuples instead of strings. If so, it means that they are nested kwargs.
            E.g. ('subplot_kw', ('axes_class', 'polar')) means that kw['axes_class'] and kw['polar']
            would be passed to mpl func as subplot_kw=dict(axes_class=kw['axes_class'], polar=kw['polar']).

        if mode=='flat', returns a flat tuple of keys, instead of nesting them.
            in this case, the dict-like matplotlib keys will NOT be included.
            E.g. in the example above, the result would be ('axes_class', 'polar').
            ('subplot_kw' gets excluded since it is a dict-like key.)
        '''
        if mpl_funcname not in cls.MPL_KWARGS:
            raise InputError(f'invalid mpl_funcname: {mpl_funcname!r}.')
        settings = cls.MPL_KWARGS[mpl_funcname].copy()
        result = []
        here = settings.pop('here', ())
        result.extend(here)
        from_ = settings.pop('from', ())
        for f in from_:
            result.extend(cls.get_mpl_keys(f, mode=mode))
        # other keys mean "pass these kwargs as this key=dict(other kwargs)".
        for key, f in settings.items():
            # [TODO] encapsulate repeated code from above...
            keys_from_key = []
            fcopy = f.copy()
            here = fcopy.pop('here', ())
            keys_from_key.extend(here)
            from_ = fcopy.pop('from', ())
            for g in from_:
                keys_from_key.extend(cls.get_mpl_keys(g, mode=mode))
            # put keys_from_key into result.
            if mode=='nested':
                result.append((key, tuple(keys_from_key)))
            elif mode=='flat':
                result.extend(keys_from_key)
            else:
                raise InputError(f'invalid mode: {mode!r}.')
        return tuple(result)

    def get_mpl_func_settings(self, mpl_funcname):
        '''return dict of {key: value} for all mpl kwargs for mpl_funcname, with values from self.
        Note: this is different get_mpl_kwargs, since the result will not have any nested kwargs.
        '''
        result = dict()
        for key in self.get_mpl_keys(mpl_funcname, mode='flat'):
            val = self.get(key, last_resort_default=UNSET)
            if val is not UNSET:
                result[key] = val
        return result

    def pop_mpl_kwargs(self, mpl_funcname, kw, **other_kwargs):
        '''return kwargs to use for mpl_funcname, using values from self as defaults, and kw if provided.
        pop values from kw if they are used.

        use values from kw if possible,
        else from other_kwargs if possible (exists and not UNSET).
        else from self if possible (not UNSET).
        '''
        defaults = self.get_mpl_func_settings(mpl_funcname)
        return self.cls_pop_mpl_kwargs(mpl_funcname, kw, defaults=defaults, **other_kwargs)

    def get_mpl_kwargs(self, mpl_funcname, **kw):
        '''return kwargs to use for mpl_funcname, using values from self as defaults, and kw if provided.'''
        return self.pop_mpl_kwargs(mpl_funcname, kw)

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}({self.kw!r})'


PlotSettings._instantiate_default_settings()


class PlotSettingsMixin():
    '''mixin which provides obj.plot_settings, a PlotSettings object.
    Additionally, kwargs in __init__ will be passed to obj.plot_settings,
        which will remember all valid plot settings entered into it.

    Be sure to put PlotSettingsMixin class ahead of matplotlib classes in MRO,
        so that PlotSettingsMixin can properly pop plot settings kwargs.

    mpl_super: list of strings, names of matplotlib super() classes (from MPL_KWARGS.keys()).
        If provided, pass kwargs for those classes, from self.plot_settings, during super().__int__.
    '''
    def __init__(self, *args_super, mpl_super=[], **kw):
        self.plot_settings = PlotSettings(pop_from=kw)  # pop plot settings kwargs from kw.
        if len(mpl_super) > 0:
            mpl_kwargs = dict()
            for mpl_funcname in mpl_super:
                mpl_kwargs.update(self.plot_settings.get_mpl_kwargs(mpl_funcname))
            kw.update(mpl_kwargs)
        super().__init__(*args_super, **kw)

    def __init_subclass__(cls, *args_super, **kw):
        '''appends note about using self.plot_settings, to cls.__doc__.
        if "PlotSettings" or "plot_settings" appears in cls.__doc__, do NOT append this note;
            assuming instead that this means the doc already mentions how to use plot_settings.
        '''
        msg = (f'To view or adjust plot settings in self, see self.plot_settings, or help(self.plot_settings).\n')
        msg = textwrap.indent(msg, DEFAULTS.TAB)
        if cls.__doc__ is None:
            cls.__doc__ = msg
        elif 'PlotSettings' not in cls.__doc__ and 'plot_settings' not in cls.__doc__:
            cls.__doc__ += f'\n\n{msg}'
