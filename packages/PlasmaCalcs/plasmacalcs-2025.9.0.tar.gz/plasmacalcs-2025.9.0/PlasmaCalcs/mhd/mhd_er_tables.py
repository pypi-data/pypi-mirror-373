"""
File Purpose: equation of state (EOS) and radiation tables for single-fluid MHD analysis;
Function of eperm (internal energy per unit mass) and r (mass density) --> quantity,
    for various quantities like pressure, temperature, entropy, opacity.

Optionally, can provide e (internal energy density) instead of eperm;
    in that case will convert internally via eperm = e / r.
"""

import os

import numpy as np
import xarray as xr

from .elements import ElementList
from ..errors import (
    DimensionalityError,
    FileContentsError,
    InputConflictError, InputMissingError,
)
from ..tools import (
    alias, simple_property,
    format_docstring,
    UNSET, NO_VALUE,
    using_attrs,
    read_idl_params_file, attempt_literal_eval,
    DictlikeFromKeysAndGetitem,
    product, is_iterable,
    xarray_is_sorted, xarray_interp_inverse,
)
from ..units import UnitsHaver


### --------------------- eperm rho tables --------------------- ###

_paramdocs_ertable = {
    # making erTable
    'xtable': '''UNSET or xarray.DataArray, probably 2D
        must have dims & coords for 'eperm' and 'r'.
        eperm = internal energy per unit mass; r = mass density.
        UNSET --> will call self.load_xtable() to load it.''',
    'quantity': '''None or str
        name of quantity, if known.''',
    'ln_quant': '''bool
        whether this quantity's values are in ln-space. E.g. ln(P) instead of P.''',
    'array': '''array, at least 2D
        first two dims must correspond to r (dim0), and eperm (dim1)
        additional dims will be unlabeled, E.g. dim_2, dim_3, dim_4, ...''',
    'kw_er_coords': '''epermcoords, rcoords: 1D array
        coords for eperm (energy per unit mass) and r (mass density).
        Units should be 'raw' units.''',
    # erTable from memmap
    'extra_dims': '''extra_dims: None, list of str, or dict
        if provided, will be used as names for additional xarray dims.
        if dict, will be used as names and coords for additional dims.''',
    'data_shape': '''None or tuple
        shape of a single array in the memmap file.
        None --> infer shape = (len(epermcoords), len(rcoords))''',
    'data_dtype': '''data_dtype: np.dtype or something which implies np.dtype
        dtype of the data in memmap file''',
    'data_order': ''''C' or 'F'
        order of the data in memmap file. 'F' is Fortran order.''',
    'scale_quant': '''number, default 1.
        scale quantity by this value immediately after reading from memmap.
        (always corresponds to the not-ln'd quant, even if ln_quant=True).''',
    'scale_quants': r'''dict
        {quantity: scaling factor} for each quantity in file. Default scaling factor is 1.
        quantity value * scaling factor should always convert to 'raw' units.
        (always corresponds to the not-ln'd quant, even if ln_quant=True).''',
    # calling interp
    'r': '''number or array
        evaluate table at these value(s) of r (mass density).''',
    'eperm': '''UNSET, number, or array
        evaluate table at these value(s) of eperm (internal energy per unit mass).
        must provide eperm or e, but not both.''',
    'e': '''UNSET, number, or array
        evaluate table at these value(s) of e (internal energy density).
        since table uses eperm and r, internally convert e to eperm via eperm = e / r.
        must provide eperm or e, but not both.''',
    'ln': '''bool
        whether to report result in ln-space, e.g. ln(P) instead of P.''',
    'keep_er_coords': '''bool
        whether to keep eperm and r as coords in result.''',
    # handling units
    'u': '''None or UnitsManager
        used to calculate scale_quants to convert to 'raw' units.
        None --> all scale quants will be 1.''',
    'units_input': '''None, 'raw', 'cgs', or 'si'
        inputs unit system (for eperm, r, and quantity).
        ignored if u is trivial, else required.''',
}

