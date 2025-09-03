"""
File Purpose: subsampling "main" dimensions (and snapshot dimension)

Produce a subsampled version of the data where
some of the variables have been subsampled on main dimensions.
"""
import json
import os
import re

import numpy as np

from ..errors import (
    InputError, InputMissingError, InputConflictError,
    SubsamplingError, SubsamplingFormatError, SubsamplingNotFoundError,
)
from ..tools import (
    simple_property, alias,
    UNSET,
    is_iterable,
    ProgressUpdater,
    code_snapshot_info, nbytes_path,
)


### --------------------- SubsamplingInfo and methods --------------------- ###

class SubsamplingInfo():
    '''information about subsampling
    
    json: dict of subsampling info: {
        'forall': {       # optional; if not provided use vals from byvars.
            'snaps': [mode, info],                   # optional, can provide here or in byvars but not both.
            'array_dims': [list of array dim names in order],      # provide here or in byvars but not both.
            },
        'byvars': [       # optional; if not provided do snaps slicing only
            {
            'snaps': [mode, info],                   # optional, can provide here or in forall but not both.
            'array_dims': [list of array dim names in order],      # provide here or in forall but not both.
            'exact': {   # optional
                var1: [mode1, info1],
                var2: [mode2, info2],  # optional
                ...,
                },
            'regex': {   # optional
                re_var3: [mode3, info3],
                ...,
                },
            },
            ...,  # optionally can provide more dicts like above
            ]
        }
        where:
            snaps = how to subsample snapshots (use dim='snap' for these). Example:
                'snaps': ['slice', {'snap': [start, stop, step]}]
            exact = dict of exact names; subsampling for var with this name
            regex = dict of regex patterns; subsampling for var if re.fullmatch(pattern, var)
            mode = mode for subsampling. e.g. 'slice'
            info = info for subsampling, format depends on mode.
                e.g. for 'slice', info = dict of {dim: [start, stop, step]}.
        Note: if multiple matches for any var, always use the earliest one;
            i.e. earliest dict in list, and always exact match before regex match.
    meta: dict, None, or UNSET
        metadata about the subsampling info. Must be in json format, if provided.
        None --> no metadata
        UNSET --> use code_snapshot_info() to get metadata when this object is created.
    _json_indent: int
        number of spaces to indent when saving json file.
    _init_appliers: bool
        whether to self.init_appliers() during __init__.
        Usually should be True, but if debugging might want to use False.
    '''
    # subsampling_path_manager_cls = SubsamplingInfoPathManager  # <-- defined lower in this file!

    def __init__(self, json, *, meta=UNSET, _json_indent=4, _init_appliers=True):
        self.json = json
        self._json_indent = _json_indent
        self.meta = meta
        self.init_meta()
        self.init_checks()
        if _init_appliers:
            self.init_appliers()

    # # # METHODS -- IMPLEMENTED HERE # # #
    @classmethod
    def implied_from(cls, json_or_filename_or_info, **kw_cls):
        '''return cls object from json, filename, or SubsamplingInfo object.'''
        x = json_or_filename_or_info
        if isinstance(x, SubsamplingInfo):
            info = x
            if isinstance(info, cls):
                return info
            else:
                kw.setdefault('_json_indent', info._json_indent)
                return cls(info.json, **kw_cls)
        elif isinstance(x, str):
            filename = x
            return cls.load(filename, **kw_cls)
        elif isinstance(x, dict):
            json = x
            return cls(json, **kw_cls)
        else:
            raise InputError(f'cannot create {cls.__name__} from {type(x)}.')

    def init_appliers(self):
        '''initialize all subsampling appliers for this SubsamplingInfo object.'''
        aa = {}
        # handle the forall stuff
        forall = self.json.get('forall', {})
        forall_array_dims = forall.get('array_dims', None)
        forall_snap_applier = None
        if self.has_forall_snaps():
            aa['forall'] = {}
            mode, info = forall['snaps']
            snap_applier = self.MODES[mode](info, array_dims=['snap'])
            aa['forall']['snaps'] = snap_applier
        # handle the byvars stuff
        aa['byvars'] = []
        for vdict in self.json.get('byvars', []):
            # handle the possibly-forall stuff
            array_dims = forall_array_dims
            if array_dims is None:
                array_dims = vdict.get('array_dims', [])
            snap_applier = forall_snap_applier
            if snap_applier is None:
                snapstuff = vdict.get('snaps', None)
                if snapstuff is not None:
                    mode, info = snapstuff
                    snap_applier = self.MODES[mode](info, array_dims=['snap'])
            # handle the definitely-byvars stuff
            adict = dict()
            for exact in [ex_ for ex_ in ['exact', 'regex'] if ex_ in vdict]:
                dd = dict()
                for var, [mode, info] in vdict[exact].items():
                    subsampler_cls = self.MODES[mode]
                    dd[var] = subsampler_cls(info, array_dims=array_dims, snap_applier=snap_applier)
                adict[exact] = dd
            aa['byvars'].append(adict)
        self.appliers = aa

    def init_checks(self):
        '''do some sanity checks about this SubsamplingInfo object.
        Raise SubsamplingFormatError if any checks fail.
        Here, checks:
            - uniqueness of var keys: expect to not have exact same var key appear in multiple places.
            - snaps can appear in forall or byvars, but not both.
            - array_dims can appear in forall or byvars, but not both.
            - array_dims must be provided (possibly via forall) for any byvars dict with at least 1 var.
        '''
        # uniqueness of var keys:
        all_vars = set()
        for vdict in self.json.get('byvars', []):
            for exact in [ex_ for ex_ in ['exact', 'regex'] if ex_ in vdict]:
                for var in vdict[exact]:
                    if var in all_vars:
                        raise SubsamplingFormatError(f'var {var!r} appears in multiple places.')
                    all_vars.add(var)
        # snaps can appear in globals or in individual dicts, but not both.
        if 'snaps' in self.json.get('forall', {}):
            for vdict in self.json.get('byvars', []):
                if 'snaps' in vdict:
                    raise SubsamplingFormatError('snaps can appear in globals or in individual dicts, but not both.')
        # array_dims can appear in globals or in individual dicts, but not both.
        if 'array_dims' in self.json.get('forall', {}):
            for vdict in self.json.get('byvars', []):
                if 'array_dims' in vdict:
                    raise SubsamplingFormatError('array_dims can appear in globals or in individual dicts, but not both.')
        # array_dims must be provided for any byvars dict with at least 1 var.
        if 'array_dims' not in self.json.get('forall', {}):
            for vdict in self.json.get('byvars', []):
                if 'array_dims' not in vdict:
                    for exact in [ex_ for ex_ in ['exact', 'regex'] if ex_ in vdict]:
                        if len(vdict[exact]) > 0:
                            errmsg = 'array_dims must be provided via forall or in each byvars dict with at least 1 var'
                            raise SubsamplingFormatError(errmsg)

    # # # META UPDATES # # #
    def init_meta(self):
        '''initialize self.meta. None remains None. UNSET becomes code_snapshot_info().'''
        if self.meta is UNSET:
            self.meta = code_snapshot_info()

    def update_meta(self, d):
        '''self.meta.update(d). If self.meta is None, keep it as None.'''
        # [TODO] more sophisticated update options?
        if self.meta is not None:
            self.meta.update(d)

    # # # SNAPS BASIC INFO # # #
    def has_forall_snaps(self):
        '''returns True if 'snaps' in 'forall', else False.'''
        return 'snaps' in self.json.get('forall', {})

    def has_byvars_snaps(self):
        '''return True if 'snaps' in any byvars, else False.'''
        return any('snaps' in vdict for vdict in self.json.get('byvars', []))

    # # # INFO / APPLIER FOR A SINGLE VAR # # #
    def get_applier(self, var, *, missing_ok=True):
        '''returns a SubsamplingMode instance appropriate for var based on self.
        Assumes self.init_appliers() was run and is up-to-date.

        var: str
            variable name to get applier for, or string 'snaps'.
            'snaps' --> get 'snaps' applier from forall, else crash.
            else --> get first match from byvars.
        missing_ok: bool
            When var has no match in self:
                if missing_ok: return SubsamplingIdentity instance.
                otherwise: raise SubsamplingNotFoundError.
        '''
        aa = self.appliers
        if var == 'snaps':
            if self.has_forall_snaps():
                return aa['forall']['snaps']
            else:
                raise SubsamplingNotFoundError('no "forall" subsampling applier for snaps.')
        # else
        for adict in aa['byvars']:
            for exact_var, applier in adict.get('exact', {}).items():
                if var == exact_var:
                    return applier
            for regex_var, applier in adict.get('regex', {}).items():
                if re.fullmatch(regex_var, var):
                    return applier
        if missing_ok:
            return self.MODES['identity'](None, array_dims=[])
        else:
            raise SubsamplingNotFoundError(f'no subsampling applier for var {var!r}.')

    def get_var_info(self, var, default=UNSET):
        '''returns the (mode, info, array_dims, None_or_snaps_mode_and_info) for var within self.

        default: UNSET or any object
            if var not found, return default if provided, else raise SubsamplingNotFoundError
        '''
        # handle the forall stuff
        forall = self.json.get('forall', {})
        forall_array_dims = forall.get('array_dims', None)
        forall_snaps = forall.get('snaps', None)
        for vdict in self.json.get('byvars', []):
            array_dims = vdict.get('array_dims', []) if forall_array_dims is None else forall_array_dims
            snapstuff = vdict.get('snaps', None) if forall_snaps is None else forall_snaps
            for exact_var, [mode, info] in vdict.get('exact', {}).items():
                if var == exact_var:
                    return (mode, info, array_dims, snapstuff)
            for regex_var, [mode, info] in vdict.get('regex', {}).items():
                if re.fullmatch(regex_var, var):
                    return (mode, info, array_dims, snapstuff)
        if default is UNSET:
            return default
        else:
            raise SubsamplingNotFoundError(f'no subsampling info for var {var!r}.')

    # # # SAVING / LOADING # # #
    @classmethod
    def load(cls, file_or_dir=None, **kw_cls):
        '''load based on subsampling_info.txt.
        
        file_or_dir: None or str
            where to load from.
            None --> load from current directory
            directory --> load from 'subsampling_info.txt' here,
                            or from 'subsampling_info/subsampling_info.txt' here.
            file --> load from this file.
        '''
        paths = cls.subsampling_path_manager_cls.implied(file_or_dir)
        paths.assert_isfile('info_txt')
        with open(paths['info_txt'], 'r') as f:
            s = json.load(f)
        if paths.isfile('info_meta'):
            with open(paths['info_meta'], 'r') as f:
                meta = json.load(f)
        else:
            meta = None
        return cls(s, meta=meta, **kw_cls)

    def save(self, dir=os.curdir):
        '''saves subsampling info. Return SubsamplingInfoPathManager instance with relevant paths.
        Crashes if this would overwrite any existing files.

        dir: str
            save to 'subsampling_info/subsampling_info.txt' within this directory,
            or to 'subsampling_info.txt' within this dir if dir basename == 'subsampling_info'.

        Also saves 'subsampling_meta.txt' if relevant, at same level as subsampling_info.txt.
        '''
        paths = self.subsampling_path_manager_cls.implied(dir=dir, make=True)
        paths.assert_does_not_exist('info_txt')
        if self.meta is not None:
            paths.assert_does_not_exist('info_meta')
        with open(paths['info_txt'], 'w') as f:
            json.dump(self.json, f, indent=self._json_indent)
        if self.meta is not None:
            with open(paths['info_meta'], 'w') as f:
                json.dump(self.meta, f, indent=self._json_indent)
        return paths

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}({self.json!r})'

    # # # MODES -- REGISTER # # #
    MODES = {}  # dict of {mode name: applier class} for registered subsampling applier modes

    @staticmethod
    def register_applier_mode(cls_applier_to_register, mode=None):
        '''register cls_applier_to_register as a known applier mode for subsampling.'''
        cls = cls_applier_to_register
        if mode is None: mode = cls.__name__
        if mode in SubsamplingInfo.MODES:
            raise KeyError(f'mode {mode!r} already registered.')
        cls.mode = mode
        SubsamplingInfo.MODES[mode] = cls


