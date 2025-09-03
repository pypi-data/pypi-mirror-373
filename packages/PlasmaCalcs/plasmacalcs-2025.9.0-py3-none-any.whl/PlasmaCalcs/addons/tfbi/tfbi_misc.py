"""
File Purpose: misc tools related to tfbi
"""

import xarray as xr

from ..instability_tools import itAccessor
from ...errors import InputError
from ...tools import (
    alias,
    is_integer,
    xarray_vars_lookup_with_defaults,
)
from ...defaults import DEFAULTS


### --------------------- Helper methods --------------------- ###

def T_from_ldebye(ldebye, *, n, eps0, q, kB):
    '''returns T given ldebye. ldebye**2 = eps0 * kB * T / (n * q**2)
    --> T = ldebye**2 * n * q**2 / (eps0 * kB)

    if ldebye is an xarray.DataArray with a name,
        result name will be 'T_from_{ldebye.name}'.
    '''
    result = ldebye**2 * n * (q**2 / (eps0 * kB))
    if isinstance(result, xr.DataArray) and (ldebye.name is not None):
        result.name = f'T_from_{ldebye.name}'
    return result

@itAccessor.register('T_from_ldebye', totype='dataset')
def xarray_T_from_ldebye(ds, ldebye=None, *, n=None, eps0=None, q=None, kB=None):
    '''return T given ldebye. ldebye**2 = eps0 * kB * T / (n * q**2)
    --> T = ldebye**2 * n * q**2 / (eps0 * kB)

    ds: xarray.Dataset
        dataset to use for inputs. Must contain ldebye data.
    ldebye, n, eps0, q, kB: None, str, or value
        None --> use default lookups (see below) for variable names from ds.
        str --> name of variable in ds representing this physical quantity
        value --> directly use this value.

    quantity meanings:
        ldebye: debye length
        n: number density (of each fluid, if multiple fluids)
        eps0: vacuum permittivity
        q: charge (of each fluid, if multiple fluids with different charges)
        kB: boltzmann constant
    default lookups (if not provided explicitly, use first available):
        ldebye: 'ldebye', 'eqperp_ldebye'
        n: 'n'
        eps0: 'eps0', DEFAULTS.PHYSICAL.CONSTANTS_SI['qe']
        q: 'q', 'qe', 'abs_qe', DEFAULTS.PHYSICAL.CONSTANTS_SI['eps0']
        kB: 'kB', DEFAULTS.PHYSICAL.CONSTANTS_SI['kB']
    '''
    provided = dict(ldebye=ldebye, n=n, eps0=eps0, q=q, kB=kB)
    lookup = dict(ldebye=['ldebye', 'eqperp_ldebye'],
                  n='n',
                  eps0='eps0',
                  q=['q', 'qe', 'abs_qe'],
                  kB='kB')
    defaults = dict(eps0=DEFAULTS.PHYSICAL.CONSTANTS_SI['eps0'],
                    q=DEFAULTS.PHYSICAL.CONSTANTS_SI['qe'],
                    kB=DEFAULTS.PHYSICAL.CONSTANTS_SI['kB'])
    vals = xarray_vars_lookup_with_defaults(ds, provided, lookup, defaults)
    return T_from_ldebye(**vals)


### --------------------- Index in tfbi hypercube --------------------- ###

itAccessor._TFBI_INDEX0_ORDER = ('EBspeed', 'Tgrid', 'ionfrac_H', 'kappae', 'ngrid')
itAccessor.register_attr('tfbi0_order', totype=None,
    value=property(lambda self: self._TFBI_INDEX0_ORDER,
    doc='''standard order of parameters within "type-0" tfbi hypercube, i.e.:
        ('EBspeed', 'Tgrid', 'ionfrac_H', 'kappae', 'ngrid')'''))
itAccessor.register_attr('tfbi0_index_order', totype=None, value=alias('tfbi0_order'))
itAccessor.register_attr('tfbi0keys', totype=None, value=alias('tfbi0_order'))

@itAccessor.register('tfbi0i', aliases=['tfbi0_index'])
def tfbi0_index(array):
    '''returns a 5-tuple of indexes corresponding to this point within "type-0" tfbi hypercube.
    indexes from coords: ('EBspeed_index', 'Tgrid_index', 'ionfrac_H_index', 'kappae_index', 'ngrid_index')
    '''
    coords = [f'{c}_index' for c in array.it.tfbi0_order]
    if not all(c in array.coords for c in coords):
        raise InputError(f'tfbi0_index requires coords {coords}. Only found coords: {list(array.coords)}')
    nonscalars = {c for c in coords if array.coords[c].ndim!=0}
    if not all(array.coords[c].ndim==0 for c in coords):
        raise InputError(f'tfbi0_index requires scalars {coords}. Got non-scalars: {nonscalars}')
    result = tuple(array[c].item() for c in coords)
    if not all(is_integer(i) for i in result):
        raise InputError(f'tfbi0_index requires integer indexes. Got: {result}')
    return tuple(int(i) for i in result)

@itAccessor.register('tfbi0istr', aliases=['tfbi0_index_str'])
def tfbi0_index_str(array):
    '''returns a string of indexes corresponding to this point within "type-0" tfbi hypercube.
    indexes from coords: ('EBspeed_index', 'Tgrid_index', 'ionfrac_H_index', 'kappae_index', 'ngrid_index')
    Format will be like: (0,0,0,0,0)
    '''
    result = tfbi0_index(array)
    return '(' + ",".join(str(i) for i in result) + ')'

@itAccessor.register('tfbi0params', aliases=['tfbi0_params'])
def tfbi0_params(array):
    '''returns a dict of {param: value} for a point within "type-0" tfbi hypercube.
    Result has keys: ('EBspeed', 'Tgrid', 'ionfrac_H', 'kappae', 'ngrid')
    if param values are DataArray scalars, use .item() to convert to scalars.
    '''
    result = {c: array[c] for c in array.it.tfbi0_order}
    result = {c: v.item() if getattr(v, 'ndim', None)==0 else v for c, v in result.items()}
    return result

@itAccessor.register('tfbi0str', aliases=['tfbi0_params_str'])
def tfbi0_params_str(array, fmt='.3g'):
    '''returns a string telling param values for a point within "type-0" tfbi hypercube.
    Result looks like: EBspeed=val, Tgrid=val, ionfrac_H=val, kappae=val, ngrid=val
    '''
    result = tfbi0_params(array)
    return ', '.join(f'{c}={v:{fmt}}' for c, v in result.items())

@itAccessor.register('tfbi0isel', aliases=['tfbi0_index_isel'])
def tfbi0_index_isel(array, tfbii0):
    '''returns a dict of {param: index} given the 5 indexes within "type-0" tfbi hypercube.
    Result has keys: ('EBspeed', 'Tgrid', 'ionfrac_H', 'kappae', 'ngrid'),
    tfbii0: 5-tuple of indexes for those 5 params, in that order ^
    '''
    return dict(zip(array.it.tfbii0_order, tfbii0))