@format_docstring(**_paramdocs_ertable)
class erTable():
    '''lookup table from eperm and r to quantity. Units are always 'raw' units.
    Call self(r=r, eperm=eperm) to get value of quantity at eperm and r.
        (equivalent: self.interp(r=r, eperm=eperm). See help(self.interp) for more details.)

    xtable: {xtable}
    quantity: {quantity}
    ln_quant: {ln_quant}
    '''
    def __init__(self, xtable=UNSET, quantity=None, *, ln_quant=False, **kw_super):
        if xtable is not UNSET:
            xtable = self.labeled_xtable(xtable, quantity=quantity)
        self.xtable = xtable
        self.quantity = quantity
        self.ln_quant = ln_quant

    @staticmethod
    def labeled_xtable(xtable, *, quantity=None, units='raw'):
        '''return copy of xarray.DataArray, labeled with name=quantity and attrs['units']='raw'
        Does not make copy if xtable is already labeled appropriately.
        '''
        if (xtable.name == quantity) and ('units' in xtable.attrs) and (xtable.attrs['units'] == units):
            return xtable
        result = xtable.copy()
        result.name = quantity
        result.attrs['units'] = units
        return result

    # # # SUBCLASS COULD IMPLEMENT # # #
    def load_xtable(self):
        '''load xtable. Here, raises NotImplementedError.
        Subclasses which do not implement this should provide xtable during initialization.
        '''
        raise NotImplementedError(f'implement {type(self).__name__}.load_xtable() or provide xtable during init.')

    # # # OTHER WAYS TO CREATE INSTANCES OF THIS CLASS # # #
    @staticmethod
    @format_docstring(**_paramdocs_ertable, sub_ntab=1)
    def xtable_from_array(array, *, epermcoords, rcoords, quantity=None, extra_dims=None):
        '''create xtable from unlabeled array and coords.
        no unit conversions are performed here; provide inputs in the desired unit system.

        array: {array}
        {kw_er_coords}
        quantity: {quantity}
        extra_dims: {extra_dims}
        '''
        dims = ['eperm', 'r']
        if extra_dims is not None:
            dims.extend(list(extra_dims))
        for i in range(len(dims), np.ndim(array)):  # if missing any dims use unnamed.
            dims.append(f'dim_{i}')
        coords = {'r': rcoords, 'eperm': epermcoords}
        if isinstance(extra_dims, dict):
            coords.update(extra_dims)
        return xr.DataArray(array, dims=dims, coords=coords, name=quantity)

    @classmethod
    @format_docstring(**_paramdocs_ertable, sub_ntab=1)
    def from_array(cls, array, *, epermcoords, rcoords,
                   quantity=None, extra_dims=None, ln_quant=False, **kw_init):
        '''create reTable from unlabeled array, and coords.
        
        array: {array}
        {kw_er_coords}
        quantity: {quantity}
        ln_quant: {ln_quant}
        extra_dims: {extra_dims}
        '''
        kw = dict(epermcoords=epermcoords, rcoords=rcoords,
                  quantity=quantity, extra_dims=extra_dims)
        kw_cls = dict(ln_quant=ln_quant, **kw_init)
        xtable = cls.xtable_from_array(array, **kw)
        return cls(xtable, **kw_cls)

    # # # XTABLE UNITS CHECKING # # #
    @property
    def xtable(self):
        '''xarray.DataArray, probably 2D; must have dims for eperm and r.
        if self.xtable was UNSET, self.load_xtable() first. Units are always 'raw' units.
        '''
        result = self._xtable
        if result is UNSET:
            result = self.load_xtable()
        self._xtable = result
        return result
    @xtable.setter
    def xtable(self, value):
        self._xtable = value

    # # # EVALUATE # # #
    __call__ = alias('interp')

    @format_docstring(**_paramdocs_ertable, sub_ntab=1)
    def interp(self, *, r, eperm=UNSET, e=UNSET, ln=False, keep_er_coords=False, **kw_xarray_interp):
        '''return values of quantity at eperm and r.

        r: {r}
        eperm: {eperm}
        e: {e}
        ln: {ln}
        keep_er_coords: {keep_er_coords}
        '''
        if eperm is UNSET:
            if e is UNSET:
                raise InputMissingError('provide eperm or e.')
            else:
                eperm = e / r
        elif (e is not UNSET):  # and eperm is not UNSET
            raise InputConflictError('cannot provide both eperm and e; must provide only one of them.')
        kw_xarray_interp.setdefault('assume_sorted', self.coords_are_sorted)  # [EFF] faster if sorted!
        result = self.xtable.interp(eperm=eperm, r=r, **kw_xarray_interp)  # xarray.DataArray.interp(...)
        if not keep_er_coords:
            result = result.drop_vars(('eperm', 'r'))
        # exponentiate (or take ln) if necessary
        if self.ln_quant and (not ln):
            result = np.exp(result)
        elif (not self.ln_quant) and ln:
            result = np.log(result)
        return result

    coords_are_sorted = simple_property('_coords_are_sorted', setdefaultvia='can_assume_sorted',
            doc='''whether eperm and r coords (of self.xtable) are sorted (in non-decreasing order).
            Cache result for efficiency, assumes coords are not changed later.''')

    def can_assume_sorted(self):
        '''return whether eperm and r coords are sorted (in non-decreasing order).
        If True, can assume sorted for xarray interp calls, which improves efficiency signficantly.
        '''
        eperm = self.xtable.coords['eperm']
        r = self.xtable.coords['r']
        return xarray_is_sorted(eperm) and xarray_is_sorted(r)

    def interp_inverse(self, quantity, *, r=UNSET, eperm=UNSET, ln=False, **kw_interp_inverse):
        '''return values of r or eperm, given quantity values and other coord's values.

        quantity: number or array
            values of quantity.
        r, eperm: UNSET, number, or array
            values of r, eperm. (r=mass density; eperm=internal energy per unit mass==e/r)
            must provide exactly one of these.
        ln: bool
            whether the values of quantity input to this function are in ln-space.

        any additional kwargs are passed to xarray_interp_inverse.
        '''
        # bookkeeping
        if r is UNSET and eperm is UNSET:
            raise InputMissingError('provide r or eperm.')
        elif r is not UNSET and eperm is not UNSET:
            raise InputConflictError('provide exactly one of r or eperm.')
        interpto = {'r': r} if (r is not UNSET) else {'eperm': eperm}
        _output = 'r' if r is UNSET else 'eperm'
        kw_interp_inverse.setdefault('assume_sorted', self.coords_are_sorted)  # [EFF] faster if sorted!
        # exponentiate (or take ln) if necessary
        if self.ln_quant and (not ln):
            quantity = np.log(quantity)
        elif (not self.ln_quant) and ln:
            quantity = np.exp(quantity)
        # bookkeeping for quantity name stuff:
        xtable = self.xtable
        if xtable.name is None:
            xtable = xtable.rename('_unnamed_xtable_quantity')
        interpto[xtable.name] = quantity
        # get result
        return xarray_interp_inverse(self.xtable, interpto, **kw_interp_inverse)

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'shape={self.xtable.shape}']
        if self.quantity is not None:
            contents.append(f'quantity={self.quantity!r}')
        if self.ln_quant:
            contents.append(f'ln_quant={self.ln_quant!r}')
        return f'{type(self).__name__}({", ".join(contents)})'