### --------------------- SubsamplingPathManager --------------------- ###

class SubsamplingInfoPathManager(dict):
    '''class that helps manage subsampling info paths.
    info_dir: str
        path to subsampling_info directory. Internally will be converted to abspath.

    All paths will be stored internally as abspaths.
        info_dir: subsampling_info
        info_txt: subsampling_info/subsampling_info.txt
        info_meta: subsampling_info/subsampling_meta.txt
    subclasses might add other paths too.
    Note: self.basename(key) aliases to os.path.basename(self[key]).

    make: whether to create the 'subsampling_info' folder if it doesn't exist yet.
    exist_ok: if False and any folders to make already exist, crash instead.
    '''
    basename_info_dir = 'subsampling_info'
    basename_info_txt = 'subsampling_info.txt'
    basename_info_meta = 'subsampling_meta.txt'
    keys_to_make_paths = ('info_dir',)

    def __init__(self, info_dir, *, make=True, exist_ok=True):
        if not os.path.basename(info_dir) == self.basename_info_dir:
            raise InputError(f'expected basename(info_dir)={self.basename_info_dir!r}. Got info_dir={info_dir!r}')
        super().__init__(info_dir=os.path.abspath(info_dir))
        self.init_path_strings()
        self.make = make
        self.exist_ok = exist_ok
        if make:
            self.make_paths()

    def init_path_strings(self):
        '''initialize all path strings. See help(self) for details.'''
        self['info_txt'] = os.path.join(self['info_dir'], self.basename_info_txt)
        self['info_meta'] = os.path.join(self['info_dir'], self.basename_info_meta)

    def make_paths(self):
        '''create paths for all keys in self.keys_to_make_paths, if the paths don't exist already.
        if any paths existed already but not self.exist_ok, crash before making any of them!
        '''
        if not self.exist_ok:
            for key in self.keys_to_make_paths:
                if os.path.exists(self[key]):
                    raise FileExistsError(f'key {key!r} path already exists: {self[key]!r}')
        for key in self.keys_to_make_paths:
            os.makedirs(self[key], exist_ok=self.exist_ok)

    @classmethod
    def implied(cls, file_or_dir=None, *, dir=None, make=None, **kw):
        '''returns SubsamplingInfoPathManager implied from path information or current directory.
        file_or_dir: None or str
            None --> look within current directory (or use dir if dir is provided)
            directory --> info_dir = here if 'subsampling_info.txt' contained within it,
                            else look for 'subsampling_info' directory to use as info_dir.
            file --> if 'subsampling_info.txt', use info_dir = directory containing file.
        dir: None or str
            'subsampling_info' --> info_dir = dir
            any other str --> info_dir = dir/subsampling_info
            Cannot provide dir AND file_or_dir.
        make: None or bool
            None --> use True if dir is provided, else False.

        (use cls.basename_info_txt and cls.basename_info_dir instead of 'subsampling_info.txt' and 'subsampling_info'.)
        '''
        if (file_or_dir is not None) and (dir is not None):
            raise InputConflictError('cannot provide both file_or_dir and dir.')
        kw.update(make=(dir is not None) if make is None else make)
        # provided dir (probably saving a new subsampling info)
        if dir is not None:
            if os.path.basename(dir) == cls.basename_info_dir:
                info_dir = os.path.abspath(dir)
            else:
                info_dir = os.path.join(os.path.abspath(dir), cls.basename_info_dir)
            return cls(info_dir, **kw)
        # did not provide dir (probably loading an existing subsampling info)
        if file_or_dir is None:
            file_or_dir = os.getcwd()
        if os.path.isdir(file_or_dir):
            d = os.path.abspath(file_or_dir)
            if os.path.exists(os.path.join(d, cls.basename_info_txt)):
                info_dir = d
                return cls(info_dir, **kw)
            elif os.path.exists(os.path.join(d, cls.basename_info_dir)):
                info_dir = os.path.join(d, cls.basename_info_dir)
                return cls(info_dir, **kw)
            else:
                raise FileNotFoundError(f'no {cls.basename_info_txt!r} or {cls.basename_info_dir!r} in {d!r}')
        elif os.path.isfile(file_or_dir):
            f = os.path.abspath(file_or_dir)
            if os.path.basename(f) == cls.basename_info_txt:
                info_dir = os.path.dirname(f)
                return cls(info_dir, **kw)
            else:
                raise InputError(f'expected basename(file)={cls.basename_info_txt!r} but got file={f!r}')
        else:
            raise FileNotFoundError(f'file_or_dir={file_or_dir!r} not found.')

    # # # ALIASES TO OS OPERATIONS # # #
    def basename(self, key):
        '''returns os.path.basename(self[key])'''
        return os.path.basename(self[key])

    def exists(self, key):
        '''returns os.path.exists(self[key])'''
        return os.path.exists(self[key])

    def isdir(self, key):
        '''returns os.path.isdir(self[key])'''
        return os.path.isdir(self[key])

    def isfile(self, key):
        '''returns os.path.isfile(self[key])'''
        return os.path.isfile(self[key])

    def assert_does_not_exist(self, key):
        if self.exists(key):
            raise FileExistsError(f'{self[key]!r}')
    def assert_exists(self, key):
        if not self.exists(key):
            raise FileNotFoundError(f'{self[key]!r}')
    def assert_isdir(self, key):
        if not self.isdir(key):
            raise NotADirectoryError(f'{self[key]!r}')
    def assert_isfile(self, key):
        if not self.isfile(key):
            raise FileNotFoundError(f'{self[key]!r}')

    # # # DISPLAY # # #
    def __repr__(self):
        contents = ',\n'.join(f'{k!r:>25s} : {v!r}' for k, v in self.items())
        return f'{type(self).__name__}({{\n{contents}}})'


