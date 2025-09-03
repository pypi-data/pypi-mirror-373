"""
File Purpose: code associated with Bifrost Snaps
"""
import os
import re

from .bifrost_io_tools import (
    read_bifrost_snap_idl,
    bifrost_snap_idl_files,
    bifrost_infer_snapname_here,
    BifrostVarPathsManager,
    BifrostScrVarPathsManager,
)
from ...dimensions import (
    ParamsSnap, ParamsSnapList,
    SpecialDimensionValue, MISSING_SNAP,
)
from ...errors import FileContentsConflictError


### --------------------- BifrostSnap and BifrostSnapList --------------------- ###

class BifrostSnap(ParamsSnap):
    '''info about a single bifrost snapshot, including label (str) and index (int).

    The "index" should only be meaningful in the context of a SnapList
    The "label" should be the str name for this snapshot
        - unique within context (e.g. there's only one "snapshot 1" in a simulation)
        - easiest to use str int labels (e.g. "snapshot 1" --> label="1")

    s: the label (str) of the snapshot. if None, cannot convert to str.
    i: the "index" (int) of the snapshot (within a SnapList). if None, cannot convert to int.
    t: time at this snapshot ['raw' units]
    params: dict of parameters (e.g. from .idl file) at this snapshot. if None, make empty dict.
    '''
    var_paths_manager_cls = BifrostVarPathsManager

    @classmethod
    def _check_idl_filename_pattern(cls, snapname, filename):
        '''check that filename matches snapname_NNN.idl pattern. Crash if not.
        subclass might override, to avoid, enhance, or alter this check.
        returns match object from re.fullmatch.
        '''
        pattern = rf'{snapname}_([0-9]+)[.]idl'
        match = re.fullmatch(pattern, os.path.basename(filename))
        if match is None:
            errmsg = (f'Filename does not match snapname_NNN.idl pattern. '
                      f'snapname={snapname!r} filename={filename!r}')
            raise FileContentsConflictError(errmsg)
        return match

    @classmethod
    def from_idl_file(cls, filename, *, i=None):
        '''return BifrostSnap based on idl file.
        filename: str.
            file to read from. Like snapname_NNN.idl.
            will use s=NNN as label. E.g. snapname_071.idl --> s='071'.
            snapname determined from file contents (one of the params should be "snapname")
        i: None or int
            index of this snapshot in a SnapList.
        '''
        params = read_bifrost_snap_idl(filename)
        snapname = params['snapname']
        match = cls._check_idl_filename_pattern(snapname, filename)
        s = match.group(1)
        t = params.get('t', None)
        return cls(s=s, i=i, t=t, params=params)

    # # # PROPERTIES # # #
    @property
    def snapname(self):
        '''return snapname of this snap: self.params["snapname"]'''
        return self.params['snapname']

    @property
    def filename(self):
        '''return filename of idl file for this snap: snapname_NNN.idl'''
        return f'{self.snapname}_{self.s}.idl'

    # # # VAR PATH MANAGER # # #
    def var_paths_manager(self, calculator):
        '''return BifrostVarPathsManager for this snap.
        calculator: BifrostCalculator. used for snapdir.
        '''
        return self.var_paths_manager_cls(self, calculator)


class BifrostSnapList(ParamsSnapList):
    '''list of BifrostSnap objects'''
    value_type = BifrostSnap

    @classmethod
    def from_idl_files(cls, filenames):
        '''return BifrostSnapList based on idl files.
        order within result matches order of filenames.

        filenames: list of str.
            files to read from. Like snapname_NNN.idl.
            will use s=NNN as label. E.g. snapname_071.idl --> s='071'.
            snapname determined from file contents (one of the params should be "snapname")
        '''
        snaps = [cls.value_type.from_idl_file(f, i=i) for i, f in enumerate(filenames)]
        return cls(snaps)

    @classmethod
    def from_here(cls, snapname=None, *, dir=os.curdir):
        '''return BifrostSnapList from all snapname_NNN.idl files in directory.
        Sorted by snap number.

        snapname: None or str.
            snaplist from matching snapname_NNN.idl files. (NNN can be any integer, doesn't need to be 3 digits.)
            None --> infer; look for files like "*_NNN.idl" in dir;
                    if 0 such files or 2+ different implied snapnames, raise FileAmbiguityError.
        dir: str. directory to search in.
        '''
        if snapname is None: snapname = bifrost_infer_snapname_here(dir)
        filenames = bifrost_snap_idl_files(snapname, dir=dir)
        result = cls.from_idl_files(filenames)
        # quick check that snapname inside idl file 0 matches with idl file snapname.
        # (don't check all of them here because that could be somewhat slow.)
        if len(result) > 0 and result[0]['snapname'] != snapname:
            errmsg = (f'Snapname provided {snapname!r} does not match snapname param inside '
                      f'idl file {result[0].filename!r}: snapname={result[0]["snapname"]!r}')
            raise FileContentsConflictError(errmsg)
        return result

    # # # MISC PROPERTIES # # #
    @property
    def snapname(self):
        '''return snapname of this snaplist: self[0].snapname.
        returns None if no snaps in list.
        '''
        return self[0].snapname if len(self) > 0 else None


### --------------------- Special --------------------- ###

class BifrostScrSnap(BifrostSnap, SpecialDimensionValue):
    '''BifrostSnap corresponding to the ".scr" snapshot.
    There is at most 1 scr snap per Bifrost simulation.
    '''
    var_paths_manager_cls = BifrostScrVarPathsManager

    @classmethod
    def _check_idl_filename_pattern(cls, snapname, filename):
        '''check that filename matches snapname.idl.scr pattern. Crash if not.
        subclass might override, to avoid, enhance, or alter this check.
        '''
        pattern = rf'{snapname}.idl.(scr)'  # (scr) as group --> snap name will be 'scr'
        match = re.fullmatch(pattern, os.path.basename(filename))
        if match is None:
            errmsg = (f'Filename does not match snapname.idl.scr pattern. '
                      f'snapname={snapname!r} filename={filename!r}')
            raise FileContentsConflictError(errmsg)
        return match

    @classmethod
    def from_here(cls, snapname, *, dir=os.curdir, missing_ok=True):
        '''return BifrostScrSnap from the scr file with this snapname, in this directory.
        missing_ok: bool
            whether it is okay for scr file to be missing.
            True & missing --> return MISSING_SNAP.
            False & missing --> raise FileNotFoundError.
        '''
        scr_filename = f'{snapname}.idl.scr'
        scr_filepath = os.path.join(dir, scr_filename)
        if not os.path.exists(scr_filepath):
            if missing_ok: return MISSING_SNAP
            raise FileNotFoundError(f'Scr file not found: {scr_filepath!r}')
        return cls.from_idl_file(scr_filepath)