@format_docstring(**_paramdocs_ertable)
class erTableFromMemmap(erTable):
    '''lookup table from eperm and r to quantity. Table loaded from a memmap file.
    Internally, all values should be in 'raw' units (see scale_quant kwarg for more details).

    Call self(r=r, eperm=eperm) to get value of quantity at eperm and r.
        (equivalent: self.interp(r=r, eperm=eperm). See help(self.interp) for more details.)

    filename: str
        name of file. Internally stored as abspath.
    quantity: {quantity}
    {kw_er_coords}
    index_in_file: int
        n such that this table is the nth table in the memmap file.
    ln_quant: {ln_quant}
    scale_quant: {scale_quant}
    extra_dims: {extra_dims}
        use this when memmap arrays have more dims than just eperm and r.
    data_shape: {data_shape}
        if extra_dims provided with coords, include those in inferred shape too.
    data_dtype: {data_dtype}
    data_order: {data_order}
    
    [EFF] loading is "lazy"; wait to load until first time the table is actually accessed.
    '''
    def __init__(self, filename, quantity=None, *,
                 epermcoords, rcoords, index_in_file,
                 ln_quant=False, scale_quant=1,
                 extra_dims=None, data_shape=None,
                 data_dtype=np.float32, data_order='F',
                 **kw_super):
        self.filename = os.path.abspath(filename)
        self.rcoords = rcoords
        self.epermcoords = epermcoords
        self.index_in_file = index_in_file
        self.scale_quant = scale_quant
        self.extra_dims = extra_dims
        self.data_shape = data_shape
        self.init_infer_data_shape()
        self.data_dtype = np.dtype(data_dtype)
        self.data_order = data_order
        super().__init__(xtable=UNSET, # xtable not loaded yet!
                         quantity=quantity, ln_quant=ln_quant, **kw_super)

    def init_infer_data_shape(self):
        '''infer data_shape from self.data_shape and self.extra_dims;
        set self.data_shape to the inferred value.'''
        data_shape = self.data_shape
        extra_dims = self.extra_dims
        if data_shape is None:
            data_shape = [len(self.epermcoords), len(self.rcoords)]
            if extra_dims is not None:
                if isinstance(extra_dims, dict):
                    data_shape.extend([len(coords) for coords in extra_dims.values()])
                else:
                    errmsg = f'cannot infer data_shape when extra_dims provided without coord info.'
                    raise InputConflictError(errmsg)
            data_shape = tuple(data_shape)
        elif (extra_dims is not None) and (len(data_shape) < 2 + len(extra_dims)):
            errmsg = f'data_shape dimensionality {data_shape} inconsistent with number of extra_dims.'
            raise DimensionalityError(errmsg)
        self.data_shape = data_shape
        return data_shape

    def _load_table_array(self):
        '''load table array from memmap file.'''
        array_size_nbytes = product(self.data_shape) * self.data_dtype.itemsize
        offset_nbytes = array_size_nbytes * self.index_in_file
        result = np.memmap(self.filename, offset=offset_nbytes,
                           mode='r',  # read-only; never alters existing files!
                           shape=self.data_shape,
                           dtype=self.data_dtype,
                           order=self.data_order,
                           )
        result = np.asarray(result)  # convert to numpy array.
        return result

    def load_xtable(self):
        '''load table xarray from memmap file. scale quant by self.scale_quant if not 1.
        save result to self.xtable, also return it.
        '''
        array = self._load_table_array()
        kw = dict(epermcoords=self.epermcoords, rcoords=self.rcoords,
                  quantity=self.quantity, extra_dims=self.extra_dims)
        xtable = self.xtable_from_array(array, **kw)
        if self.scale_quant != 1:
            if self.ln_quant:
                # result = log(exp(xtable) * factor)
                #       == log(exp(xtable)) + log(factor)
                #       == xtable + log(factor)
                xtable = xtable + np.log(self.scale_quant)
            else:
                xtable = xtable * self.scale_quant
        xtable = self.labeled_xtable(xtable, quantity=self.quantity)
        self.xtable = xtable
        return xtable


