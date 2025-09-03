"""
File Purpose: BifrostDirectLoader
"""
import os

import numpy as np
import xarray as xr

from ...defaults import DEFAULTS
from ...errors import CacheNotApplicableError, SnapValueError, DimensionalityError
from ...tools import (
    simple_property,
    product,
)
from ...quantities import DirectLoader


### --------------------- BifrostDirectLoader --------------------- ###

class BifrostDirectLoader(DirectLoader):
    '''manages loading data directly from bifrost output files.'''
    
    _slice_maindims_in_load_direct = True   # tell MainDimensionsHaver to let us handle slicing logic here.

    # # # PROPERTIES AFFECTING DIRECT LOADING # # #
    cls_behavior_attrs.register('stagger_direct', default=True)
    stagger_direct = simple_property('_stagger_direct', default=True,
            doc='''whether to stagger arrays to cell centers when loading directly from file.
            if all arrays are at cell centers, don't need to worry about stagger anymore.
            else, need to be sure to align arrays before doing calculations on them.''')

    cls_behavior_attrs.register('squeeze_direct', default=True)
    squeeze_direct = simple_property('_squeeze_direct', default=True,
            doc='''whether to squeeze arrays when loading directly from file.
            if True, remove dimensions of size 1, and alter self.maindims appropriately.''')

    def _maindims_post_squeeze(self):
        '''returns tuple of maindims remaining after squeezing if applicable. E.g. ('x', 'z').
        If not squeeze_direct or if 3D run, maindims will be ('x', 'y', 'z').
        Otherwise, remove any dims with size 1.
        '''
        if not self.squeeze_direct:
            return ('x', 'y', 'z')
        else:
            data_shape = (self.params['mx'], self.params['my'], self.params['mz'])
            return tuple(d for d, size in zip(('x', 'y', 'z'), data_shape) if size > 1)

    def _squeeze_direct_result__post_slicing(self, array):
        '''squeeze result of direct loading (maybe actually load_fromfile), after self.slices have been applied.
        only squeezes the dims for which self.data_array_shape shows size 1.
        returns array, possibly squeezed.
        '''
        to_squeeze = [d for d, size in zip(('x', 'y', 'z'), self.data_array_shape) if size == 1]
        if len(to_squeeze)>0:
            already_removed = self._slices_which_scalarize()  # list of dims which slicing removed.
            if array.ndim != 3 - len(already_removed):
                raise DimensionalityError('squeeze_direct cannot account for all dims.')
            array_dims = [x for x in ('x', 'y', 'z') if x not in already_removed]
            indexers = [0 if d in to_squeeze else slice(None) for d in array_dims]
            array = array[tuple(indexers)]   # e.g. equivalent: array[:, 0, :] if squeezing y only.
        return array

    def _slice_direct_numpy(self, array):
        '''self._slice_maindims_numpy(array), but using self.squeeze_direct=False.
        Can apply this directly to arrays loaded from memmaps.
        Cannot apply this to arrays after squeezing.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        with self.using(squeeze_direct=False):
            return self._slice_maindims_numpy(array)

    # # # DIRECT STAGGER INSTRUCTIONS # # #
    # {fromfile_var: ops to perform on var to align it to grid cell centers}
    _STAGGER_DIRECT_TO_CENTER_OPS = {
        # snap vars
        'r': None, 'e': None,  # None means no ops needed
        'px':'xup', 'py':'yup', 'pz':'zup',
        'bx':'xup', 'by':'yup', 'bz':'zup',
        # other vars: ??? (any other directly loadable vars that need staggering?)
        # (e.g.: 'efx': 'yup zup', 'efy': 'xup zup', 'efz': 'xup yup')
    }

    def _stagger_direct_to_center__then_slice(self, array, fromfile_var):
        '''stagger directly loaded data array (of fromfile_var values) to cell centers.
        Then slice, if self._slice_maindims_in_load_direct.

        Instructions for how to stagger to center depends on fromfile_var.
        if fromfile_var doesn't require any ops to center it, do nothing.

        array: numpy array
            the numpy array of data from file. (memmap is okay too.)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        ops = self._STAGGER_DIRECT_TO_CENTER_OPS.get(fromfile_var, None)
        if ops is None:
            return self._slice_direct_numpy(array)
        # else, stagger array to cell centers, then slice.
        return self._stagger_direct_and_slice(array, ops)

    # # # FILE PATH INFO # # #
    @property
    def snapdir(self):
        '''directory containing the snapshot files.
        Here, gives self.dirname, because Bifrost outputs are stored at top-level of directory.
        '''
        return self.dirname

    def snap_filepath(self, snap=None):
        '''convert snap to full file path for this snap, i.e. to the snapname_NNN.idl file.'''
        snap = self._as_single_snap(snap)
        dir_ = self.snapdir
        file_s = snap.file_s(self) if hasattr(snap, 'file_s') else str(snap)
        filename = os.path.join(dir_, f'{self.snapname}_{file_s}.idl')
        return filename

    # # # DIRECT LOADING-RELATED INFO # # #
    def directly_loadable_vars(self, snap=None):
        '''return tuple of directly loadable variables for this snap.

        snap: None, str, int, Snap, or iterable indicating multiple snaps.
            the snapshot number to load. if None, use self.snap.
            if multiple snaps, return the result if all snaps have same result, else crash.
        '''
        kw = dict() if snap is None else dict(snap=snap)
        with self.using(**kw):
            multiple_snaps = self.snap_is_iterable()
            if multiple_snaps:
                snaps = self.snap
            else:
                snaps = [self._as_single_snap(snap)]
        result = None
        for snap in snaps:
            # result for this snap
            if hasattr(snap, 'exists_for') and not snap.exists_for(self):
                result_here = np.nan
            else:
                vpm = snap.var_paths_manager(self)
                result_here = vpm.vars
            # compare against known result
            if result is None:
                result = result_here
            elif result != result_here:
                errmsg = 'directly_loadable_vars differ between snaps. Retry with single snap instead.'
                raise SnapValueError(errmsg)
            # else, continue
        return result

    def var_paths_manager(self, snap=None):
        '''return VarPathsManager for this snap (or current snap if None provided)'''
        snap = self._as_single_snap(snap)
        return snap.var_paths_manager(self)

    @property
    def data_array_shape(self):
        '''shape of each data array. ('mx', 'my', 'mz') from self.params.
        Assumes shape is the same for all snaps; will crash if not.
        '''
        return (self.params['mx'], self.params['my'], self.params['mz'])

    @property
    def data_array_size(self):
        '''array size (number of elements) of each data array. (from data_array_shape)'''
        return product(self.data_array_shape)

    data_array_dtype = simple_property('_data_array_dtype', default=np.dtype('float32'),
            doc='''numpy dtype of each data array. default is np.dtype('float32').
            Used by np.memmap during self.load_fromfile.''')

    @property
    def data_array_nbytes(self):
        '''number of bytes in each data array. (from data_array_size and data_array_dtype)'''
        return self.data_array_size * self.data_array_dtype.itemsize

    data_array_order = simple_property('_data_array_order', default='F',
            doc='''ordering of data array axes: 'F' (Fortran) or 'C' (C order). Default 'F'.''')

    # # # LOAD FROMFILE # # #
    def _var_for_load_fromfile(self, varname_internal):
        '''return var, suitably adjusted to pass into load_fromfile().
        Here:
            append self.component if self._loading_component
        E.g. 'b' turns into 'bz' when loading 'z' component.
        '''
        result = varname_internal
        if getattr(self, '_loading_component', False):
            result = result + str(self.component)
        return result

    def load_fromfile(self, fromfile_var, *args__None, snap=None, **kw__None):
        '''return numpy array of fromfile_var, loaded directly from file.

        fromfile_var: str
            the name of the variable to read, adjusted appropriately for loading fromfile.
            E.g. use 'bz' not 'b', to get magnetic field z-component.
            See also: self._var_for_load_fromfile().
        snap: None, str, int, or Snap
            the snapshot number to load. if None, use self.snap.
        '''
        snap = self._as_single_snap(snap)  # expect single snap when loading from file.
        if hasattr(snap, 'exists_for') and not snap.exists_for(self):
            result = xr.DataArray(self.snap_dim.NAN, attrs=dict(units='raw'))
            return self.assign_snap_coord(result)  # [TODO][EFF] assign coords when making array instead...
        vpm = snap.var_paths_manager(self)
        filepath = vpm.var2path[fromfile_var]
        offset = vpm.var2index[fromfile_var] * self.data_array_nbytes
        result = np.memmap(filepath, offset=offset,
                           mode='r',  # read-only; never alters existing files!
                           shape=self.data_array_shape,
                           dtype=self.data_array_dtype,
                           order=self.data_array_order,
                           )
        result = np.asarray(result)  # convert to numpy array.
        if self.squeeze_direct:  # squeeze bookkeeping before applying any self.slices.
            assert result.shape == self.data_array_shape, "pre-squeeze shape check failed."
        if self.stagger_direct:
            result = self._stagger_direct_to_center__then_slice(result, fromfile_var)
        else:
            result = self._slice_direct_numpy(result)
        if self.squeeze_direct:
            result = self._squeeze_direct_result__post_slicing(result)
        return result
