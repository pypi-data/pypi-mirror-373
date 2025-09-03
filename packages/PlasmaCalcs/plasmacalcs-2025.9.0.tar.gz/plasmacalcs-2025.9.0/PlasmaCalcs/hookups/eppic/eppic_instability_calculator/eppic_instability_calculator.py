"""
File Purpose: InstabilityCalculator specialized in computing EPPIC values.
Input is an xarray.Dataset.
Knows how to write input deck files for eppic, based on values.
"""

from .eppic_dist_inputs_loader import EppicDistInputsLoader
from .eppici_maker import EppiciMaker
from .eppic_glob_inputs_loader import EppicGlobInputsLoader
from .eppic_instability_plotters import EppicInstabilityPlotterManager
from .eppic_safety_info_loader import EppicSafetyInfoLoader
from ....errors import InputConflictError
from ....other_calculators import InstabilityCalculator
from ....tools import UNSET, format_docstring
from ....defaults import DEFAULTS

@format_docstring(NDIM_SPACE=DEFAULTS.EPPIC.NDIM_SPACE, 
                  NPTOTCELLD0=DEFAULTS.EPPIC.NPTOTCELLD0,
                  DIST_DEFAULTS=DEFAULTS.EPPIC.DIST_DEFAULTS,
                  GLOB_DEFAULTS=DEFAULTS.EPPIC.GLOB_DEFAULTS)
class EppicInstabilityCalculator(EppiciMaker, EppicDistInputsLoader, EppicGlobInputsLoader,
                                 EppicSafetyInfoLoader, EppicInstabilityPlotterManager,
                                 InstabilityCalculator):
    '''InstabilityCalculator specialized in computing EPPIC values,
    and with helpful method to make an EPPIC input deck in zeroth order equilibrium.

    ds: xarray.Dataset
        should probably have all relevant base vars (& simple derived vars).
        Possibilities include:
            ds, m, q, gamma, n, u, T, nusj, nusn, E, B, E_un0,
            m_n or m_neutral, n_n or n_neutral, u_n or u_neutral, T_n or T_neutral.

    ndim_space: UNSET or int
        number of spatial dimensions (probably 2 or 3).
        UNSET --> ds['ndim_space'] if provided, else DEFAULTS.EPPIC.NDIM_SPACE (default={NDIM_SPACE}).
    nptotcelld0: UNSET or int
        nptotcelld for the unsubcycled distribution (not necessarily dist 0).
        UNSET --> ds['nptotcelld0'] if provided, else DEFAULTS.EPPIC.NPTOTCELLD0 (default={NPTOTCELLD0}).
        (raise InputConflictError if ds['nptotcelld0'] conflicts with value input here.)
    glob_vals: UNSET or dict of values
        can specify non-default values for global parameters.
        Recognizes all keys (will add as a data_var in self.ds),
        but some defaults are already defined in DEFAULTS.EPPIC.GLOB_DEFAULTS:
            {GLOB_DEFAULTS}.
    dist_vals: UNSET or dict of (value or xarray.DataArray with 'fluid' dimension)
        can specify non-default values for misc. distribution parameters.
        Recognizes all keys (will add as a data_var in self.ds),
        but some defaults are already defined in DEFAULTS.EPPIC.DIST_DEFAULTS:
            {DIST_DEFAULTS}.
        To specify new value but same value for each dist, use non-DataArray value.
        To specify different values for each dist, use {{key: DataArray with 'fluid' dimension}}.
        This is really just an alternative to manually adding these values to ds;
            any values provided directly in ds will not be overridden.
    '''
    # fluid_list_cls = EppicDistList   # using this would cause crash when using non-EppicDist Fluids,
    # jfluid_list_cls = EppicNeutralList   # which is not actually desireable...

    def __init__(self, ds, *, ndim_space=UNSET, nptotcelld0=UNSET,
                 glob_vals=UNSET, dist_vals=UNSET, **kw_super):
        self._kw_input = dict(ndim_space=ndim_space, nptotcelld0=nptotcelld0,
                              dist_vals=dist_vals, glob_vals=glob_vals)
        ds = self.assign_inputs(ds)
        super().__init__(ds, **kw_super)  # includes: self.ds = self.assign_bases(ds)

    def assign_inputs(self, ds):
        '''return a copy of ds, after assigning relevant init inputs from self.
        Currently, checks:
            - nptotcelld0
            - dist_vals
        '''
        # ndim_space
        ndim_space_in = self._kw_input['ndim_space']
        ndim_space_ds = ds.get('ndim_space', None)
        if ndim_space_ds is not None and ndim_space_in is not UNSET:
            if ndim_space_ds != ndim_space_in:
                raise InputConflictError(f"ndim_space conflict: {ndim_space_ds} != {ndim_space_in}")
        if ndim_space_ds is None:
            if ndim_space_in is UNSET:
                ndim_space_in = DEFAULTS.EPPIC.NDIM_SPACE
            ds = ds.assign(ndim_space=ndim_space_in)
        # nptotcelld0  # [TODO] encapsulate instead of repeating code from ndim_space^?
        nptotcelld0_in = self._kw_input['nptotcelld0']
        nptotcelld0_ds = ds.get('nptotcelld0', None)
        if nptotcelld0_ds is not None and nptotcelld0_in is not UNSET:
            if nptotcelld0_ds != nptotcelld0_in:
                raise InputConflictError(f"nptotcelld0 conflict: {nptotcelld0_ds} != {nptotcelld0_in}")
        if nptotcelld0_ds is None:
            if nptotcelld0_in is UNSET:
                nptotcelld0_in = DEFAULTS.EPPIC.NPTOTCELLD0
            ds = ds.assign(nptotcelld0=nptotcelld0_in)
        # dist_vals
        dv_use = DEFAULTS.EPPIC.DIST_DEFAULTS.copy()
        dv_in = self._kw_input['dist_vals']
        if dv_in is UNSET: dv_in = {}
        dv_use.update(dv_in)
        for var, value in dv_use.items():
            if var in ds:
                if var in dv_in:
                    raise InputConflictError(f'ds already has {var!r}; cannot also provide in dist_vals.')
                # else, pass. Don't override ds value with value from DIST_DEFAULTS.
            else:
                ds = ds.assign({var: value})
        # glob_vals   # [TODO]: encapsulate instead of repeating code from dist_vals^?
        gv_use = DEFAULTS.EPPIC.GLOB_DEFAULTS.copy()
        gv_in = self._kw_input['glob_vals']
        if gv_in is UNSET: gv_in = {}
        gv_use.update(gv_in)
        for var, value in gv_use.items():
            if var in ds:
                if var in gv_in:
                    raise InputConflictError(f'ds already has {var!r}; cannot also provide in glob_vals.')
                # else, pass. Don't override ds value with value from GLOB_DEFAULTS.
            else:
                ds = ds.assign({var: value})
        return ds