class erTableManager(dict):
    '''manages er tables. Dict of {quantity (str): erTable}'''
    er_table_from_memmap_cls = erTableFromMemmap

    __call__ = alias('interp')

    @format_docstring(**_paramdocs_ertable, sub_ntab=1)
    def interp(self, var, *, r, eperm=UNSET, e=UNSET, ln=False,
               keep_er_coords=False, **kw_xarray_interp):
        '''return values of var at eperm and r.

        var: str
            name of quantity to interpolate.
        r: {r}
        eperm: {eperm}
        e: {e}
        ln: {ln}
        keep_er_coords: {keep_er_coords}
        '''
        table = self[var]
        kw = dict(ln=ln, keep_er_coords=keep_er_coords, **kw_xarray_interp)
        return table.interp(r=r, eperm=eperm, e=e, **kw)

    # # # FROM FILE # # #
    @classmethod
    @format_docstring(**_paramdocs_ertable, sub_ntab=1)
    def from_file(cls, memmap_file, *, epermcoords, rcoords,
                  quantities, ln_quants=[], scale_quants={}, extra_dims=None,
                  data_shape=None, data_dtype=np.float32, data_order='F',
                  **kw_init_er_table):
        '''create erTableManager from numpy memmap file with multiple tables.
        
        memmap_file: str
            path to memmap file.
        {kw_er_coords}
        quantities: list of str
            names of quantities in file.
            each quantitiy in file should be an ND array with dims eperm, r, and any extra_dims.
        ln_quants: list of str
            names of quantities whose values in file are in ln-space.
        scale_quants: {scale_quants}
        extra_dims: {extra_dims}
        data_shape: {data_shape}
        data_dtype: {data_dtype}
        data_order: {data_order}
        '''
        kw = dict(epermcoords=epermcoords, rcoords=rcoords,
                  extra_dims=extra_dims, data_shape=data_shape,
                  data_dtype=data_dtype, data_order=data_order,
                  **kw_init_er_table)
        file = os.path.abspath(memmap_file)
        manager = cls()
        for i, var in enumerate(quantities):
            ln = var in ln_quants
            table = cls.er_table_from_memmap_cls(file, var, index_in_file=i, ln_quant=ln,
                                                 scale_quant=scale_quants.get(var, 1),
                                                 **kw)
            manager[var] = table
        return manager

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(keys={list(self.keys())})'


