"""
File Purpose: tools related to cross sections for collisions
"""

import ast
import os

import numpy as np
import xarray as xr

from ...errors import FileContentsError, InputError
from ...units import UnitsManager
from ...tools import (
    simple_property, alias,
    SymmetricPairMapping,
)

from ...defaults import DEFAULTS

# location of the cross_section_tables folder, on this machine.
# this is used when trying to get one of the default cross section tables.
# __file__ means the file where this line of code is located.
DEFAULTS.CROSS_SECTIONS_DIR = os.path.join(os.path.dirname(__file__), 'cross_section_tables')


class UnitsManagerCrossUnits(UnitsManager):
    '''UnitsManager for cross sections, since crossunits are in [cm^-2].'''
    @classmethod
    def from_crossunits(cls, crossunits, **kw):
        '''return UnitsManagerCrossUnits with length units conversions based on crossunits.
            cross_section [si] = result('area', 'si') * cross_section [from file]
        equivalent to cls(l=np.sqrt(crossunits) * 1e-2, **kw)
        '''
        l = np.sqrt(crossunits) * 1e-2   # the 1e-2 converts cm to m
        return cls(l=l, **kw)


### --------------------- CrossTable, and getting from file --------------------- ###

class CrossTable():
    '''stores data about a cross sections table.

    kT: temperatures [eV]. array of values
    cross: cross sections [crossunits]. array of values
    crossunits: conversion factor; cross * crossunits = cross section [cm^-2]. single value.
    fc  numerical factor, based on convention of the cross table.
        when getting the collision frequency, the formula needs to use fc * cross.
        PlasmaCalcs 'collisions_cross_section' ('collcross') already includes the fc factor.
        The value of fc should probably be set as follows:
            tables utilizing Bruno+2010 should have fc=4/3.
            tables utilizing Vranjes+2013 should have fc=1.
        By default, should prefer to use Bruno+2010 (hence the default is 4/3),
            as explained in Wargnier+2022.

    note: some cross tables are available by default;
        these can be loaded with cls.default(name), where name is one of cls.DEFAULTS.keys().
    '''
    # # # INITIALIZATION / CREATION # # #
    def __init__(self, kT, cross, crossunits, fc=4/3):
        self.kT = kT
        self.cross = cross
        self.crossunits = crossunits
        self.fc = fc
        self.u = UnitsManagerCrossUnits.from_crossunits(crossunits)

    @classmethod
    def from_file(cls, filename, fc=4/3):
        '''return CrossTable from file. Be sure to put the appropriate value of fc.
        Bruno+2010 should have fc=4/3. Vranjes+2013 should have fc=1.
        see help(CrossTable) for more fc info. 
        '''
        cross_data = read_cross_text(filename)
        result = cls(**cross_data, fc=fc)
        result.filename = os.path.abspath(filename)
        result.dirname = os.path.dirname(result.filename)
        result.filebase = os.path.basename(result.filename)
        return result

    @classmethod
    def from_defaults(cls, name):
        '''return CrossTable from one of the default cross table files.
        name = one of cls.DEFAULTS.keys().
        '''
        filename, fc = cls._default_file(name)
        return cls.from_file(filename, fc=fc)

    DEFAULTS = {   # dict of {shorthand: (filename, fc)}
        # shorthand: e=electrons; p=protons; h=H(neutral); he=He(neutral); hep=He+; hepp=He++
        # order doesn't really matter, but grouping files here for better readability...
        # -- bruno -- charged-neutral collisions --
        'e-h'    : ('e-h-bruno-fits.txt',     4/3),
        'e-he'   : ('e-he-bruno-fits.txt',    4/3),
        'h-p'    : ('h-p-bruno-fits.txt',     4/3),
        'h-hep'  : ('h-hep-bruno-fits.txt',   4/3),
        'h-hepp' : ('h-hepp-bruno-fits.txt',  4/3),
        'he-p'   : ('he-p-bruno-fits.txt',    4/3),
        'he-hep' : ('he-hep-bruno-fits.txt',  4/3),
        'he-hepp': ('he-hepp-bruno-fits.txt', 4/3),
        # -- bruno -- neutral-neutral collisions --
        'h-h'    : ('h-h-bruno-fits.txt',     4/3),
        'he-h'   : ('he-h-bruno-fits.txt',    4/3),
        'he-he'  : ('he-he-bruno-fits.txt',   4/3),
        # -- vranjes -- charged-neutral collisions --
        'e-h_vranjes'  : (os.path.join('vranjes', 'e-h-cross.txt'), 1),
        'e-he_vranjes' : (os.path.join('vranjes', 'e-he-cross.txt'), 1),
        'h-p_vranjes'  : (os.path.join('vranjes', 'p-h-cross.txt'), 1),
        'he-p_vranjes' : (os.path.join('vranjes', 'p-he-cross.txt'), 1),
        # -- vranjes -- neutral-neutral collisions --
        'h-h_vranjes'  : (os.path.join('vranjes', 'h-h-cross.txt'), 1),
        'he-he_vranjes': (os.path.join('vranjes', 'he-he-cross.txt'), 1),
    }

    @classmethod
    def _default_file(cls, name):
        '''return (abspath to one of the default cross table files, fc for that file)
        name = one of cls.DEFAULTS.keys().
        '''
        try:
            filename, fc = cls.DEFAULTS[name]
        except KeyError:  # make a nicer error message in this case.
            raise InputError(f'name={name!r}; expected one of {tuple(cls.DEFAULTS.keys())}.') from None
        return (os.path.join(DEFAULTS.CROSS_SECTIONS_DIR, filename), fc)

    # # # PROPERTIES / DATA # # #
    T = simple_property('_T', setdefaultvia='_get_T', doc='''temperatures [K], associated with kT.''')

    def _get_T(self):
        '''return T based on self.kT'''
        return self.kT * self.u('eV kB-1', 'si')

    @property
    def cross_si(self):
        '''cross sections, in [m^-2].'''  # [TODO][EFF] caching?
        return self.cross * self.u('area', 'si')

    @property
    def collcross_si(self):
        '''cross sections, in [m^-2], multiplied by fc.'''
        return self.cross_si * self.fc

    def lims(self, attr):
        '''return self.attr.min(), self.attr.max()'''
        val = getattr(self, attr)
        return val.min(), val.max()

    def keys(self):
        '''returns keys of self, as a list.
        These are: ['kT', 'cross', 'cross_si', 'crossunits', 'T']
        '''
        return ['kT', 'cross', 'cross_si', 'crossunits', 'T']

    def __getitem__(self, key):
        '''returns self.key, if key in self.keys().'''
        keys = self.keys()
        if key in keys:
            return getattr(self, key)
        else:
            raise KeyError(f'key={key!r} not recognized; expected one of {keys}')

    # # # INTERPOLATING # # #
    def interp(self, value, input='T', output='collcross_si', *, log=True, **kw_interp):
        '''interpolate value from input (default: 'T') to output (default: 'collcross_si')
        returns result like value (e.g., number if number; array if array),
            with numerical values corresponding to output variable instead of input variable.

        value: number or array-like
            values to interpolate
            note: if value is an xarray, return an xarray with same dims, attrs, and coords as value.
        input: str
            input variable; should be an attribute of self.
            value is a value of this variable.
        output: str
            output variable; should be an attribute of self.
            result is a value of this variable.
        log: bool, default True
            whether to interpolate on log scale.
            True --> interpolate log10(value) against log10(input).
        additional kwargs go to np.interp.

        example: interp(2000, 'T', 'cross_si') --> single value, with cross section at T=2000 K.
        '''
        # get input values
        input_vals = getattr(self, input)
        output_vals = getattr(self, output)
        # interpolate
        if log:
            input_vals = np.log10(input_vals)
            value = np.log10(value)
        result = np.interp(value, input_vals, output_vals, **kw_interp)
        if isinstance(value, xr.DataArray):  # convert back to xarray if needed!
            result = xr.DataArray(result, dims=value.dims, attrs=value.attrs, coords=value.coords)
        return result

    __call__ = alias('interp')

    # # # CONVENIENT # # #
    def __len__(self):
        return len(self.kT)

    # # # DISPLAY # # #
    def __repr__(self):
        Tmin, Tmax = self.lims('T')
        cmin, cmax = self.lims('cross_si')
        contents = [f'len={len(self)}',
                    f'T min={Tmin:.2e}, max={Tmax:.2e} [K]',
                    f'cross min={cmin:.2e}, max={cmax:.2e} [m^-2]',
                    f'crossunits={self.crossunits:.2e} cm^-2',
                    f'fc={self.fc:.2f}']
        cstr = ' | '.join(contents)
        return f'{type(self).__name__}({cstr})'

    def __str__(self):
        filebase = getattr(self, 'filebase', None)
        if filebase is not None:
            return f'{type(self).__name__}({filebase!r})'
        else:
            Tmin, Tmax = self.lims('T')
            cmin, cmax = self.lims('cross_si')
            contents = [f'{Tmin:.1e} < T < {Tmax:.1e} K', f'{cmin:.1e} < cross < {cmax:.1e} m^-2']
            cstr = ', '.join(contents)
            return f'{type(self).__name__}({cstr})'


