"""
File Purpose: loading info related to 'safe' eppic.i inputs,
from values in an EppicInstabilityCalculator.
"""
import numpy as np
import xarray as xr

from ..eppic_runtime_info import EppicRuntimeInfoLoader
from ..eppic_sim_info import EppicSimInfoLoader
from ....defaults import DEFAULTS
from ....errors import LoadingNotImplementedError
from ....tools import (
    simple_property,
    xarray_sum, xr1d,
)


class EppicSafetyInfoLoader(EppicSimInfoLoader, EppicRuntimeInfoLoader):
    '''loads info about 'safe' eppic.i inputs, from values in an EppicInstabilityCalculator.
    E.g. self('safe_sim_size') tells expected size of a simulation using 'safe' inputs.
        (including: safe_total_Gbytes, safe_pow2_Nspace, safe_spacetimesteps)
    '''

    # # # HACKY CLASS INHERITENCE STUFF # # #

    # required to ensure we don't use EppicSimInfoLoader's ndim_space.
    @known_var
    def get_ndim_space(self):
        '''number of spatial dimensions to put in the simulation. Loaded directly from self.ds.'''
        return self.load_direct('ndim_space')

    # required to ensure we don't use EppicSimInfoLoader's nptotcell
    @known_var(deps=['safe_nptotcelld', 'safe_pow2_subcycle'], aliases=['safe_nptotcell'])
    def get_nptotcell(self):
        '''number of particles per cell for all fluids combined, using 'safe' simulation inputs,
        appropriately weighted considering subcycling.
        Equivalent: sum_fluids_(safe_nptotcelld/safe_pow2_subcycle)
        '''
        return xarray_sum(self('safe_nptotcelld') / self('safe_pow2_subcycle'), 'fluid')

    # required to ensure we don't use EppicSimInfoLoader's nsubdomains
    @known_var(deps=['safe_nsubdomains'])
    def get_nsubdomains(self):
        '''number of subdomains to use for eppic run.
        Loaded directly from self.ds if available, else self('safe_nsubdomains')
        '''
        try:
            return self.load_direct('nsubdomains')
        except LoadingNotImplementedError:
            return self('safe_nsubdomains')


    # # # SIMULATION SIZE # # #

    SAFE_SIM_SIZE_VARS = [
        # size (time)
        'safe_dt', 'safe_nt', 'safe_rounded_nt',
        'safe_nout', 'safe_rounded_nout', 'safe_nsnaps',
        # size (space)
        'safe_dspace', 'safe_Nspace', 'safe_pow2_Nspace',
        'safe_data_array_Mbytes', 'arrays_per_snap',
        # size (total)
        'safe_total_Gbytes', 'safe_spacetimesteps',
        # size (runtime)
        'tasks_per_node',
        'n_nodes',
        'min_n_nodes', 'min_n_nodes_given_nsubdomains', 'min_n_nodes_given_runtime_guess',
        'safe_cpu_seconds_per_timestep', 'safe_cpu_seconds', 'safe_node_hours',
        'safe_runtime_seconds', 'safe_runtime_HMS',
    ]
    @known_var(deps=SAFE_SIM_SIZE_VARS)
    def get_safe_sim_size(self):
        '''dataset with various values related size of a simulation using 'safe' inputs.
        Equivalent: self(self.SAFE_SIM_SIZE_VARS)
        '''
        cached = dict(_cached_safe_dt=self('safe_dt'),
                      _cached_safe_pow2_subcycle=self('safe_pow2_subcycle'))
        with self.using(**cached):  # [EFF] caching on most expensive vars to avoid recalculating.
            return self(self.SAFE_SIM_SIZE_VARS)

    @known_var(deps=['safe_rounded_nt', 'safe_pow2_Nspace', 'ndim_space'])
    def get_safe_spacetimesteps(self):
        '''number of "cells" across space AND time for a simulation using 'safe' inputs.
        safe_spacetimesteps = safe_rounded_nt * (safe_pow2_Nspace ** ndim_space).
        '''
        timesteps = self('safe_rounded_nt') * 1.0   # *1.0 in case of Very Big results too large for int64.
        spacesteps = (self('safe_pow2_Nspace') * 1.0) ** self('ndim_space')
        return timesteps * spacesteps

    @known_var(deps=['safe_rounded_nt', 'safe_rounded_nout'])
    def get_safe_nsnaps(self):
        '''number of snapshots in entire simulation if using safe_rounded_nout and safe_nt.
        safe_nsnaps = safe_nt / safe_rounded_nout.
        '''
        return self('safe_rounded_nt') / self('safe_rounded_nout')

    @known_var(deps=['safe_pow2_Nspace', 'ndim_space', 'nout_avg'])
    def get_safe_data_array_size(self):
        '''number of elements in a single output data array for a simulation using 'safe' inputs.
        safe_data_array_size = (safe_pow2_Nspace/nout_avg) ** ndim_space
        '''
        return (self('safe_pow2_Nspace') / self('nout_avg')) ** self('ndim_space')

    @staticmethod
    def _to_bytes_factor(M=False, dtype='32'):
        '''number of (Mega)bytes per item in an array with this dtype.
        M: '', 'M', 'G'. Tells whether to use bytes, MB, or GB.
        dtype: '', '32', or '64'. Dtype to use. '' or '32' --> float32. '64' --> float64.
        '''
        if dtype=='' or dtype=='32':
            esize = np.dtype('float32').itemsize
        elif dtype=='64':
            esize = np.dtype('float64').itemsize
        if M=='M':
            esize = esize / 1024**2
        elif M=='G':
            esize = esize / 1024**3
        return esize

    @known_pattern(r'safe_data_array_(|M|G)bytes(|32|64)', deps=['safe_data_array_size'])
    def get_safe_data_array_bytes(self, var, *, _match=None):
        '''number of bytes in a single output data array for a simulation using 'safe' inputs.
        result = safe_data_array_size * number of bytes per element.
        pattern: Mbytes or Gbytes to get MB or GB. Uses 1024 not 1000 (e.g. MB --> 1024**2.)
        pattern: bytes32 or bytes64 to specify dtype. Unspecified --> float32.
        '''
        M, dtype = _match.groups()
        esize = self._to_bytes_factor(M, dtype)
        return self('safe_data_array_size') * esize

    @known_var(deps=['part_out_subcycle', 'flux_out_subcycle', 'nvsqr_out_subcycle'])
    def get_arrays_per_snap(self):
        '''average number of arrays (excluding vdist arrays) per snapshot file.
        n_global = 1   # phi, only.
        n_den = (nfluids / part_out_subcycle)
        n_flux = (nfluids * 3 / flux_out_subcycle)   # 3 is from vector components x,y,z
        n_nvsqr = (nfluids * 3 / nvsqr_out_subcycle)  # 3 is from vector components x,y,z
        n_snap_arrays_space = n_global + n_den + n_flux + n_nvsqr
        '''
        nfluids = len(self.fluids)
        n_global = 1
        n_den = nfluids / self('part_out_subcycle')
        n_flux = nfluids * 3 / self('flux_out_subcycle')
        n_nvsqr = nfluids * 3 / self('nvsqr_out_subcycle')
        return n_global + n_den + n_flux + n_nvsqr

    @known_pattern(r'safe_snap_(|M|G)bytes(|32|64)',
                   deps=['arrays_per_snap', {(0,1): 'safe_data_array_{group0}bytes{group1}'}])
    def get_safe_snap_bytes(self, var, *, _match=None):
        '''average number of bytes per snapshot (excluding vdist arrays) if using 'safe' inputs.
        safe_snap_bytes = arrays_per_snap * safe_data_array_bytes
        pattern: Mbytes or Gbytes to get MB or GB. Uses 1024 not 1000 (e.g. MB --> 1024**2.)
        pattern: bytes32 or bytes64 to specify dtype. Unspecified --> float32.
        '''
        M, dtype = _match.groups()
        n_per_snap = self('arrays_per_snap')
        arr_bytes = self(f'safe_data_array_{M}bytes{dtype}')
        return n_per_snap * arr_bytes

    @known_pattern(r'safe_total_(|M|G)bytes(|32|64)',
                   deps=['safe_nsnaps', {(0,1): 'safe_snap_{group0}bytes{group1}'}])
    def get_safe_total_bytes(self, var, *, _match=None):
        '''total number of bytes expected (excluding vdist) across all snaps, if using 'safe' inputs.
        safe_total_bytes = safe_nsnaps * safe_snap_bytes
        pattern: Mbytes or Gbytes to get MB or GB. Uses 1024 not 1000 (e.g. MB --> 1024**2.)
        pattern: bytes32 or bytes64 to specify dtype. Unspecified --> float32.
        '''
        M, dtype = _match.groups()
        nsnaps = self('safe_nsnaps')
        snap_bytes = self(f'safe_snap_{M}bytes{dtype}')
        return nsnaps * snap_bytes


    # # # NUMBER OF PROCESSORS TO USE # # #

    cls_behavior_attrs.register('tasks_per_node', default=56)
    tasks_per_node = simple_property('_tasks_per_node', default=56,
        doc='''number of processers per node to use for eppic run. Default 56 works well on Frontera.
        n_processors = n_nodes * n_tasks_per_node.
        Utilized by safe_runtime_seconds computations.''')

    @known_var
    def get_tasks_per_node(self):
        '''number of tasks per node to use for eppic run.
        internally, value is stored (and can be adjusted) at self.tasks_per_node.
        '''
        return xr.DataArray(self.tasks_per_node)

    cls_behavior_attrs.register('n_nodes', default=4)
    n_nodes = simple_property('_n_nodes', default=4,
        doc='''number of nodes to use for eppic run. Default 4.
        (n_processors = n_nodes * n_tasks_per_node.)
        Utilized by safe_cpu_seconds_... computations
            (because 'efield' and 'collect' runtime per node depends on n_nodes,
            because mpi communication is more expensive with more nodes).

        Can be set to DataArray if desired. Common examples:
            # minimum number of nodes 
            ec.n_nodes = ec('min_n_nodes')  # 
            ec.n_nodes = ec('min_n_nodes_given_nsubdomains')  # min allowed n_nodes (lowest node-hour cost)''')

    @known_var
    def get_n_nodes(self):
        '''number of nodes to use for eppic run.
        Larger is always more expensive (in cpu hours), but can reduce wall clock time
            (caution: large n_nodes can mean more nodes actually increases wall clock time,
                due to increased mpi communication costs.)
        internally, value is stored (and can be adjusted) at self.n_nodes.
            For more details see help(type(self).n_node) or self.help_call_options('n_nodes')
        '''
        return xr.DataArray(self.n_nodes)

    cls_behavior_attrs.register('max_runtime_hours', default=48)
    max_runtime_hours = simple_property('_max_runtime_hours', default=48,
        doc='''maximum allowed runtime, in wall clock hours. Default 48.
        Utilized by min_n_nodes computations.
            (less nodes always costs fewer node hours, but might take way too long).
        Can be set to DataArray if desired, to check multiple options at once.''')

    @known_var
    def get_max_runtime_hours(self):
        '''maximum allowed runtime, in wall clock hours.
        Utilized by min_n_nodes computations.
            (less nodes always costs fewer node hours, but might take way too long).
        internally, value is stored (and can be adjusted) at self.max_runtime_hours.
        '''
        return xr.DataArray(self.max_runtime_hours)

    cls_behavior_attrs.register('min_n_nodes_lims', default=(4, 2048))
    min_n_nodes_lims = simple_property('_min_n_nodes_lims', default=(4, 2048),
        doc='''two-tuple of min & max values to test for, during min_n_nodes computations.
        (4, 512) corresponds to (smallest, largest) power of 2 allowed in Frontera 'normal' queue.
            Default goes up to 2048 to allow for 'large' queue requests too.''')

    @known_var(deps=['safe_runtime_seconds', 'max_runtime_hours'])
    def get_min_n_nodes_given_runtime_guess(self):
        '''minimum number of nodes, given safe_runtime_seconds and max_runtime_hours,
        to ensure safe_runtime_seconds < max_runtime_hours * 3600,
            or use max_min_n_nodes if safe_runtime_seconds > max_runtime_hours.

        Only tests powers-of-2 between self.min_n_nodes_lims [0] and [1], inclusive.
        '''
        test_vals = [2**i for i in range(int(np.log2(self.min_n_nodes_lims[0])),
                                         int(np.log2(self.min_n_nodes_lims[1]) + 1))]
        test = xr1d(test_vals, '__checking__min_n_nodes_given_runtime_guess__')
        cache = dict(_cached_safe_pow2_subcycle=self('safe_pow2_subcycle'))  # [EFF] cache expensive vars
        #cache = dict()
        with self.using(n_nodes=test, **cache):
            safe_runtime_seconds = self('safe_runtime_seconds')
            max_runtime_seconds = self('max_runtime_hours') * 3600
        not_too_long = safe_runtime_seconds <= max_runtime_seconds
        result = test.where(not_too_long).min('__checking__min_n_nodes_given_runtime_guess__')
        if not result.isnull().any():   # store as 'int' if it won't override nan or inf values.
            result = result.astype('int')
        return result

    @known_var(deps=['min_n_nodes_given_runtime_guess', 'min_n_nodes_given_nsubdomains'])
    def get_min_n_nodes(self):
        '''minimum number of nodes, given runtime guess, max_runtime_hours, nsubdomains, and tasks_per_node.
        Ensures the following:
            (1) n_processors % nsubdomains == 0,
                where n_processors = n_nodes * tasks_per_node.
                (This is ensured by min_n_nodes_given_nsubdomains.)
            (2) safe_runtime_seconds < max_runtime_hours * 3600,
                or use max_min_n_nodes if safe_runtime_seconds > max_runtime_hours.
                (This is ensured by min_n_nodes_given_runtime_guess.)

        Equivalent: maximum(min_n_nodes_given_runtime_guess, min_n_nodes_given_nsubdomains)
        '''
        return np.maximum(self('min_n_nodes_given_runtime_guess'), self('min_n_nodes_given_nsubdomains'))


    # # # RUNTIME STUFF # # #

    cls_behavior_attrs.register('runtime_safety', default=DEFAULTS.EPPIC.RUNTIME_SAFETY)
    runtime_safety = simple_property('_runtime_safety', setdefault=lambda: DEFAULTS.EPPIC.RUNTIME_SAFETY,
        doc=f'''safety factor for safe runtime calculations. Larger is LESS safe.
        safe_cpu_seconds = unsafe_cpu_seconds * runtime_safety.
        Default: DEFAULTS.EPPIC.RUNTIME_SAFETY (default: {DEFAULTS.EPPIC.RUNTIME_SAFETY})''')

    @known_var
    def get_runtime_safety(self):
        '''safety factor for safe runtime calculations. Larger is LESS safe.
        safe_cpu_seconds = unsafe_cpu_seconds * runtime_safety.
        internally, value is stored (and can be adjusted) at self.runtime_safety.
        '''
        return self.runtime_safety

    @known_var(deps=['safe_pow2_Nspace', 'ndim_space', 'guess_cpu_seconds_sum_per_ct_safe', 'runtime_safety'])
    def get_safe_cpu_seconds_per_timestep(self):
        '''safety factors * cpu seconds expected per timestep, for simulation using 'safe' inputs.
        unsafe_result = (safe_pow2_Nspace ** ndim_space) * guess_cpu_seconds_sum_per_ct_safe
        safe_result = unsafe_result * runtime_safety.
        '''
        with self.using(_cached_safe_pow2_subcycle=self('safe_pow2_subcycle')):  # [EFF] cache avoids recalculating
            safe_ncells = self('safe_pow2_Nspace') ** self('ndim_space')
            unsafe_result = safe_ncells * self('guess_cpu_seconds_sum_per_ct_safe')
        return unsafe_result * self('runtime_safety')

    @known_var(deps=['safe_rounded_nt', 'safe_cpu_seconds_per_timestep'])
    def get_safe_cpu_seconds(self):
        '''safety factors * cpu seconds expected in total, for simulation using 'safe' inputs.
        result = safe_rounded_nt * safe_cpu_seconds_per_timestep

        To get required wall clock seconds, divide by number of processors.
        '''
        cached = dict(_cached_safe_pow2_Nspace=self('safe_pow2_Nspace'),
                      _cached_safe_dt=self('safe_dt'))
        with self.using(**cached):  # [EFF] caching on most expensive vars to avoid recalculating.
            return self('safe_rounded_nt') * self('safe_cpu_seconds_per_timestep')

    @known_var(deps=['n_processors', 'safe_cpu_seconds'])
    def get_safe_runtime_seconds(self):
        '''predicted run cost, in wall clock time [seconds]. safe_cpu_seconds / number of processors.
        n_processors = self.n_nodes * self.tasks_per_node.
        '''
        return self('safe_cpu_seconds') / self('n_processors')

    @known_var(deps=['safe_runtime_seconds'])
    def get_safe_runtime_HMS(self):
        '''predicted run cost, in wall clock time [string like: 'hh:mm:ss'].'''
        value = self('safe_runtime_seconds')
        hh_num = (value / 3600).astype('int')
        hh_str = hh_num.astype('str').str.zfill(2)
        mm_num = ((value - hh_num * 3600) / 60).astype('int')
        mm_str = mm_num.astype('str').str.zfill(2)
        ss_num = (value - hh_num * 3600 - mm_num * 60).astype('int')
        ss_str = ss_num.astype('str').str.zfill(2)
        colon_str = xr.DataArray(':')
        result = xr.concat([hh_str, colon_str, mm_str, colon_str, ss_str], dim='__to_join__', coords='minimal')
        return result.str.join('__to_join__')

    @known_var(deps=['safe_cpu_seconds', 'tasks_per_node'])
    def get_safe_node_hours(self):
        '''predicted run cost, in node hours. safe_cpu_seconds * seconds2hours / tasks_per_node.
        (seconds2hours = 1 / 3600)

        Compare directly with Frontera SU cost (1 SU is 1 node-hour in 'normal' partition).
        '''
        seconds2hours = 1 / 3600
        return self('safe_cpu_seconds') * seconds2hours / self('tasks_per_node')

    @known_var(deps=['safe_pow2_Nspace', 'guess_cpu_seconds_sum_per_ct'])
    def get_unsafe_cpu_seconds_per_timestep(self):
        '''cpu seconds expected per timestep, with no runtime_safety and no safety inside guess_cpu.
        safe_pow2_Nspace * guess_cpu_seconds_sum_per_ct  (without _safe)
        '''
        return self('safe_pow2_Nspace') * self('guess_cpu_seconds_sum_per_ct')

    @known_var(deps=['safe_cpu_seconds_per_timestep', 'unsafe_cpu_seconds_per_timestep'])
    def get_direct_runtime_safety(self):
        '''direct_runtime_safety = safe_cpu_seconds_per_timestep / unsafe_cpu_seconds_per_timestep.'''
        return self('safe_cpu_seconds_per_timestep') / self('unsafe_cpu_seconds_per_timestep')


    # # # SIMULATION SAFETY FACTORS DETAILS # # #
    # e.g. what were the input safety factors?
    # e.g. what were the effective, "direct", safety factors (accounting for pow2 rounding)?

    SAFETY_DETAILS_VARS = [
        'dspace_safety', 'direct_dspace_safety',
        'nspace_safety', 'direct_nspace_safety',
        'dt_safety', 'direct_dt_safety',
        'ntime_safety', 'direct_ntime_safety',
        'nout_waveprop_safety', 'direct_nout_waveprop_safety',
        'nout_growth_safety', 'direct_nout_growth_safety',
        # runtime
        'runtime_safety', 'direct_runtime_safety',
    ]
    @known_var(deps=SAFETY_DETAILS_VARS)
    def get_safety_details(self):
        '''dataset with various values related to safety factors used in 'safe' inputs.
        Equivalent: self(self.SAFETY_DETAILS_VARS)
        '''
        cached = dict(_cached_safe_pow2_Nspace=self('safe_pow2_Nspace'),
                        _cached_safe_dt=self('safe_dt'),
                        _cached_safe_pow2_subcycle=self('safe_pow2_subcycle'))
        with self.using(**cached):  # [EFF] caching on most expensive vars to avoid recalculating.
            return self(self.SAFETY_DETAILS_VARS)