@format_docstring(**_paramdocs_ertable)
def eos_file_tables(eos_file, *, epermcoords, rcoords, u=None):
    '''return erTableManager dict (of {{var: Equation Of State lookup table}}), for vars in file.

    file should have quantities:
        'P' (pressure),
        'T' (temperature),
        'ne' (electron number density),
        'kappaR' (Rosseland opacity).
    file values of P, ne, and kappaR should be in ln-space (e.g. ln(P) instead of P).
    file should have values in cgs
    (despite note in helita implying ne would be in si... I'm 99% sure it is in cgs here.
        e.g. ne close to n (== r / (amu * self.M_AMU_FLUID)) in the corona,
        where plasma should be mostly ionized.
        As opposed to ne 1e-6 times smaller than n, if ne was truly in si in table.)

    eos_file: str
        path to eos table file.
    {kw_er_coords}
    u: {u}
    '''
    kw_eos = dict(
        # properties of the "standard eos table" file.
        #  to load eos tables from file with nonstandard properties,
        #  write a different function but feel free to use this code as an example.
        quantities = ['P', 'T', 'ne', 'kappaR'],
        ln_quants = ['P', 'ne', 'kappaR'],
        data_type = np.float32,
        data_order = 'F',
        )
    if u is None:
        scaling = dict()
    else:
        scaling = {
            'P': u('pressure', 'raw', convert_from='cgs'),
            'T': u('temperature', 'raw', 'cgs'),
            'ne': u('number_density', 'raw', 'cgs'),
            'kappaR': u('opacity', 'raw', 'cgs'),
            }
    kw_eos['scale_quants'] = scaling
    kw = dict(epermcoords=epermcoords, rcoords=rcoords)
    return erTableManager.from_file(eos_file, **kw, **kw_eos)