class SubsamplingResultPathManager(SubsamplingInfoPathManager):
    '''class that helps manage paths related to results of subsampling.
    "Result of subsampling" appears in folder structure as:
        RUNDIR/subsampling_result/SNAPSDIR
        RUNDIR/subsampling_result/subsampling_info
    Contrast this with interpreting subsampled data, which expects folder structure:
        RUNDIR/SNAPSDIR (of subampled data)
        RUNDIR/subsampling_info
    The idea is that the contents of subsampling_result may be treated as a new RUNDIR.
    
    snaps_dir: str
        path to snaps directory. Internally will be converted to abspath.

    All paths will be stored internally as abspaths:
        run_dir: RUNDIR   # abspath to any directory.
        snaps_dir: RUNDIR/SNAPSDIR
        result_dir: RUNDIR/subsampling_result   # [TODO] allow for other names here as well, e.g. subsampling_result_N.
        subsampled_snaps_dir: RUNDIR/subsampling_result/SNAPSDIR
        info_dir: RUNDIR/subsampling_result/subsampling_info
        info_txt: RUNDIR/subsampling_result/subsampling_info/subsampling_info.txt
        info_meta: RUNDIR/subsampling_result/subsampling_info/subsampling_meta.txt
    subclasses might add other paths too.
    Note: self.basename(key) aliases to os.path.basename(self[key]).
    
    make: whether to create subsampling-related folders if they doesn't exist yet.
    exist_ok: if False and any folders to make already exist, crash instead.
    '''
    basename_result_dir = 'subsampling_result'
    keys_to_make_paths = ('result_dir', 'subsampled_snaps_dir', 'info_dir')

    def __init__(self, snaps_dir, make=True, exist_ok=True):
        super(SubsamplingInfoPathManager, self).__init__(snaps_dir=os.path.abspath(snaps_dir))
        self.init_path_strings()
        self.make = make
        self.exist_ok = exist_ok
        if make:
            self.make_paths()

    def init_path_strings(self):
        '''initialize all path strings. See help(self) for details.'''
        self['run_dir'] = os.path.dirname(self['snaps_dir'])
        basename_result_dir = self.basename_result_dir
        self['result_dir'] = os.path.join(self['run_dir'], basename_result_dir)
        self['subsampled_snaps_dir'] = os.path.join(self['result_dir'], self.basename('snaps_dir'))
        self['info_dir'] = os.path.join(self['result_dir'], self.basename_info_dir)
        super().init_path_strings()  # initialize info_txt and info_meta

    @classmethod
    def implied(cls, file_or_dir=None, *, dir=None, make=None, **kw):
        raise NotImplementedError(f'{type(self).__name__}.implied()')

    # # # STORAGE SIZE INFO # # #
    def nbytes_snaps_dirs(self):
        '''return dict of storage size (in bytes) of snaps_dir and subsampled_snaps_dir.
        Keys will be: 'nbytes_snaps_dir', 'nbytes_subsampled_snaps_dir'.
        Vals will be nbytes (int) if path exists, else None.
        '''
        result = {}
        for key in ('snaps_dir', 'subsampled_snaps_dir'):
            if self.exists(key):
                result[f'nbytes_{key}'] = nbytes_path(self[key])
            else:
                result[f'nbytes_{key}'] = None
        return result


