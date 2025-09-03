"""
File Purpose: misc. tools for reading directly from Copapic files
"""
import collections
import datetime
import os
import re
import pandas as pd
import xarray as xr
import json

# from ...errors import (
#     ValueLoadingError,
#     FileContentsError, FileContentsConflictError, FileContentsMissingError,
#     InputError,
# )
from ...tools import (
    InDir
)

### --------------------- read copapic.json file --------------------- ###

def read_copapic_json_file(filename):
    '''Parse Copapic input from the file, returning (dict of global vars, dict of dists).
    dict of global vars has {varname: value} for all pairs not inside a distribution.
    dict of dists has {N: {varname: value} for all pairs in dist} for each dist;
        for each varname in a dist, ensure varname ends with str(N) (append it if necessary).
        the N's will all be stored here as ints.

    Arguments:
    filename: string
        file to read from.
    '''
    deck = json.load(open(filename, 'r'))
    return deck


def read_copapic_snaps_info(snaps_from, dt, dir=os.curdir):
    '''returns (snapnames, times).
    snaps_from: string
        directory of output files. Corresponds to the title of the simulation.
    dir: string (default '.')
        directory of 'copapic.json' file.
    dt: None or value
        the simulation time step; each snap's time is equal to dt * (snap name)
        if None, attempt to read 'dt' from copapic.json file.
    '''
    with InDir(dir):  # temporarily cd to dir; restore original dir after.
        # get snaps
        snapnums = []
        if not os.path.isdir(snaps_from):
            return ([], [])
        for filename in os.listdir(snaps_from):  # directory named 'parallel'
            match = re.match(r'data_(\d+)\.', filename[:-2])
            if match:
                snapname, = match.groups()
                snapnums.append(int(snapname))

    snapnums = sorted(snapnums)
    snapnames, times = [], []
    for snapnum in snapnums:
        snapnames.append(str(snapnum))
        times.append(dt * snapnum)
    return (snapnames, times)