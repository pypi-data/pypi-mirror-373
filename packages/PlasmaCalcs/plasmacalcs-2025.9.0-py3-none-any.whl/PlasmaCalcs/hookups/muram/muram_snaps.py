"""
File Purpose: code associated with Muram Snaps
"""
import os
import re

from .muram_io_tools import (
    muram_snap_files,
    read_muram_header,
    muram_directly_loadable_vars,
)
from ...dimensions import ParamsSnap, ParamsSnapList


### --------------------- MuramSnap and MuramSnapList --------------------- ###

class MuramSnap(ParamsSnap):
    '''info about a single muram snapshot, including label (str) and index (int).

    The "index" should only be meaningful in the context of a SnapList
    The "label" should be the str name for this snapshot
        - unique within context (e.g. there's only one "snapshot 1" in a simulation)
        - easiest to use str int labels (e.g. "snapshot 1" --> label="1")

    s: the label (str) of the snapshot. if None, cannot convert to str.
    i: the "index" (int) of the snapshot (within a SnapList). if None, cannot convert to int.
    t: time at this snapshot ['raw' units]
    params: dict of parameters (e.g. from .idl file) at this snapshot. if None, make empty dict.
    '''
    @classmethod
    def from_header_file(cls, filename, *, i=None):
        '''return MuramSnap based on Header.NNN file.
        filename: str
            file to read from. Like Header.NNN
            will use s=NNN as label. E.g. "Header.004321" --> label="004321"
        i: None or int
            index of this snapshot in a SnapList.
        '''
        params = read_muram_header(filename)
        s = params['snap_s']
        t = params['t']
        return cls(s=s, i=i, t=t, params=params)

    @property
    def filename(self):
        '''return the basename of snapshot's header file: Header.NNN'''
        return f'Header.{self.s}'
    @property
    def dirname(self):
        '''return the directory containing this snapshot's Header.NNN file.'''
        return self.params['dirname']  # equivalent: self['dirname']
    @property
    def filepath(self):
        '''return the abspath to this snapshot's Header.NNN file.'''
        return os.path.join(self.dirname, self.filename)

    def directly_loadable_vars(self):
        '''return the list of directly loadable vars for this snap.'''
        return muram_directly_loadable_vars(self.s, dir=self.dirname)


class MuramSnapList(ParamsSnapList):
    '''list of MuramSnap objects'''
    value_type = MuramSnap

    @classmethod
    def from_header_files(cls, filenames):
        '''return MuramSnapList from a list of header files.
        order within result matches order of filenames.

        filenames: list of str
            list of filenames to read from. Like Header.NNN
            will use s=NNN as label. E.g. "Header.004321" --> label="004321"
        '''
        snaps = [cls.value_type.from_header_file(f, i=i) for i, f in enumerate(filenames)]
        return cls(snaps)

    @classmethod
    def from_here(cls, *, dir=os.curdir):
        '''return MuramSnapList from all Header.NNN files in directory.
        Sorted by snap number.
        dir: str. directory to look in.
        '''
        filenames = muram_snap_files(dir=dir)
        return cls.from_header_files(filenames)
