"""
File Purpose: misc. tools for reading directly from bifrost files
"""
import os
import re

import numpy as np

from ...errors import (
    InputError,
    FileAmbiguityError, FileContentsError, FileContentsConflictError,
)
from ...tools import (
    read_idl_params_file, updated_idl_params_file,
    alias_child, alias_key_of, weakref_property_simple,
    UNSET,
    ProgressUpdater,
)


### --------------------- bifrost snapname_NNN.idl files --------------------- ###

def read_bifrost_snap_idl(filename, *, eval=True, strip_strs=True):
    '''Parse Bifrost snapname_NNN.idl file into a dictionary.

    filename: string
        file to read from.
    eval: bool, default True
        whether to attempt to evaluate the values,
        using ast.literal_eval (safer but less flexible than eval).
        False --> values will remain as strings.
        True --> try to evaluate values but use strings if evaluation fails.
            Also convert '.true.' and '.false.' to True and False, case-insensitively.
    strip_strs: bool, default True
        whether to strip whitespace from all string values in result, after eval.

    File formatting notes:
        - semicolons (;) are used for comments. (idl format)
        - ignore blank lines & lines that don't assign a variable (missing '=')
        - ignores all leading & trailing whitespace in vars & values.
        - might use '.true.' and '.false.' for booleans.
    '''
    result = read_idl_params_file(filename, eval=eval)
    if eval:
        # handle .true. and .false. conversions below. Other evals have already been handled^
        for key, value in result.items():
            if isinstance(value, str):
                lowered = value.lower()
                if lowered == '.true.':
                    result[key] = True
                elif lowered == '.false.':
                    result[key] = False
        # strip whitespace from string values in result
        if strip_strs:
            for key, value in result.items():
                if isinstance(value, str):
                    result[key] = value.strip()
    return result

def bifrost_snap_idl_files(snapname, *, dir=os.curdir, abspath=False):
    '''return list of all bifrost snapname_NNN.idl files in directory.
    Sorts by snap number.

    snapname: str. match snapname_NNN.idl. (NNN can be any integer, doesn't need to be 3 digits.)
    abspath: bool. whether to return absolute paths or just the file basenames within directory.
    '''
    pattern = rf'{snapname}_([0-9]+)[.]idl'
    result = []
    for f in os.listdir(dir):
        match = re.fullmatch(pattern, f)
        if match is not None:
            snap_number = int(match.group(1))
            result.append((snap_number, f))
    result.sort()
    result = [f for (n, f) in result]
    if abspath:
        absdir = os.path.abspath(dir)
        result = [os.path.join(absdir, f) for f in result]
    return result

def bifrost_infer_snapname_here(dir=os.curdir):
    '''infer snapname based on files in directory, if possible.
    For files like snapname_NNN.idl, if all have same snapname, return it.
    If no such files, raise FileNotFoundError; if multiple implied snapnames, raise FileAmbiguityError.
    NNN can be any integer, doesn't need to be 3 digits.
    '''
    pattern = re.compile(r'(.+)_[0-9]+[.]idl')
    snapname = None
    for f in os.listdir(dir):
        match = pattern.fullmatch(f)
        if match is not None:
            if snapname is None:
                snapname = match.group(1)
            elif snapname != match.group(1):
                raise FileAmbiguityError(f'found different snapnames: {snapname!r}, {match.group(1)!r}')
    if snapname is None:
        raise FileNotFoundError(f'no files like "snapname_NNN.idl" found in directory: {dir!r}')
    return snapname


### --------------------- bifrost mesh files --------------------- ###

