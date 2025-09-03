"""
File Purpose: reading genrad tables, e.g. radtab.dat files.
These include lookup tables which might improve ion densities compared to saha.
"""
import os

import numpy as np
import xarray as xr

from .mhd_fluids import ElementHaver
from ...defaults import DEFAULTS
from ...errors import (
    InputError,
    FileContentsError,
    FluidKeyError,
)
from ...tools import alias

# location of the folder in PlasmaCalcs containing default genrad tables, on this machine.
# this is used when trying to get one of the default genrad tables.
# __file__ means the file where this line of code is located.
DEFAULTS.GENRAD_TAB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mhd_tables')

def _float(s):
    '''convert fortran float string to np.float64.'''
    return np.float64(s.replace('d', 'e'))

def _consume_comment_lines(enumlines, *, start=None, comment=None):
    r'''eat (i, line) from enumlines until reaching a nonempty line that doesn't start with '*'.
    return (next(enumlines), comment.strip()) where next(enumlines) is the next line.

    start: None or (i, line)
        if provided, start here. Otherwise, start at next(enumlines)
    comment: None or str
        if provided, append result to this comment + '\n'.
    '''
    comment = '' if comment is None else (comment + '\n')
    if start is None:
        start = next(enumlines)
    i, line = start
    while line.startswith('*') or len(line)==0:
        if len(line) != 0:
            comment += line[len('*'):].strip() + '\n'
        i, line = next(enumlines)
    return ((i, line), comment.strip())

def _consume_data_lines(enumlines, *, start=None, Nnums=None, var=None):
    '''eat (i, line) from enumlines until reaching a line that startswith ' or *
    treat these lines as data; split() and convert from fortran float strs to np.float64.
    return (next(enumlines), data), where next(enumlines) is the next line.
    
    start: None or (i, line)
        if provided, start here. Otherwise, start at next(enumlines)
    Nnums: None or int
        if provided, ensure len(data)==N_nums, else crash with FileContentsError.
    var: None or str
        if provided, included this name in errmsg if crashing with FileContentsError.
    '''
    datalines = []
    if start is None:
        start = next(enumlines)
    i, line = start
    while (not line.startswith("'")) and (not line.startswith('*')):
        datalines.append(line)
        i, line = next(enumlines)
    data_str = ' '.join(datalines).split()
    data = [_float(num) for num in data_str]  # fortran float sometimes uses d instead of e
    if (Nnums is not None) and (len(data) != Nnums):
        errmsg = f'got {len(data)} numbers, expected {Nnums}, near line {i}'
        if var is not None:
            errmsg = errmsg + f', for var={var!r}'
        raise FileContentsError(errmsg)
    return ((i, line), data)

def _consume_indepvar_data_lines(enumlines, *, start=None, var=None):
    '''eat (i, line) from enumlines until reaching a line that startswith ' or *
    expect first line to be an int, and remaining lines to contain that many values.
    treat remaining lines as data; split() and convert from fortran float strs to np.float64.
    return (next(enumlines), data), where next(enumlines) is the next line.
    
    start: None or (i, line)
        if provided, start here. Otherwise, start at next(enumlines)
    var: None or str
        if provided, included this name in errmsg if crashing with FileContentsError.
    '''
    if start is None:
        start = next(enumlines)
    i, line = start
    try:
        Nnums = int(line)
    except ValueError:
        errmsg = f'expected integer on line {i}'
        if var is not None: errmsg += f', for var={var!r}'
        errmsg += f', got line={line!r}'
        raise FileContentsError(errmsg)
    return _consume_data_lines(enumlines, start=next(enumlines), Nnums=Nnums, var=var)


