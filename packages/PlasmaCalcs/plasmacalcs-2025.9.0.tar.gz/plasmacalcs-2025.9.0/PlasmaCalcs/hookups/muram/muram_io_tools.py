"""
File Purpose: misc. tools for reading directly from muram files
"""
import os
import re

import numpy as np

from ...errors import InputError


### --------------------- muram param files --------------------- ###

def muram_snap_files(dir=os.curdir, *, abspath=False):
    '''return list of all muram Header.NNN files in directory.
    Sorts by snap number.

    abspath: bool. whether to return absolute paths or just the file basenames within directory.
    '''
    pattern = rf'Header[.]([0-9]+)'
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

def read_muram_header(filename):
    '''Parse Muram Header.NNN file into a dictionary, containing:
        'order': 3-tuple containing 0,1,2 in same order as layout.order file
        'N0', 'N1', 'N2': number of cells in 0th, 1st, 2nd dimensions in data files.
        'Nx', 'Ny', 'Nz': number of cells in x, y, z dimensions
        'dx', 'dy', 'dz': cell width in each dimension
        't': time of this snapshot, in 'raw' units.
        'snap_s': snap number as a string, e.g. '004321'
        'dirname': directory containing the header file.

    Header file should contain at least 7 numbers, separated by whitespace:
        size0  size1  size2  ds0  ds1  ds2  time
    telling the number of cells (sizex) and cell width (dsx) in each dimension x=0,1,2,
        and the time t of this snapshot.

    params are mapped to x,y,z via the 'layout.order' file (in same dir as Header.NNN file).
        'layout.order' should contain only:
            0  1  2
        in any order, separated by whitespace.
    then e.g. the x size will be [size0, size1, size2][order[0]].
    (for y use order[1]; for z use order[2].)
    The dimensions in memmap files correspond to the order here;
        MuramCalculator.load_direct() handles transposing appropriately.
    '''
    filename = os.path.abspath(filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError(f'file not found: {filename!r}')
    pattern = r'Header[.]([0-9]+)'
    match = re.fullmatch(pattern, os.path.basename(filename))
    if match is None:
        raise InputError(f'filename={os.path.basename(filename)!r} must match pattern={pattern!r}')
    snap_s = match.group(1)
    dirname = os.path.dirname(filename)
    layout_order_file = os.path.join(dirname, 'layout.order')
    if not os.path.isfile(layout_order_file):
        raise FileNotFoundError(f'layout.order file not found: {layout_order_file!r}')
    order = np.loadtxt(layout_order_file, dtype=int)
    header = np.loadtxt(filename)
    sizes_012 = header[:3].astype(int)
    sizes_xyz = sizes_012[order]
    ds = header[3:6][order]
    time = header[6]
    result = dict(order=order,
                  N0=sizes_012[0], N1=sizes_012[1], N2=sizes_012[2],
                  Nx=sizes_xyz[0], Ny=sizes_xyz[1], Nz=sizes_xyz[2],
                  dx=ds[0], dy=ds[1], dz=ds[2], t=time,
                  snap_s=snap_s, dirname=dirname,
                  )
    return result

def muram_directly_loadable_vars(snap_s, *, dir=os.curdir):
    '''return list of directly loadable vars for this snap, in this directory.
    snap_s: str
        snap number, as a string.
        E.g. if header file is 'Header.004321', snap_s should be '004321'.
    dir: str
        directory in which to search for files. Default: current directory.
    '''
    pattern = rf'(.+)[.]{snap_s}'  # var.{snap_s}
    result = []
    for f in os.listdir(dir):
        match = re.fullmatch(pattern, f)
        if match is not None:
            result.append(match.group(1))
    return sorted(result)