@format_docstring(**_paramdocs_ertable)
def rad_file_tables(rad_file, *, epermcoords, rcoords, radbins, u=None):
    '''return erTableManager dict (of {{var: Radiation lookup table}}), for vars in file.

    file should have quantities:
        'pscatter' (probability of scattering)
        'emtherm' (thermal emission)
        'opacity' (opacity)
    file values should all (?) be in ln-space (e.g. ln(emtherm) instead of emtherm). [TODO] check
    file should have values in cgs. [TODO] check

    rad_file: str
        path to rad table file.
    {kw_er_coords}
    radbins: int or 1D array-like
        number of radiation bins or coordinates of radiation bins.
    u: {u}
    '''
    if not is_iterable(radbins):
        radbins = np.arange(radbins)
    extra_dims = {'radbin': radbins}
    kw_rad = dict(
        # properties of the "standard rad table" file.
        #  to load rad tables from file with nonstandard properties,
        #  write a different function but feel free to use this code as an example.
        quantities = ['pscatter', 'emtherm', 'opacity'],
        ln_quants = ['pscatter', 'emtherm', 'opacity'],  # [TODO] check
        extra_dims = extra_dims,
        data_type = np.float32,
        data_order = 'F',
        )
    if u is None:
        scaling = dict()
    else:
        scaling = {
            'opacity': u('opacity', 'raw', convert_from='cgs'),
            # [TODO] units for pscatter and emtherm? 
            }
    kw = dict(epermcoords=epermcoords, rcoords=rcoords)
    return erTableManager.from_file(rad_file, **kw, **kw_rad)


### --------------------- directly related to tabparam.in --------------------- ###