# tell SubsamplingInfo about SubsamplingInfoPathManager
SubsamplingInfo.subsampling_path_manager_cls = SubsamplingInfoPathManager


### --------------------- SubsamplingApplier --------------------- ###

class SubsamplingApplier():
    '''applier of a subsampling method.

    info: any object
        info required for self.apply.
    array_dims: list of str
        names of expected array dimensions in order.
        May be used to translate between information in info, and an array being subsampled.
    extra_info: any objects
        any extra kwargs will all be saved in self.extra_info.
    '''
    def __init_subclass__(cls, *, mode=None, **kw):
        '''register subclass as a subsampling mode.'''
        super().__init_subclass__(**kw)
        SubsamplingInfo.register_applier_mode(cls, mode=mode)

    def __init__(self, info, *, array_dims, snap_applier=None, **extra_info):
        self.info = info
        self.array_dims = array_dims
        self.snap_applier = snap_applier
        self.extra_info = extra_info
        self._check_info()

    # # # METHODS -- SUBCLASS SHOULD IMPLEMENT # # #
    def _check_info(self):
        '''checks that self.info is in the expected format. Crash if not.'''
        raise NotImplementedError(f'{type(self).__name__}._check_info()')

    def apply(self, array):
        '''apply subsampling to array; return new array.'''
        raise NotImplementedError(f'{type(self).__name__}.apply()')

    def apply1d(self, dict_):
        '''return result of subsampling dict_ of 1d arrays, with keys in array_dims.
        Subclass should raise SubsamplingError if this is not possible.
        '''
        raise NotImplementedError(f'{type(self).__name__}.apply1d()')

    # # # METHODS DEFINED HERE # # #
    def apply_snap_applier(self, snap_srcs, *, missing_ok=True):
        '''return self.snap_applier(snap_srcs), or snap_srcs unchanged if self.snap_applier=None.

        missing_ok: bool
            whether it is okay for snap_applier to be None
            False --> crash with SubsamplingNotFoundError if snap_applier is None.
        '''
        result = snap_srcs
        if self.snap_applier is None:
            if not missing_ok:
                raise SubsamplingNotFoundError('no snap_applier provided, and missing_ok=False.')
        else:
            result = self.snap_applier.apply(snap_srcs)
        return result

    def __repr__(self):
        return f'{type(self).__name__}({self.info!r}, array_dims={self.array_dims!r}, mode={self.mode!r})'