class GenradTable():
    '''single table from genrad file, with some var as a function of T, tauh, or column mass.
    
    indict: dict with length 1
        key = independent variable name. Probably 'temp', 'tauh', or 'cmass'.
        indict[key] = independent variable data
    outdict: dict with length 1
        key = dependent variable name
        outdict[key] = dependent variable data
    coords: None or dict of scalars
        if provided, assign these coords to self.xtable.
    comment: None or str
        if provided, any arbitrary comment about this variable.
    
    self will also store self.xtable, an xarray.DataArray, with
        name = outdict key
        values = outdict values
        coords = {xtable[indict key]: indict values}
    '''
    def __init__(self, indict, outdict, *, coords=None, comment=None):
        self.indict = indict
        self.outdict = outdict
        self.coords = coords
        self.comment = comment
        self.init_checks()
        self.init_xtable()
        
    def init_checks(self):
        if not isinstance(self.indict, dict):
            raise InputError('expected indict to be a dict')
        if not isinstance(self.outdict, dict):
            raise InputError('expected outdict to be a dict')
        if len(self.indict) != 1:
            raise InputError('expected indict to have length 1')
        if len(self.outdict) != 1:
            raise InputError('expected outdict to have length 1')

    invar = property(lambda self: list(self.indict.keys())[0], doc='independent variable name')
    outvar = property(lambda self: list(self.outdict.keys())[0], doc='dependent variable name')
    invals = property(lambda self: np.asanyarray(self.indict[self.invar]), doc='independent variable values')
    outvals = property(lambda self: np.asanyarray(self.outdict[self.outvar]), doc='dependent variable values')
    
    def init_xtable(self):
        '''initialize self.xtable.'''
        kw = dict(
            dims=[self.invar],
            coords={self.invar: self.invals},
            name=self.outvar,
        )
        if self.coords is not None:
            kw['coords'] = {**kw['coords'], **self.coords}
        if self.comment is not None:
            kw['attrs'] = {'comment': self.comment}
        self.xtable = xr.DataArray(self.outvals, **kw)

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'{self.invar!r}', f'{self.outvar!r}', f'len={self.invals.size}']
        if self.comment is not None:
            comment = self.comment.split('\n')
            comminfo = f'comment={comment[0][:40]!r}'
            if len(comment[0]) > 40 or len(comment) > 1:
                comminfo += '...'
            contents.append(comminfo)
        return f'{type(self).__name__}({", ".join(contents)})'

    # # # INTERPOLATING # # #
    __call__ = alias('interp')

    def interp(self, invalues, *, fill_value='extrapolate', **kw_xarray_interp):
        '''interpolate from self.xtable.interp(**kw_interp).
        invalues: values of independent variable. Same units as self.invals.
        '''
        kwargs = None if fill_value is None else dict(fill_value=fill_value)
        kw = dict(kwargs=kwargs, **kw_xarray_interp)
        return self.xtable.interp({self.invar: invalues}, **kw)


