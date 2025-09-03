"""
File Purpose: itAccessor allows to put array.it.{method} options in xarray objects.

This file also puts wavevector dims-related attrs in itAccessor.
"""

from ...tools import XarrayAccessor


### --------------------- it accessor --------------------- ###
# it can stand for "instability theory" or "instability tools" :)

class itAccessor(XarrayAccessor, accessor_name='it', access_type=None):
    '''Accessor for instability theory tools.'''
    pass  # attach methods & attrs via itAccessor.register & register_attr.

class itArrayAccessor(itAccessor, access_type='array'):
    '''Accessor for instability theory tools on DataArrays.'''
    pass  # attach methods & attrs via itAccessor.register & register_attr with totype='array'.

class itDatasetAccessor(itAccessor, access_type='dataset'):
    '''Accessor for instability theory tools on Datasets.'''
    pass  # attach methods & attrs via itAccessor.register & register_attr with totype='dataset'.