class SubsamplingIdentity(SubsamplingApplier, mode='identity'):
    '''subsampling applier that does nothing!'''
    def _check_info(self):
        '''checks that self.info is in the expected format. Crash if not.'''
        if self.info is not None:
            raise SubsamplingFormatError('info for identity should be None.')

    def apply(self, array):
        '''return array, unchanged.'''
        return array

    def apply1d(self, dict_):
        '''return dict_, unchanged.'''
        return dict_


class SubsamplingSlice(SubsamplingApplier, mode='slice'):
    '''slice subsampling applier. Expect info to be dict of {array_dim: [start, stop, step]}.'''
    # # # REQUIRED BY PARENT # # #
    def _check_info(self):
        '''checks that self.info is in the expected format. Crash if not.'''
        for key, val in self.info.items():
            if len(val) != 3:
                raise SubsamplingFormatError(f'info for {key!r} should have 3 elements: [start, stop, step].')
            if key not in self.array_dims:
                raise InputError(f'key {key!r} not in array_dims={self.array_dims!r}.')

    def apply(self, array):
        '''apply subsampling to array; return new array.'''
        array = np.asanyarray(array)
        slices = tuple(slice(*self.info.get(dim, (None,))) for dim in self.array_dims)
        return array[slices]

    def apply1d(self, dict_):
        '''return result of subsampling dict_ of 1d arrays, with keys in array_dims'''
        slices = {k: slice(*self.info.get(k, (None,))) for k in dict_}
        result = {k: v[slices[k]] for k, v in dict_.items()}
        return result

    # # # ADDITIONAL METHODS # # #
    def slice(self, dim=None):
        '''returns slice for this dim, or dict of {dim: slice} for all dims in array_dims.'''
        if dim is None:
            return {dim: slice(*self.info.get(dim, (None,))) for dim in self.array_dims}
        else:
            return slice(*self.info.get(dim, (None,)))

    def start(self, dim=None):
        '''returns slice start for this dim, or dict of {dim: slice start} for all array_dims.'''
        if dim is None:
            return {d: s.start for d, s in self.slices().items()}
        else:
            return slice(*self.info.get(dim, (None,))).start

    def stop(self, dim=None):
        '''returns slice stop for this dim, or dict of {dim: slice stop} for all array_dims.'''
        if dim is None:
            return {d: s.stop for d, s in self.slices().items()}
        else:
            return slice(*self.info.get(dim, (None,))).stop

    def step(self, dim=None):
        '''returns slice step for this dim, or dict of {dim: slice step} for all array_dims.'''
        if dim is None:
            return {d: s.step for d, s in self.slices().items()}
        else:
            return slice(*self.info.get(dim, (None,))).step