class GenradTableManager(dict):
    '''manages genrad tables. Dict of {quantity (str): GenradTable}.

    thresh: 2-tuple of (values, comment)
        thresh values & comment from genrad file. [TODO] what do they mean?
        internally stored as (self.thresh, self.threshcomment)
    incrad: 2-tuple of (value, comment)
        incrad values & comment from genrad file. [TODO] what dooes it mean?
        internally stored as (self.incrad, self.incradcomment)

    self.filename will tell abspath to file if created self via GenradTableManager.from_file()
    '''
    genrad_table_cls = GenradTable
    INDEP_VARS = ['temp', 'tauh', 'cmass']  # <-- treat these as independent variables.

    def __init__(self, *args_dict, thresh=(None, None), incrad=(None, None), **kw_dict):
        (self.thresh, self.threshcomment) = thresh
        (self.incrad, self.incradcomment) = incrad
        super().__init__(*args_dict, **kw_dict)

    @classmethod
    def from_defaults(cls, name='radtab'):
        '''return GenradTableManager from one of the default genrad table files.
        name = one of cls.DEFAULTS.keys().
        '''
        try:
            filename = cls.DEFAULTS[name]
        except KeyError:
            raise InputError(f'name={name!r}; expected one of {tuple(cls.DEFAULTS.keys())}.') from None
        filepath = os.path.join(DEFAULTS.GENRAD_TAB_DIR, filename)
        return cls.from_file(filepath)

    DEFAULTS = {  # dict of {shorthand name: filename}
        'radtab': 'radtab.dat',
    }

    @classmethod
    def from_file(cls, genrad_file):
        '''load genrad tables from file.'''
        with open(genrad_file, 'r') as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]

        result = {}
        kw_result = {}
        enumlines = enumerate(lines)
        # get header
        (i, line), header = _consume_comment_lines(enumlines)
        # get 'thin' data
        if line.strip() != "'temp'":  # expect first independent var=='temp'
            raise NotImplementedError(f"reading genrad file when first non-comment line (i={i}; line={line!r}) isn't 'temp'.")
        (i, line), tempdata = _consume_indepvar_data_lines(enumlines, var='temp')
        (i, line), thincomment = _consume_comment_lines(enumlines, start=(i, line))
        if line.strip() != "'thin'":  # expect first dependent var=='thin'
            raise NotImplementedError(f"reading genrad file when first dependent var (i={i}; line={line!r}) isn't 'thin'.")
        (i, line), thincomment = _consume_comment_lines(enumlines, comment=thincomment)
        thinunits = _float(line)  # at least, I think this is units... anyways, there's a single number before the data.
        (i, line), thindata = _consume_data_lines(enumlines, Nnums=len(tempdata), var='thin')
        result['thin'] = GenradTable({'temp': tempdata}, {'thin': thindata}, coords={'units?': thinunits}, comment=thincomment)
        # get 'thresh' values
        (i, line), threshcomment = _consume_comment_lines(enumlines, start=(i, line))
        if line.strip() != "'thresh'":  # expect var=='thresh'
            raise NotImplementedError(f"reading genrad file when var after 'thin' is not 'thresh'. Got i={i}; line={line!r}.")
        (i, line), threshcomment = _consume_comment_lines(enumlines, comment=threshcomment)
        (i, line), threshdata = _consume_data_lines(enumlines, start=(i, line), Nnums=2, var='thresh')  # tmin, tscl
        kw_result['thresh'] = (threshdata, threshcomment)
        # get 'incrad' value
        (i, line), incradcomment = _consume_comment_lines(enumlines, start=(i, line))
        if line.strip() != "'incrad'":  # expect var=='incrad'
            raise NotImplementedError(f"reading genrad file when var after 'thresh' is not 'incrad'. Got i={i}; line={line!r}.")
        (i, line), incradcomment = _consume_comment_lines(enumlines, comment=incradcomment)
        (i, line), incraddata = _consume_data_lines(enumlines, start=(i, line), Nnums=1, var='incrad')
        kw_result['incrad'] = (incraddata[0], incradcomment)
        # get first independent variable
        (i, line), comment = _consume_comment_lines(enumlines, start=(i, line))
        indepvar = line.strip().strip("'")
        if indepvar not in cls.INDEP_VARS:
            raise FileContentsError(f"expected one of the INDEP_VARS {cls.INDEP_VARS}. Got i={i}; line={line!r}.")
        (i, line), indepdata = _consume_indepvar_data_lines(enumlines, var=indepvar)
        # get first dependent variable
        (i, line), comment = _consume_comment_lines(enumlines, start=(i, line), comment=comment)
        depvar = line.strip().strip("'")
        (i, line), depdata = _consume_data_lines(enumlines, var=depvar, Nnums=len(indepdata))
        result[depvar] = GenradTable({indepvar: indepdata}, {depvar: depdata}, comment=comment)

        # the rest of this file has a bunch of variables then data. Sometimes multiple dependent vars for same independent.
        (i, line), comment = _consume_comment_lines(enumlines, start=(i, line))
        var = line.strip().strip("'")
        while var != 'end':
            if var in cls.INDEP_VARS:
                indepvar = var
                (i, line), indepdata = _consume_indepvar_data_lines(enumlines, var=indepvar)
            else:
                depvar = var
                (i, line), depdata = _consume_data_lines(enumlines, var=depvar, Nnums=len(indepdata))
                result[depvar] = GenradTable({indepvar: indepdata}, {depvar: depdata}, comment=comment)
                comment = ''  # reset the comment to empty string after each dependent var.
            (i, line), comment = _consume_comment_lines(enumlines, start=(i, line), comment=comment)
            var = line.strip().strip("'")

        result = cls(result, **kw_result)
        result.filename = os.path.abspath(genrad_file)
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        if len(self) <= 1:
            contents_str = super().__repr__()
        else:
            contents = [f'{key!r}: {val}' for key, val in self.items()]
            contents_str = '{\n    ' + ',\n    '.join(contents) + '\n}'
        return f'{type(self).__name__}({contents_str})'

    # # # INTERPOLATING # # #
    __call__ = alias('interp')

    def interp(self, var, invalues, **kw_interp):
        '''interpolate var from self[var].interp(values, **kw_interp).'''
        return self[var].interp(invalues, **kw_interp)

    # # # CHECKING AVAILABLE SPECIES # # #
    def neufrac_available(self, elem=None):
        '''return dict of {element name: neufrac variable}
        such that self[neufrac variable] = table telling neutral fraction for this element,
            as a funtion of temperature.

        elem: None, str, or ElementHaver (e.g. Element or Specie)
            if provided, return neufrac variable for elem (if str, else elem.get_element()).
            if no neufrac variable exists for this elem, return None.
        '''
        result = {}
        if 'h_ion' in self:
            result['H'] = 'h_ion'
        if 'mg_ion' in self:
            result['Mg'] = 'mg_ion'
        if 'ca_ion' in self:
            result['Ca'] = 'ca_ion'
        # [TODO] ^^ other elements must be added here in order for self('ionfrac_radtab') to know about them.
        if elem is None:
            return result
        if isinstance(elem, ElementHaver):
            elem = str(elem.get_element())
        return result.get(elem, None)

    def neufrac_table(self, elem):
        '''return self[var] for var telling neufrac for this elem.
        elem: str or ElementHaver (e.g. Element or Specie)
            element name, element, or object with elem.get_element().
        '''
        neufrac_var = self.neufrac_available(elem)
        if neufrac_var is None:
            raise FluidKeyError(f'no neutral fraction table available for elem={elem!r}.')
        return self[neufrac_var]