@format_docstring(**_paramdocs_ertable)
class erTabInputManager(DictlikeFromKeysAndGetitem, UnitsHaver):
    '''manages tables, based on tab input file.
    All tables and table coords here are in 'raw' units.
    self is dict-like, with keys quantity names, values erTable objects.
        (alternatively, use self.tables for dict like self.)
    self.elements is an ElementList based on the elements info in tab input file.

    filename: str
        path to tab input file, e.g. tab_param.in. Internally stored as abspath.
        This should be an idl-like file which includes params for tables:
            EOSTableFile: str, path to eos table file
            RhoEiRadTableFile: str, path to radiation table file
            nRhoBin: int, number of bins for r (mass density)
            RhoMin, RhoMax: numbers, r [cgs units] for smallest and largest bins
            nEiBin: int, number of bins for eperm (internal energy per unit mass)
            EiMin, EiMax: numbers, eperm [cgs units] for smallest and largest bins
            nRadBins: int, number of radiation bins in the radiation tables.
        It should also include params for elements (each as a string separated by spaces):
            cel: elements names. Internally stored in title case (e.g. 'H', 'He').
            abund: abundances of elements: A(elem) = 12 + log10(n(elem) / n(H)).
            aweight: masses of elements [amu].
    u: {u}
        example: if this TabInputManager is associated with a BifrostCalculator,
            probably will have u = the BifrostUnitsManager from that BifrostCalculator.
    ionize_ev: str or dict
        first ionization potentials of elements [eV]. E.g., {{'H': 13.6}}.
        affects self.elements; irrelevant to tables.
        str --> use ElementList.DEFAULTS['ionize_ev'][ionize_ev]
    '''
    er_table_manager_cls = erTableManager
    element_list_cls = ElementList

    def __init__(self, filename, *, u=None, ionize_ev='physical', **kw_super):
        self.filename = os.path.abspath(filename)
        self.params = read_idl_params_file(self.filename, eval=True)
        self.ionize_ev = ionize_ev
        # units
        super().__init__(u=u, **kw_super) 
        self.init_tables()  # makes self.tables
        self.make_element_list()  # makes self.elements

    def init_tables(self):
        '''initialize self.tables and return result'''
        kw_coords = self.get_coords(for_kw=True)
        # eos tables
        eosfile = self.eosfile
        eos = eos_file_tables(eosfile, **kw_coords, u=self.u)
        # rad tables
        radfile = self.radfile
        radbins = self.n_radbins
        rad = rad_file_tables(radfile, **kw_coords, u=self.u, radbins=radbins)
        # result
        result = eos
        result.update(rad)
        self.tables = result
        return result

    def make_element_list(self, *, ionize_ev=None, set=True):
        '''set & return self.elements = ElementList based on params in self.
        ionize_ev: None, str, or dict
            first ionization potentials of elements [eV]. E.g., {'H': 13.6}.
            str --> use ElementList.DEFAULTS['ionize_ev'][ionize_ev]
            None --> use self.tabin.ionize_ev (default: 'physical')
        set: bool
            whether to set self.elements to the result. Default True.
        '''
        if ionize_ev is None:
            ionize_ev = self.ionize_ev
        cel = self.params['cel'].split()
        abund = self.params['abund'].split()
        aweight = self.params['aweight'].split()
        # check lengths
        if not (len(cel) == len(abund) == len(aweight)):
            raise FileContentsError('cel, abund, and aweight imply different numbers of elements')
        names = [e.title() for e in cel]
        m = {e: attempt_literal_eval(v) for e, v in zip(names, aweight)}
        abundance = {e: attempt_literal_eval(v) for e, v in zip(names, abund)}
        result = self.element_list_cls.from_names(names, m=m, abundance=abundance, ionize_ev=ionize_ev)
        if set: self.elements = result
        return result

    # # # RELEVANT PATHS # # #
    @property
    def dirname(self):
        '''directory containing tabinputfile. Equivalent: os.path.dirname(self.filename)'''
        return os.path.dirname(self.filename)

    @property
    def eosfile(self):
        '''filepath to eos table file.'''
        return os.path.join(self.dirname, self.params['EOSTableFile'])

    @property
    def radfile(self):
        '''filepath to radiation table file.'''
        return os.path.join(self.dirname, self.params['RhoEiRadTableFile'])

    # # # RELEVANT QUANTITIES # # #
    def get_r_coords(self):
        '''return r coords in 'raw' units. Assumes params from paramfile are in cgs units.'''
        rmin = self.params['RhoMin'] * self.u('r', 'raw', convert_from='cgs')
        rmax = self.params['RhoMax'] * self.u('r', 'raw', convert_from='cgs')
        Nr = self.params['nRhoBin']
        return np.logspace(np.log10(rmin), np.log10(rmax), Nr)

    def get_eperm_coords(self):
        '''return eperm coords in 'raw' units. Assumes params from paramfile are in cgs units.'''
        emin = self.params['EiMin'] * self.u('energy_density r-1', 'raw' ,convert_from='cgs')
        emax = self.params['EiMax'] * self.u('energy_density r-1', 'raw', convert_from='cgs')
        Ne = self.params['nEiBin']
        return np.logspace(np.log10(emin), np.log10(emax), Ne)

    def get_coords(self, *, for_kw=False):
        '''return dict of eperm coords and r coords, in 'raw' units.
        Assumes params from paramfile are in cgs units.
        for_kw: bool
            False --> result keys are 'eperm', 'r'.
            True --> result keys are 'epermcoords', 'rcoords'.
        '''
        eperm = self.get_eperm_coords()
        r = self.get_r_coords()
        if for_kw:
            return {'epermcoords': eperm, 'rcoords': r}
        else:
            return {'eperm': eperm, 'r': r}

    @property
    def n_radbins(self):
        '''return number of radbins in self.'''
        return self.params['nRadBins']

    # # # DICT-LIKE BEHAVIOR # # #
    def __getitem__(self, key):
        return self.tables[key]

    def keys(self):
        return self.tables.keys()

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{self.__class__.__name__}({self.filename!r}, keys={list(self.keys())})'