### --------------------- Subsampler --------------------- ###

class Subsampler():
    '''interface to help with actually doing the subsampling, of a Subsamplable object.

    target: Subsamplable
        the Subsamplable object which self will subsample when called.
    info: SubsamplingInfo, str, or json-like dict
        str --> path to load subsampling info from.
                can be filename or directory. see SubsamplingInfo.load for details.
        dict --> subsampling info in json-like format, see SubsamplingInfo for details.

    Below, "snap src" refers to the hashable object that identifies a snapshot.
    Its exact behavior is not defined here and may vary across different Subsamplable subclasses.
    E.g. it may be a filepath, or a Snap object.
    The only expectation here is that each src must be hashable.

    Expects Subsamplable target object to have:
        - rawvars_loadable(src): list of all directly loadable vars within snap src.
        - rawvar_load(var, src): load a single raw var from snap src.
            OR override rawvar_load_and_subsample instead.
        - rawvar_save(var, data, dst): save a single raw var to snap dst.
        - target.snapdir: should tell abspath of folder with all snapshots.
        - target.snaps.file_path(self): should tell array of snapshot filepaths.
        - target.subsampling_info_cls: SubsamplingInfo subclass to use for this target.

    Results will be saved to subsampling result paths; see SubsamplingResultPathManager for help.
    '''
    path_manager_cls = SubsamplingResultPathManager

    def __init__(self, target, info):
        self.target = target
        self.info = target.subsampling_info_cls.implied_from(info)

    def subsample(self, *, subsampled_data_exist_ok=False):
        '''apply subsampling to all data as appropriate (determined by self.info)
        returns self.path_manager() instance with relevant paths.
            (results will be saved to paths determined by SubsamplingResultPathManager;
            probably 'subsampling_result' at the same directory-level as target.snapdir.)

        Never overwrites any of the pre-subsampling data.
        By default, refuses to overwrite any existing data at all.

        subsampled_data_exist_ok: bool
            whether it is okay for subsampled data file(s) to already exist before saving any data. Default False.
            (Doesn't interact with any subsampling_info files.)
        '''
        srcs, src2vars = self.srcs_and_src2vars()
        paths = self.path_manager(make=False)  # make=False --> don't create any folders here yet.
        updater = ProgressUpdater(wait=False)  # wait=False --> always show progress.
        for i, src in enumerate(srcs):
            updater.print(f'Subsampling snap {i+1} of {len(srcs)}: {src!r}')
            self.subsample_snap(src, include_vars=src2vars.get(src, None),
                                dst_exists_ok=subsampled_data_exist_ok)
        self.info.update_meta(paths.nbytes_snaps_dirs())  # put info about snaps dirs sizes
        self.info.save(paths['info_dir'])
        updater.finalize('subsample()')
        return paths

    def path_manager(self, *, make=True, exist_ok=True):
        '''returns instance of path_manager_cls, based on self.target.snapdir.
        Use this when creating subsampled data.

        make: whether to create the 'subsampling_result' folder if it doesn't exist yet.
        exist_ok: if False and any folders to make already exist, crash instead.
        '''
        snapdir = self.target.snapdir  # in its own line to make debugging easier in case of crash.
        return self.path_manager_cls(snapdir, make=make, exist_ok=exist_ok)

    # # # GETTING SRCS AND VARS FOR EACH SRC # # #
    def srcs(self):
        '''returns list of all snap srcs in self.target (before applying any subsampling)'''
        return self.target.subsampling_snap_srcs()

    def srcs_and_src2vars(self):
        '''returns (srcs, src2vars), where:
            srcs = [list of all snap srcs to keep]
            src2vars = dict of {src: [vars to keep for src]} if relevant.
                        if keeping all vars from src, src2vars might exclude src key.
                        (if keeping all vars from all srcs, src2vars may be an empty dict.)
        '''
        if self.info.has_forall_snaps():
            srcs = self.srcs_forall()  # returns list of srcs
            src2vars = {}  # no var-specific mapping based on snaps
        elif self.info.has_byvars_snaps():
            var2srcs = self.srcs_byvars()   # returns dict of {var: [srcs to keep for var]}
            srcs = set.union(*[set(v) for v in var2srcs.values()])
            src2vars = {src: set() for src in srcs}
            for var, srcs_ in var2srcs.items():
                for src in srcs_:
                    src2vars[src].add(var)
        else:  # NO SNAP SUBSAMPLING
            srcs = self.srcs()  # returns list of srcs
            src2vars = {}  # no var-specific mapping based on snaps
        return srcs, src2vars

    def srcs_forall(self):
        '''list of all srcs, subsampled by self.info['forall']['snaps'].'''
        if not self.info.has_forall_snaps():
            raise SubsamplingError('srcs_forall expects info to have "forall" snaps')
        srcs = self.srcs()
        return self.info.get_applier('snaps').apply(srcs)

    def srcs_byvars(self):
        '''dict of {var: [srcs in which to keep data for var]}

        Subsampling will be relative to full list of snaps;
            raise SubsamplingError if would need to write var at a snap where it was previously missing.
            E.g. crash if var5 appears only every 5 snaps but info says slice to every 7 snaps for var5.

        Any var with no snap subsampling indicated will be kept in all srcs where it was already.
        '''
        if not self.info.has_byvars_snaps():
            raise SubsamplingError('srcs_byvars expects info to have "byvars" snaps')
        srcs = self.srcs()
        src2vars = self.target.rawvars_loadable_across(srcs)
        var2srcs = {}  # {var: [srcs that have var]}
        for s, vars_ in src2vars.items():
            for v in vars_:
                var2srcs.setdefault(v, set()).add(s)
        # getting result: {var: [srcs to keep for var]}
        result = {}
        SKIPPED = set()
        for var in var2srcs:
            try:  # any subsampling for this var? if no, just keep it in all srcs where it was already.
                applier = self.info.get_applier(var, missing_ok=False)
            except SubsamplingNotFoundError:
                result[var] = var2srcs[var]
                SKIPPED.add(var)  # bookkeeping to help with debugging
                continue
            try:  # any snap subsampling for this var? if no, just keep it in all srcs where it was already.
                subsampled = applier.apply_snap_applier(srcs, missing_ok=False)
            except SubsamplingNotFoundError:
                result[var] = var2srcs[var]
                SKIPPED.add(var)  # bookkeeping to help with debugging
                continue
            # crash if subsampling would cause needing to write a var at a snap that previously didn't have it.
            for s in subsampled:
                if var not in src2vars[s]:
                    raise SubsamplingError(f'var {var!r} does not appear in original snap {s!r}')
            # actually subsampling this var! Add to result:
            result[var] = subsampled
        return result

    # # # SUBSAMPLING SINGLE SNAP # # #
    def subsample_snap(self, src, *, dst=None, dst_exists_ok=False, include_vars=None):
        '''apply subsampling to all appropriate data vars in this snap.
        returns abspath to dst where data was saved (or, None if no data was saved).

        src: any hashable object
            snap src to subsample.
        dst: None or str
            filepath for where to save subsampled data.
            None --> self.dst_from_src(src)
        include_vars: None or list of strs
            list of vars to include in result.
            None --> use self.target.rawvars_loadable(src)
                    (and do not apply any 'snaps' subsampling from subsampling_info)
            if empty list, do not save any vars, and return None instead of path.
        '''
        # setup / bookkeeping
        if include_vars is None:
            include_vars = self.target.rawvars_loadable(src)
        elif len(include_vars) == 0:
            return None
        if dst is None:
            dst = self.dst_from_src(src)
        if (not dst_exists_ok) and os.path.exists(dst):
            raise FileExistsError(f'{dst!r} already exists and dst_exists_ok=False.')
        # do the subsampling
        for var in include_vars:
            subsampled = self.target.rawvar_load_and_subsample(var, src, self.info)
            self.target.rawvar_save(var, subsampled, dst)
        return os.path.abspath(dst)

    def dst_from_src(self, src):
        '''return filepath for where to save subsampled data for this src.
        Details determined by self.path_manager() and self.target.snap_src_to_filepath().
        '''
        paths = self.path_manager()
        src_path = self.target.snap_src_to_filepath(src)
        dst = os.path.join(paths['subsampled_snaps_dir'], os.path.basename(src_path))
        return dst

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(target={self.target!r},\n\ninfo={self.info!r})'


