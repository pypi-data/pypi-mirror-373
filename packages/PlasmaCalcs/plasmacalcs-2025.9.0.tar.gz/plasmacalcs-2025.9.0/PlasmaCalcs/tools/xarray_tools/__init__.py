"""
Package Purpose: tools related to xarrays
"""
from . import _xarray_bind_tools  # allow _xarray_bind_tools to bind stuff, as needed

from .xarray_accessors import (
    xarray_register_dataarray_accessor_cls,
    xarray_register_dataset_accessor_cls,
    XarrayAccessor,
    pcAccessor, pcArrayAccessor, pcDatasetAccessor,
)
from .xarray_agg_stats import (
    xarray_aggregate,
    xarray_sum,
    xarray_prod,
    # stats
    xarray_stats,
    xarray_min, xarray_mean, xarray_median, xarray_max,
    xarray_std, xarray_rms,
    # non-aggregator stats
    xarray_minimum, xarray_minimum_of_datavars,
    xarray_maximum, xarray_maximum_of_datavars,
)
from .xarray_coords import (
    # coords
    xarray_nondim_coords, xarray_dims_coords,
    xarray_assign_self_as_coord,
    xarray_fill_coords, xarray_index_coords,
    xarray_promote_index_coords, xarray_demote_index_coords,
    xarray_scale_coords, xarray_shift_coords, xarray_log_coords,
    xarray_is_sorted,
    # coord math
    xarray_get_dx_along, xarray_differentiate,
)
from .xarray_dimensions import (
    _paramdocs_ensure_dims,
    # dimensions
    is_iterable_dim,
    take_along_dimension, take_along_dimensions, join_along_dimension,
    xarray_rename, xarray_assign, xarray_promote_dim, xarray_ensure_dims,
    xarray_squeeze, xarray_squeeze_close, xarray_closeness,
    xarray_drop_unused_dims, xarray_drop_vars, xarray_popped,
    # broadcasting
    xarray_broadcastable_array, xarray_broadcastable_from_dataset,
    xarray_from_broadcastable, 
    # coarsen / windowing
    xarray_coarsened,
)
from .xarray_grids import (
    xr1d, xrrange, xarray_range,
    XarrayGrid, xarray_grid,
    xarray_angle_grid,
)
from .xarray_indexing import (
    xarray_isel, xarray_search, xarray_sel,
    xarray_where,
    xarray_map,
    xarray_argsort, xarray_sort_array_along, xarray_sort_dataset_along,
    xarray_cmin, xarray_cmax, xarray_varmin, xarray_varmax,
    xarray_at_min_of, xarray_at_max_of,
    xarray_min_coord_where, xarray_max_coord_where,
)
from .xarray_io import (
    XarrayIoSerializable,
    xarray_save, xarray_load, xarray_mergeload,
    _xarray_save_prep,
    _xarray_coord_serializations, _xarray_coord_deserializations,
)
from .xarray_masks import (
    xarray_mask,
    xarray_has_mask, xarray_store_mask, xarray_stored_mask, xarray_popped_mask,
    xarray_unmask,
    xarray_demask_from_mask, xarray_demask_from_ds,
    xarray_unmask_var, xarray_unmask_vars,
)
from .xarray_misc import (
    xarray_copy_kw, xarray_with_data,
    xarray_as_array,
    xarray_vars_lookup, xarray_vars_lookup_with_defaults,
    xarray_where_finite,
    xarray_astypes, xarray_convert_types,
    xarray_object_coords_to_str,
)
from .xarray_sci import (
    xarray_interp_inverse,
    xarray_gaussian_filter,
    xarray_polyfit, xarray_assign_polyfit_stddev, xarray_coarsened_polyfit,
    xarray_curve_fit, xarray_curve_eval, XarrayCurveFitter,
    XarrayLineFitter, xarray_line_fit,
)
from .xarray_werr_stats import (
    xarray_werrmean,
    xarray_werr2pmstd, xarray_pmstd2werr, xarray_mean_pm_std,
    xarray_werradd, xarray_werrsub, xarray_werrmul, xarray_werrdiv,
)
