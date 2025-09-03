"""
File Purpose: EppicSubsamplable
"""
import os
import re

# optional external modules
from ...tools import ImportFailed
try:
    import h5py
except ImportError as err:
    h5py = ImportFailed("h5py", err=err, locals=locals())

# internal imports
from .eppic_direct_loader import EppicDirectLoader
from ...dimensions import (
    Subsamplable,
)
from ...errors import SubsamplingError, SubsamplingFormatError
from ...tools import (
    UNSET,
)


### --------------------- EppicSubsamplable --------------------- ###

class EppicSubsamplable(EppicDirectLoader, Subsamplable):
    '''manages subsampling of EPPIC output, and interpreting subsampled EPPIC output.

    self.subsample() outputs to {self.dirname}/subsampling_result:
        subsampled snapshots go to subsampling_result/parallel  (assuming full_read_mode='h5_2')
        subsampling info goes to subsampling_result/subsampling_info

        Users may prefer the simpler version if just looking for simple slicing of snaps/x/y/z:
            self.subsample_simple_slices() can easily serve this purpose.

    self.subsampling_info by default reads info from {self.dirname}/subsampling_info.
        If that directory doesn't exist, it will be None, and assume there is no subsampling.

    snap src objects for EPPIC will be Snap objects, not filepaths.
    '''

    # # # SUBSAMPLING IMPLEMENTATION DETAILS (REQUIRED BY PARENT) # # #

    def subsampling_snap_srcs(self):
        '''list of all snap srcs in self (before applying any subsampling).
        Here, just returns self.snaps.
        '''
        return self.snaps

    def snap_src_to_filepath(self, src):
        '''convert snap src to filepath. Returns self.snap_filepath(src).'''
        return self.snap_filepath(src)

    def rawvars_loadable(self, src):
        '''returns list of all directly loadble vars within snap src.
        Used by subsampling routines. Basically just calls self.directly_loadable_vars.
        '''
        return self.directly_loadable_vars(snap=src)

    def rawvar_load(self, var, src):
        '''load a single raw var from snap src.
        Used by subsampling routines. Basically just calls self.load_fromfile.
        '''
        return self.load_fromfile(var, snap=src)

    def rawvar_save(self, var, data, dst):
        '''saves a single raw var to snap dst.
        crash if this would require overwriting any existing data at dst.
        '''
        with h5py.File(dst, 'a') as f:
            if var in f:
                raise SubsamplingError(f'var {var!r} already exists in dst={dst!r}.')
            f[var] = data

    def rawvar_load_and_subsample(self, var, src, info):
        '''returns var loaded and subsampled from src.'''
        applier = info.get_applier(var)
        if applier.mode == 'slice' and self.full_read_mode == 'h5_2':
            # [EFF] slice before loading full array.
            path = self.snap_filepath(src)
            if not os.path.exists(path):
                raise SubsamplingError(f'file {path!r} does not exist.')
            with h5py.File(path, 'r') as f:
                data_obj = f[var]
                subsampled = applier.apply(data_obj)
            return subsampled
        else: # less efficient but more generic: subsample after loading full array.
            return super().rawvar_load_and_subsample(var, src, info)


    # # # SUBSAMPLING CONVENIENT METHODS # # #

    def subsample_maindims_simple(self, *, snap=None, x=None, y=None, z=None, **kw_subsample):
        '''self.subsample(subsampling_info corresponding to slicing snaps and maindims, only).

        snap, x, y, z: None or slice
            slice for this dim.
        '''
        info = self.subsampling_info_maindims_simple(snap=snap, x=x, y=y, z=z, as_json=False)
        return self.subsample(info, **kw_subsample)

    def subsampling_info_maindims_simple(self, *, snap=None, x=None, y=None, z=None, as_json=False):
        '''SubsamplingInfo corresponding to slicing snaps and maindims, only.
        
        snap, x, y, z: None or slice
            slice for this dim.
        as_json: bool
            if True, return json for info instead of converting to SubsamplingInfo object.
            (Could be useful if you want to use this json as a starting point then make small edits)
        '''
        result = {}
        if snap is not None:
            assert isinstance(snap, slice)
            result['forall'] = {'snaps': ['slice', {'snap': [snap.start, snap.stop, snap.step]}]}
        if not all(d is None for d in (x, y, z)):
            vdict = {'array_dims': list(self.maindims)}
            xyzslices = {}
            if x is not None: xyzslices['x'] = [x.start, x.stop, x.step]
            if y is not None: xyzslices['y'] = [y.start, y.stop, y.step]
            if z is not None: xyzslices['z'] = [z.start, z.stop, z.step]
            vdict['regex'] = {self._maindims_vars_regex: ['slice', xyzslices]}
            result['byvars'] = [vdict]
        return result if as_json else self.subsampling_info_cls(result)

    def subsample_maindims_at_snaps(self, *, x=None, y=None, z=None,
                                den=UNSET, flux=UNSET, nvsqr=UNSET, phi=UNSET, others=None,
                                **kw_subsample):
        '''subsample same maindims but different snaps for different vars.

        x, y, z: None or slice
            slice for this main dim.
        den, flux, nvsqr, phi: UNSET, None or slice
            slice for snaps for this variable.
            None --> do NOT slice snaps for this variable (but still slice maindims!)
        others: None or slice
            slice snaps for whichever of den, flux, nvsqr, and phi are UNSET.
            None --> do not slice snaps (but still slice maindims!)
        '''
        info = self.subsampling_info_maindims_at_snaps(x=x, y=y, z=z,
                                    den=den, flux=flux, nvsqr=nvsqr, phi=phi, others=others,
                                    as_json=False)
        return self.subsample(info, **kw_subsample)

    def subsampling_info_maindims_at_snaps(self, *, x=None, y=None, z=None,
                                den=UNSET, flux=UNSET, nvsqr=UNSET, phi=UNSET, others=None,
                                as_json=False):
        '''SubsamplingInfo corresponding to subsampling maindims at different snaps.

        x, y, z: None or slice
            slice for this main dim. All maindims variables will be sliced according to this.
        den, flux, nvsqr, phi: UNSET, None or slice
            slice for snaps for this variable.
            None --> do not slice snaps for this variable (but still slice maindims!)
        others: None or slice
            slice snaps for whichever of den, flux, nvsqr, and phi are UNSET.
            None --> do not slice snaps (but still slice maindims!)
        as_json: bool
            if True, return json for info instead of converting to SubsamplingInfo object.
            (Could be useful if you want to use this json as a starting point then make small edits)
        '''
        result = {}
        xyz_info = []
        if all(d is None for d in (x,y,z)):
            xyz_info = ['identity', None]
        else:
            xyz_slicer = {}
            if x is not None: xyz_slicer['x'] = [x.start, x.stop, x.step]
            if y is not None: xyz_slicer['y'] = [y.start, y.stop, y.step]
            if z is not None: xyz_slicer['z'] = [z.start, z.stop, z.step]
            xyz_info = ['slice', xyz_slicer]
        result['byvars'] = []
        VAR_TO_REGEX = dict(den='den[0-9]+', flux='flux[xyz][0-9]+', nvsqr='nvsqr[xyz][0-9]+', phi='phi')
        for var, val in dict(den=den, flux=flux, nvsqr=nvsqr, phi=phi).items():
            if val is UNSET:
                continue  # handled by "others"
            reg = VAR_TO_REGEX.pop(var)
            if val is None:
                if xyz_info[0] != 'identity':  # slice maindims but not snaps
                    vdict = {
                        'array_dims': list(self.maindims),
                        'regex': {reg: xyz_info}
                    }
                else:  # nothing to slice for this var
                    vdict = None
            else:  # slice snaps (and possibly also maindims)
                vdict = {
                        'array_dims': list(self.maindims),
                        'snaps': ['slice', {'snap': [val.start, val.stop, val.step]}],
                        'regex': {reg: xyz_info}
                    }
            # add vdict to result
            if vdict is not None:
                result['byvars'].append(vdict)
        if len(VAR_TO_REGEX) != 0:
            reg = '|'.join(VAR_TO_REGEX.values())
            if others is None:
                if xyz_info[0] != 'identity':  # slice maindims but not snaps
                    vdict = {
                        'array_dims': list(self.maindims),
                        'regex': {reg: xyz_info}
                    }
                else:  # nothing to slice for this var
                    vdict = None
            else:
                vdict = {
                        'array_dims': list(self.maindims),
                        'snaps': ['slice', {'snap': [others.start, others.stop, others.step]}],
                        'regex': {reg: xyz_info}
                    }
            # add vdict to result
            if vdict is not None:
                result['byvars'].append(vdict)
        return result if as_json else self.subsampling_info_cls(result)


    # # # READING SUBSAMPLED DATA -- HELPER METHODS # # #

    _maindims_vars_regex = '((den|flux[xyz]|nvsqr[xyz])[0-9]+)|phi'
    _vdist_vars_regex = 'vdist[0-9]+'

    def _apply_subsampling_to_maindims_coords(self, coords):
        '''apply subsampling to maindims coords.
        coords is a dict of {'x': xcoords, 'y': ycoords} possibly also 'z': zcoords.

        [TODO] check that vars actually all have the same maindims, else, crash?
            implementation now just assumes 'den0' exists and has same maindims as other vars.
        '''
        info = self.subsampling_info
        if info is None:
            return coords
        var = 'den0'  # assume this var exists and has same maindims as all others...
        return info.get_applier(var).apply1d(coords)

    def _apply_subsampling_to_vdist_coords(self, vcoords, fluid):
        '''apply subsampling to vdist coords for this fluid (a single Fluid)'''
        info = self.subsampling_info
        if info is None:
            return vcoords
        N = int(fluid)
        var = f'vdist{N}'
        return info.get_applier(var).apply1d(vcoords)

    def _get_subsampling_step(self, x, var='den0'):
        '''get subsampling step for var along this direction.
        Crash with SubsamplingFormatError if subsampling mode for var exists but is not 'slice'.
        '''
        info = self.subsampling_info
        if info is None:
            return 1
        applier = info.get_applier(var)
        if applier.mode != 'slice':
            raise SubsamplingFormatError(f'applier mode for var={var!r} is not "slice".')
        return applier.step(x)