def read_bifrost_meshfile(meshfile):
    '''returns dict of mesh coords from a Bifrost mesh file.

    Mesh file format looks like:
        x size (int)
        x coords
        x "down" coords
        dx values when taking "up derivative"
        dx values when taking "down derivative"
        then similar for y and z.

    The "down" and "up" refer to interpolation / staggering.

    result will have keys:
        x_size: int, number of points in x
        x: x coords list (as numpy array)
        x_down: x "down" coords
        dxup: dx when taking "up derivative"
        dxdn: dx when taking "down derivative"
    '''
    meshfile = os.path.abspath(meshfile)  # <-- makes error messages more verbose, if crash later.
    with open(meshfile, 'r') as f:
        lines = f.readlines()
    if len(lines) != 5 * len(('x', 'y', 'z')):
        raise FileContentsError(f'expected 5 lines per axis, got nlines={len(lines)}')
    result = {}
    x_to_lines = {'x': lines[:5], 'y': lines[5:10], 'z': lines[10:15]}
    for x, xlines in x_to_lines.items():
        result[f'{x}_size'] = int(xlines[0])
        result[x]           = np.array([float(s) for s in xlines[1].split()])
        result[f'{x}_down'] = np.array([float(s) for s in xlines[2].split()])
        result[f'{x}_ddup'] = np.array([float(s) for s in xlines[3].split()])
        result[f'{x}_dddn'] = np.array([float(s) for s in xlines[4].split()])
        # sanity checks:
        for key in [x, f'{x}_down', f'{x}_ddup', f'{x}_dddn']:
            if len(result[key]) != result[f'{x}_size']:
                raise FileContentsConflictError(f'length of {key!r} does not match {x}_size')
    return result

def slice_bifrost_meshfile(meshfile, slices, *, dst=None):
    '''read meshfile contents, slice by slices, output to dst (return as str if dst=None)
    meshfile: str, path to mesh file
    slices: dict of {x: indexer} for any x from ('x', 'y', 'z').
        currently, implementation requires all provided indexers to be slice objects.
    dst: None or str.
        None --> return output as a string.
        str --> write output to file with this name; return abspath to dst.
                (never overwrites existing output; dst must be a file that doesn't exist yet.)
    '''
    # read meshfile. (to keep all as strings, we avoid using read_bifrost_meshfile directlY)
    meshfile = os.path.abspath(meshfile)
    with open(meshfile, 'r') as f:
        lines = f.readlines()
    if len(lines) != 5 * len(('x', 'y', 'z')):
        raise FileContentsError(f'expected 5 lines per axis, got nlines={len(lines)}')
    lines = [line.rstrip('\n') for line in lines]
    result = []
    x_to_lines = {'x': lines[:5], 'y': lines[5:10], 'z': lines[10:15]}
    for x in ('x', 'y', 'z'):
        xlines = x_to_lines[x]
        if x in slices:
            indexer = slices[x]
            if not isinstance(indexer, slice):
                raise NotImplementedError(f'expected slices[{x!r}] to be a slice; got {indexer!r}')
            new_arr_lines = []
            new_size = None
            for line in xlines[1:]:  # x, x_down, x_ddup, x_dddn'
                splitted = line.split()
                new_vals = splitted[indexer]
                new_line = '   ' + '   '.join(new_vals)  # spacing matches default mesh formatting for arr lines.
                new_arr_lines.append(new_line)
                if new_size is None:
                    new_size = len(new_vals)
                else:
                    assert new_size == len(new_vals), 'expect all arr_lines to have same length'
            result.append(f'{new_size:>12d}')  # >12d matches default mesh formatting for size lines.
            result.extend(new_arr_lines)
        else:  # x is not being sliced; don't change anything!
            result.extend(xlines)
    result = '\n'.join(result)
    # output result
    if dst is None:
        return result
    else:
        with open(dst, 'x') as f:   # mode='x' --> crash if dst exists; never touch existing files.
            f.write(result)
        return os.path.abspath(dst)


### --------------------- BifrostVarPathsManager --------------------- ###

