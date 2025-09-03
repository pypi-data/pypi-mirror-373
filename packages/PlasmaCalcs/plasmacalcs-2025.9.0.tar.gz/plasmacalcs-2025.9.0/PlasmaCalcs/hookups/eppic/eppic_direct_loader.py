"""
File Purpose: EppicDirectLoader
"""
import os
import math  # for lcm...

# required external modules
import numpy as np
import xarray as xr

# optional external modules
from ...tools import ImportFailed
try:
    import h5py
except ImportError as err:
    h5py = ImportFailed("h5py", err=err, locals=locals())
try:
    import openpmd_api as io
except ImportError as err:
    openpmd_api = ImportFailed("openpmd_api", err=err, locals=locals())

# internal modules
from ...dimensions import INPUT_SNAP
from ...errors import (
    LoadingNotImplementedError,
    InputError,
)
from ...quantities import DirectLoader, QuasineutralLoader
from ...tools import interprets_fractional_indexing
from ...defaults import DEFAULTS


### --------------------- EppicDirectLoader --------------------- ###

class EppicDirectLoader(DirectLoader, QuasineutralLoader):
    '''manages loading data directly from eppic output files.

    input_deck: EppicInputDeck
        input deck. E.g. EppicInputDeck.from_file('eppic.i').
        Currently, requires that input_deck.filename is not None.
    read_mode: str
        how to read the files.
        Currently, must be 'h5' or 'h5_2'. See help(EppicDirectLoader.read_mode) for details.

    attributes of self (not available at __init__)
    '''
    # parent class ordering notes: no consistent mro() if QuasineutralLoader before DirectLoader.
    #  (related to DirectLoader being a SnapHaver, but not exactly sure why the error happens.
    #   but DirectLoader first here is fine; it doesn't overlap with QuasineutralLoader methods.)

    _h5_zfill = DEFAULTS.EPPIC.H5_SNAP_ZFILL
    _slice_maindims_in_load_direct = True   # [EFF] slice directly when reading h5 files, if using self.slices

    def __init__(self, input_deck, *, read_mode='h5', **kw_super):
        self.input_deck = input_deck
        self.read_mode = read_mode
        super().__init__(**kw_super)

    # # # READ MODE AND SNAPDIR # # #
    @property
    def read_mode(self):
        '''mode telling which files to read.
        Currently, must be 'h5' or 'h5_2'
        Maybe other modes will be added at some point.

        Options:
            'h5' --> read from .h5 files,
                    determine file format based on input_deck['hdf_output_arrays'].
            'h5_2' --> read from .h5 files,
                    assuming input_deck['hdf_output_arrays']==2.
        '''
        return self._read_mode
    @read_mode.setter
    def read_mode(self, value):
        if value != 'h5' and value != 'h5_2' and value != 'h5_3' and value != 'h5_4':
            raise ValueError(f'read_mode {value!r} not supported.')
        self._read_mode = value

    @property
    def full_read_mode(self):
        '''full read_mode, including hdf_output_arrays information.'''
        read_mode = self.read_mode
        if read_mode == 'h5':
            hdf_output_arrays = self.input_deck['hdf_output_arrays']
            return f'{read_mode}_{hdf_output_arrays}'
        else:
            return read_mode

    @property
    def snapdir(self):
        '''directory containing the snapshot files.
        If self.full_read_mode=='h5_2' or 'h5_3' or 'h5_4',
        this is '{self.dirname}/parallel'.
        Otherwise, this will crash with a NotImplementedError.
        '''
        if self.full_read_mode == 'h5_2' or self.full_read_mode == 'h5_3' or self.full_read_mode == 'h5_4':
            return os.path.join(self.input_deck.dirname, 'parallel')
        else:
            raise NotImplementedError(f'{type(self).__name__}.snapdir, when read_mode={self.full_read_mode!r}')

    def snap_filepath(self, snap=None):
        '''convert snap to full file path for this snap.

        snap: None, str, int, or Snap
            the snapshot number to load.
            if None, use self.snap.
        '''
        if self.full_read_mode == 'h5_2' or self.full_read_mode == 'h5_3' or self.full_read_mode == 'h5_4':
            return self._h5_2_filename(snap=snap)
        else:
            raise NotImplementedError(f'{type(self).__name__}.snap_filepath, when read_mode={self.full_read_mode!r}')


    # # # LOAD FROMFILE # # #
    def _var_for_load_fromfile(self, varname_internal):
        '''return var, suitably adjusted to pass into load_fromfile().
        Here:
            append self.component if self._loading_component
            append self.fluid.N if self._loading_fluid
        E.g. 'flux' turns into 'fluxz2' when loading 'z' component and fluid 2.
        '''
        result = varname_internal
        if getattr(self, '_loading_component', False):
            result = result + str(self.component)
        if getattr(self, '_loading_fluid', False):
            result = result + str(self.fluid.N)
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
            fromfile_var='fluxx1', snap=7, read_mode='h5_2'
                --> h5py.File('parallel/parallel000007.h5')['fluxx1'][:]
        '''
        snap = self._as_single_snap(snap)  # expect single snap when loading from file.
        if hasattr(snap, 'exists_for') and not snap.exists_for(self):
            result = xr.DataArray(self.snap_dim.NAN, attrs=dict(units='raw'))
            return self.assign_snap_coord(result)  # [TODO][EFF] assign coords when making array instead...
        if snap is INPUT_SNAP:
            raise LoadingNotImplementedError(f'var={fromfile_var!r}, when snap is INPUT_SNAP')
        full_read_mode = self.full_read_mode
        if full_read_mode == 'h5_2':
            return self._h5_2_load_fromfile(fromfile_var, *args, snap=snap, **kw)
        elif full_read_mode == 'h5_3' or full_read_mode == 'h5_4':
            return self._openpmd_load_fromfile(fromfile_var, *args, snap=snap, **kw)
        # reaching this line means the read mode is not recognized.
        raise LoadingNotImplementedError(f'unsupported full_read_mode: {full_read_mode!r}')

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
        full_read_mode = self.full_read_mode
        if full_read_mode == 'h5_2':
            result = list(self._h5_2_directly_loadable_vars(snap=snap))
        elif full_read_mode == 'h5_3' or full_read_mode == 'h5_4':
            result = list(self._openpmd_directly_loadable_vars(snap=snap))
        return result

    def wheref_loadable(self, var=None, snaps=None, *, set=False):
        '''returns snaps from self.snaps where 'n', 'flux', 'nvsqr', 'vdist', 'phi' values can be loaded,
        for all fluids currently in self.fluid (for non-phi vars).
        [EFF] method is IMPLICIT, based on var_out_subcycling details for each fluid.
            Does not actually check the files directly, because it's expensive to do that.

        [TODO] account for subsampling_info too.

        var: None, list of str, str from ('n', 'flux', 'nvsqr', 'vdist', 'phi'), or 'all'
            None --> return dict of answer for each of those vars
            'all' --> return SnapList where all vars are loadable.
            list --> return SnapList where all vars in list are loadable.
            str --> return SnapList for this var only.
        snaps: None, 'current', 'current_range', 'current_n', or SnapList
            the snaps to consider.
            None --> self.snaps.
            'current' --> self.snap
            'current_range' --> self.snaps.select_between(self.snap[0].t, self.snap[-1].t)
            'current_n' --> 'current_range', but evently downsample result size similar to current n snap.
                        (note: even downsampling isn't always possible; result size won't exactly match.
                         useful if you want "roughly N snaps". See example below.)
            E.g. if self.snap [10,20,30,...,200] (len=19), and self.snaps [0,...,300] (len=301),
                checking where_loadable(var) which is available every 4 snaps, result will be:
                None --> [0,4,8,...,300] (len=76)
                'current' --> [20,40,...,200] (len=10)  # because 10,30,50,... aren't divisible by 4
                'current_range' --> [12,16,20,...,200] (len=48)
                'current_n' --> [12,20,28,...,200] (len=24)
                                # because interprets_fractional_indexing(slice(None,None,1/19), L=48)
                                # gives slice(0, None, 2), which is then applied to current_range result.
        set: bool
            if True, also set self.snap = result.
        '''
        result = {}
        downsample = False
        if snaps is None:
            snaps = self.snaps
        elif isinstance(snaps, str):
            if snaps=='current':
                snaps = self.snap_list()
            elif snaps=='current_range' or snaps=='current_n':
                snaplist = self.snap_list()
                if snaps == 'current_n': downsample = len(snaplist)
                snaps = self.snaps.select_between(snaplist[0].t, snaplist[-1].t)
            else:
                raise InputError(f'got str snaps={snaps!r}, expected "current" or "current_range"')
        combine = False
        KNOWN = ('n', 'flux', 'nvsqr', 'vdist', 'phi')
        if var is None:
            vars_ = KNOWN
        elif isinstance(var, str):
            if var == 'all':
                combine = True
                vars_ = KNOWN
            else:
                vars_ = [var]
        else:  # list of vars
            combine = True
            vars_ = var
        unknown = [v for v in vars_ if v not in KNOWN]
        if len(unknown) > 0:
            raise InputError(f'unsupported var(s): {unknown!r}. Expected only vars from: {KNOWN!r}')
        nout = self.input_deck['nout']
        subcycles = {}
        FLUID_VARS = {
            'n': 'part_out_subcycle',
            'flux': 'flux_out_subcycle',
            'nvsqr': 'nvsqr_out_subcycle',
            'vdist': 'vdist_out_subcycle',
        }
        for v, subvar in FLUID_VARS.items():
            if v in vars_:
                subcycle = 1
                for fluid in self.iter_fluid():
                    subcycle = math.lcm(subcycle, fluid.get(subvar, 1))
                subcycles[v] = subcycle
        if 'phi' in vars_:
            subcycles['phi'] = self.input_deck.get('phi_out_subcycle', 1)
        if combine:  # combine the subcycles
            subcycle = 1
            for v, sc in subcycles.items():
                subcycle = math.lcm(subcycle, sc)
            var = 'COMBINED'
            subcycles = {var: subcycle}
        for v, subcycle in subcycles.items():
            if subcycle == 1:
                result[v] = snaps
            else:
                igood = [i for i, snap in enumerate(snaps) if int(snap.s) % (subcycle * nout) == 0]
                result[v] = snaps[igood]
        # downsample maybe
        if downsample:
            for v, rr in result.items():
                if len(rr) > downsample:  # actually downsample this one :)
                    slicer = interprets_fractional_indexing(slice(None,None,1/downsample), L=len(rr))
                    result[v] = rr[slicer]
        if isinstance(var, str):
            result = result[var]
        # output (maybe set self.snap first, too)
        if set:
            self.snap = result
        return result

    def where_loadable(self, var=None, snaps=None, *, set=False):
        '''returns snaps from self.snaps where 'n', 'flux', 'nvsqr', 'vdist', 'phi' values can be loaded,
        for ALL fluids in self.fluids.
        Equivalent:
            with self.using(fluid=None):
                return self.wheref_loadable(var=var, snaps=snaps)

        [EFF] method is IMPLICIT, based on var_out_subcycling details for each fluid.
            Does not actually check the files directly, because it's expensive to do that.

        [TODO] account for subsampling_info too.

        var: None, list of str, str from ('n', 'flux', 'nvsqr', 'vdist', 'phi'), or 'all'
            None --> return dict of answer for each of those vars
            'all' --> return SnapList where all vars are loadable.
            list --> return SnapList where all vars in list are loadable.
            str --> return SnapList for this var only.
        snaps: None, 'current', 'current_range', 'current_n', or SnapList
            the snaps to consider.
            None --> self.snaps.
            'current' --> self.snap
            'current_range' --> self.snaps.select_between(self.snap[0].t, self.snap[-1].t)
            'current_n' --> 'current_range', but evently downsample result size similar to current n snap.
                        (note: even downsampling isn't always possible; result size won't exactly match.
                         useful if you want "roughly N snaps". See example below.)
            E.g. if self.snap [10,20,30,...,200] (len=19), and self.snaps [0,...,300] (len=301),
                checking where_loadable(var) which is available every 4 snaps, result will be:
                None --> [0,4,8,...,300] (len=76)
                'current' --> [20,40,...,200] (len=10)  # because 10,30,50,... aren't divisible by 4
                'current_range' --> [12,16,20,...,200] (len=48)
                'current_n' --> [12,20,28,...,200] (len=24)
                                # because interprets_fractional_indexing(slice(None,None,1/19), L=48)
                                # gives slice(0, None, 2), which is then applied to current_range result.
        set: bool
            if True, also set self.snap = result.
        '''
        with self.using(fluid=None):
            return self.wheref_loadable(var=var, snaps=snaps, set=set)

    # # # H5_2 READ MODE # # #
    def _h5_2_load_fromfile(self, fromfile_var, *args__None, snap=None, **kw__None):
        '''return numpy array of var, loaded directly from file, using "h5_2" read_mode.
        This corresponds to h5 read mode with hdf_output_arrays=2.

        fromfile_var: str
            the name of the variable as stored in the snapshot.
        snap: None, str, int, or Snap
            the snapshot number to load.
            if None, use self.snap.

        Example:
            fromfile_var='fluxx1', snap=7
                --> h5py.File('parallel/parallel000007.h5')['fluxx1'][:]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        filename = self._h5_2_filename(snap=snap)
        if not os.path.exists(filename):
            raise FileNotFoundError(f'{os.path.abspath(filename)!r}')
        with h5py.File(filename, 'r') as file:
            try:
                result = file[fromfile_var]
            except KeyError:
                errmsg = f'var={fromfile_var!r} not recognized (in file {os.path.abspath(filename)!r})'
                raise LoadingNotImplementedError(errmsg)
            if getattr(self, '_slice_maindims_in_load_direct', False):
                # [EFF] slice here instead of reading all data then slicing later.
                preslice = result
                result = self._slice_maindims_numpy(result, h5=True)
                return result[:] if (result is preslice) else result  # if didn't slice yet, use [:] to read h5 data.
            else:
                return result[:]

    def _h5_2_filename(self, *, snap=None):
        '''return name of file from which to load values, for read_mode='h5_2'.

        snap: None, str, int, or Snap
            the snapshot number to load.
            if None, use self.snap.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        snap = self._as_single_snap(snap)
        dir_ = self.snapdir  # probably {dirname}/parallel
        file_s = snap.file_s(self) if hasattr(snap, 'file_s') else str(snap)
        snap00N = file_s.zfill(self._h5_zfill)  # e.g. '000017' if _h5_zfill=6, snap=17.
        filename = os.path.join(dir_, f'parallel{snap00N}.h5')
        if (self.full_read_mode == 'h5_4'):
            filename = filename.replace('.h5', '.bp')
        return filename

    def _h5_2_directly_loadable_vars(self, *, snap=None):
        '''return tuple of directly loadable variables, for read_mode='h5_2'.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        filename = self._h5_2_filename(snap=snap)
        with h5py.File(filename, 'r') as file:
            return tuple(file.keys())

    # # # OPENPMD READ MODE # # #
    def _openpmd_directly_loadable_vars(self, *, snap=None):
        '''return tuple of directly loadable variables, for read_mode='openpmd'.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        filename = self._h5_2_filename(snap=snap)
        
        series = io.Series(filename, io.Access.read_only)
        snap = self._as_single_snap(snap)
        i = series.iterations[int(str(snap))]
        meshes = [m for m, n in i.meshes.items()]
        return tuple(meshes)
    
    def _openpmd_load_fromfile(self, eppic_var, *args__None, snap=None, **kw__None):
        '''return numpy array of var, loaded directly from file, using "openpmd" read_mode.
        This corresponds to openpmd read mode.

        eppic_var: str
            the name of the variable as stored in the snapshot.
        snap: None, str, int, or Snap
            the snapshot number to load.
            if None, use self.snap.

        Example:
            eppic_var='fluxx1', snap=7
                --> zarr.open('data/000007/fields/fluid_2/fluxx1')
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        
        snap = self._as_single_snap(snap)
        if eppic_var not in self._openpmd_directly_loadable_vars(snap=snap):
            errmsg = f'var={eppic_var!r} not recognized'
            raise LoadingNotImplementedError(errmsg)
        
        filename = self._h5_2_filename(snap=snap)
        series = io.Series(filename, io.Access.read_only)
        i = series.iterations[int(str(snap))]
        
        try:
            var = i.meshes[eppic_var]
        except KeyError:
            errmsg = f'var={eppic_var!r} not recognized (in file {os.path.abspath(filename)!r})'
            raise LoadingNotImplementedError(errmsg)

        if getattr(self, '_slice_maindims_in_load_direct', False):
            slices = self.slices
            slices = [slices.get(dim, slice(None)) for dim in self.maindims]
            result = var[tuple(slices)]
        else:
            result = var[:]

        series.flush()
        series.close()
        return np.array(result[:])