"""
Package Purpose: misc plotting tools.
"""
# module references, in case other packages need to access internal modules.
# provide module references for all modules which might be overwritten by same-named object.
# E.g. from .colorbar import colorbar --> "colobar" here will be the function not the module.
from . import colorbar as _colorbar_module

from .colorbar import (
    make_cax, find_mappable, colorbar,
    Colorbar,
    _paramdocs_colorbar,
)
from .colors import (
    get_cmap,
    ColormapExtremes, BaseColormap, Colormap, cmap,
    CMAPS,
)
from .currently_active import (
    current_figure_exists, current_figure_or_None,
    current_axes_exists, current_axes_or_None, current_axes_has_data,
    current_image_exists, current_image_or_None,
    maintaining_current_plt, maintaining_current_figure, maintaining_current_axes, maintaining_current_image,
    using_current_plt, using_current_figure, using_current_axes, using_current_image,
    MaintainingCurrentPlt, UsingCurrentPlt,
)
from .lims import (
    calculate_vlims, update_vlims, calculate_lims_from_margin,
    get_data_interval, get_lims_with_margin,
    plt_zoom, plt_zoomx, plt_zoomy, set_margins_if_provided,
    set_lims_if_provided,
)
from .plot_dims import (
    PlotDimsMixin,
    infer_movie_dim, infer_xy_dims, infer_xyt_dims,
)
from .plot_tricks import (
    ax_outline, fig_outline, ax_remove_ticks, ax_remove_ticklabels,
    get_colorbar_axes,
    get_min_n_ticks, set_min_n_ticks,
    use_simple_log_tick_locator, SimpleLogTickLocator, use_simple_ticks_renamer,
    ax_aspect,
    plt_transformer,
    PLOT_LOCATION_NAMES, plot_locations, plot_note,
)