### --------------------- Subsamplable --------------------- ###

class Subsamplable():
    '''object that can be subsampled.
    
    Subclass should implement:
        - rawvars_loadable(src): list of all directly loadable vars within snap src.
        - rawvar_load(var, src): load a single raw var from snap src.
            OR override rawvar_load_and_subsample(var, src, info) to avoid using rawvar_load.
        - rawvar_save(var, data, dst): save a single raw var to snap dst.
            Before overwriting any existing data, subclass's implementation should crash by default.
        - _snap_src_to_filepath(self, src): return filepath for snap src.
        - self.snapdir: should tell abspath of folder with all snapshots.
            OR, override subsampling_path_manager() to avoid using snapdir.
        - self.snaps.file_path(self): should tell array of snapshot filepaths.
            OR, override subsampling_snap_srcs to avoid using self.snaps.file_path(self).
    Subclass may use str for snap src but might use something else.
    The only requirement for snap src imposed here is that it must be hashable.
    '''
    subsampler_cls = Subsampler
    subsampling_info_cls = SubsamplingInfo
    subsampling_info_path_manager_cls = SubsamplingInfoPathManager

    # # # METHODS -- REQUIRED OR SUGGESTED, FOR SUBCLASS TO OVERRIDE # # #
    def subsampling_snap_srcs(self):
        '''list of all snap srcs in self (before applying any subsampling)'''
        return self.snaps.file_path(self)

    def snap_src_to_filepath(self, src):
        '''return filepath for snap src. See also: self.subsampling_snap_srcs().
        Subclass must implement this.
        '''
        raise NotImplementedError(f'{type(self).__name__}.snap_src_to_filepath()')

    def rawvars_loadable(src):
        '''returns list of all directly loadable vars within snap src.
        Subclass must implement this.
        '''
        raise NotImplementedError(f'{type(self).__name__}.rawvars_loadable()')

    def rawvars_loadable_across(self, srcs=None):
        '''returns dict of {src: [vars loadable from src]} for all snap srcs
        The implementation here just calls rawvars_loadable for each src.

        if srcs is None, use self.subsampling_snap_srcs().
        '''
        if srcs is None: srcs = self.subsampling_snap_srcs()
        result = {}
        for src in srcs:
            loadable = self.rawvars_loadable(src)
            result[src] = loadable
        return result

    def rawvar_load(var, src):
        '''load a single raw var from snap src.
        Subclass can implement this or override rawvar_load_and_subsample instead.
        '''
        raise NotImplementedError(f'{type(self).__name__}.rawvar_load()')

    def rawvar_save(var, data, dst):
        '''save a single raw var to snap dst.
        Subclass must implement this.
        Before overwriting any existing data, subclass's implementation should crash by default.
        '''
        raise NotImplementedError(f'{type(self).__name__}.rawvar_save()')

    def rawvar_load_and_subsample(self, var, src, info):
        '''returns var loaded and subsampled from src.
        Subclass should either:
            - implement rawvar_load(var, src)
            - override rawvar_load_and_subsample instead,
                e.g. slice h5py object instead of loading full array to slice.
        '''
        applier = info.get_applier(var)
        data = self.rawvar_load(var, src)
        return applier.apply(data)

    # # # SUBSAMPLING (to help with subsampling some data) # # #
    def subsampler(self, subsampling_info):
        '''return self.subsampler_cls instance with self and subsampling_info.
        See help(self.subsample) for details on subsampling_info.
        '''
        return self.subsampler_cls(self, subsampling_info)

    def subsample(self, subsampling_info, *, subsampled_data_exist_ok=False):
        '''apply subsampling to all data indicated by subsampling_result_info.
        returns SubsamplingResultPathManager with relevant paths.
            (results will be saved to paths determined by SubsamplingResultPathManager;
            probably 'subsampling_result' at the same directory-level as target.snapdir.)

        Never overwrites any of the pre-subsampling data.
        By default, refuses to overwrite any existing data at all.
        
        subsampling_info: SubsamplingInfo, str, or json-like dict
            str --> path to load subsampling info from.
                    can be filename or directory. see SubsamplingInfo.load for details.
            dict --> subsampling info in json-like format, see SubsamplingInfo for details.
        subsampled_data_exist_ok: bool
            whether it is okay for subsampled data file(s) to already exist before saving any data. Default False.
            (Doesn't interact with any subsampling_info files.)
        '''
        subsampler = self.subsampler(subsampling_info)
        paths = subsampler.subsample(subsampled_data_exist_ok=subsampled_data_exist_ok)
        return paths

    # # # SUBSAMPLING INFO (to help with reading subsampled data) # # #
    # [TODO] reload subsampling_info when relevant, but cache results to know when it's not relevant.
    subsampling_info = simple_property('_subsampling_info', setdefaultvia='_default_subsampling_info',
            doc='''SubsamplingInfo telling how existing data was subsampled from prior data.
            By default, this info will be loaded from {self.dirname}/subsampling_info.''')

    @subsampling_info.setter
    def subsampling_info(self, info):
        '''set self._subsampling_info to info.
        see self.subsampling_info_cls.implied_from(info) for more details.
        '''
        self._subsampling_info = self.subsampling_info_cls.implied_from(info)
    def _default_subsampling_info(self):
        '''default value for self.subsampling_info: load from {self.dirname}/subsampling_info.'''
        try:
            return self.load_subsampling_info()
        except FileNotFoundError:
            return None

    def load_subsampling_info(self):
        '''load subsampling info from {self.dirname}/subsampling_info.'''
        return self.subsampling_info_cls.load(self.dirname)