class BifrostVarPathsManager():
    '''manages filepaths (as abspaths) and readable vars for a BifrostSnap.
    self.kind2path = {kind: path}
    self.kind2vars = {kind: [list of readable vars]}
    self.var2kind = {var: kind}
    self.var2path = {var: path}
    self.path2kind = {path: kind}
    self.path2vars = {path: [list of readable vars]}
    self.var2index = {var: index of var in its path's list of vars}
    
    self.kinds: tuple of kinds with any vars in self.
    self.vars: tuple of all vars in self.
    self.paths: tuple of all paths with any vars in self.

    kinds are: 'snap', 'aux', 'hion', 'helium', 'ooe'.
    if kind has no vars, do not include it in results.

    snap: BifrostSnap
    bcalc: BifrostCalculator
    '''
    KINDS = ('snap', 'aux', 'hion', 'helium', 'ooe')
    KIND2FILEBASE = {
        'snap': '{snapname}_{NNN}.snap',
        'aux': '{snapname}_{NNN}.aux',
        'hion': '{snapname}.hion_{NNN}.snap',
        'helium': '{snapname}.helium_{NNN}.snap',
    }

    def __init__(self, snap, bcalc):
        self.snap = snap
        self.bcalc = bcalc
        self.init_all()

    snap = weakref_property_simple('_snap')  # weakref --> snap caching paths manager would be fine.
    bcalc = weakref_property_simple('_bcalc')  # weakref --> bcalc caching paths manager would be fine.
    params = alias_child('snap', 'params')
    snapname = alias_key_of('params', 'snapname')
    NNN = property(lambda self: self.snap.file_s(self.bcalc),
            doc='''(str) the NNN part of the snapname_NNN.idl filename.''')
    snapdir = alias_child('bcalc', 'snapdir')

    def snappath(self, filename):
        '''returns os.path.join(self.snapdir, filename)'''
        return os.path.join(self.snapdir, filename)

    def kind2filebase(self, kind):
        '''returns file basename for this kind.
        Equivalent: self.KIND2FILEBASE[kind].format(snapname=self.snapname, NNN=self.NNN)
        '''
        return self.KIND2FILEBASE[kind].format(snapname=self.snapname, NNN=self.NNN)

    def init_all(self):
        '''init all KINDS in self.'''
        self.kind2path = dict()
        self.kind2vars = dict()
        self.var2kind = dict()
        self.var2path = dict()
        self.path2kind = dict()
        self.path2vars = dict()
        self.var2index = dict()
        self.init_snap_kind()
        self.init_aux_kind()
        self.init_hion_kind()
        self.init_helium_kind()
        self.init_ooe_kind()
        self.kinds = tuple(self.kind2vars.keys())
        self.vars = tuple(self.var2kind.keys())
        self.paths = tuple(self.path2vars.keys())

    def _init_kind_vars_path(self, kind, vars, path):
        '''updates self with corresponding kind, vars, and path.'''
        self.kind2vars[kind] = vars
        self.kind2path[kind] = path
        for var in vars:
            if var in self.var2kind:  # var not unique... crash!
                errmsg = f'{type(self).__name__} with multiple vars with same name: {var!r}'
                raise LoadingNotImplementedError(errmsg)
            self.var2kind[var] = kind
            self.var2path[var] = path
        self.path2kind[path] = kind
        self.path2vars[path] = vars
        self.var2index.update({var: i for i, var in enumerate(vars)})

    def init_snap_kind(self):
        '''vars stored in snapname_NNN.snap file.'''
        path = self.snappath(self.kind2filebase('snap'))
        if self.params.get('do_mhd', False):
            vars = ('r', 'px', 'py', 'pz', 'e', 'bx', 'by', 'bz')
        else:
            vars = ('r', 'px', 'py', 'pz', 'e')
        self._init_kind_vars_path('snap', vars, path)

    def init_aux_kind(self):
        '''vars stored in snapname_NNN.aux file.'''
        path = self.snappath(self.kind2filebase('aux'))
        vars = tuple(self.params.get('aux', '').split())
        if len(vars) > 0:
            self._init_kind_vars_path('aux', vars, path)

    def init_hion_kind(self):
        '''vars stored in snapname.hion_NNN.snap file.'''
        path = self.snappath(self.kind2filebase('hion'))
        if self.params.get('do_hion', 0) > 0:
            vars = ('hionne', 'hiontg', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'nh2')
            self._init_kind_vars_path('hion', vars, path)

    def init_helium_kind(self):
        '''vars stored in snapname.helium_NNN.snap file.'''
        path = self.snappath(self.kind2filebase('helium'))
        if self.params.get('do_helium', 0) > 0:
            vars = ('nhe1', 'nhe2', 'nhe3')
            self._init_kind_vars_path('helium', vars, path)

    def init_ooe_kind(self):
        '''out of equilibrium vars.'''
        if self.params.get('do_out_of_eq', 0) > 0:
            pass  # fail silently; not implemented yet.
            # (doesn't give WRONG answer, just gives no answer, so it's okay to fail silently)
            #raise NotImplementedError('loading ooe vars. Got do_out_of_eq > 0')

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(vars={self.vars})'

    def help(self):
        '''print docstring of self...'''
        print(type(self).__doc__)


