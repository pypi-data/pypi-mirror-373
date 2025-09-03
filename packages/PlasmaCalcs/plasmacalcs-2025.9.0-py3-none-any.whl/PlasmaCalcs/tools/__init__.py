"""
Package purpose: misc tools; portable (not specific to PlasmaCalcs).
"""
from .array_select import (
    select_i_closest, select_closest,
    select_i_before, select_before,
    select_i_after, select_after,
    select_i_between, select_between,
    ArraySelectable, ArraySelectableChildHaver,
)
from .arrays import (
    memory_size_check, memory_size_check_loading_arrays_like,
    finite_op, finite_min, finite_mean, finite_max, finite_std,
    finite_median, finite_percentile,
    unique_close,
    interprets_fractional_indexing, ndindex_array,
    looks_flat, nest_shape,
    wraplist, ndenumerate_nonNone,
    np_dtype_object_to_str,
)
from .display import (
    repr_simple,
    print_clear, help_str,
    join_strs_with_max_line_len,
)
from .docs_tools import (
    format_docstring,
    docstring_but_strip_examples,
    DocstringInfo,
    sphinx_docstring,
    list_objs,
)
from .history import (
    git_hash_local, git_hash, git_hash_here, git_hash_PlasmaCalcs,
    _PlasmaCalcs_version,
    datetime_now,
    code_snapshot_info,
)
from .fft_tools import (
    # array_fft
    fftN, fft2, fft1, fftfreq_shifted,
    ifftN, ifftfreq_shifted,
    # fft_dimnames
    FFTDimname,
    # fft_slices
    FFTSlices,
    # xarray_fft
    xarray_fftN,
    xarray_ifftN,
    xarray_lowpass,
)
from .imports import (
    enable_reload, reload,
    import_relative,
    ImportFailed,
)
from .io_tools import (
    attempt_literal_eval,
    read_idl_params_file, updated_idl_params_file,
    read_python_params_file,
)
from .iterables import (
    is_iterable,
    argmax, rargmax,
    scalar_item,
    DictWithAliases,
    DictlikeFromKeysAndGetitem,
    Partition, PartitionFromXarray,
    Container, ContainerOfList, ContainerOfArray, ContainerOfDict,
    Bijection, BijectiveMemory,
    SymmetricPairMapping,
    DictOfSimilar,
)
from .math import (
    ast_math_eval,
    round_to_int, float_rounding,
    is_integer,
    product, nonempty_product,
    np_all_int,
    as_roman_numeral, from_roman_numeral,
)
from .multiprocessing import (
    Task,
    CrashIfCalled, UniqueTask, UNSET_TASK, identity, IdentityTask,
    TaskContainer, TaskList, TaskArray,
    TaskContainerCallKwargsAttrHaver,
    TaskGroup, TaskPartition,
    mptest_add100, mptest_sleep, mptest_sleep_add100, mptest_echo,
    check_pickle, copy_via_pickle,
)
from .oop_tools import (
    # binding
    bind_to, Binding,
    # manage_attrs
    maintaining_attrs, using_attrs,
    maintain_attrs, use_attrs,
    MaintainingAttrs, UsingAttrs,
    UsingAttrsSignaled,
    IncrementableAttrManager,
    # oop_misc
    apply,
    MetaClsRepr,
)
from .os_tools import (
    pc_path,
    find_files_re,
    InDir,
    with_dir,
    maintain_cwd, maintain_directory, maintain_dir,
    get_paths_with_common_start,
    next_unique_name,
    nbytes_path,
)
from .properties import (
    alias, alias_to_result_of, alias_child, alias_key_of, alias_in,
    weakref_property_simple,
    simple_property, simple_tuple_property,
    elementwise_property,
    dict_with_defaults_property,
)
from .pytools import (
    printsource, displaysource,
    is_iterable,
    inputs_as_dict, _inputs_as_dict__maker,
    value_from_aliases,
    help_str, print_help_str, _help_str_paramdocs,
    indent_doclines, indent_paramdocs,
    pad_missing_format_keys, format_except_missing,
    replace_missing_format_keys, format_replace_missing,
)
from .sentinels import (
    Sentinel,
    UNSET, NO_VALUE, ATTR_UNSET, RESULT_MISSING,
)
from .supercomputer import (
    find_jobfiles, find_slurmfiles,
    SlurmOptionsDict, read_slurm_options,
    slurm_options_here, slurm_option_here,
)
from .timing import (
    Profile,
    PROFILE, profiling, print_profile,
    Stopwatch, TickingWatch,
    ProgressUpdater,
    TimeLimit,
)
from .trees import Tree
from .xarray_tools import (
    ## accessors ##
    XarrayAccessor, pcAccessor,
    # pcArrayAccessor, pcDatasetAccessor,  # <-- keep out of top-level namespace;
    # users can do pcAccessor.register(totype='array') or totype='dataset' instead.
    ## agg_stats ##
    xarray_aggregate,
    xarray_sum,
    xarray_prod,
    xarray_stats,
    xarray_min, xarray_mean, xarray_median, xarray_max,
    xarray_std, xarray_rms,
    xarray_minimum, xarray_minimum_of_datavars,
    xarray_maximum, xarray_maximum_of_datavars,
    ## coords ##
    xarray_nondim_coords, xarray_dims_coords,
    xarray_assign_self_as_coord,
    xarray_fill_coords, xarray_index_coords,
    xarray_promote_index_coords, xarray_demote_index_coords,
    xarray_scale_coords, xarray_shift_coords, xarray_log_coords,
    xarray_is_sorted,
    # coord math
    xarray_get_dx_along, xarray_differentiate,
    ## dimensions ##
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
    ## grids ##
    xr1d, xrrange, xarray_range,
    XarrayGrid, xarray_grid,
    xarray_angle_grid,
    ## indexing ##
    xarray_isel, xarray_search, xarray_sel,
    xarray_where,
    xarray_map,
    xarray_argsort, xarray_sort_array_along, xarray_sort_dataset_along,
    xarray_cmin, xarray_cmax, xarray_varmin, xarray_varmax,
    xarray_at_min_of, xarray_at_max_of,
    xarray_min_coord_where, xarray_max_coord_where,
    ## io ##
    XarrayIoSerializable,
    xarray_save, xarray_load, xarray_mergeload,
    _xarray_save_prep,
    _xarray_coord_serializations, _xarray_coord_deserializations,
    ## masks ##
    xarray_mask,
    xarray_has_mask, xarray_store_mask, xarray_stored_mask, xarray_popped_mask,
    xarray_unmask,
    xarray_demask_from_mask, xarray_demask_from_ds,
    xarray_unmask_var, xarray_unmask_vars,
    ## misc ##
    xarray_copy_kw, xarray_with_data,
    xarray_as_array,
    xarray_vars_lookup, xarray_vars_lookup_with_defaults,
    xarray_where_finite,
    xarray_astypes, xarray_convert_types,
    xarray_object_coords_to_str,
    ## sci ##
    xarray_interp_inverse,
    xarray_gaussian_filter,
    xarray_polyfit, xarray_assign_polyfit_stddev, xarray_coarsened_polyfit,
    xarray_curve_fit, xarray_curve_eval, XarrayCurveFitter,
    XarrayLineFitter, xarray_line_fit,
    ## werr_stats ##
    xarray_werrmean,
    xarray_werr2pmstd, xarray_pmstd2werr, xarray_mean_pm_std,
    xarray_werradd, xarray_werrsub, xarray_werrmul, xarray_werrdiv,
)
