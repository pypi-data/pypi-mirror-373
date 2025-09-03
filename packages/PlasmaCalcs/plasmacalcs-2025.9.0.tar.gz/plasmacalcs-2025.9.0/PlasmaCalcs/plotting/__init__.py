"""
Package purpose: convenient plotting methods & misc plotting tools
"""
# module references, in case other packages need to access internal modules.
# provide module references for all modules which might be overwritten by same-named object.
# E.g. from .subplots import subplots --> "subplots" here will be the function not the module.
from . import subplots as _subplots_module
from .plot_tools import _colorbar_module

from .contours import (
    XarrayContourPlotElement, XarrayContour,
)
from .faceplot import (
    FaceplotPlotElement, Faceplot,
    xarray_faces_3D,
)
from .images import (
    ImagePlotElement, Image,
    XarrayImagePlotElement, XarrayImage,
)
from .labels import (
    TextPlotElement, MovieText, XarrayText,
    xarray_title_plot_node, xarray_suptitle_plot_node,
    title_from_coords,
    XarraySubplotTitlesInferer,
)
from .lines import (
    XarrayLinePlotElement, XarrayLine,
)
from .movies import (
    FuncAnimation,
    MoviePlotElement, MoviePlotNode,
    EmptyMovieNode, MovieOrganizerNode,
)
from .patches import (
    PatchPlotElement, XarrayPatch,
    RectanglePatchPlotElement, XarrayRectanglePatch,
    LimsPatchPlotElement, XarrayLimsPatch,
)
from .plot_settings import (
    PlotSettings, PlotSetting,
    DEFAULT_PLOT_SETTINGS, MPL_KWARGS,
)
from .plotter_manager import MetaPlotterManager, PlotterManager
from .scatter import (
    ScatterPlotElement,
    XarrayScatter,
)
from .subplots import (
    subplots_figsize,
    subplots, Subplots,
)
from .subplots_extensions import (
    MovieSubplots,
    XarraySubplots,
)
from .xarray_timelines import (
    XarrayTimelines,
    IndexableCycler,
)

# PLOT_TOOLS SUBPACKAGE #
from .plot_tools import (
    # colorbar
    make_cax, find_mappable, colorbar,
    Colorbar,
    # colors
    get_cmap,
    ColormapExtremes, BaseColormap, Colormap, cmap,
    CMAPS,
    # currently_active
    current_figure_exists, current_figure_or_None,
    current_axes_exists, current_axes_or_None, current_axes_has_data,
    current_image_exists, current_image_or_None,
    maintaining_current_plt, maintaining_current_figure, maintaining_current_axes, maintaining_current_image,
    using_current_plt, using_current_figure, using_current_axes, using_current_image,
    MaintainingCurrentPlt, UsingCurrentPlt,
    # lims
    calculate_vlims, update_vlims, calculate_lims_from_margin,
    get_data_interval, get_lims_with_margin,
    plt_zoom, plt_zoomx, plt_zoomy, set_margins_if_provided,
    set_lims_if_provided,
    # plot_dims
    PlotDimsMixin,
    infer_movie_dim, infer_xy_dims, infer_xyt_dims,
    # plot_tricks
    ax_outline, fig_outline, ax_remove_ticks, ax_remove_ticklabels,
    get_colorbar_axes,
    get_min_n_ticks, set_min_n_ticks,
    use_simple_log_tick_locator, SimpleLogTickLocator, use_simple_ticks_renamer,
    ax_aspect,
    plt_transformer,
    PLOT_LOCATION_NAMES, plot_locations, plot_note,
)