class BifrostScrVarPathsManager(BifrostVarPathsManager):
    '''manages filepaths (as abspaths) and readable vars for a SCR_SNAP
    self.kind2path = {kind: path}
    self.kind2vars = {kind: [list of readable vars]}
    self.var2kind = {var: kind}
    self.var2path = {var: path}
    self.path2kind = {path: kind}
    self.path2vars = {path: [list of readable vars]}
    self.var2index = {var: index of var in its path's list of vars}
    
    self.kinds: tuple of kinds with any vars in self.
    self.vars: tuple of all vars in self.
    self.paths: tuple of all paths with any vars in self.

    kinds are: 'snap', 'aux', 'hion', 'helium', 'ooe'.
    if kind has no vars, do not include it in results.

    snap: BifrostSnap
    bcalc: BifrostCalculator
    '''
    KIND2FILEBASE = {
        'snap': '{snapname}.snap.scr',
        'aux': '{snapname}.aux.scr',
        'hion': '{snapname}.hion.snap.scr',
        'helium': '{snapname}.helium.snap.scr',
    }


class BifrostDataCutter(BifrostVarPathsManager):
    '''interface for creating new data files cut from existing data files.
    "cut" refers to indexing by simple slices, with trivial step (1 or None),
        e.g. slice x by slice(500, 1000). But not by slice(500, 1000, 10).

    (NEVER overwrites existing files; if any result files already exist, crash.)

    self.kind2path = {kind: path}
    self.kind2vars = {kind: [list of readable vars]}
    self.var2kind = {var: kind}
    self.var2path = {var: path}
    self.path2kind = {path: kind}
    self.path2vars = {path: [list of readable vars]}
    self.var2index = {var: index of var in its path's list of vars}

    self.kind2newpath = {kind: newpath}
    self.path2newpath = {original path: newpath}
    self.newpath2path = {newpath: original path}
    
    self.kinds: tuple of kinds with any vars in self.
    self.vars: tuple of all vars in self.
    self.paths: tuple of all paths with any vars in self.
    self.newpaths: tuple of all newpaths with any vars in self.

    kinds are: 'snap', 'aux', 'hion', 'helium', 'ooe'.
    if kind has no vars, do not include it in results.

    snap: BifrostSnap
    bcalc: BifrostCalculator
    new_snapname: str or UNSET
        new snapname to use for the cutted data files. UNSET --> '{self.snapname}_cut'
    '''
    def __init__(self, snap, bcalc, *, new_snapname=UNSET):
        super().__init__(snap, bcalc)
        self.new_snapname = f'{self.bcalc.snapname}_cut' if new_snapname is UNSET else new_snapname
        self.init_new_paths()

    def newpath(self, oldpath):
        '''return newpath from oldpath. (both are abspaths.)
        newpath = oldpath, but replace self.bcalc.snapname (within oldpath basename) by new_snapname
        crash if newpath == oldpath.
        '''
        oldbasename = os.path.basename(oldpath)
        newbasename = oldbasename.replace(self.bcalc.snapname, self.new_snapname)
        newpath = os.path.join(os.path.dirname(oldpath), newbasename)
        if newpath == oldpath:
            raise FileExistsError(f'Expect newpath != oldpath, but got both equal to: {newpath!r}')
        return newpath

    def init_new_paths(self):
        '''initialize self.kind2newpath, path2newpath and newpath2path'''
        self.kind2newpath = dict()
        self.path2newpath = dict()
        self.newpath2path = dict()
        for kind, path in self.kind2path.items():
            newpath = self.newpath(path)
            self.kind2newpath[kind] = newpath
            self.path2newpath[path] = newpath
            self.newpath2path[newpath] = path
        self.newpaths = tuple(self.kind2newpath.values())

    # # # SLICES # # #
    @property
    def slices(self):
        '''self.bcalc.slices, but ensuring all are slice objects and have trivial step (1 or None).
        Also ensures at least 1 nontrivial slice exists (i.e. not empty and not all slice(None).)'''
        slices = self.bcalc.slices
        if not all(isinstance(s, slice) for s in slices.values()):
            raise NotImplementedError(f'cut, when non-slice object(s) in slices; got slices={slices!r}')
        if not all(s.step is None or s.step==1 for s in slices.values()):
            raise NotImplementedError(f'cut, with nontrivial step (step != 1 or None); got slices={slices!r}')
        if all(s == slice(None) for s in slices.values()):
            raise InputError(f'no reason to cut; no non-trivial slices exist. Got slices={slices!r}')
        return slices

    def slices_tuple(self):
        '''returns tuple of slices to apply to array with (x, y, z) as first 3 dims.
        determined by self.slices.get(x, slice(None)) for x in 'x', 'y', 'z'.
        '''
        slices = self.slices
        return tuple(slices.get(x, slice(None)) for x in ('x', 'y', 'z'))

    # # # CUT KIND # # #
    def cut_kind(self, kind):
        '''cut data for this kind, writing results to self.kind2newpath[kind].
        see self.kinds for options.
        returns self.kind2newpath[kind], which is an abspath to the new path.

        (NEVER overwrites existing data; if the newpath exists already, crash.)

        amount to cut is determined by self.bcalc.slices.
        size of arrays within memmap data files is determined by bcalc.data_array_shape.
        '''
        # preprocessing
        oldpath = self.kind2path[kind]
        newpath = self.kind2newpath[kind]
        if os.path.exists(newpath):
            raise FileExistsError(f'newpath already exists: {newpath!r}')
        array_shape = self.bcalc.data_array_shape
        _vars_here = self.kind2vars[kind]
        n_arrays_here = len(_vars_here)
        full_file_shape = (*array_shape, n_arrays_here)   # (nx, ny, nz, n_arrays_here)
        slices_tuple = self.slices_tuple()
        kw_memmap = dict(dtype=self.bcalc.data_array_dtype,
                         order=self.bcalc.data_array_order)
        # reading data
        data = np.memmap(oldpath, offset=0, mode='r',  # read-only; never alters existing files!
                         shape=full_file_shape, **kw_memmap)
        # slicing data
        newdata = data[slices_tuple]
        # writing data
        mapped = np.memmap(newpath, offset=0, mode='w+',
                           shape=newdata.shape, **kw_memmap)
        mapped[:] = newdata[:]
        mapped.flush()
        return newpath

    # # # CUT MESHFILE # # #
    def _new_meshfile_path(self):
        '''abspath to new meshfile. Equivalent: self.newpath(self.bcalc.meshfile).'''
        return self.newpath(self.bcalc.meshfile)

    def cut_meshfile(self):
        '''cut meshfile, writing results to self.newpath(self.bcalc.meshfile).
        amount to cut is determined by self.bcalc.slices.

        "cutting the meshfile" means apply slice_bifrost_meshfile()
        '''
        oldpath = self.bcalc.meshfile
        newpath = self._new_meshfile_path()
        return slice_bifrost_meshfile(oldpath, self.slices, dst=newpath)

    # # # CUT IDL FILE # # #
    def _idl_file_path(self):
        '''path to idl file for self.snap. Equivalent: self.bcalc.snap_filepath(self.snap).'''
        return self.bcalc.snap_filepath(self.snap)

    def _new_idl_file_path(self):
        '''abspath to new idl file. Equivalent: self.newpath(self.bcalc.snap_filepath(self.snap)).'''
        return self.newpath(self._idl_file_path())

    def _data_array_shape_after_cut(self):
        '''returns shape each data array will be after cutting (using self.slices).'''
        slices = self.slices  # self.slices property guarantees each value is a slice with trivial step.
        shape = list(self.bcalc.data_array_shape)
        assert len(shape)==3, 'not implemented in non-3D case...'
        for i, x in enumerate(('x', 'y', 'z')):
            if x in slices:
                indexer = slices[x]
                new_idx = range(shape[i])[indexer]
                new_len = len(new_idx)
                shape[i] = new_len
        return tuple(shape)

    def cut_idl_file(self):
        '''cut idl_file, writing results to self.newpath(self.bcalc.idlfile).
        the idlfile is the snapname_NNN.idl file; see self.bcalc.snap_filepath().
        amount to cut is determined by self.bcalc.slices.

        "cutting the idlfile" means replacing the relevant parameters in the idlfile:
            'mx', 'my', 'mz' --> new sizes after cutting
            'snapname' --> new snapname
            'meshfile' --> new meshfile name
        '''
        new_shape = self._data_array_shape_after_cut()
        params = dict()
        params['mx'] = new_shape[0]
        params['my'] = new_shape[1]
        params['mz'] = new_shape[2]
        new_snapname = self.new_snapname
        params['snapname'] = f'"{new_snapname}"'
        new_meshfile = os.path.basename(self.newpath(self.bcalc.meshfile))
        params['meshfile'] = f'"{new_meshfile}"'
        return updated_idl_params_file(self._idl_file_path(), params, dst=self._new_idl_file_path())

    # # # CUT ALL # # #
    def new_file_paths(self):
        '''list of abspaths to all new files which self.cut() will create.
        These are self.newpaths, and the new path for the meshfile & idl file.
        '''
        return list(self.newpaths) + [self._new_meshfile_path(), self._new_idl_file_path()]

    def _check_output_files_dont_exist(self):
        '''ensure that all output files do not exist yet.'''
        for path in self.new_file_paths():
            if os.path.exists(path):
                raise FileExistsError(f'output file already exists: {path!r}')

    def cut(self, *, verbose=True):
        '''cut all data & supporting files, writing results to new path based on self.new_snapname.
        (never edits any existing files, only makes new ones.)

        returns list of all new file paths (i.e. self.new_file_paths())

        verbose: bool
            whether to print progress updates during cutting.
        '''
        updater = ProgressUpdater(print_freq=0 if verbose else -1)
        self._check_output_files_dont_exist()
        updater.print(f'cutting idl file')
        self.cut_idl_file()
        updater.print(f'cutting meshfile')
        self.cut_meshfile()
        # ^ do those first in case of crash; they are fast & inexpensive.
        # v next do the data files.
        for i, kind in enumerate(self.kinds):
            updater.print(f'cutting {kind} data (this is kind {i+1} of {len(self.kinds)})')
            self.cut_kind(kind)
        return self.new_file_paths()
