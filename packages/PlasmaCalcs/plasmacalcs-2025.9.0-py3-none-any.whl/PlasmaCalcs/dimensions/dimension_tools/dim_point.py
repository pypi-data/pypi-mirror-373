"""
File Purpose: DimPoint and DimRegion
"""
import xarray as xr

from ...errors import DimensionValueError
from ...tools import (
    repr_simple,
    UNSET,
    is_iterable_dim,
    xarray_assign,
)

### --------------------- DimRegion and DimPoint --------------------- ###

class DimRegion(dict):
    '''dict of values representing some region of dimension space (possibly a single point).'''
    # # # DISPLAY # # #
    def __repr__(self):
        '''like dict repr but use repr_simple(val) instead of repr(val) for values.'''
        contents = ', '.join(f'{key}={repr_simple(val)}' for key, val in self.items())
        return f'{type(self).__name__}({contents})'

    def assign_to(self, array, **kw_xarray_assign):
        '''array.assign_coords(self). Internally, use PlasmaCalcs xarray_assign function.
        xarray_assign also allows to provide attrs and/or name to assign those as well.
        Also convert array to xr.DataArray if it isn't one already.

        Probably will fail if any values are iterable dimensions e.g. DimensionValueList instead of DimensionValue.
        '''
        if not isinstance(array, xr.DataArray):
            array = xr.DataArray(array)
        return xarray_assign(array, self, **kw_xarray_assign)

class DimPoint(DimRegion):
    '''dict of values representing a single point in dimension-space.
    When setting elements of this dict, ensures not is_iterable_dim(value)

    Does not need to include all dimensions, but all contents must be single-valued dimensions.
    E.g. {'fluid': 0, 'snap': 1} is fine, even if 'jfluid' and 'component' are also dimensions.
    However, {'fluid': 0, 'component':[0,1,2]} is not, because component is multi-valued.
    '''
    def __init__(self, *args_dict, **kw_dict):
        super().__init__(*args_dict, **kw_dict)
        # dict.__init__ doesn't actually utilize __setitem__; need to check values here too.
        for key, value in self.items():
            self._check_value(value, key=key)

    def __setitem__(self, key, value):
        self._check_value(value, key=key)
        super().__setitem__(key, value)

    def _check_value(self, value, *, key=UNSET):
        '''raise DimensionValueError if value is iterable.
        if raising error, include key in error message if provided.
        '''
        if is_iterable_dim(value):
            if key is UNSET:
                errmsg = f"is_iterable_dim(value): {value!r}."
            else:
                errmsg = f"for {key!r}, is_iterable_dim(value): {value!r}."
            raise DimensionValueError(errmsg)