def read_cross_text(filename):
    '''reads cross sections from text file.
    returns a dictionary with keys 'kT', 'cross'. 
        kT = Temperature [eV]. array of values
        cross = cross section [crossunits]. array of values
        crossunits = conversion factor; cross * crossunits = cross section [cm^-2]. single value.

    raises FileContentsError if file is invalid.

    Text file should look like:
        ; any number of blank lines or lines with comments (starting with ';'),
        ;    at any point in the file, are permitted.
        ; ALWAYS ignores any portion of a line after a ';'

        1.0e-16   ; a single number. this is the "crossunits".
        ; Cross sections in this file represent value [cm^-2] = (value in file) * crossunits

        ; E (eV)      (ignored values)    cross section [crossunits]
           0.100        -1.0000           33.873
           0.297        -1.0000           33.350
           0.801        -1.0000           26.996
           1.306        -1.0000           22.475
           1.647        -1.0000           20.092
           1.988        -1.0000           17.587

        ; ... etc. Values above are just an example
        ; any nonzero amount of whitespace between values is allowed.

        ; Extra values (more than 3 values per line) are allowed, but ignored if provided.
    '''
    result = dict(kT=[], cross=[])
    with open(filename, 'r') as f:
        lines = f.readlines()
    _absfile = os.path.abspath(filename)  # useful for error messages / debugging
    # sanitize lines
    lines = [line.split(';', maxsplit=1)[0] for line in lines]  # remove comments
    lines = [line.strip() for line in lines]  # remove whitespace
    lines = [line.split() for line in lines]  # split into words
    # loop through lines, take relevant lines.
    for _i, line in enumerate(lines):   # track i_ to make debugging easier, if there's a crash.
        if len(line) == 0:
            continue  # ignore empty lines
        elif len(line) == 1:
            if 'crossunits' in result:
                errmsg = f'Line {_i} has exactly 1 value in it, but crossunits was already found! file={_absfile!r}'
                raise FileContentsError(errmsg)
            else:
                result['crossunits'] = ast.literal_eval(line[0])
        elif len(line) == 2:
            errmsg = f'Line {_i} has exactly 2 values in it; expected 0, 1, or >2 values. file={_absfile!r}'
            raise FileContentsError(errmsg)
        else:   # len(line) >= 3:
            kT = ast.literal_eval(line[0])
            # ignore line[1]
            cross = ast.literal_eval(line[2])
            # ignore line[3 or more]
            result['kT'].append(kT)
            result['cross'].append(cross)
    # convert to numpy arrays
    for key in ('kT', 'cross'):
        result[key] = np.array(result[key])
    return result


