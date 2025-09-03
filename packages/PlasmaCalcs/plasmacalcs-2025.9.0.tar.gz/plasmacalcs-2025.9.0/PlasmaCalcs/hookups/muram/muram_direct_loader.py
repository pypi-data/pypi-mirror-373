"""
File Purpose: MuramDirectLoader
"""
import os

import numpy as np
import xarray as xr

from ...defaults import DEFAULTS
from ...errors import CacheNotApplicableError, SnapValueError
from ...quantities import DirectLoader
from ...tools import (
    simple_property,
    product,
)


### --------------------- MuramDirectLoader --------------------- ###

class MuramDirectLoader(DirectLoader):
    '''manages loading data directly from bifrost output files.'''

    # # # FILE PATH INFO # # #
    @property
    def snapdir(self):
        '''directory containing the snapshot files.
        Here, gives self.dirname, because Muram outputs are stored at top-level of directory.
        '''
        return self.dirname

    def snap_filepath(self, snap=None):
        '''convert snap to full file path for this snap, i.e. to the Header.NNN file.'''
        snap = self._as_single_snap(snap)
        return snap.filepath

    # # # DIRECT LOADING-RELATED INFO # # #
    def directly_loadable_vars(self, snap=None):
        '''return tuple of directly loadable variables for this snap.

        snap: None, str, int, Snap, or iterable indicating multiple snaps.
            None --> use self.snap.
            multiple snaps --> return result if all snaps have same result, else crash.
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
                result_here = snap.directly_loadable_vars()
            # compare against known result
            if result is None:
                result = result_here
            elif result != result_here:
                errmsg = 'directly_loadable_vars differ between snaps. Retry with single snap instead.'
                raise SnapValueError(errmsg)
            # else, continue
        return result

    @property
    def data_array_shape(self):
        '''shape of each array of data stored in files. ('N0', 'N1', 'N2') from self.params.
        Shape with (x, y, z) dimensions is some transposition of the result;
        transpose order stored in 'layout.order' file, see also self.params['order'].
        '''
        return (self.params['N0'], self.params['N1'], self.params['N2'])

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
    _RESULT_PRIM_VAR_TO_FILEBASE = {
        'result_prim_r': 'result_prim_0',
        'result_prim_ux': 'result_prim_1',
        'result_prim_uy': 'result_prim_2',
        'result_prim_uz': 'result_prim_3',
        'result_prim_e': 'result_prim_4',
        'result_prim_bx': 'result_prim_5',
        'result_prim_by': 'result_prim_6',
        'result_prim_bz': 'result_prim_7',
    }

    def _var_for_load_fromfile(self, varname_internal):
        '''return var, suitably adjusted to pass into load_fromfile().
        Here, follow the steps:
            (1) if self._loading_component, append self.component.
                E.g. 'result_prim_b' turns into 'result_prim_bz' when loading 'z' component.
            (2) convert result_prim_... via self._RESULT_PRIM_VAR_TO_FILEBASE, if applicable.
                E.g. 'result_prim_bx' becomes 'result_prim_5'.
        '''
        result = varname_internal
        if getattr(self, '_loading_component', False):
            result = result + str(self.component)
        result = self._RESULT_PRIM_VAR_TO_FILEBASE.get(result, result)
        return result

    # # # LOAD FROMFILE # # #
    def load_fromfile(self, fromfile_var, *args__None, snap=None, **kw__None):
        '''return numpy array of fromfile_var, loaded directly from file.

        fromfile_var: str
            the name of the variable to read, adjusted appropriately for loading fromfile.
            E.g. use 'result_prim_5' not 'bx', to get magnetic field x-component.
            See also: self._var_for_load_fromfile().
        snap: None, str, int, or Snap
            the snapshot number to load. if None, use self.snap.
        '''
        snap = self._as_single_snap(snap)  # expect single snap when loading from file.
        if hasattr(snap, 'exists_for') and not snap.exists_for(self):
            result = xr.DataArray(self.snap_dim.NAN, attrs=dict(units='raw'))
            return self.assign_snap_coord(result)  # [TODO][EFF] assign coords when making array instead...
        filepath = os.path.join(snap.dirname, f'{fromfile_var}.{snap.s}')
        result = np.memmap(filepath,
                           mode='r',  # read-only; never alters existing files!
                           shape=self.data_array_shape,
                           dtype=self.data_array_dtype,
                           order=self.data_array_order,
                           )
        result = result.transpose(self.params['order'])  # transpose to match maindims order ('x', 'y', 'z').
        result = np.asarray(result)  # convert to numpy array.
        return result
