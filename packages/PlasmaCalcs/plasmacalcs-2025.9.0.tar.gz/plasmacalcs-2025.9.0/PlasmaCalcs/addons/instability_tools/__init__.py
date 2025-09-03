"""
Package Purpose: addons related to analysis of instabilities in general
"""

from .instability_data_tools import (
    pwl2_flatend, pwl3_flatend,
    Pwl2FlatendFitter, Pwl3FlatendFitter,
)
from .instability_quantity_loader import InstabilityQuantityLoader
from .instability_theory_tools import (
    xarray_khat, xarray_k,
    xarray_at_growmax,
    xarray_growth_kmax, xarray_grows,
    xarray_kmod_at_growmax, xarray_kang_at_growmax,
    xarray_khat_at_growmax, xarray_kds_at_growmax, xarray_k_at_growmax,
    xarray_smod_vphase, xarray_mod_vphase, xarray_vphase,
    xarray_where_grows, xarray_where_nogrows,
    xarray_stack_nonk_dims,
    xarray_kw_growthplot, xarray_growthplots, xarray_growthplot,
    xarray_klims_physical, xarray_klines,
)
from .instability_xarray_accessor import (
    itAccessor, itArrayAccessor, itDatasetAccessor,
)