### --------------------- CrossMapping --------------------- ###

class CrossMapping(SymmetricPairMapping):
    '''SymmetricPairMapping where values are CrossTable objects.

    smart: True, False, 'files', or 'defaults'
        if smart, values can also be strings.
        'files' --> strings are interepreted as filenames.
        'defaults' --> strings are interpreted as one of the keys for CrossTable.from_defaults.
        True --> use 'files' mode if the file exists, else 'defaults' mode, for strings.
        False --> strings are not allowed; all entries must be CrossTable objects.

        string values are converted into CrossTable objects immediately, during self[key] = value;
    '''
    cross_table_type = CrossTable

    def __init__(self, mapping=dict(), *, smart=True):
        self.smart = smart
        super().__init__(mapping)

    def __setitem__(self, key, value):
        '''set self.mapping[key] = value.
        key: tuple of (obj1, obj2). If obj2 < obj1, will use (obj2, obj1) instead.
        value: CrossTable object
        '''
        smart = self.smart
        if smart and isinstance(value, str):
            if isinstance(smart, str):
                if smart == 'files':
                    value = self.cross_table_type.from_file(value)
                elif smart == 'defaults':
                    value = self.cross_table_type.from_defaults(value)
                else:
                    raise ValueError(f'smart={smart!r} not recognized.')
            else:  # smart = True; try both modes.
                if os.path.isfile(value):
                    value = self.cross_table_type.from_file(value)
                else:
                    value = self.cross_table_type.from_defaults(value)
        else:  # not smart
            if not isinstance(value, CrossTable):
                raise TypeError(f'value={value!r} must be a CrossTable object')
        super().__setitem__(key, value)

    # # # DISPLAY # # #
    _repr_newlines = True  # put newlines bewteen each key-value pair in __repr__

    def __str__(self):
        keys = tuple(self.keys())
        vals = tuple(self.values())
        keys = [f'({key[0]!s}, {key[1]!s})' for key in keys]
        vals = [(str(val) if getattr(val, 'filebase', None) is None else val.filebase) for val in vals]
        contents = ', '.join(f'{key}: {val!r}' for key, val in zip(keys, vals))
        return f'{type(self).__name__}({contents})'
