"""
File Purpose: CopapicDirectLoader
"""
import os
import math  # for lcm...

# required external modules
import numpy as np
import xarray as xr

# optional external modules
from ...tools import ImportFailed
try:
    import openpmd_api as io
except ImportError as err:
    io = ImportFailed("openpmd_api", err=err, locals=locals())

# internal modules
from ...dimensions import INPUT_SNAP
from ...errors import (
    LoadingNotImplementedError,
    InputError,
)
from ...quantities import DirectLoader, QuasineutralLoader
from ...tools import interprets_fractional_indexing
from ...defaults import DEFAULTS


### --------------------- CopapicDirectLoader --------------------- ###

class CopapicDirectLoader(DirectLoader, QuasineutralLoader):
    '''manages loading data directly from Copapic output files.

    input_deck: CopapicInputDeck
        input deck. E.g. CopapicInputDeck.from_file('copapic.json').
        Currently, requires that input_deck.filename is not None.

    attributes of self (not available at __init__)
    '''

    _slice_maindims_in_load_direct = True   # [EFF] slice directly when reading h5 files, if using self.slices

    def __init__(self, input_deck, **kw_super):
        self.input_deck = input_deck
        super().__init__(**kw_super)

    # # # READ MODE AND SNAPDIR # # #
    @property
    def snapdir(self):
        '''directory containing the snapshot files.
        '''
        return self.input_deck.output_dir

    # # # LOAD FROMFILE # # #
    def _var_for_load_fromfile(self, varname_internal):
        '''return var, suitably adjusted to pass into load_fromfile().
        Here:
            append self.component if self._loading_component
            append self.fluid.N if self._loading_fluid
        E.g. 'flux' turns into 'fluxz2' when loading 'z' component and fluid 2.
        '''
        result = varname_internal
        if getattr(self, '_loading_fluid', False):
            result = result + '-' + str(self.fluid.N)
        if getattr(self, '_loading_component', False):
            result = result + '_' + str(self.component)
        return result

    def load_fromfile(self, fromfile_var, *args, snap=None, **kw):
        '''return numpy array of fromfile_var, loaded directly from file.
        use self.full_read_mode to determine which file(s) / how to read them.

        fromfile_var: str
            the name of the variable to read, adjusted appropriately for loading fromfile.
            E.g., use 'fluxz2', not 'flux', to get flux for fluid 2 and component z.
            See also: self._var_for_load_fromfile().
        snap: None, str, int, or Snap
            the snapshot number to load. if None, use self.snap.

        Example:
            fromfile_var='fluxx1', snap=7
        '''
        snap = self._as_single_snap(snap)  # expect single snap when loading from file.
        if hasattr(snap, 'exists_for') and not snap.exists_for(self):
            result = xr.DataArray(self.snap_dim.NAN, attrs=dict(units='raw'))
            return self.assign_snap_coord(result)  # [TODO][EFF] assign coords when making array instead...
        if snap is INPUT_SNAP:
            raise LoadingNotImplementedError(f'var={fromfile_var!r}, when snap is INPUT_SNAP')
        return self._openpmd_load_fromfile(fromfile_var, *args, snap=snap, **kw)

    def directly_loadable_vars(self, snap=None):
        '''return tuple of directly loadable variables.
        These are the variables that can be loaded directly from a file,
        using the current full_read_mode.

        snap: None, str, int, or Snap
            the snapshot number to load. if None, use self.snap.
        '''
        snap = self._as_single_snap(snap)  # expect single snap when loading from file.
        if hasattr(snap, 'exists_for') and not snap.exists_for(self):
            return np.nan
        result = list(self._openpmd_directly_loadable_vars(snap=snap))
        return result

    # def wheref_loadable(self, var=None, snaps=None):
    #     '''returns snaps from self.snaps where 'n', 'flux', 'nvsqr', 'vdist', 'phi' values can be loaded,
    #     for all fluids currently in self.fluid (for non-phi vars).
    #     [EFF] method is IMPLICIT, based on var_out_subcycling details for each fluid.
    #         Does not actually check the files directly, because it's expensive to do that.

    #     [TODO] account for subsampling_info too.

    #     var: None, list of str, str from ('n', 'flux', 'nvsqr', 'vdist', 'phi'), or 'all'
    #         None --> return dict of answer for each of those vars
    #         'all' --> return SnapList where all vars are loadable.
    #         list --> return SnapList where all vars in list are loadable.
    #         str --> return SnapList for this var only.
    #     snaps: None, 'current', 'current_range', 'current_n', or SnapList
    #         the snaps to consider.
    #         None --> self.snaps.
    #         'current' --> self.snap
    #         'current_range' --> self.snaps.select_between(self.snap[0].t, self.snap[-1].t)
    #         'current_n' --> 'current_range', but evently downsample result size similar to current n snap.
    #                     (note: even downsampling isn't always possible; result size won't exactly match.
    #                      useful if you want "roughly N snaps". See example below.)
    #         E.g. if self.snap [10,20,30,...,200] (len=19), and self.snaps [0,...,300] (len=301),
    #             checking where_loadable(var) which is available every 4 snaps, result will be:
    #             None --> [0,4,8,...,300] (len=76)
    #             'current' --> [20,40,...,200] (len=10)  # because 10,30,50,... aren't divisible by 4
    #             'current_range' --> [12,16,20,...,200] (len=48)
    #             'current_n' --> [12,20,28,...,200] (len=24)
    #                             # because interprets_fractional_indexing(slice(None,None,1/19), L=48)
    #                             # gives slice(0, None, 2), which is then applied to current_range result.
    #     '''
    #     result = {}
    #     downsample = False
    #     if snaps is None:
    #         snaps = self.snaps
    #     elif isinstance(snaps, str):
    #         if snaps=='current':
    #             snaps = self.snap_list()
    #         elif snaps=='current_range' or snaps=='current_n':
    #             snaplist = self.snap_list()
    #             if snaps == 'current_n': downsample = len(snaplist)
    #             snaps = self.snaps.select_between(snaplist[0].t, snaplist[-1].t)
    #         else:
    #             raise InputError(f'got str snaps={snaps!r}, expected "current" or "current_range"')
    #     combine = False
    #     KNOWN = ('n', 'flux', 'nvsqr', 'vdist', 'phi')
    #     if var is None:
    #         vars_ = KNOWN
    #     elif isinstance(var, str):
    #         if var == 'all':
    #             combine = True
    #             vars_ = KNOWN
    #         else:
    #             vars_ = [var]
    #     else:  # list of vars
    #         combine = True
    #         vars_ = var
    #     unknown = [v for v in vars_ if v not in KNOWN]
    #     if len(unknown) > 0:
    #         raise InputError(f'unsupported var(s): {unknown!r}. Expected only vars from: {KNOWN!r}')
    #     nout = self.input_deck['nout']
    #     subcycles = {}
    #     FLUID_VARS = {
    #         'n': 'part_out_subcycle',
    #         'flux': 'flux_out_subcycle',
    #         'nvsqr': 'nvsqr_out_subcycle',
    #         'vdist': 'vdist_out_subcycle',
    #     }
    #     for v, subvar in FLUID_VARS.items():
    #         if v in vars_:
    #             subcycle = 1
    #             for fluid in self.iter_fluid():
    #                 subcycle = math.lcm(subcycle, fluid.get(subvar, 1))
    #             subcycles[v] = subcycle
    #     if 'phi' in vars_:
    #         subcycles['phi'] = self.input_deck.get('phi_out_subcycle', 1)
    #     if combine:  # combine the subcycles
    #         subcycle = 1
    #         for v, sc in subcycles.items():
    #             subcycle = math.lcm(subcycle, sc)
    #         var = 'COMBINED'
    #         subcycles = {var: subcycle}
    #     for v, subcycle in subcycles.items():
    #         if subcycle == 1:
    #             result[v] = snaps
    #         else:
    #             igood = [i for i, snap in enumerate(snaps) if int(snap.s) % (subcycle * nout) == 0]
    #             result[v] = snaps[igood]
    #     # downsample maybe
    #     if downsample:
    #         for v, rr in result.items():
    #             if len(rr) > downsample:  # actually downsample this one :)
    #                 slicer = interprets_fractional_indexing(slice(None,None,1/downsample), L=len(rr))
    #                 result[v] = rr[slicer]
    #     return result[var] if isinstance(var, str) else result

    # def where_loadable(self, var=None, snaps=None):
    #     '''returns snaps from self.snaps where 'n', 'flux', 'nvsqr', 'vdist', 'phi' values can be loaded,
    #     for ALL fluids in self.fluids.
    #     Equivalent:
    #         with self.using(fluid=None):
    #             return self.wheref_loadable(var=var, snaps=snaps)

    #     [EFF] method is IMPLICIT, based on var_out_subcycling details for each fluid.
    #         Does not actually check the files directly, because it's expensive to do that.

    #     [TODO] account for subsampling_info too.

    #     var: None, list of str, str from ('n', 'flux', 'nvsqr', 'vdist', 'phi'), or 'all'
    #         None --> return dict of answer for each of those vars
    #         'all' --> return SnapList where all vars are loadable.
    #         list --> return SnapList where all vars in list are loadable.
    #         str --> return SnapList for this var only.
    #     snaps: None, 'current', 'current_range', 'current_n', or SnapList
    #         the snaps to consider.
    #         None --> self.snaps.
    #         'current' --> self.snap
    #         'current_range' --> self.snaps.select_between(self.snap[0].t, self.snap[-1].t)
    #         'current_n' --> 'current_range', but evently downsample result size similar to current n snap.
    #                     (note: even downsampling isn't always possible; result size won't exactly match.
    #                      useful if you want "roughly N snaps". See example below.)
    #         E.g. if self.snap [10,20,30,...,200] (len=19), and self.snaps [0,...,300] (len=301),
    #             checking where_loadable(var) which is available every 4 snaps, result will be:
    #             None --> [0,4,8,...,300] (len=76)
    #             'current' --> [20,40,...,200] (len=10)  # because 10,30,50,... aren't divisible by 4
    #             'current_range' --> [12,16,20,...,200] (len=48)
    #             'current_n' --> [12,20,28,...,200] (len=24)
    #                             # because interprets_fractional_indexing(slice(None,None,1/19), L=48)
    #                             # gives slice(0, None, 2), which is then applied to current_range result.
    #     '''
    #     with self.using(fluid=None):
    #         return self.wheref_loadable(var=var, snaps=snaps)

    def _openpmd_load_fromfile(self, copapic_var, *args__None, snap=None, **kw__None):
        '''return numpy array of var, loaded directly from file, using "openpmd" read_mode.

        copapic_var: str
            the name of the variable as stored in the snapshot.
        snap: None, str, int, or Snap
            the snapshot number to load.
            if None, use self.snap.

        Example:
            copapic_var='den0', snap=7
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        
        snap = self._as_single_snap(snap)
        # if copapic_var not in self._openpmd_directly_loadable_vars(snap=snap):
        #     errmsg = f'var={copapic_var!r} not recognized'
        #     raise LoadingNotImplementedError(errmsg)
        
        series = io.Series(self._openpmd_base_name(), io.Access.read_only)
        i = series.iterations[int(str(snap))]
        underscore_count = copapic_var.count('_')
        dash_count = copapic_var.count('-')
        if dash_count == 0:
            # no fluid
            if underscore_count == 0:
                # no component
                baseName = copapic_var
                component = " Scalar"
            else:
                # has component
                component = copapic_var.split('_')[1]
                baseName = copapic_var.split('_')[0]
        elif dash_count == 1:
            # has fluid
            if underscore_count == 0:
                # no component
                baseName = copapic_var.split('-')[0]
                fluid = copapic_var.split('-')[1]
                baseName = baseName + '_' + fluid
                component = " Scalar"
            else:
                # has component
                component = copapic_var.split('_')[1]
                base = copapic_var.split('_')[0]
                baseName = base.split('-')[0]
                fluid = base.split('-')[1]
                baseName = baseName + '_' + fluid

        if (baseName not in i.meshes):
            raise LoadingNotImplementedError(f'var={baseName!r} not found')
        var = i.meshes[baseName]

        for a, b in var.items():
            if (var.scalar):
                var = b
                break
            if a == component:
                var = b
                break
        
        if getattr(self, '_slice_maindims_in_load_direct', False):
            # [EFF] slice here instead of reading all data then slicing later.
            slices = self.slices
            slicer = tuple(slices.get(d, slice(None)) for d in self.maindims)
            result = var[slicer]
        else:
            result = var[:]

        series.flush()
        series.close()
        return result

    def _openpmd_directly_loadable_vars(self, *, snap=None):
        '''return tuple of directly loadable variables.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        series = io.Series(self._openpmd_base_name(), io.Access.read_only)
        i = series.iterations[int(str(snap))]
        result = [x.replace("_",'') for x in i.meshes]
        
        return tuple(result)

    def _openpmd_base_name(self):
        '''return basefrom which to load values'.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        n_fill = np.ceil(np.log10(self.input_deck['nt'])+1).astype(int)
        dir_ = self.input_deck.output_dir
        suffix = self.input_deck['file_extension']
        name = f'{dir_}/data_%0{n_fill}T.{suffix}'
        return name
